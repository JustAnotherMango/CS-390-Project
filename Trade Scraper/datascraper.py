# datascraper.py

from dotenv import load_dotenv
load_dotenv()

import os
import time
import logging
import re
import mysql.connector
from datetime import datetime
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame

# -----------------------------------------------------------------------------
# CONFIG & LOGGING
# -----------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'trades_db'
}
DATE_FORMAT = "%d %b %Y"

# -----------------------------------------------------------------------------
# HELPERS
# -----------------------------------------------------------------------------
def safe_parse_date(s: str):
    """Parse a date string or return None."""
    try:
        return datetime.strptime(s, DATE_FORMAT)
    except Exception:
        try:
            return datetime.strptime(s.replace("Sept", "Sep"), DATE_FORMAT)
        except Exception:
            logger.error(f"Failed to parse date: {s!r}")
            return None

def is_valid_ticker(t: str):
    """Return False for blank, N/A, or invalid tickers."""
    if not t:
        return False
    t = t.strip().lower()
    return all([
        t not in ("", "n/a", "none", "null"),
        "state" not in t,
        "bond" not in t,
        len(t) <= 12
    ])

def adjust_ticker_for_alpaca(t: str):
    """Convert 'BRK/B' to 'BRK.B'."""
    return t.replace("/", ".") if "/" in t else t

def get_db_connection():
    """Open and return a MySQL connection."""
    try:
        logger.info("Connecting to MySQL...")
        return mysql.connector.connect(**db_config)
    except mysql.connector.Error as e:
        logger.error(f"DB connection error: {e}")
        raise

def get_max_trade_date_from_db():
    """Return the most recent trade_date in politician_trades."""
    try:
        cnx = get_db_connection()
        cur = cnx.cursor(dictionary=True)
        cur.execute(
            "SELECT MAX(STR_TO_DATE(trade_date, %s)) AS max_date "
            "FROM politician_trades",
            (DATE_FORMAT,)
        )
        row = cur.fetchone()
        cur.close(); cnx.close()
        return row['max_date'] if row and row['max_date'] else None
    except Exception as e:
        logger.error(f"Error fetching max trade date: {e}")
        return None

def fetch_distinct_tickers_from_db():
    """Fetch unique valid tickers from politician_trades."""
    try:
        cnx = get_db_connection()
        cur = cnx.cursor()
        cur.execute(
            "SELECT DISTINCT ticker FROM politician_trades "
            "WHERE ticker IS NOT NULL AND ticker <> 'N/A'"
        )
        tickers = {r[0].strip() for r in cur.fetchall() if r[0].strip()}
        cur.close(); cnx.close()
        return {t for t in tickers if is_valid_ticker(t)}
    except Exception as e:
        logger.error(f"Error fetching tickers: {e}")
        return set()

def get_historical_price(symbol: str, date_str: str, price_type="close"):
    """Return (price, timestamp) nearest to date_str."""
    dt = safe_parse_date(date_str)
    if not dt:
        return None, None
    cnx = get_db_connection()
    cur = cnx.cursor(dictionary=True)
    query = (
        f"SELECT timestamp, {price_type} FROM historical_trades "
        "WHERE symbol=%s "
        "ORDER BY ABS(TIMESTAMPDIFF(SECOND, timestamp, %s)) "
        "LIMIT 1"
    )
    cur.execute(query, (symbol, dt))
    row = cur.fetchone()
    cur.close(); cnx.close()
    if row and row[price_type] is not None:
        return float(row[price_type]), row['timestamp']
    return None, None

def get_current_price(_: str):
    """Dummy fallback price."""
    return 150.0

def parse_trade_size(txt: str):
    """Convert '500K–1M' or '< 1K' into numeric (min, max)."""
    s = txt.strip().upper()
    if s in ("", "N/A"):
        return None, None
    if s.startswith("<"):
        m = re.match(r"<\s*([\d\.]+)([KM])", s)
        if m:
            num = float(m.group(1))
            mult = 1000 if m.group(2) == 'K' else 1000000
            return 0, num * mult
        return None, None
    m = re.match(r"([\d\.]+)([KM])[–-]([\d\.]+)([KM])", s)
    if m:
        n1,u1,n2,u2 = float(m.group(1)), m.group(2), float(m.group(3)), m.group(4)
        m1 = 1000 if u1=='K' else 1000000
        m2 = 1000 if u2=='K' else 1000000
        return n1*m1, n2*m2
    return None, None

def calculate_roi_range(min_amt, max_amt, symbol, buy_dt, sell_dt):
    """Compute worst/best/average ROI%."""
    try:
        bp,_ = get_historical_price(symbol, buy_dt)
        sp,_ = get_historical_price(symbol, sell_dt)
        if not bp: bp = get_current_price(symbol)
        if not sp: sp = get_current_price(symbol)
        if min_amt is not None and max_amt is not None:
            worst = ((sp - max_amt) / max_amt) * 100 if max_amt else None
            best  = ((sp - min_amt) / min_amt) * 100 if min_amt else None
            avg   = (worst + best)/2 if worst is not None and best is not None else None
        else:
            worst = best = avg = ((sp - bp) / bp) * 100 if bp else None
        return (
            round(worst,2) if worst is not None else None,
            round(best,2)  if best  is not None else None,
            round(avg,2)   if avg   is not None else None
        )
    except Exception as e:
        logger.error(f"ROI error for {symbol}: {e}")
        return None, None, None

# -----------------------------------------------------------------------------
# SCRAPING & INSERTION
# -----------------------------------------------------------------------------
def scrape_politician_page(url, max_pages=10, update_mode=False, cutoff_date=None):
    """Scrape trades from one politician's page."""
    opts = Options(); opts.add_argument("--headless")
    driver = webdriver.Chrome(options=opts)
    driver.get(url); time.sleep(1)

    # header
    try:
        name    = driver.find_element(By.CSS_SELECTOR, "article.politician-detail-card h1").text
        party   = driver.find_element(By.CSS_SELECTOR, "span.q-field.party").text
        chamber = driver.find_element(By.CSS_SELECTOR, "span.q-field.chamber").text
        state   = driver.find_element(By.CSS_SELECTOR, "span.q-field.us-state-full").text
    except Exception:
        name, party, chamber, state = "Unknown", "Unknown", "Unknown", "Unknown"

    # image
    try:
        img = driver.find_element(By.CSS_SELECTOR, "img.republican").get_attribute("src")
    except:
        try:
            img = driver.find_element(By.CSS_SELECTOR, "img.democrat").get_attribute("src")
        except:
            img = None

    trades = []
    for page in tqdm(range(1, max_pages+1), desc=f"Scraping pages for {name}"):
        page_url = url if page==1 else f"{url}?page={page}"
        driver.get(page_url); time.sleep(1)
        try:
            rows = driver.find_element(By.CSS_SELECTOR, "table.w-full") \
                         .find_elements(By.TAG_NAME, "tr")
        except:
            break

        valid = 0
        for r in rows:
            cells = r.find_elements(By.TAG_NAME, "td")
            if len(cells) < 7:
                continue

            traded_issuer = cells[0].text.strip()
            ticker_raw    = cells[0].find_element(By.CSS_SELECTOR, "span.q-field.issuer-ticker") \
                                  .text.split(":")[0].strip()
            if not is_valid_ticker(ticker_raw):
                continue

            pub = " ".join(cells[1].text.splitlines())
            td  = " ".join(cells[2].text.splitlines())
            gap = cells[3].text.strip()
            tt  = cells[4].text.strip()
            mn, mx = parse_trade_size(cells[5].text)

            dt_obj = safe_parse_date(td)
            if update_mode and cutoff_date and dt_obj and dt_obj.date() <= cutoff_date:
                driver.quit()
                return trades

            trades.append({
                "politician": name, "party": party, "chamber": chamber, "state": state,
                "traded_issuer": traded_issuer, "ticker": ticker_raw,
                "published_date": pub, "trade_date": td,
                "gap_unit": None, "gap": gap, "trade_type": tt, "page": page,
                "min_purchase_price": mn, "max_purchase_price": mx, "image": img
            })
            valid += 1

        if valid == 0:
            break

    driver.quit()
    return trades

def insert_trades_into_db(trades):
    """Insert scraped trades into DB with a progress bar."""
    try:
        cnx = get_db_connection()
    except:
        return

    cursor = cnx.cursor()
    q = """
    INSERT INTO politician_trades (
      politician, party, chamber, state,
      traded_issuer, ticker,
      published_date, trade_date,
      gap_unit, gap, trade_type, page,
      image, min_purchase_price, max_purchase_price
    ) VALUES (
      %s, %s, %s, %s,
      %s, %s,
      %s, %s,
      %s, %s, %s, %s,
      %s, %s, %s
    )
    """
    for t in tqdm(trades, desc="Inserting trades"):
        vals = (
            t["politician"], t["party"], t["chamber"], t["state"],
            t["traded_issuer"], t["ticker"],
            t["published_date"], t["trade_date"],
            t["gap_unit"], t["gap"], t["trade_type"], t["page"],
            t["image"], t["min_purchase_price"], t["max_purchase_price"]
        )
        try:
            cursor.execute(q, vals)
            cnx.commit()
        except Exception as e:
            logger.error(f"Insert error: {e}")
            cnx.rollback()

    cursor.close()
    cnx.close()

# -----------------------------------------------------------------------------
# ROI CALCULATIONS
# -----------------------------------------------------------------------------
def update_roi_by_pairs():
    """Compute & update ROI based on buy–sell pairs per ticker."""
    tickers = fetch_distinct_tickers_from_db()
    for tk in tqdm(tickers, desc="Updating ROI by pairs"):
        cnx = get_db_connection()
        cur = cnx.cursor(dictionary=True)
        cur.execute(
            """
            SELECT id, trade_type, trade_date, published_date
            FROM politician_trades
            WHERE ticker=%s
            ORDER BY STR_TO_DATE(trade_date, %s) ASC
            """,
            (tk, DATE_FORMAT)
        )
        rows = cur.fetchall()
        cur.close(); cnx.close()

        clean = []
        for r in rows:
            tt = r.get('trade_type')
            if not isinstance(tt, str):
                logger.warning(f"Skipping id={r.get('id')} for {tk}: invalid trade_type")
                continue
            clean.append(r)

        pairs = []
        i = 0
        while i < len(clean) - 1:
            if (clean[i]['trade_type'].strip().lower() == "buy" and
                clean[i+1]['trade_type'].strip().lower() == "sell"):
                pairs.append((clean[i], clean[i+1]))
                i += 2
            else:
                i += 1

        if not pairs:
            continue

        rois = []
        for buy, sell in pairs:
            b,_ = get_historical_price(tk, buy['trade_date'])
            s,_ = get_historical_price(tk, sell['published_date'])
            if b and s:
                rois.append(((s - b)/b)*100)

        if not rois:
            continue

        avg_roi = sum(rois)/len(rois)
        min_roi, max_roi = min(rois), max(rois)

        cnx = get_db_connection()
        uc = cnx.cursor()
        try:
            uc.execute(
                "UPDATE politician_trades SET avg_roi=%s, min_roi=%s, max_roi=%s WHERE ticker=%s",
                (round(avg_roi,2), round(min_roi,2), round(max_roi,2), tk)
            )
            cnx.commit()
        except Exception as e:
            logger.error(f"Error updating ROI for {tk}: {e}")
            cnx.rollback()
        finally:
            uc.close(); cnx.close()

def update_roi_for_all_trades():
    """Compute & update ROI for each row individually with progress bar."""
    cnx = get_db_connection()
    cs = cnx.cursor(dictionary=True)
    cu = cnx.cursor()
    cs.execute(
        """
        SELECT id, ticker, trade_date, published_date,
               min_purchase_price, max_purchase_price
        FROM politician_trades
        """
    )
    records = cs.fetchall()
    cs.close()

    for r in tqdm(records, desc="Updating ROI per trade"):
        worst, best, avg = calculate_roi_range(
            r['min_purchase_price'], r['max_purchase_price'],
            r['ticker'], r['trade_date'], r['published_date']
        )
        try:
            cu.execute(
                "UPDATE politician_trades SET min_roi=%s, max_roi=%s, avg_roi=%s WHERE id=%s",
                (worst, best, avg, r['id'])
            )
            cnx.commit()
        except Exception as e:
            logger.error(f"Error updating ROI id {r['id']}: {e}")
            cnx.rollback()

    cu.close()
    cnx.close()

# -----------------------------------------------------------------------------
# HISTORICAL DATA POPULATION
# -----------------------------------------------------------------------------
def populate_historical_trades():
    """Fetch distinct tickers, pull bars from Alpaca, insert into historical_trades."""
    API_KEY    = os.getenv("APCA_API_KEY")    or "PK3JXYAJVNEAWAJ1X3I6"
    API_SECRET = os.getenv("APCA_API_SECRET") or "TjNn9ltUdOaw80zerWy4lhpCZRa9qwAhNb8ItR3g"
    if not API_KEY or not API_SECRET:
        raise ValueError("Missing Alpaca credentials in .env")
    client = StockHistoricalDataClient(API_KEY, API_SECRET)

    tickers = fetch_distinct_tickers_from_db()
    if not tickers:
        logger.info("No tickers to fetch.")
        return

    symbols = sorted(adjust_ticker_for_alpaca(t) for t in tickers)
    logger.info(f"Fetching historical data for: {symbols}")

    req = StockBarsRequest(
        symbol_or_symbols=symbols,
        timeframe=TimeFrame.Day,
        start=datetime(2016,1,1),
        end=datetime.now()
    )
    bars = client.get_stock_bars(req).df

    cnx = get_db_connection()
    cur = cnx.cursor()
    insert_q = """
        INSERT INTO historical_trades
          (symbol, timestamp, open, high, low, close, volume, trade_count, vwap)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """

    for idx, row in tqdm(bars.iterrows(), total=len(bars), desc="Inserting historical trades"):
        if isinstance(idx, tuple):
            sym, ts = idx
        else:
            sym = row.get("symbol")
            ts  = row.get("timestamp")
        try:
            cur.execute(insert_q, (
                sym,
                ts.strftime("%Y-%m-%d %H:%M:%S"),
                float(row['open']), float(row['high']), float(row['low']),
                float(row['close']), int(row['volume']),
                row.get('trade_count'), row.get('vwap')
            ))
            cnx.commit()
        except Exception as e:
            logger.error(f"Error inserting {sym}@{ts}: {e}")
            cnx.rollback()

    cur.close()
    cnx.close()
    logger.info("Historical trades populated successfully.")

# -----------------------------------------------------------------------------
# MAIN MENU
# -----------------------------------------------------------------------------
def run_operation():
    """Interactive menu for scraper operations."""
    print("\n1: Full Insert   2: Update Trades   3: Fetch Historical   "
          "4: ROI by Pairs   5: ROI Individual   q: Quit")
    choice = input("Enter choice: ").strip().lower()
    if choice == 'q':
        return False
    if choice in ('1','2'):
        update = choice == '2'
        cutoff = get_max_trade_date_from_db() if update else None
        if update and cutoff:
            print(f"Skipping trades older than {cutoff}")
        urls = [
            "https://www.capitoltrades.com/politicians/P000197",
            "https://www.capitoltrades.com/politicians/D000617",
            "https://www.capitoltrades.com/politicians/G000596",
            "https://www.capitoltrades.com/politicians/D000624"
        ]
        all_trades = []
        for u in urls:
            all_trades += scrape_politician_page(u, update_mode=update, cutoff_date=cutoff)
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