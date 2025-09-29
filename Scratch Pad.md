# Scratch Pad — Project Checkpoints

Legend: [ ] Pending  [x] Completed  [-] In Progress

## Week 1 — Foundation & DevEx
- [x] Monorepo/Repo scaffold and basic scripts
- [x] Docker Compose present
- [x] API skeleton and health endpoint
- [x] Initial DB migration plan (Alembic) and verification
- [x] Security baselines (.env.example guidance, headers/crypto plan)
- [x] Docs: README, SECURITY, RUNBOOK
- [x] CI/Pipelines placeholder
- [x] Week 1 verified on 2025-09-29

## Week 2 — ETL, Categorization, Recurring
- [ ] CSV ingestion endpoint `POST /v1/transactions/csv` (multipart) → returns {job_id}
- [ ] Background job scaffolding (RQ) for CSV processing
- [ ] Read APIs: `GET /v1/transactions`, `GET /v1/spend/summary`
- [ ] Feature flags endpoint `/v1/flags`
- [ ] Minimal UI: Upload CSV form + list view (clean, minimal)

Notes
- No mock/system-generated data until approved.
- Pipelines kept minimal for now; expand in Week 2–3.
