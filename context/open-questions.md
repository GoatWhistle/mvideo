# Open questions

| ID | Question | Decision affected | Source to consult | Status |
|---|---|---|---|---|
| Q1 | Deadline, defense format and duration, jury criteria and weights? | Timeline, priorities, deck length | Platform «Задать вопрос», event page | open |
| Q2 | Case promises CSV/JSON with a labeled train/val part; archive has parquet + `skus.pkl`. Which part is the labeled one? | Training and evaluation design | Organizers | open |
| Q3 | Is there a human gold set per category, or do we build it? | R12 evaluation, effort | Organizers | open |
| Q4 | Exact list of mandatory attributes per category («точный перечень… вместе с датасетом» — not found in archive)? | Scope of extraction | Organizers | open |
| Q5 | Format of the predictions file (CSV/JSON schema, one row per card or per attribute)? | Artifact 5 | Organizers | open |
| Q7 | TypeSafe API key for Jev? | Decision stage | User | answered 2026-10-14: OpenRouter key |
| Q6 | May we use external LLM APIs, and is cost/latency measured by the jury? | Hybrid routing, R6 | Organizers | open |

## Assumptions pending answers

| ID | Assumption | Revisit when |
|---|---|---|
| Q2 | `*_search` params in `skus.pkl` are normalized filter attributes and serve as labels | Organizers name the labeled part |
| Q4 | Mandatory = brand, model + the most-used `*_search` attributes per category, ranked by click traffic | Official list arrives |
| Q5 | JSON Lines: one object per SKU with `{attribute: {value, confidence}}` | Official format arrives |
