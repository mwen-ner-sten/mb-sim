"""Device model that aggregates register maps for Modbus simulation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from .register_map import RegisterDefinition, RegisterMap


@dataclass
class DeviceConfig:
    device_id: int
    name: str = ""
    description: str = ""


class Device:
    """Represents a simulated Modbus device with holding registers."""

    def __init__(self, config: DeviceConfig) -> None:
        self.config = config
        self.holding_registers = RegisterMap()

    def add_holding_register(self, definition: RegisterDefinition) -> None:
        self.holding_registers.add_register(definition)

    def read_holding_register(self, address: int) -> int:
        return self.holding_registers.get_value(address)

    def write_holding_register(self, address: int, value: int) -> None:
        self.holding_registers.set_value(address, value)

    def list_holding_registers(self) -> List[RegisterDefinition]:
        return [
            RegisterDefinition(address=address, value=value)
            for address, value in self.holding_registers.items()
        ]

    @property
    def display_name(self) -> str:
        if self.config.name:
            return self.config.name
        return f"Device {self.config.device_id}"

