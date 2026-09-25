# Tactical UI Component Architecture & Design System

This document outlines the architectural specifications and design standards powering the XenoraSec tactical cyber-defense user interface.

## 1. Visual Token Hierarchy

The design system implements a dark-first tactical theme configured in `frontend/index.html` and `frontend/src/index.css`.

- **Background Canvas**: `#090d16` (deep dark tactical slate)
- **Primary Surfaces**: `#0e1526` (card containers, sidebar panes)
- **Elevated Surfaces**: `#162035` (hover states, modal overlays)
- **Borders & Dividers**: `#1e2c47` (subtle structural separation)
- **Brand Accent**: `#2563eb` (primary interactive focus)

## 2. Typography

- **Headings & Body UI**: `Inter`, `-apple-system`, `BlinkMacSystemFont`, `Segoe UI`, `Roboto`, `sans-serif`
- **Telemetry & Technical Indicators**: `JetBrains Mono`, `ui-monospace`, `SFMono-Regular`, `Menlo`, `Monaco`, `Consolas`, `monospace`
- All network targets, port numbers, vulnerability counts, CVSS scores, timestamps, and log streams render strictly with the monospace font family.

## 3. Component Architecture & Atom Elements

- **`StatusBadge`**: Displays scan lifecycle states (`running`, `completed`, `failed`, `timeout`, `partial`) with animated spinners, tactical indicator icons, and monospace status labels.
- **`SeverityBadge`**: CVSS-aligned badge rendering (`critical`, `high`, `medium`, `low`, `info`) with distinct background fills, borders, and dot indicators.
- **`RiskScore`**: Flexible CVSS posture gauge with supporting sizes (`sm`, `md`, `lg`) and dynamic visual status bars.
- **`LiveTerminal`**: EventSource-backed real-time execution console with circular buffer history, stage filtering (`nmap`, `nuclei`, `ai`), auto-scroll toggling, and ANSI stream formatting.

## 4. Modal Workflows & Overlays

### ReportExportModal
Allows operators to export full technical or executive summaries across four discrete formats:
- **PDF**: ReportLab compiled executive briefing with risk summaries and tables.
- **HTML**: Standalone interactive HTML report with self-contained styles.
- **Markdown**: GitHub-flavored security advisory markdown.
- **JSON**: Raw machine-parsable schema export.

### BatchProgressModal
Provides real-time telemetry over multi-target CIDR sweeps and parallel scans, detailing worker progress, completion percentages, and direct access links.
