import os
import time
import uuid
import json
import hmac
import hashlib
import logging
import redis
from rq import Queue
from rq.job import Job
from fastapi import FastAPI, UploadFile, File, HTTPException, status, Depends, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import select, func, and_, text, String
from sqlalchemy.orm import Session
from .db import get_session
from .models import Transactions, TransactionsRaw, Flag
from .suggestions_engine import generate_suggestions

app = FastAPI(title="craft_cost API")

# CORS: configurable via env; default to localhost for dev
cors_env = os.getenv("CORS_ALLOW_ORIGINS")
if cors_env:
    allowed = [o.strip() for o in cors_env.split(",") if o.strip()]
else:
    # Dev default
    allowed = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

RATE_LIMIT_RPM = int(os.getenv("RATE_LIMIT_RPM", "120"))
_redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    if RATE_LIMIT_RPM <= 0:
        return await call_next(request)
    try:
        ip = request.client.host if request.client else "unknown"
        bucket = int(time.time() // 60)
        key = f"rl:{ip}:{request.url.path}:{bucket}"
        r = redis.from_url(_redis_url)
        count = r.incr(key)
        if count == 1:
            r.expire(key, 60)
        if count > RATE_LIMIT_RPM:
            return JSONResponse(status_code=429, content={"error": {"code": "rate_limited", "message": "Too many requests"}})
    except Exception:
        # Fail open on limiter errors in dev
        pass
    return await call_next(request)


@app.middleware("http")
async def request_id_and_logging_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    start = time.time()
    response = await call_next(request)
    duration_ms = int((time.time() - start) * 1000)
    response.headers["X-Request-ID"] = request_id
    # Security headers (API)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "no-referrer")
    response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
    # Minimal JSON log with redaction
    redact = {"authorization", "cookie"}
    headers = {k: ("<redacted>" if k.lower() in redact else v) for k, v in request.headers.items()}
    logging.getLogger("api").info(json.dumps({
        "event": "http_request",
        "method": request.method,
        "path": request.url.path,
        "status": getattr(response, "status_code", None),
        "duration_ms": duration_ms,
        "request_id": request_id,
    }))
    return response

@app.get("/healthz")
async def healthz():
    return {"status": "ok", "service": "craft_cost API"}

def _queue() -> Queue:
    return Queue("default", connection=redis.from_url(_redis_url))


# Week 2: enqueue CSV ingestion job (no DB writes yet)
@app.post("/v1/transactions/csv")
async def upload_csv(file: UploadFile = File(...)):
    data = await file.read()
    q = _queue()
    # pass function path so worker can import its own code
    job = q.enqueue_call(
        func="worker.jobs.csv_ingest_db.ingest_csv",
        args=(data,),
        kwargs={},
        timeout=300,
    )
    return JSONResponse(status_code=status.HTTP_202_ACCEPTED, content={"job_id": job.id})


@app.get("/v1/jobs/{job_id}")
async def job_status(job_id: str):
    q = _queue()
    job = Job.fetch(job_id, connection=q.connection)
    state = job.get_status()  # queued, started, finished, failed, deferred
    resp = {"job_id": job.id, "status": state}
    if state == "finished":
        resp["result"] = job.result
    if state == "failed":
        resp["error"] = str(job.exc_info)[-1000:]
    return resp

@app.get("/v1/transactions")
async def list_transactions(
    cursor: int | None = Query(None, description="Return items with id < cursor (pagination)"),
    limit: int = Query(50, ge=1, le=200),
    category: str | None = Query(None),
    period: str | None = Query(None, description="Optional: last_7d | last_30d | last_90d | all_time"),
    db: Session = Depends(get_session),
):
    # Join normalized tx with raw to expose date/amount/description in one payload
    stmt = (
        select(
            Transactions.id.label("id"),
            Transactions.user_id,
            func.cast(Transactions.category, String).label("category"),
            Transactions.merchant_norm,
            TransactionsRaw.date,
            TransactionsRaw.amount,
            TransactionsRaw.description,
        )
        .join(TransactionsRaw, Transactions.tx_id == TransactionsRaw.id)
        .order_by(Transactions.id.desc())
        .limit(limit)
    )
    if cursor is not None:
        stmt = stmt.where(Transactions.id < cursor)
    if category:
        stmt = stmt.where(Transactions.category == category)
    if period in {"last_7d", "last_30d", "last_90d"}:
        days = 7 if period == "last_7d" else (30 if period == "last_30d" else 90)
        stmt = stmt.where(TransactionsRaw.date >= func.current_date() - days)

    rows = db.execute(stmt).all()
    items = [
        {
            "id": r.id,
            "user_id": r.user_id,
            "category": r.category,
            "merchant": r.merchant_norm,
            "date": r.date.isoformat() if r.date else None,
            "amount": float(r.amount) if r.amount is not None else None,
            "description": r.description,
        }
        for r in rows
    ]
    next_cursor = items[-1]["id"] if items else None
    return {"items": items, "next_cursor": next_cursor}

@app.get("/v1/spend/summary")
async def spend_summary(period: str = "last_30d", db: Session = Depends(get_session)):
    # Minimal: sum by category from normalized transactions joined to raw amounts
    if period == "last_7d":
        days = 7
    elif period == "last_30d":
        days = 30
    elif period == "last_90d":
        days = 90
    elif period == "all_time":
        days = None
    else:
        days = 30
    # If no created_at, filter by raw.date
    stmt = (
        select(Transactions.category, func.coalesce(func.sum(TransactionsRaw.amount), 0))
        .join(TransactionsRaw, Transactions.tx_id == TransactionsRaw.id)
    )
    if days is not None:
        stmt = stmt.where(TransactionsRaw.date >= func.current_date() - days)
    stmt = stmt.group_by(Transactions.category)
    rows = db.execute(stmt).all()
    by_category = { (k or "uncategorized"): float(v or 0) for k, v in rows }
    total = float(sum(by_category.values()))
    return {"period": period, "total": total, "by_category": by_category}


@app.get("/v1/suggestions")
async def get_suggestions(db: Session = Depends(get_session)):
    items = generate_suggestions(db)
    return {"items": items}


class FlagPayload(BaseModel):
    key: str
    value: bool


@app.get("/v1/flags")
async def get_flags(db: Session = Depends(get_session)):
    rows = db.execute(select(Flag)).scalars().all()
    return {"flags": {r.key: r.bool_value for r in rows}}


@app.post("/v1/flags")
async def set_flag(payload: FlagPayload, db: Session = Depends(get_session)):
    # upsert simple bool flag
    existing = db.get(Flag, payload.key)
    if existing:
        existing.bool_value = payload.value
    else:
        db.add(Flag(key=payload.key, bool_value=payload.value))
    db.commit()
    return {"ok": True}

# (DB-backed /v1/flags defined above)


# Week 3: Recategorize a transaction by id
class RecategorizePayload(BaseModel):
    category: str


ALLOWED_CATEGORIES = {
    "housing","utilities","telco","insurance","transport","grocery","dining","entertainment",
    "subscriptions","health","personal","fees","income","other",
}


@app.post("/v1/transactions/{tx_id}/recategorize")
async def recategorize_transaction(tx_id: int, payload: RecategorizePayload, db: Session = Depends(get_session)):
    cat = payload.category.strip().lower()
    if cat not in ALLOWED_CATEGORIES:
        raise HTTPException(status_code=400, detail={"code": "invalid_category", "message": "Unsupported category"})

    # Ensure exists, then update
    tx = db.get(Transactions, tx_id)
    if not tx:
        raise HTTPException(status_code=404, detail={"code": "not_found", "message": "Transaction not found"})
    # Explicitly cast to Postgres enum to avoid type mismatch on update
    db.execute(text("UPDATE transactions SET category = CAST(:cat AS tx_category) WHERE id = :id"), {"cat": cat, "id": tx_id})
    db.commit()

    # Return joined view consistent with list endpoint
    stmt = (
        select(
            Transactions.id.label("id"),
            Transactions.user_id,
            func.cast(Transactions.category, String).label("category"),
            Transactions.merchant_norm,
            TransactionsRaw.date,
            TransactionsRaw.amount,
            TransactionsRaw.description,
        )
        .join(TransactionsRaw, Transactions.tx_id == TransactionsRaw.id)
        .where(Transactions.id == tx_id)
        .limit(1)
    )
    row = db.execute(stmt).first()
    if not row:
        raise HTTPException(status_code=500, detail={"code": "updated_row_missing", "message": "Updated row missing"})
    return {
        "id": row.id,
        "user_id": row.user_id,
        "category": row.category,
        "merchant": row.merchant_norm,
        "date": row.date.isoformat() if row.date else None,
        "amount": float(row.amount) if row.amount is not None else None,
        "description": row.description,
    }


# Webhook scaffolds (Stripe/Plaid)
@app.post("/v1/webhooks/stripe")
async def webhook_stripe(request: Request):
    secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    payload = await request.body()
    sig = request.headers.get("Stripe-Signature")
    if secret and sig:
        try:
            mac = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
            if mac not in sig:
                return JSONResponse(status_code=400, content={"error": {"code": "invalid_signature", "message": "Signature mismatch"}})
        except Exception:
            return JSONResponse(status_code=400, content={"error": {"code": "invalid_request", "message": "Unable to verify"}})
    # Accept in dev even without secret
    return {"ok": True}


@app.post("/v1/webhooks/plaid")
async def webhook_plaid(request: Request):
    secret = os.getenv("PLAID_WEBHOOK_SECRET")
    payload = await request.body()
    sig = request.headers.get("Plaid-Verification") or request.headers.get("Plaid-Webhook-Signature")
    if secret and sig:
        try:
            mac = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256).hexdigest()
            if mac not in sig:
                return JSONResponse(status_code=400, content={"error": {"code": "invalid_signature", "message": "Signature mismatch"}})
        except Exception:
            return JSONResponse(status_code=400, content={"error": {"code": "invalid_request", "message": "Unable to verify"}})
    return {"ok": True}


# Retention job trigger (dev/admin)
@app.post("/v1/admin/retention/transactions_raw")
async def trigger_retention(days: int = 90, dry_run: bool = True):
    q = _queue()
    job = q.enqueue_call(
        func="worker.jobs.retention.enforce_transactions_raw_retention",
        args=(days, dry_run),
        timeout=120,
    )
    return {"job_id": job.id}
