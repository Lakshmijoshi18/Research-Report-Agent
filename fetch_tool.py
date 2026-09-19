"""
FETCH TOOL (upgrade to Step 2)
--------------------------------
Takes a URL and pulls the actual readable text from the page -- not just
the short snippet a search engine shows.

No API key needed. Uses 'requests' to download the page and
'BeautifulSoup' to strip out HTML tags/scripts/ads and keep just the
readable paragraph text.

SETUP (one-time):
  pip install beautifulsoup4 requests
"""

import requests
from bs4 import BeautifulSoup

HEADERS = {
    # Some websites block requests that don't look like a real browser
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}


def fetch_article_text(url: str, max_chars: int = 3000, timeout: int = 8) -> str:
    """
    Downloads a webpage and extracts its main readable text.
    Returns an empty string if the page can't be fetched (this is normal --
    some sites block bots, time out, or aren't real articles. The agent
    should just skip those, not crash).
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=timeout)
        response.raise_for_status()
    except requests.RequestException:
        return ""  # couldn't fetch it -- caller will fall back to snippet

    soup = BeautifulSoup(response.text, "html.parser")

    # Remove elements that are never useful content
    for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
        tag.decompose()

    paragraphs = soup.find_all("p")
    text = " ".join(p.get_text(strip=True) for p in paragraphs)

    # Truncate so we don't blow up the prompt size / cost sent to Gemini
    return text[:max_chars]


if __name__ == "__main__":
    # Quick standalone test
    test_url = input("Enter a URL to fetch: ").strip()
    text = fetch_article_text(test_url)

    if text:
        print(f"\nExtracted {len(text)} characters:\n")
        print(text[:500] + "...")
    else:
        print("\nCould not extract text from this URL (blocked, timed out, or not readable).")
