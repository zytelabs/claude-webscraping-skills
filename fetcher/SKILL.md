---
name: fetcher
description: Fetches raw HTML from a URL using httpx, with automatic fallback to Zyte API if blocked.
---

# Fetcher

Fetch the raw HTML of a URL and return it for further processing.

## When to use
Use this skill when the user provides one or more URLs and asks you to fetch, retrieve, scrape, or get the HTML or page content.

## Instructions
1. Run `fetcher.py` with the URL as an argument:
   ```
   python fetcher.py <url>
   ```
2. If the script returns a successful HTML response, return the HTML to the conversation for use in the next step.
3. If the script returns a `BLOCKED` status, re-run with the `--zyte` flag:
   ```
   python fetcher.py <url> --zyte
   ```
4. Inform the user if a URL could not be fetched after both attempts.

## Notes
- For multiple URLs, run the script once per URL
- Pass the raw HTML output into the Parser skill for extraction
