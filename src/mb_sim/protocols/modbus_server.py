"""Modbus server implementation supporting RTU and TCP transports."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional, Union

from pymodbus.datastore import ModbusServerContext
from pymodbus.datastore.context import ModbusDeviceContext
from pymodbus.server import ModbusTcpServer, ModbusSerialServer
from pymodbus import ModbusDeviceIdentification

from mb_sim.models.device import Device
from mb_sim.models.register_map import RegisterMap


class TransportType(Enum):
    """Supported Modbus transport types."""
    TCP = "tcp"
    RTU = "rtu"


@dataclass
class TransportConfig:
    """Configuration for a Modbus transport."""
    transport_type: TransportType
    host: str = "localhost"
    port: int = 502
    serial_port: str = "/dev/ttyUSB0"
    baudrate: int = 9600
    parity: str = "N"
    stopbits: int = 1
    bytesize: int = 8
    timeout: float = 0.1


class ModbusServer:
    """Modbus server that manages multiple slave devices over different transports."""

    def __init__(self, config: TransportConfig, device_map: Dict[int, Device]) -> None:
        self.config = config
        self.device_map = device_map
        self.logger = logging.getLogger(__name__)
        self._server: Optional[Union[ModbusTcpServer, ModbusSerialServer]] = None
        self._running = False

        # Create slave contexts for each device
        self._slave_contexts = self._create_slave_contexts()

        # Create server context with all slaves
        self._server_context = ModbusServerContext(
            devices=self._slave_contexts,
            single=False
        )

    def _create_slave_contexts(self) -> Dict[int, ModbusDeviceContext]:
        """Create Modbus slave contexts from device map."""
        contexts = {}

        for slave_id, device in self.device_map.items():
            # Create a datastore for this slave
            datastore = ModbusDeviceContext(
                di=RegisterMap(),  # Discrete inputs
                co=RegisterMap(),  # Coils
                hr=device.holding_registers,  # Holding registers
                ir=RegisterMap(),  # Input registers
            )
            contexts[slave_id] = datastore

        return contexts

    async def start(self) -> None:
        """Start the Modbus server."""
        if self._running:
            self.logger.warning("Server is already running")
            return

        self._running = True
        self.logger.info(f"Starting Modbus {self.config.transport_type.value} server")

        try:
            if self.config.transport_type == TransportType.TCP:
                await self._start_tcp_server()
            elif self.config.transport_type == TransportType.RTU:
                await self._start_rtu_server()
            else:
                raise ValueError(f"Unsupported transport type: {self.config.transport_type}")
        except Exception as e:
            self._running = False
            self.logger.error(f"Failed to start server: {e}")
            raise

    async def _start_tcp_server(self) -> None:
        """Start TCP server."""
        self.logger.info(f"Starting TCP server on {self.config.host}:{self.config.port}")

        # Set up device identification
        identity = ModbusDeviceIdentification()
        identity.VendorName = "MB-Sim"
        identity.ProductCode = "MBS"
        identity.VendorUrl = "https://wen-ner-sten.com"
        identity.ProductName = "Modbus Simulator"
        identity.ModelName = "MB-Sim v0.0.1"
        identity.MajorMinorRevision = "0.0.1"

        # Create TCP server
        self._server = ModbusTcpServer(
            context=self._server_context,
            identity=identity,
            address=(self.config.host, self.config.port),
        )

        # Start the server
        await self._server.serve_forever()

    async def _start_rtu_server(self) -> None:
        """Start RTU server."""
        self.logger.info(f"Starting RTU server on {self.config.serial_port}")

        # Set up device identification
        identity = ModbusDeviceIdentification()
        identity.VendorName = "MB-Sim"
        identity.ProductCode = "MBS"
        identity.VendorUrl = "https://wen-ner-sten.com"
        identity.ProductName = "Modbus Simulator"
        identity.ModelName = "MB-Sim v0.0.1"
        identity.MajorMinorRevision = "0.0.1"

        # Create RTU server
        self._server = ModbusSerialServer(
            context=self._server_context,
            identity=identity,
            port=self.config.serial_port,
            baudrate=self.config.baudrate,
            parity=self.config.parity,
            stopbits=self.config.stopbits,
            bytesize=self.config.bytesize,
            timeout=self.config.timeout,
        )

        # Start the server
        await self._server.serve_forever()

    async def stop(self) -> None:
        """Stop the Modbus server."""
        if not self._running:
            return

        self._running = False
        self.logger.info("Stopping Modbus server")

        if self._server:
            await self._server.shutdown()

    def is_running(self) -> bool:
        """Check if the server is running."""
        return self._running and self._server and self._server.is_active()

    def get_slave_context(self, slave_id: int) -> Optional[ModbusDeviceContext]:
        """Get the slave context for a specific slave ID."""
        return self._slave_contexts.get(slave_id)