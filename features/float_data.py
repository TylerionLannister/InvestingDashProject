
# float_data.py

from massive import RESTClient
import os
from dotenv import load_dotenv

# Load .env and get API key
load_dotenv()
MASSIVE_API_KEY = os.getenv("MASSIVE_API_KEY")

# Create client
client = RESTClient(MASSIVE_API_KEY)

def fetch_float(ticker: str):
    """
    Fetch the most recent float for a given ticker.
    Returns a dictionary with numeric fields for the scanner.
    """
    try:
        # list_stocks_floats returns an iterator
        data_iter = client.list_stocks_floats(
            ticker=ticker,
            limit=1,
            sort="effective_date.desc",
        )

        # Get the first (latest) record if exists
        float_data = next(data_iter, None)

        if not float_data:
            return {
                "float": None,
                "free_float_percent": None,
                "effective_date": None
            }

        # Return the numeric fields we care about
        return {
            "float": float_data.free_float,
            "free_float_percent": float_data.free_float_percent,
            "effective_date": float_data.effective_date
        }

    except Exception as e:
        print(f"Error fetching float for {ticker}: {e}")
        # Let the scanner's safe_api_call handle it
        raise e

# ------------------------
# Test
# ------------------------
if __name__ == "__main__":
    ticker = "GME"
    info = fetch_float(ticker)
    print(info)