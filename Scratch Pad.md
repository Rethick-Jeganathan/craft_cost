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
- [x] CSV ingestion endpoint `POST /v1/transactions/csv` (multipart) → returns {job_id}
- [x] Background job scaffolding (RQ) for CSV processing
- [x] UI/UX shell (Tailwind, global styles, navbar, dashboard cards)
  - [x] Restyled Upload page with Tailwind
  - [x] Branding: rename to craft_cost + logo + hero homepage
  - [x] Spend page wired to real read APIs (stub replaced)
  - [x] Read APIs: `GET /v1/transactions`, `GET /v1/spend/summary`
  - [x] Feature flags endpoint `/v1/flags`
  - [x] Minimal UI: Upload CSV form + list view (clean, minimal)

  - [x] Week 2 verified on 2025-09-30

## Week 3 — Read UX, Recategorization, Flags
- [ ] Recategorization endpoint `POST /v1/transactions/{id}/recategorize` (or `PATCH`)
- [ ] Spend UI polish
  - [ ] Filters: category, date range (last 7/30/90 days)
  - [ ] Loading states and skeletons
  - [ ] Cursor pagination wired to API
- [ ] React Query for data fetching/caching
- [ ] UI primitives in `packages/ui`: Button, Card, Input, Table
- [ ] Flags page `/flags` wired to `/v1/flags` (toggle + persist)
- [ ] Docs updates (README, RUNBOOK snippets for filters/flags)
- [ ] Week 3 verified on 2025-10-xx

Notes
- No mock/system-generated data until approved.
- Pipelines kept minimal for now; expand in Week 2–3.
- UI/UX research themes: simple card dashboard, primary CTA for CSV import, clear job/progress states, accessible forms, subtle contrast with dark surface, minimal color usage.
