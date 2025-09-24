from mb_sim.models.device import Device, DeviceConfig
from mb_sim.models.register_map import RegisterDefinition


def test_device_holding_register_round_trip() -> None:
    config = DeviceConfig(device_id=1, name="Pump")
    device = Device(config)

    device.add_holding_register(RegisterDefinition(address=40001, value=7))
    assert device.read_holding_register(40001) == 7

    device.write_holding_register(40001, 11)

    assert device.read_holding_register(40001) == 11


def test_device_display_name_defaults_to_device_id() -> None:
    config = DeviceConfig(device_id=3)
    device = Device(config)

    assert device.display_name == "Device 3"


def test_device_list_holding_registers_returns_sorted_definitions() -> None:
    config = DeviceConfig(device_id=5, name="Filter")
    device = Device(config)
    device.add_holding_register(RegisterDefinition(address=40002, value=21))
    device.add_holding_register(RegisterDefinition(address=40001, value=7))

    registers = device.list_holding_registers()

    assert registers[0].address == 40001
    assert registers[1].value == 21

