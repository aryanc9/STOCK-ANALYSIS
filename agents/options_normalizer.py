import numpy as np
from db.database import get_connection, create_tables

def run():
    create_tables()
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT company, implied_vol
    FROM options_signals
    """)
    rows = cursor.fetchall()

    if not rows:
        print("No options signals found")
        return

    values = np.array([r[1] for r in rows])
    mean = values.mean()
    std = values.std() if values.std() > 0 else 1

    for company, value in rows:
        z = (value - mean) / std
        cursor.execute("""
        UPDATE options_signals
        SET implied_vol = ?
        WHERE company = ?
        """, (round(z, 3), company))

    conn.commit()
    conn.close()
    print("📊 Options risk normalized across universe")

if __name__ == "__main__":
    run()
