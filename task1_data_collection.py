import requests
import json
import time
from datetime import datetime
import os

CATEGORIES = {
    "technology":   ["ai", "software", "tech", "code", "computer", "data", "cloud", "api", "gpu", "llm"],
    "worldnews":    ["war", "government", "country", "president", "election", "climate", "attack", "global"],
    "sports":       ["nfl", "nba", "fifa", "sport", "game", "team", "player", "league", "championship"],
    "science":      ["research", "study", "space", "physics", "biology", "discovery", "nasa", "genome"],
    "entertainment":["movie", "film", "music", "netflix", "game", "book", "show", "award", "streaming"],
}

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "TrendPulse/1.0"})


def categorize_story(title: str) -> str:
    """Return the first matching category for a story title, or 'uncategorized'."""
    if not title:
        return "uncategorized"
    title_lower = title.lower()
    return next(
        (cat for cat, kws in CATEGORIES.items() for kw in kws if kw in title_lower),
        "uncategorized",
    )


def fetch_top_story_ids() -> list:
    """Fetch the first 500 top story IDs from HackerNews."""
    url = "https://hacker-news.firebaseio.com/v0/topstories.json"
    try:
        response = SESSION.get(url, timeout=10)
        response.raise_for_status()
        return response.json()[:500]
    except Exception as e:
        print(f"Error fetching top stories: {e}")
        return []


def fetch_story_details(story_id: int) -> dict | None:
    """Fetch a single story's details by ID."""
    url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
    try:
        response = SESSION.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Failed to fetch story {story_id}: {e}")
        return None


def build_story_record(story: dict, category: str) -> dict:
    """Build a clean record dict from a raw HackerNews story."""
    return {
        "post_id":      story.get("id"),
        "title":        story.get("title"),
        "category":     category,
        "score":        story.get("score", 0),
        "num_comments": story.get("descendants", 0),
        "author":       story.get("by", "unknown"),
        "collected_at": datetime.now().isoformat(),
    }


def main():
    print("Fetching top story IDs...")
    story_ids = fetch_top_story_ids()
    print(f"Found {len(story_ids)} top stories")

    category_counts = {cat: 0 for cat in CATEGORIES}
    all_stories = []

    # enumerate() to detect the last category without rebuilding list each iteration
    for i, category in enumerate(CATEGORIES):
        print(f"\nProcessing {category} category...")
        category_stories = []

        for story_id in story_ids:
            if category_counts[category] >= 25:
                break

            story = fetch_story_details(story_id)
            if not story:
                continue

            title = story.get("title", "")
            if not title or categorize_story(title) != category:
                continue

            record = build_story_record(story, category)
            all_stories.append(record)
            category_stories.append(record)
            category_counts[category] += 1
            print(f"  Added: {title[:60]}... (#{category_counts[category]}/25)")

        print(f"Collected {len(category_stories)} {category} stories")

        if i < len(CATEGORIES) - 1:
            print("Waiting 2 seconds before next category...")
            time.sleep(2)

    os.makedirs("data", exist_ok=True)
    filename = f"data/trends_{datetime.now().strftime('%Y%m%d')}.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(all_stories, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*50}")
    print(f"Collected {len(all_stories)} stories. Saved to {filename}")
    print(f"{'='*50}")
    print("Category breakdown:")
    for cat, count in category_counts.items():
        print(f"  {cat}: {count} stories")


if __name__ == "__main__":
    main()
