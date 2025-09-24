# Scenario Format

## 1. File Structure
- YAML files stored under `scenarios/` with naming `scenario_<bus-mode>_<feature>.yml`
- Top-level metadata: scenario name, description, version
- List of devices with slave IDs, transports, register maps

## 2. Register Definitions
- Separate sections per register type: coils, discrete inputs, input registers, holding registers
- Fields: address, default value, min/max, units, behavior profile
- Optional automation helpers (increment step, ramp patterns)

## 3. Behaviors & Overrides
- Behavior profiles referencing predefined templates (`normal`, `error`, custom)
- Override blocks for event-driven changes or timed sequences
- Hooks for scripted logic (Python module path) for advanced cases

## 4. Persistence & Import/Export
- CLI commands to load/save current state from/to scenario files
- Support partial updates (apply to subset of devices/registers)
- Validation rules for overlapping addresses and data type mismatches

## 5. Example Skeleton
- Provide minimal scenario showing single TCP slave with holding registers
- Include advanced example with RTU + TCP devices and custom behaviors

