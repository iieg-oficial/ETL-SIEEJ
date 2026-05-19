# AGENTS.md — Mapa de navegación para agentes de IA

> Punto de entrada para cualquier agente que trabaje en este repositorio.
> No es una biblia de reglas: es un **mapa**. Lee solo lo que necesites.

---

## 1. Antes de empezar (obligatorio)

1. Lee `.claude/progress/current.md` — estado de la sesión anterior.
2. Lee `.claude/feature_list.json` — fases del pipeline activo y su estado.
3. Lee `docs/architecture.md` — qué significa hacer un buen trabajo aquí.

## 2. Mapa del repositorio

| Archivo / carpeta | Qué contiene | Cuándo leerlo |
|---|---|---|
| `.claude/feature_list.json` | Fases del pipeline activo con estado | Siempre, al empezar |
| `.claude/progress/current.md` | Estado de la sesión activa | Siempre, al empezar |
| `.claude/progress/history.md` | Bitácora de sesiones anteriores (local, no commiteado) | Si necesitas contexto histórico |
| `docs/architecture.md` | Principios de "buen trabajo" en este proyecto | Antes de implementar |
| `CLAUDE.md` | Stack, estructura de directorios, convenciones de código | Antes de escribir código |
| `.claude/CHECKPOINTS.md` | Criterios objetivos para declarar una fase como `done` | Para auto-evaluarte |
| `.claude/rules/` | Reglas de patrones, base de datos, errores comunes | Antes de implementar |
| `.claude/agents/` | Definiciones de subagentes (líder, implementador, revisor) | Si orquestas trabajo |
| `core/pipelines/{pipeline}/` | Código del pipeline activo | Para implementar |
| `migrations/{pipeline}/sql/` | Migraciones Flyway del pipeline activo | Fase 6 |

## 3. Reglas duras

- **Una sola fase a la vez.** No mezcles cambios de fases distintas en la misma sesión.
- **No declares una fase `done` sin verificación.** Ver `.claude/CHECKPOINTS.md`.
- **Documenta en `.claude/progress/current.md`** mientras trabajas, no al final.
- **Si no sabes algo, busca en los docs** antes de inventarlo.
- **Si te bloqueas**, documenta el bloqueo en `.claude/progress/current.md` y para.

## 4. Cómo elegir una fase

```
1. Abre .claude/feature_list.json
2. Filtra por status == "pending"
3. Toma la de menor "id" (las fases son secuenciales)
4. Cambia su status a "in_progress" y guarda el archivo
5. Anota en .claude/progress/current.md: pipeline, fase, hora de inicio, plan breve
```

## 5. Cierre de sesión

Antes de terminar:

1. Verifica: `just flyway-reset {pipeline}` + `python dags/etl_{pipeline}.py`
2. Si la fase está terminada: marca `status: "done"` en `.claude/feature_list.json`.
3. Añade el resumen al final de `.claude/progress/history.md` (créalo si no existe).
4. Deja `.claude/progress/current.md` con solo la plantilla vacía.
5. No dejes archivos temporales ni `print()` de debug.

## 6. Si te bloqueas

- Relee la sección relevante de `.claude/rules/`.
- Consulta los pipelines de referencia: `establecimientos_de_salud`, `marginacion`.
- Documenta el bloqueo en `.claude/progress/current.md` y termina la sesión.
