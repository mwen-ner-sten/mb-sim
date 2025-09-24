# CLI Reference

## 1. Entry Points
- Primary command: `python -m mb_sim.cli` (alias `mb-sim` TBD)
- Subcommands for managing scenarios, transports, diagnostics

## 2. Global Options
- `--config` to point to custom configuration file
- `--log-level`, `--log-format` for runtime logging control
- `--env-file` for environment variable overrides

## 3. Core Commands
- `serve`: launch simulator with specified scenario(s)
- `scenario list|load|save|validate`
- `device add|remove|clone`
- `register set|get|watch`

## 4. Diagnostics & Utilities
- `transport status` for RTU/TCP listener health
- `metrics export` to expose runtime metrics snapshot
- `capture dump` to export recent Modbus transactions

## 5. Usage Examples
- Start simulator from scenario: `mb-sim serve --scenario scenarios/scenario_rtu_basic.yml`
- Override port: `mb-sim serve --transport tcp --port 1502`
- Apply register override: `mb-sim register set --id 12 --type holding --address 40001 --value 123`

