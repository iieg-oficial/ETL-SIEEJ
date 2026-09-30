"""Descubrimiento de cargas en Acervo, con el cliente S3 sustituido por un doble."""

import json

import pytest

from core.acervo import list_uploads, normalize
from core.acervo.client import Upload

PREFIX = "formulario/"
DEPENDENCIA = "Secretaría de Educación"


def _envio(persona: str, archivos: list[dict], estado: str = "enviado", dependencia: str = DEPENDENCIA) -> dict:
    return {
        "envio": {"id": 1, "estado": estado, "actualizado_en": "2026-09-10 21:43:10+00:00"},
        "datos": {
            "general": {"nombre_de_la_dependencia": dependencia, "nombre_del_conjunto_de_datos": "Aulas google"},
            "conunto_datos": [{"fecha_de_corte_del_archivo": "2026-09-10", "fecha_de_actualizacion": "2026-09-01"}],
        },
        "archivos": archivos,
    }


def _archivo(nombre: str, subido_en: str) -> dict:
    return {
        "field_path": "conunto_datos[0].carga_de_datos",
        "object_key": f"{PREFIX}persona/conunto_datos-0.carga_de_datos/{nombre}",
        "filename_original": nombre,
        "size_bytes": 10,
        "subido_en": subido_en,
    }


class _FakeS3:
    """Doble del cliente S3: solo devuelve lo que list_uploads consulta."""

    def __init__(self, envios: dict[str, dict]):
        self._envios = envios

    def get_paginator(self, _operation):
        contents = []
        for key, envio in self._envios.items():
            contents.append({"Key": key, "ETag": '"abc123"'})
            for archivo in envio["archivos"]:
                contents.append({"Key": archivo["object_key"], "ETag": '"def456"'})

        class _Paginator:
            @staticmethod
            def paginate(**_kwargs):
                return [{"Contents": contents}]

        return _Paginator()

    def get_object(self, Bucket, Key):  # noqa: N803 - firma de boto3
        payload = json.dumps(self._envios[Key]).encode()
        return {"Body": type("Body", (), {"read": lambda self: payload})()}


def _listar(envios: dict[str, dict], **kwargs) -> list[Upload]:
    return list_uploads(DEPENDENCIA, client=_FakeS3(envios), bucket="sieej", prefix=PREFIX, **kwargs)


def test_un_envio_con_un_archivo_devuelve_una_carga():
    envios = {f"{PREFIX}persona/envio.json": _envio("persona", [_archivo("a.csv", "2026-09-10 21:31:00+00:00")])}

    assert len(_listar(envios)) == 1


def test_varios_archivos_del_mismo_campo_colapsan_al_mas_reciente():
    # Quien captura puede reemplazar el archivo antes de enviar, y el envío los conserva todos.
    envios = {
        f"{PREFIX}persona/envio.json": _envio(
            "persona",
            [
                _archivo("viejo.xlsx", "2026-09-10 21:31:00+00:00"),
                _archivo("nuevo.csv", "2026-09-10 21:42:00+00:00"),
            ],
        )
    }

    uploads = _listar(envios)

    assert len(uploads) == 1
    assert uploads[0].filename == "nuevo.csv"


def test_los_borradores_se_descartan():
    envios = {
        f"{PREFIX}persona/envio.json": _envio(
            "persona", [_archivo("a.csv", "2026-09-10 21:31:00+00:00")], estado="en_proceso"
        )
    }

    assert _listar(envios) == []


def test_se_pueden_aceptar_todos_los_estados():
    envios = {
        f"{PREFIX}persona/envio.json": _envio(
            "persona", [_archivo("a.csv", "2026-09-10 21:31:00+00:00")], estado="en_proceso"
        )
    }

    assert len(_listar(envios, estado=None)) == 1


def test_los_envios_de_otra_dependencia_se_descartan():
    envios = {
        f"{PREFIX}otra/envio.json": _envio(
            "otra", [_archivo("a.csv", "2026-09-10 21:31:00+00:00")], dependencia="Secretaría de Salud"
        )
    }

    assert _listar(envios) == []


def test_la_dependencia_se_compara_sin_acentos_ni_mayusculas():
    envios = {
        f"{PREFIX}persona/envio.json": _envio(
            "persona", [_archivo("a.csv", "2026-09-10 21:31:00+00:00")], dependencia="SECRETARIA DE EDUCACION"
        )
    }

    assert len(_listar(envios)) == 1


def test_la_carga_trae_las_fechas_del_formulario():
    envios = {f"{PREFIX}persona/envio.json": _envio("persona", [_archivo("a.csv", "2026-09-10 21:31:00+00:00")])}

    upload = _listar(envios)[0]

    assert upload.fecha_corte == "2026-09-10"
    assert upload.fecha_actualizacion == "2026-09-01"


@pytest.mark.parametrize(
    ("etag", "es_md5"),
    [("abc123", True), ("abc123-2", False), ("", False)],
)
def test_el_etag_multiparte_no_sirve_como_hash_de_contenido(etag, es_md5):
    upload = Upload(
        object_key="k",
        filename="f",
        size=1,
        uploaded_at="2026-09-10",
        envio="persona",
        envio_id=1,
        conjunto="Aulas google",
        updated_at="2026-09-10",
        field_path="conunto_datos[0].carga_de_datos",
        fecha_corte="2026-09-10",
        fecha_actualizacion="2026-09-01",
        etag=etag,
    )

    assert upload.etag_is_md5 is es_md5


def test_normalize_conserva_los_espacios():
    # A diferencia de normalize_text, que los convierte en guiones bajos.
    assert normalize("Secretaría  de   Educación") == "secretaria de educacion"
