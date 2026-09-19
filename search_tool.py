"""
STEP 2: The Search Tool
------------------------
This step takes the sub-questions from Step 1 (the Planner) and actually
searches the live web for each one.

No API key needed for this step -- duckduckgo-search is completely free
and doesn't require any signup.

What it does:
  1. Takes a single sub-question (a string)
  2. Searches the web for it
  3. Returns the top results as a list of dicts: {title, url, snippet}

This does NOT call Claude/Gemini at all. It's a plain web search tool that
your agent will use as one of its "actions".

SETUP (one-time):
  pip install duckduckgo-search
"""

import time
from duckduckgo_search import DDGS


def search_web(query: str, max_results: int = 3, max_retries: int = 3) -> list[dict]:
    """
    Search the web for a query and return the top results.
    Each result is a dict with 'title', 'href' (the URL), and 'body' (a short snippet).

    DuckDuckGo's free search sometimes rate-limits rapid automated requests
    and raises an error even when results DO exist. We catch broadly here
    (not one specific exception class) because the underlying library has
    changed its exception names between versions -- broad catching is more
    reliable than guessing the exact class. We retry a couple of times with
    a short delay before giving up gracefully.
    """
    for attempt in range(1, max_retries + 1):
        try:
            results = []
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=max_results):
                    results.append({
                        "title": r.get("title", ""),
                        "url": r.get("href", ""),
                        "snippet": r.get("body", ""),
                    })
            return results

        except Exception as e:
            if attempt == max_retries:
                print(f"    Search failed for '{query}' after {max_retries} attempts ({e}). Skipping it.")
                return []  # give up gracefully -- don't crash the whole agent
            wait = 3 * attempt
            print(f"    Search issue ({e}), retrying in {wait}s (attempt {attempt}/{max_retries})...")
            time.sleep(wait)


if __name__ == "__main__":
    # Quick standalone test -- run this file directly to try it out
    query = input("Enter something to search: ").strip()

    if not query:
        print("Please enter a search query.")
    else:
        print(f"\nSearching for: {query}\n")
        results = search_web(query)

        if results:
            for i, r in enumerate(results, start=1):
                print(f"{i}. {r['title']}")
                print(f"   {r['url']}")
                print(f"   {r['snippet'][:150]}...")
                print()
        else:
            print("No results found.")
