#!/usr/bin/env python3
"""
fetcher.py — Fetch HTML from a URL using httpx.
Falls back to Zyte API if --zyte flag is passed.

Usage:
    python fetcher.py <url>
    python fetcher.py <url> --zyte
"""

import sys
import argparse

def fetch_with_httpx(url: str) -> dict:
    try:
        import httpx
    except ImportError:
        sys.exit("Missing dependency: pip install httpx")

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        )
    }

    try:
        with httpx.Client(follow_redirects=True, timeout=15) as client:
            response = client.get(url, headers=headers)

        if response.status_code in (403, 429, 503):
            return {"status": "BLOCKED", "code": response.status_code, "html": None}

        # Heuristic: if response contains clear bot-detection signals, flag as blocked
        html = response.text
        html_lower = html.lower()
        if len(html) < 200 or any(
            phrase in html_lower
            for phrase in ["captcha", "access denied", "bot detection", "are you a human"]
        ):
            return {"status": "BLOCKED", "code": response.status_code, "html": None}

        return {"status": "OK", "code": response.status_code, "html": html}

    except httpx.RequestError as e:
        return {"status": "ERROR", "error": str(e), "html": None}


def fetch_with_zyte(url: str) -> dict:
    """
    Fetch via Zyte API. Requires ZYTE_API_KEY environment variable.
    pip install zyte-api
    """
    import os
    import json

    api_key = os.environ.get("ZYTE_API_KEY")
    if not api_key:
        sys.exit(
            "ZYTE_API_KEY environment variable not set.\n"
            "Get a free API key at https://www.zyte.com"
        )

    try:
        import httpx
    except ImportError:
        sys.exit("Missing dependency: pip install httpx")

    payload = {"url": url, "httpResponseBody": True}

    try:
        with httpx.Client(timeout=30) as client:
            response = client.post(
                "https://api.zyte.com/v1/extract",
                auth=(api_key, ""),
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

        import base64
        html = base64.b64decode(data["httpResponseBody"]).decode("utf-8", errors="replace")
        return {"status": "OK", "code": 200, "html": html}

    except Exception as e:
        return {"status": "ERROR", "error": str(e), "html": None}


def main():
    parser = argparse.ArgumentParser(description="Fetch HTML from a URL")
    parser.add_argument("url", help="URL to fetch")
    parser.add_argument(
        "--zyte", action="store_true", help="Use Zyte API instead of httpx"
    )
    args = parser.parse_args()

    if args.zyte:
        result = fetch_with_zyte(args.url)
    else:
        result = fetch_with_httpx(args.url)

    if result["status"] == "BLOCKED":
        print(f"BLOCKED (HTTP {result['code']}) — re-run with --zyte flag")
        sys.exit(2)
    elif result["status"] == "ERROR":
        print(f"ERROR — {result['error']}")
        sys.exit(1)
    else:
        print(result["html"])


if __name__ == "__main__":
    main()
