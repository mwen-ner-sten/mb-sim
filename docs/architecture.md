# Architecture Overview

## 1. System Context
- Define simulator role within automation test environments
- Summarize primary external actors (Modbus masters, operator, filesystem)
- Highlight transports (RTU, TCP) and UI channels (CLI, GUI)

## 2. Runtime Components
- Describe transport servers (`protocols/rtu`, `protocols/tcp`) and message flow
- Detail device model layer (`models/device`, register abstractions)
- Outline scenario loader/persistence services
- Note GUI/CLI front-ends and shared application core

## 3. Data Flow & State Management
- Map request/response pipeline from transport through device register read/write
- Explain state storage (in-memory register tables, scenario snapshots)
- Capture logging, metrics, and event emission strategy

## 4. Extensibility Points
- Document hooks for new function codes and custom behaviors
- Describe plugin model for scripted register logic
- Identify configuration override hierarchy (scenario, CLI flags, env)

## 5. Deployment & Packaging Considerations
- Discuss local development layout vs. packaged distribution
- Note optional services (metrics endpoint, IPC integrations)

