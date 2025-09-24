# Scratch Pad — Secure Software Development (Secure SDLC)

Project: Debt & Expense Reduction Advisor

Legend: [ ] Pending  [x] Completed  [-] In Progress

## 0) Policy, Governance, and Standards
- [x] Define target baseline (OWASP ASVS L2+, SOC2-lite guardrails per Project Plan)
- [ ] Map features to ASVS controls (AuthZ, Data Protection, Input Validation, Logging/Audit)
- [ ] Security review cadence (at least once per major module/week)
- [ ] Add CODEOWNERS for security-critical files (API security, crypto, auth, webhooks)

## 1) Architecture & Threat Modeling
- [x] Document initial architecture and trust boundaries (`README.md` Mermaid diagram)
- [ ] DFD and STRIDE per component (Web, API, Worker, PDF, DB, Redis, MinIO, MailHog)git a
- [ ] Identify high-risk data flows (PII, tokens, webhooks) and apply mitigations
- [ ] Capture assumptions and abuse cases (e.g., replayed webhooks, BOLA, mass assignment)

## 2) Dependencies & Supply Chain
- [x] Pin dependency versions (Python/Node)
- [ ] Enable automated SCA (e.g., Dependabot for npm/pip, or Renovate)
- [ ] Add vulnerability scanning to CI (e.g., Trivy for images, npm audit/pip-audit gates)
- [ ] Verify license policy compliance

## 3) Secrets & Key Management
- [x] `.env.example` present; no real secrets committed
- [x] AES-GCM field-level encryption utility (`apps/api/app/security/crypto.py`)
- [x] `AES_GCM_KEY` placeholder added to `.env.example`
- [ ] Production: configure KMS-managed keys and rotation procedures
- [ ] Secrets scanning in CI/pre-commit (e.g., gitleaks)

## 4) Authentication & Authorization
- [ ] Adopt NextAuth.js (sessions, secure cookies) with session rotation
- [ ] Server-side entitlements checks (plan-based) and OPA-style policy points for sensitive ops
- [ ] Object-level authorization checks (avoid BOLA)
- [ ] Admin-only endpoints guarded and audited

## 5) Data Protection & Privacy
- [x] App-layer AES-GCM for selected PII fields
- [ ] Encrypt sensitive columns at rest (expand coverage, consider pgcrypto/KMS for prod)
- [ ] S3/MinIO bucket policies and presigned URL TTLs hardened
- [ ] Data retention enforcement (90-day on raw transactions) and deletion jobs
- [ ] Data export/delete endpoints with audit trail

## 6) Input Validation & Output Encoding
- [x] Pydantic models for API; Zod planned for UI
- [ ] Strict length/type patterns for IDs and tokens
- [ ] Sanitize/escape user-provided HTML/file names (no untrusted HTML to PDF)
- [ ] Disable/mitigate XXE, SSRF sources; restrict egress

## 7) API Security
- [x] Consistent error model `{error:{code,message,details?}}` (documented; implement fully in handlers later)
- [x] `idempotency` table created; Idempotency-Key pattern planned
- [ ] Enforce Idempotency-Key on mutating endpoints
- [ ] Rate limits (Redis-backed) for endpoints and LLM suggestions
- [ ] Pagination cursors hardened and bounded
- [ ] Request/response size limits

## 8) Web UI Security
- [x] Security headers in Web (`apps/web/next.config.js`): HSTS, CSP (baseline), Referrer/Permissions
- [ ] Harden CSP (script-src nonce/strict-dynamic; block remote fonts/images where possible)
- [ ] CORS: restrict origins per environment (dev only wildcard currently)
- [ ] CSRF protection for state-changing actions (if using cookies)
- [ ] Client-side PII redaction and safe rendering

## 9) Integrations & Webhooks (Stripe, Plaid, SendGrid)
- [ ] Verify webhook signatures (tolerance windows, replay protection)
- [ ] Enforce Idempotency-Key per event; store delivery attempts/outcomes
- [ ] Use allowlist for event types; reject unknown
- [ ] Time sync checks (skew tolerance) and strict content-type handling

## 10) Background Jobs & Queues
- [ ] Validate all job payloads; deny deserialization of untrusted types
- [ ] Idempotent job design; retries with backoff; dead-letter queue pattern
- [ ] Egress/network policies for workers; least-privileged service accounts
- [ ] Per-job audit logging (export, delete, ETL actions)

## 11) Documents & PDFs
- [ ] Sandbox PDF rendering (no remote resources; resource/time limits; non-root user)
- [ ] Sanitize all user-provided strings before rendering (no HTML injection)
- [ ] Store PDFs with private ACL; presigned short TTL; watermark in non-prod

## 12) Logging, Monitoring, and Auditing
- [x] JSON logs planned; headers middleware in API
- [ ] Centralize logs; structured fields (user_id, request_id)
- [ ] Redact PII at log sinks; enforce logging policy
- [ ] Sentry/alerts and basic /metrics endpoints
- [x] `audit_events` table created; ensure coverage for consent, exports, deletes

## 13) Infrastructure & Container Security
- [ ] Run services as non-root; read-only rootfs when possible
- [ ] Drop Linux capabilities; enable seccomp/apparmor profiles if available
- [ ] Network segmentation: restrict inter-service connectivity beyond Compose defaults
- [ ] Image hardening: slim bases, regular CVE scanning, SBOMs
- [ ] Minimal permissions for MinIO buckets

## 14) Testing & Verification
- [ ] SAST (CodeQL or Semgrep) in CI for API/Web
- [ ] DAST smoke (e.g., OWASP ZAP baseline) in CI against dev/staging
- [ ] Security unit/integration tests (authz, rate limits, idempotency)
- [ ] Fuzzing targeted at parsers (CSV ingestion)

## 15) Deployment & Operations
- [ ] Separate staging/prod configs; secrets via env/manager; no fallbacks
- [ ] Backup & restore drills for Postgres/MinIO
- [ ] Rollback and blue/green guidance in `RUNBOOK.md`

## 16) Incident Response
- [ ] Document IR contacts and on-call workflow
- [ ] Playbooks for key incidents (secrets exposure, webhook abuse, data deletion mishap)
- [ ] Post-incident review template and action tracking

---

## Current Status Snapshot (Week 1)
- [x] Security headers (API + Web) in place
- [x] AES-GCM crypto utility and env placeholder present
- [x] Idempotency and audit tables created via initial migration
- [ ] Rate limiting not yet implemented (planned Week 4)
- [ ] Webhook signature verification not yet implemented (planned with integrations)
- [ ] CI security scanners (SAST/SCA/DAST) not yet configured
- [ ] Container hardening not yet applied (non-root user, capabilities, seccomp)

## Action Queue (Next Suggested Security Steps)
- [ ] Add Dependabot/renovate for npm/pip and CodeQL (CI)
- [ ] Implement Redis-backed rate limiting middleware for API
- [ ] Restrict CORS to localhost dev and configured prod origins
- [ ] Add webhook signature verification scaffolds for Stripe/Plaid
- [ ] Run containers as non-root and add resource limits
- [ ] Add log redaction middleware and request_id propagation
- [ ] Define retention enforcement job for `transactions_raw` (90 days)
