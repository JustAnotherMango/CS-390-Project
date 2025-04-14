from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import mysql.connector
from collections import defaultdict
from datetime import datetime

DATE_FORMAT = "%d %b %Y"

def get_max_trade_date_from_db():
    try:
        cnx = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="trades_db",
            connection_timeout=5
        )
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT MAX(STR_TO_DATE(trade_date, '%d %b %Y')) AS max_date FROM politician_trades")
        result = cursor.fetchone()
        cursor.close()
        cnx.close()
        if result["max_date"]:
            return result["max_date"]
        else:
            return None
    except Exception as e:
        print("Error getting max trade date from DB:", e, flush=True)
        return None

def scrape_politician_page(politician_url, max_pages=10, update_mode=False, max_existing_date=None):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(politician_url)
    time.sleep(1)
    try:
        politician_name = driver.find_element(By.CSS_SELECTOR, "article.politician-detail-card h1").text
        party = driver.find_element(By.CSS_SELECTOR, "span.q-field.party").text
        chamber = driver.find_element(By.CSS_SELECTOR, "span.q-field.chamber").text
        state = driver.find_element(By.CSS_SELECTOR, "span.q-field.us-state-full").text
        details = driver.find_element(By.CSS_SELECTOR, "article.politician-detail-card h2").text.split()
    except Exception as e:
        print("Error extracting politician details:", e, flush=True)
        politician_name, party, chamber, state = "Unknown Politician", "Unknown", "Unknown", "Unknown"


    print(f"Scraping trades for: {politician_name} ({party}, {chamber}, {state})", flush=True)
    
    trades = []
    page = 1
    while page <= max_pages:
        page_url = politician_url if page == 1 else f"{politician_url}?page={page}"
        print(f"Scraping page {page}: {page_url}", flush=True)
        driver.get(page_url)
        time.sleep(1)
        try:
            table = driver.find_element(By.CSS_SELECTOR, "table.w-full")
        except Exception as e:
            print(f"No trades table found on page {page}: {e}", flush=True)
            break

        rows = table.find_elements(By.TAG_NAME, "tr")
        if not rows:
            print(f"No rows found on page {page}. Ending pagination.", flush=True)
            break

        valid_count = 0
        for row in rows:
            trade_text = row.text
            fields = trade_text.split("\n")
            if fields and fields[0].strip().upper() == "TRADED ISSUER":
                continue
            if len(fields) >= 9:
                traded_issuer = fields[0]
                ticker = fields[1]
                published_date = f"{fields[2]} {fields[3]}"
                trade_date = f"{fields[4]} {fields[5]}"
                gap_unit = fields[6]
                gap = fields[7]
                trade_type = fields[8]
                trade_size = fields[9].replace('\u2013', '-').replace('\u2014', '-').replace('\u2212', '-') if len(fields) > 9 else "N/A"


                DATE_FORMAT = "%d %b %Y"
                if update_mode and max_existing_date:
                    try:
                        trade_date_dt = datetime.strptime(trade_date, DATE_FORMAT)
                        if trade_date_dt.date() <= max_existing_date:
                            print(
                                f"Encountered trade_date {trade_date} <= DB max date {max_existing_date} for {politician_name}. Stopping scraping for this politician.",
                                flush=True,
                            )
                            driver.quit()
                            return trades
                    except Exception as e:
                        print(f"Error parsing trade_date '{trade_date}': {e}", flush=True)

                trades.append({
                    "politician": politician_name,
                    "party": party,
                    "chamber": chamber,
                    "state": state,
                    "traded_issuer": traded_issuer,
                    "ticker": ticker,
                    "published_date": published_date,
                    "trade_date": trade_date,
                    "gap_unit": gap_unit,
                    "gap": gap,
                    "trade_type": trade_type,
                    "trade_size": trade_size,
                    "page": page
                })
                valid_count += 1
            else:
                print("Row has fewer than 10 fields; skipping.", flush=True)

        print(f"Valid trades found on page {page}: {valid_count}", flush=True)
        if valid_count == 0:
            print("No valid trades on this page. Stopping pagination.", flush=True)
            break
        page += 1
    driver.quit()
    return trades


def insert_trades_into_db(trades):
    print("Starting initial insertion process...", flush=True)
    try:
        cnx = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="trades_db",
            connection_timeout=5
        )
        print("DB connection established.", flush=True)
    except Exception as e:
        print("Error connecting to DB:", e, flush=True)
        return

    cursor = cnx.cursor()
    insert_query = """
    INSERT INTO politician_trades (
        politician, party, chamber, state, traded_issuer, ticker, published_date,
        trade_date, gap_unit, gap, trade_type, trade_size, page
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

    total_trades = len(trades)
    print(f"Preparing to insert {total_trades} trades into the DB...", flush=True)
    inserted_count = 0

    for idx, trade in enumerate(trades, start=1):
        values = (
            trade["politician"],
            trade["party"],
            trade["chamber"],
            trade["state"],
            trade["traded_issuer"],
            trade["ticker"],
            trade["published_date"],
            trade["trade_date"],
            trade["gap_unit"],
            trade["gap"],
            trade["trade_type"],
            trade["trade_size"],
            trade["page"]
        )
        try:
            cursor.execute(insert_query, values)
            cnx.commit()
            inserted_count += 1
        except Exception as e:
            print(f"Error inserting record {idx}: {e}", flush=True)
            cnx.rollback()

    print(f"Inserted {inserted_count} rows out of {total_trades} attempts.", flush=True)
    trade_counts = defaultdict(int)
    for trade in trades:
        trade_counts[trade["politician"]] += 1

    for politician, count in trade_counts.items():
        print(f"Successfully submitted {count} trades for {politician}.", flush=True)

    cursor.close()
    cnx.close()
    print("Initial insertion process finished.", flush=True)

def update_trades_into_db(trades):
    print("Starting update insertion process...", flush=True)
    try:
        cnx = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="trades_db",
            connection_timeout=5
        )
        print("DB connection established for update.", flush=True)
    except Exception as e:
        print("Error connecting to DB for update:", e, flush=True)
        return

    cursor = cnx.cursor()
    insert_query = """
    INSERT INTO politician_trades (
        politician, party, chamber, state, traded_issuer, ticker, published_date,
        trade_date, gap_unit, gap, trade_type, trade_size, page
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

    total_new = len(trades)
    print(f"Preparing to insert {total_new} new trades into the DB...", flush=True)
    inserted_count = 0

    for idx, trade in enumerate(trades, start=1):
        values = (
            trade["politician"],
            trade["party"],
            trade["chamber"],
            trade["state"],
            trade["traded_issuer"],
            trade["ticker"],
            trade["published_date"],
            trade["trade_date"],
            trade["gap_unit"],
            trade["gap"],
            trade["trade_type"],
            trade["trade_size"],
            trade["page"]
        )
        try:
            cursor.execute(insert_query, values)
            cnx.commit()
            inserted_count += 1
            print(f"Updated record {idx}/{total_new} inserted successfully.", flush=True)
        except Exception as e:
            print(f"Error inserting updated record {idx}: {e}", flush=True)
            cnx.rollback()

    print(f"Updated {inserted_count} rows out of {total_new} attempts.", flush=True)
    cursor.close()
    cnx.close()
    print("Update insertion process finished.", flush=True)


def test_db_connection():
    print("Testing DB connection...", flush=True)
    try:
        cnx = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="trades_db",
            connection_timeout=5
        )
        print("Connected to DB successfully.", flush=True)
        cnx.close()
    except Exception as e:
        print("Error in DB connection test:", e, flush=True)

def run_operation():
    print("\nChoose an operation:")
    print("1: Full Insert (populate DB with all scraped trades)")
    print("2: Update (insert only new trades)")
    choice = input("Enter 1 or 2 (or 'q' to quit): ").strip()
    
    if choice.lower() == 'q':
        print("Exiting.")
        return False

    update_mode = (choice == "2")
    max_existing_date = None

    if update_mode:
        max_existing_date = get_max_trade_date_from_db()
        if max_existing_date:
            print(f"DB maximum trade_date: {max_existing_date}", flush=True)
        else:
            print("No existing trade dates found in DB; will insert all trades.", flush=True)

    politician_urls = [
        "https://www.capitoltrades.com/politicians/P000197",
        "https://www.capitoltrades.com/politicians/D000617",
        "https://www.capitoltrades.com/politicians/M000355",
        "https://www.capitoltrades.com/politicians/B001327"
    ]
    all_trades = []
    for url in politician_urls:
        trades = scrape_politician_page(url, max_pages=10, update_mode=update_mode, max_existing_date=max_existing_date)
        all_trades.extend(trades)
    print("Final list of scraped trades:", all_trades, flush=True)

    if choice == "1":
        insert_trades_into_db(all_trades)
    elif choice == "2":
        update_trades_into_db(all_trades)
    else:
        print("Invalid choice. Exiting.", flush=True)
        return False

    return True

if __name__ == "__main__":
    while True:
        should_continue = run_operation()
        if not should_continue:
            break
        again = input("\nDo you want to perform another operation? (y/n): ").strip().lower()
        if again != 'y':
            print("Exiting program.")
            break
