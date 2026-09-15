from __future__ import annotations

from dataclasses import dataclass, field

import requests
from requests.exceptions import ChunkedEncodingError, ConnectionError, HTTPError, Timeout
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

from core.utils.logger import get_console_logger

logger = get_console_logger(__name__)

RETRY_ATTEMPTS = 5
SERVER_ERROR_STATUS = 500
NOT_FOUND_STATUS = 404

# Claves de connectionParameters que este script gestiona activamente en cada
# datastore. Cualquier otra clave que ya exista (ej. "fetch size" ajustado a
# mano en la UI) se preserva tal cual -- ver _build_datastore_payload.
_MANAGED_DATASTORE_KEYS = (
    "host",
    "port",
    "database",
    "schema",
    "user",
    "passwd",
    "dbtype",
    "Expose primary keys",
    "validate connections",
)

# Campos del featureType que este script gestiona activamente. El resto
# (title/abstract/keywords/metadata con estilos o virtual tables manuales)
# se preserva si el featureType ya existía -- ver _build_featuretype_payload.
_MANAGED_FEATURETYPE_KEYS = ("name", "nativeName", "srs", "projectionPolicy", "enabled", "attributes", "metadata")


class GeoServerError(RuntimeError):
    """Error no transitorio del REST API de GeoServer (4xx distinto de 404, payload inválido, etc.)."""


def _is_transient(exception: BaseException) -> bool:
    if isinstance(exception, ConnectionError | Timeout | ChunkedEncodingError):
        return True
    if isinstance(exception, HTTPError) and exception.response is not None:
        return exception.response.status_code >= SERVER_ERROR_STATUS
    return False


def _log_retry(state) -> None:
    logger.warning(f"[geoserver] Retry attempt {state.attempt_number} after {state.outcome.exception()}")


def _mask_password(payload: dict | None) -> dict | None:
    """Devuelve una copia superficial del payload con 'passwd' enmascarado, solo para logging."""
    if not payload or "dataStore" not in payload:
        return payload
    masked = {**payload, "dataStore": {**payload["dataStore"]}}
    conn = masked["dataStore"].get("connectionParameters")
    if conn and "entry" in conn:
        masked["dataStore"]["connectionParameters"] = {
            "entry": [{**e, "$": "***"} if e.get("@key") == "passwd" else e for e in conn["entry"]]
        }
    return masked


@dataclass
class GeoServerClient:
    base_url: str  # ej. "https://10.25.7.4/sextante/rest", sin slash final
    user: str
    password: str
    verify_ssl: bool = False
    timeout: int = 30
    session: requests.Session = field(default_factory=requests.Session, init=False)

    def __post_init__(self) -> None:
        self.base_url = self.base_url.rstrip("/")
        self.session.auth = (self.user, self.password)
        self.session.headers.update({"Accept": "application/json", "Content-Type": "application/json"})

    @retry(
        stop=stop_after_attempt(RETRY_ATTEMPTS),
        wait=wait_exponential(multiplier=2, min=2, max=30),
        retry=retry_if_exception(_is_transient),
        before_sleep=_log_retry,
        reraise=True,
    )
    def _request(
        self,
        method: str,
        path: str,
        *,
        json_body: dict | None = None,
        params: dict | None = None,
        expect: tuple[int, ...] = (),
    ) -> requests.Response:
        url = f"{self.base_url}{path}"
        response = self.session.request(
            method, url, json=json_body, params=params, timeout=self.timeout, verify=self.verify_ssl
        )
        if response.status_code >= SERVER_ERROR_STATUS:
            response.raise_for_status()
        if expect and response.status_code not in expect and response.status_code != NOT_FOUND_STATUS:
            raise GeoServerError(f"{method} {url} -> {response.status_code}: {response.text[:500]}")
        return response

    # ---------------------------------------------------------------- workspace
    def get_workspace(self, name: str) -> dict | None:
        response = self._request("GET", f"/workspaces/{name}.json")
        if response.status_code == NOT_FOUND_STATUS:
            return None
        response.raise_for_status()
        return response.json()

    def ensure_workspace(self, name: str) -> None:
        if self.get_workspace(name) is not None:
            logger.info(f"[workspace] {name} ya existe")
            return
        self._request("POST", "/workspaces", json_body={"workspace": {"name": name}}, expect=(201,))
        logger.info(f"[workspace] {name} creado")

    # ---------------------------------------------------------------- datastore
    def get_datastore(self, workspace: str, name: str) -> dict | None:
        response = self._request("GET", f"/workspaces/{workspace}/datastores/{name}.json")
        if response.status_code == NOT_FOUND_STATUS:
            return None
        response.raise_for_status()
        return response.json()

    def ensure_postgis_datastore(
        self,
        workspace: str,
        name: str,
        *,
        host: str,
        port: str | int,
        database: str,
        schema: str,
        user: str,
        password: str,
        expose_primary_keys: bool = True,
    ) -> None:
        existing = self.get_datastore(workspace, name)
        payload = self._build_datastore_payload(
            workspace,
            name,
            host=host,
            port=port,
            database=database,
            schema=schema,
            user=user,
            password=password,
            expose_primary_keys=expose_primary_keys,
            existing=existing,
        )
        logger.debug(f"[datastore] payload: {_mask_password(payload)}")
        if existing is None:
            self._request("POST", f"/workspaces/{workspace}/datastores", json_body=payload, expect=(201,))
            logger.info(f"[datastore] {workspace}/{name} creado")
        else:
            self._request("PUT", f"/workspaces/{workspace}/datastores/{name}.json", json_body=payload, expect=(200,))
            logger.info(f"[datastore] {workspace}/{name} actualizado")

    @staticmethod
    def _build_datastore_payload(
        workspace: str,
        name: str,
        *,
        host: str,
        port: str | int,
        database: str,
        schema: str,
        user: str,
        password: str,
        expose_primary_keys: bool,
        existing: dict | None,
    ) -> dict:
        """Arma el JSON completo de dataStore. Si `existing` viene dado, parte de
        su connectionParameters (preservando cualquier clave no gestionada aquí,
        ej. 'fetch size' ajustado a mano en la UI) y solo sobreescribe las claves
        en _MANAGED_DATASTORE_KEYS. Nunca reenvía un 'passwd' existente (llega
        cifrado como 'crypt2:...') -- siempre usa la contraseña real en texto
        plano que se le pasa a esta función.
        """
        entries: dict[str, str] = {}
        if existing is not None:
            for entry in existing["dataStore"]["connectionParameters"]["entry"]:
                entries[entry["@key"]] = entry["$"]

        entries.update(
            {
                "host": str(host),
                "port": str(port),
                "database": database,
                "schema": schema,
                "user": user,
                "passwd": password,
                "dbtype": "postgis",
                "Expose primary keys": str(expose_primary_keys).lower(),
                "validate connections": "true",
            }
        )

        return {
            "dataStore": {
                "name": name,
                "type": "PostGIS",
                "enabled": True,
                "workspace": {"name": workspace},
                "connectionParameters": {"entry": [{"@key": k, "$": v} for k, v in entries.items()]},
            }
        }

    # ------------------------------------------------------------- feature type
    def get_featuretype(self, workspace: str, datastore: str, name: str) -> dict | None:
        response = self._request("GET", f"/workspaces/{workspace}/datastores/{datastore}/featuretypes/{name}.json")
        if response.status_code == NOT_FOUND_STATUS:
            return None
        response.raise_for_status()
        return response.json()

    def list_featuretypes(self, workspace: str, datastore: str) -> list[str]:
        """Nombres de todos los featuretypes registrados hoy en `datastore`, para
        que el caller pueda detectar huérfanos (ver remove_orphan_featuretypes
        en scripts/create_geoserver_layers.py).
        """
        response = self._request(
            "GET", f"/workspaces/{workspace}/datastores/{datastore}/featuretypes.json", expect=(200,)
        )
        if response.status_code == NOT_FOUND_STATUS:
            return []
        response.raise_for_status()
        # GeoServer devuelve "" en vez de {} cuando el datastore no tiene featuretypes.
        feature_types = response.json().get("featureTypes") or {}
        entries = feature_types.get("featureType", [])
        return [entry["name"] for entry in entries]

    def delete_featuretype(self, workspace: str, datastore: str, name: str, *, recurse: bool = True) -> None:
        """Borra un featuretype y, con recurse=True, su layer asociada."""
        self._request(
            "DELETE",
            f"/workspaces/{workspace}/datastores/{datastore}/featuretypes/{name}.json",
            params={"recurse": str(recurse).lower()},
            expect=(200,),
        )
        logger.info(f"[featuretype] {workspace}/{datastore}/{name} eliminado (huérfano)")

    def ensure_featuretype(
        self,
        workspace: str,
        datastore: str,
        *,
        layer_name: str,
        managed_fields: dict,
    ) -> None:
        """`managed_fields` trae solo los campos que este script controla (ver
        _MANAGED_FEATURETYPE_KEYS: name/nativeName/srs/projectionPolicy/enabled/
        attributes/metadata). Si el featureType ya existe, se parte de su JSON
        completo y solo se sobreescriben esas claves -- title/abstract/keywords
        y cualquier otro metadata (estilos, virtual tables hechas a mano) que no
        estén en managed_fields se preservan intactos.
        """
        existing = self.get_featuretype(workspace, datastore, layer_name)
        payload = self._build_featuretype_payload(managed_fields, existing=existing)
        params = {"recalculate": "nativebbox,latlonbbox"}
        if existing is None:
            self._request(
                "POST",
                f"/workspaces/{workspace}/datastores/{datastore}/featuretypes",
                json_body=payload,
                params=params,
                expect=(201,),
            )
            logger.info(f"[featuretype] {workspace}/{datastore}/{layer_name} creado")
        else:
            self._request(
                "PUT",
                f"/workspaces/{workspace}/datastores/{datastore}/featuretypes/{layer_name}.json",
                json_body=payload,
                params=params,
                expect=(200,),
            )
            logger.info(f"[featuretype] {workspace}/{datastore}/{layer_name} actualizado")

    @staticmethod
    def _build_featuretype_payload(managed_fields: dict, *, existing: dict | None) -> dict:
        feature_type: dict = {}
        if existing is not None:
            feature_type.update(existing["featureType"])
        for key in _MANAGED_FEATURETYPE_KEYS:
            if key in managed_fields:
                feature_type[key] = managed_fields[key]
            elif existing is None and key not in feature_type:
                continue
        return {"featureType": feature_type}
