# Deck plan: Атрибут

Status: ready for audit. Updated 2026-10-15.
Rules: [AGENTS.md](AGENTS.md). Proofs: [pitch-evidence.md](pitch-evidence.md).

## 1. Regulation

| Item | Value | Source |
| --- | --- | --- |
| Talk | 6:00 engine default, speech 4:50 | not published, open question Q1 |
| Q&A | not published | Q1 |
| Format | not published | Q1 |
| Demo | inside slide 4 or a separate slot | `demo-runbook.md` |
| Who switches slides | speaker | default |
| Screen | 1920×1080 | default |
| Deck language | ru | `../brief/PLATFORM.md` (no language set), case page in Russian |
| Deck file required by organizers | presentation with approach, metrics and conclusions; one repo or archive | `../brief/PLATFORM.md` |

## 2. Criteria and slides

Jury weights are not published; the case success metrics are used without weights.

| Criterion | Weight | Slides | Seconds | Proof shown on the slide |
| --- | ---: | --- | ---: | --- |
| Per-attribute P/R/F1 | — | 8, A2 | 30 | `f1_baseline`, `f1_final`, ablation chart |
| Coverage | — | 2, 10 | 50 | `seller_coverage`, `final_coverage`, `empty_after` |
| Traffic-weighted quality | — | 11, A2 | 25 | `f1w_final` |
| Rare and new categories | — | 8, 11 | 55 | `f1_new_baseline`, `f1_new_final` |
| Risks and mitigations | — | 11 | 25 | four case risks with measures |
| Hybrid and cost | — | 3, 9 | 45 | `jev_slots`, `jev_cost_1m`, Jev without gain |
| Feedback loop (bonus) | — | 4, 7 | 60 | review queue on the example |

## 3. End-to-end example

- **Input:** SKU 400410050 «Смартфон HONOR X9c 12/256GB Purple», split `test`; seller fields give ranges («6.6" и более», «5001-7000 мАч»).
- **Product output:** diagonal 6.7" and battery 6600 мАч from quotes, network standards from a catalog twin, series sent to the review queue.
- **Checked by hand:** 2026-10-15 against `gold.parquet`: 8 of 9 accepted values correct, processor incomplete, series correctly not accepted.
- **On slides:** 2 fails today, 4 processed, 7 explained.
- **On the demo stand:** the stand runs baseline and ranker; the twin value comes from the offline file. Pitch-evidence rows 3–4.

## 4. Slide list

| # | id | Title (thesis) | Criterion | Time | Cumulative |
| ---: | --- | --- | --- | ---: | ---: |
| 1 | cover | Характеристики из текста карточки, которые нельзя выдумать | — | 0:15 | 0:15 |
| 2 | problem | Продавец пишет диапазон, товар выпадает из фильтров | coverage | 0:30 | 0:45 |
| 3 | solution | Значение только с доказательством, сомнительное человеку | hybrid | 0:25 | 1:10 |
| 4 | product | Та же карточка проходит через каскад | loop | 0:35 | 1:45 |
| 5 | mechanic | Ранжировщик с честной уверенностью | quality | 0:25 | 2:10 |
| 6 | funnel | Двойники закрывают то, чего нет в тексте | quality | 0:30 | 2:40 |
| 7 | explain | Видно, откуда значение, спорное решает человек | loop | 0:25 | 3:05 |
| 8 | measured | Каскад точнее правил, новые категории на уровне правил | P/R/F1 | 0:30 | 3:35 |
| 9 | architecture | Дорогая модель за портом | cost | 0:20 | 3:55 |
| 10 | impact | Обязательные поля заполнены втрое чаще | coverage | 0:20 | 4:15 |
| 11 | risks | Четыре риска кейса с мерами и замерами | risks | 0:25 | 4:40 |
| 12 | final | Готовы к вашим вопросам | — | 0:10 | 4:50 |

Reserve: 1:10. Appendices: A1 status, A2 ablation by slices.

## 5. Slide cards

Cards are folded into the slides themselves, `SPEECH.md` and `notes.js`; the sources of every
number are in `pitch-evidence.md`.

## 6. Organizer memo coverage

| Requirement (quote) | Where | Status |
| --- | --- | --- |
| «Финальная презентация с подходом, метриками и выводами» | slides 3–11, appendices | done |
| «На защите покажите риски своего решения вместе с мерами их снижения» | slide 11 | done |
| «Начните с базлайна … и покажите, что дает каждый шаг» | slide 8, appendix A2 | done |

## 7. Open markers

| Marker | Slide | What exactly | Owner | Due |
| --- | --- | --- | --- | --- |
| `[NEED TO CHECK]` | all | Regulation: talk and Q&A minutes, format (Q1) | team | before the defense |
| `[NEED TO CHECK]` | 1, 12 | Product name and mark: working name «Атрибут», default mark; team name GoatWhistle from the GitHub org | team | before the defense |
| `[NEED SCREENSHOT]` | 4 | Real stand screen instead of the rebuilt component, if twins reach the stand | team | after the twins issue |
| `[NEED TO CHECK]` | 12 | QR leads to a private repository; the jury needs access or a public link | team | before submission |
| — | — | Backup demo recording | team | before the defense |

## 8. Audit

2026-10-15, first version. `npm run build:final` passes, `npm run shots` 0 layout issues and 0 console
errors, `npm run speech:check` 0 errors. Should fix: speakers and handoffs once roles are set.
