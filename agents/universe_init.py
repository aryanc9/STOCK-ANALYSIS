import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "altdata.db")

NIFTY_UNIVERSE = [
    ("Bharti Airtel", "BHARTIARTL", "Telecom"),
    ("HDFC Bank", "HDFCBANK", "Banking"),
    ("Hindustan Unilever", "HINDUNILVR", "FMCG"),
    ("ICICI Bank", "ICICIBANK", "Banking"),
    ("ITC Limited", "ITC", "FMCG"),
    ("Infosys", "INFY", "IT Services"),
    ("Larsen & Toubro", "LT", "Engineering"),
    ("Reliance Industries", "RELIANCE", "Energy"),
    ("State Bank of India", "SBIN", "Banking"),
    ("Tata Consultancy Services", "TCS", "IT Services"),
]


def init_universe():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Drop old table if exists (clean reset)
    cursor.execute("DROP TABLE IF EXISTS nifty_universe")

    # Create correct schema
    cursor.execute("""
    CREATE TABLE nifty_universe (
        company TEXT NOT NULL,
        symbol TEXT NOT NULL,
        sector TEXT
    )
    """)

    # Insert canonical universe
    cursor.executemany(
        "INSERT INTO nifty_universe (company, symbol, sector) VALUES (?, ?, ?)",
        NIFTY_UNIVERSE
    )

    conn.commit()
    conn.close()

    print("✅ NIFTY universe initialized successfully")
    print(f"📊 Total stocks: {len(NIFTY_UNIVERSE)}")


if __name__ == "__main__":
    init_universe()
