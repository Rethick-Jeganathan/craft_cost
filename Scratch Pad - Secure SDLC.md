# Scratch Pad — Secure Software Development (Secure SDLC)

Project: craft_cost

Legend: [ ] Pending  [x] Completed  [-] In Progress

## 0) Policy, Governance, and Standards
- [x] Define target baseline (OWASP ASVS L2+, SOC2-lite guardrails per Project Plan)
- [x] Map features to ASVS controls (AuthZ, Data Protection, Input Validation, Logging/Audit)
- [x] Security review cadence (at least once per major module/week)
- [x] Add CODEOWNERS for security-critical files (API security, crypto, auth, webhooks)

## 1) Architecture & Threat Modeling
- [x] Document initial architecture and trust boundaries (`README.md` Mermaid diagram)
- [x] DFD and STRIDE per component (Web, API, Worker, PDF, DB, Redis, MinIO, MailHog)
- [x] Identify high-risk data flows (PII, tokens, webhooks) and apply mitigations
- [x] Capture assumptions and abuse cases (e.g., replayed webhooks, BOLA, mass assignment)

## 2) Dependencies & Supply Chain
- [x] Pin dependency versions (Python/Node)
- [x] Enable automated SCA bot (Renovate configured; CodeQL replaced with Semgrep in CI due to Bitbucket)
- [x] Add SCA in CI (npm audit/pip-audit gates)
- [x] Verify license policy compliance

## 3) Secrets & Key Management
- [x] `.env.example` present; no real secrets committed
- [x] AES-GCM field-level encryption utility (`apps/api/app/security/crypto.py`)
- [x] `AES_GCM_KEY` placeholder added to `.env.example`
- [ ] Production: configure KMS-managed keys and rotation procedures [moved to Future]
- [x] Secrets scanning in CI (gitleaks)

## 4) Authentication & Authorization
- [ ] Adopt NextAuth.js (sessions, secure cookies) with session rotation
- [ ] Server-side entitlements checks (plan-based) and OPA-style policy points for sensitive ops
- [ ] Object-level authorization checks (avoid BOLA)
- [ ] Admin-only endpoints guarded and audited

## 5) Data Protection & Privacy
- [x] App-layer AES-GCM for selected PII fields
- [ ] Encrypt sensitive columns at rest (expand coverage, consider pgcrypto/KMS for prod)
- [ ] S3/MinIO bucket policies and presigned URL TTLs hardened
- [x] Data retention enforcement (90-day on raw transactions) – dev job + admin trigger
- [ ] Data export/delete endpoints with audit trail

## 6) Input Validation & Output Encoding
- [x] Pydantic models for API; Zod planned for UI
- [ ] Strict length/type patterns for IDs and tokens
- [ ] Sanitize/escape user-provided HTML/file names (no untrusted HTML to PDF)
- [ ] Disable/mitigate XXE, SSRF sources; restrict egress

## 7) API Security
- [x] Consistent error model `{error:{code,message,details?}}` (documented; implement fully in handlers later)
- [x] `idempotency` table created; Idempotency-Key pattern planned
- [ ] Enforce Idempotency-Key on mutating endpoints [moved to Future]
- [x] Rate limits (Redis-backed) – minimal per-IP per-route limiter (dev)
- [ ] Pagination cursors hardened and bounded [moved to Future]
- [ ] Request/response size limits [moved to Future]

## 8) Web UI Security
- [x] Security headers in Web (`apps/web/next.config.js`): HSTS, CSP (baseline), Referrer/Permissions
- [ ] Harden CSP (nonce/strict-dynamic) [moved to Future]
- [x] CORS: restrict origins per environment (now configurable via CORS_ALLOW_ORIGINS)
- [ ] CSRF protection for cookie workflows [moved to Future]
- [ ] Client-side PII redaction and safe rendering [moved to Future]

## 9) Integrations & Webhooks (Stripe, Plaid, SendGrid)
- [x] Basic HMAC signature verification scaffolds for Stripe/Plaid (dev-only)
- [ ] Idempotency-Key per event; delivery attempts/outcomes [moved to Future]
- [ ] Event allowlist; reject unknown [moved to Future]
- [ ] Time sync checks and strict content-type [moved to Future]

## 10) Background Jobs & Queues
- [ ] Validate job payloads and audit logging [moved to Future]

## 11) Documents & PDFs
- [ ] PDF sandboxing & sanitization & storage hardening [moved to Future]

## 12) Logging, Monitoring, and Auditing
- [x] JSON logs + request_id middleware in API; baseline security headers
- [ ] Centralize logs; structured fields (user_id)
- [x] Basic header redaction (Authorization/Cookie); broader PII redaction policy – Future
- [ ] Sentry/alerts and basic /metrics endpoints
- [x] `audit_events` table created; ensure coverage for consent, exports, deletes

## 13) Infrastructure & Container Security
- [x] Containers run as non-root (api/web/worker/pdf)
- [ ] Capability drops / seccomp profiles – Future
- [ ] Network segmentation beyond Compose defaults [moved to Future]
- [ ] Image hardening and SBOMs [moved to Future]
- [ ] MinIO bucket policies [moved to Future]

## 14) Testing & Verification
- [x] SAST (Semgrep) in CI for API/Web
- [ ] DAST smoke (OWASP ZAP baseline) [moved to Future]
- [-] Security tests (authz/rate limits/idempotency) – minimal added; expand later
- [ ] Fuzzing for CSV ingestion [moved to Future]

## 15) Deployment & Operations
- [ ] Staging/prod config separation [moved to Future]
- [ ] Backup & restore drills [moved to Future]
- [ ] Rollback and blue/green guidance [moved to Future]

## 16) Incident Response
- [ ] IR contacts/workflow & playbooks [moved to Future]

---

## Future Security (Backlog)
- Automated SCA bot (Renovate/Dependabot) and license compliance
- Production-grade key management (KMS) and rotation
- Idempotency-Key enforcement on mutating endpoints
- Rate limits and request/response size limits
- Hardened pagination cursors
- CSP hardening, CSRF protections, client-side PII redaction
- Webhook signatures, replay protection, event allowlist, time sync
- Job payload validation, per-job audit logging
- PDF sandboxing/sanitization, storage policies
- Container user/capabilities, network segmentation, image hardening, SBOMs, MinIO policies
- DAST baseline (OWASP ZAP), fuzzing targeted at CSV ingestion
- Staging/prod config separation, backups/restores, rollout strategies
- IR contacts, playbooks, and post-incident processes

---

## Current Status Snapshot (Week 1)
- [x] Security headers (API + Web) in place
- [x] AES-GCM crypto utility and env placeholder present
- [x] Idempotency and audit tables created via initial migration
- [x] Rate limiting implemented (dev minimal)
- [x] Webhook signature verification scaffolds present (dev)
- [x] CI security scanners: SAST (Semgrep) + SCA (npm audit/pip-audit) configured; DAST planned
- [x] Containers run as non-root (basic); capabilities/seccomp hardening – Future

## Action Queue (Next Suggested Security Steps)
- [x] Add Renovate for npm/pip (CI); CodeQL replaced with Semgrep in CI
- [x] Implement Redis-backed rate limiting middleware for API
- [x] Restrict CORS to localhost dev and configured prod origins
- [x] Add webhook signature verification scaffolds for Stripe/Plaid
- [x] Run containers as non-root (basic)
- [x] Add log redaction middleware and request_id propagation
- [x] Define retention enforcement job for `transactions_raw` (90 days)
