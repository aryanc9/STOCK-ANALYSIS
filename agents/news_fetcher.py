import feedparser
from db.database import get_connection, create_tables

NEWS_SOURCES = [
    "https://news.google.com/rss/search?q={query}+stock+india",
    "https://feeds.finance.yahoo.com/rss/2.0/headline?s={query}.NS"
]

def fetch_news():
    create_tables()
    conn = get_connection()
    cursor = conn.cursor()

    # 🔹 Load universe from DB (NOT JSON)
    cursor.execute("""
    SELECT symbol, company
    FROM nifty_universe
    """)
    stocks = cursor.fetchall()

    for symbol, company in stocks:
        print(f"Fetching news for {company}")

        query = company.replace(" ", "+")

        for source in NEWS_SOURCES:
            feed_url = source.format(query=query)
            feed = feedparser.parse(
                feed_url,
                request_headers={"User-Agent": "Mozilla/5.0"}
            )

            for entry in feed.entries:
                headline = entry.get("title", "")
                summary = entry.get("summary", "")
                published = entry.get("published", "")

                if not headline:
                    continue

                cursor.execute("""
                INSERT INTO news
                (company, headline, summary, source, published_at, raw_text)
                VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    company,
                    headline,
                    summary,
                    feed_url,
                    published,
                    f"{headline} {summary}"
                ))

                print("  ✔", headline[:80])

    conn.commit()
    conn.close()
    print("📰 News ingestion complete")

if __name__ == "__main__":
    fetch_news()
