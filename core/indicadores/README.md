# Banco de indicadores

Catálogo curado de consultas pre-hechas sobre las bases de los pipelines. Agregar un
indicador es escribir un YAML en `catalogo/<tema>/<id>.yaml`; no se toca código Python.

Diseño completo en [`docs/banco_indicadores.md`](../../docs/banco_indicadores.md).
Reglas de negocio para consumirlo desde otro proyecto (la api/MCP) en
[`docs/contrato_banco_indicadores.md`](../../docs/contrato_banco_indicadores.md).

## Uso

```bash
python -m core.indicadores listar --tema empleo
python -m core.indicadores describir tasa_desocupacion_municipal
python -m core.indicadores ejecutar tasa_desocupacion_municipal -p cve_geo=14039
```

Desde Python:

```python
from core.indicadores import listar, obtener, ejecutar

listar(tema="pobreza", nivel="municipal")  # metadata, sin sql
obtener("pobreza_municipal")  # Indicador completo
ejecutar("pobreza_municipal", cve_geo="14039")
```

## Contrato de salida

Todo indicador devuelve **exactamente** estas columnas, en este orden:

| Columna | Tipo | Nota |
|---|---|---|
| `cve_geo` | `text` | `'00'` nacional, `'14'` entidad, `'14039'` municipio — siempre con `LPAD` |
| `nombre_geo` | `text` | Nombre oficial |
| `periodo` | `text` | ISO: `2024`, `2024-Q1`, `2024-03` |
| `valor` | `numeric` | |
| `categoria` | `text` \| `NULL` | Desagregación opcional: sexo, tipo de delito, actividad |

Nombre, unidad, fuente y definición no se repiten por fila: viven en el YAML.

## Plantilla del YAML

El nombre del archivo debe ser `<id>.yaml` y la carpeta debe llamarse igual que el `tema`.

```yaml
id: tasa_desocupacion_municipal      # único en todo el catálogo
nombre: Tasa de desocupación municipal
tema: empleo                         # = nombre de la carpeta
definicion: >
  Qué mide, en una o dos frases. Copiar de los COMMENT ON de las migraciones.
unidad: porcentaje
fuente: INEGI — Indicadores del Mercado Laboral Municipal (ILMM)
pipeline: ilmm                       # carpeta en core/pipelines/, determina la BD
origen: vw_tasa_desocupacion         # vista/MV de la que lee (trazabilidad)
nivel: municipal                     # nacional | estatal | municipal
periodicidad: anual
cobertura:
  geografica: Nacional
  temporal: "2017-2024"
notas: |                             # opcional: trampas, no comparabilidad
  Qué NO es este indicador.
parametros:                          # opcional
  - nombre: cve_geo
    tipo: str                        # str | int
    requerido: false
    descripcion: Clave INEGI de 5 dígitos del municipio (ej. 14039). Omitir para todos.
sql: |
  SELECT ... AS cve_geo, ... AS nombre_geo, ... AS periodo, ... AS valor, ... AS categoria
  FROM vw_tasa_desocupacion
  WHERE (CAST(:cve_geo AS text) IS NULL OR clave_municipio = CAST(:cve_geo AS text))
  ORDER BY cve_geo, periodo
```

## Tres reglas obligatorias del SQL

1. **Filtros opcionales con `(:param IS NULL OR condición)`.** Un solo SQL cubre todas las
   combinaciones de filtros sin construir cadenas → sin inyección posible.
2. **Siempre `CAST(:param AS tipo)`**, en *cada* aparición del parámetro. Un bind `NULL`
   sin cast hace que PostgreSQL falle con *"could not determine data type of parameter"*.

3. **Proyectar las cinco columnas con `AS`.** Se valida al cargar el catálogo.

`ejecutar` envuelve el SQL en `SELECT * FROM (...) LIMIT 5001` y abre la conexión en
`postgresql_readonly=True`: el catálogo no puede escribir ni traerse una serie entera. La fila
extra es a propósito — si la consulta rebasa las 5000 filas, `ejecutar` falla nombrando los
parámetros con los que acotar, en vez de devolver una serie truncada en silencio.

## Verificar

```bash
pytest tests/indicadores/test_catalogo.py     # sin BD
pytest -m integration tests/indicadores/      # con BD, requiere los .env
```

El catálogo se valida al importar: ids duplicados, SQL que no empiece con `SELECT`/`WITH`,
SQL que no proyecte las cinco columnas y desajustes entre `parametros` y los `:binds`
revientan ahí, no en producción.

## Fuentes de verdad

Las **migraciones** describen el esquema real (`migrations/<pipeline>/sql/`), no los README
de pipeline, que a veces están desfasados. Los `COMMENT ON` de esas migraciones son la mejor
materia prima para `definicion` y `notas`.

El banco solo lee: no modifica `schemas.py`, migraciones ni DAGs, y no refresca vistas
materializadas — eso sigue siendo del `load.py` de cada pipeline.
