# Session state

Updated: 2026-10-15, MSK

## Current task

Implementation in separate branch `feat/automatic-catalog`; functional SHA from Git: `e854c91`.
Main `626a7c1` merged into this branch, preserving upstream CatBoost/isotonic, batch Jev/twins,
legacy sync API and reports. Draft PR https://github.com/GoatWhistle/mvideo/pull/35 is open.
Parent spec and ten tickets published; verified progress updated. Main has not been merged.
SQLite approved; prepared dataset absent. No paid calls made in this task; upstream reports are
historical evidence only and cannot establish quality after unit and metric changes.

Implemented: unit conversion; quote/negation/accessory guards and conflicts; full-field v2 metrics;
audit-catalog CLI; automatic category and streaming extraction; background Jev with two-call budget,
cache and context retry; RU/EN UI with quotes, provenance/calibration status, duration, cancellation
and JSON export; SQLite migrations/seed, durable idempotent corrections, scoped aliases, rerun/undo.
Decision cache includes accepted/review fields so it cannot overwrite a fresh correction.
Offline extract-product CLI shares ProcessCard and SQLite with API; integration compares outputs.

Compatibility: root automatic screen uses /api/v1/extract/stream; upstream /api/v1/extract remains
synchronous, /manual retains old screen with STAND_PACK and temporary review state. New screen has
no calibrated confidence and excludes quote-free twins. Upstream experiments are preserved offline.

Validation at e854c91: Ruff check/format, mypy; 205 unit + 7 integration tests; frontend verify
(36 rules, 300 tests, build); 16 browser tests on Compose, matrix375/1440 × light/dark × RU/EN,
axe, cancellation/new run, quotes/export, feedback/undo/alias. Independent review disposition ship
for final cancellation/duration additions and earlier provenance fix only, not whole-surface approval.
Documenter confirmed existing system preserved. Evidence: docs/evidence.md, work/audits/.
Clean clone /private/tmp/mvideo-clean-check rebuilt without .env, real volume migrated/seeded,
healthchecks and HTTP scenario passed; CLI also ran in its container. Previous restart/seed-repeat
checks passed. Long24k/non-Latin/reduced-motion checked at375/720; full200%zoom not checked.

Preview: http://localhost:8088 (backend8008), isolated mvideo-automatic-check project, SQLite volume,
offline override /private/tmp/mvideo-compose-check.yml. Local Vite5179/API8000 stopped.
Temporary clean-check projects8089/8009 and8090/8010 stopped after verification; volumes retained.
Docker uses isolated /private/tmp/mvideo-docker-config and explicit user Docker socket because
credential helper hung. No user credentials changed. dbmate: /private/tmp/mvideo-dbmate.
Final screenshots: /private/tmp/mvideo-ui-evidence-final.

Next: review draft PR; remaining work needs dataset: new audit, fair before/after, refit/calibrate
final automatic cascade, end-to-end quality/ablation and predictions. Defense/six-artifact acceptance
remains open. Do not substitute old reports or synthetic tests for real-catalog quality.

## Explicit user instructions

- 2026-10-14: «нам нужно сделать репозиторий приватный в нашей github организации goatwhistle на основе шаблона который я дал, репу называй mvideo и там еще 3 файла с заданием»
- 2026-10-14: deadline «Завтра в 17:00» (2026-10-15 17:00); LLM — Claude API; demo stand — «Да, простой»; team roles — «Пока не важно».
- 2026-10-14: «вырази всё в issue» — plan lives as a spec issue with tickets.
- 2026-10-14: «а модели типа jev typesafe, openjev, laya сюда ложатся?» → «ок»: decision model (Jev) picks among candidates; CatBoost for ablation; Claude fallback.
- 2026-10-14: «посмотри скилл для работы с issue и оформи все претензии внутрь issue и туда пиши что есть шас и что будет и что мы получаем на выход»
- 2026-10-14: «jev фоновый, очевидно что мы хотим вау эффекта для хакатона»
- 2026-10-14: «минимум ручности больше работы автоматом»

- 2026-10-14: «делай»; «в отедльной ветке»
- 2026-10-15: «SQLite — для текущего стенда»
- 2026-10-15: prepared dataset availability: «нету»

## Pitfalls

- Run backend/frontend commands from their folders. Git writes, local browser/server/Docker need
  escalation. gh REST works; GraphQL unreliable. Use body files for multiline content.
- No paid calls during tests. Runtime uses SQLite; unit composition Settings() is stateless.
- WAL enabled by separate dbmate migration; UoW verifies it and uses BEGIN IMMEDIATE + busy_timeout.
- E2E fixture JSON is read at runtime, not statically imported (isolated Docker frontend build).
- Impeccable cache uses writable temp path. ui-ux-pro-max CSV and code-review skill absent;
  direct checks recorded. PRODUCT/DESIGN placeholders predate this work, no brand approved.
- Ruff formatting applied in a separate commit; decision Markdown renderer split to keep≤250lines.
