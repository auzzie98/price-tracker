import sqlite3
conn = sqlite3.connect("data/price-tracker.db")
conn.execute("UPDATE sku_prices SET median_price_cents = 57999 WHERE sku_id = \"asus-dual-rtx5070-12g\"")
conn.commit()
print("Updated GPU price to 57999")
conn.close()