# I Screenshotted a Dress and Claude Built Me a Mood Board: Chaining Skills for Product Discovery at Any Scale

I like to follow fashion. I also happen to be a developer advocate at a web scraping company. These two things don't overlap as often as you'd think, but this week they did.

Here's what happened: I was scrolling through my feed and came across a stunning blush pink strapless gown with cascading fringe detail. The kind of dress you screenshot immediately and send to your best friend with no context, just the image. We've all been there.

Normally that's where the story ends. You screenshot, you send, you move on. Maybe you open Google Lens, click through ten results, lose half of them in different tabs, give up, and go back to scrolling.

I tried doing this manually before building the skill. The process looked like this: open Google, type a vague description of the dress, scroll past ads, open six tabs, wait for each site to load, realize three of them don't ship to my country, forget which tab had the one I liked, lose one tab completely because I accidentally closed it, and end up with nothing. Thirty minutes, zero results I could compare side by side.

Then I tried the developer version: write a Python script to search Google, parse the results, hit each URL, extract the product data. That works, technically. But every time I wanted to search for a different dress, I was back in the terminal editing query strings, re-running scripts, debugging why one site returned empty HTML (it was blocking my request), and manually stitching results together. The code worked. The workflow didn't.

What I actually wanted was to drop a screenshot and get a mood board. No tabs. No terminal. No debugging. Just the answer.

So I built a Claude Skill that does exactly that.

## What the skill does

I drop an image into Claude. Claude looks at the dress, describes it as a short search query ("pink fringe strapless gown"), searches for similar products across the web, extracts structured product data from each result (name, price, image, brand, availability), and generates an HTML mood board I can open in my browser. Product cards with images, prices, and direct buy links. Sorted by price. Ready to shop.

The whole thing runs inside a single conversation. The same task that took me thirty minutes manually and still failed, or ten minutes of scripting that I'd have to redo for every new dress, now takes about two minutes. And I don't leave the chat window.

## How it works under the hood

The mood board is actually three Claude Skills chained together. Each skill does one thing, and the mood-board skill orchestrates the full pipeline.

| Skill | What it does | Key script |
|-------|-------------|------------|
| **serp-search** | Finds product URLs via Zyte SERP extraction | `serp_search.py` |
| **product-extractor** | Extracts structured product data via Zyte API | `fetch_price.py` |
| **mood-board** | Orchestrator: chains the above two skills, filters URLs, generates HTML mood board | `generate_moodboard.py` |

The orchestrator's SKILL.md tells Claude exactly how to chain them:

**Step 1: Describe the image.** Claude looks at the screenshot and turns it into a 4-5 word shopping query. This is the most important step. "Blush pink strapless fringe tassel floor length evening gown" returns mostly category pages. "Pink fringe strapless gown" returns actual products. I learned this through testing: shorter, more specific queries with shopping intent outperform long descriptive ones.

**Step 2: Find similar products.** The query goes to the **serp-search** skill, which calls Zyte API's SERP extraction endpoint. It fetches Google search results and returns structured JSON: URLs, titles, descriptions, ranks. No proxies to configure, no CAPTCHA solving, no anti-ban logic to write. Zyte handles all of that behind a single API call. The skill runs two slightly different queries and merges results for broader coverage, deduplicating by URL.

**Step 3: Filter and extract.** Not every URL from a search result is a product page. A department store's category listing, a marketplace's search results page, a brand's filtered browse page: these don't have a single product to extract. The skill filters those out using URL patterns (/collections/, /browse/, /s?k=) and keeps only pages that look like individual products. Then it passes each URL to the **product-extractor** skill, which calls Zyte API's product extraction endpoint. Back comes structured JSON: product name, price, currency, main image, brand, availability.

**Step 4: Build the mood board.** The extracted data feeds into `generate_moodboard.py`. Product cards in a grid, sorted by price, each with an image, the product name, the price, and a "Shop Now" link. It looks like something you'd share with a friend, not a data dump.

The key design decision: each skill is independently useful. The serp-search skill works on its own when you just need search results. The product-extractor works on its own when you have a URL and want structured data. The mood-board skill composes them into a workflow. This is what makes Claude Skills powerful: you build small, focused tools, and Claude figures out how to chain them based on what the SKILL.md instructions say.

## What surprised me

I tested the skill with my screenshot of the pink fringe gown. The first search returned products from a mix of independent boutiques, designer brands, and handmade marketplaces. Prices ranged from $79 to $749. Seven products, all with images and working buy links.

Three things stood out.

**One query isn't enough.** "Pink fringe strapless gown" returned a mix of product pages and category pages. I needed a second, slightly different query ("pink fringe strapless evening dress buy") to fill the board with enough actual products. The skill now runs two query variations and merges the results.

**Fashion sites are hard to scrape.** This is the part that connects to my day job. The sites that sell the kinds of dresses you'd actually want to buy are the same sites that actively fight automated access. Dynamic pricing that changes by session. Rotating page layouts designed to break selectors. JavaScript-heavy SPAs that serve empty HTML to anything that isn't a full browser. Sophisticated anti-ban systems that fingerprint your requests and block anything that looks automated. I didn't have to think about any of that because Zyte API's anti-ban management, browser rendering, and proxy rotation handled it behind a single POST request. But I noticed it: sites that would return empty responses or garbage HTML to a regular `requests.get()` came back with clean, structured product data through Zyte.

**The AI description is the linchpin.** The quality of the mood board depends entirely on how well the AI describes the image. "Pink dress" gives you garbage. "Pink fringe strapless gown" gives you exactly what you want. The prompt engineering for the description step matters more than any other part of the pipeline.

## From mood board to market intelligence

Here's where the fun project connects to something bigger.

The fashion e-commerce industry runs on competitive pricing intelligence. Brands need to know what their competitors are charging, whether their products are being resold by unauthorized sellers, whether MAP (minimum advertised price) policies are being violated, and how pricing shifts across markets and seasons. The sites they need to monitor are some of the hardest to extract data from on the entire web: heavy JavaScript rendering, aggressive anti-ban measures, session-based dynamic pricing, and layouts that change per visitor.

My mood board skill and a production fashion price monitoring system use the same architecture. The same pattern of chaining Claude Skills scales from a personal project to an enterprise pipeline:

**Discovery.** My skill starts with an image and finds similar products. A price monitoring system starts with a product catalog and finds where those products are listed across the web. Both use search and discovery to identify target URLs. At scale, this becomes a recurring crawl: discover new listings, track existing ones, flag delisted products.

**Extraction.** My skill extracts one product per page. A monitoring system extracts the same fields (price, availability, name, image) from hundreds of thousands of pages. The Zyte API call is identical. The difference is volume and frequency. What my skill does interactively, a production system does on a scheduled Scrapy spider running on Scrapy Cloud, with Zyte API handling the anti-ban layer underneath.

**Comparison.** My skill puts everything in a mood board for visual comparison. A monitoring system puts everything in a database for trend analysis, price change detection, MAP violation alerts, and automated reporting.

**Infrastructure.** This is the part that doesn't change. Whether you're extracting one dress or a million products, the anti-ban challenge is the same. The sites rotate layouts, fingerprint browsers, throttle requests, and block scrapers. Zyte API handles browser rendering, proxy rotation, and ban management at both scales. The skill user and the enterprise customer are calling the same endpoint.

The pattern of chaining composable skills is also the same. At production scale, the serp-search skill becomes a discovery spider. The product-extractor skill becomes an extraction pipeline. The mood-board orchestrator becomes a scheduling and alerting system. Each component is independently testable, independently deployable, and independently scalable. That's the power of building with composable pieces rather than a monolithic script.

The difference between my Saturday afternoon project and a production deployment is scheduling, scale, and what you do with the output. The data pipeline underneath is the same.

## Try it yourself

The mood board skill is available in the [Zyte Claude Skills repository](https://github.com/zytelabs/claude-webscraping-skills). You'll need a Zyte API key (there's a [free tier](https://www.zyte.com/zyte-api/)) and Claude with skills enabled.

Drop an image of any product into the conversation. Doesn't have to be fashion. Sneakers, furniture, electronics, skincare. The skill doesn't care what kind of product it is. Zyte API's extraction works across categories.

If you build something with it, or adapt it for a different use case, I'd love to see it. Find me in the [Extract Data community on Discord](https://discord.gg/extractdata).

And if you're working in fashion e-commerce and the scale problem resonates, [Zyte's data delivery team](https://www.zyte.com/) handles exactly this: production-grade product extraction from the sites that fight back hardest.

---

*Neha Setia is a Senior Developer Advocate at Zyte.*
