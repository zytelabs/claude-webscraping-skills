#!/usr/bin/env python3
"""
parser.py — Extract structured product data from HTML.
Tries Extruct (JSON-LD / microdata) first, falls back to Parsel CSS selectors.

Usage:
    python parser.py page.html
    python parser.py page.html --fields "price,rating,brand"
"""

import sys
import json
import argparse
import re


# ---------------------------------------------------------------------------
# Path 1: Extruct — structured metadata (JSON-LD, microdata, OpenGraph)
# ---------------------------------------------------------------------------

def extract_with_extruct(html: str, url: str = "http://example.com") -> dict | None:
    try:
        import extruct
    except ImportError:
        sys.exit("Missing dependency: pip install extruct")

    try:
        data = extruct.extract(
            html,
            base_url=url,
            syntaxes=["json-ld", "microdata", "opengraph"],
            uniform=True,
        )
    except Exception as e:
        return None

    product = {}

    # --- JSON-LD ---
    for item in data.get("json-ld", []):
        item_type = item.get("@type", "")
        if isinstance(item_type, list):
            item_type = item_type[0]
        if "Product" in str(item_type):
            product["name"] = item.get("name")
            product["description"] = item.get("description")
            product["brand"] = _nested(item, "brand", "name")

            offers = item.get("offers", {})
            if isinstance(offers, list):
                offers = offers[0]
            product["price"] = offers.get("price") or offers.get("lowPrice")
            product["currency"] = offers.get("priceCurrency")
            product["availability"] = offers.get("availability", "").split("/")[-1]

            agg = item.get("aggregateRating", {})
            product["rating"] = agg.get("ratingValue")
            product["review_count"] = agg.get("reviewCount")

            product["sku"] = item.get("sku") or item.get("mpn")

            specs = item.get("additionalProperty", [])
            if specs:
                product["specs"] = {
                    s.get("name"): s.get("value") for s in specs if s.get("name")
                }
            break

    # --- Microdata fallback ---
    if not product:
        for item in data.get("microdata", []):
            if "Product" in str(item.get("type", "")):
                props = item.get("properties", {})
                product["name"] = _first(props.get("name"))
                product["price"] = _first(props.get("price"))
                product["rating"] = _first(props.get("ratingValue"))
                break

    # --- OpenGraph fallback ---
    if not product:
        og = {k: v for d in data.get("opengraph", []) for k, v in d.items()}
        if og.get("og:type") in ("product", "og:product"):
            product["name"] = og.get("og:title")
            product["price"] = og.get("og:price:amount") or og.get("product:price:amount")
            product["currency"] = og.get("og:price:currency") or og.get("product:price:currency")

    # Strip None values
    product = {k: v for k, v in product.items() if v is not None}

    return product if product else None


# ---------------------------------------------------------------------------
# Path 2: Parsel — CSS selector heuristics
# ---------------------------------------------------------------------------

SELECTOR_CANDIDATES = {
    "name": [
        "h1.product-title::text",
        "h1[itemprop='name']::text",
        "h1::text",
        "[class*='product-name']::text",
        "[class*='product-title']::text",
    ],
    "price": [
        "[itemprop='price']::attr(content)",
        "[itemprop='price']::text",
        "[class*='price']::text",
        "[id*='price']::text",
        "span.price::text",
    ],
    "rating": [
        "[itemprop='ratingValue']::attr(content)",
        "[itemprop='ratingValue']::text",
        "[class*='rating']::attr(aria-label)",
        "[class*='stars']::attr(aria-label)",
    ],
    "review_count": [
        "[itemprop='reviewCount']::text",
        "[class*='review-count']::text",
        "[class*='reviews']::text",
    ],
    "availability": [
        "[itemprop='availability']::attr(content)",
        "[class*='availability']::text",
        "[class*='stock']::text",
        "[id*='availability']::text",
    ],
    "brand": [
        "[itemprop='brand']::text",
        "[class*='brand']::text",
        "[id*='brand']::text",
    ],
    "sku": [
        "[itemprop='sku']::text",
        "[itemprop='mpn']::text",
        "[class*='sku']::text",
    ],
}


def extract_with_parsel(html: str, requested_fields: list[str] | None = None) -> dict:
    try:
        from parsel import Selector
    except ImportError:
        sys.exit("Missing dependency: pip install parsel")

    sel = Selector(text=html)
    fields = requested_fields or list(SELECTOR_CANDIDATES.keys())
    product = {}

    for field in fields:
        candidates = SELECTOR_CANDIDATES.get(field, [])
        for css in candidates:
            try:
                value = sel.css(css).get()
                if value:
                    product[field] = value.strip()
                    break
            except Exception:
                continue

    # Specs: look for definition lists or attribute tables
    rows = sel.css("table.product-attributes tr, dl.specs dt, [class*='spec'] [class*='label']")
    if rows:
        specs = {}
        for row in rows:
            label = row.css("::text").get("").strip()
            value_sel = row.xpath("following-sibling::*[1]//text()").getall()
            value = " ".join(v.strip() for v in value_sel if v.strip())
            if label and value:
                specs[label] = value
        if specs:
            product["specs"] = specs

    # Offers: look for promotional text
    offer_texts = sel.css(
        "[class*='offer']::text, [class*='promo']::text, [class*='deal']::text, [class*='badge']::text"
    ).getall()
    offers = [t.strip() for t in offer_texts if len(t.strip()) > 3]
    if offers:
        product["offers"] = offers[:5]  # cap at 5

    return product


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _nested(d: dict, *keys):
    for k in keys:
        if not isinstance(d, dict):
            return None
        d = d.get(k)
    return d


def _first(val):
    if isinstance(val, list):
        return val[0] if val else None
    return val


def clean_price(value: str | None) -> str | None:
    if not value:
        return None
    match = re.search(r"[\d,]+\.?\d*", value.replace(",", ""))
    return match.group() if match else value.strip()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Extract structured product data from HTML")
    parser.add_argument("html_file", help="Path to saved HTML file")
    parser.add_argument(
        "--fields",
        help="Comma-separated list of fields to extract (Parsel path only)",
        default=None,
    )
    parser.add_argument(
        "--url",
        help="Original URL (improves Extruct base URL resolution)",
        default="http://example.com",
    )
    args = parser.parse_args()

    try:
        with open(args.html_file, "r", encoding="utf-8", errors="replace") as f:
            html = f.read()
    except FileNotFoundError:
        sys.exit(f"File not found: {args.html_file}")

    requested_fields = [f.strip() for f in args.fields.split(",")] if args.fields else None

    # Try Extruct first
    result = extract_with_extruct(html, url=args.url)
    method = "extruct"

    # Fall back to Parsel if Extruct found nothing useful
    if not result:
        result = extract_with_parsel(html, requested_fields=requested_fields)
        method = "parsel"

    output = {
        "method": method,
        "data": result,
    }

    print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
