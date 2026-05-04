"""
Mood Board HTML Generator
Reads product data from stdin (JSON) and generates a styled HTML mood board.

Usage:
    echo '[{"name": "...", "price": "58.0", ...}]' | python generate_moodboard.py "search query"
"""

import json
import re
import sys
from datetime import datetime


def generate(query: str, products: list) -> str:
    """Generate an HTML mood board from product data."""

    # Sort by price
    products.sort(key=lambda p: float(p.get("price", 0)))

    cards = ""
    for p in products:
        name = p.get("name", "Unknown")[:55]
        try:
            price = float(p.get("price", 0))
            price_str = f"${price:.0f}" if price == int(price) else f"${price:.2f}"
        except (ValueError, TypeError):
            price_str = str(p.get("price", ""))

        # Prefer embedded base64 images for offline / sandbox-safe rendering.
        image = p.get("image_base64") or p.get("image", "")
        color = p.get("color", "")
        brand = p.get("brand", "")
        url = p.get("url", "#")

        # Redact retailer names that shouldn't appear in screenshots.
        # (Currently focuses on "Zara" as requested.)
        name_display = re.sub(r"(?i)\bZara\b", "", name).replace("  ", " ").strip()
        if not name_display:
            name_display = name

        # Do not display retailer brand names in the mood board (privacy/screenshot-friendly).
        # Prefer a neutral label derived from color, otherwise fall back to a generic value.
        label = (color if color else "Style")
        cards += f"""
    <div class="card">
      <img class="card-img" src="{image}" alt="{name_display}"
           onerror="this.style.display='none'">
      <div class="card-body">
        <div class="card-label">{label}</div>
        <div class="card-name">{name_display}</div>
        <div class="card-price">{price_str}</div>
      </div>
      <a class="card-link" href="{url}" target="_blank" rel="noopener">Shop Now</a>
    </div>"""

    count = len(products)
    today = datetime.now().strftime("%B %d, %Y")

    if count >= 2:
        low = float(products[0]["price"])
        high = float(products[-1]["price"])
        price_range = f"${low:.0f} – ${high:.0f}"
    else:
        price_range = ""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Mood Board: {query}</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#faf8f5;color:#2d2d2d}}
.hero{{text-align:center;padding:56px 24px 40px;background:linear-gradient(180deg,#f5ede6,#faf8f5)}}
.hero-label{{font-size:11px;letter-spacing:3px;text-transform:uppercase;color:#b8a089;margin-bottom:16px}}
.hero h1{{font-size:36px;font-weight:300;font-style:italic;color:#3d2e1f;margin-bottom:12px}}
.hero-meta{{font-size:13px;color:#999}}
.hero-meta span{{color:#c43b5c;font-weight:500}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:28px;max-width:1200px;margin:0 auto;padding:32px 32px 60px}}
.card{{background:#fff;border-radius:14px;overflow:hidden;box-shadow:0 1px 12px rgba(0,0,0,.04);transition:transform .25s,box-shadow .25s;display:flex;flex-direction:column}}
.card:hover{{transform:translateY(-5px);box-shadow:0 12px 36px rgba(0,0,0,.08)}}
.card-img{{width:100%;height:380px;object-fit:cover;background:#f5f0eb}}
.card-body{{padding:22px;flex:1}}
.card-label{{font-size:10px;color:#b8a089;text-transform:uppercase;letter-spacing:2px;margin-bottom:8px}}
.card-name{{font-size:16px;font-weight:400;line-height:1.3;color:#3d2e1f;margin-bottom:12px}}
.card-price{{font-size:24px;font-weight:600;color:#c43b5c}}
.card-link{{display:block;text-align:center;padding:15px;background:#3d2e1f;color:#f5ede6;text-decoration:none;font-size:11px;letter-spacing:2px;text-transform:uppercase;transition:background .2s}}
.card-link:hover{{background:#c43b5c}}
.footer{{text-align:center;padding:32px 24px 48px;border-top:1px solid #ece6de;font-size:12px;color:#bbb}}
</style>
</head>
<body>
<div class="hero">
<div class="hero-label">Mood Board</div>
<h1>{query}</h1>
<div class="hero-meta"><span>{count}</span> items found{f' &middot; {price_range}' if price_range else ''} &middot; {today}</div>
</div>
<div class="grid">{cards}
</div>
<div class="footer">Powered by Zyte API</div>
</body>
</html>"""

    return html


if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else "Product Search"

    raw = sys.stdin.read().strip()
    try:
        products = json.loads(raw)
    except json.JSONDecodeError:
        print("Error: invalid JSON input", file=sys.stderr)
        sys.exit(1)

    html = generate(query, products)

    with open("moodboard.html", "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Generated moodboard.html with {len(products)} products")
