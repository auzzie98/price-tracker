# Add product

Use this workflow to add one hand picked product at a time. Do not add a batch.

## Steps

1. Read TASKS.md for the current product task, config/products.yaml, and .clinerules/02-scraping-rules.md.
2. Ask Austin for, or confirm with Austin, the manufacturer part number, brand, model, category, chip, and the exact page URL at each retailer that lists it.
3. Add one entry to `config/products.yaml`, with the MPN and the exact URLs. Leave a URL as TO ADD if that retailer does not list it, do not guess a URL.
4. Add the SKU to the database through `scripts/init_db.py` or the product loader, not by hand editing data/.
5. Scrape that product once per enabled retailer, and check that the observations match the MPN, not a similar product.

## Hard stops

- New products only. Retailer sold or retailer fulfilled only. Third party sellers are skipped in v1.
- Do not match by name alone. Match by manufacturer part number.
- Different SKUs are different products: an ASUS card and an MSI card with the same chip, OC and non OC versions, different VRAM sizes, and boxed versus tray CPUs are not the same SKU.
