import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from db.database import get_connection, create_tables
FAST_AI_MODE = True

POSITIVE_WORDS = [
    "growth", "profit", "expansion", "strong", "record",
    "up", "increase", "gain", "bullish", "positive"
]

NEGATIVE_WORDS = [
    "loss", "decline", "drop", "weak", "cut",
    "down", "decrease", "risk", "negative", "concern"
]


# ADD THIS IMPORT
from textblob import TextBlob

print("AI processor file loaded")

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
print("API key loaded:", "YES" if API_KEY else "NO")

client = OpenAI(api_key=API_KEY)

# -----------------------------
# 1️⃣ FALLBACK AI (FREE, LOCAL)
# -----------------------------
def fallback_analyze(text):
    text = text.lower()

    pos_hits = sum(word in text for word in POSITIVE_WORDS)
    neg_hits = sum(word in text for word in NEGATIVE_WORDS)

    score = 0.0
    if pos_hits + neg_hits > 0:
        score = (pos_hits - neg_hits) / (pos_hits + neg_hits)

    return {
        "sentiment_score": score,          # -1 to 1
        "impact_horizon": "short",
        "confidence": min(1.0, abs(score))
    }


# -----------------------------
# 2️⃣ PRIMARY AI (CHATGPT)
# -----------------------------
def analyze_news(company, text):
    if FAST_AI_MODE:
        return fallback_analyze(text)

    # ChatGPT path (kept for later)
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Return only valid JSON."},
                {"role": "user", "content": f"Analyze news about {company}: {text}"}
            ],
            temperature=0.2
        )
        return json.loads(response.choices[0].message.content)

    except Exception:
        return fallback_analyze(text)


# -----------------------------
# 3️⃣ PIPELINE EXECUTION
# -----------------------------
def process_news(limit=500):
    print("Starting AI processing")

    create_tables()
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, company, raw_text
        FROM news
        WHERE id NOT IN (SELECT news_id FROM news_signals)
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    print("Rows to process:", len(rows))

    for news_id, company, text in rows:
        try:
            result = analyze_news(company, text)

            cursor.execute("""
                INSERT INTO news_signals (news_id, sentiment, horizon, confidence)
                VALUES (?, ?, ?, ?)
            """, (
                news_id,
                result["sentiment_score"],
                result["impact_horizon"],
                result["confidence"]
            ))

            print("Inserted signal for news_id", news_id)

        except Exception as e:
            print("FAILED for news_id", news_id, e)

    conn.commit()
    conn.close()
    print("Processing complete")

if __name__ == "__main__":
    process_news()
