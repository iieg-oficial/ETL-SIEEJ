#!/usr/bin/env bash
set -euo pipefail

payload="$(cat || true)"
command_text="$(printf '%s' "$payload" | jq -r '.. | .command? // empty' 2>/dev/null | awk 'NF {print; exit}')"

if [[ -n "$command_text" ]] \
  && [[ "$command_text" =~ (^|[[:space:];|&])(python|python3)([[:space:]]|$) ]] \
  && [[ "$command_text" != *"conda run -n etl"* ]] \
  && [[ "$command_text" != just* ]]; then
  cat <<'EOF'
{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"ask","permissionDecisionReason":"Use conda run -n etl for Python commands in this workspace."}}
EOF
  exit 0
fi

cat <<'EOF'
{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"allow"}}
EOF
