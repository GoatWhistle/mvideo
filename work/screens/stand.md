# Screen: stand (index route)

Task: a catalog person pastes or picks a seller card, sees attributes with quote, confidence and
source, and resolves low-confidence values; a resolution becomes an alias and the card is re-extracted.

## Panels

- Left column: card form (sample Select, category Select, title, description, seller lines "name: value",
  Extract button), then the review queue (pending items, Accept / Correct with inline field).
- Right column: extracted attributes table (attribute, value, confidence %, status badge, source,
  quote) with "not found in the text" line; below it the card text with quote marks (solid underline
  for accepted, dashed for review; hovering a table row outlines its mark).
- Below 64rem: one column, form and queue first, then results. Below 48rem the table turns into
  stacked rows.

## States

- Stand data missing: form card shows ErrorState with the `stand_unavailable` text and Retry.
- Before the first run: result card EmptyState.
- Extracting: skeleton after the delay; on re-run the previous result dims (stale).
- Extraction error: ErrorState with Retry of the last input.
- Queue: skeleton, error with Retry, EmptyState, list.

## Checked

2026-10-14, local uvicorn + vite preview on the real pack: 1440 light/dark RU, 375 light RU and dark EN,
1440 EN; no horizontal overflow, no console errors; correction of a review item re-extracts the card
and the value comes back as "Confirmed by a person", 97 %.
