# Check retailer

Use this workflow for one retailer at a time, from RETAILER_FEASIBILITY.md and Task 5 in TASKS.md.

## Steps

1. Read RETAILER_FEASIBILITY.md, config/retailers.yaml, and .clinerules/02-scraping-rules.md.
2. Open the retailer `/robots.txt` and record whether product pages are off limits.
3. Search the retailer terms of service for automated, scraping, and robots, and record any ban.
4. Run one plain request to one exact product page from config/products.yaml, and record whether it returns the price, or a block or CAPTCHA.
5. Record where the price lives: in the page HTML, in embedded structured data, or loaded afterward by script.
6. Record request volume for the hand picked list at the interval in config/settings.yaml.
7. Fill in that retailer row in RETAILER_FEASIBILITY.md, with the date and the exact page checked. If it fails, set enabled to false in config/retailers.yaml, with a note and a date.

## Hard stops

- Do not work around a block, a CAPTCHA, or a robots.txt limit.
- Do not invent a result. If you could not open a page, write to check, with what you tried.
- Do not add a headless browser, a proxy, or a paid feed without a new decision.
