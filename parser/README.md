# parser

Extracts structured product data from raw HTML. Tries JSON-LD via Extruct first, falls back to CSS selectors via Parsel.

## Overview

`parser.py` takes a saved HTML file and returns a JSON object containing structured product data. It uses two extraction methods in order of preference: Extruct for clean structured metadata (JSON-LD, microdata, OpenGraph), and Parsel CSS selectors as a heuristic fallback. The output includes a `method` field so you always know how the data was obtained.

## Requirements

**Python:** 3.10+

**Dependencies:**

```bash
pip install extruct parsel
```

## Usage

### Basic extraction

```bash
python parser.py page.html
```

### Specify fields (Parsel path only)

```bash
python parser.py page.html --fields "price,rating,brand"
```

The `--fields` flag only applies when the script falls back to Parsel. Extruct extracts all available fields from structured metadata automatically.

### Pass the original URL for better resolution

```bash
python parser.py page.html --url "https://example.com/product/123"
```

Providing `--url` improves Extruct's base URL resolution for relative links embedded in JSON-LD.

## Output

The script prints a JSON object to stdout:

```json
{
  "method": "extruct",
  "data": {
    "name": "Example Product",
    "price": "29.99",
    "currency": "USD",
    "availability": "InStock",
    "rating": "4.5",
    "review_count": "128",
    "brand": "Example Brand",
    "sku": "EX-123",
    "specs": {
      "Weight": "1.2kg",
      "Dimensions": "30 x 20 x 10cm"
    }
  }
}
```

### The `method` field

| Value | Meaning |
|-------|---------|
| `"extruct"` | Structured metadata found — data is clean and reliable, use directly |
| `"parsel"` | Fell back to CSS selectors — review fields for completeness, especially on unusual layouts |

Always check the `method` field before using the output downstream.

## Extraction methods

### Method 1: Extruct (preferred)

Extruct reads structured metadata formats embedded in the page HTML, in this order:

1. **JSON-LD** — the most common and reliable format for product data
2. **Microdata** — an older format, used as a secondary fallback
3. **OpenGraph** — used if neither JSON-LD nor microdata yield a product

Extruct extraction is stable, requires no selector maintenance, and is unaffected by visual page redesigns.

### Method 2: Parsel (fallback)

When Extruct finds no product data, the script falls back to Parsel, which applies a set of heuristic CSS selectors across the page. The following fields are covered:

| Field | Example selectors tried |
|-------|------------------------|
| `name` | `h1.product-title`, `h1[itemprop='name']`, `h1` |
| `price` | `[itemprop='price']`, `[class*='price']`, `span.price` |
| `rating` | `[itemprop='ratingValue']`, `[class*='rating']` |
| `review_count` | `[itemprop='reviewCount']`, `[class*='review-count']` |
| `availability` | `[itemprop='availability']`, `[class*='stock']` |
| `brand` | `[itemprop='brand']`, `[class*='brand']` |
| `sku` | `[itemprop='sku']`, `[itemprop='mpn']`, `[class*='sku']` |

Parsel also attempts to extract specs from definition lists and attribute tables, and promotional text from offer/promo/badge elements.

Parsel selectors are generated heuristically and may need adjustment for unusual page layouts.

## Examples

Extract from a locally saved file:

```bash
python parser.py page.html
```

Extract specific fields only:

```bash
python parser.py page.html --fields "name,price,brand"
```

Full pipeline from fetch to parse:

```bash
python ../fetcher/fetcher.py https://example.com/product/123 > page.html
python parser.py page.html --url "https://example.com/product/123"
```

## Pipeline

This script accepts HTML from the [fetcher](../fetcher/) skill and its output is designed to be passed to the [compare](../compare/) skill for side-by-side analysis across multiple pages.

```
fetcher.py → page.html → parser.py → structured JSON → compare skill
```

## Files

```
parser/
├── parser.py   # Main script
└── SKILL.md    # Claude skill definition
```
