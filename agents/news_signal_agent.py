import json
from datetime import datetime
from confluent_kafka import Consumer, Producer
from textblob import TextBlob

# -------------------------
# Kafka config
# -------------------------
CONSUMER_CONF = {
    "bootstrap.servers": "localhost:9092",
    "group.id": "news-signal-agent",
    "auto.offset.reset": "earliest",
}

PRODUCER_CONF = {
    "bootstrap.servers": "localhost:9092"
}

RAW_TOPIC = "raw_news"
OUT_TOPIC = "news_signals"

consumer = Consumer(CONSUMER_CONF)
producer = Producer(PRODUCER_CONF)


# -------------------------
# Simple, fast sentiment model
# -------------------------
def analyze_sentiment(text: str):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity  # -1 to 1

    sentiment = (
        "positive" if polarity > 0.1
        else "negative" if polarity < -0.1
        else "neutral"
    )

    confidence = abs(polarity)

    return polarity, sentiment, confidence


# -------------------------
# Main loop
# -------------------------
def run_news_signal_agent():
    print("🧠 News Signal Agent started")
    consumer.subscribe([RAW_TOPIC])

    try:
        while True:
            msg = consumer.poll(timeout=1.0)

            if msg is None:
                continue

            if msg.error():
                print(f"❌ Consumer error: {msg.error()}")
                continue

            event = json.loads(msg.value().decode("utf-8"))

            symbol = event.get("symbol")
            payload = event.get("payload", {})
            text = f"{payload.get('headline', '')} {payload.get('summary', '')}"

            polarity, sentiment, confidence = analyze_sentiment(text)

            signal_event = {
                "schema_version": "1.0",
                "event_type": "signal.news",
                "event_time": datetime.utcnow().isoformat(),
                "symbol": symbol,
                "payload": {
                    "sentiment_score": polarity,
                    "sentiment": sentiment,
                    "confidence": round(confidence, 3),
                    "impact_horizon": "short",
                    "source": payload.get("source", "")
                }
            }

            producer.produce(
                topic=OUT_TOPIC,
                value=json.dumps(signal_event)
            )
            producer.poll(0)

            print(f"📊 {symbol} | sentiment={sentiment} conf={confidence:.2f}")

    except KeyboardInterrupt:
        print("🛑 Stopping agent")

    finally:
        consumer.close()
        producer.flush()


if __name__ == "__main__":
    run_news_signal_agent()
