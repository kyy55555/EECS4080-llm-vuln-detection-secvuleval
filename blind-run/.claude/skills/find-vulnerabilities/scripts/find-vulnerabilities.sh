#!/usr/bin/env bash
#
# find-vulnerabilities.sh — Ask Claude Code to find vulnerabilities in a source file.
#
# Usage:  ./find-vulnerabilities.sh <source-file> [output-file]
#
# Examples:
#   ./find-vulnerabilities.sh uasn1.c
#   ./find-vulnerabilities.sh src/parser.c /tmp/vulns.txt

set -euo pipefail

# ── args ────────────────────────────────────────────────────────────────
SOURCE_FILE="${1:?Usage: $0 <source-file> [output-file]}"
OUTPUT_FILE="${2:-vuln-report-$(basename "$SOURCE_FILE").txt}"
MODEL="${MODEL:-claude-opus-5-5}"

# ── sanity checks ──────────────────────────────────────────────────────
if ! command -v claude &>/dev/null; then
  echo "Error: 'claude' CLI not found in PATH." >&2
  exit 1
fi

if ! command -v jq &>/dev/null; then
  echo "Error: 'jq' not found in PATH (needed for stream parsing)." >&2
  exit 1
fi

if [[ ! -f "$SOURCE_FILE" ]]; then
  echo "Error: source file '$SOURCE_FILE' not found." >&2
  exit 1
fi

# Ensure the output directory exists
mkdir -p "$(dirname "$OUTPUT_FILE")"

# ── prompt ─────────────────────────────────────────────────────────────
read -r -d '' PROMPT <<EOF || true
You are reviewing the C function in the file "${SOURCE_FILE}" from the Linux kernel, as part of a defensive code-review study. Work only from this file; do not search the web or read any other file.

Decide whether this function contains a security vulnerability.
Write your answer to "${OUTPUT_FILE}" as JSON with exactly this structure:
{
  "is_vulnerable": true or false,
  "cwe": "CWE-xxx" or null,
  "vulnerable_statements": [
    {"statement": "<the exact line of code>", "reason": "<why it is vulnerable>"}
  ],
  "suggested_fix": "<how to fix it, in a few sentences>"
}
If the function is not vulnerable, set "is_vulnerable" to false and leave "vulnerable_statements" empty.
List only statements you believe are really vulnerable. Do not include exploit code.
EOF

# ── run ────────────────────────────────────────────────────────────────
echo "▶ Scanning: ${SOURCE_FILE}"
echo "▶ Report:   ${OUTPUT_FILE}"

# Pre-approve the tools Claude Code needs so it won't block on permission
# prompts during non-interactive (-p) runs.
#   Read   — read the source file
#   Write  — create the report
#   Edit   — in case it prefers incremental writes
#
# --output-format stream-json streams NDJSON events in real time.
# We pipe through jq to show human-readable progress:
#   - tool use  → "⚙ Read(uasn1.c)"
#   - assistant → the actual response text
claude -p "$PROMPT"                       \
  --model "$MODEL"                        \
  --allowedTools "Read,Write,Edit"        \
  --output-format stream-json             \
  --verbose                               \
| tee "${OUTPUT_FILE%.json}.stream.jsonl" \
| jq -r '
    if .type == "assistant" then
      (.message.content[]? | select(.type == "text") | .text // empty)
    elif .type == "tool_use" then
      "⚙ \(.name)(\(.input | keys[0] // "" | tostring))"
    else
      empty
    end
  '

# ── verify output ──────────────────────────────────────────────────────
if [[ -f "$OUTPUT_FILE" ]]; then
  echo "✔ Report written to ${OUTPUT_FILE}"
else
  echo "⚠ Claude finished but no report was created at ${OUTPUT_FILE}." >&2
  exit 1
fi
