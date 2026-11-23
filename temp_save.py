import sqlite3
conn = sqlite3.connect("data/price-tracker.db")
rows = conn.execute("SELECT category, period, index_value, skus_used FROM index_values ORDER BY category, period").fetchall()
print("OLD INDEX_VALUES:")
for row in rows:
    print(row)
conn.close()