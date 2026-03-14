# short_volume_data.py

from massive import RESTClient
import os
from dotenv import load_dotenv

# Load .env and get API key
load_dotenv()
MASSIVE_API_KEY = os.getenv("MASSIVE_API_KEY")

# Create client
client = RESTClient(MASSIVE_API_KEY)

def fetch_short_volume(ticker: str):
    """
    Fetch the most recent short volume for a given ticker.
    Returns a dictionary with the latest short volume info.
    """
    try:
        # list_short_volume returns an iterator
        data_iter = client.list_short_volume(
	    ticker=ticker,
	    limit=1,
	    sort="date.desc",
	    )
        # Get the first (latest) record if exists
        short_volume = next(data_iter, None)
        return short_volume
    except Exception as e:
        print(f"Error fetching short volume for {ticker}: {e}")
        #return None
        raise e

# ------------------------
# Test
# ------------------------
if __name__ == "__main__":
    ticker = "GME"
    info = fetch_short_volume(ticker)
    print(info)