# Project context

Project: mvideo (working name) — attribute extraction from product cards
Hackathon and track: «Точка сборки» (GIGASCHOOL), task 3, case owner М.Видео
Deadline: 2026-10-15 17:00 MSK
P0 scenario: paste a card once → automatic category and extraction → background Jev and bounded automatic rechecks → filled card with quotes and export → only unresolved exceptions need a correction → suggested scoped alias and automatic rerun. Implemented scenario and remaining evaluation limits: `docs/automatic-catalog.md`.

## Current facts

| Topic | Status | Current fact | Evidence |
|---|---|---|---|
| Task | approved | Six artifacts: code, README, EDA, pipeline, predictions file, deck; one repo; runs from README | brief/PLATFORM.md, 2026-10-14 |
| Data | verified | sku_desc 1.18M (sku_id, title, description); query_clicks 31M; skus.pkl = YML catalog dict, no executable opcodes | data/raw, 2026-10-14 |
| Gold | approved (assumption) | `*_search` params are labels, excluded from input | docs/adr/0001, Q2 |
| Approach | approved | Candidates with quotes (dictionaries, rules) → TypeSafe Jev picks via `DecisionModel` port with probabilities → threshold → review queue; CatBoost = ablation baseline; Claude only fallback | docs/adr/0002, 0003, 2026-10-14 |
| Stand | approved | One page, no auth, real pipeline | docs/adr/0005 |
| Data prep | implemented | `uv run prepare-data` → data/processed (cards, gold, splits, required_attributes); gold+text 241k cards; 661 s, 5.2 GB peak | docs/running.md |
| EDA | verified | Gold value verbatim in text for 58% required pairs (brand/model 96–99%, color 26%, weight 3%); seller params are ranges; spec block only ~8k gold cards | notebooks/eda.ipynb |
| Tracker | approved | Spec and tickets in GitHub Issues of GoatWhistle/mvideo | .claude/tracker.md |

| Storage | verified on stand | SQLite approved 2026-10-15; correction survives container restart, scoped alias and undo pass real API tests | docs/adr/0006-sqlite-feedback.md, docs/evidence.md |

## Pointers

- [Session](SESSION.md)
- [Open questions](open-questions.md)
- [Organizer materials](../brief/README.md)
- [Working artifacts](../work/README.md)
- [Product documentation](../docs/README.md)
