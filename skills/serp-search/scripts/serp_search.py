"""
SERP Search via Zyte API
Fetches Google search results and returns structured organic results.

Usage:
    python serp_search.py <api_key> "<search_query>"
"""

import requests
import json
import sys


def search(api_key: str, query: str) -> list:
    """Search Google via Zyte API SERP extraction."""
    search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"

    response = requests.post(
        "https://api.zyte.com/v1/extract",
        auth=(api_key, ""),
        json={"url": search_url, "serp": True},
        timeout=60,
    )

    if response.status_code != 200:
        print(json.dumps({"error": f"Zyte API returned {response.status_code}"}))
        sys.exit(1)

    serp = response.json().get("serp", {})
    results = serp.get("organicResults", [])

    # Return clean structured results
    clean_results = []
    for r in results:
        clean_results.append({
            "url": r.get("url", ""),
            "name": r.get("name", ""),
            "description": r.get("description", ""),
            "rank": r.get("rank", 0),
        })

    return clean_results


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python serp_search.py <api_key> '<search_query>'")
        sys.exit(1)

    api_key = sys.argv[1]
    query = sys.argv[2]
    results = search(api_key, query)
    print(json.dumps(results, indent=2))
