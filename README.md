# MB-Sim: Modbus Simulator

A comprehensive Modbus simulator for testing and development, supporting both RTU and TCP transports with a modern GUI interface.

## Features

- **Modbus Protocol Support**: Full support for Modbus RTU and TCP with multiple concurrent slaves
- **Device Management**: Create and manage multiple simulated Modbus devices with custom register maps
- **Register Configuration**: Configure holding registers, coils, discrete inputs, and input registers
- **Scenario Management**: Load and save device configurations from YAML scenario files
- **Modern GUI**: PyQt6-based interface for device management, register editing, and real-time monitoring
- **Command Line Interface**: Full CLI for automated testing and scripting
- **Real-time Updates**: Live register value updates and activity logging

## Installation

### Prerequisites

- Python 3.11+
- Virtual environment (recommended)

### Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd mb-sim
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Install the package in development mode:
   ```bash
   pip install -e .
   ```

## Usage

### Command Line Interface

Start the Modbus simulator:
```bash
mb-sim serve --scenario scenarios/scenario_tcp_basic.yml --port 1502
```

Available options:
- `--scenario`: Load a specific scenario file
- `--transport`: Choose between `tcp` (default) or `rtu`
- `--host`: Server host (default: localhost)
- `--port`: Server port (default: 1502)
- `--log-level`: Set logging level (DEBUG, INFO, WARNING, ERROR)

### GUI Application

Launch the graphical interface:
```bash
python -m mb_sim.gui
```

The GUI provides:
- Device list with real-time status
- Register table with inline editing
- Activity logging
- Device and register management dialogs

### Creating Scenarios

Scenario files use YAML format and define devices with their register configurations:

```yaml
name: Basic TCP Scenario
description: A basic Modbus TCP scenario with holding registers
version: 0.0.1
devices:
  1:
    name: Pump Controller
    description: A simulated pump controller
    registers:
      holding_registers:
        - address: 40001
          value: 123
          label: Pump Status
        - address: 40002
          value: 456
          label: Flow Rate
```

## Development

### Project Structure

```
src/mb_sim/
├── cli/           # Command line interface
├── gui/           # PyQt6 GUI application
├── models/        # Device and register models
├── protocols/     # Modbus protocol implementation
├── scenario/      # Scenario file management
└── simulator/     # Simulation runtime

tests/
├── gui/           # GUI tests
├── models/        # Model tests
└── ...

scenarios/         # Scenario configuration files
docs/              # Documentation
```

### Running Tests

Execute the test suite:
```bash
make test
```

Run linting and formatting checks:
```bash
make lint
make format
```

### Development Commands

The project includes a Makefile with common development tasks:

- `make lint`: Run linting (ruff + black)
- `make test`: Execute tests with coverage
- `make sim`: Launch the simulator CLI
- `make format`: Format code with black
- `make check`: Run all checks (lint + test)

## Architecture

The simulator is built with a modular architecture:

- **Models**: Device and register abstractions
- **Protocols**: Modbus RTU/TCP implementation using pymodbus
- **Runtime**: Simulation management and device lifecycle
- **GUI**: PyQt6 interface for interactive management
- **CLI**: Command-line interface for automation

## Requirements

- Python 3.11+
- PyQt6: Modern GUI framework
- pymodbus: Modbus protocol implementation
- PyYAML: Scenario file parsing
- pytest: Testing framework
- ruff: Fast Python linter
- black: Code formatter

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass (`make check`)
6. Submit a pull request

## License

This project is licensed under the terms specified in the project guidelines.

## Contact

Mike Wennersten
- Email: mike@wen-ner-sten.com
- Homepage: wen-ner-sten.com