from datetime import datetime
from db.database import get_connection, create_tables

NEUTRAL_NEWS = 0.0
NEUTRAL_EARNINGS = 0.0
NEUTRAL_RISK = 0.0

def classify_regime(news_z, earnings_z, risk_z):
    if risk_z > 1.0:
        return "High Risk Regime"
    if news_z > 1.0 and earnings_z > 0.5:
        return "Momentum Regime"
    if news_z < -1.0 and earnings_z < -0.5:
        return "Deteriorating Regime"
    return "Neutral Regime"

def dominant_driver(news_z, earnings_z, risk_z):
    if abs(news_z) >= max(abs(earnings_z), abs(risk_z)):
        return "Information Flow"
    if abs(earnings_z) >= abs(risk_z):
        return "Fundamentals"
    return "Market Risk"

def signal_alignment(news_z, earnings_z):
    if news_z > 0.5 and earnings_z > 0.5:
        return "Aligned Positive"
    if news_z < -0.5 and earnings_z < -0.5:
        return "Aligned Negative"
    return "Mixed / Insufficient"

def compute_confidence(news_z, earnings_z, risk_z, coverage):
    base = 0.5 + 0.2 * max(abs(news_z), abs(earnings_z))
    if risk_z > 1.0:
        base -= 0.2
    if coverage != "Full":
        base -= 0.2
    return round(max(0.1, min(base, 0.9)), 2)

def run_reasoning_agent():
    create_tables()
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        u.company,
        COALESCE(ss.news_momentum, ?),
        COALESCE(es.confidence_score, ?),
        COALESCE(os.implied_vol, ?),
        ss.news_momentum IS NOT NULL,
        es.confidence_score IS NOT NULL,
        os.implied_vol IS NOT NULL
    FROM nifty_universe u
    LEFT JOIN stock_signals ss ON ss.company = u.company
    LEFT JOIN earnings_signals es ON es.company = u.company
    LEFT JOIN options_signals os ON os.company = u.company
    """, (NEUTRAL_NEWS, NEUTRAL_EARNINGS, NEUTRAL_RISK))

    rows = cursor.fetchall()

    for (company,
         news_z, earnings_z, risk_z,
         has_news, has_earnings, has_options) in rows:

        coverage_count = sum([has_news, has_earnings, has_options])
        if coverage_count == 3:
            coverage = "Full"
        elif coverage_count == 2:
            coverage = "Partial"
        else:
            coverage = "Sparse"

        regime = classify_regime(news_z, earnings_z, risk_z)
        driver = dominant_driver(news_z, earnings_z, risk_z)
        alignment = signal_alignment(news_z, earnings_z)
        confidence = compute_confidence(news_z, earnings_z, risk_z, coverage)

        if coverage == "Sparse":
            primary_risk = "Insufficient data"
        elif regime == "High Risk Regime":
            primary_risk = "Volatility expansion"
        else:
            primary_risk = "No dominant risk"

        cursor.execute("""
        INSERT OR REPLACE INTO reasoning_state
        (company, dominant_driver, regime, signal_alignment,
         confidence, primary_risk, last_updated, coverage)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            company,
            driver,
            regime,
            alignment,
            confidence,
            primary_risk,
            datetime.utcnow().isoformat(),
            coverage
        ))

        print(f"🧠 Reasoned: {company} ({coverage})")

    conn.commit()
    conn.close()
    print("✅ Agentic reasoning v3 complete")

if __name__ == "__main__":
    run_reasoning_agent()
