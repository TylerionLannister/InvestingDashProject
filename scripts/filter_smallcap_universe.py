import os
import pandas as pd
import yfinance as yf
from time import sleep

# Paths (relative to repo root)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_FILE = os.path.join(BASE_DIR, "data", "raw", "us_stocks.csv")
PROCESSED_FILE = os.path.join(BASE_DIR, "data", "processed", "smallcap_universe.csv")

# Small-cap limits
MIN_MARKET_CAP = 50_000_000    # $50M
MAX_MARKET_CAP = 2_000_000_000 # $2B

def filter_smallcap_universe():
    # Load full US stock list
    df = pd.read_csv(RAW_FILE)
    tickers = df['ticker'].dropna().astype(str).tolist()

    print(f"Total tickers to check: {len(tickers)}")

    smallcaps = []

    # Batch processing with retry logic
    for i in range(0, len(tickers), 50):
        batch = tickers[i:i+50]
        tickers_str = " ".join(batch)

        for attempt in range(3):
            try:
                tickers_info = yf.Tickers(tickers_str)
                break
            except Exception as e:
                print(f"Error fetching batch {i}-{i+50}, retrying... ({attempt+1}/3)")
                sleep(2)
        else:
            print(f"Skipping batch {i}-{i+50} after 3 failed attempts.")
            continue

        for symbol, tkr in tickers_info.tickers.items():
            try:
                mc = tkr.info.get("marketCap")
                if mc and MIN_MARKET_CAP <= mc <= MAX_MARKET_CAP:
                    smallcaps.append(symbol)
            except Exception:
                continue

        print(f"Processed {i+len(batch)} / {len(tickers)} tickers, smallcaps found: {len(smallcaps)}", end="\r")

    print(f"\nTotal small-cap tickers: {len(smallcaps)}")

    # Save to CSV
    os.makedirs(os.path.dirname(PROCESSED_FILE), exist_ok=True)
    pd.DataFrame({"Symbol": smallcaps}).to_csv(PROCESSED_FILE, index=False)
    print(f"Saved small-cap universe to {PROCESSED_FILE}")


if __name__ == "__main__":
    filter_smallcap_universe()