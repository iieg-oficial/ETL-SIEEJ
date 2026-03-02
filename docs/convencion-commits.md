<div align="center">

# 📋 Convención de Commits - ETL SIEEJ

<img src="https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white" alt="Git"/>
<img src="https://img.shields.io/badge/Conventional_Commits-FE5196?style=for-the-badge&logo=conventionalcommits&logoColor=white" alt="Conventional Commits"/>
<img src="https://img.shields.io/badge/Hook-Automático-22c55e?style=for-the-badge" alt="Hook"/>

---

### Mensajes claros, historial rastreable, equipo en sincronía 🎯

</div>

---

## 🚀 Formato

```
<tipo>(<scope>): <descripción en imperativo>
```

```bash
# Ejemplos
git commit -m "feat(pipeline): add etl_empleo_formal extract stage"
git commit -m "fix(core): handle null values in normalize_headers"
git commit -m "update(dags): change repd schedule to first of month"
git commit -m "docs(guide): add flyway guide to docs/"
git commit -m "merge(pipeline): mergre [PIPELINE] into develop"
```

---

## 📝 Tipos

<div align="center">

| Tipo | Descripción | Ejemplo |
|:----:|:------------|:--------|
| `feat` | Nueva funcionalidad o pipeline | `feat(pipeline): add etl_fiscalia bootstrap stage` |
| `fix` | Corrección de error | `fix(core): handle empty dataframe in bulk_insert` |
| `update` | Modificación de funcionalidad existente | `update(dags): change ce schedule from march to april` |
| `refactor` | Refactorización sin cambio funcional | `refactor(utils): extract normalize logic to helper` |
| `chore` | Dependencias, configs, mantenimiento | `chore(deps): upgrade pandas to 2.2.0` |
| `docs` | Documentación | `docs: add contributing guide` |
| `merge` | merge pipeline

</div>

---

## 🗂️ Scopes

El scope indica qué parte del proyecto fue afectada:

<div align="center">

| Scope | Aplica a |
|:-----:|:---------|
| `pipeline` | Nuevo pipeline completo o stages |
| `core` | Módulos en `core/` (db, pipeline, config) |
| `utils` | Utilidades en `core/utils/` |
| `migrations` | Scripts SQL de Flyway |
| `dags` | Archivos DAG de Airflow |
| `config` | Configuración del proyecto |
| `docs` | Documentación (también puede omitirse el scope) |


</div>

---

## 📚 Ejemplos por área

<details>
<summary><strong>⬇️ Extracción de datos</strong></summary>

```bash
feat(pipeline): add incremental extraction for repd source
fix(pipeline): resolve timeout in ce_extract for large files
update(pipeline): improve zip extraction retry logic
```

</details>

<details>
<summary><strong>⚙️ Transformación y carga</strong></summary>

```bash
feat(pipeline): add data quality validation to fiscalia transform
fix(utils): correct date format normalization for iso strings
update(core): add batch size configuration to bulk_insert
refactor(utils): split clean.py into clean and validate modules
```

</details>

<details>
<summary><strong>🗄️ Migraciones</strong></summary>

```bash
feat(migrations): add V3 diccionario table for censos_economicos
fix(migrations): correct column type in V2 stg_ce_data
update(migrations): add index on municipio for ce_datos
```

</details>

<details>
<summary><strong>🔁 DAGs y Airflow</strong></summary>

```bash
feat(dags): add etl_empleo_formal bootstrap and update DAGs
update(dags): change repd update schedule to 0 2 1 * *
fix(dags): remove catchup=True causing unintended backfill
chore(config): update airflow worker memory limit to 4GB
```

</details>

<details>
<summary><strong>🧠 Core y utilidades</strong></summary>

```bash
feat(core): add retry logic to Database connection pool
refactor(core): extract stage context passing to base class
update(utils): normalize_headers now strips leading/trailing spaces
fix(core): close db connection on pipeline failure
```

</details>

---

## ✅ Reglas

<table>
<tr>
<td width="50%">

**1. Tipo y scope en minúsculas**
`feat(pipeline)` ✅ - `Feat(Pipeline)` ❌

**2. Descripción en inglés, imperativo**
`"add extract stage"` ✅
`"added extract stage"` ❌
`"agrega stage de extracción"` ❌

**3. Máximo 72 caracteres en la primera línea**

</td>
<td width="50%">

**4. Scope específico al componente afectado**
`fix(core)` ✅ - `fix` ❌ *(si hay un scope claro)*

**5. Un commit = un cambio lógico**
No mezcles feat + fix en el mismo commit.

**6. Sin commits `WIP` en el PR final**

</td>
</tr>
</table>

---

<div align="center">

<sub>Convención de commits - ETL SIEEJ - IIEG Jalisco</sub>

</div>
