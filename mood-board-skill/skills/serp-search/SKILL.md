---
name: serp-search
description: Searches Google via Zyte API and returns structured organic results (URLs, titles, descriptions, ranks). Use when the user wants to find web pages, product listings, or search results for a query. Handles anti-bot protection and returns clean structured data.
---

# SERP Search

## Instructions
1. **Trigger:** Use this skill when the user provides a search query and wants to find relevant web pages or product listings.
2. **Execution:** Run the Python script `scripts/serp_search.py` with two arguments:
    * Argument 1: The Zyte API Key (retrieve from the environment variable `ZYTE_API_KEY`).
    * Argument 2: The search query as a quoted string.
    * *Command Example:* `python scripts/serp_search.py $ZYTE_API_KEY "pink fringe strapless gown buy online"`
3. **Output Processing:**
    * The script prints a JSON array of organic search results.
    * Each result contains: `url`, `name`, `description`, `rank`.
    * Present results to the user as a clean numbered list with title and URL.
    * If no results are returned, suggest the user try a shorter or different query.

## Tips for better results
- Shorter queries (4-6 words) return more product pages than long descriptive queries.
- Adding "buy online" or "shop" to a query biases results toward product pages rather than informational content.
- URLs containing `/collections/`, `/browse/`, `/s?k=`, `filterBy`, or `/refine/` are typically category pages, not individual products.

## Requirements
* Ensure the `requests` library is installed (`pip install requests`).
* Ensure `ZYTE_API_KEY` is set in the environment.
