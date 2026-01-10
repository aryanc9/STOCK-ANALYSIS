from confluent_kafka import Producer
import json
from datetime import datetime

producer = Producer({
    "bootstrap.servers": "localhost:9092"
})

event = {
    "schema_version": "1.0",
    "event_type": "news.raw",
    "event_time": datetime.utcnow().isoformat(),
    "symbol": "RELIANCE",
    "payload": {
        "company": "Reliance Industries",
        "headline": "Reliance launches new green energy initiative",
        "source": "test"
    }
}

producer.produce(
    topic="raw_news",
    value=json.dumps(event)
)

producer.flush()
print("✅ Event published to raw_news")
