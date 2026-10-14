#!/usr/bin/env bash
set -euo pipefail

DATA="${1:-../data/processed}"
OUT="${2:-../data/predictions}"
SHARDS="${SHARDS:-5}"
PARALLEL="${PARALLEL:-3}"
WORK="${WORK:-../data/shards}"

rm -rf "$WORK"
uv run shard-cards --data "$DATA" --out "$WORK" --shards "$SHARDS"
for ((first = 0; first < SHARDS; first += PARALLEL)); do
  pids=()
  for ((i = first; i < first + PARALLEL && i < SHARDS; i++)); do
    nice -n 10 uv run baseline --data "$WORK/$i" --out "$WORK/out_$i" \
      --reports "$WORK/reports_$i" --all-cards --no-candidates > "$WORK/log_$i.txt" 2>&1 &
    pids+=("$!")
  done
  for pid in "${pids[@]}"; do
    wait "$pid"
  done
done
mkdir -p "$OUT"
target="$OUT/baseline_all.predictions.jsonl"
if [[ -f "$target" ]]; then
  mv "$target" "$target.bak"
fi
for ((i = 0; i < SHARDS; i++)); do
  cat "$WORK/out_$i/baseline_all.predictions.jsonl"
done > "$target"
wc -l "$target"
