import sqlite3
conn = sqlite3.connect("data/price-tracker.db")
conn.execute("INSERT OR REPLACE INTO skus (id, mpn, brand, model, category, chip, architecture) VALUES (?, ?, ?, ?, ?, ?, ?)", ("asus-dual-rtx5070-12g", "DUAL-RTX5070-12G", "ASUS", "Dual RTX 5070 12GB", "GPUs", "RTX 5070", "Blackwell"))
conn.execute("INSERT OR REPLACE INTO skus (id, mpn, brand, model, category, chip, architecture) VALUES (?, ?, ?, ?, ?, ?, ?)", ("corsair-vengeance-32gb-ddr5-6000-cl30", "CMK32GX5M2B6000Z30", "CORSAIR", "Vengeance 32GB", "RAM", "DDR5-6000 CL30", "DDR5"))
conn.commit()
print("Added GPU and RAM SKUs")
conn.close()