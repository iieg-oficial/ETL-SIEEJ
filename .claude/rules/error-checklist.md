---
paths:
  - "core/pipelines/**"
---

# Error Checklist

Flag these when spotted:

- **Extract**: Column rename mismatches, missing retry/cache logic, silent fetch failures, no empty-DataFrame guard when source returns 0 records
- **Transform**: Reading nonexistent files, ineffective normalization, unintended null/column drops, duplicates, calling `list_values_to_null` on columns still in `object` dtype with float values (cast first with `pd.to_numeric`), calling `list_values_to_null` before converting datetime columns (convert with `pd.to_datetime` first, then `.dt.date` after)
- **Load**: FK mapping failures, missing `sync_id_sequence`, load order violations, slow bulk inserts, duplicates, SERIAL `id` included in INSERT columns, `pd.NA` not converted before insert (use `df.astype(object).where(df.notna(), None)`)
