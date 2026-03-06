import sqlite3
import pandas as pd
import numpy as np

DB_PATH = "fundamentals.db"

WEIGHTS = {
    "P/E": 0.4,
    "Operating Margin": 0.3,
    "Debt/Equity": 0.15,
    "Free Cash Flow / Price": 0.15
}


def score_stocks(db_path=DB_PATH, weights=WEIGHTS):

    conn = sqlite3.connect(db_path)
    df = pd.read_sql("SELECT * FROM ratios", conn)
    df = df.sort_values("date").drop_duplicates(subset="symbol", keep="last")
    conn.close()

    scored_rows = []
    missing_rows = []

    required_metrics = list(weights.keys())

    # --------------------------
    # Track missing metrics
    # --------------------------
    for _, row in df.iterrows():
        missing = [m for m in required_metrics if pd.isna(row[m])]
        if missing:
            missing_rows.append({
                "symbol": row["symbol"],
                "sector": row["sector"],
                "issue": "Missing " + ", ".join(missing)
            })
        scored_rows.append(row)  # Include all rows for scoring

    scored_df = pd.DataFrame(scored_rows)

    # --------------------------
    # Calculate scores using available metrics only
    # --------------------------
    if not scored_df.empty:

        score = pd.Series(0.0, index=scored_df.index)

        for idx, row in scored_df.iterrows():

            row_score = 0.0
            row_weight_total = 0.0

            for metric, weight in weights.items():

                if pd.notna(row[metric]):
                    # normalize within sector
                    sector_vals = scored_df[scored_df["sector"] == row["sector"]][metric]
                    if metric in ["P/E", "Debt/Equity"]:
                        norm_val = 1 - (row[metric] - sector_vals.min()) / (sector_vals.max() - sector_vals.min() + 1e-6)
                    else:
                        norm_val = (row[metric] - sector_vals.min()) / (sector_vals.max() - sector_vals.min() + 1e-6)
                    row_score += norm_val * weight
                    row_weight_total += weight

            # scale score by available weight fraction
            if row_weight_total > 0:
                score[idx] = row_score / row_weight_total
            else:
                score[idx] = np.nan

        scored_df["score"] = score
        scored_df.sort_values("score", ascending=False, inplace=True)

    # --------------------------
    # Convert missing rows
    # --------------------------
    missing_df = pd.DataFrame(missing_rows)

    # --------------------------
    # Store in database
    # --------------------------
    conn = sqlite3.connect(db_path)
    if not scored_df.empty:
        scored_df[["symbol", "sector", "score", "date"]].to_sql(
            "scores", conn, if_exists="replace", index=False
        )
    if not missing_df.empty:
        missing_df.to_sql(
            "missing_data", conn, if_exists="replace", index=False
        )
    conn.close()

    return scored_df, missing_df


if __name__ == "__main__":
    scored, missing = score_stocks()
    print("Scored:")
    print(scored[["symbol", "sector", "score"]])
    print("\nMissing:")
    print(missing)
