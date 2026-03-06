import streamlit as st
import pandas as pd
import sqlite3
import yfinance as yf

from pipeline import main
from scoring import score_stocks
from database import load_last_update

DB_PATH = "fundamentals.db"

st.set_page_config(page_title="Stock Fundamentals Dashboard", layout="wide")

st.title("📊 Stock Fundamentals Dashboard")


# -------------------------
# Search + Refresh
# -------------------------

ticker_input = st.text_input(
    "Enter stock symbols (comma separated)",
    placeholder="AAPL, MSFT, TSLA"
)

if st.button("🔄 Refresh Data"):

    if not ticker_input.strip():
        st.warning("Please enter at least one stock symbol.")
        st.stop()

    tickers = [
        ticker.strip().upper()
        for ticker in ticker_input.split(",")
        if ticker.strip()
    ]

    with st.spinner("Updating data... please wait..."):
        main(tickers)
        score_stocks()

    st.success("Data updated successfully!")
    st.rerun()


# -------------------------
# Last update timestamp
# -------------------------

last_update = load_last_update()
st.write(f"Last update: {last_update}")


# -------------------------
# Load database tables
# -------------------------

conn = sqlite3.connect(DB_PATH)

try:
    scores = pd.read_sql("SELECT * FROM scores", conn)
except:
    scores = pd.DataFrame(columns=["symbol", "sector", "score", "date"])

try:
    missing = pd.read_sql("SELECT * FROM missing_data", conn)
except:
    missing = pd.DataFrame(columns=["symbol", "sector", "issue"])

conn.close()


# -------------------------
# Clean data types
# -------------------------

if "score" in scores.columns:
    scores["score"] = pd.to_numeric(scores["score"], errors="coerce")
    scores["score"] = scores["score"].round(3)

missing["score"] = None


# -------------------------
# Combine scored + missing
# -------------------------

combined = pd.concat([scores, missing], ignore_index=True)

# Remove duplicates (prefer rows that have scores)
combined = combined.sort_values("score", ascending=False)
combined = combined.drop_duplicates(subset="symbol", keep="first")


# -------------------------
# Sector selector
# -------------------------

all_sectors = combined["sector"].dropna().unique()

selected_sector = st.selectbox(
    "Select sector",
    sorted(all_sectors)
)

sector_df = combined[combined["sector"] == selected_sector].copy()


# -------------------------
# Sorting logic
# -------------------------

sector_df["score_sort"] = sector_df["score"].fillna(-1)

sector_df = sector_df.sort_values(
    "score_sort",
    ascending=False
).drop(columns="score_sort")


# -------------------------
# Rating labels
# -------------------------

def score_label(score):

    if pd.isna(score):
        return "Missing data"

    if score >= 0.75:
        return "🟢 Strong"

    elif score >= 0.50:
        return "🟡 Neutral"

    else:
        return "🔴 Weak"


sector_df["rating"] = sector_df["score"].apply(score_label)


# -------------------------
# Top Stock Banner
# -------------------------

scored_only = sector_df[sector_df["score"].notna()]

if not scored_only.empty:

    top_symbol = scored_only.iloc[0]["symbol"]
    top_score = scored_only.iloc[0]["score"]

    st.markdown(f"### 🥇 Top Stock in {selected_sector}")
    st.markdown(f"**{top_symbol}** (Score: {top_score:.2f})")


# -------------------------
# Score Explanation
# -------------------------
st.subheader(
    "🏆 Sector Stocks",
    help="""
Stock scores are calculated using four financial metrics:

• **P/E Ratio** – Indicates how expensive the stock is relative to earnings (lower can indicate better value).

• **Operating Margin** – Measures how efficiently a company generates profit from revenue (higher is stronger).

• **Debt-to-Equity** – Shows how much debt the company uses relative to shareholder equity (lower suggests less financial risk).

• **Free Cash Flow / Price** – Represents how much cash the company generates relative to its stock price.

Each stock is compared **against other companies in the same sector**, and the metrics are normalized and combined into a weighted score.

Higher scores generally indicate companies that are **more profitable, less leveraged, and better valued relative to their peers.**
"""
)

# -------------------------
# Stock Table
# -------------------------

st.dataframe(
    sector_df,
    use_container_width=True
)


# -------------------------
# Price Chart
# -------------------------

st.subheader("📈 Price Chart")

available_stocks = sector_df["symbol"].tolist()

selected_stock = st.selectbox(
    "Select stock to view price",
    available_stocks
)

stock = yf.Ticker(selected_stock)

hist = stock.history(period="6mo")

st.line_chart(hist["Close"])
