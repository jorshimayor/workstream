# AGENTS.md

This repository is for Workstream, Flow's task evaluation and contribution infrastructure.

## Core Definition

Workstream manages project guides, task queues, submission packets, automated checks, reviewer routing, evaluation sprints, revision loops, contribution records, payment status, and reputation signals.

Workstream is how Flow measures, certifies, and coordinates useful human-agent work.

## Working Rules

- Keep wording consistent with `README.md`, `docs/glossary.md`, and `docs/architecture_lockdown.md`.
- Do not use old names such as "task-production control plane" or "Garden roadmap".
- Spreadsheet exports live locally under ignored `sheets/`; do not commit them.
- Do not add extra sheets to local `sheets/workstream_roadmap.xlsx`; the workbook must contain one sheet only: `WorkStream RoadMap`.
- Treat local `sheets/workstream_roadmap.xlsx` as the primary spreadsheet export. The CSV is fallback only.
- If updating the roadmap, update both local XLSX and CSV exports.
- Do not import XLSX into Google Sheets with "replace spreadsheet"; use a temporary sheet and copy only the roadmap tab.
- Prefer evidence-backed docs over vague product claims.
- Keep v0.1 focused on project guide -> task -> submission -> checks -> review -> revision -> contribution/payment/reputation records.
- Review decisions are only accept, needs revision, or reject.
- Frontend is locked as React + Vite + TypeScript.
- Backend API is locked as Python with FastAPI.
- ORM, migrations, and API schemas are locked as SQLAlchemy 2.x async + Alembic + Pydantic schemas.
- Workstream verifies external Flow authentication tokens; do not add Workstream-owned login, signup, password reset, password storage, or primary auth sessions.
- Week 1 implementation is backend-first; do not start frontend work until backend contracts and lifecycle guards are stable.
- Execution is async-first; do not document synchronous-first checkers or jobs.
- FastAPI background tasks are acceptable for simple local v0.1 jobs; use Celery or equivalent durable workers when retries, scheduling, isolation, or distributed execution are needed.
- Postgres is the record database.
- Local filesystem storage is acceptable only behind an object-storage abstraction compatible with R2/S3-style storage.
- Do not expand into blockchain settlement, marketplace, external source adapters, automated routing, or agent workspace until the internal loop is proven.

## Done Criteria

Before reporting completion:

- run a stale wording scan
- check markdown links
- verify the local XLSX has one sheet only when local sheet exports are present
- verify the current Workstream definition appears in README and local sheet exports when local sheet exports are present
- update related docs/templates and local sheet exports together when the roadmap changes
