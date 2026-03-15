from pathlib import Path
import pandas as pd
import time

from features.registry import FEATURES

from utils.api_utils import safe_api_call
from features.short_interest_data import fetch_short_interest
from features.short_volume_data import fetch_short_volume
from features.float_data import fetch_float


BASE_DIR = Path(__file__).resolve().parent.parent
UNIVERSE_PATH = BASE_DIR / "data" / "processed" / "smallcap_universe.csv"


def load_universe():
    df = pd.read_csv(UNIVERSE_PATH)

    if "Symbol" not in df.columns:
        raise ValueError("Symbol column not found in universe file")

    return df["Symbol"].tolist()


def run_scan(limit=None, tickers: list = None):
    if tickers is None:
        tickers = load_universe()
        total = len(tickers)
        if limit:
            tickers = tickers[:limit]
    else:
        total = len(tickers)
        if limit:
            tickers = tickers[:limit]

    print(f"Scanning {len(tickers)} of {total} tickers")

    results = []

    for idx, ticker in enumerate(tickers, start=1):
        print(f"\nScanning {idx}/{len(tickers)} — {ticker}")

        row = {
            "timestamp": pd.Timestamp.utcnow(),
            "ticker": ticker
        }

        for feature_name, feature_func in FEATURES.items():
            value = safe_api_call(feature_func, ticker)

            # Flatten dict features
            if isinstance(value, dict):
                for k, v in value.items():
                    row[f"{feature_name}_{k}"] = v
            else:
                row[feature_name] = value

        results.append(row)

        time.sleep(0.5)

    df_results = pd.DataFrame(results)
    return df_results