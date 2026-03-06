import yfinance as yf

def get_live_price(ticker: str) -> float:
    """
    Get the live price of a stock
    """
    stock = yf.Ticker(ticker)
    data = stock.history(period="1d")

    if data.empty:
        raise ValueError(f"No data found for {ticker}")

    return data["Close"].iloc[-1]