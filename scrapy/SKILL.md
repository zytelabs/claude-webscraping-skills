---
name: scrapy-quick-spider
description: >
  Build a self-contained single-file Scrapy spider for scraping an ecommerce
  category (product list pages + product detail pages) using Zyte API AI
  extraction. Use this skill whenever the user wants to quickly scrape an
  ecommerce site, crawl a product category, extract product data, or build a
  Scrapy spider fast without a full project setup. Triggers include: "scrape
  this category", "build a spider for", "crawl products from", "get all
  products from", "scrape product listings", or any request to extract
  ecommerce data from a URL. The output is a ready-to-run Python script — no
  project scaffolding needed.
---

# Scrapy Quick Spider

Builds a **single-file, runnable Scrapy spider** for ecommerce category
crawling using Zyte API's AI extraction. No project setup. Just a `.py` file
the user can run immediately.

---

## When to use this skill

User provides a category/listing URL and wants all products from it scraped.
Output is a self-contained Python script saved to their workspace.

---

## What you need from the user

- **Entry URL** — the category or product listing page (e.g. `https://shop.com/category/widgets`)
- **Output format** (optional) — default to `jsonl`

That's it. No detail page URL needed — the spider discovers product URLs from
the listing page automatically.

---

## How it works

The spider uses two Zyte API AI extraction types, chained together:

1. **`productNavigation`** on the category page → returns product URLs + pagination
2. **`product`** on each product URL → returns structured product data

No selectors. No schema definition. No user confirmation step. Just generate
and save.

Read `references/zyte-extraction-fields.md` to understand the exact fields
returned by each extraction type before writing the spider.

---

## Spider architecture

Use `AsyncCrawlerProcess` to run from a script (no project needed):

```python
from scrapy import Spider, Request
from scrapy.crawler import AsyncCrawlerProcess
```

### Spider flow

```
start()
  └─► parse_navigation()       # productNavigation extraction
        ├─► parse_navigation()  # follow nextPage if present
        └─► parse_product()     # product extraction for each item URL
```

### AsyncCrawlerProcess

Use `AsyncCrawlerProcess` instead of `CrawlerProcess` — it manages the asyncio event loop
internally. Do **not** wrap in `asyncio.run()` or use `await process.crawl()`. Call
`process.crawl(Spider)` (sync) then `process.start()` to run. Wrapping in `asyncio.run()`
causes `RuntimeError: Event loop stopped before Future completed` on exit.

All spider methods must be `async`.

### Zyte API integration

Use `zyte_api_automap` in request meta. Always include `errback=self.handle_error` on every
request. Use `productNavigation` for the initial category request — it returns `items[].url`
(product URLs) and `nextPage.url`.

`start()` uses `Request` directly (no response object available). Inside callbacks, use
`response.follow(url, ...)` instead of `Request(url, ...)` — it handles relative URLs
automatically.

**`extractFrom` format:** Use separate `*Options` fields — `productNavigationOptions` and
`productOptions` — always paired with `"httpResponseBody": True`. Do **not** pass `extractFrom`
as a nested dict inside the extraction type field itself (e.g. `"productNavigation": {"extractFrom": ...}`)
— this is invalid and returns a 400.

**`followRedirect`:** Do not include `"followRedirect": True` — it is the default and
`scrapy-zyte-api` will emit a warning and drop it.

```python
# Navigation requests (initial + pagination)
meta={"zyte_api_automap": {
    "httpResponseBody": True,
    "productNavigation": True,
    "productNavigationOptions": {"extractFrom": "httpResponseBody"},
}}

# Product requests
meta={"zyte_api_automap": {
    "httpResponseBody": True,
    "product": True,
    "productOptions": {"extractFrom": "httpResponseBody"},
}}
```

### CrawlerProcess settings

```python
process = AsyncCrawlerProcess(settings={
    "ADDONS": {
        "scrapy_zyte_api.Addon": 500,
    },
    "ZYTE_API_KEY": os.environ.get("ZYTE_API_KEY"),
    "ZYTE_API_TRANSPARENT_MODE": True,
    "FEEDS": {
        output_file: {"format": output_format},
    },
    "LOG_ENABLED": False,
    "ROBOTSTXT_OBEY": False,
    "CONCURRENT_REQUESTS": 32,
})
# Re-silence after AsyncCrawlerProcess reconfigures logging on init
for noisy in ("scrapy", "twisted", "filelock", "hpack", "zyte_api", "scrapy_zyte_api"):
    logging.getLogger(noisy).setLevel(logging.WARNING)
```

### Logging

Use Rich for terminal output + a plain-text file handler. Set `LOG_ENABLED: False` to prevent
Scrapy's own handler conflicting with Rich. The logger silencing must happen **after**
`AsyncCrawlerProcess()` is instantiated — it reconfigures logging on init and will undo earlier silencing.

```python
_file_handler = logging.FileHandler(f"{SPIDER_NAME}.log")
_file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True, markup=True), _file_handler],
)
logger = logging.getLogger(__name__)
```

Log navigation and product requests, and errors via `handle_error`:

```python
logger.info("[blue]Navigating[/] | url=[yellow]%s[/]", url)
logger.info("[blue]Requesting product[/] | url=[yellow]%s[/]", url)
logger.info("[green]Scraped product[/] | name=[bold]%s[/] | sku=[cyan]%s[/]", name, sku)

def handle_error(self, failure):
    logger.error("[red]Request failed[/] | url=[yellow]%s[/] | error=%s", failure.request.url, failure.value)
```

---

## Full script template

See `references/spider-template.py` for the complete, annotated template.
Generate the final spider from this template, substituting in the user's URL,
spider name, and output settings.

## Generating the spider name and output filenames

Derive a clean spider name from the domain:
- `https://shop.example.com/widgets` → `example_com`
- Use only lowercase letters and underscores

Both output files are derived from `SPIDER_NAME`:
- `OUTPUT_FILE = f"{SPIDER_NAME}.jsonl"` — scraped data
- `f"{SPIDER_NAME}.log"` — plain-text log file

---

## Dependencies

Tell the user to install before running:

```bash
pip install scrapy scrapy-zyte-api rich
```

`AsyncCrawlerProcess` requires Scrapy 2.11+.

And set their API key:
```bash
export ZYTE_API_KEY=your_key_here
```

---

## Saving the output

Save the spider to the user's working directory named after the spider
(e.g. `example_com.py`). Use `present_files` to hand it to the user.

Always show a brief "how to run" block after saving:

```
python example_com.py
# data  → example_com.jsonl
# logs  → example_com.log
```
