from datetime import datetime
from db.database import get_connection, create_tables

def sigmoid(x):
    return 1 / (1 + pow(2.71828, -x))

def compute_probabilities(news_z, earnings_z, risk_z, regime):
    # Base directional signal
    direction_score = 0.6 * news_z + 0.4 * earnings_z

    # Risk penalty
    risk_penalty = 0.5 * max(0, risk_z)

    raw_up = direction_score - risk_penalty
    raw_down = -direction_score + risk_penalty

    p_up = sigmoid(raw_up)
    p_down = sigmoid(raw_down)

    # Normalize
    total = p_up + p_down
    p_up /= total
    p_down /= total

    return round(p_up, 2), round(p_down, 2)

def expected_volatility(risk_z):
    base = 0.18
    return round(base + 0.1 * max(0, risk_z), 2)

def skew_label(p_up, p_down):
    if p_up - p_down > 0.15:
        return "Upside Skewed"
    if p_down - p_up > 0.15:
        return "Downside Skewed"
    return "Balanced"

def run_scenario_agent():
    create_tables()
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        rs.company,
        ss.news_momentum,
        es.confidence_score,
        os.implied_vol,
        rs.regime
    FROM reasoning_state rs
    JOIN stock_signals ss ON ss.company = rs.company
    JOIN earnings_signals es ON es.company = rs.company
    JOIN options_signals os ON os.company = rs.company
    """)

    rows = cursor.fetchall()

    for company, news_z, earnings_z, risk_z, regime in rows:
        p_up, p_down = compute_probabilities(news_z, earnings_z, risk_z, regime)
        vol = expected_volatility(risk_z)
        skew = skew_label(p_up, p_down)

        cursor.execute("""
        INSERT OR REPLACE INTO scenario_forecasts
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            company,
            p_up,
            p_down,
            vol,
            skew,
            30,
            datetime.utcnow().isoformat()
        ))

        print(f"🔮 Scenario updated for {company}")

    conn.commit()
    conn.close()
    print("✅ Probabilistic scenarios generated")

if __name__ == "__main__":
    run_scenario_agent()
