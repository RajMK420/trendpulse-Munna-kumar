import pandas as pd
import json
import os
from datetime import datetime
from pathlib import Path

DATA_DIR = Path("data")
MIN_SCORE = 5


def find_latest_json() -> Path | None:
    """Return the most recent trends_YYYYMMDD.json path, or None if absent."""
    if not DATA_DIR.exists():
        print("No data/ folder found.")
        return None

    files = sorted(DATA_DIR.glob("trends_*.json"))
    if not files:
        print("No trends_*.json file found.")
        return None

    latest = files[-1]
    print(f"Found: {latest.name}")
    return latest


def load_json_to_df(path: Path) -> pd.DataFrame:
    """Load a JSON file and return a DataFrame."""
    print(f"Loading {path}...")
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    print(f"Loaded {len(df)} stories.")
    return df


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply all cleaning steps and return the tidy DataFrame.

    Steps:
        1. Drop duplicate post_ids (keep first occurrence).
        2. Drop rows missing post_id, title, or score.
        3. Coerce score / num_comments to int, filling gaps with 0.
        4. Remove stories with score below MIN_SCORE.
        5. Strip leading/trailing whitespace from titles.
    """
    original = len(df)

    df = (
        df
        .drop_duplicates(subset=["post_id"], keep="first")
        .dropna(subset=["post_id", "title", "score"])
        .assign(
            score        = lambda x: pd.to_numeric(x["score"],        errors="coerce").fillna(0).astype(int),
            num_comments = lambda x: pd.to_numeric(x["num_comments"], errors="coerce").fillna(0).astype(int),
        )
        .loc[lambda x: x["score"] >= MIN_SCORE]
        .assign(title=lambda x: x["title"].str.strip())
        .reset_index(drop=True)
    )

    removed = original - len(df)
    print(f"Cleaned: {original} -> {len(df)} rows  ({removed} removed).")
    return df


def save_csv(df: pd.DataFrame, path: Path) -> None:
    """Write DataFrame to CSV and print confirmation."""
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8")
    print(f"Saved {len(df)} rows to {path}.")


def print_summary(df: pd.DataFrame, original_count: int) -> None:
    """Print category breakdown and final counts."""
    print("\nStories per category:")
    for cat, count in df["category"].value_counts().items():
        print(f"  {cat:<15} {count:>3}")
    print(f"\nTask 2 complete: {original_count} -> {len(df)} stories cleaned.")


def main() -> None:
    json_path = find_latest_json()
    if json_path is None:
        return

    df = load_json_to_df(json_path)
    original_count = len(df)

    df = clean(df)

    save_csv(df, DATA_DIR / "trends_clean.csv")
    print_summary(df, original_count)


if __name__ == "__main__":
    main()
