<div align="center">

# 🤝 Guía de Contribución — ETL SIEEJ

<img src="https://img.shields.io/badge/IIEG-Jalisco-5C2D91?style=for-the-badge" alt="IIEG"/>
<img src="https://img.shields.io/badge/Contribuciones-Bienvenidas-f97316?style=for-the-badge&logo=github" alt="Contribuciones"/>
<img src="https://img.shields.io/badge/Flujo-Issue → PR-017CEE?style=for-the-badge" alt="Flujo"/>

---

### Todo cambio en producción empieza con un issue. 🎯

</div>

---

## Índice

- [Visión General del Flujo](#visión-general-del-flujo)
- [Issues](#issues)
- [Convenciones de Commits](#convenciones-de-commits)
- [Pull Requests](#pull-requests)
- [Board del Proyecto](#board-del-proyecto)
- [Code Review](#code-review)
- [Lo que NO hacer](#lo-que-no-hacer)

---

## Visión General del Flujo

La visión general se muestra en la siguiente imagen:
<img src = "assets/vision_general.png">

Esencialmente los pasos son los siguientes:

**1. Issue**<br/>
Describe el problema o feature con contexto y criterios de aceptación

**2. Branch**<br/>
Crea una rama desde `develop` con el nombre convencional

**3. Commits**<br/>
Crea los commits siguiendo la convención de [nuestra guía de commits]("docs/convencion_de_commits.md").

**4. PR**<br/>
Abre el PR hacia `develop`, agrega contexto y solicita revisión


---

## Issues

### ¿Cuándo crear un issue?

Siempre. Antes de tocar código, debe existir un issue que justifique el cambio.

<table>
<tr>
<td>

**Crea un issue para:**
- Bugs y comportamientos inesperados
- Nuevos pipelines o features
- Mejoras a la documentación
- Refactorizaciones o deuda técnica
- Ideas o propuestas de mejora

</td>
<td>

**Un buen issue incluye:**
- Descripción clara del problema o feature
- Pasos para reproducir (si es bug)
- Criterios de aceptación
- Contexto adicional (logs, screenshots, etc.)
- Labels apropiados

</td>
</tr>
</table>

### Plantilla recomendada

```markdown
## Descripción
¿Qué está pasando o qué se necesita?

## Criterios de Aceptación
- [ ] El pipeline X procesa correctamente...
- [ ] Las migraciones están actualizadas
- [ ] El DAG está documentado

## Contexto adicional
Logs, screenshots, referencias, etc.
```

> Si el issue es un **nuevo pipeline**, consulta la guía paso a paso para la **[creación de nuevo flujo](docs/nuevo_flujo.md)**.

---

## Convenciones de Commits

Usamos **Conventional Commits** con scope específico al proyecto (`feat(pipeline)`, `fix(core)`, `update(dags)`...).

> Guía completa con tipos, scopes y ejemplos se encuentra en nuestra **[guía de convención de commits](docs/convencion-commits.md)**.

---

## Pull Requests

### Checklist antes de abrir un PR

```markdown
### Código
- [ ] El pipeline funciona en modo `bootstrap` local
- [ ] El pipeline funciona en modo `update` local
- [ ] No hay credenciales ni datos sensibles hardcodeados
- [ ] No hay archivos `.env` ni `flyway.conf` en el PR
- [ ] Los logs siguen el formato del proyecto

### Base de datos
- [ ] Las migraciones están en `migrations/<pipeline>/sql/`
- [ ] Los archivos SQL siguen la nomenclatura `V{n}__descripcion.sql`
- [ ] Las migraciones son reproducibles (probadas con `flyway-reset`)

### Documentación
- [ ] El DAG tiene docstring descriptivo
- [ ] Las variables de entorno están documentadas en un `.env.example`

### Airflow
- [ ] El DAG aparece en la interfaz sin errores de importación
- [ ] Los schedules están configurados correctamente
- [ ] El DAG tiene `catchup=False` si no se necesita backfill
```

### Plantilla de descripción

```markdown
## ¿Qué hace este PR?
Descripción breve del cambio.

## ¿Por qué?
Contexto del issue que resuelve. Closes #<número>

## Cambios principales
- Agrega stage Extract para fuente X
- Agrega migración V3__nueva_tabla.sql
- Actualiza config de pipeline

## Cómo probar
1. `just build-dev user=test pass=test db=test`
2. `just flyway-migrate <pipeline>`
3. `python dags/etl_<pipeline>.py`

## Screenshots / Logs (opcional)
```

### Reglas del PR

<table>
<tr>
<td>

**El PR debe:**
- Apuntar a `develop` (no a `main`)
- Referenciar el issue: `Closes #42`
- Tener descripción clara de los cambios
- Tener al menos **1 aprobación** antes de merge
- Pasar todos los checks del CI

</td>
<td>

**El PR NO debe:**
- Incluir archivos `.env`, `flyway.conf` ni credenciales
- Mezclarse con cambios no relacionados
- Tener más de ~500 líneas de cambio (dividir si es necesario)
- Mergear sin revisión
- Incluir commits `WIP` o de debug

</td>
</tr>
</table>

---

## Board del Proyecto

El board de GitHub Projects organiza el trabajo en columnas:

| Columna | Qué va aquí |
|:-------:|:------------|
| **Backlog** | Issues identificados, sin prioridad aún |
| **To Do** | Issues priorizados para el sprint actual |
| **In Progress** | Issues con trabajo activo (rama creada) |
| **In Review** | PRs abiertos esperando revisión |
| **Done** | Issues cerrados / PRs mergeados |

> Cuando creas una rama para un issue, mueve la tarjeta a **In Progress**.
> Cuando abres el PR, muévela a **In Review**.

---

## Code Review

### Como autor

- Asigna reviewers apenas abras el PR
- Responde todos los comentarios antes de solicitar re-review
- No hagas force push mientras hay una revisión activa
- Usa "Resolve conversation" solo cuando el cambio esté aplicado

### Como reviewer

- Revisa el PR en las primeras 24-48 horas
- Diferencia entre **bloqueantes** y **sugerencias** en tus comentarios
- Aprueba con confianza cuando el código sea correcto, aunque no sea exactamente como lo harías tú

```
❌  "Esto está mal"
✅  "Considera usar `upsert` aquí para manejar duplicados: `core/utils/bulk_ops.py:45`"

❌  "No me gusta esta función"
✅  "Sugerencia (no bloqueante): podrías extraer esta lógica a un método separado para facilitar el testing"
```

---

## Lo que NO hacer

> Estos puntos no son negociables. 🔒

<table>
<tr>
<td>

**Seguridad**
- ❌ Nunca subas contraseñas, tokens o API keys
- ❌ Nunca subas `flyway.conf` (tiene credenciales)
- ❌ Nunca subas archivos `.env` con valores reales
- ❌ Nunca hardcodees URLs de producción en el código

</td>
<td>

**Git**
- ❌ No hagas push directo a `main` o `develop`
- ❌ No uses `--force` en ramas compartidas
- ❌ No mergees tu propio PR sin revisión
- ❌ No borres ramas de otros sin consultar

</td>
</tr>
</table>

---

<div align="center">

<sub>Guía de contribución — ETL SIEEJ · IIEG Jalisco</sub>

</div>
