from mb_sim.models.register_map import RegisterDefinition, RegisterMap


def test_add_and_get_register_value() -> None:
    register_map = RegisterMap()
    register_map.add_register(RegisterDefinition(address=1, value=10))

    assert register_map.get_value(1) == 10


def test_set_value_updates_register() -> None:
    register_map = RegisterMap([RegisterDefinition(address=2, value=5)])

    register_map.set_value(2, 42)

    assert register_map.get_value(2) == 42


def test_unknown_register_raises_key_error() -> None:
    register_map = RegisterMap()

    try:
        register_map.get_value(99)
    except KeyError as exc:
        assert "99" in str(exc)
    else:
        raise AssertionError("Expected KeyError for missing register")

