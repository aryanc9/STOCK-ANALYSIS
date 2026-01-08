from db.database import get_connection, create_tables

def build_explanations():
    create_tables()
    conn = get_connection()
    cursor = conn.cursor()

    # Get stock-level signals
    cursor.execute("""
    SELECT
        ss.company,
        ss.news_momentum,
        COUNT(ns.id) as news_count,
        AVG(ns.confidence) as avg_confidence
    FROM stock_signals ss
    JOIN news n ON n.company = ss.company
    JOIN news_signals ns ON ns.news_id = n.id
    GROUP BY ss.company
    """)

    rows = cursor.fetchall()

    for company, momentum, news_count, avg_conf in rows:
        if momentum > 0.05:
            sentiment_desc = "positive"
        elif momentum < -0.05:
            sentiment_desc = "negative"
        else:
            sentiment_desc = "mixed"

        explanation = (
            f"{company} shows {sentiment_desc} recent news sentiment "
            f"based on {news_count} recent articles. "
            f"The signal confidence is {round(avg_conf, 2)}, "
            f"suggesting a {'clear' if avg_conf > 0.5 else 'moderate'} information trend."
        )

        cursor.execute("""
        INSERT OR REPLACE INTO stock_explanations (company, explanation)
        VALUES (?, ?)
        """, (company, explanation))

        print(f"Explanation generated for {company}")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    build_explanations()
