# Frontend Component Directory & Interface Reference

A comprehensive inventory of tactical React 19 UI components across XenoraSec.

## Core Layout Components

| Component | File Path | Description |
|-----------|-----------|-------------|
| `Layout` | `src/layouts/Layout.tsx` | Main application shell, tactical collapsible sidebar, active route detection, mobile navigation drawer, and backend worker queue telemetry indicator. |

## Atom & Indicator Components

| Component | File Path | Description |
|-----------|-----------|-------------|
| `StatusBadge` | `src/components/StatusBadge.tsx` | Visual status pill with animated spinners and color-coded execution states. |
| `SeverityBadge` | `src/components/SeverityBadge.tsx` | CVSS-compliant severity tag with color indicators and optional dot styling. |
| `RiskScore` | `src/components/RiskScore.tsx` | CVSS posture gauge offering multiple display densities (`sm`, `md`, `lg`) and dynamic visual status bars. |
| `LoadingSpinner` | `src/components/LoadingSpinner.tsx` | Configurable SVG loading indicator for asynchronous operational states. |

## Interactive Scanners & Consoles

| Component | File Path | Description |
|-----------|-----------|-------------|
| `ScanPanel` | `src/components/ScanPanel.tsx` | Single target and CIDR subnet scan submission form with target sanitization and timing controls. |
| `ScanProfileSelector` | `src/components/ScanProfileSelector.tsx` | Grid-based selection cards for Quick Recon, Full Web Audit, Network Discovery, and Custom scan modes. |
| `LiveTerminal` | `src/components/LiveTerminal.tsx` | Real-time SSE streaming execution console with log stage filtering, auto-scroll, and ANSI color formatting. |

## Overlays & Modals

| Component | File Path | Description |
|-----------|-----------|-------------|
| `ReportExportModal` | `src/components/ReportExportModal.tsx` | Dialog for compiling and downloading PDF, HTML, Markdown, and JSON vulnerability dossiers. |
| `BatchProgressModal` | `src/components/BatchProgressModal.tsx` | Real-time progress monitor for concurrent multi-target sweeps. |
| `AssetDetailModal` | `src/pages/AssetInventoryPage.tsx` | Deep-dive modal inspecting target open ports, service versions, and vulnerability matches. |
