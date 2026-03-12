import yfinance as yf
import pandas as pd


def get_current_price(ticker: str) -> float:
    stock = yf.Ticker(ticker)
    return stock.history(period="1d")["Close"].iloc[-1]


def get_options_chain(ticker: str, expiry: str = None) -> pd.DataFrame:
    stock = yf.Ticker(ticker)

    expirations = stock.options
    if not expirations:
        return pd.DataFrame()

    selected_expiry = expiry if expiry else expirations[0]

    chain = stock.option_chain(selected_expiry)

    calls = chain.calls.copy()
    calls["type"] = "call"

    puts = chain.puts.copy()
    puts["type"] = "put"

    df = pd.concat([calls, puts], ignore_index=True)

    df = df[["strike", "type", "openInterest", "volume"]]
    df.rename(columns={"openInterest": "open_interest"}, inplace=True)

    return df


def get_top_call_oi_strike(df: pd.DataFrame):
    calls = df[df["type"] == "call"]
    row = calls.loc[calls["open_interest"].idxmax()]
    return row["strike"], row["open_interest"]


def get_top_put_oi_strike(df: pd.DataFrame):
    puts = df[df["type"] == "put"]
    row = puts.loc[puts["open_interest"].idxmax()]
    return row["strike"], row["open_interest"]


def get_call_put_oi_ratio(df: pd.DataFrame) -> float:
    call_oi = df[df["type"] == "call"]["open_interest"].sum()
    put_oi = df[df["type"] == "put"]["open_interest"].sum()

    if put_oi == 0:
        return float("inf")

    return call_oi / put_oi


def get_gamma_ramp_strike(df: pd.DataFrame, price: float):
    calls = df[df["type"] == "call"]

    above_price = calls[calls["strike"] > price]

    if above_price.empty:
        return None, None

    max_oi = calls["open_interest"].max()
    threshold = max_oi * 0.10

    candidates = above_price[above_price["open_interest"] >= threshold]

    if candidates.empty:
        return None, None

    closest = candidates.sort_values("strike").iloc[0]

    return closest["strike"], closest["open_interest"]


def get_call_oi_within_percent(df: pd.DataFrame, price: float, pct: float = 0.10):
    calls = df[df["type"] == "call"]

    upper_bound = price * (1 + pct)

    ramp_calls = calls[
        (calls["strike"] > price) &
        (calls["strike"] <= upper_bound)
    ]

    return int(ramp_calls["open_interest"].sum())


def get_distance_to_gamma(price: float, gamma_strike):
    if gamma_strike is None:
        return None

    return ((gamma_strike - price) / price) * 100


def get_options_pressure(ticker: str):

    df = get_options_chain(ticker)
    if df.empty:
        return None

    price = get_current_price(ticker)

    call_strike, call_oi = get_top_call_oi_strike(df)
    put_strike, put_oi = get_top_put_oi_strike(df)

    ratio = get_call_put_oi_ratio(df)

    gamma_strike, gamma_oi = get_gamma_ramp_strike(df, price)

    ramp_oi = get_call_oi_within_percent(df, price)

    distance_pct = get_distance_to_gamma(price, gamma_strike)

    largest_pressure_strike = call_strike if call_oi > put_oi else put_strike

    return {
        "ticker": ticker,
        "current_price": price,
        "top_call_strike": call_strike,
        "top_call_oi": call_oi,
        "top_put_strike": put_strike,
        "top_put_oi": put_oi,
        "call_put_oi_ratio": ratio,
        "largest_pressure_strike": largest_pressure_strike,
        "gamma_ramp_strike": gamma_strike,
        "gamma_ramp_oi": gamma_oi,
        "call_oi_within_10pct": ramp_oi,
        "distance_to_gamma_strike_pct": distance_pct
    }


if __name__ == "__main__":
    ticker = "SLS"
    info = get_options_pressure(ticker)
    print(info)