import sqlite3
import random
from datetime import datetime, timedelta

random.seed(42)  # reproducible

conn = sqlite3.connect("data/price-tracker.db")

# SKU IDs
skus = [
    "amd-ryzen-7-9800x3d",
    "asus-dual-rtx5070-12g", 
    "corsair-vengeance-32gb-ddr5-6000-cl30"
]

# Current medians in cents
current_medians = {
    "amd-ryzen-7-9800x3d": 46999,
    "asus-dual-rtx5070-12g": 57999,
    "corsair-vengeance-32gb-ddr5-6000-cl30": 23999
}

# Current date
base_date = datetime(2026, 11, 22)

# Generate 30 days of mock data (from day -29 to day 0)
# Prices should trend toward the current medians
for sku in skus:
    median = current_medians[sku]
    # Start 30 days ago with some variance, end at the median
    for day in range(30):
        date = (base_date - timedelta(days=29-day)).strftime("%Y-%m-%d")
        # Small random walk that ends near the median
        # Use a weighted approach: earlier days have more variance, later days trend to median
        variance = 30 - day  # more variance earlier
        change = random.randint(-50, 50) * (variance / 30)  # decreasing change
        # Start further away and converge to median
        start_price = median + random.randint(-100, 100)
        price = start_price + change
        # Ensure price is positive and within reasonable range
        price = max(10000, min(price, median + 200))  # cap at 200 above median
        
        # Check if this observation already exists
        existing = conn.execute(
            "SELECT COUNT(*) FROM observations WHERE sku_id = ? AND observed_at = ? AND retailer_id = 'bh'",
            (sku, date)
        ).fetchone()[0]
        
        if existing == 0:
            conn.execute(
                "INSERT INTO observations (observed_at, sku_id, retailer_id, price_cents, in_stock, source_url) VALUES (?, ?, ?, ?, 1, ?)",
                (date, sku, "bh", price, f"https://example.com/mock/{sku}-{date}")
            )
    
    # Also add the current day's observation if not exists
    existing = conn.execute(
        "SELECT COUNT(*) FROM observations WHERE sku_id = ? AND observed_at = '2026-11-22' AND retailer_id = 'bh'",
        (sku,)
    ).fetchone()[0]
    
    if existing == 0:
        conn.execute(
            "INSERT INTO observations (observed_at, sku_id, retailer_id, price_cents, in_stock, source_url) VALUES (?, ?, ?, ?, 1, ?)",
            ("2026-11-22", sku, "bh", median, f"https://example.com/mock/{sku}-2026-11-22")
        )

conn.commit()
print("Mock historical observations generated")
conn.close()