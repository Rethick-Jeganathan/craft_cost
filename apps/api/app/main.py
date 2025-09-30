from __future__ import annotations
import os
import redis
from rq import Queue
from rq.job import Job
from fastapi import FastAPI, UploadFile, File, HTTPException, status
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

def _queue() -> Queue:
    redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
    return Queue("default", connection=redis.from_url(redis_url))


# Week 2: enqueue CSV ingestion job (no DB writes yet)
@app.post("/v1/transactions/csv")
async def upload_csv(file: UploadFile = File(...)):
    data = await file.read()
    q = _queue()
    # pass function path so worker can import its own code
    job = q.enqueue_call(
        func="worker.jobs.csv_ingest.process_csv",
        args=(data,),
        kwargs={},
        job_timeout=300,
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
