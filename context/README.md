# Project context

Project: mvideo (working name) — attribute extraction from product cards
Hackathon and track: «Точка сборки» (GIGASCHOOL), task 3, case owner М.Видео
Deadline: 2026-10-15 17:00 MSK
P0 scenario: paste a card → attributes with value, confidence, quote and source → low-confidence value goes to the review queue → correction adds an alias → rerun is confident

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
| Final metrics | verified | test+new_category micro F1 77.5 (baseline 66.8), weighted 80.6, coverage 79.0%, ECE 0.021 | reports/final.md, 2026-10-15 |
| Artifacts | implemented | README, EDA, pipeline, predictions (data/predictions, outside git), deck (presentation/dist) | docs/requirements-map.md |
| Tracker | approved | Spec and tickets in GitHub Issues of GoatWhistle/mvideo | .claude/tracker.md |

## Pointers

- [Session](SESSION.md)
- [Open questions](open-questions.md)
- [Organizer materials](../brief/README.md)
- [Working artifacts](../work/README.md)
- [Product documentation](../docs/README.md)
