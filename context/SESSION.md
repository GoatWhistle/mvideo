# Session state

Updated: 2026-10-14, MSK

## Explicit user instructions

- 2026-10-14: «нам нужно сделать репозиторий приватный в нашей github организации goatwhistle на основе шаблона который я дал, репу называй mvideo и там еще 3 файла с заданием»
- 2026-10-14: deadline «Завтра в 17:00» (2026-10-15 17:00); LLM — Claude API; demo stand — «Да, простой»; team roles — «Пока не важно».
- 2026-10-14: «вырази всё в issue» — plan lives as a spec issue with tickets.
- 2026-10-14: «а модели типа jev typesafe, openjev, laya сюда ложатся?» → «ок»: decision model (Jev) picks among candidates; CatBoost for ablation; Claude fallback.

## Current state

- Done: kickoff, data prep, EDA (merged to main)
- In progress: baseline (feat/baseline, worker); ADR update for decision model (docs/decision-model)
- Stand: template only

## How to continue

After the baseline PR: ranker + calibration and Jev choice stage in parallel, then stand. Need a TypeSafe API key (open question Q7).

## Pitfalls already hit

- Network ~110 KB/s: new Python dependencies download slowly; reuse the uv cache.
- ~6 GB free RAM: `skus.pkl` (1.5 GB pickle) must be parsed in a streaming way.
- zsh: `echo ===` fails (`=` expansion); quote it.

## Left, in order

1. Baseline
2. CatBoost ranker, Jev choice stage, stand
3. Ablation, README, deck

## Red checks

None run yet.
