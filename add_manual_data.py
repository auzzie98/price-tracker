import sqlite3

conn = sqlite3.connect("data/price-tracker.db")

# Add SKU
conn.execute(
    "INSERT OR IGNORE INTO skus (id, mpn, brand, model, category, chip, architecture) "
    "VALUES ('amd-ryzen-7-9800x3d', '100-100001084WOF', 'AMD', 'Ryzen 7 9800X3D', 'CPUs', 'Ryzen 7 9800X3D', 'Zen 5')"
)

# Add retailers
conn.execute(
    "INSERT OR IGNORE INTO retailers (id, name, base_url, enabled) "
    "VALUES ('bestbuy', 'Best Buy', 'https://www.bestbuy.com', 1)"
)
conn.execute(
    "INSERT OR IGNORE INTO retailers (id, name, base_url, enabled) "
    "VALUES ('bh', 'B and H', 'https://www.bhphotovideo.com', 1)"
)
conn.execute(
    "INSERT OR IGNORE INTO retailers (id, name, base_url, enabled) "
    "VALUES ('newegg', 'Newegg', 'https://www.newegg.com', 1)"
)

# Add sku_retailer_urls
conn.execute(
    "INSERT OR IGNORE INTO sku_retailer_urls (sku_id, retailer_id, url, active) "
    "VALUES ('amd-ryzen-7-9800x3d', 'bestbuy', "
    " 'https://www.bestbuy.com/product/amd-ryzen-7-9800x3d-8-core-16-thread-4-7-ghz-5-2-ghz-max-boost-socket-am5-pci-express-5-0-unlocked-desktop-processor-silver/JXKQHH5XSR', 1)"
)
conn.execute(
    "INSERT OR IGNORE INTO sku_retailer_urls (sku_id, retailer_id, url, active) "
    "VALUES ('amd-ryzen-7-9800x3d', 'bh', "
    " 'https://www.bhphotovideo.com/c/product/1859346-REG/amd_100_100001084wof_ryzen_7_9800x3d_am5.html', 1)"
)
conn.execute(
    "INSERT OR IGNORE INTO sku_retailer_urls (sku_id, retailer_id, url, active) "
    "VALUES ('amd-ryzen-7-9800x3d', 'newegg', "
    " 'https://www.newegg.com/amd-ryzen-7-9000-series-ryzen-7-9800x3d-granite-ridge-zen-5-socket-am5-desktop-cpu-processor/p/N82E16819113877T', 1)"
)

conn.commit()

# Add 3 manual observations
conn.execute(
    "INSERT INTO observations (observed_at, sku_id, retailer_id, price_cents, in_stock, source_url) "
    "VALUES ('2026-11-22T00:00:00', 'amd-ryzen-7-9800x3d', 'bestbuy', 47900, 1, "
    " 'https://www.bestbuy.com/product/amd-ryzen-7-9800x3d-8-core-16-thread-4-7-ghz-5-2-ghz-max-boost-socket-am5-pci-express-5-0-unlocked-desktop-processor-silver/JXKQHH5XSR')"
)
conn.execute(
    "INSERT INTO observations (observed_at, sku_id, retailer_id, price_cents, in_stock, source_url) "
    "VALUES ('2026-11-22T00:00:00', 'amd-ryzen-7-9800x3d', 'bh', 41900, 1, "
    " 'https://www.bhphotovideo.com/c/product/1859346-REG/amd_100_100001084wof_ryzen_7_9800x3d_am5.html')"
)
conn.execute(
    "INSERT INTO observations (observed_at, sku_id, retailer_id, price_cents, in_stock, source_url) "
    "VALUES ('2026-11-22T00:00:00', 'amd-ryzen-7-9800x3d', 'newegg', 46999, 1, "
    " 'https://www.newegg.com/amd-ryzen-7-9000-series-ryzen-7-9800x3d-granite-ridge-zen-5-socket-am5-desktop-cpu-processor/p/N82E16819113877T')"
)

conn.commit()

# Verify
rows = conn.execute("SELECT COUNT(*) FROM observations").fetchone()[0]
print(f"Observations inserted: {rows}")

# Show observations for this SKU
print("Observations for amd-ryzen-7-9800x3d:")
for row in conn.execute(
    "SELECT retailer_id, price_cents, in_stock, source_url FROM observations WHERE sku_id = 'amd-ryzen-7-9800x3d'"
).fetchall():
    print(f"  retailer: {row[0]}, price_cents: {row[1]}, in_stock: {row[2]}")

conn.close()