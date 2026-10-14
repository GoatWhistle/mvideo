# P0 plan

Source of truth for tickets: the spec issue in GoatWhistle/mvideo GitHub Issues. Decisions: `docs/adr/`.
Deadline T = 2026-10-15 17:00 MSK.

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
