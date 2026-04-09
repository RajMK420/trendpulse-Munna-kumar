import pandas as pd
import numpy as np
from pathlib import Path

DATA_DIR = Path("data")
INPUT_CSV  = DATA_DIR / "trends_clean.csv"
OUTPUT_CSV = DATA_DIR / "trends_analysed.csv"


def load_data(path: Path) -> pd.DataFrame:
    """Load the cleaned CSV produced by Task 2."""
    if not path.exists():
        raise FileNotFoundError(f"{path} not found — run Task 2 first.")
    df = pd.read_csv(path)
    print(f"Loaded {df.shape[0]} rows, {df.shape[1]} columns from {path.name}.")
    return df


def explore(df: pd.DataFrame) -> None:
    """Print a quick data snapshot."""
    print("\nFirst 5 rows:")
    print(df.head().to_string(index=False))
    print(f"\nAverage score    : {df['score'].mean():.1f}")
    print(f"Average comments : {df['num_comments'].mean():.0f}")


def numpy_stats(df: pd.DataFrame) -> None:
    """Compute and print NumPy-based score statistics."""
    scores = df["score"].to_numpy()

    print("\nNumPy score stats:")
    print(f"  Mean      : {np.mean(scores):.1f}")
    print(f"  Median    : {np.median(scores):.0f}")
    print(f"  Std dev   : {np.std(scores):.1f}")
    print(f"  Min / Max : {np.min(scores)} / {np.max(scores)}")

    top_cat   = df["category"].value_counts()
    print(f"\nMost stories in : {top_cat.index[0]}  ({top_cat.iloc[0]} stories)")

    idx   = df["num_comments"].idxmax()
    title = df.loc[idx, "title"][:60]
    count = df.loc[idx, "num_comments"]
    print(f"Most commented  : '{title}...'  ({count} comments)")


def add_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Derive two new columns and return the enriched DataFrame.

    - engagement : num_comments / (score + 1)  — +1 avoids division by zero
    - is_popular : score > mean score
    """
    avg = df["score"].mean()
    df = df.assign(
        engagement = lambda x: x["num_comments"] / (x["score"] + 1),
        is_popular = lambda x: x["score"] > avg,
    )
    print(f"\nEngagement range : {df['engagement'].min():.2f} – {df['engagement'].max():.2f}")
    print(f"Popular stories  : {df['is_popular'].sum()} / {len(df)}")
    return df


def insights(df: pd.DataFrame) -> None:
    """Print a quick bonus insight on popular-story engagement."""
    avg_eng = df.loc[df["is_popular"], "engagement"].mean()
    print(f"\nPopular stories avg engagement : {avg_eng:.2f}")


def save_csv(df: pd.DataFrame, path: Path) -> None:
    """Write the analysed DataFrame to CSV."""
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8")
    print(f"Saved {len(df)} rows to {path}.")


def main() -> None:
    try:
        df = load_data(INPUT_CSV)
    except FileNotFoundError as e:
        print(e)
        return

    explore(df)
    numpy_stats(df)
    df = add_columns(df)
    insights(df)
    save_csv(df, OUTPUT_CSV)
    print("\nTask 3 complete — ready for Task 4 visualization.")


if __name__ == "__main__":
    main()
