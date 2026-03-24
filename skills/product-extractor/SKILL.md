---
name: product-extractor
description: Extracts structured product data (price, currency, availability) from e-commerce URLs using Zyte AI.
---

# Product Extractor

## Instructions
1.  **Trigger:** Use this skill when the user provides a product URL and asks for details (price, stock, description).
2.  **Execution:** Run the python script `scripts/fetch_price.py` with two arguments:
    *   Argument 1: The Zyte API Key (Retrieve this from the environment variable `ZYTE_API_KEY`).
    *   Argument 2: The Product URL provided by the user.
    *   *Command Example:* `python scripts/fetch_price.py $ZYTE_API_KEY "https://example.com/product"`
3.  **Output Processing:** 
    *   The script prints a JSON object containing the product details.
    *   Present this data to the user in a clean summary table.
    *   *Fallback:* If the JSON is incomplete, the script also saves `browser_html.html`. Read that file to find missing details if necessary.

## Requirements
*   Ensure the `requests` library is installed (`pip install requests`).
*   Ensure `ZYTE_API_KEY` is set in the environment.
