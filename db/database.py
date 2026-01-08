import sqlite3
import os

def get_connection():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DB_PATH = os.path.join(BASE_DIR, "data", "altdata.db")
    return sqlite3.connect(DB_PATH)

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    # Raw news
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS news (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company TEXT,
        headline TEXT,
        summary TEXT,
        source TEXT,
        published_at TEXT,
        raw_text TEXT
    )
    """)

    # AI-processed news signals
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS news_signals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        news_id INTEGER,
        sentiment REAL,
        horizon TEXT,
        confidence REAL,
        FOREIGN KEY (news_id) REFERENCES news (id)
    )
    """)

    # Stock-level aggregated signals
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS stock_signals (
        company TEXT PRIMARY KEY,
        news_momentum REAL
    )
    """)

    # Human-readable explanations
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS stock_explanations (
        company TEXT PRIMARY KEY,
        explanation TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS price_data (
        company TEXT,
        date TEXT,
        open REAL,
        high REAL,
        low REAL,
        close REAL,
        volume INTEGER,
        PRIMARY KEY (company, date)
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS earnings_signals (
        company TEXT,
        quarter TEXT,
        confidence_score REAL,
        risk_score REAL,
        outlook TEXT,
        FOREIGN KEY (company) REFERENCES stock_signals (company)
        PRIMARY KEY (company, quarter)
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS options_signals (
        company TEXT,
        implied_vol REAL,
        market_bias TEXT,
        FOREIGN KEY (company) REFERENCES stock_signals (company)
        PRIMARY KEY (company)
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reasoning_state (
        company TEXT PRIMARY KEY,
        dominant_driver TEXT,
        regime TEXT,
        signal_alignment TEXT,
        confidence REAL,
        primary_risk TEXT,
        last_updated TEXT,
        FOREIGN KEY (company) REFERENCES stock_signals (company)
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS nifty_universe (
        symbol TEXT PRIMARY KEY,
        company TEXT,
        sector TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scenario_forecasts (
        company TEXT PRIMARY KEY,
        p_upside REAL,
        p_downside REAL,
        expected_vol REAL,
        skew TEXT,
        horizon_days INTEGER,
        last_updated TEXT
    )
    """)




    conn.commit()
    conn.close()
