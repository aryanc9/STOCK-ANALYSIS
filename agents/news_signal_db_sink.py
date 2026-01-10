import json
import sqlite3
import os
from confluent_kafka import Consumer

# -------------------------
# Kafka config
# -------------------------
CONSUMER_CONF = {
    "bootstrap.servers": "localhost:9092",
    "group.id": "news-signal-db-sink",
    "auto.offset.reset": "earliest",
}

TOPIC = "news_signals"

# -------------------------
# Database
# -------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "altdata.db")

consumer = Consumer(CONSUMER_CONF)


def run_db_sink():
    print("🗄️ News Signal DB Sink started")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    consumer.subscribe([TOPIC])

    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                print("❌ Kafka error:", msg.error())
                continue

            event = json.loads(msg.value().decode("utf-8"))
            payload = event["payload"]

            cursor.execute("""
                INSERT INTO news_signals (
                    symbol,
                    sentiment_score,
                    sentiment,
                    confidence,
                    impact_horizon,
                    source,
                    event_time
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                event["symbol"],
                payload["sentiment_score"],
                payload["sentiment"],
                payload["confidence"],
                payload["impact_horizon"],
                payload["source"],
                event["event_time"]
            ))

            conn.commit()

            print(f"🗄️ Stored signal for {event['symbol']}")

    except KeyboardInterrupt:
        print("🛑 Stopping DB sink")

    finally:
        consumer.close()
        conn.close()


if __name__ == "__main__":
    run_db_sink()
