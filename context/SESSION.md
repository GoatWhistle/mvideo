# Session state

Updated: 2026-10-14, MSK

## Explicit user instructions

- 2026-10-14: «нам нужно сделать репозиторий приватный в нашей github организации goatwhistle на основе шаблона который я дал, репу называй mvideo и там еще 3 файла с заданием»
- 2026-10-14: deadline «Завтра в 17:00» (2026-10-15 17:00); LLM — Claude API; demo stand — «Да, простой»; team roles — «Пока не важно».
- 2026-10-14: «вырази всё в issue» — plan lives as a spec issue with tickets.

## Current state

- Task: kickoff context (docs/kickoff) and data preparation (feat/data-prep) in parallel
- Branch and revision: see `git log -1`
- Stand: template only, nothing product-specific runs yet

## How to continue

Take the next unblocked ticket from the spec issue; data prep output lands in `data/processed/`.

## Pitfalls already hit

- Network ~110 KB/s: new Python dependencies download slowly; reuse the uv cache.
- ~6 GB free RAM: `skus.pkl` (1.5 GB pickle) must be parsed in a streaming way.
- zsh: `echo ===` fails (`=` expansion); quote it.

## Left, in order

1. Data prep, then baseline and EDA
2. Ranker, LLM tail, stand
3. Ablation, README, deck

## Red checks

None run yet.
