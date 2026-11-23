from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from fastapi import FastAPI
from fastapi.responses import FileResponse

WEB_ROOT = Path(__file__).resolve().parents[1] / "web"
DB_PATH = Path(__file__).resolve().parents[1] / "data" / "price-tracker.db"


def page_response(relative_path):
    response = FileResponse(WEB_ROOT / relative_path)
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"
    return response

app = FastAPI()

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.get("/api/indexes")
def api_indexes():
    from price_tracker.db import connect
    import sqlite3
    db_path = str(DB_PATH)
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
    db_path = str(DB_PATH)
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
    db_path = str(DB_PATH)
    conn = sqlite3.connect(db_path)
    rows = conn.execute("SELECT sku_id, median_price_cents, retailers_used FROM sku_prices").fetchall()
    conn.close()
    products = []
    for sku_id, median_price_cents, retailers_used in rows:
        products.append({"sku_id": sku_id, "price_dollars": median_price_cents / 100, "retailers_used": retailers_used})
    return {"products": products}

@app.get("/api/products/{sku}")
def api_product(sku: str):
    from price_tracker.db import connect
    import sqlite3
    db_path = str(DB_PATH)
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
    db_path = str(DB_PATH)
    conn = sqlite3.connect(db_path)
    rows = conn.execute("SELECT sku_id, period, median_price_cents FROM sku_prices ORDER BY period DESC LIMIT 10").fetchall()
    conn.close()
    movers = []
    for sku_id, period, median_price_cents in rows:
        movers.append({"sku_id": sku_id, "period": period, "price_cents": median_price_cents, "price_dollars": median_price_cents / 100})
    return {"movers": movers}

@app.get("/", include_in_schema=False)
def index_page():
    return page_response("index.html")

@app.get("/index.html", include_in_schema=False)
def index_html():
    return page_response("index.html")

@app.get("/category", include_in_schema=False)
def category_page():
    return page_response("category.html")

@app.get("/gpus", include_in_schema=False)
def gpus_page():
    return page_response("category.html")

@app.get("/cpus", include_in_schema=False)
def cpus_page():
    return page_response("category.html")

@app.get("/ram", include_in_schema=False)
def ram_page():
    return page_response("category.html")

@app.get("/methodology", include_in_schema=False)
@app.get("/methodology.html", include_in_schema=False)
def methodology_page():
    return page_response("methodology.html")

@app.get("/product/{sku}", include_in_schema=False)
def product_page(sku: str):
    return page_response("product.html")

@app.get("/static/{path:path}", include_in_schema=False)
def static_files(path: str):
    response = FileResponse(WEB_ROOT / "static" / path)
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"
    return response

if __name__ == "__main__":
    import os
    from pathlib import Path
    import uvicorn
    # Ensure data directory exists and database is initialized
    db_path = Path(__file__).resolve().parents[1] / "data" / "price-tracker.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if not db_path.is_file():
        from src.price_tracker.db import init_database
        schema_path = Path(__file__).resolve().parents[1] / "db" / "schema.sql"
        init_database(str(db_path), str(schema_path))
        print(f"Initialized database at {db_path}")
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)