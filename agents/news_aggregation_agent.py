import json
import sqlite3
import os
from datetime import datetime
from math import log
from confluent_kafka import Consumer

# -------------------------
# Kafka config
# -------------------------
CONSUMER_CONF = {
    "bootstrap.servers": "localhost:9092",
    "group.id": "news-aggregation-agent",
    "auto.offset.reset": "earliest",
}

TOPIC = "news_signals"

# -------------------------
# Database
# -------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "altdata.db")

consumer = Consumer(CONSUMER_CONF)


def run_aggregation_agent():
    print("🧮 News Aggregation Agent started")

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
            symbol = event["symbol"]

            # --- Pull last 100 signals for this symbol ---
            cursor.execute("""
                SELECT sentiment_score, confidence
                FROM news_signals
                WHERE symbol = ?
                ORDER BY event_time DESC
                LIMIT 100
            """, (symbol,))

            rows = cursor.fetchall()
            if not rows:
                continue

            sentiments = [r[0] for r in rows]
            confidences = [r[1] for r in rows]

            news_momentum = sum(sentiments) / len(sentiments)
            avg_confidence = sum(confidences) / len(confidences)
            signal_strength = news_momentum * avg_confidence * log(len(rows) + 1)

            cursor.execute("""
                INSERT INTO stock_signals
                (symbol, news_momentum, avg_confidence, signal_strength, last_updated)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(symbol) DO UPDATE SET
                    news_momentum = excluded.news_momentum,
                    avg_confidence = excluded.avg_confidence,
                    signal_strength = excluded.signal_strength,
                    last_updated = excluded.last_updated
            """, (
                symbol,
                round(news_momentum, 4),
                round(avg_confidence, 4),
                round(signal_strength, 4),
                datetime.utcnow().isoformat()
            ))

            conn.commit()

            print(
                f"📈 {symbol} | momentum={news_momentum:.3f} "
                f"conf={avg_confidence:.2f} strength={signal_strength:.2f}"
            )

    except KeyboardInterrupt:
        print("🛑 Stopping aggregation agent")

    finally:
        consumer.close()
        conn.close()


if __name__ == "__main__":
    run_aggregation_agent()
