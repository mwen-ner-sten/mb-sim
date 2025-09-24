from mb_sim.gui.app import create_app


def test_create_app_sets_application_name(qtbot) -> None:  # type: ignore[no-untyped-def]
    app = create_app()
    assert app.applicationName() == "mb-sim"

