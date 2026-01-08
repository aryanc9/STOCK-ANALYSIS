📊 Stock Intelligence Platform

Alternative Data–Driven Market Analysis & Signal Engine

Overview

This project is a research-grade stock intelligence platform designed to aggregate alternative datasets, generate structured signals, and support decision-making for equity analysis.

The system focuses on the Indian equity market (NIFTY universe) and combines:

alternative data

automated signal extraction

probabilistic reasoning

optional AI-generated explanations

The long-term goal is to support alpha generation, not price prediction alone.

Key Capabilities
1. Alternative Data Ingestion

The platform automatically collects and processes non-traditional datasets, including:

📰 Real-time financial news (RSS-based)

🧠 News sentiment & confidence scoring

💬 Earnings call transcript signals

📊 Options-derived market expectations

📈 Historical price & volume data (Yahoo Chart API)

🌱 ESG / qualitative sentiment (extensible)

All ingestion is fully automated through agent-based scripts.

2. Signal Generation Pipeline

Each data source produces structured signals, not raw text:

News Signals

sentiment score

confidence

short/medium horizon impact

Earnings Signals

confidence score

risk score

qualitative outlook

Options Signals

implied volatility

directional bias

Market Data Signals

price trends

volume behavior

technical extensions (RSI, EMA planned)

Signals are normalized so they can be combined and compared across sources.

3. AI Reasoning Layer (Agentic Design)

The platform uses an agent-style architecture:

Each agent has a single responsibility
(news analysis, price ingestion, earnings parsing, reasoning, etc.)

A reasoning agent synthesizes:

dominant drivers

market regime

signal alignment

confidence & primary risks

This design allows the system to scale toward:

autonomous updates

self-healing pipelines

multi-step reasoning

4. Interactive Research Dashboard

Built using Streamlit, the dashboard provides:

🔍 Stock search (company-based)

📈 Price & volume charts

📰 News sentiment trends

💼 Earnings analysis

📊 Options expectations

🧠 AI reasoning state

🔮 Probabilistic scenarios

📄 Raw news inspection

The dashboard is read-only by design, suitable for analysts.

Architecture Overview
┌─────────────┐
│  Universe   │  (company ↔ symbol mapping)
└──────┬──────┘
       │
┌──────▼──────┐
│ Ingestion   │  (news, prices, earnings, options)
│  Agents     │
└──────┬──────┘
       │
┌──────▼──────┐
│ Signal      │  (normalized, confidence-weighted)
│ Builders    │
└──────┬──────┘
       │
┌──────▼──────┐
│ Reasoning   │  (regime, drivers, risk)
│ Agent       │
└──────┬──────┘
       │
┌──────▼──────┐
│ Dashboard   │  (analysis & visualization)
└─────────────┘

Project Structure
ATHENA Workspace/
│
├── agents/
│   ├── universe_init.py
│   ├── news_fetcher.py
│   ├── news_ai_processor.py
│   ├── price_data_agent.py
│   ├── earnings_agent.py
│   ├── options_agent.py
│   ├── signal_builder.py
│   ├── reasoning_agent.py
│
├── db/
│   └── database.py
│
├── data/
│   └── altdata.db
│
├── dashboard.py
├── README.md
└── requirements.txt

Setup Instructions
1. Create virtual environment
python3 -m venv venv
source venv/bin/activate

2. Install dependencies
pip install -r requirements.txt

3. Initialize the universe
python -m agents.universe_init

4. Run data pipelines
python -m agents.news_fetcher
python -m agents.news_ai_processor
python -m agents.price_data_agent
python -m agents.signal_builder
python -m agents.reasoning_agent

5. Launch dashboard
streamlit run dashboard.py

Design Philosophy

Signals over predictions
The system focuses on interpretable signals, not black-box price forecasts.

Alternative data first
Traditional fundamentals are secondary to behavioral and informational signals.

Agentic, not monolithic
Each component can evolve independently.

Cheap, modular, extensible
Designed to run locally with free or low-cost data sources.

Current Limitations

Not intended for live trading

Yahoo price data is used as a fallback

Earnings transcript coverage is limited

No portfolio-level optimization yet

These are design tradeoffs, not flaws.

Planned Extensions

Technical indicator agent (RSI, EMA, volatility)

Cross-stock relative strength analysis

Alpha scoring engine

Portfolio construction layer

Fully autonomous orchestration agent

LLM-powered research assistant mode

Intended Audience

Hackathon judges

Quant-curious developers

Market research analysts

Students exploring alternative data & AI systems

Disclaimer

This project is for educational and research purposes only.
It is not financial advice and should not be used for live trading decisions.