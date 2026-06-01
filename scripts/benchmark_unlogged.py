#!/usr/bin/env python3
"""
Benchmark: estrategias de carga para el load stage de DENUE.

Compara estrategias de upsert:
  1. COPY raw + FK mapping en SQL (psycopg2)
  2. COPY a tabla temporal + INSERT ON CONFLICT (psycopg2)
  3. psycopg2.extras.execute_values con INSERT ... ON CONFLICT
  4. COPY raw + FK mapping en SQL (psycopg3 binario)
  5. SQLAlchemy insert().on_conflict_do_update() — actual (comentado por lento)

Crea una base de datos temporal por estrategia, carga datos reales
y reporta tiempos detallados.

Uso:
    python scripts/benchmark_unlogged.py --entidades 1
    python scripts/benchmark_unlogged.py --entidades 1,6 --keep-dbs
    python scripts/benchmark_unlogged.py --entidades 14 --chunk-size 100000
"""

import argparse
import io
import sys
import time
from pathlib import Path

import pandas as pd
import psycopg
from psycopg2.extras import execute_values
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.pipelines.denue.attributes import DenueTables as T
from core.pipelines.denue.config import settings
from core.pipelines.denue.mappings import (
    RANGOS_PERSONAL,
    TIPOS_ESTABLECIMIENTOS,
    get_sector_codigo,
)
from core.pipelines.denue.schemas import (
    CatActualizaciones,
    CatClasesActividad,
    CatLocalidades,
    CatRamas,
    CatRangosPersonal,
    CatSectores,
    CatSubramas,
    CatSubsectores,
    CatTiposEstablecimientos,
    StgEstablecimientos,
)
from core.utils import df_to_records
from core.utils.bulk_ops import (
    get_all_records,
    get_mapping,
    insert_records,
    sync_id_sequence,
    upsert_records,
)
from core.utils.logger import get_logger

logger = get_logger("benchmark.unlogged")

ADMIN_URL = f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/postgres"
MIGRATIONS_DIR = Path("migrations/denue/sql")

STG_TABLE = StgEstablecimientos.__tablename__
STG_CONFLICT_KEYS = [StgEstablecimientos.id.key, StgEstablecimientos.actualizacion_id.key]

STRATEGIES = ["copy_sql_v3", "copy_sql", "copy_temp", "execute_values"]
# "sqlalchemy" — comentado por lento (~380s vs ~80s)


def db_url(db_name):
    return f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{db_name}"


def db_name_for(strategy):
    return f"denue_bench_{strategy}"


def create_database(name):
    engine = create_engine(ADMIN_URL, isolation_level="AUTOCOMMIT")
    with engine.connect() as conn:
        conn.execute(text(f"DROP DATABASE IF EXISTS {name}"))
        conn.execute(text(f"CREATE DATABASE {name}"))
    engine.dispose()
    logger.info(f"Database '{name}' created")


def drop_database(name):
    engine = create_engine(ADMIN_URL, isolation_level="AUTOCOMMIT")
    with engine.connect() as conn:
        conn.execute(
            text(
                f"SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                f"WHERE datname = '{name}' AND pid <> pg_backend_pid()"
            )
        )
        conn.execute(text(f"DROP DATABASE IF EXISTS {name}"))
    engine.dispose()
    logger.info(f"Database '{name}' dropped")


def create_tables(db_name):
    engine = create_engine(db_url(db_name))
    v2_sql = MIGRATIONS_DIR.joinpath("V2__catalogs_denue.sql").read_text()
    v3_sql = MIGRATIONS_DIR.joinpath("V3__tables_denue.sql").read_text()

    with engine.begin() as conn:
        for stmt in v2_sql.split(";"):
            stmt = stmt.strip()
            if stmt:
                conn.execute(text(stmt))
        for stmt in v3_sql.split(";"):
            stmt = stmt.strip()
            if stmt:
                conn.execute(text(stmt))

    engine.dispose()
    logger.info(f"Tables created in '{db_name}'")


def get_data(entidades):
    all_dfs = []
    all_catalogs = {}

    for entidad in entidades:
        transform_dir = Path("data/transform/denue")
        df_pkl = transform_dir / f"denue_df_{entidad}.pkl"
        catalogs_pkl = transform_dir / f"denue_catalogs_{entidad}.pkl"

        if df_pkl.exists() and catalogs_pkl.exists():
            logger.info(f"Loading existing pkl for entidad {entidad}")
            df = pd.read_pickle(df_pkl)
            catalogs = pd.read_pickle(catalogs_pkl).to_dict()
        else:
            logger.info(f"Running extract + transform for entidad {entidad}")
            from core.pipelines.denue.stages.extract import DenueExtract
            from core.pipelines.denue.stages.transform import DenueTransform

            extract = DenueExtract(mode="bootstrap", entidad=entidad)
            extract_data = extract.execute()

            transform = DenueTransform(mode="bootstrap", entidad=entidad)
            result = transform.execute(extract_data)

            df = result["df"]
            catalogs = result["catalogs"]

        all_dfs.append(df)
        for key, value in catalogs.items():
            if key not in all_catalogs:
                all_catalogs[key] = list(value)
            else:
                existing = {str(r) for r in all_catalogs[key]}
                for r in value:
                    if str(r) not in existing:
                        all_catalogs[key].append(r)
                        existing.add(str(r))

    df = pd.concat(all_dfs, ignore_index=True) if all_dfs else pd.DataFrame()
    return df, all_catalogs


class Timer:
    def __init__(self, label):
        self.label = label
        self.elapsed = 0.0

    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, *args):
        self.elapsed = time.perf_counter() - self.start
        logger.info(f"[{self.label}] {self.elapsed:.3f}s")


def load_catalogs(session, catalogs):
    insert_records(
        session,
        RANGOS_PERSONAL,
        CatRangosPersonal,
        conflict_keys=[CatRangosPersonal.id.key],
    )
    insert_records(
        session,
        TIPOS_ESTABLECIMIENTOS,
        CatTiposEstablecimientos,
        conflict_keys=[CatTiposEstablecimientos.id.key],
    )
    insert_records(
        session,
        catalogs[T.CAT_ACTUALIZACIONES],
        CatActualizaciones,
        conflict_keys=[CatActualizaciones.fecha_actualizacion.key],
    )
    insert_records(
        session,
        catalogs[T.CAT_LOCALIDADES],
        CatLocalidades,
        conflict_keys=[CatLocalidades.cve_geo_id.key],
    )

    scian = [
        (T.CAT_SECTORES, CatSectores, CatSectores.codigo.key),
        (T.CAT_SUBSECTORES, CatSubsectores, CatSubsectores.codigo.key),
        (T.CAT_RAMAS, CatRamas, CatRamas.codigo.key),
        (T.CAT_SUBRAMAS, CatSubramas, CatSubramas.codigo.key),
        (T.CAT_CLASES_ACTIVIDAD, CatClasesActividad, CatClasesActividad.codigo.key),
    ]
    for key, model, conflict_key in scian:
        records = catalogs.get(key, [])
        insert_records(session, records, model, conflict_keys=[conflict_key])

    for model in [
        CatActualizaciones,
        CatLocalidades,
        CatSectores,
        CatSubsectores,
        CatRamas,
        CatSubramas,
        CatClasesActividad,
    ]:
        sync_id_sequence(session, model)


def map_foreign_keys(session, df):
    actualizaciones_map = get_mapping(
        session,
        CatActualizaciones,
        CatActualizaciones.fecha_actualizacion.key,
        CatActualizaciones.id.key,
    )
    localidades_rows = get_all_records(
        session,
        CatLocalidades,
        [CatLocalidades.id.key, CatLocalidades.cve_geo_id.key],
    )
    localidades_map = {r[CatLocalidades.cve_geo_id.key]: r[CatLocalidades.id.key] for r in localidades_rows}
    sectores_map = get_mapping(session, CatSectores, CatSectores.codigo.key, CatSectores.id.key)
    subsectores_map = get_mapping(session, CatSubsectores, CatSubsectores.codigo.key, CatSubsectores.id.key)
    ramas_map = get_mapping(session, CatRamas, CatRamas.codigo.key, CatRamas.id.key)
    subramas_map = get_mapping(session, CatSubramas, CatSubramas.codigo.key, CatSubramas.id.key)
    clases_map = get_mapping(session, CatClasesActividad, CatClasesActividad.codigo.key, CatClasesActividad.id.key)

    mapped_df = df.copy()
    mapped_df[StgEstablecimientos.actualizacion_id.key] = mapped_df["fecha_actualizacion"].map(actualizaciones_map)

    mask = mapped_df["cve_mun"].notna() & mapped_df["localidad_id"].notna()
    mapped_df["cve_geo_id"] = pd.array([None] * len(mapped_df), dtype="Int64")
    mapped_df.loc[mask, "cve_geo_id"] = (
        mapped_df.loc[mask, "entidad_id"].astype(int) * 10_000_000
        + mapped_df.loc[mask, "cve_mun"].astype(int) * 10_000
        + mapped_df.loc[mask, "localidad_id"].astype(int)
    )
    mapped_df["localidad_id"] = mapped_df["cve_geo_id"].map(localidades_map)

    codigo_str = mapped_df["codigo_actividad"].dropna().astype(int).astype(str)
    mapped_df["sector_id"] = codigo_str.map(lambda x: sectores_map.get(get_sector_codigo(x)))
    mapped_df["subsector_id"] = codigo_str.str[:3].map(subsectores_map)
    mapped_df["rama_id"] = codigo_str.str[:4].map(ramas_map)
    mapped_df["subrama_id"] = codigo_str.str[:5].map(subramas_map)
    mapped_df["clase_actividad_id"] = codigo_str.map(clases_map)

    return mapped_df.astype(object).where(mapped_df.notna(), None)


def get_stg_columns():
    cols = [c for c in StgEstablecimientos.columns() if c != StgEstablecimientos.id.key]
    return [StgEstablecimientos.id.key] + cols


# ---------------------------------------------------------------------------
# Estrategia 1: SQLAlchemy (actual)
# ---------------------------------------------------------------------------
def upsert_sqlalchemy(session, records, cols, chunk_size):
    upsert_records(
        session,
        records,
        StgEstablecimientos,
        conflict_keys=STG_CONFLICT_KEYS,
        chunk_size=chunk_size,
    )


# ---------------------------------------------------------------------------
# Estrategia 2: psycopg2 execute_values
# ---------------------------------------------------------------------------
def upsert_execute_values(engine, records, cols, chunk_size):
    conflict_str = ", ".join(STG_CONFLICT_KEYS)
    update_keys = [c for c in cols if c not in STG_CONFLICT_KEYS]
    updates_str = ", ".join(f"{k} = EXCLUDED.{k}" for k in update_keys)
    cols_str = ", ".join(cols)

    sql = f"INSERT INTO {STG_TABLE} ({cols_str}) VALUES %s ON CONFLICT ({conflict_str}) DO UPDATE SET {updates_str}"

    raw_conn = engine.raw_connection()
    try:
        cur = raw_conn.cursor()
        values = [tuple(r.get(c) for c in cols) for r in records]

        total = len(values)
        for i in range(0, total, chunk_size):
            chunk = values[i : i + chunk_size]
            execute_values(cur, sql, chunk, page_size=chunk_size)
            logger.info(f"  chunk: {min(i + chunk_size, total)}/{total}")

        raw_conn.commit()
        cur.close()
    except Exception:
        raw_conn.rollback()
        raise
    finally:
        raw_conn.close()


# ---------------------------------------------------------------------------
# Estrategia 3: COPY a temp table + INSERT ON CONFLICT
# ---------------------------------------------------------------------------
def upsert_copy_temp(engine, mapped_df, cols):
    conflict_str = ", ".join(STG_CONFLICT_KEYS)
    update_keys = [c for c in cols if c not in STG_CONFLICT_KEYS]
    updates_str = ", ".join(f"{k} = EXCLUDED.{k}" for k in update_keys)
    cols_str = ", ".join(cols)

    raw_conn = engine.raw_connection()
    try:
        cur = raw_conn.cursor()

        cur.execute(f"CREATE TEMP TABLE tmp_stg (LIKE {STG_TABLE} INCLUDING DEFAULTS)")

        buf = io.StringIO()
        subset = mapped_df[cols].copy()
        int_cols = [
            "id",
            "actualizacion_id",
            "localidad_id",
            "sector_id",
            "subsector_id",
            "rama_id",
            "subrama_id",
            "clase_actividad_id",
            "rango_personal_id",
            "tipo_establecimiento_id",
        ]
        for col in subset.columns:
            if col in int_cols:
                subset[col] = subset[col].apply(lambda v: str(int(v)) if v is not None else "\\N")
            else:
                subset[col] = subset[col].apply(lambda v: str(v).replace("\\", "\\\\") if v is not None else "\\N")
        subset.to_csv(buf, sep="\t", header=False, index=False, quoting=3)
        buf.seek(0)

        logger.info(f"  COPY {len(subset):,} rows to tmp_stg")
        cur.copy_expert(
            f"COPY tmp_stg ({cols_str}) FROM STDIN WITH (FORMAT text, NULL '\\N')",
            buf,
        )

        logger.info(f"  INSERT INTO {STG_TABLE} FROM tmp_stg ON CONFLICT DO UPDATE")
        cur.execute(
            f"INSERT INTO {STG_TABLE} ({cols_str}) "
            f"SELECT {cols_str} FROM tmp_stg "
            f"ON CONFLICT ({conflict_str}) DO UPDATE SET {updates_str}"
        )

        raw_conn.commit()
        cur.close()
    except Exception:
        raw_conn.rollback()
        raise
    finally:
        raw_conn.close()


# ---------------------------------------------------------------------------
# Estrategia 4: COPY raw + FK mapping en SQL + INSERT ON CONFLICT
# ---------------------------------------------------------------------------
RAW_COLS = [
    "id",
    "nombre_establecimiento",
    "razon_social",
    "latitud",
    "longitud",
    "fecha_alta",
    "nombre_asentamiento",
    "ageb",
    "codigo_actividad",
    "entidad_id",
    "cve_mun",
    "localidad_id",
    "fecha_actualizacion",
    "rango_personal_id",
    "tipo_establecimiento_id",
]

RAW_DDL = """
CREATE TEMP TABLE tmp_raw (
    id INTEGER,
    nombre_establecimiento TEXT,
    razon_social TEXT,
    latitud FLOAT,
    longitud FLOAT,
    fecha_alta DATE,
    nombre_asentamiento TEXT,
    ageb TEXT,
    codigo_actividad TEXT,
    entidad_id INTEGER,
    cve_mun INTEGER,
    localidad_id INTEGER,
    fecha_actualizacion DATE,
    rango_personal_id INTEGER,
    tipo_establecimiento_id INTEGER
)
"""

SECTOR_RANGO_CASE = """
CASE
    WHEN LEFT(r.codigo_actividad, 2) IN ('31','32','33') THEN '31-33'
    WHEN LEFT(r.codigo_actividad, 2) IN ('48','49') THEN '48-49'
    ELSE LEFT(r.codigo_actividad, 2)
END
"""

INSERT_FROM_RAW = f"""
INSERT INTO {STG_TABLE} (
    id, actualizacion_id, nombre_establecimiento, razon_social,
    latitud, longitud, fecha_alta, nombre_asentamiento, ageb,
    localidad_id, sector_id, subsector_id, rama_id, subrama_id,
    clase_actividad_id, rango_personal_id, tipo_establecimiento_id
)
SELECT
    r.id,
    ca.id,
    r.nombre_establecimiento,
    r.razon_social,
    r.latitud,
    r.longitud,
    r.fecha_alta,
    r.nombre_asentamiento,
    r.ageb,
    cl.id,
    cs.id,
    csub.id,
    cr.id,
    csr.id,
    cca.id,
    r.rango_personal_id,
    r.tipo_establecimiento_id
FROM tmp_raw r
LEFT JOIN cat_actualizaciones ca ON ca.fecha_actualizacion = r.fecha_actualizacion
LEFT JOIN cat_localidades cl ON cl.cve_geo_id = (
    r.entidad_id * 10000000 + r.cve_mun * 10000 + r.localidad_id
)
LEFT JOIN cat_sectores cs ON cs.codigo = {SECTOR_RANGO_CASE}
LEFT JOIN cat_subsectores csub ON csub.codigo = LEFT(r.codigo_actividad, 3)
LEFT JOIN cat_ramas cr ON cr.codigo = LEFT(r.codigo_actividad, 4)
LEFT JOIN cat_subramas csr ON csr.codigo = LEFT(r.codigo_actividad, 5)
LEFT JOIN cat_clases_actividad cca ON cca.codigo = r.codigo_actividad
ON CONFLICT (id, actualizacion_id) DO UPDATE SET
    nombre_establecimiento = EXCLUDED.nombre_establecimiento,
    razon_social = EXCLUDED.razon_social,
    latitud = EXCLUDED.latitud,
    longitud = EXCLUDED.longitud,
    fecha_alta = EXCLUDED.fecha_alta,
    nombre_asentamiento = EXCLUDED.nombre_asentamiento,
    ageb = EXCLUDED.ageb,
    localidad_id = EXCLUDED.localidad_id,
    sector_id = EXCLUDED.sector_id,
    subsector_id = EXCLUDED.subsector_id,
    rama_id = EXCLUDED.rama_id,
    subrama_id = EXCLUDED.subrama_id,
    clase_actividad_id = EXCLUDED.clase_actividad_id,
    rango_personal_id = EXCLUDED.rango_personal_id,
    tipo_establecimiento_id = EXCLUDED.tipo_establecimiento_id
"""


def upsert_copy_sql(engine, raw_df):
    raw_conn = engine.raw_connection()
    try:
        cur = raw_conn.cursor()
        cur.execute(RAW_DDL)

        buf = io.StringIO()
        subset = raw_df[RAW_COLS].copy()

        int_cols = [
            "id",
            "entidad_id",
            "cve_mun",
            "localidad_id",
            "rango_personal_id",
            "tipo_establecimiento_id",
        ]
        for col in subset.columns:
            if col in int_cols:
                subset[col] = subset[col].apply(lambda v: str(int(v)) if v is not None else "\\N")
            elif col == "codigo_actividad":
                subset[col] = subset[col].apply(lambda v: str(int(float(v))) if v is not None else "\\N")
            else:
                subset[col] = subset[col].apply(lambda v: str(v).replace("\\", "\\\\") if v is not None else "\\N")

        subset.to_csv(buf, sep="\t", header=False, index=False, quoting=3)
        buf.seek(0)

        logger.info(f"  COPY {len(subset):,} raw rows to tmp_raw")
        cur.copy_expert(
            f"COPY tmp_raw ({', '.join(RAW_COLS)}) FROM STDIN WITH (FORMAT text, NULL '\\N')",
            buf,
        )

        logger.info(f"  INSERT INTO {STG_TABLE} FROM tmp_raw with SQL JOINs")
        cur.execute(INSERT_FROM_RAW)

        raw_conn.commit()
        cur.close()
    except Exception:
        raw_conn.rollback()
        raise
    finally:
        raw_conn.close()


# ---------------------------------------------------------------------------
# Estrategia 5: COPY raw + FK mapping en SQL (psycopg3 binario)
# ---------------------------------------------------------------------------
def upsert_copy_sql_v3(db_name, raw_df):
    conn_str = (
        f"host={settings.DB_HOST} port={settings.DB_PORT} "
        f"dbname={db_name} user={settings.DB_USER} password={settings.DB_PASSWORD}"
    )
    with psycopg.connect(conn_str) as conn:
        with conn.cursor() as cur:
            cur.execute(RAW_DDL)

            buf = io.StringIO()
            subset = raw_df[RAW_COLS].copy()
            int_cols = [
                "id",
                "entidad_id",
                "cve_mun",
                "localidad_id",
                "rango_personal_id",
                "tipo_establecimiento_id",
            ]
            for col in subset.columns:
                if col in int_cols:
                    subset[col] = subset[col].apply(lambda v: str(int(v)) if v is not None else "\\N")
                elif col == "codigo_actividad":
                    subset[col] = subset[col].apply(lambda v: str(int(float(v))) if v is not None else "\\N")
                else:
                    subset[col] = subset[col].apply(lambda v: str(v).replace("\\", "\\\\") if v is not None else "\\N")
            subset.to_csv(buf, sep="\t", header=False, index=False, quoting=3)
            buf.seek(0)

            logger.info(f"  COPY {len(subset):,} raw rows to tmp_raw (psycopg3)")
            with cur.copy(f"COPY tmp_raw ({', '.join(RAW_COLS)}) FROM STDIN (FORMAT TEXT)") as copy:
                while data := buf.read(8192):
                    copy.write(data.encode())

            logger.info(f"  INSERT INTO {STG_TABLE} FROM tmp_raw with SQL JOINs")
            cur.execute(INSERT_FROM_RAW)

        conn.commit()


# ---------------------------------------------------------------------------
# Run load
# ---------------------------------------------------------------------------
def run_load(strategy, db_name, df, catalogs, chunk_size):
    engine = create_engine(db_url(db_name), pool_pre_ping=True)
    Session = sessionmaker(bind=engine, expire_on_commit=False)
    timings = {}

    session = Session()
    try:
        with Timer("load_catalogs") as t:
            load_catalogs(session, catalogs)
        timings["load_catalogs"] = t.elapsed

        if strategy in ("copy_sql", "copy_sql_v3"):
            timings["map_foreign_keys"] = 0.0
            session.commit()

            raw_df = df.astype(object).where(df.notna(), None)
            with Timer("upsert_establecimientos") as t:
                if strategy == "copy_sql":
                    upsert_copy_sql(engine, raw_df)
                else:
                    upsert_copy_sql_v3(db_name, raw_df)
            timings["upsert_establecimientos"] = t.elapsed

        else:
            with Timer("map_foreign_keys") as t:
                mapped_df = map_foreign_keys(session, df)
            timings["map_foreign_keys"] = t.elapsed

            session.commit()

            cols = get_stg_columns()

            with Timer("upsert_establecimientos") as t:
                if strategy == "sqlalchemy":
                    records = df_to_records(mapped_df, cols)
                    upsert_sqlalchemy(session, records, cols, chunk_size)
                    session.commit()

                elif strategy == "execute_values":
                    records = df_to_records(mapped_df, cols)
                    upsert_execute_values(engine, records, cols, chunk_size)

                elif strategy == "copy_temp":
                    upsert_copy_temp(engine, mapped_df, cols)

            timings["upsert_establecimientos"] = t.elapsed

        with engine.connect() as conn:
            count = conn.execute(text(f"SELECT count(*) FROM {STG_TABLE}")).scalar()
        timings["total_records"] = count

    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
        engine.dispose()

    timings["total"] = timings["load_catalogs"] + timings["map_foreign_keys"] + timings["upsert_establecimientos"]
    return timings


def print_results(all_timings):
    phases = ["load_catalogs", "map_foreign_keys", "upsert_establecimientos", "total"]
    strategies = list(all_timings.keys())

    logger.info("")
    logger.info("=" * 100)
    baseline_key = strategies[0]
    baseline = all_timings[baseline_key]

    col_w = 18
    logger.info(f"RESULTADOS (baseline = {baseline_key})")
    logger.info("=" * 100)

    header = f"{'Fase':<28}"
    for s in strategies:
        header += f" {s:>{col_w}}"
    logger.info(header)
    logger.info("-" * 100)

    for phase in phases:
        row = f"{phase:<28}"
        for s in strategies:
            val = all_timings[s][phase]
            b_val = baseline[phase]
            speedup = (b_val / val) if val > 0 else float("inf")
            cell = f"{val:.1f}s ({speedup:.1f}x)" if val > 0 else "— (n/a)"
            row += f" {cell:>{col_w}}"
        logger.info(row)

    logger.info("-" * 100)
    logger.info(f"Registros cargados: {baseline['total_records']:,}")
    logger.info("=" * 100)


def main():
    parser = argparse.ArgumentParser(description="Benchmark estrategias de carga para DENUE")
    parser.add_argument("--entidades", type=str, default="1", help="IDs de entidades separados por coma (default: 1)")
    parser.add_argument("--drop-dbs", action="store_true", help="Eliminar las bases de prueba al finalizar")
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=settings.CHUNK_SIZE,
        help=f"Chunk size para upsert (default: {settings.CHUNK_SIZE})",
    )
    args = parser.parse_args()

    entidades = [int(e) for e in args.entidades.split(",")]
    total_strategies = len(STRATEGIES)

    logger.info("=" * 80)
    logger.info("BENCHMARK: estrategias de carga para stg_establecimientos")
    logger.info(f"Estrategias: {', '.join(STRATEGIES)}")
    logger.info(f"Entidades: {entidades}")
    logger.info(f"Chunk size: {args.chunk_size:,}")
    logger.info("=" * 80)

    logger.info("[1] Obteniendo datos reales")
    df, catalogs = get_data(entidades)
    if df.empty:
        logger.error("No hay datos. Ejecutar extract+transform primero.")
        sys.exit(1)
    logger.info(f"Rows a cargar: {len(df):,}")

    db_names = {s: db_name_for(s) for s in STRATEGIES}

    logger.info("[2] Creando bases de datos de prueba")
    for s in STRATEGIES:
        create_database(db_names[s])

    all_timings = {}
    try:
        logger.info("[3] Creando tablas")
        for s in STRATEGIES:
            create_tables(db_names[s])

        for i, strategy in enumerate(STRATEGIES, start=1):
            logger.info("")
            logger.info(f"[{i + 3}] Estrategia: {strategy.upper()}")
            logger.info("-" * 40)
            all_timings[strategy] = run_load(strategy, db_names[strategy], df, catalogs, args.chunk_size)

        print_results(all_timings)

    finally:
        if args.drop_dbs:
            logger.info("Limpiando bases de prueba")
            for s in STRATEGIES:
                drop_database(db_names[s])
        else:
            logger.info(f"Bases conservadas: {', '.join(db_names.values())}")


if __name__ == "__main__":
    main()
