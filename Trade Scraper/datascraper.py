import os
import time
import logging
import re
import mysql.connector
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database connection settings
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'trades_db'
}
DATE_FORMAT = "%d %b %Y"

# Parse a date string or return None
def safe_parse_date(date_str):
    try:
        return datetime.strptime(date_str, DATE_FORMAT)
    except Exception:
        try:
            return datetime.strptime(date_str.replace("Sept", "Sep"), DATE_FORMAT)
        except Exception:
            logger.error(f"Failed to parse date: {date_str}")
            return None

# Check if a ticker looks valid
def is_valid_ticker(ticker):
    if not ticker:
        return False
    t = ticker.strip().lower()
    return t not in ["", "n/a", "none", "null"] and "state" not in t and "bond" not in t and len(t) <= 12

# Convert tickers like 'BRK/B' to 'BRK.B'
def adjust_ticker_for_alpaca(ticker):
    return ticker.replace('/', '.') if '/' in ticker else ticker

# Open MySQL connection
def get_db_connection():
    try:
        logger.info("Connecting to MySQL...")
        return mysql.connector.connect(**db_config)
    except mysql.connector.Error as err:
        logger.error(f"DB connection error: {err}")
        raise

# Get the latest trade date stored
def get_max_trade_date_from_db():
    try:
        cnx = get_db_connection()
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT MAX(STR_TO_DATE(trade_date, %s)) AS max_date FROM politician_trades", (DATE_FORMAT,))
        result = cursor.fetchone()
        cursor.close()
        cnx.close()
        return result['max_date'] if result and result['max_date'] else None
    except Exception as e:
        logger.error(f"Error fetching max trade date: {e}")
        return None

# Fetch unique valid tickers from trades table
def fetch_distinct_tickers_from_db():
    try:
        cnx = get_db_connection()
        cursor = cnx.cursor()
        cursor.execute("SELECT DISTINCT ticker FROM politician_trades WHERE ticker IS NOT NULL AND ticker <> 'N/A'")
        all_tickers = {r[0].strip() for r in cursor.fetchall() if r[0].strip()}
        cursor.close()
        cnx.close()
        return {t for t in all_tickers if is_valid_ticker(t)}
    except Exception as e:
        logger.error(f"Error fetching tickers: {e}")
        return set()

# Get historical price nearest to given date
def get_historical_price(ticker, date_str, price_type="close"):
    date = safe_parse_date(date_str)
    if not date:
        return None, None
    cnx = get_db_connection()
    cursor = cnx.cursor(dictionary=True)
    query = (f"SELECT timestamp, {price_type} FROM historical_trades "
             "WHERE symbol=%s ORDER BY ABS(TIMESTAMPDIFF(SECOND, timestamp, %s)) LIMIT 1;")
    cursor.execute(query, (ticker, date))
    row = cursor.fetchone()
    cursor.close()
    cnx.close()
    if row:
        return float(row[price_type]) if row[price_type] is not None else None, row['timestamp']
    return None, None

# Dummy current price fallback
def get_current_price(ticker):
    return 150.0

# Convert trade size strings to numeric range
def parse_trade_size(size_str):
    txt = size_str.strip().upper()
    if txt in ("N/A", ""):
        return None, None
    if txt.startswith("<"):
        match = re.match(r"<\s*([\d\.]+)([KM])", txt)
        if match:
            num = float(match.group(1))
            mult = 1000 if match.group(2)=='K' else 1000000
            return 0, num*mult
        return None, None
    m = re.match(r"([\d\.]+)([KM])[–-]([\d\.]+)([KM])", txt)
    if m:
        n1, u1, n2, u2 = float(m.group(1)), m.group(2), float(m.group(3)), m.group(4)
        mul1 = 1000 if u1=='K' else 1000000
        mul2 = 1000 if u2=='K' else 1000000
        return n1*mul1, n2*mul2
    return None, None

# Compute ROI percent range for a trade
def calculate_roi_range(min_amt, max_amt, ticker, buy_date, sell_date):
    try:
        buy_price, _ = get_historical_price(ticker, buy_date)
        sell_price, _ = get_historical_price(ticker, sell_date)
        if not buy_price: buy_price = get_current_price(ticker)
        if not sell_price: sell_price = get_current_price(ticker)
        if min_amt is not None and max_amt is not None:
            worst = ((sell_price - max_amt) / max_amt)*100 if max_amt else None
            best  = ((sell_price - min_amt) / min_amt)*100 if min_amt else None
            avg   = (worst + best)/2 if worst and best else None
        else:
            worst = best = avg = ((sell_price - buy_price)/buy_price)*100 if buy_price else None
        return round(worst,2) if worst else None, round(best,2) if best else None, round(avg,2) if avg else None
    except Exception as e:
        logger.error(f"ROI calc error for {ticker}: {e}")
        return None, None, None

# Scrape trades from a politician's page
def scrape_politician_page(url, max_pages=10, update_mode=False, cutoff_date=None):
    opts = Options()
    opts.add_argument("--headless")
    driver = webdriver.Chrome(options=opts)
    driver.get(url)
    time.sleep(1)
    try:
        name = driver.find_element(By.CSS_SELECTOR, "article.politician-detail-card h1").text
        party = driver.find_element(By.CSS_SELECTOR, "span.q-field.party").text
        chamber = driver.find_element(By.CSS_SELECTOR, "span.q-field.chamber").text
        state = driver.find_element(By.CSS_SELECTOR, "span.q-field.us-state-full").text
    except Exception:
        name, party, chamber, state = "Unknown", "Unknown", "Unknown", "Unknown"
    try:
        img = driver.find_element(By.CSS_SELECTOR, "img.republican").get_attribute("src")
    except Exception:
        try:
            img = driver.find_element(By.CSS_SELECTOR, "img.democrat").get_attribute("src")
        except Exception:
            img = None
    trades = []
    for page in range(1, max_pages+1):
        page_url = url if page==1 else f"{url}?page={page}"
        driver.get(page_url)
        time.sleep(1)
        try:
            rows = driver.find_element(By.CSS_SELECTOR, "table.w-full").find_elements(By.TAG_NAME, "tr")
        except Exception:
            break
        valid = 0
        for r in rows:
            cells = r.find_elements(By.TAG_NAME, "td")
            if len(cells)<7: continue
            ticker_raw = cells[0].find_element(By.CSS_SELECTOR, "span.q-field.issuer-ticker").text.split(':')[0].strip()
            if not is_valid_ticker(ticker_raw): continue
            pub = " ".join(cells[1].text.splitlines())
            trade = " ".join(cells[2].text.splitlines())
            min_p, max_p = parse_trade_size(cells[5].text)
            date_obj = safe_parse_date(trade)
            if update_mode and cutoff_date and date_obj and date_obj.date() <= cutoff_date:
                driver.quit()
                return trades
            trades.append({
                "politician": name,
                "party": party,
                "chamber": chamber,
                "state": state,
                "ticker": ticker_raw,
                "published_date": pub,
                "trade_date": trade,
                "min_purchase_price": min_p,
                "max_purchase_price": max_p,
                "image": img
            })
            valid += 1
        if valid==0:
            break
    driver.quit()
    return trades

# Insert scraped trades into DB
def insert_trades_into_db(trades):
    try:
        cnx = get_db_connection()
    except Exception:
        return
    cursor = cnx.cursor()
    q = ("INSERT INTO politician_trades (politician, party, chamber, state, ticker, "
         "published_date, trade_date, image, min_purchase_price, max_purchase_price) "
         "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)")
    for t in trades:
        vals = (t['politician'], t['party'], t['chamber'], t['state'], t['ticker'],
                t['published_date'], t['trade_date'], t['image'], t['min_purchase_price'], t['max_purchase_price'])
        try:
            cursor.execute(q, vals)
            cnx.commit()
        except Exception as e:
            logger.error(f"Insert error: {e}")
            cnx.rollback()
    cursor.close()
    cnx.close()

# Update ROI for all trades using buy-sell pairs
def update_roi_by_pairs():
    tickers = fetch_distinct_tickers_from_db()
    if not tickers:
        return
    for tk in tickers:
        cnx = get_db_connection()
        cur = cnx.cursor(dictionary=True)
        cur.execute("SELECT trade_type, trade_date, published_date, min_purchase_price, max_purchase_price "
                    "FROM politician_trades WHERE ticker=%s ORDER BY STR_TO_DATE(trade_date, %s)",
                    (tk, DATE_FORMAT))
        rows = cur.fetchall()
        cur.close()
        cnx.close()
        pairs = []
        i = 0
        while i < len(rows)-1:
            if rows[i]['trade_type'].lower()=='buy' and rows[i+1]['trade_type'].lower()=='sell':
                pairs.append((rows[i], rows[i+1]))
                i += 2
            else:
                i += 1
        if not pairs:
            continue
        rois = []
        for buy, sell in pairs:
            b, _ = get_historical_price(tk, buy['trade_date'])
            s, _ = get_historical_price(tk, sell['published_date'])
            if not b or not s:
                continue
            rois.append(((s-b)/b)*100)
        if not rois:
            continue
        avg_roi = sum(rois)/len(rois)
        min_roi, max_roi = min(rois), max(rois)
        cnx = get_db_connection()
        uc = cnx.cursor()
        try:
            uc.execute("UPDATE politician_trades SET avg_roi=%s, min_roi=%s, max_roi=%s WHERE ticker=%s",
                       (round(avg_roi,2), round(min_roi,2), round(max_roi,2), tk))
            cnx.commit()
        except Exception:
            cnx.rollback()
        uc.close()
        cnx.close()

# Update ROI for every single trade record
def update_roi_for_all_trades():
    cnx = get_db_connection()
    cs = cnx.cursor(dictionary=True)
    cu = cnx.cursor()
    cs.execute("SELECT id, ticker, trade_date, published_date, min_purchase_price, max_purchase_price FROM politician_trades")
    for r in cs.fetchall():
        worst, best, avg = calculate_roi_range(r['min_purchase_price'], r['max_purchase_price'],
                                             r['ticker'], r['trade_date'], r['published_date'])
        try:
            cu.execute("UPDATE politician_trades SET min_roi=%s, max_roi=%s, avg_roi=%s WHERE id=%s",
                       (worst, best, avg, r['id']))
            cnx.commit()
        except Exception as e:
            logger.error(f"Error updating ROI id {r['id']}: {e}")
            cnx.rollback()
    cs.close()
    cu.close()
    cnx.close()

# Fetch and populate historical data from Alpaca
def populate_historical_trades():
    API_KEY, API_SECRET = os.getenv('APCA_API_KEY'), os.getenv('APCA_API_SECRET')
    client = StockHistoricalDataClient(API_KEY, API_SECRET)
    tickers = fetch_distinct_tickers_from_db()
    if not tickers:
        return
    symbols = sorted(adjust_ticker_for_alpaca(t) for t in tickers)
    req = StockBarsRequest(symbol_or_symbols=symbols, timeframe=TimeFrame.Day,
                           start=datetime(2016,1,1), end=datetime(2025,4,17))
    data = client.get_stock_bars(req).df
    cnx = get_db_connection()
    cur = cnx.cursor()
    q = ("INSERT INTO historical_trades (symbol, timestamp, open, high, low, close, volume, trade_count, vwap) "
         "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)")
    for idx, row in data.iterrows():
        sym, ts = (row.name if isinstance(row.name, tuple) else (row.get('symbol'), row.get('timestamp')))
        try:
            cur.execute(q, (sym, ts.strftime('%Y-%m-%d %H:%M:%S'),
                            float(row['open']), float(row['high']), float(row['low']), float(row['close']),
                            int(row['volume']), row.get('trade_count'), row.get('vwap')))
            cnx.commit()
        except Exception as e:
            logger.error(f"Insert hist trade error: {e}")
            cnx.rollback()
    cur.close()
    cnx.close()

# Main interactive menu
def run_operation():
    print("\n1: Full Insert   2: Update Trades   3: Fetch Historical   4: ROI by Pairs   5: ROI Individual   q: Quit")
    choice = input("Enter choice: ").strip().lower()
    if choice == 'q':
        return False
<<<<<<< HEAD

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
=======
    if choice in ['1', '2']:
        update = (choice == '2')
        cutoff = get_max_trade_date_from_db() if update else None
        if update and cutoff:
            print(f"Skipping trades older than {cutoff}")
        urls = [
            "https://www.capitoltrades.com/politicians/P000197",
            "https://www.capitoltrades.com/politicians/D000617"
        ]
        all_trades = []
        for u in urls:
            all_trades += scrape_politician_page(u, update_mode=update, cutoff_date=cutoff)
>>>>>>> ScraperUpdate
        insert_trades_into_db(all_trades)
    elif choice == '3':
        populate_historical_trades()
    elif choice == '4':
        update_roi_by_pairs()
    elif choice == '5':
        update_roi_for_all_trades()
    else:
        print("Invalid choice.")
        return False
    return True

if __name__ == '__main__':
    while run_operation():
        if input("\nAnother? (y/n): ").strip().lower() != 'y':
            break
    print("Exiting.")
