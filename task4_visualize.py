import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

DATA_DIR   = Path("data")
OUTPUT_DIR = Path("outputs")
INPUT_CSV  = DATA_DIR / "trends_analysed.csv"

CATEGORY_COLORS = ["#534AB7", "#1D9E75", "#D85A30", "#D4537E", "#BA7517"]


def shorten(title: str, max_len: int = 50) -> str:
    """Truncate a title to max_len characters, appending '...' if needed."""
    return title[:max_len - 3] + "..." if len(title) > max_len else title


def load_data(path: Path) -> pd.DataFrame:
    """Load the analysed CSV produced by Task 3."""
    if not path.exists():
        raise FileNotFoundError(f"{path} not found — run Task 3 first.")
    df = pd.read_csv(path)
    print(f"Loaded {len(df)} stories from {path.name}.")
    return df


def chart_top10(df: pd.DataFrame, ax: plt.Axes | None = None) -> None:
    """Horizontal bar chart of the top 10 stories by score."""
    top10 = (
        df.nlargest(10, "score")[["title", "score"]]
        .assign(label=lambda x: x["title"].map(shorten))
    )

    standalone = ax is None
    if standalone:
        _, ax = plt.subplots(figsize=(10, 6))

    bars = ax.barh(top10["label"], top10["score"], color="#85B7EB")
    ax.invert_yaxis()
    ax.set_xlabel("Score")
    ax.set_title("Top 10 stories by score")

    for bar, score in zip(bars, top10["score"]):
        ax.text(
            bar.get_width() + 0.5,
            bar.get_y() + bar.get_height() / 2,
            str(score), va="center", fontsize=9,
        )

    if standalone:
        plt.tight_layout()
        _save("chart1_top_stories.png")


def chart_categories(df: pd.DataFrame, ax: plt.Axes | None = None) -> None:
    """Vertical bar chart of story counts per category."""
    counts = df["category"].value_counts()

    standalone = ax is None
    if standalone:
        _, ax = plt.subplots(figsize=(10, 6))

    bars = ax.bar(counts.index, counts.values, color=CATEGORY_COLORS[: len(counts)])
    ax.set_xlabel("Category")
    ax.set_ylabel("Stories")
    ax.set_title("Stories per category")
    ax.tick_params(axis="x", rotation=45)

    for bar in bars:
        h = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            h + 0.5, str(int(h)),
            ha="center", va="bottom", fontsize=9,
        )

    if standalone:
        plt.tight_layout()
        _save("chart2_categories.png")


def chart_scatter(df: pd.DataFrame, ax: plt.Axes | None = None) -> None:
    """Scatter plot of score vs comments, coloured by popularity."""
    popular     = df[df["is_popular"]]
    not_popular = df[~df["is_popular"]]

    standalone = ax is None
    if standalone:
        _, ax = plt.subplots(figsize=(10, 8))

    ax.scatter(not_popular["score"], not_popular["num_comments"],
               c="#B5D4F4", alpha=0.6, s=60, label="Not popular")
    ax.scatter(popular["score"], popular["num_comments"],
               c="#EF9F27", alpha=0.7, s=80, label="Popular",
               edgecolors="#854F0B", linewidths=0.5)

    ax.set_xlabel("Score")
    ax.set_ylabel("Comments")
    ax.set_title("Score vs comments")
    ax.legend()
    ax.grid(True, alpha=0.25)

    if standalone:
        plt.tight_layout()
        _save("chart3_scatter.png")


def dashboard(df: pd.DataFrame) -> None:
    """1x3 dashboard combining all three charts."""
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 5))

    chart_top10(df, ax=ax1)
    chart_categories(df, ax=ax2)
    chart_scatter(df, ax=ax3)

    fig.suptitle("TrendPulse dashboard", fontsize=15, fontweight="500")
    plt.tight_layout()
    _save("dashboard.png")


def _save(filename: str) -> None:
    """Save the current figure to OUTPUT_DIR and close it."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / filename
    plt.savefig(path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved: {path}")


def main() -> None:
    try:
        df = load_data(INPUT_CSV)
    except FileNotFoundError as e:
        print(e)
        return

    chart_top10(df)
    chart_categories(df)
    chart_scatter(df)
    dashboard(df)

    print("\nTask 4 complete — 4 PNG files created in outputs/.")
    print("Full pipeline done: Collect -> Clean -> Analyse -> Visualize.")


if __name__ == "__main__":
    main()
