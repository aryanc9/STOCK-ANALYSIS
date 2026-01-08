import random
from db.database import get_connection, create_tables

def run_options_agent():
    create_tables()
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT company, COUNT(*) as news_cnt
    FROM news
    GROUP BY company
    """)
    companies = cursor.fetchall()

    for company, news_cnt in companies:
        random.seed(hash(company) % 9999)

        implied_vol = round(0.2 + random.random() * 0.4, 2)

        if implied_vol > 0.45:
            bias = "High Uncertainty"
        elif implied_vol > 0.3:
            bias = "Moderate Risk"
        else:
            bias = "Calm Expectations"

        cursor.execute("""
        INSERT OR REPLACE INTO options_signals
        VALUES (?, ?, ?)
        """, (company, implied_vol, bias))

        print(f"Options signal generated for {company}")

    conn.commit()
    conn.close()
    print("📊 Options signals ready")

if __name__ == "__main__":
    run_options_agent()
