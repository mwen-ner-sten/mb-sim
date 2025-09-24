"""Main CLI entry point for mb-sim."""

import argparse
import logging
import sys
from typing import Optional

from mb_sim.simulator.runtime import SimulationRuntime
from mb_sim.protocols.transport_manager import TransportManager
from mb_sim.protocols.modbus_server import TransportConfig, TransportType


def setup_logging(level: str = "INFO") -> None:
    """Set up logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


def create_parser() -> argparse.ArgumentParser:
    """Create the main argument parser."""
    parser = argparse.ArgumentParser(
        description="MB-Sim - Modbus Simulator",
        prog="mb-sim"
    )

    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Set the logging level"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Serve command
    serve_parser = subparsers.add_parser("serve", help="Start the Modbus simulator")
    serve_parser.add_argument(
        "--scenario",
        help="Scenario file to load"
    )
    serve_parser.add_argument(
        "--transport",
        choices=["tcp", "rtu"],
        default="tcp",
        help="Transport type (default: tcp)"
    )
    serve_parser.add_argument(
        "--host",
        default="localhost",
        help="Host to bind to (default: localhost)"
    )
    serve_parser.add_argument(
        "--port",
        type=int,
        default=1502,
        help="Port to bind to (default: 1502)"
    )
    serve_parser.add_argument(
        "--serial-port",
        default="/dev/ttyUSB0",
        help="Serial port for RTU (default: /dev/ttyUSB0)"
    )

    return parser


def handle_serve(args: argparse.Namespace) -> int:
    """Handle the serve command."""
    try:
        # Set up logging
        setup_logging(getattr(args, 'log_level', 'INFO'))

        # Create simulation runtime
        runtime = SimulationRuntime()

        # Load scenario or create default device
        if args.scenario:
            from mb_sim.scenario.scenario_manager import ScenarioManager

            scenario_manager = ScenarioManager()
            scenario = scenario_manager.load_scenario(args.scenario)

            print(f"Loaded scenario: {scenario.name}")
            print(f"Description: {scenario.description}")
            print(f"Devices: {len(scenario.devices)}")

            # Add devices from scenario to runtime
            for device in scenario.devices.values():
                # Create a device descriptor for the runtime
                class DeviceDescriptor:
                    def __init__(self, device_id, name, registers):
                        self.device_id = device_id
                        self.name = name
                        self.registers = registers

                descriptor = DeviceDescriptor(
                    device_id=device.config.device_id,
                    name=device.config.name,
                    registers=device.list_holding_registers()
                )

                runtime.add_device(descriptor)
        else:
            # Create default device
            from mb_sim.models.device import DeviceConfig
            from mb_sim.models.register_map import RegisterDefinition

            device_config = DeviceConfig(
                device_id=1,
                name="Default Device",
                description="Default simulated device"
            )

            # Add some default registers
            default_registers = [
                RegisterDefinition(address=40001, value=123),
                RegisterDefinition(address=40002, value=456),
                RegisterDefinition(address=40003, value=789),
            ]

            device = runtime.add_device(
                type("DeviceDescriptor", (), {
                    "device_id": 1,
                    "name": "Default Device",
                    "registers": default_registers
                })()
            )

        # Create transport configuration
        transport_config = TransportConfig(
            transport_type=TransportType(args.transport),
            host=args.host,
            port=args.port,
            serial_port=args.serial_port
        )

        # Create transport manager
        transport_manager = TransportManager()

        # Add all devices to transport
        device_map = {}
        for device in runtime.list_devices():
            device_map[device.config.device_id] = device

        transport_manager.add_transport(
            "main",
            transport_config,
            device_map
        )

        # Start the server
        print(f"Starting Modbus {args.transport.upper()} server on {args.host}:{args.port}")
        print("Press Ctrl+C to stop the server")

        # Run the event loop
        import asyncio
        loop = asyncio.get_event_loop()
        loop.run_until_complete(transport_manager.start_all())

        # Keep running until interrupted
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            print("\nStopping server...")
            loop.run_until_complete(transport_manager.stop_all())

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def main(args: Optional[list] = None) -> int:
    """Main entry point for the CLI."""
    parser = create_parser()

    # Parse known args to handle global options
    parsed_args, remaining = parser.parse_known_args(args)

    if not parsed_args.command:
        parser.print_help()
        return 1

    if parsed_args.command == "serve":
        return handle_serve(parsed_args)

    return 0


def serve_main(args: Optional[list] = None) -> int:
    """Entry point for just the serve command (for testing)."""
    parser = create_parser()
    parsed_args = parser.parse_args(args)

    if parsed_args.command == "serve":
        return handle_serve(parsed_args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())