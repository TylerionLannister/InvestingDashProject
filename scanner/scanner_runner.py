from scanner.short_interest import fetch_short_interest
from scanner.options_data import fetch_options_chain
from scanner.market_data import fetch_float_and_marketcap

def fetch_squeeze_signals(ticker):
    signals = {}
    signals.update(fetch_short_interest(ticker))
    signals.update(fetch_options_chain(ticker))
    signals.update(fetch_float_and_marketcap(ticker))
    return signals