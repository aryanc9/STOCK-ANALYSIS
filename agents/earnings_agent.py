from db.database import get_connection, create_tables

# Simple keyword-based language model (fast + explainable)
CONFIDENT_WORDS = [
    "strong", "confident", "growth", "momentum",
    "robust", "improving", "opportunity"
]

RISK_WORDS = [
    "uncertain", "risk", "challenge", "pressure",
    "slowdown", "headwind", "volatile"
]

# Simulated earnings summaries (stand-in for transcripts)
EARNINGS_SUMMARIES = {
    "Reliance Industries": {
        "Q4-2024": "The company reported strong growth across segments with confident outlook despite global volatility."
    },
    "Infosys": {
        "Q4-2024": "Management highlighted cautious demand environment and ongoing cost pressures."
    },
    "Tata Consultancy Services": {
        "Q4-2024": "The quarter showed steady performance with stable margins and moderate growth expectations."
    },
    "HDFC Bank": {
        "Q4-2024": "Results reflected resilient performance with controlled risk and improving asset quality."
    },
    "ITC Limited": {
        "Q4-2024": "The company expressed confidence in FMCG growth while noting inflationary pressures."
    }
}

def score_text(text):
    text = text.lower()

    confidence_hits = sum(word in text for word in CONFIDENT_WORDS)
    risk_hits = sum(word in text for word in RISK_WORDS)

    confidence_score = confidence_hits / max(1, len(CONFIDENT_WORDS))
    risk_score = risk_hits / max(1, len(RISK_WORDS))

    if confidence_score > risk_score:
        outlook = "Positive"
    elif risk_score > confidence_score:
        outlook = "Cautious"
    else:
        outlook = "Neutral"

    return confidence_score, risk_score, outlook

def run_earnings_agent():
    create_tables()
    conn = get_connection()
    cursor = conn.cursor()

    for company, quarters in EARNINGS_SUMMARIES.items():
        for quarter, summary in quarters.items():
            conf, risk, outlook = score_text(summary)

            cursor.execute("""
            INSERT OR REPLACE INTO earnings_signals
            VALUES (?, ?, ?, ?, ?)
            """, (
                company,
                quarter,
                round(conf, 2),
                round(risk, 2),
                outlook
            ))

            print(f"Earnings processed for {company} {quarter}")

    conn.commit()
    conn.close()
    print("📊 Earnings signals generated")

if __name__ == "__main__":
    run_earnings_agent()
