from pathlib import Path
from scanner.scanner import run_scan


BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_PATH = BASE_DIR / "data" / "outputs" / "short_scan.csv"


def main():

    # limit=3 keeps your testing behavior
    df_results = run_scan(limit=3)

    print("\nScan complete. Sample output:")
    print(df_results.head())

    OUTPUT_PATH.parent.mkdir(exist_ok=True)

    df_results.to_csv(OUTPUT_PATH, index=False)

    print(f"\nResults saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()