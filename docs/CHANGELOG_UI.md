# XenoraSec UI Overhaul & Tactical Security Interface Changelog

All notable changes introduced as part of the tactical cybersecurity interface overhaul are documented here.

## [2.1.0] - Tactical UI & Experience Overhaul

### Highlights
- Re-architected entire frontend interface with tactical dark theme (`#090d16` canvas, `#0e1526` surface, `#1e2c47` border).
- Introduced JetBrains Mono font loading for all telemetry, CVSS scores, network targets, ports, and logs.
- Added live engine queue and backend health indicators directly to the collapsible tactical sidebar.
- Implemented real-time SSE execution stream console (`LiveTerminal`) with ANSI color decoding and stage filtering.
- Re-engineered `ScanResultsPage` with CVSS posture gauges, port tables, findings accordions, and JSON inspector.
- Updated multi-format vulnerability reporting modal supporting PDF, interactive HTML, Markdown, and JSON.
- Built automated Playwright end-to-end verification suite testing critical navigation and scan workflows.
