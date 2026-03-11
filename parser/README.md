# parser skill

A Claude skill that extracts structured product data from raw HTML. Tries JSON-LD via Extruct first, falls back to CSS selectors via Parsel.

## Overview

The parser skill gives Claude the ability to extract structured data from raw HTML as part of an automated workflow. Drop the `SKILL.md` into your Claude skills folder and Claude will know when to reach for it, which extraction method to use, and when to ask you for more specific field requirements.

It is the second step in the scraping pipeline, sitting between the [fetcher skill](../fetcher/) and the compare skill.

## What it does

When given an HTML file, Claude runs `parser.py` and returns a structured JSON object. The script tries two extraction methods in order:

1. **Extruct** — reads JSON-LD, microdata, and OpenGraph structured data embedded in the page. Stable, maintenance-free, and the preferred path whenever available.
2. **Parsel** — falls back to heuristic CSS selectors if no structured metadata is found. More flexible, but worth reviewing on unusual page layouts.

The output includes a `method` field so Claude — and you — always know how the data was obtained.

## Installation

Copy the skill folder into your Claude skills directory:

```
skills/
└── parser/
    ├── SKILL.md      ← Claude reads this
    └── parser.py
```

Install the Python dependencies:

```bash
pip install extruct parsel
```

## How Claude uses it

Claude triggers this skill when you have raw HTML and need to extract structured data from it. The `SKILL.md` file defines this behaviour:

```markdown
## When to use
Use this skill when you have raw HTML and need to extract structured data from
it — product details, prices, specs, ratings, or any page content.
```

In practice, Claude will typically run this skill immediately after the fetcher skill has retrieved your HTML. If the Parsel fallback is used and key fields are missing, Claude will ask you which fields you need and re-run with the `--fields` flag — no manual intervention required.

## Example prompts

```
Extract the product data from this HTML file
```

```
Fetch https://example.com/product/123 and parse the product details
```

```
Get the name, price, and rating from each of these pages: [list of URLs]
```

## Output

Claude returns a JSON object with a `method` field and a `data` object containing the extracted fields — name, price, currency, availability, rating, review count, brand, SKU, and specs where available.

The `method` field tells you how the data was extracted:

| Value | Meaning |
|-------|---------|
| `"extruct"` | Structured metadata found — clean and reliable, use directly |
| `"parsel"` | Fell back to CSS selectors — review for completeness on unusual layouts |

## Pipeline

The parser skill is designed to sit between the fetcher skill and the compare skill:

```
fetcher skill → raw HTML → parser skill → structured JSON → compare skill
```

## Requirements

- Python 3.10+
- `extruct` (`pip install extruct`)
- `parsel` (`pip install parsel`)
