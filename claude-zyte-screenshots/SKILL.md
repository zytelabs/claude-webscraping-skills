---
name: zyte-screenshots
description: >
  Capture a full-page screenshot of any public URL using the Zyte API. Use this skill whenever
  the user provides a URL and asks to take a screenshot, capture a page, grab a visual snapshot,
  or see what a website looks like. Also trigger when the user says things like "screenshot this",
  "capture this page", "show me what this site looks like", or "get a screenshot of [URL]".
  Requires ZYTE_API_KEY in the environment. After capturing, the skill saves the screenshot as a
  PNG file named after the website, reports the file location, and gives a 1-line description of
  what's visible in the screenshot.
---

# Zyte Screenshots Skill

Capture full-page screenshots of any public URL via the Zyte API using curl, save as a PNG file,
and briefly describe the visual content.

---

## Prerequisites

- `curl` installed (standard on macOS/Linux)
- `jq` installed
- `base64` CLI available
- `ZYTE_API_KEY` set in the environment

---

## Workflow

### Step 1 — Validate inputs

1. Confirm the user has provided a valid URL (must start with `http://` or `https://`).
2. Check for `ZYTE_API_KEY` in the environment:
   ```bash
   echo $ZYTE_API_KEY
   ```
   If empty or unset, stop and tell the user to export it before continuing:
   ```bash
   export ZYTE_API_KEY="your_api_key_here"
   ```

### Step 2 — Derive the output filename

The filename must be the website name with `https://` and `.com` removed. Strip exactly as follows:
- Remove `https://` or `http://`
- Remove `www.` prefix if present
- Remove `.com` (and anything after it)
- Replace any remaining dots or slashes with underscores

Examples:
| URL | Filename |
|-----|----------|
| `https://www.example.com` | `example.png` |
| `https://quotes.toscrape.com` | `quotes.toscrape.png` |
| `https://news.ycombinator.com` | `news.ycombinator.png` |

### Step 3 — Run the curl command

Run this exact command, substituting `$ZYTE_API_KEY`, the target URL, and the derived filename:

```bash
curl -s https://api.zyte.com/v1/extract \
  -u "$ZYTE_API_KEY": \
  -H "Content-Type: application/json" \
  -d '{
    "url": "URL",
    "screenshot": true
  }' \
| jq -r '.screenshot' \
| base64 --decode > FILENAME.png
```

After running, verify the file was created and is non-empty:
```bash
[ -s "FILENAME.png" ] && echo "Success" || echo "Failed"
```

**Common errors:**
| Error | Cause | Fix |
|-------|-------|-----|
| `401 Unauthorized` | Wrong or missing API key | Check `ZYTE_API_KEY` value |
| `jq` outputs `null` | API returned an error | Print raw response to debug |
| Empty file | base64 received no input | Check API response |

To debug, first print the raw API response:
```bash
curl -s https://api.zyte.com/v1/extract \
  -u "$ZYTE_API_KEY": \
  -H "Content-Type: application/json" \
  -d '{"url": "URL", "screenshot": true}'
```

### Step 4 — View and describe the screenshot

After a successful download:

1. Use the `view` tool to open and inspect the PNG file.
2. Tell the user the exact file path so they can open it:
   ```
   📁 Screenshot saved to: /home/claude/FILENAME.png
   ```
3. Write a single sentence describing what is visible in the screenshot (e.g. layout, brand, main content area).

---

## Response format

```
✅ Screenshot captured!

📁 Location: /path/to/FILENAME.png

🖼️  What's in it: [One-sentence visual description]
```
