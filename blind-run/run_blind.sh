#!/usr/bin/env bash

cd "$(dirname "$0")"
mkdir -p results

if [ ! -f results/run_info.txt ]; then
  echo "model: claude-opus-5-5" > results/run_info.txt
  claude --version >> results/run_info.txt
  date >> results/run_info.txt
fi

for f in samples/*.c; do
  name=$(basename "$f" .c)
  out="results/$name.json"
  if [ -f "$out" ]; then
    continue
  fi
  echo "=== $name"
  bash .claude/skills/find-vulnerabilities/scripts/find-vulnerabilities.sh "$f" "$out" > "results/$name.log" 2>&1
done

echo "done"