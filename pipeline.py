# pipeline.py
import sqlite3
import pandas as pd
import requests
import yfinance as yf
from fetch_fundamentals import (
    fetch_income_statement,
    fetch_balance_sheet,
    fetch_cash_flow,
    save_to_db
)
from data.market_data import get_live_price  # yfinance live price

DB_PATH = "fundamentals.db"





# --- Get sector (still using FMP if needed) --

def get_sector(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return info.get("sector")
    except Exception as e:
        print(f"Error fetching sector for {ticker}: {e}")
        return None

# --- Record last update ---
def update_last_run():
    conn = sqlite3.connect(DB_PATH)
    df = pd.DataFrame({
        "key": ["last_update"],
        "value": [pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")]
    })
    df.to_sql("metadata", conn, if_exists="replace", index=False)
    conn.close()

def calculate_ratios(ticker, price):
    conn = sqlite3.connect(DB_PATH)

    income_df = pd.read_sql(
        f"SELECT * FROM income_statement WHERE symbol='{ticker}' ORDER BY date DESC LIMIT 1",
        conn
    )

    balance_df = pd.read_sql(
        f"SELECT * FROM balance_sheet WHERE symbol='{ticker}' ORDER BY date DESC LIMIT 1",
        conn
    )

    cash_df = pd.read_sql(
        f"SELECT * FROM cash_flow WHERE symbol='{ticker}' ORDER BY date DESC LIMIT 1",
        conn
    )

    conn.close()

    if income_df.empty or balance_df.empty or cash_df.empty:
        print(f"Missing fundamentals for {ticker}, skipping ratio calculation.")
        return None

    income = income_df.iloc[0]
    balance = balance_df.iloc[0]
    cash = cash_df.iloc[0]

    # Convert to numeric safely
    eps = pd.to_numeric(income["eps"], errors="coerce")
    operating_income = pd.to_numeric(income["operating_income"], errors="coerce")
    revenue = pd.to_numeric(income["revenue"], errors="coerce")
    total_debt = pd.to_numeric(balance["total_debt"], errors="coerce")
    total_equity = pd.to_numeric(balance["total_equity"], errors="coerce")
    free_cash_flow = pd.to_numeric(cash["free_cash_flow"], errors="coerce")

    ratios = {
        "symbol": ticker,
        "sector": get_sector(ticker),
        "date": pd.Timestamp.now().strftime("%Y-%m-%d"),
        "P/E": price / eps if pd.notna(eps) and eps != 0 else None,
        "Operating Margin": operating_income / revenue if pd.notna(operating_income) and pd.notna(revenue) and revenue != 0 else None,
        "Debt/Equity": total_debt / total_equity if pd.notna(total_debt) and pd.notna(total_equity) and total_equity != 0 else None,
        "Free Cash Flow / Price": free_cash_flow / price if pd.notna(free_cash_flow) and price != 0 else None
    }

    return ratios

def main(tickers):
    for ticker in tickers:
        # --- Get live price ---
        try:
            price = get_live_price(ticker)
        except Exception as e:
            print(f"Error getting live price for {ticker}: {e}")
            continue

        # --- Fetch fundamentals ---
        income = fetch_income_statement(ticker)
        balance = fetch_balance_sheet(ticker)
        cash = fetch_cash_flow(ticker)

        if income:
            save_to_db(income, "income_statement")
        if balance:
            save_to_db(balance, "balance_sheet")
        if cash:
            save_to_db(cash, "cash_flow")

        # --- Calculate ratios ---
        try:
            ratios = calculate_ratios(ticker, price)
            if ratios is None:
                print(f"Skipping {ticker} due to missing data.")
                continue

            save_to_db(ratios, "ratios")
            print(f"Saved ratios for {ticker}: {ratios}")
        except Exception as e:
            print(f"Error calculating ratios for {ticker}: {e}")
            continue

    # --- Score all stocks after processing ---
    try:
        scored, missing = score_stocks()
        print("Scoring complete.")
    except Exception as e:
        print(f"Error scoring stocks: {e}")

    # --- Update last run ---
    update_last_run()

# --- Test run ---
if __name__ == "__main__":
    test_tickers = ["AAPL", "GOOGL", "TSLA"]
    main(test_tickers)
