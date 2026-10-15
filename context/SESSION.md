# Session state

Updated: 2026-10-15, checkpoint push

## Explicit user instructions

- 2026-10-14: «нам нужно сделать репозиторий приватный в нашей github организации goatwhistle на основе шаблона который я дал, репу называй mvideo и там еще 3 файла с заданием»
- 2026-10-14: deadline «Завтра в 17:00» (2026-10-15 17:00); LLM — Claude API; demo stand — «Да, простой»; team roles — «Пока не важно».
- 2026-10-14: «вырази всё в issue» — plan lives as a spec issue with tickets.
- 2026-10-14: «а модели типа jev typesafe, openjev, laya сюда ложатся?» → «ок»: decision model (Jev) picks among candidates; CatBoost for ablation; Claude fallback.
- 2026-10-14: Jev via OpenRouter key; «jev используй максимально эффективно чтобы увелить метрики, но оставб бюджет на стенд» (limited inference key $2.5, ~$0.64 spent).
- 2026-10-14: «будь аккуратние с озу и cpu, а то доступ пропадет» — ≤~6 cores / ≤~8 GB total, nice, ≤3 shard processes.
- 2026-10-14: stand review queue storage — «in memory».
- 2026-10-14: category inference and catalog twins (TF-IDF, not neural embeddings) approved.
- 2026-10-15: «изучи ваще че как с решением. смотри в две ветки. прям изучи братец»
- 2026-10-15: «подними мне это все»

Additional instructions preserved in origin/feat/automatic-catalog:
- 2026-10-14: «посмотри скилл для работы с issue и оформи все претензии внутрь issue и туда пиши что есть шас и что будет и что мы получаем на выход»
- 2026-10-14: «jev фоновый, очевидно что мы хотим вау эффекта для хакатона»
- 2026-10-14: «минимум ручности больше работы автоматом»
- 2026-10-14: «делай»; «в отедльной ветке»
- 2026-10-15: «SQLite — для текущего стенда»
- 2026-10-15: prepared dataset availability: «нету»

## Current state

- Code unchanged. Branch docs/first-checkpoint, base main 331ea2f.
- Fetched origin; other branch origin/feat/automatic-catalog 347a9bb. Common ancestor 626a7c1;
  main has 9 unique commits, automatic has 10. Detached worktree: .local/automatic-catalog.
- main contains final fusion, category inference, twins for all cards and stand, reports and deploy.
  Historical reports: F1 66.8 → 77.5, weighted 76.4 → 80.6, pair coverage 79.0%, ECE 0.0205;
  25,550 eval cards. final_all reports 1,177,200 cards, 131,584 without attributes. Not rerun here.
- Automatic branch adds unit/evidence guards, complete required-field accounting, category keyword
  routing, JSONL extraction, optional background Jev, SQLite feedback/undo/scoped aliases and CLI.
  Default catalog is synthetic, two categories. New ProcessCard uses rules + Jev, not CatBoost/fusion;
  confidence is null. Legacy /manual uses BaselineChooser. No new real-dataset metrics/calibration.
- Reproduced on both heads: main maps seller weight 500 г to 500 кг, treats 1 г and 1 кг as equal,
  and drops required fields lacking a profile; automatic fixes all three. Main report validity must
  be qualified; correction impact is unmeasured. Main twins use SKU provenance with offsets -1,
  conflicting with the quote-only ADR. SKU split does not isolate product families.
- Read-only merge-tree reports 12 conflicted files, including model/training/pack code, Compose,
  README and docs. No merge started. Automatic lacks the later main fusion/category/deploy commits.
- Both Compose stands stopped at user request «останови все»: automatic port 8088 (API 8008), main
  port 8089 (API 8009). Projects mvideo-auto-local and mvideo-main-local. Docker Desktop
  started. Automatic SQLite volume mvideo-auto-local_catalog-data retains feedback. Paid models off.
  Explicit synthetic packs: 2 categories/2 examples; real data and trained models unavailable.
  Local start/stop scripts and overrides: data/local-runtime/. Backend images reused installed
  CatBoost from calibr-backend, then uv sync --locked reconciled every dependency with branch locks.
  Backend limits 2 CPUs/2 GB each, frontend 0.5 CPU/128 MB. Other projects left running.

## How to continue

Created presentation/dist/deck.pdf and deck.html: 9 slides, Q1–Q5, UI prototype at Q3; old uploads
and output/tmp copies removed. Speech: presentation/SPEECH.md. Artifacts unignored. PDF rendered
and inspected; Chrome export passed. speech:check still fails: missing presentation numbers.json.
Next: merge corrected extraction with ML, re-evaluate on real data; 77.5 F1 is not ProcessCard evidence.
Telegram checked: Oct 15 16:59 MSK is the product brief deadline, code optional; PDF ≤10 slides,
public link, five numbered answers and UI prototype at Q3. Exact sources: brief/QA.md.
Submission, name, speakers/timing and repo access unresolved.

## Pitfalls already hit

- Network ~110 KB/s: new Python dependencies download slowly; reuse the uv cache.
- ~6 GB free RAM: `skus.pkl` (1.5 GB pickle) must be parsed in a streaming way.
- zsh: `echo ===` fails (`=` expansion); a variable named `path` overwrites PATH.
- OpenRouter management key cannot run inference; Jev id is `typesafe/jev-1.13` on `/api/v1/systemone`.
- Other projects on the host (vitest, rustc) drive load to 15–19; our jobs stay niced.

## Left, in order

1. Review the branch investigation and agree on the implementation scope.
2. Integration and re-evaluation require real dataset/model artifacts.
3. Verify submission artifacts and live demo against the chosen version.

## Red checks

Frontend verify passed both heads (automatic: 300 tests); selected Python domain/usecase checks:
main 88 (pyarrow-dependent stand_twins excluded), automatic 105. Initial reduced environment lacked
anyio/pyarrow; reruns added anyio. Full backend suite/mypy/Ruff and dataset metrics not repeated.
Startup checks: both HTTP health/extraction passed; automatic weight/RAM/conflict correction,
SQLite persistence through backend restart and undo passed. All 16 automatic browser tests passed
using installed Chrome via data/local-runtime/playwright.config.mjs; bundled Chromium was missing.
Main presentation build failed: ignored presentation/src/data/numbers.json is absent; not repaired.
