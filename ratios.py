from fetch_fundamentals import fetch_income_statement, fetch_balance_sheet, fetch_cash_flow

import sqlite3
import pandas as pd

DB_PATH = "fundamentals.db"

def calculate_ratios(ticker, price, db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    
    # Load latest records
    income_df = pd.read_sql(
        "SELECT * FROM income_statement WHERE symbol=? ORDER BY date DESC LIMIT 1",
        (ticker,),
        conn
    )
    balance_df = pd.read_sql(
        "SELECT * FROM balance_sheet WHERE symbol=? ORDER BY date DESC LIMIT 1",
        (ticker,),
        conn
    )
    cash_df = pd.read_sql(
        "SELECT * FROM cash_flow WHERE symbol=? ORDER BY date DESC LIMIT 1",
        (ticker,),
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

    ratios = {}
    ratios["symbol"] = ticker
    ratios["P/E"] = price / eps if pd.notna(eps) and eps != 0 else None
    ratios["Operating Margin"] = operating_income / revenue if pd.notna(operating_income) and pd.notna(revenue) and revenue != 0 else None
    ratios["Debt/Equity"] = total_debt / total_equity if pd.notna(total_debt) and pd.notna(total_equity) and total_equity != 0 else None
    ratios["Free Cash Flow / Price"] = free_cash_flow / price if pd.notna(free_cash_flow) and price != 0 else None

    return ratios

if __name__ == "__main__":
    ticker = "AAPL"
    ratios = calculate_ratios(ticker)
    print(ratios)