import argparse
import json
import logging
import sys

from core.indicadores import registro

# core.db loguea a stdout; aquí stdout es solo el JSON, así que su log se manda a stderr.
logging.getLogger("database").handlers = [logging.StreamHandler(sys.stderr)]


def _params(pares: list[str]) -> dict:
    try:
        return dict(par.split("=", 1) for par in pares)
    except ValueError:
        raise SystemExit("Los parámetros van como -p nombre=valor") from None


def main() -> None:
    parser = argparse.ArgumentParser(prog="python -m core.indicadores", description="Banco de indicadores")
    sub = parser.add_subparsers(dest="comando", required=True)

    p_listar = sub.add_parser("listar", help="Lista los indicadores del catálogo")
    p_listar.add_argument("--tema")
    p_listar.add_argument("--nivel", choices=["nacional", "estatal", "municipal"])

    p_describir = sub.add_parser("describir", help="Metadata completa de un indicador")
    p_describir.add_argument("id")

    p_ejecutar = sub.add_parser("ejecutar", help="Ejecuta un indicador y devuelve los datos")
    p_ejecutar.add_argument("id")
    p_ejecutar.add_argument("-p", dest="params", action="append", default=[], metavar="nombre=valor")

    args = parser.parse_args()

    if args.comando == "listar":
        salida = registro.listar(tema=args.tema, nivel=args.nivel)
    elif args.comando == "describir":
        salida = registro.obtener(args.id).metadata()
    else:
        salida = registro.ejecutar(args.id, **_params(args.params))

    print(json.dumps(salida, indent=2, ensure_ascii=False, default=str))


if __name__ == "__main__":
    try:
        main()
    except ValueError as e:
        sys.exit(f"❌ {e}")
