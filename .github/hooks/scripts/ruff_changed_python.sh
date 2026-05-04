#!/usr/bin/env bash
set -euo pipefail

repo_root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$repo_root"

mapfile -t changed_python_files < <(
  {
    git diff --name-only -- '*.py'
    git diff --cached --name-only -- '*.py'
    git ls-files --others --exclude-standard -- '*.py'
  } | awk 'NF' | sort -u
)

if [[ ${#changed_python_files[@]} -eq 0 ]]; then
  cat <<'EOF'
{"continue":true,"systemMessage":"Ruff check skipped: no changed Python files were detected."}
EOF
  exit 0
fi

if command -v conda >/dev/null 2>&1; then
  runner=(conda run -n etl python -m ruff check)
elif command -v ruff >/dev/null 2>&1; then
  runner=(ruff check)
else
  cat <<'EOF'
{"continue":true,"systemMessage":"Ruff check skipped: neither conda nor ruff is available in the current shell."}
EOF
  exit 0
fi

set +e
ruff_output="$(${runner[@]} "${changed_python_files[@]}" 2>&1)"
ruff_status=$?
set -e

if [[ $ruff_status -eq 0 ]]; then
  joined_files="$(printf '%s, ' "${changed_python_files[@]}")"
  joined_files="${joined_files%, }"
  jq -Rn --arg msg "Ruff check passed for changed Python files: $joined_files" '{continue:true,systemMessage:$msg}'
  exit 0
fi

summary="$(printf '%s' "$ruff_output" | tail -n 40)"
jq -Rn --arg msg "Ruff check failed for changed Python files. Review and fix before closing the session.\n$summary" '{continue:true,systemMessage:$msg}'
