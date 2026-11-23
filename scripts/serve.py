from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from fastapi import FastAPI
from fastapi.responses import FileResponse

app = FastAPI()

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.get("/api/indexes")
def api_indexes():
    from price_tracker.db import connect
    import sqlite3
    db_path = "data/price-tracker.db"
    conn = sqlite3.connect(db_path)
    rows = conn.execute("SELECT category, period, index_value, skus_used FROM index_values").fetchall()
    conn.close()
    result = {"categories": []}
    for category in ["CPUs", "GPUs", "RAM"]:
        category_rows = [r for r in rows if r[0] == category]
        if category_rows:
            result["categories"].append({"category": category, "index_value": category_rows[0][2], "skus_used": category_rows[0][3]})
        else:
            result["categories"].append({"category": category, "index_value": 100.0, "skus_used": 0})
    return result

@app.get("/api/indexes/{category}")
def api_indexes_category(category: str):
    from price_tracker.db import connect
    import sqlite3
    db_path = "data/price-tracker.db"
    conn = sqlite3.connect(db_path)
    rows = conn.execute("SELECT period, index_value, skus_used FROM index_values WHERE category = ? ORDER BY period", (category,)).fetchall()
    conn.close()
    if not rows:
        return {"category": category, "index_value": 100.0, "skus_used": 0, "period_values": []}
    result = []
    for period, index_value, skus_used in rows:
        result.append({"period": period, "index_value": index_value, "skus_used": skus_used})
    return {"category": category, "index_values": result, "count": len(result)}

@app.get("/api/products")
def api_products():
    from price_tracker.db import connect
    import sqlite3
    db_path = "data/price-tracker.db"
    conn = sqlite3.connect(db_path)
    rows = conn.execute("SELECT id, median_price_cents, retailers_used FROM sku_prices").fetchall()
    conn.close()
    products = []
    for sku_id, median_price_cents, retailers_used in rows:
        products.append({"sku_id": sku_id, "price_dollars": median_price_cents / 100, "retailers_used": retailers_used})
    return {"products": products}

@app.get("/api/products/{sku}")
def api_product(sku: str):
    from price_tracker.db import connect
    import sqlite3
    db_path = "data/price-tracker.db"
    conn = sqlite3.connect(db_path)
    rows = conn.execute("SELECT period, median_price_cents FROM sku_prices WHERE sku_id = ? ORDER BY period", (sku,)).fetchall()
    conn.close()
    price_points = []
    for period, median_price_cents in rows:
        price_points.append({"period": period, "price_cents": median_price_cents, "price_dollars": median_price_cents / 100})
    return {"sku": sku, "price_points": price_points, "count": len(price_points)}

@app.get("/api/movers")
def api_movers():
    from price_tracker.db import connect
    import sqlite3
    db_path = "data/price-tracker.db"
    conn = sqlite3.connect(db_path)
    rows = conn.execute("SELECT sku_id, period, median_price_cents FROM sku_prices ORDER BY period DESC LIMIT 10").fetchall()
    conn.close()
    movers = []
    for sku_id, period, median_price_cents in rows:
        movers.append({"sku_id": sku_id, "period": period, "price_cents": median_price_cents, "price_dollars": median_price_cents / 100})
    return {"movers": movers}

@app.get("/", include_in_schema=False)
def index_page():
    return FileResponse("web/index.html")

@app.get("/index.html", include_in_schema=False)
def index_html():
    return FileResponse("web/index.html")

@app.get("/category", include_in_schema=False)
def category_page():
    return FileResponse("web/category.html")

@app.get("/product/{sku}", include_in_schema=False)
def product_page(sku: str):
    return FileResponse("web/product.html")

@app.get("/static/{path:path}", include_in_schema=False)
def static_files(path: str):
    return FileResponse("web/static/" + path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
