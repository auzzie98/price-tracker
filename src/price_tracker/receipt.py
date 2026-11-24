from __future__ import annotations

import re
from pathlib import Path

import yaml


PRICE_PATTERN = re.compile(r"\$([0-9][0-9,]*\.[0-9]{2})")
DATE_PATTERN = re.compile(
    r"\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|"
    r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
    r"[a-z]*\s+\d{1,2},?\s+\d{4})\b",
    re.IGNORECASE,
)


def normalize_text(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def extract_price(text: str) -> int | None:
    match = PRICE_PATTERN.search(text)
    if not match:
        return None
    return int(round(float(match.group(1).replace(",", "")) * 100))


def extract_date(text: str) -> str | None:
    match = DATE_PATTERN.search(text)
    return match.group(0) if match else None


def extract_seller(text: str) -> str | None:
    lines = text.replace("\r", "").split("\n")
    pattern = re.compile(r"(?:sold\s*(?:and\s*shipped)?\s*by)\s*:?\s*(.+)", re.IGNORECASE)
    for line in lines:
        match = pattern.search(line)
        if match:
            seller = re.sub(r"\s+", " ", match.group(1)).strip(" .")
            seller = re.split(r"\b(?:ships?|fulfill(ed)?|available|arrives)\b", seller, maxsplit=1, flags=re.IGNORECASE)[0].strip(" ,")
            if seller:
                return seller
    return None


def extract_retailer(text: str, retailers: list[dict]) -> str | None:
    normalized = normalize_text(text)
    for retailer in sorted(retailers, key=lambda item: -len(item["name"])):
        name = normalize_text(retailer["name"])
        if name and name in normalized:
            return retailer["id"]
    return None


def extract_stock_status(text: str) -> str:
    normalized = normalize_text(text)
    if re.search(r"\b(out of stock|unavailable|not available)\b", normalized):
        return "out_of_stock"
    if re.search(r"\b(in stock|available|ships today)\b", normalized):
        return "in_stock"
    return "unknown"


def load_catalog() -> list[dict]:
    root = Path(__file__).resolve().parents[2]
    with (root / "config" / "products.yaml").open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle).get("products", [])


def match_catalog_model(text: str, products: list[dict]) -> dict | None:
    normalized = normalize_text(text)
    compact = re.sub(r"[^a-z0-9]", "", text.lower())
    known_brands = {
        normalize_text(product["brand"])
        for product in products
        if product.get("brand")
    }
    text_brands = {
        brand for brand in known_brands
        if brand and brand in normalized
    }

    for product in products:
        mpn = normalize_text(product["mpn"])
        mpn_compact = re.sub(r"[^a-z0-9]", "", product["mpn"].lower())
        if mpn_compact and mpn_compact in compact:
            return product

    scored: list[tuple[int, dict]] = []
    for product in products:
        model_name = normalize_text(product["model"])
        chip = normalize_text(product["chip"] or "")
        brand = normalize_text(product["brand"])
        score = 0
        if model_name and model_name in normalized:
            score += 100
        if chip and chip in normalized:
            score += 45
        if brand and brand in normalized:
            score += 10
        for alias in (
            normalize_text(product["mpn"]),
            normalize_text(product["brand"] + " " + product["model"]),
        ):
            if alias and alias in normalized:
                score += 20
        if score:
            scored.append((score, product))

    if not scored:
        return None
    scored.sort(key=lambda item: item[0], reverse=True)
    if scored[0][0] >= 55:
        return scored[0][1]
    return None


def parse_receipt(text: str, picked_model_id: str, picked_retailer_id: str) -> dict:
    products = load_catalog()
    matched = match_catalog_model(text, products)
    picked = next((item for item in products if item["id"] == picked_model_id), None)

    root = Path(__file__).resolve().parents[2]
    with (root / "config" / "retailers.yaml").open("r", encoding="utf-8") as handle:
        retailers = yaml.safe_load(handle).get("retailers", [])

    extracted_retailer_id = extract_retailer(text, retailers)
    seller = extract_seller(text)
    picked_retailer = next(
        (item for item in retailers if item["id"] == picked_retailer_id),
        None,
    )
    manufacturer_names = {
        "amd", "intel", "nvidia", "msi", "gigabyte", "sapphire", "asrock",
        "corsair", "g skill", "gskill", "kingston", "teamgroup", "crucial",
        "pny",
    }
    seller_normalized = normalize_text(seller or "")
    third_party = False
    if seller:
        if (
            seller_normalized in manufacturer_names
            or any(name in seller_normalized for name in manufacturer_names)
        ):
            third_party = False
        elif picked_retailer:
            retailer_name = normalize_text(picked_retailer["name"])
            third_party = (
                seller_normalized not in retailer_name
                and retailer_name not in seller_normalized
            )

    mismatch = bool(matched and picked and matched["id"] != picked_model_id)
    brand_or_product_match = bool(
        matched is None
        and picked
        and normalize_text(picked["brand"]) in normalize_text(text)
        and normalize_text(picked["chip"]) not in normalize_text(text)
    )

    if matched:
        match_status = "match" if matched["id"] == picked_model_id else "mismatch"
    elif brand_or_product_match:
        match_status = "mismatch"
    else:
        match_status = "no_match"

    return {
        "extracted_model_id": matched["id"] if matched else None,
        "extracted_model_name": matched["model"] if matched else None,
        "extracted_category": matched["category"] if matched else None,
        "extracted_part_number": matched["mpn"] if matched else None,
        "suggested_model_id": matched["id"] if matched else None,
        "match_status": match_status,
        "needs_manual_check": matched is None,
        "picked_model_id": picked_model_id,
        "picked_model_name": picked["model"] if picked else picked_model_id,
        "extracted_retailer_id": extracted_retailer_id,
        "seller_name": seller,
        "third_party": third_party,
        "stock_status": extract_stock_status(text),
        "extracted_price_cents": extract_price(text),
        "extracted_date": extract_date(text),
    }
