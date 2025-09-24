# Testing Strategy

## 1. Testing Pillars
- Unit tests for protocol parsing, register logic, and utilities
- Integration tests for RTU/TCP transports using loopback fixtures
- GUI smoke tests with pytest-qt or equivalent tooling
- Scenario validation tests ensuring YAML configs parse and load

## 2. Test Environment
- Use pytest with Python 3.11 virtualenv
- Fixtures in `tests/conftest.py` for simulator core, transport stubs
- Sample payloads under `tests/data/` for regression checks
- Mark long-running simulations with `@pytest.mark.slow`

## 3. Coverage Goals & Reporting
- Target ≥90% coverage for `src/mb_sim`
- Command: `pytest --cov=src/mb_sim --cov-report=term-missing`
- Track coverage trends via CI artifacts

## 4. Continuous Integration
- CI pipeline runs lint, unit tests, coverage reporting
- Optional nightly job for slow/integration suites
- Publish artifacts (logs, coverage HTML, captured packets)

## 5. Testing Future Work
- Evaluate property-based tests for register behaviors
- Add performance benchmarks for high-volume polling scenarios
- Explore end-to-end tests with real Modbus master clients

