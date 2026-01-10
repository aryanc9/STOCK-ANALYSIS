import feedparser
import json
import sqlite3
import os
from datetime import datetime
from confluent_kafka import Producer

# -------------------------
# Database (universe source)
# -------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "altdata.db")

def load_universe():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT company, symbol FROM nifty_universe")
    rows = cursor.fetchall()
    conn.close()
    return rows


# -------------------------
# Kafka producer
# -------------------------
producer = Producer({
    "bootstrap.servers": "localhost:9092"
})

TOPIC = "raw_news"

NEWS_SOURCES = [
    "https://news.google.com/rss/search?q={query}+stock+india",
    "https://feeds.finance.yahoo.com/rss/2.0/headline?s={symbol}.NS"
]


def publish_event(event):
    producer.produce(
        topic=TOPIC,
        value=json.dumps(event)
    )
    producer.poll(0)


def run_news_fetcher():
    universe = load_universe()

    if not universe:
        print("❌ Universe empty. Run init_universe first.")
        return

    print(f"📰 Fetching news for {len(universe)} stocks")

    for company, symbol in universe:
        for source in NEWS_SOURCES:
            url = source.format(
                query=company.replace(" ", "+"),
                symbol=symbol
            )

            feed = feedparser.parse(
                url,
                request_headers={"User-Agent": "Mozilla/5.0"}
            )

            for entry in feed.entries:
                event = {
                    "schema_version": "1.0",
                    "event_type": "news.raw",
                    "event_time": datetime.utcnow().isoformat(),
                    "symbol": symbol,
                    "payload": {
                        "company": company,
                        "headline": entry.get("title", ""),
                        "summary": entry.get("summary", ""),
                        "source": feed.feed.get("title", ""),
                        "published_at": entry.get("published", ""),
                        "url": entry.get("link", "")
                    }
                }

                publish_event(event)
                print(f"📤 {symbol} | {entry.get('title', '')[:60]}")

    producer.flush()
    print("✅ News fetcher completed")


if __name__ == "__main__":
    run_news_fetcher()
