import pandas as pd
from scoring.short_scoring import (
    compute_short_score_relative,
    compute_short_score_absolute,
    get_top_n
)
from scanner.scanner import run_scan


def test_short_scoring():
    # Load the scanner output
    df = pd.read_csv("data/outputs/short_scan.csv")

    # Compute scores
    df = compute_short_score_relative(df)
    df = compute_short_score_absolute(df)

    # Save full scored universe
    df.to_csv("data/outputs/short_scored.csv", index=False)

    # Optional: save top 50 for Agent
    df_top50 = get_top_n(df, n=50)
    df_top50.to_csv("data/outputs/short_top50.csv", index=False)

    print("Scoring complete!")
    print("Top 10 relative scores:")
    print(df_top50[['ticker', 'short_score', 'short_score_absolute']].head(10))



# Example usage:
# test_single_stock("AAPL")
def test_single_stock(ticker: str):
    """
    Scan a single ticker, apply relative and absolute short scoring,
    and print the results.
    """
    # Run scanner for just this ticker
    df = run_scan(tickers=[ticker], limit=1)

    # Fill NaN with 0 or a safe default for scoring
    df.fillna(0, inplace=True)

    # Compute scores
    df = compute_short_score_relative(df)
    df = compute_short_score_absolute(df)

    # Print results
    print("\nScoring results for:", ticker)
    print(df[['ticker', 'short_score', 'short_score_absolute']].iloc[0])

    return df.iloc[0]  # return Series for easy inspection



if __name__ == "__main__":
    #test_short_scoring()
    test_single_stock("IBRX")