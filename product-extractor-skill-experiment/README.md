# Product Extractor Skill

An experimental skill to explore how to use Zyte API with Claude Skills. This skill extracts structured product data (price, currency, availability) from e-commerce URLs using Zyte AI.

## Overview

The Product Extractor skill is designed to fetch and extract product information from e-commerce websites. It uses the Zyte API to scrape product data including prices, currency, availability, and other product details from any product URL.

## Features

- 🛍️ Extract product data from e-commerce URLs
- 💰 Retrieve price and currency information
- 📦 Check product availability/stock status
- 🔍 Get product descriptions and details
- 🌐 Uses browser rendering for JavaScript-heavy sites
- 📄 Saves browser HTML as fallback for manual inspection

## Prerequisites

- Python 3.x
- Zyte API Key ([Get one here](https://www.zyte.com/))
- `requests` library

## Installation

1. Clone this repository:
```bash
git clone https://github.com/NehaSetia-DA/product-extractor-skill-experiment.git
cd product-extractor-skill-experiment
```

2. Install required dependencies:
```bash
pip install requests
```

3. Set your Zyte API key as an environment variable:
```bash
export ZYTE_API_KEY="your-api-key-here"
```

Or on Windows:
```bash
set ZYTE_API_KEY=your-api-key-here
```

## Usage

### Command Line

Run the script with your Zyte API key and product URL:

```bash
python scripts/fetch_product.py $ZYTE_API_KEY "https://example.com/product"
```

Or with the API key directly:
```bash
python scripts/fetch_product.py "your-api-key" "https://example.com/product"
```

### Output

The script will:
1. Print a JSON object containing the extracted product details to stdout
2. Save `browser_html.html` file containing the rendered HTML for fallback reference

### Example

```bash
python scripts/fetch_product.py $ZYTE_API_KEY "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
```

## Project Structure

```
product-extractor-skill-experiment/
├── README.md                 # This file
├── SKILL.md                  # Skill documentation for Claude
├── scripts/
│   └── fetch_product.py       # Main script for fetching product data
└── .gitattributes           # Git attributes configuration
```

## Using with Claude

This skill is designed to work with Claude Skills. Follow these steps to use it with Claude:

### Prerequisites

- Claude account ( Pro, Max, Team, or Enterprise plan)
- Code execution enabled in Claude settings
- Zyte API key (set as `ZYTE_API_KEY` environment variable)

### Step 1: Package the Skill

1. Ensure your folder structure matches the project structure shown above
2. Create a ZIP file of the entire folder
3. **Important:** The ZIP should contain the skill folder as its root (not files directly in the ZIP root)

**Correct structure:**
```
product-extractor-skill.zip
 └── product-extractor-skill/
     ├── SKILL.md
     └── scripts/
         └── fetch_product.py
```

**Incorrect structure:**
```
product-extractor-skill.zip
 ├── SKILL.md
 └── scripts/
     └── fetch_product.py
```

### Step 2: Upload to Claude

1. Open Claude and go to **Settings > Capabilities**
2. Navigate to the Skills section
3. Click **Add Skill** or **Upload Skill**
4. Select your ZIP file (`product-extractor-skill.zip`)
5. Claude will validate and load your skill

### Step 3: Enable the Skill

1. After uploading, ensure the skill is enabled in **Settings > Capabilities**
2. The skill will appear in your list of available skills

### Step 4: Use the Skill

Simply ask Claude questions that should trigger the skill. For example:

- "What's the price of this product: https://example.com/product"
- "Can you check the availability and price for this URL: https://example.com/product"
- "Get me the product details from this link: https://example.com/product"

Claude will automatically:
1. **Detect** when you provide a product URL and ask for details
2. **Execute** the Python script with your Zyte API key and the product URL
3. **Process** the JSON output and present it in a clean, readable format
4. **Fall back** to reading `browser_html.html` if the JSON is incomplete

### Testing Your Skill

After uploading:
1. Try several different prompts that should trigger the skill
2. Review Claude's thinking to confirm it's loading the skill
3. If Claude isn't using it when expected, iterate on the description in `SKILL.md`

For more details on skill creation, see the [official Claude Skills documentation](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills).

## Requirements

- Python 3.x
- `requests` library (`pip install requests`) - Claude will install this automatically
- Valid Zyte API key set in `ZYTE_API_KEY` environment variable

## Error Handling

The script includes basic error handling:
- Validates that both API key and URL are provided
- Exits with an error message if arguments are missing

## Contributing

This is an experimental project. Feel free to submit issues or pull requests!

## License

This project is experimental and provided as-is.

## Resources

- [Zyte API Documentation](https://docs.zyte.com/)
- [Zyte Website](https://www.zyte.com/)
