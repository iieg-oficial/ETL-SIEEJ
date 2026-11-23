from core.pipelines.defunciones_inegi.stages import load


def test_action_refreshes_mortality_views(monkeypatch):
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

    loader.db = DatabaseStub()
    monkeypatch.setattr(loader, "_edition_years", lambda *_: [2024])
    monkeypatch.setattr(loader, "_load_editions", lambda *_: {2024: 1})
    monkeypatch.setattr(loader, "_load_catalogs", lambda *_: None)
    monkeypatch.setattr(loader, "_build_mappings", lambda *_: {})
    monkeypatch.setattr(loader, "_load_edition_facts", lambda *_: 10)
    refreshed = []
    monkeypatch.setattr(loader, "_refresh_views", lambda: refreshed.append(True))

    assert loader.action({"editions": [2024], "catalogs": {}}) == {"defunciones": 10, "editions": [2024]}
    assert refreshed == [True]


def test_refresh_views_targets_mortality_views(monkeypatch):
    loader = load.DefuncionesInegiLoad()
    db = object()
    loader.db = db
    refreshed = []
    monkeypatch.setattr(load, "refresh_materialized_views", lambda database, views: refreshed.append((database, views)))

    loader._refresh_views()
    assert refreshed == [(db, ["vm_mortalidad_materna_geo", "vm_mortalidad_infantil_geo", "vm_mortalidad_adulta_geo"])]
