from __future__ import annotations
from fastapi import FastAPI, UploadFile, File, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI(title="DebtAdvisor API")

# CORS (relaxed in dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/healthz")
async def healthz():
    return {"status": "ok", "service": "DebtAdvisor API"}

# Week 2 scaffolding (no processing/generation yet)
@app.post("/v1/transactions/csv")
async def upload_csv(file: UploadFile = File(...)):
    # Endpoint scaffolded; processing disabled until approval.
    return JSONResponse(
        status_code=status.HTTP_202_ACCEPTED,
        content={"job_id": None, "message": "CSV ingestion scaffolded; processing disabled until approved"},
    )

@app.get("/v1/transactions")
async def list_transactions(cursor: str | None = None, limit: int = 50, category: str | None = None):
    # Read-only stub; returns no data until ingestion approved.
    return {"items": [], "next_cursor": None}

@app.get("/v1/spend/summary")
async def spend_summary(period: str = "last_30d"):
    # Stub summary with zeros.
    return {"period": period, "total": 0, "by_category": {}}

@app.get("/v1/flags")
async def get_flags():
    # Flags not persisted yet; stub only.
    return {"flags": {"csv_ingestion_enabled": False}}
