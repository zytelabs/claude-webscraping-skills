import requests
import sys

def fetch_product_data(url: str, api_key: str) -> None:
    api_response = requests.post(
        "https://api.zyte.com/v1/extract",
        auth=(api_key, ""),
        json={
            "url": url,
            "browserHtml": True,
            "product": True,
            "productOptions": {"extractFrom": "browserHtml"},
        },
    )
    
    browser_html: str = api_response.json()["browserHtml"]
    with open("browser_html.html", "w", encoding="utf-8") as fp:
        fp.write(browser_html)
    
    product = api_response.json()["product"]
    print(product)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python fetch_price.py <api_key> <product_url>")
        sys.exit(1)
    
    api_key = sys.argv[1]
    product_url = sys.argv[2]
    fetch_product_data(product_url, api_key)
