import pandas as pd
from pathlib import Path

NASDAQ_URL = "https://www.nasdaqtrader.com/dynamic/symdir/nasdaqlisted.txt"
OTHER_URL = "https://www.nasdaqtrader.com/dynamic/symdir/otherlisted.txt"

DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"
OUTPUT_FILE = DATA_DIR / "us_stocks.csv"

def load_nasdaq():

    df = pd.read_csv(NASDAQ_URL, sep="|")

    df = df[df["Symbol"] != "File Creation Time"]
    df = df[df["Test Issue"] == "N"]
    df = df[df["ETF"] == "N"]

    return df["Symbol"].dropna().astype(str).tolist()


def load_other():

    df = pd.read_csv(OTHER_URL, sep="|")

    df = df[df["ACT Symbol"] != "File Creation Time"]
    df = df[df["Test Issue"] == "N"]
    df = df[df["ETF"] == "N"]

    return df["ACT Symbol"].dropna().astype(str).tolist()


def build_universe():

    nasdaq = load_nasdaq()
    other = load_other()

    #tickers = sorted(set(nasdaq + other))
    tickers = sorted(set(nasdaq + other), key=str)

    print("Total tickers:", len(tickers))

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    pd.Series(tickers, name="ticker").to_csv(OUTPUT_FILE, index=False)

    print("Saved:", OUTPUT_FILE)


if __name__ == "__main__":
    build_universe()