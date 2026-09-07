import os

import pandas as pd

os.environ.setdefault("GDRIVE_FILE_ID", "test-file-id")

from core.pipelines.participacion_ciudadana.stages import load


def test_action_refreshes_geographic_materialized_view(monkeypatch):
    loader = load.ParticipacionCiudadanaLoad()
    class DatabaseStub:
        pass

    db = DatabaseStub()
    loader.db = db

    class SessionContext:
        def __enter__(self):
            return object()

        def __exit__(self, exc_type, exc_value, traceback):
            return False

    monkeypatch.setattr(db, "connect", lambda: None, raising=False)
    monkeypatch.setattr(db, "get_session", lambda: SessionContext(), raising=False)
    monkeypatch.setattr(load, "count_records", lambda *_: 0)
    monkeypatch.setattr(load, "sync_id_sequence", lambda *_: None)
    monkeypatch.setattr(load, "bulk_insert", lambda *_: None)
    monkeypatch.setattr(load, "df_to_records", lambda *_: [])
    refreshed = []
    monkeypatch.setattr(load, "refresh_materialized_views", lambda database, views: refreshed.append((database, views)))

    result = loader.action(
        pd.DataFrame(
            [{"entidad_id": 14, "municipio_id": 39, "porc_participacion": 61.2, "anio": 2021}]
        )
    )

    assert result == {"records_before": 0}
    assert refreshed == [(db, ["vm_porcentaje_participacion_geo"])]
