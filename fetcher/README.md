# fetcher skill

A Claude skill that fetches raw HTML from a URL using httpx, with automatic fallback to Zyte API if blocked.

## Overview

The fetcher skill gives Claude the ability to retrieve raw HTML from any URL as part of an automated workflow. Drop the `SKILL.md` into your Claude skills folder and Claude will know when to reach for it, how to run it, and how to handle blocked requests — without any manual prompting.

It is the first step in the scraping pipeline, designed to hand off directly to the [parser skill](../parser/).

## What it does

When given a URL, Claude runs `fetcher.py` via httpx. If the site blocks the request, Claude automatically retries using Zyte API. If both attempts fail, Claude reports the failure clearly rather than continuing with incomplete data.

## Installation

Copy the skill folder into your Claude skills directory:

```
skills/
└── fetcher/
    ├── SKILL.md      ← Claude reads this
    ├── fetcher.py
    └── .env          ← add your Zyte API key here (optional)
```

Install the Python dependency:

```bash
pip install httpx
```

For Zyte API fallback, add your API key to a `.env` file in the skill folder:

```
ZYTE_API_KEY=your_key_here
```

## How Claude uses it

Claude triggers this skill when you ask it to fetch, retrieve, scrape, or get the HTML content of a URL. The `SKILL.md` file defines this behaviour:

```markdown
## When to use
Use this skill when the user provides one or more URLs and asks you to fetch,
retrieve, scrape, or get the HTML or page content.
```

Once triggered, Claude follows a two-step process:

1. Attempt a standard httpx request
2. If the response returns a `BLOCKED` status, retry via Zyte API

Claude surfaces any failure to you explicitly — it will never silently drop a URL and continue.

## Example prompts

```
Fetch the HTML from https://example.com/product/123
```

```
Get the page content for each of these URLs: [list]
```

```
Scrape https://example.com and pass the HTML to the parser skill
```

## Pipeline

The fetcher skill is designed to be used in sequence with the parser skill:

```
fetcher skill → raw HTML → parser skill → structured JSON
```

## Requirements

- Python 3.10+
- `httpx` (`pip install httpx`)
- A Zyte API key (only required for the fallback path)
