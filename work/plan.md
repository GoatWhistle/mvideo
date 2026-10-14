# P0 plan

Source of truth for tickets: the quality spec and its native sub-issues in GoatWhistle/mvideo GitHub Issues. Decisions: `docs/adr/`. Durable acceptance criteria: `docs/extraction-quality.md`.
Deadline T = 2026-10-15 17:00 MSK.

## Quality review work order

The following order supersedes the original implementation waves below. It does not authorize concurrent workers or paid checks. Confirmed counterexamples and unmeasured risks are distinguished in the acceptance document.

| Wave | Deliverable | Actual blockers | Completion evidence |
| --- | --- | --- | --- |
| 1 | Unit-aware normalization | None | Correct conversions through extraction and evaluation |
| 1 | Bind quotes to the product attribute | None | Accessory, negation and conflict counterexamples handled |
| 1 | Automated audit of catalog labels and split overlap | None | Reproducible clusters, samples and overlap report; human review optional |
| 2 | Evaluate all required fields and candidate recall | Normalization | Correct denominators and separate availability/candidate/selection metrics |
| 3 | Repair weak attribute candidates | Evaluation, quote binding | Error taxonomy and per-attribute before/after on fixed splits |
| 3 | Background Jev with bounded automatic rechecks | Evaluation, quote binding | Automatic routing, abstention, validated responses and no-key operation |
| 4 | One-launch extraction with automatic category | Normalization, quote binding, Jev integration | Real progressive results, API/CLI parity, automatic fill and export |
| 4 | CatBoost baseline and calibrated acceptance | Candidate repairs, Jev integration | Precision/coverage, no-intervention share, end-to-end category quality |
| 5 | Exception-only corrections and suggested aliases | One-launch extraction | One-action fix, automatic rerun, persistence and rollback |
| 6 | Ablation and six submission artifacts | Automated audit, evaluation, feedback, calibration | Fresh-clone automatic demo; paid measurements only if explicitly requested |

User direction: Jev is background, the hackathon demo needs a visible wow effect, and manual work must be minimized. Automatic category detection and one-launch processing are P0; manual category input is only an ambiguity fallback. A 95% precision target remains a proposed protocol parameter, not an achieved result. A 120-pair manual audit is not a P0 gate; automated analysis must not be represented as independent human labels. Storage choice follows backend rules. A paid Jev evaluation remains separately authorized work.

## Original implementation plan

| Wave | Ticket | Acceptance (short) | Blocked by |
|---|---|---|---|
| 1 | Organizer questions Q1–Q6 | Sent, answers verbatim in brief/QA.md | — |
| 1 | Kickoff context | No placeholders, budget green, ADRs linked | — |
| 1 | Data prep | Key overlap counted; gold from `*_search` isolated by test; splits + held-out categories; required attributes with traffic weights | — |
| 2 | EDA | Notebook runs top to bottom; coverage before pipeline | Data prep |
| 2 | Baseline | predictions.jsonl with evidence; reproducible metrics report; validation plan fixed before run | Data prep |
| 3 | Ranker + calibration | Ablation gain, ECE, threshold curve | Baseline |
| 3 | Claude tail | No-hallucination test; LLM share and cost per 1M cards | Baseline |
| 3 | Stand | P0 scenario via compose without paid keys; feedback loop live | Baseline |
| 4 | Ablation + held-out categories | One command; final predictions file | Ranker, Claude tail |
| 5 | README + clean clone | All commands work from a fresh clone | Ablation, Stand |
| 5 | Deck + rehearsal | Numbers match evidence; risks slide; PDF | EDA, Ablation |

## Checkpoints

| When | Done |
|---|---|
| 2026-10-14 22:00 | Data, EDA draft, dictionaries, rules, first predictions and baseline metrics |
| 2026-10-15 06:00 | Ranker, calibration, Claude tail, ablation |
| 2026-10-15 12:00 | Stand, README |
| 2026-10-15 15:00 | Deck, timed rehearsal |
| 2026-10-15 16:00 | Fresh-clone run, submitted |

## Out of scope

Fine-tuned BERT/NER, images, running the whole catalog through the LLM.

## Implementation checkpoint, 2026-10-15

Branch `feat/automatic-catalog`: unit conversion and quote guards, full-field metrics, deterministic
audit, background decision with bounded context recheck, streaming one-launch screen and export
implemented. Runtime acceptance evidence and remaining gaps live in `docs/automatic-catalog.md`.
No real dataset rerun; CatBoost/calibration remain pending data. User selected SQLite; corrections, scoped aliases, automatic rerun and revoke are implemented
with migration/seed and real-storage integration tests. Do not close the parent spec as completed.
