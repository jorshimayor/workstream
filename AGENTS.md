# AGENTS.md

This repository is for Workstream, Flow's task evaluation and contribution infrastructure.

## Core Definition

Workstream manages project guides, task queues, submission packets, automated checks, reviewer routing, evaluation sprints, revision loops, contribution records, payment status, and reputation signals.

Workstream is how Flow measures, certifies, and coordinates useful human-agent work.

## Working Rules

- Keep wording consistent with `README.md`, `docs/glossary.md`, and `docs/architecture_lockdown.md`.
- Do not use old names such as "task-production control plane" or "Garden roadmap".
- Do not add extra sheets to `sheets/workstream_roadmap.xlsx`; the workbook must contain one sheet only: `WorkStream RoadMap`.
- Treat `sheets/workstream_roadmap.xlsx` as the primary spreadsheet export. The CSV is fallback only.
- If updating the roadmap, update both XLSX and CSV.
- Do not import XLSX into Google Sheets with "replace spreadsheet"; use a temporary sheet and copy only the roadmap tab.
- Prefer evidence-backed docs over vague product claims.
- Keep v0.1 focused on project guide -> task -> submission -> checks -> review -> revision -> contribution/payment/reputation records.
- Review decisions are only accept, needs revision, or reject.
- Frontend is locked as React + Vite + TypeScript.
- Backend API is locked as Python with FastAPI.
- Execution is async-first; do not document synchronous-first checkers or jobs.
- FastAPI background tasks are acceptable for simple local v0.1 jobs; use Celery or equivalent durable workers when retries, scheduling, isolation, or distributed execution are needed.
- Postgres is the record database.
- Local filesystem storage is acceptable only behind an object-storage abstraction compatible with R2/S3-style storage.
- Do not expand into blockchain settlement, marketplace, external source adapters, automated routing, or agent workspace until the internal loop is proven.

## Done Criteria

Before reporting completion:

- run a stale wording scan
- check markdown links
- verify the XLSX has one sheet only
- verify the current Workstream definition appears in README and sheet exports
- update related docs/templates/sheets together, not only one file
