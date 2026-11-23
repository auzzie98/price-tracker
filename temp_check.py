import sqlite3
conn = sqlite3.connect("data/price-tracker.db")
print("skus:")
for row in conn.execute("SELECT * FROM skus"):
    print(row)
print("\nobservations:")
for row in conn.execute("SELECT * FROM observations"):
    print(row)
print("\nsku_prices:")
for row in conn.execute("SELECT * FROM sku_prices"):
    print(row)
print("\nindex_values:")
for row in conn.execute("SELECT * FROM index_values"):
    print(row)
conn.close()