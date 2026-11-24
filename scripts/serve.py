from datetime import datetime, timezone
from pathlib import Path
import re
import subprocess
import sys
import uuid
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.responses import FileResponse

WEB_ROOT = Path(__file__).resolve().parents[1] / "web"
DB_PATH = Path(__file__).resolve().parents[1] / "data" / "price-tracker.db"
UPLOAD_ROOT = WEB_ROOT / "uploads"
TESSERACT_PATH = Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe")

PRICE_PATTERN = re.compile(r"\$([0-9][0-9,]*\.[0-9]{2})")
DATE_PATTERN = re.compile(
    r"\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4})\b",
    re.IGNORECASE,
)


def page_response(relative_path):
    response = FileResponse(WEB_ROOT / relative_path)
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"
    return response

app = FastAPI()


def get_product_options():
    from price_tracker.config import load_products
    return [
        (product["id"], product["model"], product["category"])
        for product in load_products()
    ]


def get_retailer_options():
    from price_tracker.config import load_retailers
    return [(retailer["id"], retailer["name"]) for retailer in load_retailers()]


def extract_suggested_price(text):
    match = PRICE_PATTERN.search(text)
    if not match:
        return None
    return int(round(float(match.group(1).replace(",", "")) * 100))

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

@app.get("/upload-receipt", include_in_schema=False)
def upload_receipt_page():
    return page_response("upload_receipt.html")

@app.post("/upload-receipt")
async def upload_receipt(
    photo: UploadFile = File(...),
    model_id: str = Form(...),
    retailer: str = Form(...),
):
    product_ids = {item[0] for item in get_product_options()}
    retailer_ids = {item[0] for item in get_retailer_options()}
    if model_id not in product_ids:
        raise HTTPException(status_code=400, detail="Unknown model id")
    if retailer not in retailer_ids:
        raise HTTPException(status_code=400, detail="Unknown retailer")

    UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    suffix = Path(photo.filename or "receipt").suffix.lower()
    if suffix not in {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}:
        raise HTTPException(status_code=400, detail="Photo must be an image")
    filename = f"{timestamp}_{uuid.uuid4().hex}{suffix}"
    photo_path = UPLOAD_ROOT / filename

    contents = await photo.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Photo is empty")
    photo_path.write_bytes(contents)

    ocr_text = ""
    suggested_price = None
    receipt_date = None
    try:
        import pytesseract
        from PIL import Image
        if TESSERACT_PATH.is_file():
            pytesseract.pytesseract.tesseract_cmd = str(TESSERACT_PATH)
        with Image.open(photo_path) as image:
            ocr_text = pytesseract.image_to_string(image)
        suggested_price = extract_suggested_price(ocr_text)
        date_match = DATE_PATTERN.search(ocr_text)
        if date_match:
            receipt_date = date_match.group(0)
    except Exception as exc:
        ocr_text = f"OCR unavailable: {exc}"

    conn = __import__("sqlite3").connect(str(DB_PATH))
    try:
        conn.execute(
            """INSERT INTO receipt_submissions
               (model_id, retailer, photo_path, ocr_text, suggested_price_cents, status, created_at)
               VALUES (?, ?, ?, ?, ?, 'pending', ?)""",
            (
                model_id,
                retailer,
                str(photo_path.relative_to(Path(__file__).resolve().parents[1])).replace("\\", "/"),
                ocr_text,
                suggested_price,
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        conn.commit()
        submission_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    finally:
        conn.close()

    return {
        "id": submission_id,
        "status": "pending",
        "ocr_text": ocr_text,
        "suggested_price_cents": suggested_price,
        "suggested_price_dollars": suggested_price / 100 if suggested_price is not None else None,
        "date": receipt_date,
    }

@app.get("/review", include_in_schema=False)
def review_page():
    return page_response("review.html")

@app.get("/api/receipt-submissions")
def receipt_submissions():
    conn = __import__("sqlite3").connect(str(DB_PATH))
    conn.row_factory = __import__("sqlite3").Row
    try:
        rows = conn.execute(
            """SELECT rs.id, rs.model_id, rs.retailer, rs.photo_path, rs.ocr_text,
                      rs.suggested_price_cents, rs.status, rs.created_at,
                      sk.model AS model_name
               FROM receipt_submissions rs
               JOIN skus sk ON sk.id = rs.model_id
               ORDER BY rs.created_at DESC, rs.id DESC"""
        ).fetchall()
        submissions = [dict(row) for row in rows]
        for submission in submissions:
            photo_path = submission.get("photo_path")
            photo_file = (Path(__file__).resolve().parents[1] / photo_path).resolve() if photo_path else None
            submission["photo_exists"] = bool(
                photo_file
                and photo_file.is_file()
                and Path(__file__).resolve().parents[1].joinpath("web", "uploads").resolve() in photo_file.parents
            )
            submission["photo_url"] = (
                "/uploads/" + photo_file.name
                if submission["photo_exists"]
                else None
            )
        counts = {
            "pending": sum(row["status"] == "pending" for row in submissions),
            "approved": sum(row["status"] == "approved" for row in submissions),
            "rejected": sum(row["status"] == "rejected" for row in submissions),
        }
        return {"submissions": submissions, "counts": counts}
    finally:
        conn.close()

@app.post("/api/receipt-submissions/{submission_id}/approve")
def approve_submission(submission_id: int):
    conn = __import__("sqlite3").connect(str(DB_PATH))
    try:
        row = conn.execute(
            """SELECT model_id, retailer, photo_path, suggested_price_cents
               FROM receipt_submissions WHERE id = ? AND status = 'pending'""",
            (submission_id,),
        ).fetchone()
        if not row:
            existing = conn.execute(
                "SELECT status FROM receipt_submissions WHERE id = ?",
                (submission_id,),
            ).fetchone()
            if existing is None:
                raise HTTPException(status_code=404, detail=f"Submission {submission_id} not found")
            raise HTTPException(
                status_code=409,
                detail=f"Submission {submission_id} is {existing[0]}, not pending",
            )
        model_id, retailer_id, photo_path, price_cents = row
        if price_cents is None:
            print(
                f"Approve submission {submission_id} rejected: "
                "suggested_price_cents is missing",
                flush=True,
            )
            raise HTTPException(
                status_code=400,
                detail="Cannot approve: suggested price is missing",
            )
        if price_cents <= 0:
            print(
                f"Approve submission {submission_id} rejected: "
                f"invalid suggested_price_cents={price_cents}",
                flush=True,
            )
            raise HTTPException(
                status_code=400,
                detail="Cannot approve: suggested price must be greater than zero",
            )

        model = conn.execute(
            "SELECT id FROM skus WHERE id = ?", (model_id,)
        ).fetchone()
        if not model:
            print(
                f"Approve submission {submission_id} rejected: "
                f"unknown model_id={model_id}",
                flush=True,
            )
            raise HTTPException(status_code=400, detail=f"Unknown model id: {model_id}")

        retailer = conn.execute(
            "SELECT id FROM retailers WHERE id = ?", (retailer_id,)
        ).fetchone()
        if not retailer:
            conn.execute(
                "INSERT INTO retailers (id, name, base_url, enabled) VALUES (?, ?, '', 1)",
                (retailer_id, dict(get_retailer_options()).get(retailer_id, retailer_id)),
            )

        conn.execute(
            """INSERT INTO observations
               (observed_at, sku_id, retailer_id, price_cents, in_stock, source_url)
               VALUES (?, ?, ?, ?, 1, ?)""",
            (
                datetime.now(timezone.utc).isoformat(),
                model_id,
                retailer_id,
                price_cents,
                photo_path,
            ),
        )
        conn.execute(
            "UPDATE receipt_submissions SET status = 'approved' WHERE id = ?",
            (submission_id,),
        )
        conn.commit()
        print(
            f"Approved submission {submission_id}: model_id={model_id}, "
            f"retailer={retailer_id}, price_cents={price_cents}",
            flush=True,
        )
    finally:
        conn.close()

    result = subprocess.run(
        [sys.executable, str(Path(__file__).resolve().parents[1] / "scripts" / "build_derived.py")],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise HTTPException(status_code=500, detail=result.stderr or "Derived rebuild failed")
    return {"status": "approved", "submission_id": submission_id}

@app.post("/api/receipt-submissions/{submission_id}/reject")
def reject_submission(submission_id: int):
    conn = __import__("sqlite3").connect(str(DB_PATH))
    try:
        existing = conn.execute(
            "SELECT status FROM receipt_submissions WHERE id = ?",
            (submission_id,),
        ).fetchone()
        if existing is None:
            raise HTTPException(status_code=404, detail=f"Submission {submission_id} not found")
        if existing[0] != "pending":
            raise HTTPException(
                status_code=409,
                detail=f"Submission {submission_id} is {existing[0]}, not pending",
            )
        result = conn.execute(
            "UPDATE receipt_submissions SET status = 'rejected' WHERE id = ?",
            (submission_id,),
        )
        conn.commit()
        if result.rowcount == 0:
            raise HTTPException(status_code=409, detail=f"Submission {submission_id} could not be rejected")
        print(f"Rejected submission {submission_id}: no observation inserted", flush=True)
    finally:
        conn.close()
    return {"status": "rejected", "submission_id": submission_id}

@app.post("/api/receipt-submissions/{submission_id}/revert")
def revert_submission(submission_id: int):
    conn = __import__("sqlite3").connect(str(DB_PATH))
    try:
        row = conn.execute(
            """SELECT model_id, retailer, photo_path, suggested_price_cents
               FROM receipt_submissions WHERE id = ? AND status = 'approved'""",
            (submission_id,),
        ).fetchone()
        if not row:
            existing = conn.execute(
                "SELECT status FROM receipt_submissions WHERE id = ?",
                (submission_id,),
            ).fetchone()
            if existing is None:
                raise HTTPException(status_code=404, detail=f"Submission {submission_id} not found")
            raise HTTPException(
                status_code=409,
                detail=f"Submission {submission_id} is {existing[0]}, not approved",
            )

        model_id, retailer_id, photo_path, price_cents = row
        deleted = conn.execute(
            """DELETE FROM observations
               WHERE source_url = ?
                 AND sku_id = ?
                 AND retailer_id = ?
                 AND price_cents = ?""",
            (photo_path, model_id, retailer_id, price_cents),
        )
        conn.execute(
            "UPDATE receipt_submissions SET status = 'rejected' WHERE id = ?",
            (submission_id,),
        )
        conn.commit()
        print(
            f"Reverted submission {submission_id} to rejected: "
            f"deleted {deleted.rowcount} observation",
            flush=True,
        )
    finally:
        conn.close()

    result = subprocess.run(
        [sys.executable, str(Path(__file__).resolve().parents[1] / "scripts" / "build_derived.py")],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise HTTPException(status_code=500, detail=result.stderr or "Derived rebuild failed")
    return {
        "status": "rejected",
        "submission_id": submission_id,
        "observations_deleted": deleted.rowcount,
    }

@app.post("/api/receipt-submissions/{submission_id}/reset")
def reset_submission_to_pending(submission_id: int):
    conn = __import__("sqlite3").connect(str(DB_PATH))
    observations_deleted = 0
    try:
        row = conn.execute(
            """SELECT status, model_id, retailer, photo_path, suggested_price_cents
               FROM receipt_submissions WHERE id = ?""",
            (submission_id,),
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail=f"Submission {submission_id} not found")

        status, model_id, retailer_id, photo_path, price_cents = row
        if status not in {"approved", "rejected"}:
            raise HTTPException(
                status_code=409,
                detail=f"Submission {submission_id} is {status}, not approved or rejected",
            )

        if status == "approved":
            deleted = conn.execute(
                """DELETE FROM observations
                   WHERE source_url = ?
                     AND sku_id = ?
                     AND retailer_id = ?
                     AND price_cents = ?""",
                (photo_path, model_id, retailer_id, price_cents),
            )
            observations_deleted = deleted.rowcount

        conn.execute(
            "UPDATE receipt_submissions SET status = 'pending' WHERE id = ?",
            (submission_id,),
        )
        conn.commit()
        print(
            f"Reset submission {submission_id} to pending: "
            f"deleted {observations_deleted} observation",
            flush=True,
        )
    finally:
        conn.close()

    if status == "approved":
        result = subprocess.run(
            [sys.executable, str(Path(__file__).resolve().parents[1] / "scripts" / "build_derived.py")],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise HTTPException(status_code=500, detail=result.stderr or "Derived rebuild failed")

    return {
        "status": "pending",
        "submission_id": submission_id,
        "observations_deleted": observations_deleted,
    }

@app.get("/api/retailers")
def retailers_api():
    return {"retailers": [{"id": item_id, "name": name} for item_id, name in get_retailer_options()]}

@app.get("/api/receipt-options")
def receipt_options_api():
    return {
        "models": [
            {"id": item_id, "model": model, "category": category}
            for item_id, model, category in get_product_options()
        ],
        "retailers": [
            {"id": item_id, "name": name}
            for item_id, name in get_retailer_options()
        ],
    }

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

@app.get("/uploads/{path:path}", include_in_schema=False)
def uploaded_files(path: str):
    file_path = (UPLOAD_ROOT / path).resolve()
    if UPLOAD_ROOT.resolve() not in file_path.parents:
        raise HTTPException(status_code=404, detail="Photo not found")
    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="Photo not found")
    return FileResponse(file_path)

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