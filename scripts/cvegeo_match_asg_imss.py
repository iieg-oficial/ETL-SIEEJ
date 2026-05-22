"""Matching de cat_municipio (IMSS/Jalisco) contra cvegeo_municipalities (INEGI).

Estrategia:
  1. Normaliza los nombres de ambas fuentes: minúsculas, sin acentos, sin
     artículos iniciales ('el ', 'la ', 'los ', 'las ', 'de ').
  2. Intenta match exacto sobre el nombre normalizado.
  3. Para los sin match, intenta match parcial (substring o prefijo).
  4. Imprime un reporte de matches y no-matches.
  5. Actualiza cat_municipio.cvegeo_municipio_id con los matches confirmados.

Uso:
    conda run -n etl python scripts/cvegeo_match_asg_imss.py [--dry-run]
"""

import argparse
import re
import unicodedata
from dataclasses import dataclass, field

import psycopg2

# ---------------------------------------------------------------------------
# Configuración local (test environment)
# ---------------------------------------------------------------------------
ASG_IMSS_DSN = "host=localhost port=5432 dbname=asg_imss user=test password=test"
CVEGEO_DSN = "host=localhost port=5432 dbname=cvegeo user=test password=test"
CMP_JALISCO = 14  # cve_ent en cvegeo_municipalities


# ---------------------------------------------------------------------------
# Normalización de nombres
# ---------------------------------------------------------------------------

_STOP_PREFIXES = re.compile(
    r"^(el |la |los |las |de |del |san |santa |santo |ciudad de |municipio de )",
    re.IGNORECASE,
)


def normalize(name: str) -> str:
    """Normaliza un nombre de municipio para comparación."""
    # Minúsculas
    name = name.lower().strip()
    # Quitar acentos
    name = unicodedata.normalize("NFD", name)
    name = "".join(c for c in name if unicodedata.category(c) != "Mn")
    # Quitar artículos/preposiciones iniciales (solo uno, iterativo)
    for _ in range(3):
        m = _STOP_PREFIXES.match(name)
        if m:
            name = name[m.end() :]
        else:
            break
    return name.strip()


# ---------------------------------------------------------------------------
# Estructuras de datos
# ---------------------------------------------------------------------------


@dataclass
class ImssEntry:
    id: int
    clave: str
    descripcion: str
    cvegeo_municipio_id: int | None


@dataclass
class CvegeoEntry:
    id: int
    cvegeo: int
    cve_mun: int
    nomgeo: str


@dataclass
class MatchResult:
    matched: list[tuple[ImssEntry, CvegeoEntry, str]] = field(default_factory=list)
    unmatched_imss: list[ImssEntry] = field(default_factory=list)
    unmatched_cvegeo: list[CvegeoEntry] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Lógica de matching
# ---------------------------------------------------------------------------


def fetch_imss_municipios(conn) -> list[ImssEntry]:
    cur = conn.cursor()
    cur.execute(
        """
        SELECT m.id, m.clave, m.descripcion, m.cvegeo_municipio_id
        FROM cat_municipio m
        JOIN cat_entidad e ON e.id = m.entidad_id
        WHERE e.clave = '14'
        ORDER BY m.clave
        """
    )
    return [ImssEntry(*row) for row in cur.fetchall()]


def fetch_cvegeo_municipios(conn) -> list[CvegeoEntry]:
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, cvegeo, cve_mun, nomgeo
        FROM cvegeo_municipalities
        WHERE cve_ent = %s
        ORDER BY cve_mun
        """,
        (CMP_JALISCO,),
    )
    return [CvegeoEntry(*row) for row in cur.fetchall()]


def match_municipios(imss: list[ImssEntry], cvegeo: list[CvegeoEntry]) -> MatchResult:
    result = MatchResult()

    # Índice cvegeo por nombre normalizado (puede haber duplicados: tomar primero)
    cvegeo_by_norm: dict[str, CvegeoEntry] = {}
    for entry in cvegeo:
        key = normalize(entry.nomgeo)
        cvegeo_by_norm.setdefault(key, entry)

    matched_cvegeo_ids: set[int] = set()

    for imss_entry in imss:
        norm_imss = normalize(imss_entry.descripcion)
        # 1. Exact match
        if norm_imss in cvegeo_by_norm:
            cv = cvegeo_by_norm[norm_imss]
            result.matched.append((imss_entry, cv, "exact"))
            matched_cvegeo_ids.add(cv.id)
            continue

        # 2. Partial match: IMSS name starts with cvegeo name or vice versa
        partial = None
        for norm_cv, cv in cvegeo_by_norm.items():
            if norm_imss.startswith(norm_cv) or norm_cv.startswith(norm_imss):
                partial = cv
                break

        if partial:
            result.matched.append((imss_entry, partial, "partial"))
            matched_cvegeo_ids.add(partial.id)
        else:
            result.unmatched_imss.append(imss_entry)

    # cvegeo entries with no IMSS match
    for cv in cvegeo:
        if cv.id not in matched_cvegeo_ids:
            result.unmatched_cvegeo.append(cv)

    return result


# ---------------------------------------------------------------------------
# Reporte y actualización
# ---------------------------------------------------------------------------


def print_report(result: MatchResult) -> None:
    total_imss = len(result.matched) + len(result.unmatched_imss)
    total_cvegeo = len(result.matched) + len(result.unmatched_cvegeo)

    print("\n" + "=" * 70)
    print("REPORTE: IMSS (cat_municipio Jalisco) ↔ INEGI (cvegeo_municipalities)")
    print("=" * 70)
    print(f"  Municipios IMSS (Jalisco, canónicos): {total_imss}")
    print(f"  Municipios INEGI (Jalisco):           {total_cvegeo}")
    print(f"  Matches exactos:  {sum(1 for *_, t in result.matched if t == 'exact')}")
    print(f"  Matches parciales:{sum(1 for *_, t in result.matched if t == 'partial')}")
    print(f"  Sin match (IMSS): {len(result.unmatched_imss)}")
    print(f"  Sin match (INEGI):{len(result.unmatched_cvegeo)}")

    # Matches
    print("\n--- MATCHES ---")
    print(f"{'IMSS clave':<10} {'IMSS desc':<35} {'INEGI nomgeo':<35} {'tipo'}")
    print("-" * 90)
    for imss_e, cv_e, mtype in sorted(result.matched, key=lambda x: x[0].descripcion):
        print(f"{imss_e.clave:<10} {imss_e.descripcion:<35} {cv_e.nomgeo:<35} {mtype}")

    # No match IMSS
    if result.unmatched_imss:
        print("\n--- SIN MATCH (IMSS → INEGI) ---")
        print(f"{'clave':<10} {'descripcion'}")
        print("-" * 50)
        for e in sorted(result.unmatched_imss, key=lambda x: x.descripcion):
            print(f"{e.clave:<10} {e.descripcion}")

    # No match cvegeo
    if result.unmatched_cvegeo:
        print("\n--- SIN MATCH (INEGI → IMSS) ---")
        print(f"{'cvegeo':<10} {'nomgeo'}")
        print("-" * 50)
        for e in sorted(result.unmatched_cvegeo, key=lambda x: x.nomgeo):
            print(f"{e.cvegeo:<10} {e.nomgeo}")

    print()


def update_cvegeo_ids(conn_asg, result: MatchResult) -> int:
    cur = conn_asg.cursor()
    updated = 0
    for imss_e, cv_e, _ in result.matched:
        cur.execute(
            "UPDATE cat_municipio SET cvegeo_municipio_id = %s WHERE id = %s",
            (cv_e.id, imss_e.id),
        )
        updated += 1
    conn_asg.commit()
    return updated


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description="Match IMSS municipios con cvegeo")
    parser.add_argument("--dry-run", action="store_true", help="Solo reporta, no actualiza la DB")
    args = parser.parse_args()

    conn_asg = psycopg2.connect(ASG_IMSS_DSN)
    conn_cvegeo = psycopg2.connect(CVEGEO_DSN)

    try:
        imss_entries = fetch_imss_municipios(conn_asg)
        cvegeo_entries = fetch_cvegeo_municipios(conn_cvegeo)

        if not imss_entries:
            print("⚠️  cat_municipio (Jalisco) está vacío. Ejecuta el bootstrap primero.")
            return

        result = match_municipios(imss_entries, cvegeo_entries)
        print_report(result)

        if not args.dry_run:
            n = update_cvegeo_ids(conn_asg, result)
            print(f"✅ cvegeo_municipio_id actualizado en {n} entradas de cat_municipio.")
        else:
            print("(dry-run: no se actualizó la base de datos)")
    finally:
        conn_asg.close()
        conn_cvegeo.close()


if __name__ == "__main__":
    main()
