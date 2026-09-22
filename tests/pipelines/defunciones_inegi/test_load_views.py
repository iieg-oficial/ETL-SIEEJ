from core.pipelines.defunciones_inegi.stages import load


def test_action_refreshes_maternal_mortality_view(monkeypatch):
    loader = load.DefuncionesInegiLoad()

    class SessionContext:
        def __enter__(self):
            class Session:
                def commit(self):
                    pass

            return Session()

        def __exit__(self, exc_type, exc_value, traceback):
            return False

    class DatabaseStub:
        def connect(self):
            pass

        def get_session(self):
            return SessionContext()

    db = DatabaseStub()
    loader.db = db
    monkeypatch.setattr(loader, "_load_editions", lambda *_: {})
    monkeypatch.setattr(loader, "_load_catalogs", lambda *_: None)
    monkeypatch.setattr(loader, "_build_mappings", lambda *_: {})
    refreshed = []
    monkeypatch.setattr(loader, "_refresh_views", lambda: refreshed.append(True))

    assert loader.action({"editions": [], "catalogs": {}}) == {"defunciones": 0}
    assert refreshed == [True]


def test_refresh_views_targets_maternal_mortality_view(monkeypatch):
    loader = load.DefuncionesInegiLoad()
    db = object()
    loader.db = db
    refreshed = []
    monkeypatch.setattr(load, "refresh_materialized_views", lambda database, views: refreshed.append((database, views)))

    loader._refresh_views()
