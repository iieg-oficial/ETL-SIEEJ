---
name: eda-reporte
description: Use when serializing EDA results into the standardized JSON report consumed by DEA and DB.
---

# Skill: EDA Report

## Purpose
Use this skill after the EDA script runs to serialize the results into a structured JSON report for DEA and DB.

## Steps

1. Run the EDA script while capturing results in Python variables instead of relying only on console output.
2. Build the report dictionary from the schema in `template.py` in this folder.
3. Serialize with `json.dump(reporte, f, indent=2, ensure_ascii=False)`.
4. Save it to `./core/pipelines/{flujo}/eda/reporte_eda.json`.
5. Print or return a short confirmation summary with the most relevant fields.

## Template

See `template.py` in this folder.
