# GUI Overview

## 1. Core Screens
- Dashboard listing all configured slaves and their status indicators
- Register detail view with inline editing and behavior toggles
- Log console with filtering, search, and export actions

## 2. Interaction Patterns
- Real-time value updates with auto-refresh and manual refresh controls
- Modal/dialog flows for creating/editing devices and scenarios
- Keyboard shortcuts for navigation and toggling slave availability

## 3. PyQt Architecture
- Main window composed of dockable panels (dashboard, log, inspector)
- MVC-style separation: view widgets, presenter/controllers, data models
- Signal/slot usage for transport events and UI updates

## 4. Accessibility & Theming
- Provide light/dark themes with configurable font sizing
- Ensure keyboard navigability and screen-reader hints
- Surface error states with color + icon + textual feedback

## 5. Future Enhancements
- Drag-and-drop scenario reordering and grouping
- Custom value renderers (hex/dec/percent) with per-register preferences
- Embedded packet timeline for visualizing request latency

