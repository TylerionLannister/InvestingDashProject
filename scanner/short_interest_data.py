# short_interest_data.py

from massive import RESTClient
import os
from dotenv import load_dotenv

# Load .env and get API key
load_dotenv()
MASSIVE_API_KEY = os.getenv("MASSIVE_API_KEY")

# Create client
client = RESTClient(MASSIVE_API_KEY)

def fetch_short_interest(ticker: str):
    """
    Fetch the most recent short interest for a given ticker.
    Returns a dictionary with the latest short interest info.
    """
    try:
        # list_short_interest returns an iterator
        data_iter = client.list_short_interest(
            ticker=ticker,
            limit=1,
            sort="settlement_date.desc"
        )
        # Get the first (latest) record if exists
        short_interest = next(data_iter, None)
        return short_interest
    except Exception as e:
        print(f"Error fetching short interest for {ticker}: {e}")
        #return None
        raise e #return error with string instead of returning none

# ------------------------
# Test
# ------------------------
if __name__ == "__main__":
    ticker = "GME"
    info = fetch_short_interest(ticker)
    print(info)