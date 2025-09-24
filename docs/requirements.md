# Modbus Simulator Requirements (v0.0.0.1)

*Initial documentation snapshot for MVP scope*

## 1. Purpose and Scope
- Deliver a desktop-oriented Modbus simulator capable of emulating hundreds of lightweight slave devices over both serial (RTU) and IP (TCP) transports.
- Provide tooling for creating, editing, and observing simulated register maps through a graphical interface and configuration files.
- Target Python 3.11+ with all runtime code under `src/mb_sim/` and mirrored tests under `tests/`.
- Prioritize validating Modbus master protocol stacks rather than modeling complex physical devices or domain-specific data flows.

## 2. Key Personas & Usage Scenarios
- **Automation Engineer**: Needs to validate a PLC or SCADA integration against a controllable Modbus server without live hardware.
- **Firmware Developer**: Exercises edge cases (timeouts, exception codes, invalid data) while developing Modbus master firmware.
- **QA Tester**: Runs automated regression suites against predefined register scenarios and expects reproducible outcomes.

## 3. Terminology
- **Slave / Server**: Simulated Modbus endpoint that responds to master requests (IDs 1–247).
- **Register**: Addressable Modbus data point (coil, discrete input, input register, holding register).
- **Scenario**: Declarative description (stored under `scenarios/`) defining one or more simulated devices with register maps and behaviors.
- **Behavior Profile**: Ruleset determining how registers respond (normal or specific error conditions).

## 4. Functional Requirements

### 4.1 Core Modbus Simulation
- Support the full Modbus function code suite required for read and write operations (1–6, 15, 16) and diagnostics (8) with an extension mechanism for less common codes.
- Emulate both Modbus RTU (serial) and Modbus TCP (IP) transports concurrently where possible.
- Maintain distinct slave instances addressable by slave ID, sharing a common runtime so hundreds of IDs may be online simultaneously on commodity hardware.
- Provide accurate protocol framing, timing, and CRC/MBAP header handling per transport by building on `pymodbus` primitives.
- Ensure parity with the `pymodbus` feature set so new protocol capabilities can be adopted with minimal changes.

### 4.2 Device & Slave Management
- Allow creation of a generic device template configurable per instance (name, description, slave ID, transport bindings).
- Support enabling/disabling individual slaves at runtime; disabled slaves should ignore requests or return a configurable timeout/exception.
- Track per-slave metadata (last activity timestamp, connection status, active transport endpoints).
- Permit cloning of a device to rapidly provision many similar slaves.
- Support organizing slaves into discrete device groups with independent register maps and transport bindings for complex installations while keeping each device lightweight.

### 4.3 Register Configuration
- Handle all four standard register types with independent address spaces and value constraints.
- Allow register definitions to be set via GUI and persisted to scenario/config files in `configs/`.
- Support value initialization, min/max bounds, scaling, and optional units or annotations for GUI display.
- Permit incremental automation such as incrementing a series of holding registers or bulk import/export, without requiring detailed physical process modeling.
- Expose behavior controls per register: `normal` (returns stored value) or `error` (selectable Modbus exception such as Illegal Function, Illegal Data Address, or Illegal Data Value).
- Constrain register payloads to simple scalar values (bools and 16-bit words) for MVP, with hooks to expand to complex data types later.

### 4.4 Runtime Value Updates
- Enable editing register values directly in the GUI with immediate propagation to the simulation layer.
- Reflect writes performed by external Modbus masters within the GUI in real time.
- Offer optional auto-refresh intervals and manual refresh controls to view live register states.
- Allow operators to force value overrides that immediately propagate to connected masters, supporting rapid protocol testing.

### 4.5 Communication Interfaces
- **Serial (RTU)**: Configure port device, baud rate, data bits, parity, stop bits, and response timing; support loopback/virtual serial ports for development.
- **TCP**: Configure listening address/port and optional connection limits; handle multiple simultaneous master connections.
- Provide logging of requests/responses including timestamp, slave ID, function code, and status (success/error).
- Leverage `pymodbus` transport stacks for protocol compliance, while exposing hooks to customize framing or timing behavior when required.

### 4.6 Graphical User Interface
- Present a dashboard listing all configured slaves with status (online/offline, transport bindings, active connections).
- Provide detailed register tables per slave with inline editing, value formatting (hex/dec/bool), and behavior indicators.
- Include controls to toggle slave availability and modify behavior profiles without restarting the simulator.
- Offer a comprehensive log/console pane that records every Modbus transaction, transport event, and UI action with timestamp, severity, and correlation to slave ID; include filtering, search, and export to support protocol debugging.
- Support saving/loading scenarios, importing/exporting configuration snapshots, and resetting to defaults.
- Build the desktop experience with PyQt to deliver a polished, cross-platform UI (Windows, Linux, macOS) with theming and accessibility support.
- Provide a `main.py` entry point that launches the PyQt interface directly so the MVP can be started with `python main.py` or equivalent OS packaging hooks.

### 4.7 Error Handling & Diagnostics
- Allow injecting Modbus exception codes on demand per register or per request (e.g., after N accesses).
- Surface validation warnings when scenario definitions contain overlapping addresses or invalid values.
- Provide health indicators for transport listeners (e.g., port in use, failed bind).

## 5. Non-Functional Requirements
- **Performance**: Respond to typical master polling cycles (<100 ms turnaround for single request under nominal load).
- **Scalability**: Support at least a few hundred concurrent slave IDs and multiple simultaneous masters without degraded accuracy.
- **Extensibility**: Architecture should allow new function codes, device models, and scripted behaviors.
- **Reliability**: Ensure consistent register state persistence during runtime and clean shutdown.
- **Usability**: GUI should remain responsive during active polling; provide keyboard shortcuts for common actions.
- **Observability**: Offer structured logging (JSON option), comprehensive GUI log view with filtering/export, and optional metrics hooks for future monitoring integration.
- **Portability**: Deliver consistent behavior across Windows, Linux, and macOS with minimal external dependencies and support for packaged binaries or standalone executables.
- **Resource Efficiency**: Keep CPU and memory overhead low enough to host a few hundred simultaneous slave instances on a typical developer workstation.

## 6. Configuration & Persistence
- Store reusable fixture data under `assets/` and `configs/` following repository guidelines.
- Define scenario YAML files (`scenario_<bus-mode>_<feature>.yml`) describing slaves, registers, default values, and behaviors.
- Provide export/import commands to translate between live state and scenario files.
- Allow overriding configuration via environment variables or CLI flags (e.g., listen port, serial device path).

## 7. Testing & Quality Assurance
- Implement unit and integration tests mirroring the package structure under `tests/` with ≥90% coverage.
- Use pytest fixtures to simulate serial/TCP interactions; include packet captures under `tests/data/` for regression checks.
- Mark long-running integration simulations with `@pytest.mark.slow`.
- Validate PyQt GUI interactions via component tests or targeted smoke tests (e.g., pytest-qt, QtBot fixtures, or Playwright for end-to-end flows).
- Ensure `make lint`, `make test`, and `make sim` targets enforce style and behavior expectations.

## 8. Open Questions
- Packaging approach for distributing the PyQt application (standalone executables, installers, containers).
