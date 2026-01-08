import streamlit as st
import sqlite3
import os
import pandas as pd
import altair as alt

# -------------------------
# Page config
# -------------------------
st.set_page_config(
    page_title="Stock Intelligence Platform",
    layout="wide"
)

st.title("📊 Stock Intelligence Platform (Alternative Data)")
st.caption(
    "Search a stock to view alternative data signals, trends, and explanations. "
    "All data is processed automatically."
)

USE_LLM = st.checkbox("Enable AI Explanation (optional)", value=False)

# -------------------------
# Database connection
# -------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "altdata.db")
conn = sqlite3.connect(DB_PATH, check_same_thread=False)

# -------------------------
# Load available stocks (UI uses company names)
# -------------------------
stocks_df = pd.read_sql_query(
    "SELECT DISTINCT company FROM nifty_universe ORDER BY company",
    conn
)

if stocks_df.empty:
    st.error("No stocks found. Run the data pipeline first.")
    st.stop()

selected_stock = st.selectbox(
    "🔍 Search Stock",
    stocks_df["company"].tolist()
)

# -------------------------
# Resolve symbol (CRITICAL FIX)
# -------------------------
symbol_df = pd.read_sql_query(
    """
    SELECT symbol
    FROM nifty_universe
    WHERE company = ?
    """,
    conn,
    params=(selected_stock,)
)

if symbol_df.empty:
    st.error("Symbol not found for selected stock.")
    st.stop()

selected_symbol = symbol_df.iloc[0]["symbol"]

# -------------------------
# Signal Overview Cards
# -------------------------
signal_df = pd.read_sql_query(
    """
    SELECT
        ss.news_momentum,
        AVG(ns.confidence) as avg_confidence,
        COUNT(ns.id) as news_count
    FROM stock_signals ss
    JOIN news n ON n.company = ss.company
    JOIN news_signals ns ON ns.news_id = n.id
    WHERE ss.company = ?
    """,
    conn,
    params=(selected_stock,)
)

st.markdown("---")

if not signal_df.empty:
    news_momentum = signal_df["news_momentum"].iloc[0] or 0.0
    avg_conf = signal_df["avg_confidence"].iloc[0] or 0.0
    news_count = signal_df["news_count"].iloc[0] or 0

    col1, col2, col3 = st.columns(3)
    col1.metric("📰 News Momentum", round(float(news_momentum), 4))
    col2.metric("🎯 Avg Confidence", round(float(avg_conf), 2))
    col3.metric("📌 News Articles", int(news_count))
else:
    st.warning("No signals available for this stock yet.")

# -------------------------
# Tabs
# -------------------------
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "📰 News Signals",
    "📈 Market Data",
    "💼 Earnings",
    "📊 Options",
    "🧠 AI Reasoning",
    "🔮 Scenarios",
    "🧠 Explanation",
    "📄 Raw News"
])

# -------------------------
# Tab 1: News Signals
# -------------------------
with tab1:
    news_ts = pd.read_sql_query(
        """
        SELECT
            n.published_at as date,
            (ns.sentiment * ns.confidence) as weighted_sentiment
        FROM news_signals ns
        JOIN news n ON n.id = ns.news_id
        WHERE n.company = ?
        """,
        conn,
        params=(selected_stock,)
    )

    if not news_ts.empty:
        news_ts["date"] = pd.to_datetime(news_ts["date"], errors="coerce")
        news_ts = news_ts.dropna()

        st.subheader("News Sentiment Trend")
        st.line_chart(
            news_ts.set_index("date")["weighted_sentiment"]
        )
    else:
        st.info("No news sentiment data available.")

# -------------------------
# Tab 2: Market Data (PRICE FIXED)
# -------------------------
with tab2:
    st.subheader("Price & Volume")

    price_df = pd.read_sql_query(
        """
        SELECT
            DATE(p.date) as date,
            p.open,
            p.high,
            p.low,
            p.close,
            p.volume
        FROM price_data p
        JOIN nifty_universe u
            ON UPPER(TRIM(p.company)) = UPPER(TRIM(u.symbol))
        AND u.company = ?
        ORDER BY p.date
        """,
        conn,
        params=(selected_stock,)
    )


    st.write("Rows fetched:", len(price_df))

    if price_df.empty:
        st.warning("No price data available for this stock.")
    else:
        price_df["date"] = pd.to_datetime(price_df["date"])
        price_df["close"] = price_df["close"].astype(float)
        price_df["volume"] = price_df["volume"].astype(int)

        # Price chart
        price_chart = (
            alt.Chart(price_df)
            .mark_line(color="steelblue")
            .encode(
                x="date:T",
                y="close:Q",
                tooltip=["date:T", "close:Q"]
            )
            .properties(
                title=f"{selected_stock} – Closing Price",
                height=300
            )
        )

        st.altair_chart(price_chart, use_container_width=True)

        # Volume chart
        volume_chart = (
            alt.Chart(price_df)
            .mark_bar(color="orange")
            .encode(
                x="date:T",
                y="volume:Q",
                tooltip=["date:T", "volume:Q"]
            )
            .properties(
                title=f"{selected_stock} – Trading Volume",
                height=200
            )
        )

        st.altair_chart(volume_chart, use_container_width=True)

# -------------------------
# Tab 3: Earnings
# -------------------------
with tab3:
    earnings_df = pd.read_sql_query(
        """
        SELECT quarter, confidence_score, risk_score, outlook
        FROM earnings_signals
        WHERE company = ?
        """,
        conn,
        params=(selected_stock,)
    )

    st.subheader("Earnings Call Analysis")

    if earnings_df.empty:
        st.info("No earnings data available yet.")
    else:
        st.dataframe(earnings_df, use_container_width=True)

        st.subheader("Confidence vs Risk")
        st.bar_chart(
            earnings_df.set_index("quarter")[["confidence_score", "risk_score"]]
        )

# -------------------------
# Tab 4: Options
# -------------------------
with tab4:
    opt_df = pd.read_sql_query(
        """
        SELECT implied_vol, market_bias
        FROM options_signals
        WHERE company = ?
        """,
        conn,
        params=(selected_stock,)
    )

    st.subheader("Market Expectations")

    if opt_df.empty:
        st.info("No options signal available.")
    else:
        st.metric("Implied Volatility", opt_df["implied_vol"].iloc[0])
        st.success(f"Market Bias: {opt_df['market_bias'].iloc[0]}")

# -------------------------
# Tab 5: Reasoning
# -------------------------
with tab5:
    reasoning_df = pd.read_sql_query(
        """
        SELECT dominant_driver, regime, signal_alignment,
               confidence, primary_risk
        FROM reasoning_state
        WHERE company = ?
        """,
        conn,
        params=(selected_stock,)
    )

    st.subheader("AI Reasoning State")

    if reasoning_df.empty:
        st.warning("No reasoning state available.")
    else:
        row = reasoning_df.iloc[0]

        col1, col2, col3 = st.columns(3)
        col1.metric("Dominant Driver", row["dominant_driver"])
        col2.metric("Regime", row["regime"])
        col3.metric("Confidence", row["confidence"])

        st.info(f"Signal Alignment: {row['signal_alignment']}")
        st.warning(f"Primary Risk: {row['primary_risk']}")

# -------------------------
# Tab 6: Scenarios
# -------------------------
with tab6:
    sc_df = pd.read_sql_query(
        """
        SELECT p_upside, p_downside, expected_vol, skew, horizon_days
        FROM scenario_forecasts
        WHERE company = ?
        """,
        conn,
        params=(selected_stock,)
    )

    st.subheader("Probabilistic Market Scenarios (30d)")

    if sc_df.empty:
        st.warning("No scenario forecast available.")
    else:
        row = sc_df.iloc[0]

        col1, col2, col3 = st.columns(3)
        col1.metric("Upside Probability", row["p_upside"])
        col2.metric("Downside Probability", row["p_downside"])
        col3.metric("Expected Volatility", row["expected_vol"])

        st.info(f"Risk Skew: {row['skew']}")

# -------------------------
# Tab 7: Explanation
# -------------------------
with tab7:
    expl_df = pd.read_sql_query(
        """
        SELECT explanation
        FROM stock_explanations
        WHERE company = ?
        """,
        conn,
        params=(selected_stock,)
    )

    st.subheader("Why this stock is ranked this way")

    if not expl_df.empty:
        st.success(expl_df["explanation"].iloc[0])
    else:
        st.warning("Explanation not available yet.")

    if USE_LLM:
        st.info("AI-generated summary (optional)")
        st.code(f"""
Stock: {selected_stock}
News momentum: {news_momentum}
Earnings outlook: see earnings tab
Market expectations: see options tab
Summarize the overall outlook in 3 lines.
        """)

# -------------------------
# Tab 8: Raw News
# -------------------------
with tab8:
    raw_news_df = pd.read_sql_query(
        """
        SELECT headline, published_at
        FROM news
        WHERE company = ?
        ORDER BY published_at DESC
        LIMIT 10
        """,
        conn,
        params=(selected_stock,)
    )

    st.subheader("Recent News Articles")

    if not raw_news_df.empty:
        st.table(raw_news_df)
    else:
        st.info("No recent news available.")

# -------------------------
# Footer
# -------------------------
st.markdown("---")
st.caption(
    "Built using automated alternative data ingestion, fast local inference, "
    "explainable signals, and a search-driven research dashboard."
)
