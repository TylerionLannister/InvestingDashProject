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
    Returns a dictionary with numeric fields ready for the scanner.
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

        if not short_interest:
            return {
                "short_interest": None,
                "days_to_cover": None
            }

        # Only return the numeric fields we care about
        return {
            "short_interest": short_interest.short_interest,
            "days_to_cover": short_interest.days_to_cover
        }

    except Exception as e:
        print(f"Error fetching short interest for {ticker}: {e}")
        # Return None values instead of raising so scanner continues
        raise e
 


# ------------------------
# Test
# ------------------------
if __name__ == "__main__":
    ticker = "GME"
    info = fetch_short_interest(ticker)
    print(info)