from __future__ import annotations
import csv
import io
import os
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any
import hashlib

from sqlalchemy import create_engine, text

POSTGRES_URL = os.getenv("POSTGRES_URL", "postgresql+psycopg://postgres:postgres@db:5432/app")


def _ensure_dev_user(conn) -> int:
    # ensure a dev user exists; return its id
    res = conn.execute(text("""
        SELECT id FROM users WHERE email=:email
    """), {"email": "dev@example.com"}).fetchone()
    if res:
        return int(res[0])
    res = conn.execute(text("""
        INSERT INTO users (email, auth_id, kyc_min, marketing_opt_in)
        VALUES (:email, NULL, FALSE, FALSE)
        RETURNING id
    """), {"email": "dev@example.com"}).fetchone()
    return int(res[0])


def _row_hash(user_id: int, date_s: str | None, amount: Decimal, desc: str | None, merchant_raw: str | None) -> str:
    # Normalize to a deterministic key; include user_id to avoid cross-user collisions
    base = "|".join([
        str(user_id),
        (date_s or "").strip(),
        f"{amount:.2f}",
        (desc or "").strip().lower(),
        (merchant_raw or "").strip().lower(),
    ])
    return hashlib.sha256(base.encode("utf-8")).hexdigest()


def _guess_category(desc: str | None, merchant: str | None) -> str | None:
    t = f"{(merchant or '').lower()} {(desc or '').lower()}".strip()
    if not t:
        return None
    # Transport first: avoid misclassifying gas station as utilities
    if any(k in t for k in ("fuel", "gas station", "rideshare", "ride share", "uber", "lyft", "metro", "bus", "train", "taxi", "transport")):
        return "transport"
    # Housing
    if any(k in t for k in ("rent", "landlord")):
        return "housing"
    # Telco
    if any(k in t for k in ("internet", "isp", "mobile", "telco", "phone")):
        return "telco"
    # Utilities (not gas station)
    if any(k in t for k in ("utilit", "electric", "water", "power", "sewer", "energy", "natural gas", "gas bill", "gas utility", "gas company", "city utilities")):
        return "utilities"
    # Insurance
    if "insurance" in t:
        return "insurance"
    # Grocery
    if any(k in t for k in ("grocery", "grocer", "market")):
        return "grocery"
    # Dining
    if any(k in t for k in ("dining", "restaurant", "sushi", "pizza", "burger", "cafe", "coffee")):
        return "dining"
    # Subscriptions / streaming
    if any(k in t for k in ("stream", "subscription", "netflix", "hulu", "disney", "spotify", "apple tv", "youtube premium")):
        return "subscriptions"
    # Health / personal
    if any(k in t for k in ("pharmacy", "doctor", "clinic")):
        return "health"
    if any(k in t for k in ("gym", "fitness")):
        return "personal"
    # Income
    if any(k in t for k in ("salary", "payroll", "employer")):
        return "income"
    # Entertainment / travel / gift fallbacks
    if any(k in t for k in ("cinema", "movie", "entertainment")):
        return "entertainment"
    if any(k in t for k in ("flight", "hotel", "travel")):
        return "other"
    return None


def ingest_csv(data: bytes) -> Dict[str, Any]:
    engine = create_engine(POSTGRES_URL, future=True)
    rows = 0
    with engine.begin() as conn:
        user_id = _ensure_dev_user(conn)
        buf = io.StringIO(data.decode("utf-8", errors="replace"))
        reader = csv.DictReader(buf)
        for rec in reader:
            try:
                dt = rec.get("date") or rec.get("Date")
                date_obj = datetime.strptime(dt.strip(), "%Y-%m-%d").date() if dt else None
                amount_str = (rec.get("amount") or rec.get("Amount") or "0").replace(",", "")
                amount = Decimal(amount_str)
                desc = (rec.get("description") or rec.get("Description") or "").strip() or None
                merchant_raw = (rec.get("merchant") or rec.get("Merchant") or rec.get("merchant_raw") or "").strip() or None

                tx_raw_id = conn.execute(text("""
                    INSERT INTO transactions_raw (user_id, account_id, plaid_tx_id, date, amount, iso_currency, description, merchant_raw, meta_json)
                    VALUES (:user_id, NULL, NULL, :date, :amount, NULL, :description, :merchant_raw, NULL)
                    RETURNING id
                """), {
                    "user_id": user_id,
                    "date": date_obj,
                    "amount": amount,
                    "description": desc,
                    "merchant_raw": merchant_raw,
                }).fetchone()[0]

                cat = _guess_category(desc, merchant_raw)
                conn.execute(text("""
                    INSERT INTO transactions (user_id, tx_id, category, merchant_norm, normalized_desc, confidence, is_recurring)
                    VALUES (:user_id, :tx_id, CAST(:category AS tx_category), :merchant_norm, :normalized_desc, NULL, FALSE)
                """), {
                    "user_id": user_id,
                    "tx_id": tx_raw_id,
                    "category": cat,
                    "merchant_norm": merchant_raw,
                    "normalized_desc": desc,
                })
                rows += 1
            except Exception:
                # Continue on bad rows; production code should dead-letter
                continue
    return {"rows": rows}
