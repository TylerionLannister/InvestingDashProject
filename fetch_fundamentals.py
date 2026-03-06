#import os
import requests
import sqlite3
#import dotenv
import pandas as pd

import yfinance as yf

# --- Fetch functions ---
def fetch_income_statement(ticker):
    try:
        stock = yf.Ticker(ticker)
        income = stock.financials

        if income.empty:
            print(f"No income statement data for {ticker}")
            latest = None
        else:
            latest = income.iloc[:, 0]

        # Get EPS from info if needed
        info = stock.info
        eps = None
        if latest is not None:
            eps = latest.get("Earnings Per Share") or latest.get("EPS") or info.get("trailingEps")
        else:
            eps = info.get("trailingEps")

        return {
            "symbol": ticker,
            "date": income.columns[0].strftime("%Y-%m-%d") if latest is not None else None,
            "revenue": latest.get("Total Revenue") if latest is not None else None,
            "operating_income": latest.get("Operating Income") if latest is not None else None,
            "eps": eps,
            "ebitda": latest.get("EBITDA") if latest is not None else None
        }

    except Exception as e:
        print(f"Error fetching income statement {ticker}: {e}")
        return None


def fetch_balance_sheet(ticker):
    try:
        stock = yf.Ticker(ticker)
        balance = stock.balance_sheet

        if balance.empty:
            print(f"No balance sheet data for {ticker}")
            latest = None
        else:
            latest = balance.iloc[:, 0]

        info = stock.info
        total_equity = None
        cash = None
        if latest is not None:
            total_equity = latest.get("Total Stockholders Equity") or latest.get("Total Equity") or info.get("totalStockholderEquity")
            cash = latest.get("Cash and Cash Equivalents") or info.get("cash")
        else:
            total_equity = info.get("totalStockholderEquity")
            cash = info.get("cash")

        total_debt = latest.get("Total Debt") if latest is not None else info.get("totalDebt")

        return {
            "symbol": ticker,
            "date": balance.columns[0].strftime("%Y-%m-%d") if latest is not None else None,
            "total_debt": total_debt,
            "total_equity": total_equity,
            "cash": cash
        }

    except Exception as e:
        print(f"Error fetching balance sheet {ticker}: {e}")
        return None


def fetch_cash_flow(ticker):
    try:
        stock = yf.Ticker(ticker)
        cash = stock.cash_flow

        if cash.empty:
            print(f"No cash flow data for {ticker}")
            latest = None
        else:
            latest = cash.iloc[:, 0]

        free_cash_flow = None
        if latest is not None:
            free_cash_flow = latest.get("Free Cash Flow") or stock.info.get("freeCashflow")
        else:
            free_cash_flow = stock.info.get("freeCashflow")

        return {
            "symbol": ticker,
            "date": cash.columns[0].strftime("%Y-%m-%d") if latest is not None else None,
            "free_cash_flow": free_cash_flow
        }

    except Exception as e:
        print(f"Error fetching cash flow {ticker}: {e}")
        return None


# --- SQLite storage ---
def save_to_db(record, table, db_path="fundamentals.db"):
    conn = sqlite3.connect(db_path)
    df = pd.DataFrame([record])
    df.to_sql(table, conn, if_exists="append", index=False)
    conn.close()


def main():
    ticker = "AAPL"

    income = fetch_income_statement(ticker)
    balance = fetch_balance_sheet(ticker)
    cash = fetch_cash_flow(ticker)

    if income:
        save_to_db(income, "income_statement")
    if balance:
        save_to_db(balance, "balance_sheet")
    if cash:
        save_to_db(cash, "cash_flow")

    print("Data saved for:", ticker)


if __name__ == "__main__":
    main()
