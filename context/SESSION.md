# Session state

Updated: 2026-10-15, MSK

## Current task

Implementation in separate branch `feat/automatic-catalog`; last code SHA from Git: `5cefc3e`.
Base: `747572d`. Parent spec and ten tickets are published in GoatWhistle/mvideo; implementation
progress and draft PR publication are next. No merge authorized. SQLite explicitly approved;
prepared dataset explicitly absent. No paid calls made.

Implemented: unit conversion; quote/negation/accessory guards and conflicts; full-field v2 metrics;
audit-catalog CLI; automatic category and streaming extraction; background Jev with two-call timeout,
cache and context retry; RU/EN UI with quotes, provenance/calibration status and JSON export;
SQLite migrations/seed, durable idempotent corrections, scoped aliases, automatic rerun and undo.
Decision cache includes current accepted/review fields so it cannot overwrite a fresh correction.

Validation: Ruff/mypy, 161 backend unit tests; 6 real SQLite/HTTP integration tests; frontend verify
(36 rules, 290 tests, build); 16 browser tests on local API/Vite and Compose/nginx, plus 12 scenario
tests after provenance UI fix. Matrix 375/1440, light/dark, RU/EN. Compose rebuilt at final code,
migrations/seed/healthy services passed; correction survived backend container restart; seed repeat
passed. Long 24k-character input/non-Latin/reduced-motion at 375/720 passed overflow/export check.
No actual 200% zoom audit. Independent UI review scored missing provenance fix resolved (ship at
that scope); documenter preserved neutral system and recorded pre-existing context placeholders.
Evidence and remaining limits: docs/evidence.md, docs/automatic-catalog.md, work/audits/.

Preview: isolated Compose project mvideo-automatic-check, frontend :8088, backend :8008,
SQLite named volume. Controlled offline override /private/tmp/mvideo-compose-check.yml.
Local earlier API :8000 PID 450 and Vite :5179 are still running; API lacks latest cache patch.
dbmate binary /private/tmp/mvideo-dbmate. Docker credentials helper hung; build succeeded with
isolated /private/tmp/mvideo-docker-config and explicit Docker socket (no credential changes).

Next: commit reconciled docs, push branch, create draft PR, publish verified status to all Issues;
keep parent, calibration/ablation and dataset-dependent acceptance open. CatBoost, calibration,
real audit/ablation, new predictions and full submission/deck verification remain incomplete.

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

- Run backend tools from backend/ and frontend tools from frontend/ (config roots matter).
- Git writes and local server/browser/Docker commands need escalation. REST gh api is reliable;
  GraphQL often times out. Use JSON files or body files, never interpolate multiline shell text.
- No paid calls during tests. Inject Settings() for stateless unit composition; runtime load_settings
  requires SQLite by default. Controlled stand uses DECISION_MODEL=lexical and LANGUAGE_MODEL=none.
- SQLite WAL is enabled in its own nontransactional dbmate migration. Setting WAL on concurrent
  connection entry caused a flaky lock; UoW now verifies WAL and uses BEGIN IMMEDIATE + busy_timeout.
- E2E fixtures read backend/tests/fixtures/catalog-card.json at runtime; static import breaks the
  isolated frontend Docker build. JSON dictionary imports use import attributes on Node 25.
- Impeccable launcher context failed writing ~/.impeccable cache; direct project context read.
  ui-ux-pro-max CSV missing. code-review skill absent; direct code review required.
- UI retains neutral existing tokens (no Refero style approved). Real quality remains unmeasured.
- Docs now describe SQLite; historical baseline is explicitly not evidence for the new version.
