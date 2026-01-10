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

st.title("📊 Stock Intelligence Platform")
st.caption(
    "Event-driven alternative data intelligence for Indian equities. "
    "Signals are generated automatically using agentic AI."
)

USE_LLM = st.checkbox("Enable AI Explanation (optional)", value=False)

# -------------------------
# Database connection
# -------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "altdata.db")
conn = sqlite3.connect(DB_PATH, check_same_thread=False)

# =========================================================
# LOAD RANKED STOCK UNIVERSE (FROM AGGREGATION AGENT)
# =========================================================
stocks_df = pd.read_sql_query(
    """
    SELECT
        u.company,
        s.symbol,
        s.signal_strength
    FROM stock_signals s
    JOIN nifty_universe u ON u.symbol = s.symbol
    ORDER BY s.signal_strength DESC
    """,
    conn
)

if stocks_df.empty:
    st.error("No aggregated signals available yet. Make sure aggregation agent is running.")
    st.stop()

# -------------------------
# Stock selector
# -------------------------
selected_stock = st.selectbox(
    "🔍 Search Stock",
    stocks_df["company"].tolist()
)

selected_symbol = stocks_df.loc[
    stocks_df["company"] == selected_stock, "symbol"
].iloc[0]

# =========================================================
# TOP ALPHA LEADERBOARD
# =========================================================
st.subheader("🔥 Top Alpha Signals")

st.dataframe(
    stocks_df.head(10),
    use_container_width=True,
    hide_index=True
)

# =========================================================
# STOCK-LEVEL METRICS (FROM stock_signals)
# =========================================================
signal_df = pd.read_sql_query(
    """
    SELECT
        news_momentum,
        avg_confidence,
        signal_strength,
        last_updated
    FROM stock_signals
    WHERE symbol = ?
    """,
    conn,
    params=(selected_symbol,)
)

st.markdown("---")

if not signal_df.empty:
    row = signal_df.iloc[0]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("📰 News Momentum", round(row["news_momentum"], 3))
    col2.metric("🎯 Avg Confidence", round(row["avg_confidence"], 3))
    col3.metric("⚡ Signal Strength", round(row["signal_strength"], 3))
    col4.caption(f"Updated: {row['last_updated']}")
else:
    st.warning("No aggregated signal available for this stock.")

# =========================================================
# TABS
# =========================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📰 News Signals",
    "📈 Market Data",
    "🧠 Reasoning",
    "🧠 Explanation",
    "📄 Raw News"
])

# =========================================================
# TAB 1: NEWS SENTIMENT TIME SERIES (Kafka-derived)
# =========================================================
with tab1:
    news_ts = pd.read_sql_query(
        """
        SELECT
            event_time AS date,
            sentiment_score * confidence AS weighted_sentiment
        FROM news_signals
        WHERE symbol = ?
        ORDER BY event_time
        """,
        conn,
        params=(selected_symbol,)
    )

    if news_ts.empty:
        st.info("No news sentiment data available yet.")
    else:
        news_ts["date"] = pd.to_datetime(news_ts["date"])

        st.subheader("News Sentiment Momentum")

        chart = (
            alt.Chart(news_ts)
            .mark_line(color="steelblue")
            .encode(
                x="date:T",
                y="weighted_sentiment:Q",
                tooltip=["date:T", "weighted_sentiment:Q"]
            )
            .properties(height=300)
        )

        st.altair_chart(chart, use_container_width=True)

# =========================================================
# TAB 2: MARKET DATA (PRICE)
# =========================================================
with tab2:
    price_df = pd.read_sql_query(
        """
        SELECT
            date,
            open,
            high,
            low,
            close,
            volume
        FROM price_data
        WHERE symbol = ?
        ORDER BY date
        """,
        conn,
        params=(selected_symbol,)
    )

    if price_df.empty:
        st.warning("No price data available.")
    else:
        price_df["date"] = pd.to_datetime(price_df["date"])

        st.subheader("Closing Price")
        st.line_chart(price_df.set_index("date")["close"])

        st.subheader("Trading Volume")
        st.bar_chart(price_df.set_index("date")["volume"])

# =========================================================
# TAB 3: REASONING (placeholder for next agent)
# =========================================================
with tab3:
    st.info(
        "Reasoning agent not yet wired.\n\n"
        "This tab will explain **why** the signal exists by fusing:\n"
        "- News\n"
        "- Price trends\n"
        "- Earnings\n"
        "- Options expectations"
    )

# =========================================================
# TAB 4: EXPLANATION
# =========================================================
with tab4:
    expl_df = pd.read_sql_query(
        """
        SELECT explanation
        FROM stock_explanations
        WHERE symbol = ?
        """,
        conn,
        params=(selected_symbol,)
    )

    st.subheader("Human-readable Explanation")

    if not expl_df.empty:
        st.success(expl_df.iloc[0]["explanation"])
    else:
        st.warning("No explanation generated yet.")

    if USE_LLM:
        st.code(f"""
Stock: {selected_stock}
Symbol: {selected_symbol}

News momentum: {row["news_momentum"]}
Signal strength: {row["signal_strength"]}

Explain the outlook in 3 concise lines.
        """)

# =========================================================
# TAB 5: RAW NEWS
# =========================================================
with tab5:
    raw_news_df = pd.read_sql_query(
        """
        SELECT
            headline,
            source,
            event_time
        FROM news_signals
        WHERE symbol = ?
        ORDER BY event_time DESC
        LIMIT 20
        """,
        conn,
        params=(selected_symbol,)
    )

    if raw_news_df.empty:
        st.info("No raw news available.")
    else:
        st.table(raw_news_df)

# =========================================================
# FOOTER
# =========================================================
st.markdown("---")
st.caption(
    "Built with Kafka-based event streaming, decoupled agentic AI, "
    "and explainable alpha signals."
)
