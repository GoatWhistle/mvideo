# Session state

Updated: 2026-10-15 03:00 MSK

## Explicit user instructions

- 2026-10-14: «нам нужно сделать репозиторий приватный в нашей github организации goatwhistle на основе шаблона который я дал, репу называй mvideo и там еще 3 файла с заданием»
- 2026-10-14: deadline «Завтра в 17:00» (2026-10-15 17:00); LLM — Claude API; demo stand — «Да, простой»; team roles — «Пока не важно».
- 2026-10-14: «вырази всё в issue» — plan lives as a spec issue with tickets.
- 2026-10-14: «а модели типа jev typesafe, openjev, laya сюда ложатся?» → «ок»: decision model (Jev) picks among candidates; CatBoost for ablation; Claude fallback.
- 2026-10-14: Jev via OpenRouter key; «jev используй максимально эффективно чтобы увелить метрики, но оставб бюджет на стенд» (limited inference key $2.5, ~$0.64 spent).
- 2026-10-14: «будь аккуратние с озу и cpu, а то доступ пропадет» — ≤~6 cores / ≤~8 GB total, nice, ≤3 shard processes.
- 2026-10-14: stand review queue storage — «in memory».
- 2026-10-14: category inference and catalog twins (TF-IDF, not neural embeddings) approved.

## Current state

- Done and merged: data prep, EDA, baseline, ranker, Jev stage, twins, categories, fusion, stand, deck, README
- In progress: twins for all cards and on the stand (feat/twins-all, worker)
- Final test metrics: micro F1 66.8 → 77.5, weighted 76.4 → 80.6, coverage 25.9% → 79.0%, ECE 0.021 (reports/final.md)
- Built deck: presentation/dist/ (local, not in git)

## How to continue

After twins-all merges: update coverage numbers in README, docs/for-jury.md, docs/limitations.md, deck slide 10; rebuild deck; fresh-clone run; submission scrub. Open user decisions: product name («Атрибут» in deck vs «Атрибуты товаров» in README/stand), team name on cover, QR to private repo (public / access / remove), talk minutes, speakers.

## Pitfalls already hit

- Network ~110 KB/s: new Python dependencies download slowly; reuse the uv cache.
- ~6 GB free RAM: `skus.pkl` (1.5 GB pickle) must be parsed in a streaming way.
- zsh: `echo ===` fails (`=` expansion); a variable named `path` overwrites PATH.
- OpenRouter management key cannot run inference; Jev id is `typesafe/jev-1.13` on `/api/v1/systemone`.
- Other projects on the host (vitest, rustc) drive load to 15–19; our jobs stay niced.

## Left, in order

1. Twins for all cards and stand, then coverage numbers in docs and deck
2. User decisions: name, QR/repo visibility, minutes, speakers
3. Fresh-clone run, backup demo recording, submission scrub and tag

## Red checks

None known; full prepare-data and Docker build not re-run from a fresh clone.
