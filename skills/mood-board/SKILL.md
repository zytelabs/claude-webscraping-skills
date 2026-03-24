---
name: mood-board
description: Finds visually similar products from an image or text description and generates an HTML mood board with product cards, prices, and buy links. Uses the serp-search skill to discover products and the product-extractor skill to get structured data from each result. Use when the user provides a product image, screenshot, or description and wants to find similar items across the web.
---

# Mood Board Generator

## Overview
This skill chains two other skills together:
1. **serp-search**: finds product URLs from a search query
2. **product-extractor**: extracts structured product data from each URL

The mood board skill orchestrates the full pipeline: image description, search, filtering, extraction, and HTML generation.

## Instructions

### Step 1: Get the search query
- If the user provides an **image or screenshot**: describe the item in a 4-5 word shopping search query. Focus on the most distinctive visual features: color, texture or material, silhouette, and garment type. Shorter queries return more product pages.
  - Good: "pink fringe strapless gown"
  - Bad: "blush pink strapless fringe tassel floor length evening gown"
- If the user provides a **text description**: clean it up into a 4-5 word search query.

### Step 2: Search for products
Run the **serp-search** skill twice with slightly different queries to get broader results:
- Query 1: `<description> buy online`
- Query 2: `<description> shop` (rephrase slightly, e.g., swap one adjective)

Combine results and deduplicate by URL.

### Step 3: Filter URLs
Remove category and search pages. Skip URLs that contain any of these patterns:
- `/collections/`
- `/browse/`
- `/cat/`
- `/list/`
- `/s?k=`
- `/s?field`
- `filterBy`
- `refine/`
- `searchQuery`
- `color_`
- `/v/`

Keep the first 6-8 URLs that pass the filter.

### Step 4: Extract product data
Run the **product-extractor** skill on each filtered URL.

For each product, collect:
- `name` (use the first variant name if multiple variants exist, strip size suffixes like "- Small")
- `price` (use the first variant price)
- `currency`
- `image` (use the first product image URL)
- `url` (the product page URL)
- `brand` (if available)
- `color` (if available)

Skip any URL where extraction fails or returns no product name.

### Step 5: Fetch and embed images
Run `scripts/fetch_images.py` with the collected product data as JSON input to add `image_base64` to each product:

```bash
echo '<product_data_json>' | python scripts/fetch_images.py "$ZYTE_API_KEY" > enriched_products.json
```

This step embeds product images as base64 data URIs so the final HTML renders reliably in sandboxed environments.

### Step 6: Generate the mood board
Run `scripts/generate_moodboard.py` with the enriched product JSON:

```bash
cat enriched_products.json | python scripts/generate_moodboard.py "<search_query>"
```

The script generates an HTML file called `moodboard.html` in the current directory.

Present the file to the user and summarize: how many products were found, the price range, and which sites they came from.

## Example interaction

**User:** *drops a screenshot of a dress* "Find me similar dresses"

**Claude:**
1. Describes the image: "pink fringe strapless gown"
2. Runs serp-search with "pink fringe strapless gown buy online"
3. Runs serp-search with "pink strapless fringe evening dress shop"
4. Filters out category pages, keeps 6 product URLs
5. Runs product-extractor on each URL
6. Fetches product images and embeds them as base64
7. Generates moodboard.html with 5 products ($79 - $749)
8. Presents the file and summary to the user

## Requirements
* The **serp-search** skill must be installed.
* The **product-extractor** skill must be installed.
* Ensure `ZYTE_API_KEY` is set in the environment.
* Ensure `requests` is installed.
