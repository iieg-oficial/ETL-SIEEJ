#!/usr/bin/env bash
set -euo pipefail

cat <<'EOF'
{"continue":true,"systemMessage":"Workspace policy: use .github as the only active Copilot customization source. Use conda run -n etl for Python commands, start with just --list, and treat .claude/, data/, logs/, .ruff_cache/, config/airflow.cfg, and plugins/ as low-value context unless the task explicitly targets them."}
EOF
