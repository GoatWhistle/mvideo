# Demo runbook: Атрибут

Not shown to the audience. Slot in the talk: during slide 4 or right after the talk if the
regulation gives a separate demo slot (open question Q1). Facts: [pitch-evidence.md](pitch-evidence.md).
Run commands: `../docs/running.md#как-поднять-стенд`.

Mode: live on our laptop. Version: `main` at the commit tagged for submission. Operator and timer:
to be assigned (team roles are not fixed yet).

## Prep: 20 minutes before

1. [ ] Version fixed: `git rev-parse --short HEAD` matches the submission tag, `git status --short` is empty.
2. [ ] Stand pack present: `data/stand/pack.json.gz`; models in `data/stand/models/{ranker,fusion}`.
3. [ ] Stand up: `docker compose up` (or `uvicorn` + `npm run dev`, see `../docs/running.md`).
4. [ ] Health: `curl -s localhost:8000/api/v1/health` answers OK; the page opens without the `stand_unavailable` error.
5. [ ] Warm-up: pick the HONOR X9c example, check diagonal 6.7", battery 6600 мАч, the series in the review queue.
6. [ ] Do not restart the backend after the warm-up correction is reverted: the queue lives in memory.
7. [ ] Screen 1920×1080, zoom 100%, clean browser profile, notifications off, no terminal or `.env` on screen.
8. [ ] Backup recording open and paused; `dist/deck.pdf` open in a background tab.

## Main scenario

| Time | Action | What is visible | What to say |
| --- | --- | --- | --- |
| 0:00 | Select the example «Смартфон HONOR X9c 12/256GB Purple» | card text and seller fields with ranges | «Вот та же карточка, у продавца диапазоны» |
| 0:10 | Run extraction | table: value, confidence, quote highlighted in the text, source | «Каждое значение подсвечено в тексте» |
| 0:25 | Open the review queue | «Серия: Honor», low confidence | «Серию система не записала, она ждёт человека» |
| 0:35 | Correct the series to «X9c» and accept | the correction is saved | «Правка становится правилом» |
| 0:45 | Run extraction again | series «X9c» with high confidence, source «Подтверждено человеком» | «Теперь значение уверенное» |

If running late: skip the rerun; say that it is in the recording.

## Plan B

| Situation | What we do | What we say |
| --- | --- | --- |
| The stand does not start | Play the backup recording «ЗАПИСЬ» with its date | «Это запись репетиции, не живой прогон» |
| Page shows `stand_unavailable` | Rebuild the pack with `uv run stand-pack` after the talk; show the recording now | «Пакет данных не подхватился, показываю запись» |
| The example is missing from the pack | Paste the card text manually from `pitch-evidence.md` | «Вставлю ту же карточку вручную» |
| Laptop or projector fails | PDF from USB on the organizer laptop | «Покажу по слайдам» |

## Backup recording

Not recorded yet. Record the main scenario above once the stand is up on the submission commit,
label the frame «ЗАПИСЬ» with the date.
