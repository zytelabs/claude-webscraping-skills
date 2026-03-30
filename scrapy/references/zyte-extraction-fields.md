# Zyte API Extraction Fields Reference

## productList

Request: `{"url": "...", "productList": true}`

Response: `response.raw_api_response["productList"]`

### Key fields

| Field | Type | Description |
|-------|------|-------------|
| `products` | array | List of product stubs found on the page |
| `products[].url` | string | URL of the product detail page |
| `products[].name` | string | Product name (may be partial) |
| `products[].price` | string | Price string if visible on listing |
| `products[].currency` | string | Currency code |
| `products[].regularPrice` | string | Pre-sale price if shown |
| `nextPage` | object | Pagination info |
| `nextPage.url` | string | URL of the next listing page (null if last page) |
| `pageNumber` | integer | Current page number |
| `url` | string | Canonical URL of this listing page |

### Usage notes

- `products[].url` is the primary thing you need — it's what you pass to
  the `product` extraction step
- Always check `nextPage.url` — if not null, yield another `productList`
  request to continue paginating
- Product data in the listing is partial/preview only — always fetch the
  full `product` for complete data

---

## product

Request: `{"url": "...", "product": true}`

Response: `response.raw_api_response["product"]`

### Key fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Full product name |
| `price` | string | Current price (numeric string, e.g. "29.99") |
| `currency` | string | ISO currency code (e.g. "GBP", "USD") |
| `currencyRaw` | string | Raw currency symbol as seen on page (e.g. "£") |
| `regularPrice` | string | Original price before discount |
| `availability` | string | "InStock", "OutOfStock", or null |
| `brand` | object | `{name: "..."}` |
| `description` | string | Full product description text |
| `descriptionHtml` | string | Description as HTML |
| `sku` | string | SKU / product code |
| `gtin` | array | GTINs (EAN, UPC, ISBN, etc.) |
| `images` | array | `[{url: "..."}]` — product images |
| `breadcrumbs` | array | `[{name: "...", url: "..."}]` |
| `additionalProperties` | array | `[{name: "...", value: "..."}]` — specs/attributes |
| `variants` | array | Product variants (size, colour, etc.) |
| `url` | string | Canonical product URL |
| `metadata` | object | Confidence scores and extraction metadata |

### Yielding the product

You can yield the full product dict directly:

```python
def parse_product(self, response):
    product = response.raw_api_response["product"]
    yield product
```

Or pick specific fields if you want a leaner output:

```python
def parse_product(self, response):
    p = response.raw_api_response["product"]
    yield {
        "name": p.get("name"),
        "price": p.get("price"),
        "currency": p.get("currency"),
        "availability": p.get("availability"),
        "url": p.get("url"),
        "sku": p.get("sku"),
        "brand": p.get("brand", {}).get("name"),
        "description": p.get("description"),
    }
```

---

## productNavigation

Request: `{"url": "...", "productNavigation": true}`

Response: `response.raw_api_response["productNavigation"]`

This is the **default extraction type for category pages** in this skill.
Use it for the initial request and for pagination.

### Key fields

| Field | Type | Description |
|-------|------|-------------|
| `items` | array | Product links found on the page |
| `items[].url` | string | URL of the product detail page |
| `nextPage` | object | Pagination info |
| `nextPage.url` | string | URL of the next page (null if last) |
| `subCategories` | array | Subcategory links (not followed by default) |
| `url` | string | Canonical URL of this page |

### Usage notes

- Use `items[].url` to queue product detail requests
- Always check `nextPage.url` for pagination — follow it with another `productNavigation` request
- `subCategories` are ignored by default; only follow them if the user explicitly wants deep category crawling

---

## extractFrom

To extract from the raw HTTP response body rather than a browser-rendered page,
add these fields to the request meta alongside the extraction type:

```python
"httpResponseBody": True,
"productNavigationOptions": {"extractFrom": "httpResponseBody"},  # for navigation
"productOptions": {"extractFrom": "httpResponseBody"},            # for products
```

Do **not** pass `extractFrom` as a nested dict inside the extraction type field itself
(e.g. `"productNavigation": {"extractFrom": ...}`) — this is invalid and returns a 400.
