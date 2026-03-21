import pandas as pd
from scoring.short_scoring import (
    compute_short_score_relative,
    compute_short_score_absolute,
    get_top_n
)

if __name__ == "__main__":
    # Load raw scanner output
    df = pd.read_csv("data/outputs/short_scan.csv")

    # Fill missing values
    df.fillna(0, inplace=True)

    # Compute scores
    df = compute_short_score_relative(df)
    df = compute_short_score_absolute(df)

    # Save full scored CSV
    df.to_csv("data/outputs/short_scored.csv", index=False)

    # Optional: top 50
    df_top50 = get_top_n(df, 50)
    df_top50.to_csv("data/outputs/short_top50.csv", index=False)

    print("Scoring complete! Check data/outputs/short_scored.csv and data/outputs/short_top50.csv")