import os
import time
import logging
import re
import mysql.connector
from collections import defaultdict
from datetime import datetime
from tqdm import tqdm

# For Selenium scraping (politician trades)
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# For Alpaca API historical data
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration (adjust as needed)
db_config = {
    'host': 'localhost',
    'user': 'root',       # Your MySQL username
    'password': 'root',   # Your MySQL password
    'database': 'trades_db'
}

DATE_FORMAT = "%d %b %Y"  # Example: "12 Sep 2023"

#################################
# Helper: Safe Date Parsing     #
#################################

def safe_parse_date(date_str):
    """
    Attempts to parse date_str using DATE_FORMAT.
    If it fails due to a common month format issue (e.g. "Sept" vs "Sep"),
    it replaces "Sept" with "Sep" and tries again.
    """
    try:
        return datetime.strptime(date_str, DATE_FORMAT)
    except Exception:
        modified = date_str.replace("Sept", "Sep")
        try:
            return datetime.strptime(modified, DATE_FORMAT)
        except Exception as e:
            logger.error(f"safe_parse_date: failed to parse date '{date_str}'")
            return None

#################################
# Helper: Valid and Adjust Ticker #
#################################

def is_valid_ticker(ticker):
    """
    Returns False if the ticker is empty, "N/A", or clearly not a standard stock symbol.
    """
    if not ticker:
        return False
    clean = ticker.strip().lower()
    if clean in ["", "n/a", "none", "null"]:
        return False
    if "state" in clean or "bond" in clean or len(clean) > 12:
        return False
    return True

def adjust_ticker_for_alpaca(ticker):
    """
    Adjusts the ticker to a format accepted by Alpaca.
    For example, converts "BRK/B" to "BRK.B".
    """
    if "/" in ticker:
        return ticker.replace("/", ".")
    return ticker

#################################
# Database Helpers              #
#################################

def get_db_connection():
    try:
        logger.info("Attempting to connect to MySQL database...")
        conn = mysql.connector.connect(**db_config)
        logger.info("Successfully connected to MySQL database")
        return conn
    except mysql.connector.Error as err:
        logger.error(f"Database connection error: {err}")
        raise

def get_max_trade_date_from_db():
    try:
        cnx = get_db_connection()
        cursor = cnx.cursor(dictionary=True)
        query = "SELECT MAX(STR_TO_DATE(trade_date, %s)) AS max_date FROM politician_trades"
        cursor.execute(query, (DATE_FORMAT,))
        result = cursor.fetchone()
        cursor.close()
        cnx.close()
        return result["max_date"] if result["max_date"] else None
    except Exception as e:
        logger.error(f"Error getting max trade date from DB: {e}")
        return None

def fetch_distinct_tickers_from_db():
    try:
        cnx = get_db_connection()
        cursor = cnx.cursor()
        cursor.execute("SELECT DISTINCT ticker FROM politician_trades WHERE ticker IS NOT NULL AND ticker <> 'N/A'")
        results = cursor.fetchall()
        cursor.close()
        cnx.close()
        all_tickers = {row[0].strip() for row in results if row[0].strip()}
        # Only keep valid tickers
        return {t for t in all_tickers if is_valid_ticker(t)}
    except Exception as e:
        logger.error(f"Error fetching distinct tickers: {e}")
        return set()

#################################
# Historical Price Handling     #
#################################

def get_historical_price(ticker, target_date_str, price_type="close"):
    """
    Given a ticker and target date (string in DATE_FORMAT), queries the historical_trades
    table for the price (by price_type, e.g., "close") on the nearest available date.
    Returns a tuple (float_price, timestamp) or (None, None) if no result.
    """
    target_date = safe_parse_date(target_date_str)
    if not target_date:
        return None, None

    cnx = get_db_connection()
    cursor = cnx.cursor(dictionary=True)
    query = f"""
    SELECT timestamp, {price_type} 
    FROM historical_trades 
    WHERE symbol = %s
    ORDER BY ABS(TIMESTAMPDIFF(SECOND, timestamp, %s)) ASC 
    LIMIT 1;
    """
    result = None
    try:
        cursor.execute(query, (ticker, target_date))
        result = cursor.fetchone()
    except Exception as e:
        logger.error(f"Error querying historical price for {ticker}: {e}")
    finally:
        cursor.close()
        cnx.close()

    if result:
        raw_price = result[price_type]
        float_price = float(raw_price) if raw_price is not None else None
        return float_price, result['timestamp']
    else:
        return None, None

#################################
# Politician Trades Functions   #
#################################

def get_current_price(ticker):
    # Dummy implementation; replace with a live API call if needed.
    return 150.00

def parse_trade_size(trade_size_str):
    """
    Parses a trade_size string (e.g., "500K–1M", "250K–500K", "< 1K")
    and returns a tuple (min_value, max_value) as numbers.
    Returns (None, None) if parsing fails.
    """
    txt = trade_size_str.strip().upper()
    if txt == "N/A":
        return None, None
    if txt.startswith("<"):
        val_str = txt.lstrip("<").strip()
        match = re.match(r'([\d\.]+)\s*([KM])', val_str, re.IGNORECASE)
        if match:
            num = float(match.group(1))
            unit = match.group(2).upper()
            mult = 1000 if unit == "K" else 1000000
            return 0, num * mult
        return None, None
    pattern = r'([\d\.]+)\s*([KM])\s*(?:–|-)\s*([\d\.]+)\s*([KM])'
    match = re.match(pattern, txt, re.IGNORECASE)
    if match:
        n1 = float(match.group(1))
        u1 = match.group(2).upper()
        n2 = float(match.group(3))
        u2 = match.group(4).upper()
        mult1 = 1000 if u1 == "K" else 1000000
        mult2 = 1000 if u2 == "K" else 1000000
        return n1 * mult1, n2 * mult2
    return None, None

def calculate_roi_range(min_purchase, max_purchase, ticker, trade_date_str, published_date_str):
    """
    Calculates ROI (as a percentage) for a paired trade.
    It retrieves historical close prices on the buy date (trade_date_str)
    and the sell date (published_date_str). If a purchase range is provided,
    it calculates worst-case (using max_purchase) and best-case (using min_purchase) ROI.
    Returns a tuple (roi_worst, roi_best, roi_avg).
    """
    try:
        buy_price, _ = get_historical_price(ticker, trade_date_str, "close")
        sell_price, _ = get_historical_price(ticker, published_date_str, "close")
        if not buy_price:
            logger.info(f"No historical buy price for {ticker} at {trade_date_str}; using dummy price.")
            buy_price = get_current_price(ticker)
        if not sell_price:
            logger.info(f"No historical sell price for {ticker} at {published_date_str}; using dummy price.")
            sell_price = get_current_price(ticker)
        if min_purchase is not None and max_purchase is not None:
            min_purchase = float(min_purchase)
            max_purchase = float(max_purchase)
            roi_worst = ((sell_price - max_purchase) / max_purchase) * 100 if max_purchase else None
            roi_best  = ((sell_price - min_purchase) / min_purchase) * 100 if min_purchase else None
            roi_avg   = (roi_worst + roi_best) / 2 if roi_worst is not None and roi_best is not None else None
        else:
            roi_worst = roi_best = roi_avg = ((sell_price - buy_price) / buy_price) * 100 if buy_price else None
        return round(roi_worst, 2), round(roi_best, 2), round(roi_avg, 2)
    except Exception as e:
        logger.error(f"Error calculating ROI for {ticker} (buy: {trade_date_str}, sell: {published_date_str}): {e}")
        return None, None, None

def scrape_politician_page(politician_url, max_pages=10, update_mode=False, max_existing_date=None):
    """
    Scrapes politician trades from the given URL, using cell-level extraction.
    Skips trades with invalid tickers.
    """
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
    except Exception as e:
        logger.error(f"Error extracting politician details: {e}")
        politician_name, party, chamber, state = "Unknown Politician", "Unknown", "Unknown", "Unknown"
    
    # Improved image retrieval: try republican first, then democrat.
    image_url = None
    try:
        img_elem = driver.find_element(By.CSS_SELECTOR, "img.republican")
        image_url = img_elem.get_attribute("src")
    except Exception as e:
        try:
            img_elem = driver.find_element(By.CSS_SELECTOR, "img.democrat")
            image_url = img_elem.get_attribute("src")
        except Exception as e:
            logger.error(f"Error extracting politician image: {e}")
            image_url = None

    logger.info(f"Scraping trades for: {politician_name} ({party}, {chamber}, {state})")
    trades = []
    page = 1
    while page <= max_pages:
        page_url = politician_url if page == 1 else f"{politician_url}?page={page}"
        logger.info(f"Scraping page {page}: {page_url}")
        driver.get(page_url)
        time.sleep(1)
        try:
            table = driver.find_element(By.CSS_SELECTOR, "table.w-full")
        except Exception as e:
            logger.info(f"No trades table found on page {page}: {e}")
            break

        rows = table.find_elements(By.TAG_NAME, "tr")
        if not rows:
            logger.info(f"No rows found on page {page}. Ending pagination.")
            break

        valid_count = 0
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) < 7:
                continue

            try:
                traded_issuer = cells[0].text.strip()
                ticker_elem = cells[0].find_element(By.CSS_SELECTOR, "span.q-field.issuer-ticker")
                ticker_raw = ticker_elem.text.strip()
                if ":" in ticker_raw:
                    ticker_raw = ticker_raw.split(":")[0]
            except Exception as e:
                logger.error(f"Error extracting issuer/ticker: {e}")
                continue

            if not is_valid_ticker(ticker_raw):
                logger.info(f"Skipping trade with invalid ticker: '{ticker_raw}' (issuer: '{traded_issuer}')")
                continue

            try:
                pub_lines = cells[1].text.splitlines()
                published_date = " ".join(pub_lines)
            except Exception as e:
                logger.error(f"Error extracting published date: {e}")
                published_date = ""
                
            try:
                trade_lines = cells[2].text.splitlines()
                trade_date = " ".join(trade_lines)
            except Exception as e:
                logger.error(f"Error extracting trade date: {e}")
                trade_date = ""

            gap = cells[3].text.strip()
            trade_type = cells[4].text.strip()

            try:
                purchase_text = cells[5].text.strip()
                min_purchase_price, max_purchase_price = parse_trade_size(purchase_text)
            except Exception as e:
                logger.error(f"Error parsing purchase text: {e}")
                min_purchase_price, max_purchase_price = None, None

            if update_mode and max_existing_date:
                bd = safe_parse_date(trade_date)
                if bd and bd.date() <= max_existing_date:
                    logger.info(f"Encountered older trade_date {trade_date} <= DB max date {max_existing_date} for {politician_name}. Stopping.")
                    driver.quit()
                    return trades

            trades.append({
                "politician": politician_name,
                "party": party,
                "chamber": chamber,
                "state": state,
                "traded_issuer": traded_issuer,
                "ticker": ticker_raw,
                "published_date": published_date,
                "trade_date": trade_date,
                "gap": gap,
                "trade_type": trade_type,
                "page": page,
                "min_purchase_price": min_purchase_price,
                "max_purchase_price": max_purchase_price,
                "image": image_url
            })
            valid_count += 1

        logger.info(f"Valid trades found on page {page}: {valid_count}")
        if valid_count == 0:
            logger.info("No valid trades on this page. Stopping pagination.")
            break
        page += 1

    driver.quit()
    return trades

def insert_trades_into_db(trades):
    logger.info("Starting insertion process for politician trades (without ROI calc)...")
    try:
        cnx = get_db_connection()
    except Exception as e:
        logger.error(f"Error connecting to DB: {e}")
        return
    cursor = cnx.cursor()
    insert_query = """
    INSERT INTO politician_trades (
        politician, party, chamber, state, traded_issuer, ticker,
        published_date, trade_date, gap, trade_type, page, image,
        avg_roi, min_roi, max_roi, min_purchase_price, max_purchase_price
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    total_trades = len(trades)
    logger.info(f"Preparing to insert {total_trades} trades into the DB...")
    inserted_count = 0
    for idx, trade in enumerate(trades, start=1):
        try:
            min_purchase = float(trade["min_purchase_price"]) if trade["min_purchase_price"] is not None else None
            max_purchase = float(trade["max_purchase_price"]) if trade["max_purchase_price"] is not None else None
        except Exception as e:
            logger.error(f"Error converting purchase prices: {e}")
            min_purchase, max_purchase = None, None

        values = (
            trade["politician"],
            trade["party"],
            trade["chamber"],
            trade["state"],
            trade["traded_issuer"],
            trade["ticker"],
            trade["published_date"],
            trade["trade_date"],
            trade["gap"],
            trade["trade_type"],
            trade["page"],
            trade["image"],
            None, None, None,  # ROI placeholders; will update later
            min_purchase,
            max_purchase
        )
        try:
            cursor.execute(insert_query, values)
            cnx.commit()
            inserted_count += 1
            logger.info(f"Inserted record {idx}/{total_trades} successfully.")
        except Exception as e:
            logger.error(f"Error inserting record {idx}: {e}")
            cnx.rollback()

    logger.info(f"Inserted {inserted_count} rows out of {total_trades} attempts.")
    cursor.close()
    cnx.close()
    logger.info("Insertion process finished for politician trades.")

def update_roi_by_pairs():
    logger.info("Updating ROI based on buy-sell pairs for each ticker...")
    tickers = fetch_distinct_tickers_from_db()
    if not tickers:
        logger.info("No valid tickers found; aborting ROI update by pairs.")
        return

    for ticker in tickers:
        cnx = get_db_connection()
        cursor = cnx.cursor(dictionary=True)
        query = """
        SELECT id, trade_type, trade_date, published_date, min_purchase_price, max_purchase_price
        FROM politician_trades
        WHERE ticker = %s
        ORDER BY STR_TO_DATE(trade_date, %s) ASC
        """
        cursor.execute(query, (ticker, DATE_FORMAT))
        trades = cursor.fetchall()
        cursor.close()
        cnx.close()

        pairs = []
        i = 0
        while i < len(trades) - 1:
            cur = trades[i]
            nxt = trades[i+1]
            if cur["trade_type"].lower() == "buy" and nxt["trade_type"].lower() == "sell":
                pairs.append((cur, nxt))
                i += 2
            else:
                i += 1

        if not pairs:
            logger.info(f"No complete buy-sell pairs found for {ticker}; skipping ROI update for this ticker.")
            continue

        roi_values = []
        for buy_trade, sell_trade in pairs:
            buy_date = buy_trade["trade_date"]
            sell_date = sell_trade["published_date"]
            buy_price, _ = get_historical_price(ticker, buy_date, "close")
            sell_price, _ = get_historical_price(ticker, sell_date, "close")
            if not buy_price or not sell_price:
                logger.info(f"Missing historical price for ticker {ticker} in a pair; skipping this pair.")
                continue
            try:
                roi = ((sell_price - buy_price) / buy_price) * 100
                roi_values.append(roi)
            except Exception as e:
                logger.error(f"Error calculating ROI for pair {buy_trade['id']}-{sell_trade['id']}: {e}")
                continue

        if not roi_values:
            logger.info(f"No ROI values computed for {ticker}; skipping update.")
            continue

        avg_roi = sum(roi_values) / len(roi_values)
        min_roi = min(roi_values)
        max_roi = max(roi_values)
        logger.info(f"For ticker {ticker}, computed ROI (from {len(roi_values)} pairs): avg {avg_roi}, min {min_roi}, max {max_roi}")

        cnx = get_db_connection()
        update_cursor = cnx.cursor()
        update_query = """
        UPDATE politician_trades
        SET avg_roi = %s, min_roi = %s, max_roi = %s
        WHERE ticker = %s
        """
        try:
            update_cursor.execute(update_query, (round(avg_roi, 2), round(min_roi, 2), round(max_roi, 2), ticker))
            cnx.commit()
            logger.info(f"Updated ROI for ticker {ticker} in all trades.")
        except Exception as e:
            logger.error(f"Error updating ROI for ticker {ticker}: {e}")
            cnx.rollback()
        update_cursor.close()
        cnx.close()

def update_roi_for_all_trades():
    logger.info("Updating ROI for all trades individually...")
    try:
        cnx = get_db_connection()
        cursor_select = cnx.cursor(dictionary=True)
        cursor_update = cnx.cursor()
        cursor_select.execute("SELECT id, ticker, trade_date, published_date, min_purchase_price, max_purchase_price FROM politician_trades")
        records = cursor_select.fetchall()
        logger.info(f"Found {len(records)} trades to update ROI.")
        for record in records:
            roi_worst, roi_best, roi_avg = calculate_roi_range(
                record["min_purchase_price"], record["max_purchase_price"],
                record["ticker"], record["trade_date"], record["published_date"]
            )
            update_query = "UPDATE politician_trades SET min_roi = %s, max_roi = %s, avg_roi = %s WHERE id = %s"
            try:
                cursor_update.execute(update_query, (roi_worst, roi_best, roi_avg, record["id"]))
                cnx.commit()
                logger.info(f"Updated ROI for trade id {record['id']}: best {roi_best}, worst {roi_worst}, avg {roi_avg}")
            except Exception as e:
                logger.error(f"Error updating ROI for trade id {record['id']}: {e}")
                cnx.rollback()
        cursor_select.close()
        cursor_update.close()
        cnx.close()
        logger.info("Finished updating ROI for all trades individually.")
    except Exception as e:
        logger.error(f"Error in update_roi_for_all_trades: {e}")

###############################
# Historical Trades Section   #
###############################

def populate_historical_trades():
    """
    Fetches distinct tickers from politician_trades, then uses the Alpaca API
    to pull daily historical data and insert it into historical_trades.
    """
    API_KEY = "PK3JXYAJVNEAWAJ1X3I6"
    API_SECRET = "TjNn9ltUdOaw80zerWy4lhpCZRa9qwAhNb8ItR3g"
    client = StockHistoricalDataClient(API_KEY, API_SECRET)
    # Fetch distinct tickers (only valid ones)
    unique_tickers = fetch_distinct_tickers_from_db()
    if not unique_tickers:
        logger.info("No valid tickers to fetch historical data for.")
        return

    # Adjust tickers for Alpaca if needed (e.g. replace '/' with '.')
    symbol_list = sorted([adjust_ticker_for_alpaca(t) for t in unique_tickers])
    logger.info(f"Fetching historical data for: {symbol_list}")

    timeframe = TimeFrame.Day
    start_date = datetime(2016, 1, 1)
    end_date = datetime(2025, 4, 10)

    request_params = StockBarsRequest(
        symbol_or_symbols=symbol_list,
        timeframe=timeframe,
        start=start_date,
        end=end_date
    )
    logger.info("Fetching historical trade data from Alpaca API...")
    bars_response = client.get_stock_bars(request_params)
    data = bars_response.df

    cnx = get_db_connection()
    cursor = cnx.cursor()
    insert_query = """
    INSERT INTO historical_trades (
        symbol, timestamp, open, high, low, close, volume, trade_count, vwap
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    inserted_count = 0
    total_rows = len(data)
    # Wrap the iteration with tqdm for progress bar
    for index, row in tqdm(data.iterrows(), total=total_rows, desc="Inserting historical trades"):
        if isinstance(index, tuple):
            symbol, ts = index
        else:
            symbol = row.get("symbol")
            ts = row.get("timestamp")
        try:
            open_price  = float(row['open'])  if row['open']  is not None else None
            high_price  = float(row['high'])  if row['high']  is not None else None
            low_price   = float(row['low'])   if row['low']   is not None else None
            close_price = float(row['close']) if row['close'] is not None else None
            volume_val  = int(row['volume'])  if row['volume'] is not None else 0

            trade_count_val = row.get('trade_count', None)
            if trade_count_val is not None:
                trade_count_val = int(trade_count_val)
            vwap_val = row.get('vwap', None)
            if vwap_val is not None:
                vwap_val = float(vwap_val)
        except Exception as e:
            logger.error(f"Error processing row for symbol {symbol} at {ts}: {e}")
            continue

        try:
            cursor.execute(insert_query, (
                symbol, ts, open_price, high_price, low_price, close_price,
                volume_val, trade_count_val, vwap_val
            ))
            cnx.commit()
            inserted_count += 1
        except Exception as e:
            logger.error(f"Error inserting historical trade for {symbol} at {ts}: {e}")
            cnx.rollback()

    cursor.close()
    cnx.close()
    logger.info(f"Historical trades population completed. Inserted {inserted_count} records.")

#################################
# Main Menu Logic               #
#################################

def run_operation():
    print("\nChoose an operation:")
    print("1: Full Insert (populate politician trades from Selenium)")
    print("2: Update Politician Trades (insert only new politician trades)")
    print("3: Populate Historical Trades (fetch from Alpaca for valid tickers)")
    print("4: Update ROI Calculation for All Trades (using buy-sell pairs)")
    print("5: Update ROI for All Trades Individually (one-by-one update)")
    choice = input("Enter 1, 2, 3, 4, or 5 (or 'q' to quit): ").strip()

    if choice.lower() == 'q':
        print("Exiting.")
        return False

    if choice in ["1", "2"]:
        update_mode = (choice == "2")
        max_existing_date = None
        if update_mode:
            max_existing_date = get_max_trade_date_from_db()
            if max_existing_date:
                print(f"DB maximum trade_date: {max_existing_date}")
            else:
                print("No existing trade dates found; will insert all trades.")

        politician_urls = [
            "https://www.capitoltrades.com/politicians/P000197",
            "https://www.capitoltrades.com/politicians/D000617",
            "https://www.capitoltrades.com/politicians/G000596",
            "https://www.capitoltrades.com/politicians/G000590",
            "https://www.capitoltrades.com/politicians/C001123",
            "https://www.capitoltrades.com/politicians/W000829",
            "https://www.capitoltrades.com/politicians/F000450",
            "https://www.capitoltrades.com/politicians/J000309",
            "https://www.capitoltrades.com/politicians/D000624",
            "https://www.capitoltrades.com/politicians/L000601",
            "https://www.capitoltrades.com/politicians/D000399",
            "https://www.capitoltrades.com/politicians/T000490",
            "https://www.capitoltrades.com/politicians/C001047",
            "https://www.capitoltrades.com/politicians/M001232"
        ]
        all_trades = []
        for url in politician_urls:
            trades = scrape_politician_page(url, max_pages=10, update_mode=update_mode, max_existing_date=max_existing_date)
            all_trades.extend(trades)
        print("Final list of scraped politician trades:", all_trades)
        if choice == "1":
            insert_trades_into_db(all_trades)
        else:
            update_trades_into_db(all_trades)
    elif choice == "3":
        populate_historical_trades()
    elif choice == "4":
        update_roi_by_pairs()
    elif choice == "5":
        update_roi_for_all_trades()
    else:
        print("Invalid choice. Exiting.")
        return False

    return True

if __name__ == "__main__":
    while True:
        if not run_operation():
            break
        again = input("\nDo you want to perform another operation? (y/n): ").strip().lower()
        if again != 'y':
            print("Exiting program.")
            break
