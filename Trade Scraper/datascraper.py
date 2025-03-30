from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import mysql.connector
from collections import defaultdict

def scrape_politician_page(politician_url, max_pages=10):
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(politician_url)
    time.sleep(3)
    try:
        politician_name = driver.find_element(By.CSS_SELECTOR, "article.politician-detail-card h1").text
    except Exception as e:
        print("Error extracting politician name:", e, flush=True)
        politician_name = "Unknown Politician"
    print(f"Scraping trades for: {politician_name}", flush=True)
    
    trades = []
    page = 1
    while page <= max_pages:
        page_url = politician_url if page == 1 else f"{politician_url}?page={page}"
        print(f"Scraping page {page}: {page_url}", flush=True)
        driver.get(page_url)
        time.sleep(3)
        try:
            table = driver.find_element(By.CSS_SELECTOR, "table.w-full")
        except Exception as e:
            print(f"No trades table found on page {page}: {e}", flush=True)
            break

        rows = table.find_elements(By.TAG_NAME, "tr")
        if not rows or len(rows) == 0:
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
                published_date = f"{fields[2]} {fields[3]}" if len(fields) >= 4 else ""
                trade_date = f"{fields[4]} {fields[5]}" if len(fields) >= 6 else ""
                gap_unit = fields[6] if len(fields) >= 7 else ""
                gap = fields[7] if len(fields) >= 8 else ""
                trade_type = fields[8] if len(fields) >= 9 else ""
                trade_size = fields[9] if len(fields) >= 10 else ""
                trades.append({
                    "politician": politician_name,
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
                pass

        print(f"Valid trades found on page {page}: {valid_count}", flush=True)
        if valid_count == 0:
            print("No valid trades on this page. Stopping pagination.", flush=True)
            break
        page += 1
    driver.quit()
    return trades

def insert_trades_into_db(trades):
    print("Starting insertion process...", flush=True)
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
        politician, traded_issuer, ticker, published_date, trade_date,
        gap_unit, gap, trade_type, trade_size, page
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    total_trades = len(trades)
    print(f"Preparing to insert {total_trades} trades into the DB...", flush=True)
    inserted_count = 0

    for idx, trade in enumerate(trades, start=1):
        values = (
            trade["politician"],
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

    print(f"Inserted {inserted_count} rows into the database out of {total_trades} attempts.", flush=True)
    trade_counts = defaultdict(int)
    for trade in trades:
        trade_counts[trade["politician"]] += 1

    for politician, count in trade_counts.items():
        print(f"Successfully submitted {count} trades for {politician}.", flush=True)

    cursor.close()
    cnx.close()
    print("Insertion process finished.", flush=True)

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

if __name__ == "__main__":
    politician_urls = [
        "https://www.capitoltrades.com/politicians/P000197",
        "https://www.capitoltrades.com/politicians/D000617"
    ]
    all_trades = []
    for url in politician_urls:
        trades = scrape_politician_page(url, max_pages=10)
        all_trades.extend(trades)
    print("Final list of all trades:", all_trades, flush=True)
    insert_trades_into_db(all_trades)
