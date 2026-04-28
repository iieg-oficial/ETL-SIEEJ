---
description: Operaciones aisladas de git para un pipeline (crear issue+rama, commits,
  o PR final).
argument-hint: '[nombre del pipeline] [modo: init|commit|pr]'
---

> Use el agente `git-agent`.

Operación de control de versiones:

- **Pipeline:** {{flujo}}
- **Modo:** {{modo}}    <!-- init | commit | pr -->

Según el modo:

- **init**: crear el GitHub issue desde [.github/ISSUE_TEMPLATE/new-pipeline.md](../../.github/ISSUE_TEMPLATE/new-pipeline.md) y la rama `<N>-pipeline-{{flujo}}` desde `develop`. Aplica skill `issue-template`.
- **commit**: hacer los commits atómicos pendientes siguiendo la secuencia del skill `git-pipeline-commits`. Sin `git add .`. Pre-commit debe pasar.
- **pr**: abrir el PR contra `develop` con [.github/pull_request_template.md](../../.github/pull_request_template.md) ya completado. Aplica skill `pull-request-template`.

Reglas heredadas de [.github/instructions/git-rules.instructions.md](../instructions/git-rules.instructions.md).
