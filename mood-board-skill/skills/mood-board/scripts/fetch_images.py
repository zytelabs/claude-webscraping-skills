"""
Fetch product images via Zyte API and return base64-encoded data.

Usage:
    echo '[{"image": "https://...", "url": "https://..."}]' | python fetch_images.py <api_key>

Input:  JSON array of product objects (must have "image" key with URL)
Output: JSON array of same objects with "image_base64" key added (data URI string)

Products where image download fails will have image_base64 set to null.
"""

import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests


def fetch_image(api_key: str, image_url: str) -> str | None:
    """Download a single image via Zyte API and return a data URI string."""
    try:
        resp = requests.post(
            "https://api.zyte.com/v1/extract",
            auth=(api_key, ""),
            json={"url": image_url, "httpResponseBody": True},
            timeout=30,
        )
        if resp.status_code != 200:
            return None

        body_b64 = resp.json().get("httpResponseBody")
        if not body_b64:
            return None

        # Detect MIME type from URL extension (fallback to jpeg).
        ext = image_url.split("?")[0].rsplit(".", 1)[-1].lower()
        mime_map = {
            "png": "image/png",
            "webp": "image/webp",
            "gif": "image/gif",
            "svg": "image/svg+xml",
        }
        mime = mime_map.get(ext, "image/jpeg")

        return f"data:{mime};base64,{body_b64}"
    except Exception:
        return None


def fetch_all_images(api_key: str, products: list) -> list:
    """Fetch images for all products in parallel and add image_base64 field."""
    # Build work items: (index, image_url)
    work: list[tuple[int, str]] = []
    for i, p in enumerate(products):
        img = p.get("image", "")
        if img and img.startswith("http"):
            work.append((i, img))

    # Fetch in parallel (max 4 concurrent to stay within Zyte rate limits).
    results: dict[int, str | None] = {}
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(fetch_image, api_key, url): idx for idx, url in work}
        for future in as_completed(futures):
            idx = futures[future]
            try:
                results[idx] = future.result()
            except Exception:
                results[idx] = None

    # Attach base64 data to products.
    for i, p in enumerate(products):
        p["image_base64"] = results.get(i)

    return products


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: echo '<json>' | python fetch_images.py <api_key>", file=sys.stderr)
        sys.exit(1)

    api_key = sys.argv[1]
    raw = sys.stdin.read().strip()

    try:
        products = json.loads(raw)
    except json.JSONDecodeError:
        print("Error: invalid JSON input", file=sys.stderr)
        sys.exit(1)

    enriched = fetch_all_images(api_key, products)

    # Report.
    total = len(enriched)
    success = sum(1 for p in enriched if p.get("image_base64"))
    print(f"Fetched {success}/{total} images", file=sys.stderr)
    print(json.dumps(enriched))

"""
Fetch product images via Zyte API and return base64-encoded data.

Usage:
    echo '[{"image": "https://...", "url": "https://..."}]' | python fetch_images.py <api_key>

Input:  JSON array of product objects (must have "image" key with URL)
Output: JSON array of same objects with "image_base64" key added (data URI string)

Products where image download fails will have image_base64 set to null.
"""

import base64
import json
import sys
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed


def fetch_image(api_key: str, image_url: str) -> str | None:
    """Download a single image via Zyte API and return a data URI string."""
    try:
        resp = requests.post(
            "https://api.zyte.com/v1/extract",
            auth=(api_key, ""),
            json={"url": image_url, "httpResponseBody": True},
            timeout=30,
        )
        if resp.status_code != 200:
            return None

        body_b64 = resp.json().get("httpResponseBody")
        if not body_b64:
            return None

        # Detect MIME type from URL extension (fallback to jpeg)
        ext = image_url.split("?")[0].rsplit(".", 1)[-1].lower()
        mime_map = {"png": "image/png", "webp": "image/webp", "gif": "image/gif", "svg": "image/svg+xml"}
        mime = mime_map.get(ext, "image/jpeg")

        return f"data:{mime};base64,{body_b64}"
    except Exception:
        return None


def fetch_all_images(api_key: str, products: list) -> list:
    """Fetch images for all products in parallel and add image_base64 field."""
    # Build work items: (index, image_url)
    work = []
    for i, p in enumerate(products):
        img = p.get("image", "")
        if img and img.startswith("http"):
            work.append((i, img))

    # Fetch in parallel (max 4 concurrent to stay within Zyte rate limits)
    results = {}
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(fetch_image, api_key, url): idx for idx, url in work}
        for future in as_completed(futures):
            idx = futures[future]
            try:
                results[idx] = future.result()
            except Exception:
                results[idx] = None

    # Attach base64 data to products
    for i, p in enumerate(products):
        p["image_base64"] = results.get(i)

    return products


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: echo '<json>' | python fetch_images.py <api_key>", file=sys.stderr)
        sys.exit(1)

    api_key = sys.argv[1]
    raw = sys.stdin.read().strip()

    try:
        products = json.loads(raw)
    except json.JSONDecodeError:
        print("Error: invalid JSON input", file=sys.stderr)
        sys.exit(1)

    enriched = fetch_all_images(api_key, products)

    # Report
    total = len(enriched)
    success = sum(1 for p in enriched if p.get("image_base64"))
    print(f"Fetched {success}/{total} images", file=sys.stderr)
    print(json.dumps(enriched))