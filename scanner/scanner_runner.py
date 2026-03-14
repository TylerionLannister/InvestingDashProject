from pathlib import Path
import time
import pandas as pd

from short_interest_data import fetch_short_interest
from short_volume_data import fetch_short_volume
from float_data import fetch_float



# ---------- Paths ----------
BASE_DIR = Path(__file__).resolve().parent.parent
UNIVERSE_PATH = BASE_DIR / "data" / "processed" / "smallcap_universe.csv"

# ---------- Safe API Wrapper ----------
def safe_api_call(func, *args, retries=5, wait_on_429=30, **kwargs):
    """
    Safely call an API function with retry on 429 rate-limit.

    func: the API function to call
    args, kwargs: arguments to pass to func
    retries: max retry attempts
    wait_on_429: seconds to wait on rate limit
    """
    attempts = 0

    while attempts < retries:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if "429" in str(e):
                attempts += 1
                print(f"Rate limit hit on {func.__name__}. Waiting {wait_on_429}s... (attempt {attempts}/{retries})")
                time.sleep(wait_on_429)
            else:
                print(f"Error in {func.__name__} for args {args}, kwargs {kwargs}: {e}")
                return None

    print(f"Max retries reached for {func.__name__} with args {args}")
    return None

# ---------- Load Universe ----------
def load_universe():
    df = pd.read_csv(UNIVERSE_PATH)

    if "Symbol" not in df.columns:
        raise ValueError("Symbol column not found in universe file")

    return df["Symbol"].tolist()

# ---------- Scanner Loop ----------
def main():
    tickers = load_universe()
    total = len(tickers)
    print(f"Loaded {total} tickers")

    results = []

    #ONLY DOING THE FIRST TEN FOR TESTING
    for idx, ticker in enumerate(tickers[:10], start=1):
        print(f"\nScanning {idx}/{total} — {ticker}")

        # Short Interest
        short_interest = safe_api_call(fetch_short_interest, ticker)
        short_volume = safe_api_call(fetch_short_volume, ticker)
        float_value = safe_api_call(fetch_float, ticker)

        # Build row (expand later with other features)
        row = {
            "ticker": ticker,
            "short_interest": short_interest,
            "short_volume": short_volume,
            "float": float_value
        }

        results.append(row)

    # Convert results to DataFrame
    df_results = pd.DataFrame(results)
    print("\nScan complete. Sample output:")
    print(df_results.head())

    # Optionally: save results
    output_path = BASE_DIR / "data" / "outputs" / "short_scan.csv"
    output_path.parent.mkdir(exist_ok=True)  # create folder if missing
    df_results.to_csv(output_path, index=False)
    print(f"Results saved to {output_path}")

if __name__ == "__main__":
    main()
