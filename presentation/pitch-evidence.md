# Defense evidence: Атрибут

Every claim on a slide, in the speech, in the video or in an answer has a row here. No row, no
claim. Product-level proofs (reports, test runs, measurements) live in `../docs/evidence.md`;
link to them instead of copying.

Statuses:

- **Live, date**: checked on the running product or stand, with the version.
- **Code + tests**: implemented and covered by automated tests; no live run for this claim.
- **Not ready**: absent, or present but not accepted live. On slides it appears as "in progress".

Version: `main` at 8bb7399 (fusion merged), 2026-10-15. Stand: local Compose, not hosted.

## Claims

| # | Claim | Status | Proof | Slide | On the demo |
| ---: | --- | --- | --- | --- | --- |
| 1 | Every accepted value carries a quote cut from the card text | Code + tests | `test_candidates_carry_quotes_and_pick_expected_values`, `../docs/evidence.md` | 3, 4, 7 | quotes highlighted |
| 2 | `*_search` params never enter the input | Code + tests | `test_split_offer_keeps_search_params_out_of_card_input` | 11 | not shown |
| 3 | The stand extracts a card, queues low-confidence values, a correction makes the rerun confident | Code + tests; observed live by the stand worker 2026-10-14 | PR with the stand, `backend/tests/unit` review-queue loop tests | 4, 7 | full P0 loop |
| 4 | The stand uses the fusion rule with baseline and ranker, without twins and Jev | Code + tests | fusion PR, `usecase/stand_chooser.py` | 4 | twin row on slide 4 comes from the offline file, not the stand |
| 5 | Jev is called only for disputed slots, behind the `DecisionModel` port; without a key the cascade runs | Code + tests | `../docs/evidence.md#что-даёт-decision-модель-поверх-правил` | 9 | not shown |
| 6 | Jev on top of the ranker does not raise F1 | Measured | `../docs/evidence.md#что-даёт-итоговая-сборка` | 9 | not shown |
| 7 | Gold labels are catalog `*_search` params, not human labels | Assumption, said aloud | `../docs/adr/0001-gold-from-search-params.md` | 11 | not shown |

## End-to-end example

SKU 400410050, «Смартфон HONOR X9c 12/256GB Purple», split `test`, category 761. Checked by hand on
2026-10-15 against `gold.parquet` and the card text:

| Attribute | Seller field | Final value | Source | Gold | Verdict |
| --- | --- | --- | --- | --- | --- |
| Диагональ | `6.6" и более` | 6.7" | quote «6,7-дюймовый экран» | 6.7" | correct |
| Ёмкость аккумулятора | `5001-7000 мАч` | 6600 мАч | quote «6600 мА*ч» | 6600 мАч | correct |
| Встроенная память | `256 ГБ` | 256 ГБ | quote «256GB» | 256 ГБ | correct |
| Поддержка стандартов | — | 2G/3G/4G LTE/5G | twin SKU 400410051 | 2G/3G/4G LTE/5G | correct |
| Бренд, Модель, Цвет, Производитель процессора | partly | HONOR, X9c 12/256GB Purple, фиолетовый, Qualcomm | dictionary, title, seller | same | correct |
| Процессор | — | Qualcomm | dictionary | Qualcomm Snapdragon 6 gen1 … | incomplete |
| Серия | — | review queue, «Honor», confidence 0.04 | dictionary | X9c | correctly not accepted |

8 of 9 accepted values correct, 1 in the review queue. Source: `data/predictions/final_all.predictions.jsonl`.

## Numbers

| Key | Value | Population and runs | How measured | Source | Date |
| --- | --- | --- | --- | --- | --- |
| `seller_coverage` | 25.9% | 191 236 pairs, test + new_category | `uv run final` | `../docs/evidence.md#что-даёт-итоговая-сборка` | 2026-10-15 |
| `final_coverage` | 79.0% | same | same | same | 2026-10-15 |
| `text_ceiling` | 68.2% | 191 236 pairs, test + new_category | `uv run baseline` | `../docs/evidence.md#насколько-точно-базлайн-заполняет-обязательные-атрибуты` | 2026-10-14 |
| `f1_baseline`, `f1_ranker`, `f1_jev`, `f1_twins`, `f1_final` | 66.8, 70.1, 70.1, 76.3, 77.5 | 25 550 cards, one test run after val tuning | `uv run final` | `../docs/evidence.md#что-даёт-итоговая-сборка` | 2026-10-15 |
| `f1w_baseline`, `f1w_final` | 76.4, 80.6 | same, traffic-weighted | same | same | 2026-10-15 |
| `f1_new_baseline`, `f1_new_final` | 65.5, 65.8 | 1 821 cards of 8 held-out categories | same | same | 2026-10-15 |
| `f1_phone_*`, `f1_laptop_*` | 68.1 → 85.0, 69.6 → 82.5 | category slices of the same run | same | same | 2026-10-15 |
| `precision_final` | 83.3% | same | same | same | 2026-10-15 |
| `ece_final` | 0.021 | 139 290 values with gold | same | same | 2026-10-15 |
| `precision_top_conf` | 98.3% | values with confidence 0.9–1.0 | same | same | 2026-10-15 |
| `beyond_text` | 11.9% | pairs with gold filled correctly by a value absent from the text | same | same | 2026-10-15 |
| `threshold` | 0.25 | tuned on val | same | same | 2026-10-15 |
| `jev_slots`, `jev_cost_1m` | 28%, $62 | 8 000 cards, sum of `usage.cost` | `uv run decide` | `../docs/evidence.md#что-даёт-decision-модель-поверх-правил` | 2026-10-14 |
| `empty_before`, `empty_after` | 20.7%, 11.2% | all 1 177 200 cards | `predict-all.sh` | `../docs/evidence.md#что-даёт-итоговая-сборка` | 2026-10-15 |

## Done, in progress, next

| Done, live | Done, tests only | In progress or not started |
| --- | --- | --- |
| Metrics reports, predictions for all cards, EDA | Stand P0 loop (observed by the worker, not on a hosted stand) | Twins for all cards and on the stand (issue «Двойники для всех карточек и на стенде») |
| | | Product name and mark (working name «Атрибут») |

## Organizer memo requirements

| Requirement | Status | Where shown |
| --- | --- | --- |
| Risks with mitigations: hallucinations, cost, long tail, new categories | Measured | slide 11 |
| Approach, metrics and conclusions | Measured | slides 3, 5, 8, 10, appendix |
| Show what each step gives (baseline, then model) | Measured | slide 8, appendix «Абляция» |

## Outdated or conflicting material

- `reports/ranker.md` says micro F1 70.5; the deck uses 70.1 from `reports/final.md`, where the ranker
  is read from its predictions file. The 0.4 gap is the CatBoost thread count, stated in `../docs/evidence.md`.
