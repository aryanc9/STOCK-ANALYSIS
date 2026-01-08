from db.database import get_connection, create_tables

def build_news_signal():
    create_tables()
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS stock_signals (
        company TEXT PRIMARY KEY,
        news_momentum REAL
    )
    """)

    cursor.execute("""
    SELECT
        n.company,
        COUNT(*) as news_count,
        AVG(s.sentiment * s.confidence) as momentum
    FROM news_signals s
    JOIN news n ON n.id = s.news_id
    GROUP BY n.company
    """)

    rows = cursor.fetchall()

    print("Aggregating signals for companies:")
    print(rows)

    for company, count, momentum in rows:
        cursor.execute("""
        INSERT OR REPLACE INTO stock_signals (company, news_momentum)
        VALUES (?, ?)
        """, (company, momentum))

        print(f"{company} → momentum={round(momentum, 4)} from {count} articles")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    build_news_signal()
