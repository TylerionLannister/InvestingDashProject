
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
    Returns a dictionary with the latest float info.
    """
    try:
        # list_stocks_floats returns an iterator
        data_iter = client.list_stocks_floats(
	    ticker="GME",
	    limit=1,
	    sort="effective_date.desc",
	    )
        # Get the first (latest) record if exists
        float = next(data_iter, None)
        return float
    except Exception as e:
        print(f"Error fetching float for {ticker}: {e}")
        return None

# ------------------------
# Test
# ------------------------
if __name__ == "__main__":
    ticker = "GME"
    info = fetch_float(ticker)
    print(info)