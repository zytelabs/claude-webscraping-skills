---
name: parser
description: Extracts structured product data from raw HTML. Tries JSON-LD via Extruct first, falls back to CSS selectors via Parsel.
---

# Parser

Extract structured product data from raw HTML. Tries JSON-LD first via Extruct, falls back to CSS selectors via Parsel.

## When to use
Use this skill when you have raw HTML and need to extract structured data from it — product details, prices, specs, ratings, or any page content.

## Instructions
1. Save the HTML to a temporary file `page.html`
2. Run `parser.py` against it:
   ```
   python parser.py page.html
   ```
3. The script outputs a JSON object. Check the `method` field:
   - `"extruct"` — clean structured data was found, use it directly
   - `"parsel"` — fell back to CSS selectors, review fields for completeness
4. If key fields are missing from the Parsel output, ask the user which fields they need and re-run with `--fields`:
   ```
   python parser.py page.html --fields "price,rating,brand"
   ```
5. Return the parsed JSON to the conversation for use in the Compare skill.

## Notes
- Always prefer the Extruct path — it is more stable and requires no maintenance
- Parsel selectors are generated heuristically and may need adjustment for unusual page layouts
- Run once per page; pass all outputs together into the Compare skill
