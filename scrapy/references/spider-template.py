"""
Spider template for scrapy-quick-spider skill.

Substitute:
  - SPIDER_NAME     → derived from domain (e.g. "example_com")
  - START_URL       → user's category/listing URL
  - OUTPUT_FORMAT   → "jsonl" (default) or "json" / "csv"
"""

import logging
import os

from rich.logging import RichHandler
from scrapy import Request, Spider
from scrapy.crawler import AsyncCrawlerProcess

SPIDER_NAME = "example_com"
START_URL = "https://example.com/category/all"
OUTPUT_FILE = f"{SPIDER_NAME}.jsonl"
OUTPUT_FORMAT = "jsonl"

_file_handler = logging.FileHandler(f"{SPIDER_NAME}.log")
_file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True, markup=True), _file_handler],
)
logger = logging.getLogger(__name__)


class ProductSpider(Spider):
    name = SPIDER_NAME

    async def start(self):
        logger.info("[blue]Navigating[/] | url=[yellow]%s[/]", START_URL)
        yield Request(
            START_URL,
            meta={"zyte_api_automap": {
                "httpResponseBody": True,
                "productNavigation": True,
                "productNavigationOptions": {"extractFrom": "httpResponseBody"},
            }},
            callback=self.parse_navigation,
            errback=self.handle_error,
        )

    async def parse_navigation(self, response):
        data = response.raw_api_response.get("productNavigation", {})

        for item in data.get("items", []):
            url = item.get("url")
            if url:
                logger.info("[blue]Requesting product[/] | url=[yellow]%s[/]", url)
                yield response.follow(
                    url,
                    meta={"zyte_api_automap": {
                        "httpResponseBody": True,
                        "product": True,
                        "productOptions": {"extractFrom": "httpResponseBody"},
                    }},
                    callback=self.parse_product,
                    errback=self.handle_error,
                )

        next_page = data.get("nextPage", {})
        if next_page:
            next_url = next_page.get("url")
            if next_url:
                logger.info("[blue]Navigating[/] | url=[yellow]%s[/]", next_url)
                yield response.follow(
                    next_url,
                    meta={"zyte_api_automap": {
                        "httpResponseBody": True,
                        "productNavigation": True,
                        "productNavigationOptions": {"extractFrom": "httpResponseBody"},
                    }},
                    callback=self.parse_navigation,
                    errback=self.handle_error,
                )

    async def parse_product(self, response):
        product = response.raw_api_response.get("product", {})
        name = product.get("name")
        sku = product.get("sku")
        logger.info("[green]Scraped product[/] | name=[bold]%s[/] | sku=[cyan]%s[/]", name, sku)
        yield {
            "name": name,
            "price": product.get("price"),
            "currency": product.get("currency"),
            "regularPrice": product.get("regularPrice"),
            "availability": product.get("availability"),
            "brand": (product.get("brand") or {}).get("name"),
            "sku": sku,
            "description": product.get("description"),
            "images": [img.get("url") for img in product.get("images", [])],
            "additionalProperties": product.get("additionalProperties"),
            "url": product.get("url") or response.url,
        }

    def handle_error(self, failure):
        logger.error("[red]Request failed[/] | url=[yellow]%s[/] | error=%s", failure.request.url, failure.value)


if __name__ == "__main__":
    process = AsyncCrawlerProcess(
        settings={
            "ADDONS": {
                "scrapy_zyte_api.Addon": 500,
            },
            "ZYTE_API_KEY": os.environ.get("ZYTE_API_KEY"),
            "ZYTE_API_TRANSPARENT_MODE": True,
            "FEEDS": {
                OUTPUT_FILE: {"format": OUTPUT_FORMAT},
            },
            "LOG_ENABLED": False,
            "ROBOTSTXT_OBEY": False,
            "CONCURRENT_REQUESTS": 32,
        }
    )
    # Re-silence after AsyncCrawlerProcess reconfigures logging on init
    for noisy in ("scrapy", "twisted", "filelock", "hpack", "zyte_api", "scrapy_zyte_api"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
    process.crawl(ProductSpider)
    process.start()
