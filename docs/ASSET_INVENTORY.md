# Attack Surface Management & Asset Inventory

Specifications for XenoraSec's organization-wide asset inventory and persistent reconnaissance registry.

## 1. Asset Entity Model

When targets are scanned, discovered perimeter assets and service entities are automatically persisted into `scans.db`:
- **Host / IP**: Primary network identifier.
- **Open Ports**: Discovered transport ports, protocols (TCP/UDP), services (HTTP, SSH, MySQL), and version banners.
- **Vulnerabilities**: Aggregated historical findings associated with the host.
- **Risk Posture**: Dynamic asset risk score evaluated across historical scans.

## 2. Operator Workflows

- **Search & Filtering**: Search across hostnames, IPs, service names, and severity levels.
- **Asset Dossier Inspection**: Clicking an asset card or table entry opens the `AssetDetailModal`, displaying port breakdowns and active vulnerability advisories.
- **On-Demand Scans**: Directly trigger an audit against any selected asset from the inventory view.
