# fetcher

Fetches raw HTML from a URL using httpx, with automatic fallback to Zyte API if blocked.

## Overview

`fetcher.py` is a single-file HTML retrieval script designed to be the first step in a scraping pipeline. It attempts a standard httpx request first, detects common blocking signals, and retries via Zyte API if needed — returning raw HTML or a clear status on failure.

## Requirements

**Python:** 3.10+

**Dependencies:**

```bash
pip install httpx
```

For Zyte API fallback:

```bash
pip install httpx  # already required above
```

No additional package is needed for the Zyte API path — requests are made directly via httpx. A valid `ZYTE_API_KEY` is required (see [Configuration](#configuration)).

## Usage

### Standard fetch

```bash
python fetcher.py <url>
```

### Zyte API fallback

```bash
python fetcher.py <url> --zyte
```

Pass `--zyte` directly if you already know a site is likely to block standard requests, or in response to a `BLOCKED` status from a previous attempt.

## Output

On success, the script prints raw HTML to stdout.

On failure, it prints a status message and exits with a non-zero code:

| Exit code | Meaning |
|-----------|---------|
| `0` | Success — HTML printed to stdout |
| `1` | Request error (network issue, timeout, etc.) |
| `2` | Blocked — re-run with `--zyte` |

### Blocked detection

The script treats a response as blocked if any of the following are true:

- HTTP status code is `403`, `429`, or `503`
- Response body is fewer than 200 characters
- Response body contains any of: `captcha`, `access denied`, `bot detection`, `are you a human`

## Configuration

Zyte API requires an API key. Set it as an environment variable:

```bash
export ZYTE_API_KEY=your_key_here
```

Or add it to a `.env` file in the same directory as `fetcher.py`:

```
ZYTE_API_KEY=your_key_here
```

The script loads `.env` automatically — no additional library required.

## Examples

Fetch a single page:

```bash
python fetcher.py https://example.com/product/123
```

Pipe HTML directly into a file for downstream processing:

```bash
python fetcher.py https://example.com/product/123 > page.html
```

Retry a blocked URL via Zyte API:

```bash
python fetcher.py https://example.com/product/123 --zyte > page.html
```

## Pipeline

This script is designed to hand off to the [parser](../parser/) skill. Pass the HTML output to `parser.py` for structured data extraction:

```bash
python fetcher.py https://example.com/product/123 > page.html
python ../parser/parser.py page.html
```

## Files

```
fetcher/
├── fetcher.py   # Main script
├── SKILL.md     # Claude skill definition
└── .env         # API key (create this yourself, not tracked in git)
```
