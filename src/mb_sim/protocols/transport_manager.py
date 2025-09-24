"""Transport manager for handling multiple Modbus servers."""

from __future__ import annotations

import asyncio
import logging
from typing import Dict, List

from .modbus_server import ModbusServer, TransportConfig
from mb_sim.models.device import Device


class TransportManager:
    """Manages multiple Modbus servers for different transports."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.servers: Dict[str, ModbusServer] = {}
        self._running = False

    def add_transport(self, name: str, config: TransportConfig, device_map: Dict[int, Device]) -> None:
        """Add a new transport server."""
        if name in self.servers:
            raise ValueError(f"Transport '{name}' already exists")

        server = ModbusServer(config, device_map)
        self.servers[name] = server
        self.logger.info(f"Added transport '{name}' with {len(device_map)} devices")

    def remove_transport(self, name: str) -> None:
        """Remove a transport server."""
        if name not in self.servers:
            raise ValueError(f"Transport '{name}' not found")

        server = self.servers[name]
        if server.is_running():
            asyncio.create_task(server.stop())

        del self.servers[name]
        self.logger.info(f"Removed transport '{name}'")

    def get_transport(self, name: str) -> ModbusServer:
        """Get a transport server by name."""
        if name not in self.servers:
            raise ValueError(f"Transport '{name}' not found")

        return self.servers[name]

    def list_transports(self) -> List[str]:
        """List all transport names."""
        return list(self.servers.keys())

    async def start_all(self) -> None:
        """Start all transport servers."""
        if self._running:
            self.logger.warning("Transport manager is already running")
            return

        self._running = True
        self.logger.info(f"Starting {len(self.servers)} transport servers")

        tasks = []
        for name, server in self.servers.items():
            task = asyncio.create_task(server.start(), name=f"server-{name}")
            tasks.append(task)

        try:
            # Wait for all servers to start
            await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            self.logger.error(f"Error starting servers: {e}")
            self._running = False
            raise

    async def stop_all(self) -> None:
        """Stop all transport servers."""
        if not self._running:
            return

        self._running = False
        self.logger.info("Stopping all transport servers")

        tasks = []
        for name, server in self.servers.items():
            task = asyncio.create_task(server.stop(), name=f"stop-{name}")
            tasks.append(task)

        await asyncio.gather(*tasks, return_exceptions=True)

    def is_running(self) -> bool:
        """Check if any servers are running."""
        return any(server.is_running() for server in self.servers.values())