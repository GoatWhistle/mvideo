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
| Approach | approved | Cascade dictionaries → rules → CatBoost ranker → Claude Haiku on tail; quote required | docs/adr/0002 |
| Stand | approved | One page, no auth, real pipeline | docs/adr/0005 |
| Tracker | approved | Spec and tickets in GitHub Issues of GoatWhistle/mvideo | .claude/tracker.md |

## Pointers

- [Session](SESSION.md)
- [Open questions](open-questions.md)
- [Organizer materials](../brief/README.md)
- [Working artifacts](../work/README.md)
- [Product documentation](../docs/README.md)
