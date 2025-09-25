# Simulator Feature Roadmap (Draft)

## 1. Goals
- Deliver a Modbus simulator that wraps pymodbus to provide the project-specific GUI and workflow needs.
- Leverage pymodbus for protocol handling, data modelling, and diagnostics wherever feasible to minimize custom Modbus logic.
- Provide a cohesive runtime that synchronizes CLI, GUI, and scenario-driven configurations.
- Ensure the GUI surfaces live device state, register management, and diagnostics suitable for automation testing.

## 2. Guiding Principles
- Prioritize feature slices that unblock end-to-end validation (runtime ↔ protocol ↔ GUI) before adding advanced UX polish.
- Maintain test parity alongside new modules; every runtime component ships with matching tests under `tests/`.
- Keep the simulator transport-agnostic via shared abstractions so RTU/TCP differ only in framing concerns.
- Favor pymodbus extension points (contexts, data blocks, factories) before introducing custom implementations.
- Document configuration, scenarios, and user-facing behavior as features stabilize.

## 3. Phase Plan

### Phase A — Runtime Foundations (Weeks 1–2)
- **Register Model Expansion**: Introduce coil, discrete input, and input register maps with unified CRUD APIs and validation.
- **Device Lifecycle**: Add enable/disable state, metadata (last activity, description), and cloning support in `SimulationRuntime`.
- **Scenario Loader**: Define YAML schema under `scenarios/`, implement loader/serializer, and wire smoke tests with fixtures in `tests/data/`.
- **Persistence Hooks**: Implement export/import services to snapshot runtime state to configs.
- **Test Coverage**: Expand unit tests for register maps, runtime behaviors, and scenario parsing.

### Phase B — Protocol Servers (Weeks 3–4)
- **Transport Abstractions**: Create protocol layer under `src/mb_sim/protocols/` with shared base classes for RTU and TCP servers.
- **pymodbus Integration**: Wrap `pymodbus` server factories, contexts, and data blocks, ensuring configurable ports, serial settings, and concurrency.
- **Function Codes**: Support function codes 1–6, 15, 16, and diagnostics 8 with request/response translation to the runtime.
- **Exception Handling**: Map runtime errors to Modbus exceptions; add toggles for injecting faults.
- **Logging**: Introduce structured logging (JSON-friendly) capturing transactions per device.
- **Integration Tests**: Add pytest-based protocol smoke tests (marked `@pytest.mark.slow`) using loopback transports.

### Phase C — Core GUI Experience (Weeks 5–6)
- **Runtime Bridge**: Connect GUI to `SimulationRuntime` via a controller/service layer enabling live updates and edits.
- **Device Dashboard**: Display device status, metadata, transport bindings, and activity indicators.
- **Register Tables**: Provide inline editing, type-aware formatting (hex/dec/bool), and behavior flags backed by the runtime service.
- **Refresh Strategies**: Implement manual refresh, configurable auto-refresh, and change notifications from runtime events via Qt signals.
- **Error Surfacing**: Show validation warnings in the UI for invalid scenario states or transport issues.
- **GUI Tests**: Extend `tests/gui/` with QtBot coverage for new widgets and workflows, using mocked runtime services.

### Phase D — Observability & Automation (Weeks 7–8)
- **Event Bus**: Emit runtime events for register writes, protocol errors, and GUI actions; evaluate `blinker` or asyncio signals.
- **Metrics Hooks**: Prototype optional Prometheus endpoint (e.g., `prometheus_client`) with per-function/device counters and structured log export fallback (`structlog`).
- **Scenario Workflows**: Add CLI tooling for scenario CRUD (`mb_sim.cli scenarios ...`) with validation and integration tests.
- **Advanced Behaviors**: Support scripted register logic (incrementers, bounded oscillations) through plugin interface reusing pymodbus scheduling hooks where possible.
- **Stability Pass**: Run extended fuzz/regression testing, profiling, and documentation updates (`docs/gui_overview.md`, `docs/architecture.md`).

## 4. Cross-Cutting Backlog
- Packaging strategy for desktop distribution (PyInstaller, Briefcase).
- Settings system implemented with comprehensive user preferences (refresh intervals, simulation behavior, UI themes).

