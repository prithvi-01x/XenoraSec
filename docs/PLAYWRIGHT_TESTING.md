# End-to-End Verification Guide

This guide describes how to run automated verification suites against the XenoraSec tactical interface.

## Playwright UI Verification Suite

The `verify_ui_playwright.py` script executes non-headless or headless browser sessions validating critical UI workflows:

1. **Dashboard Verification**:
   - Ensures KPI cards render (Total Scans, Discovered Hosts, Critical Findings, Open Ports).
   - Confirms Recharts SVG containers mount without hydration errors.
2. **Scan Panel & Form Interactions**:
   - Tests Single vs CIDR Mode toggling.
   - Tests Target validation rules and active error messaging.
   - Tests advanced engine collapsible parameters (timing policy, port range inputs).
3. **Scan Results View**:
   - Inspects Executive Overview card and telemetry KPI strip.
   - Validates tab transitions: Overview -> Ports -> Findings -> Terminal -> Raw JSON.
4. **Modal Testing**:
   - Opens and verifies `ReportExportModal` with format selection and download handlers.
   - Validates `BatchProgressModal` with progress bars and targets table.

### Running Playwright Tests

```bash
# Ensure frontend dev server is active or built
npm --prefix frontend run preview -- --port 5173

# Execute Playwright verification script
python3 verify_ui_playwright.py
```
