import requests
import sqlite3
from db.database import get_connection, create_tables

YAHOO_CHART_URL = "https://query2.finance.yahoo.com/v8/finance/chart/{symbol}.NS"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json"
}


def fetch_yahoo_prices(symbol):
    url = YAHOO_CHART_URL.format(symbol=symbol)
    r = requests.get(url, headers=HEADERS, timeout=15)

    if r.status_code != 200:
        return None

    data = r.json()
    try:
        result = data["chart"]["result"][0]
    except Exception:
        return None

    timestamps = result["timestamp"]
    indicators = result["indicators"]["quote"][0]

    rows = []
    for i in range(len(timestamps)):
        rows.append({
            "date": timestamps[i],
            "open": indicators["open"][i],
            "high": indicators["high"][i],
            "low": indicators["low"][i],
            "close": indicators["close"][i],
            "volume": indicators["volume"][i],
        })

    return rows


def run_price_data_agent():
    create_tables()
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT symbol FROM nifty_universe")
    symbols = [row[0] for row in cursor.fetchall()]

    inserted = 0
    print("🚀 Starting Yahoo Chart price ingestion")

    for symbol in symbols:
        print(f"📈 Fetching {symbol}.NS")
        rows = fetch_yahoo_prices(symbol)

        if not rows:
            print("  ❌ No data")
            continue

        for r in rows:
            if r["close"] is None:
                continue

            cursor.execute("""
            INSERT OR REPLACE INTO price_data
            (company, date, open, high, low, close, volume)
            VALUES (?, datetime(?, 'unixepoch'), ?, ?, ?, ?, ?)
            """, (
                symbol,
                r["date"],
                r["open"],
                r["high"],
                r["low"],
                r["close"],
                r["volume"] if r["volume"] else 0
            ))
            inserted += 1

        conn.commit()
        print(f"  ✅ Inserted {len(rows)} rows")

    conn.close()
    print(f"📊 Price ingestion complete. Rows inserted: {inserted}")


if __name__ == "__main__":
    run_price_data_agent()
