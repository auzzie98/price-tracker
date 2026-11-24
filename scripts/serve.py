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


def initialize_database() -> None:
    ROOT = Path(__file__).resolve().parents[1]
    database_path = ROOT / "data" / "price-tracker.db"
    schema_path = ROOT / "db" / "schema.sql"
    database_path.parent.mkdir(parents=True, exist_ok=True)
    from price_tracker.db import init_database
    init_database(database_path, schema_path)


def get_product_options():
    from price_tracker.config import load_products
    products = [
        (product["id"], product["model"], product["category"])
        for product in load_products()
    ]
    category_order = {"GPUs": 0, "CPUs": 1, "RAM": 2}
    return sorted(
        products,
        key=lambda item: (category_order.get(item[2], 99), item[1].lower()),
    )


def get_retailer_options():
    from price_tracker.config import load_retailers
    return [(retailer["id"], retailer["name"]) for retailer in load_retailers()]


def retailer_is_sold_only(retailer_id):
    from price_tracker.config import load_retailers
    for retailer in load_retailers():
        if retailer["id"] == retailer_id:
            return retailer.get("retailer_sold_only", True)
    return False


def extract_suggested_price(text):
    match = PRICE_PATTERN.search(text)
    if not match:
        return None
    return int(round(float(match.group(1).replace(",", "")) * 100))


def receipt_preview(submission_id):
    from price_tracker.receipt import parse_receipt
    conn = __import__("sqlite3").connect(str(DB_PATH))
    conn.row_factory = __import__("sqlite3").Row
    try:
        row = conn.execute(
            """SELECT id, model_id, retailer, photo_path, ocr_text,
                      suggested_price_cents, status, created_at
               FROM receipt_submissions WHERE id = ?""",
            (submission_id,),
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail=f"Submission {submission_id} not found")
        data = parse_receipt(row["ocr_text"], row["model_id"], row["retailer"])
        matched_id = data["extracted_model_id"] or row["model_id"]
        matched_model = conn.execute(
            "SELECT id, model, category FROM skus WHERE id = ?", (matched_id,)
        ).fetchone()
        old_median = conn.execute(
            """SELECT median_price_cents FROM sku_prices
               WHERE sku_id = ? ORDER BY period DESC LIMIT 1""",
            (matched_id,),
        ).fetchone()
        price_cents = row["suggested_price_cents"] or data["extracted_price_cents"]
        new_median = None
        if price_cents:
            period_rows = conn.execute(
                """SELECT price_cents FROM observations
                   WHERE sku_id = ? AND in_stock = 1""",
                (matched_id,),
            ).fetchall()
            prices = [item[0] for item in period_rows] + [price_cents]
            prices.sort()
            count = len(prices)
            new_median = prices[count // 2] if count % 2 else (
                prices[count // 2 - 1] + prices[count // 2]
            ) // 2
            current_median = prices[:-1]
            current_median.sort()
            current_count = len(current_median)
            old_median_preview = (
                current_median[current_count // 2]
                if current_count % 2
                else (
                    current_median[current_count // 2 - 1]
                    + current_median[current_count // 2]
                ) // 2
                if current_count
                else None
            )
    finally:
        conn.close()

    return {
        "submission_id": submission_id,
        "ocr": data,
        "matched_model": dict(matched_model) if matched_model else None,
        "picked_model_id": row["model_id"],
        "retailer_id": row["retailer"],
        "price_cents": price_cents,
        "old_median_cents": old_median_preview if price_cents else (old_median[0] if old_median else None),
        "new_median_cents": new_median,
        "third_party": data["third_party"],
        "seller_name": data["seller_name"],
        "seller_warning": "Seller not found in photo, please check"
        if not data["seller_name"]
        else None,
        "status": (
            "blocked"
            if data["third_party"]
            or data["match_status"] in ("no_match", "mismatch")
            else "ready"
        ),
        "price_warning": (
            "Price looks high, check it"
            if old_median_preview
            and price_cents
            and price_cents > old_median_preview * 1.20
            else None
        ),
        "block_reason": (
            f"Third party seller, do not count: {data['seller_name']}"
            if data["third_party"]
            else "No match in the current catalog, Needs manual check"
            if data["match_status"] == "no_match"
            else (
                f"OCR says {data['extracted_model_name']}, "
                f"you picked {data['picked_model_name']}, these do not match."
                if data["match_status"] == "mismatch"
                else None
            )
        ),
    }

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
            latest = max(category_rows, key=lambda row: row[1])
            result["categories"].append({"category": category, "index_value": latest[2], "skus_used": latest[3]})
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

@app.get("/api/products/{model_id}/retailer-prices")
def product_retailer_prices(model_id: str):
    import sqlite3
    from price_tracker.config import load_products
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            """SELECT id, retailer_id, price_cents, in_stock, observed_at, source_url
               FROM observations
               WHERE sku_id = ?
               ORDER BY observed_at DESC""",
            (model_id,),
        ).fetchall()
        configured = {product["id"]: product for product in load_products()}
        product_url = None
        if model_id in configured:
            product_url = configured[model_id].get("urls", {})
        result = []
        for row in rows:
            retailer = conn.execute(
                "SELECT name, base_url FROM retailers WHERE id = ?",
                (row["retailer_id"],),
            ).fetchone()
            if not retailer:
                continue
            source_url = row["source_url"]
            is_baseline = source_url == "Nov 23, 2026 baseline snapshot"
            label = "Baseline" if is_baseline else "Approved receipt"
            result.append({
                "observation_id": row["id"],
                "retailer_id": row["retailer_id"],
                "retailer_name": retailer["name"],
                "price_cents": row["price_cents"],
                "price_dollars": row["price_cents"] / 100,
                "in_stock": bool(row["in_stock"]),
                "observed_at": row["observed_at"],
                "source_url": source_url,
                "source_label": label,
                "product_url": product_url.get(row["retailer_id"]) if product_url else None,
            })
    finally:
        conn.close()
    return {"retailer_prices": result}

@app.get("/api/products/{model_id}/history")
def api_product_history(model_id: str):
    conn = __import__("sqlite3").connect(str(DB_PATH))
    conn.row_factory = __import__("sqlite3").Row
    try:
        model = conn.execute(
            "SELECT id, brand, model, category, mpn FROM skus WHERE id = ?",
            (model_id,),
        ).fetchone()
        if not model:
            raise HTTPException(status_code=404, detail=f"Model not found: {model_id}")
        rows = conn.execute(
            """SELECT sp.period, sp.median_price_cents, sp.retailers_used
               FROM sku_prices sp
               WHERE sp.sku_id = ?
               ORDER BY sp.period ASC""",
            (model_id,),
        ).fetchall()
        point_rows = [dict(row) for row in rows]
    finally:
        conn.close()
    return {
        "model": dict(model),
        "history": [
            {
                "date": row["period"],
                "median_price_cents": row["median_price_cents"],
                "median_price_dollars": row["median_price_cents"] / 100,
                "retailers_used": row["retailers_used"],
            }
            for row in point_rows
        ],
        "count": len(point_rows),
        "data_label": "Real data, baseline Nov 23, 2026, Black Friday week snapshot",
    }

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

@app.get("/api/receipt-submissions/{submission_id}/preview")
def receipt_submission_preview(submission_id: int):
    return receipt_preview(submission_id)

@app.post("/api/receipt-submissions/{submission_id}/price")
def update_receipt_price(submission_id: int, price_cents: int = Form(...)):
    conn = __import__("sqlite3").connect(str(DB_PATH))
    try:
        if price_cents <= 0:
            raise HTTPException(status_code=400, detail="Price must be greater than zero")
        result = conn.execute(
            "UPDATE receipt_submissions SET suggested_price_cents = ? WHERE id = ?",
            (price_cents, submission_id),
        )
        conn.commit()
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail=f"Submission {submission_id} not found")
    finally:
        conn.close()
    return receipt_preview(submission_id)

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
    preview = receipt_preview(submission_id)
    if preview["status"] == "blocked":
        raise HTTPException(status_code=400, detail=preview["block_reason"])
    if preview["ocr"]["match_status"] != "match":
        raise HTTPException(
            status_code=400,
            detail=preview["block_reason"] or "Model and OCR text do not match",
        )
    if preview["ocr"]["stock_status"] == "out_of_stock":
        raise HTTPException(status_code=400, detail="OCR text says out of stock")

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
        model_id = preview["ocr"]["extracted_model_id"] or model_id
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

        if preview["third_party"]:
            retailer_name = conn.execute(
                "SELECT name FROM retailers WHERE id = ?", (retailer_id,)
            ).fetchone()
            retailer_label = retailer_name[0] if retailer_name else retailer_id
            seller_label = preview["seller_name"] or "Unknown seller"
            print(
                f"Approve submission {submission_id} rejected: "
                f"seller {seller_label}, retailer {retailer_label}",
                flush=True,
            )
            raise HTTPException(
                status_code=400,
                detail=f"Blocked: Seller found is {seller_label}, retailer is {retailer_label}",
            )

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

    conn = __import__("sqlite3").connect(str(DB_PATH))
    try:
        model_row = conn.execute(
            """SELECT median_price_cents FROM sku_prices
               WHERE sku_id = ? ORDER BY period DESC LIMIT 1""",
            (model_id,),
        ).fetchone()
        category_row = conn.execute(
            "SELECT category FROM skus WHERE id = ?", (model_id,)
        ).fetchone()
        index_row = None
        if category_row:
            index_row = conn.execute(
                """SELECT index_value FROM index_values
                   WHERE category = ? ORDER BY period DESC LIMIT 1""",
                (category_row[0],),
            ).fetchone()
    finally:
        conn.close()
    return {
        "status": "approved",
        "submission_id": submission_id,
        "new_median_price_cents": model_row[0] if model_row else None,
        "new_median_price_dollars": model_row[0] / 100 if model_row else None,
        "new_index_value": index_row[0] if index_row else None,
    }

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

@app.get("/api/catalog")
def catalog_api():
    from price_tracker.config import load_products
    from price_tracker.db import connect
    conn = connect(DB_PATH)
    conn.row_factory = __import__("sqlite3").Row
    try:
        products = []
        for product in load_products():
            row = conn.execute(
                """SELECT median_price_cents, period
                   FROM sku_prices WHERE sku_id = ?
                   ORDER BY period DESC LIMIT 1""",
                (product["id"],),
            ).fetchone()
            products.append({
                "id": product["id"],
                "mpn": product["mpn"],
                "brand": product["brand"],
                "model": product["model"],
                "category": product["category"],
                "chip": product["chip"],
                "price_cents": row["median_price_cents"] if row else None,
                "period": row["period"] if row else None,
            })
    finally:
        conn.close()
    return {"products": products}

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
    import uvicorn
    initialize_database()
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)