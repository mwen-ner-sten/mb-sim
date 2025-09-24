"""Simple in-memory register map for Modbus simulator MVP."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, MutableMapping, Optional, Tuple


RegisterValue = int


@dataclass
class RegisterDefinition:
    address: int
    value: RegisterValue = 0
    label: Optional[str] = None


class RegisterMap:
    """Tracks Modbus register values by address."""

    def __init__(self, initial: Optional[Iterable[RegisterDefinition]] = None) -> None:
        self._registers: MutableMapping[int, RegisterValue] = {}
        if initial:
            for definition in initial:
                self.add_register(definition)

    def add_register(self, definition: RegisterDefinition) -> None:
        if definition.address in self._registers:
            raise ValueError(f"Register {definition.address} already defined")
        self._registers[definition.address] = definition.value

    def set_value(self, address: int, value: RegisterValue) -> None:
        if address not in self._registers:
            raise KeyError(f"Unknown register {address}")
        self._registers[address] = value

    def get_value(self, address: int) -> RegisterValue:
        if address not in self._registers:
            raise KeyError(f"Unknown register {address}")
        return self._registers[address]

    def values(self) -> Dict[int, RegisterValue]:
        return dict(self._registers)

    def addresses(self) -> List[int]:
        return sorted(self._registers.keys())

    def items(self) -> List[Tuple[int, RegisterValue]]:
        return [(address, self._registers[address]) for address in self.addresses()]

    def remove_register(self, address: int) -> None:
        """Remove a register from the map."""
        if address not in self._registers:
            raise KeyError(f"Unknown register {address}")
        del self._registers[address]

