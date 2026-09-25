# 🛡️ XenoraSec - Advanced Vulnerability Scanner

> **Next-Generation Autonomous Security Assessment & Threat Surface Discovery Engine**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19+-61DAFB.svg?logo=react&logoColor=black)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5+-3178C6.svg?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-3+-06B6D4.svg?logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)
[![Docker Ready](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)](https://www.docker.com/)
[![AI Powered](https://img.shields.io/badge/AI-Groq%20%2B%20Llama%203.3-F05A28.svg)](https://groq.com/)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-181717?logo=github)](https://github.com/prithvi-01x/XenoraSec)

<p align="center">
  <img src="Screenshots/17.png" width="900" alt="XenoraSec Platform Dashboard">
</p>

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Architecture & Workflow](#-architecture)
- [Dual-Engine Scanning](#-dual-engine-scanning)
- [Multi-Target & CIDR Subnet Scanning](#-multi-target--cidr-subnet-scanning)
- [Asset Inventory & Attack Surface Management](#-asset-inventory--attack-surface-management)
- [AI Risk Scoring Model](#-ai-risk-scoring-model)
- [Security & Defensive Safeguards](#-security--defensive-safeguards)
- [Database Architecture](#-database-architecture)
- [REST API Reference](#-rest-api-reference)
- [Environment Configuration](#-environment-configuration)
- [Installation & Quick Start](#-quick-start)
- [Production Deployment (Docker & Nginx)](#-production-deployment)
- [CI/CD Automation Pipeline](#-cicd-automation-pipeline)
- [Frontend Tour & Mobile UX](#-frontend-tour--mobile-ux)
- [Testing & Quality Assurance](#-testing--quality-assurance)
- [Troubleshooting & FAQ](#-troubleshooting--faq)
- [Security Policy & Contributing](#-contributing--license)

---

## 🔍 Overview

**XenoraSec** is an enterprise-grade, open-source vulnerability scanning and attack surface management platform designed for security engineers, penetration testers, and DevSecOps teams. It unites industry-standard recon and vulnerability detection tools into an automated, highly concurrent, asynchronous workflow accompanied by a responsive cyber-defense dashboard.

Traditional security scanners either overwhelm security teams with disconnected raw CLI outputs or trap them behind monolithic, slow, blocking web frameworks. XenoraSec solves this by introducing:

1. **Non-Blocking Dual-Engine Orchestration**: Executes network-layer recon (**Nmap**) and template-driven vulnerability assessments (**Nuclei**) concurrently via non-blocking asyncio subprocesses with real-time stream processing.
2. **Hybrid Risk Intelligence**: Fuses a deterministic **Michaelis-Menten saturation model** (ensuring mathematically bounded, reproducible risk prioritization) with optional real-time **Groq Cloud LLM** contextual analysis.
3. **Zero-Trust Input & Network Defense**: Native safeguards against SSRF, loopback bypasses, DNS rebinding, reverse proxy header spoofing, and rogue scans.
4. **Reliable SQLite WAL / Postgres Concurrency**: Engineered for heavy polling and multi-scan execution without database lockups or zombie process leakage.
5. **Live Terminal Streaming (SSE & WebSocket)**: Interactive console component directly inside the web UI streaming subprocess logs, port discoveries, and template executions in real-time with circular buffer reconnect replay.
6. **Custom Scan Profiles & Nuclei Tag Selector**: Fine-grained scanning with pre-configured profiles (Quick Recon, Full Web Audit, Network Discovery, Custom), port range overrides, Nmap timing policies (T0-T5), and interactive Nuclei tag chips.
7. **Professional Security Report Generation**: One-click export to publication-ready ReportLab PDF, interactive standalone HTML with print styling, GitHub-flavored Markdown, and raw machine-readable JSON in Technical or Executive mode.

### 🏗️ Architecture & Pipeline
```mermaid
flowchart TB
    subgraph Client ["Client Layer (Browser & Mobile)"]
        UI["React 19 + Vite SPA"]
        TQ["TanStack Query (Auto-Polling & Cache)"]
        UI <--> TQ
    end

    subgraph SecurityGate ["Security & Ingress Gate"]
        RL["Sliding-Window Rate Limiter\n(Proxy Header Validation)"]
        VAL["Target Sanitizer & DNS Resolver\n(SSRF / Rebinding Guard)"]
        SEM["Concurrency Slot Governor\n(MAX_CONCURRENT_SCANS)"]
    end

    subgraph Core ["FastAPI Asynchronous Backend"]
        ROUTER["REST API Routes\n(/api/scan, /health)"]
        TASK["Background Task Worker\n(_run_and_store_scan)"]
    end

    subgraph Engines ["Dual Security Execution Engines"]
        NMAP["Nmap Engine\n(-sT -sV -Pn XML Stream)"]
        NUCLEI["Nuclei Engine\n(JSONL Chunk Stream & Buffer Cap)"]
    end

    subgraph Analysis ["AI Risk Analysis Engine"]
        HEUR["Michaelis-Menten\nSaturation Model"]
        GROQ["Groq Cloud LLM\n(Llama 3.3 70B Contextual)"]
        AGG["Composite Risk Aggregator\n(0.0 - 10.0 Scale)"]
    end

    subgraph Database ["Persistence Layer"]
        DB[("SQLite (WAL Mode + 30s Busy Timeout)\n/ PostgreSQL")]
    end

    Client -->|HTTP / JSON| RL
    RL --> VAL
    VAL --> SEM
    SEM --> ROUTER
    ROUTER -->|Spawn Background Task| TASK
    TASK -->|Async Exec| NMAP
    TASK -->|Async Stream| NUCLEI
    NMAP --> Analysis
    NUCLEI --> Analysis
    HEUR --> AGG
    GROQ -.->|Optional| AGG
    AGG -->|Atomic Write| DB
    ROUTER -.->|Poll State| DB
```

#### Scan Request Lifecycle
```text
[User Submits Target]
        │
        ▼
[Proxy Header Check] ────(Spoofed / Rate Exceeded)───► [HTTP 429 Error]
        │
        ▼
[DNS Resolution & SSRF Guard] ──(Private / Loopback)──► [HTTP 400 Rejected]
        │
        ▼
[Queue Slot Acquisition] ───────(Slots Exhausted)────► [HTTP 503 Busy]
        │
        ▼
[Scan ID Generated & Record Created (Status: Running)]
        │
        ├──────────────────────┬──────────────────────┐
        ▼                                             ▼
 [Nmap Process (-sV)]                      [Nuclei Process (-jsonl)]
        │                                             │
   (XML Output)                              (Streaming Buffer)
        │                                             │
        └──────────────────────┬──────────────────────┘
                               │
                               ▼
               [Composite Risk Scoring Engine]
                 ├─ Michaelis-Menten Heuristic
                 └─ Optional Groq LLM Context
                               │
                               ▼
               [Persist to SQLite WAL / PostgreSQL]
                               │
                               ▼
               [Status: Completed / Partial]
```

---

## ⚙️ Dual-Engine Scanning Mechanics

XenoraSec integrates two premier security tools through asynchronous streaming wrappers designed for resilience and memory efficiency:

### 1. Nmap Network & Service Recon Engine
- **Non-Root Execution**: Runs unprivileged `-sT` (TCP Connect) scans, enabling safe execution inside unprivileged containers and cloud environments without raw socket capabilities.
- **Service Version Detection**: Appends `-sV` and `--open` to pinpoint running application versions and discard closed/filtered ports.
- **Dynamic Timing Profiles**: Employs `-T4` for standard remote scans and dynamically accelerates to `-T5` when scanning permitted local endpoints.
- **Fault-Tolerant XML Parser**: Reads structured XML (`-oX -`) directly from stdout. If a scan is forcibly truncated, the custom XML parser reconstructs broken closing tags (`</host>`, `</nmaprun>`) to extract partial port information instead of discarding the entire run.
- **Subprocess Cancellation Safety**: Subprocess handles are strictly tracked. If an HTTP request is aborted or an `asyncio.CancelledError` is raised, `process.kill()` executes instantly, avoiding zombie processes.

### 2. Nuclei Vulnerability & Misconfiguration Engine
- **Streaming JSONL Ingestion**: Executes Nuclei with `-jsonl -silent -no-interactsh`, streaming findings line-by-line rather than loading gigabytes of output into memory.
- **Adaptive Memory Ring-Buffer**: If the incoming stdout stream exceeds `MAX_BUFFER_SIZE` (1MB), the buffer automatically halves oldest data while retaining active line boundaries.
- **Vulnerability Safety Cap**: Configurable limit (`MAX_VULNERABILITIES = 1000`) prevents Denial-of-Service attacks from honeypots or wildcard DNS servers returning infinite findings.
- **Partial Health Classification**: If JSON decode errors exceed 20% of total lines emitted, the scan is flagged as `PARTIAL` rather than `FAILED`, preserving valid CVE and CWE discoveries.

---

## 🌐 Multi-Target & CIDR Subnet Scanning

XenoraSec provides enterprise-grade mass scanning capabilities supporting both multi-target lists and standard IPv4 Classless Inter-Domain Routing (CIDR) subnet notations.

### 1. Subnet Notation & Prefix Governance
Network security teams frequently need to assess complete subnets or IP blocks without manually listing every host:
- **Prefix Boundary Enforcement**: Accepts subnet prefixes from `/24` to `/32` (e.g., `192.168.1.0/28`).
- **Defensive Prefix Guard**: To prevent accidental denial of service or resource exhaustion, subnets broader than `/24` (such as `/16` or `/8`) are rejected with an explicit validation error (`MAX_CIDR_PREFIX=24`, maximum 256 hosts).
- **Usable Host Expansion**: Automatically calculates network boundaries, broadcasts, and usable host addresses:
  - `/30`: 2 usable hosts
  - `/29`: 6 usable hosts
  - `/28`: 14 usable hosts
  - `/26`: 62 usable hosts
  - `/24`: 254 usable hosts
  - `/31` & `/32`: Single/point-to-point host boundaries handled cleanly.

### 2. Multi-Target List Ingestion & Sanitization
Targets can be supplied in flexible formats:
- **Delimiters**: Supports comma-delimited strings (`192.168.1.1, 192.168.1.2`), newline-separated lists, or mixed arrays combining domains, individual IPs, and CIDRs.
- **De-duplication & Trimming**: Automatically removes whitespace, carriage returns, and duplicate entries.
- **Per-Target Zero-Trust Validation**: Each expanded target in the batch independently traverses the SSRF, DNS resolution, and blacklist/whitelist gating rules before queue intake.

### 3. Asynchronous Batch Queue & Concurrency Slots
- **Non-Blocking Ingestion**: Calling `POST /api/scan/batch` dispatches scans across background workers and returns immediately with a unique `batch_id` and scan manifest.
- **Controlled Worker Concurrency**: Scans are scheduled via `BATCH_CONCURRENCY` (default: 3) to prevent saturation of the host network interface and database threadpool.
- **Live Progress Telemetry**: The status endpoint `GET /api/scan/batch/{batch_id}` provides real-time counts (`total`, `completed`, `running`, `failed`, `pending`) and the aggregated arithmetic mean risk score across all batch targets.

### 4. Interactive Frontend Batch Management
- **Target Mode Switcher**: Easily toggle between **Single Target** and **Multi-Target / Subnet** directly from the main `ScanPanel`.
- **Quick-Fill CIDR Chips**: One-click helper chips (`/30`, `/29`, `/28`, `/24`) for rapid testing and automated mask insertion.
- **Live Target Counter**: Real-time reactive preview displays the total number of detected valid targets, invalid targets, and estimated total scans before launching.
- **Batch Telemetry Modal**: A real-time popup monitor tracking per-scan progress, live execution state badges, target links, and final risk score summaries.

---

## 🏢 Asset Inventory & Attack Surface Management

XenoraSec transforms ephemeral scan results into a persistent, living Attack Surface Management (ASM) repository. Rather than losing port discoveries and CVE findings in isolated scan logs, assets are centrally tracked, classified, and monitored over time.

### 1. Automated Finding Ingestion & Delta Sync
Whenever any scan completes (whether launched individually or via a multi-target CIDR batch):
- **Autonomous Indexing**: The backend service parses Nmap port tables and Nuclei vulnerability lists, automatically creating or updating asset records in the `assets` table.
- **Idempotent Upsert Mechanics**: Repeated assessments of the same host do not clutter the database with duplicate assets. Instead, `upsert_asset_from_scan` performs an intelligent delta update:
  - Updates host metadata (`last_scanned_at`, `risk_score`, severity distribution counters).
  - Synchronizes open ports, updating service/version information and `last_seen` timestamps.
  - Links discovered vulnerabilities, preserving `first_seen` audit history and marking re-confirmed CVEs.

### 2. Relational Entity Architecture
```text
┌────────────────────────────────────────────────────────┐
│                        Asset                           │
│  - id: Integer (PK)                                    │
│  - ip_address: String (Indexed)                        │
│  - hostname: String (Nullable, Indexed)                │
│  - asset_type: 'ip' | 'domain' | 'url' | 'cidr_host'   │
│  - status: 'active' | 'scanned' | 'inactive'           │
│  - criticality: 'low' | 'medium' | 'high' | 'critical' │
│  - risk_score: Float (0.0 - 10.0)                      │
│  - open_ports_count, vulns_count, severity counters    │
│  - tags: JSON List / notes: Text                       │
└───────────────────────────┬────────────────────────────┘
                            │ 1:N Relationships (Cascade Delete)
             ┌──────────────┴──────────────┐
             ▼                             ▼
┌─────────────────────────┐   ┌──────────────────────────────┐
│       AssetPort         │   │      AssetVulnerability      │
│ - port, protocol        │   │ - template_id, name          │
│ - service, product      │   │ - severity, cvss, cve        │
│ - version, last_seen    │   │ - matched_at, status         │
└─────────────────────────┘   └──────────────────────────────┘
```

### 3. Asset Governance & Lifecycle Operations
- **Business Criticality Classification**: Assign custom criticality levels (`critical`, `high`, `medium`, `low`) and organizational tags to prioritize remediation efforts on core infrastructure.
- **Targeted Re-Scanning**: Re-trigger scans against any asset directly with one click via `POST /api/assets/{id}/scan`, automatically inheriting preferred scan profiles and options.
- **Perimeter Metric Aggregation**: Rapidly query overall posture statistics with `GET /api/assets/stats`, returning real-time counts across asset types, risk bands, open ports, and active vulnerabilities.

### 4. Enterprise Asset UI & Inspection Drawer
- **Asset Command Center**: Dedicated `/assets` view featuring responsive filter controls, keyword search, criticality dropdowns, and tabular host matrices.
- **Deep Service & CVE Inspection Drawer**: Click any asset row to open an interactive drawer displaying all exposed service versions (SSH, HTTP, Nginx, Envoy) and Nuclei CVE findings with direct external references.

---

## 🧠 AI Risk Scoring & Saturation Model

Security teams need risk scores that are both **contextually intelligent** and **mathematically predictable**. XenoraSec implements a hybrid evaluation system:

### 1. The Michaelis-Menten Mathematical Saturation Model
Rather than using arbitrary linear formulas that easily overflow or artificial step-functions, XenoraSec uses a hyperbolic saturation function adapted from enzyme kinetics (Michaelis-Menten / Hill equation):

$$\text{Risk Score} = V_{\max} \cdot \left( \frac{S}{S + K_m} \right)$$

Where:
- **$V_{\max} = 10.0$**: The theoretical maximum risk score ceiling.
- **$K_m = 15.0$**: The half-saturation constant (the raw score required to yield exactly a 5.0 risk score).
- **$S$**: The accumulated raw vulnerability and network exposure score.

#### Raw Score ($S$) Calculation:
$$S = \sum_{v \in V} \text{Weight}(\text{severity}_v) + \sum_{v \in V} \left( \text{CVSS}_v \times 0.15 \right) + \min\left( \text{open\_ports} \times 0.05, 1.0 \right)$$

| Finding Type | Base Weight | Multiplier / Cap | Description |
| :--- | :--- | :--- | :--- |
| **Critical** | `5.0` | N/A | Remotely exploitable RCE, auth bypass, SQLi |
| **High** | `3.0` | N/A | Privileged read, SSRF, major misconfigurations |
| **Medium** | `2.0` | N/A | Reflected XSS, CSRF, insecure transport |
| **Low** | `1.0` | N/A | Information disclosures, weak cipher suites |
| **Info / Unknown**| `0.5` | N/A | Technology banners, DNS records, headers |
| **CVSS Metric** | Variable | $\times 0.15$ | Direct contribution from official CVSS score |
| **Open Ports** | Variable | $\min(P \times 0.05, 1.0)$ | Attack surface perimeter exposure factor |

#### Mathematical Guarantees:
1. **Strict Monotonicity**: Adding any new vulnerability or open port always increases or preserves the score ($\frac{\partial \text{Score}}{\partial S} > 0$).
2. **Strict Boundedness**: For any finite or infinite set of findings, $0.0 \le \text{Score} \le 10.0$.
3. **Diminishing Marginal Risk**: The first critical vulnerability introduces an urgent jump (~2.5 to 3.5 points), while additional findings reflect real-world attack path convergence rather than artificial numeric inflation.

### 2. Optional Groq Cloud LLM Integration
When `GROQ_API_KEY` is defined in `.env`, XenoraSec augments the heuristic model with a zero-latency inference call to **Llama 3.3 70B** on Groq Cloud:
- **Holistic Threat Analysis**: Evaluates how open port topologies chain together with discovered template vulnerabilities.
- **Zero-Friction Fallback**: If the Groq API exceeds the 10-second timeout, runs out of quota, or encounters a network partition, the platform silently and immediately falls back to the deterministic Michaelis-Menten model without failing the scan.

---

## 🔒 Security Safeguards & Defensive Engineering

A security scanner is a high-value target; XenoraSec is engineered with zero-trust defensive safeguards:

### 1. SSRF & Loopback Protection with DNS Resolution
Attackers frequently attempt Server-Side Request Forgery (SSRF) or DNS rebinding by pointing custom domains to internal infrastructure (`127.0.0.1`, `169.254.169.254`, `10.0.0.1`).
- **Strict Hostname Checking**: Explicitly blocks `localhost`, `*.localhost`, and `127.0.0.0/8` ranges unless `ALLOW_LOCALHOST_SCANNING=True`.
- **Pre-Scan DNS Lookup**: Before launching any scanner, `validate_target` executes `socket.getaddrinfo` to resolve all candidate IPv4 and IPv6 addresses. If any resolved IP belongs to private (RFC 1918), link-local, multicast, or loopback space, the scan request is rejected immediately with HTTP 400.
- **Enforced Security Hierarchy**: Client-submitted scan options cannot override server-wide security policies (`ALLOW_PRIVATE_IP_SCANNING`, `ALLOW_LOCALHOST_SCANNING`).

### 2. Reverse Proxy & Rate Limiter Anti-Spoofing
Naively trusting `X-Forwarded-For` allows attackers to bypass rate limits by rotating fake headers. XenoraSec enforces:
- **Proxy Trust Gating**: Proxy headers are ignored unless `TRUST_PROXY_HEADERS=True` is explicitly configured.
- **Trusted Peer Verification**: When enabled, the direct socket connection (`request.client.host`) must match an entry in `TRUSTED_PROXIES`.
- **Rightmost Hop Parsing**: Extracts the rightmost IP address appended by the trusted reverse proxy, preventing client-injected prefix tampering.
- **IP Address Syntax Validation**: Parses candidates through `ipaddress.ip_address` to prevent header injection or non-standard address formats.

### 3. Subprocess Cancellation & Zombie Cleanup
- **Cancellation Interception**: `NmapScanner` and `NucleiScanner` explicitly catch `asyncio.CancelledError` (which inherits from `BaseException`) and execute `process.kill()` inside `finally` blocks.
- **Cold-Start Zombie Recovery**: Upon application startup, XenoraSec queries the database and transitions any dangling `RUNNING` scans to `FAILED` with an informative restart reason.

---

## 🗄️ Database Architecture & Concurrency

XenoraSec supports both development SQLite and enterprise-scale PostgreSQL via SQLAlchemy 2.0 async sessions:

```mermaid
erDiagram
    SCAN_RESULT {
        string scan_id PK "UUIDv4 identifier"
        string target "Validated hostname or IP"
        string status "running | completed | failed | timeout | partial"
        float risk_score "0.0 - 10.0 score"
        json result "Raw Nmap and Nuclei payloads"
        string error_message "Failure or partial cause"
        float duration "Total execution seconds"
        string parent_scan_id FK "Original scan if retried"
        datetime created_at "ISO UTC timestamp"
        datetime updated_at "ISO UTC timestamp"
    }
```

### 1. SQLite High-Concurrency Tuning
By default, SQLite locks the entire database file during writes, which causes `sqlite3.OperationalError: database is locked` during concurrent scanning and frequent frontend UI polling. XenoraSec eliminates this via:
- **Write-Ahead Logging (WAL)**: `PRAGMA journal_mode=WAL` allows multiple concurrent readers to query scan progress while a background worker writes scan updates.
- **Synchronous Normal**: `PRAGMA synchronous=NORMAL` reduces disk fsync overhead while maintaining ACID consistency across crashes.
- **30-Second Busy Handler**: `PRAGMA busy_timeout=30000` instructs SQLite to wait up to 30 seconds for lock release rather than immediately throwing an exception.
- **Connection Acquisition Timeout**: Engine configured with `connect_args={"timeout": 30.0, "check_same_thread": False}` and `NullPool` for clean task-scoped connections.

### 2. Enterprise PostgreSQL Migration
For multi-node deployments or high-volume enterprise scanning, switch to PostgreSQL with `asyncpg` by updating `.env`:

```env
DATABASE_URL="postgresql+asyncpg://xenora_user:secure_password@postgres.internal:5432/xenorasec"
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
```
When a PostgreSQL connection string is detected, XenoraSec automatically activates SQLAlchemy `QueuePool` with active pre-ping health checks.

---

## 📡 REST API Reference

XenoraSec provides a clean, fully documented OpenAPI (Swagger) interface accessible at `/docs`.

### Core Endpoints

| Method | Endpoint | Description | Status Codes |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/scan/` | Initiate an individual security scan | `200`, `400`, `429`, `503` |
| `POST` | `/api/scan/batch` | Queue batch scan across multi-targets or CIDR subnets | `200`, `400`, `429`, `503` |
| `GET` | `/api/scan/batch/{batch_id}` | Poll batch execution telemetry & aggregated score | `200`, `404` |
| `GET` | `/api/scan/results/{scan_id}` | Fetch full scan results & findings | `200`, `400`, `404` |
| `GET` | `/api/scan/history` | Paginated historical scan records (supports batch filter) | `200`, `400` |
| `POST` | `/api/scan/{scan_id}/retry` | Retry a failed, timeout, or partial scan | `200`, `400`, `404`, `503` |
| `POST` | `/api/scan/{scan_id}/cancel` | Abort a running background scan | `200`, `400`, `404` |
| `DELETE` | `/api/scan/{scan_id}` | Permanently delete a scan result | `200`, `400`, `404` |
| `GET` | `/api/scan/queue` | Query active scan concurrency slots | `200` |
| `POST` | `/api/scan/cleanup` | Purge scans older than N days (`secret` req) | `200`, `403`, `503` |
| `GET` | `/api/assets` | Paginated Asset Inventory with keyword & criticality filters | `200` |
| `GET` | `/api/assets/stats` | Perimeter ASM KPI metrics & severity distribution | `200` |
| `GET` | `/api/assets/{id}` | Inspect asset with open service ports & active CVEs | `200`, `404` |
| `PATCH` | `/api/assets/{id}` | Update asset criticality, operational status, and notes | `200`, `400`, `404` |
| `DELETE` | `/api/assets/{id}` | Delete asset and cascade remove linked ports/vulns | `200`, `404` |
| `POST` | `/api/assets/{id}/scan` | Trigger automated re-scan of an existing asset | `200`, `404`, `503` |
| `GET` | `/health` | Liveness & database connection health | `200`, `503` |

### API Usage Examples

#### 1. Launch a New Scan
```bash
curl -X POST "http://localhost:8000/api/scan/" \
     -H "Content-Type: application/json" \
     -d '{"target": "example.com"}'
```
**Response (`200 OK`):**
```json
{
  "scan_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "target": "example.com",
  "status": "running",
  "message": "Scan started successfully"
}
```

#### 2. Query Scan Results & Risk Intelligence
```bash
curl -s "http://localhost:8000/api/scan/results/9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d"
```
**Response Sample:**
```json
{
  "scan_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "target": "example.com",
  "status": "completed",
  "risk_score": 6.84,
  "duration": 42.18,
  "summary": {
    "total_vulnerabilities": 3,
    "open_ports": 2,
    "severity_distribution": {
      "critical": 0,
      "high": 1,
      "medium": 2,
      "low": 0,
      "info": 0
    },
    "risk_level": "high"
  }
}
```

#### 3. Retry a Partial or Failed Scan
```bash
curl -X POST "http://localhost:8000/api/scan/9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d/retry"
```

#### 4. Live Terminal Streaming (SSE & WebSocket)
Stream backend scanner stdout, port discoveries, and vulnerability matches in real-time:
```bash
# Server-Sent Events (SSE)
curl -N "http://localhost:8000/api/scan/{scan_id}/stream"

# WebSocket live console stream
wscat -c "ws://localhost:8000/api/scan/{scan_id}/ws"
```

#### 5. Generate & Download Professional Reports
Export publication-ready security assessments in PDF, HTML, Markdown, or JSON:
```bash
# Publication PDF report (ReportLab)
curl -O -J "http://localhost:8000/api/scan/{scan_id}/report?format=pdf&report_type=technical"

# Interactive offline HTML report with print-to-PDF styles
curl -O -J "http://localhost:8000/api/scan/{scan_id}/report?format=html&report_type=technical"

# GitHub-flavored Markdown report
curl -O -J "http://localhost:8000/api/scan/{scan_id}/report?format=markdown&report_type=executive"

# Machine-readable JSON export
curl -O -J "http://localhost:8000/api/scan/{scan_id}/report?format=json&report_type=technical"
```

#### 6. Scan Profiles & Nuclei Template Catalog
Query built-in scan presets (Quick Recon, Full Web Audit, Network Discovery, Custom) and template tags:
```bash
# List available scan profiles
curl "http://localhost:8000/api/scan/profiles"

# List available Nuclei template categories and tags
curl "http://localhost:8000/api/scan/templates"
```

#### 7. Multi-Target & CIDR Batch Operations
Launch mass security audits across subnets or host lists, and monitor aggregate telemetry:
```bash
# Launch a batch scan for a CIDR block and extra hosts
curl -X POST "http://localhost:8000/api/scan/batch" \
     -H "Content-Type: application/json" \
     -d '{
       "raw_targets": "192.168.1.0/29\napi.example.com",
       "scan_profile": "quick",
       "batch_name": "Perimeter Audit Q3"
     }'

# Query batch progress and overall composite risk
curl -s "http://localhost:8000/api/scan/batch/{batch_id}"
```

#### 8. Asset Inventory Management API
Inspect, filter, update criticality, and trigger automated re-scans across persistent assets:
```bash
# Query paginated inventory with filters
curl -s "http://localhost:8000/api/assets?criticality=high&status=active&limit=10"

# Fetch aggregated attack surface statistics
curl -s "http://localhost:8000/api/assets/stats"

# Inspect detailed asset ports and active CVE vulnerabilities
curl -s "http://localhost:8000/api/assets/{asset_id}"

# Update asset criticality rating and operational notes
curl -X PATCH "http://localhost:8000/api/assets/{asset_id}" \
     -H "Content-Type: application/json" \
     -d '{"criticality": "critical", "notes": "Primary authentication gateway"}'

# Trigger an immediate re-scan of an asset
curl -X POST "http://localhost:8000/api/assets/{asset_id}/scan"
```

---

## ⚙️ Environment Configuration

All settings in XenoraSec can be configured via environment variables or specified inside a `.env` file in the project root:

| Variable | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| **`APP_NAME`** | `string` | `"XenoraSec"` | Branding identifier |
| **`DEBUG`** | `boolean` | `false` | Verbose FastAPI debug logs |
| **`DATABASE_URL`** | `string` | `sqlite+aiosqlite:///./scans.db` | SQLite or PostgreSQL URI |
| **`MAX_CONCURRENT_SCANS`** | `integer` | `3` | Maximum simultaneous active scans |
| **`GLOBAL_SCAN_TIMEOUT`** | `integer` | `600` | Hard timeout (seconds) per scan |
| **`NMAP_TIMEOUT`** | `integer` | `180` | Maximum seconds for Nmap phase |
| **`NMAP_TIMING`** | `string` | `"T4"` | Nmap timing template (`T1`-`T5`) |
| **`NUCLEI_TIMEOUT`** | `integer` | `300` | Maximum seconds for Nuclei phase |
| **`NUCLEI_RATE_LIMIT`** | `integer` | `50` | Nuclei HTTP requests per second |
| **`MAX_VULNERABILITIES`**| `integer` | `1000` | Safety limit to prevent memory bloat |
| **`ALLOW_LOCALHOST_SCANNING`**| `boolean` | `false` | Enable/disable scanning 127.0.0.1 |
| **`ALLOW_PRIVATE_IP_SCANNING`**| `boolean` | `false` | Enable/disable RFC 1918 subnets |
| **`RATE_LIMIT_ENABLED`** | `boolean` | `true` | Enable client IP rate limiting |
| **`RATE_LIMIT_PER_MINUTE`**| `integer` | `10` | Requests allowed per minute per IP |
| **`RATE_LIMIT_PER_HOUR`**| `integer` | `100` | Requests allowed per hour per IP |
| **`TRUST_PROXY_HEADERS`**| `boolean` | `false` | Enable when behind reverse proxies |
| **`ALLOWED_ORIGINS`** | `string` | `http://localhost:5173,...` | Allowed CORS origins (comma separated)|
| **`MAX_CIDR_PREFIX`** | `integer` | `24` | Maximum allowable CIDR subnet mask (prevents wide subnet scans) |
| **`MAX_BATCH_TARGETS`** | `integer` | `256` | Maximum total target count accepted per batch submission |
| **`BATCH_CONCURRENCY`** | `integer` | `3` | Worker concurrency slots allocated for batch scans |
| **`GROQ_API_KEY`** | `string` | `null` | Groq Cloud API key for Llama 3.3 LLM |
| **`GROQ_MODEL`** | `string` | `"llama-3.3-70b-versatile"` | Target Groq model identifier |
| **`CLEANUP_SECRET`** | `string` | `null` | Required secret for `/api/scan/cleanup`|

---

## 📸 Screenshots

### Dashboard - Scan Progress
<p align="center">
  <img src="Screenshots/15.png" width="700">
</p>

### Scan History
<p align="center">
  <img src="Screenshots/11.png" width="700">
</p>

---

## ✨ Key Features

- **🛡️ Asynchronous Dual-Engine Scanning**: Concurrent network recon (Nmap) and template vulnerability assessment (Nuclei v3.3.8) with streaming stdout parsing.
- **🌐 Multi-Target & CIDR Subnet Auditing**: First-class support for IPv4 CIDR blocks (`/24` to `/32`) and multi-host lists with asynchronous worker queuing.
- **🏢 Attack Surface & Asset Inventory**: Autonomous indexing of discovered hosts, exposed services, and CVEs into a persistent relational asset catalog.
- **🧠 Hybrid AI Risk Scoring**: Mathematical Michaelis-Menten bounded scoring (0.0 - 10.0) with zero-latency Groq Cloud LLM contextual analysis.
- **🐳 Turnkey Production Containerization**: Production Docker Compose orchestrating FastAPI backend, SQLite WAL persistence, and Nginx reverse proxy.
- **🔄 GitHub Actions CI/CD Matrix**: Multi-version Python (3.11, 3.12) automated testing, TypeScript strict type checks, and ESLint quality gates.
- **🖥️ Responsive Cyber-Defense Dashboard**: Real-time progress streaming, interactive Recharts telemetry, dark mode, and mobile drawer navigation.
- **🔒 Zero-Trust Perimeter Defense**: Native SSRF prevention, DNS rebinding mitigation, sliding-window rate limiting, and trusted proxy verification.

---

## 🚀 Installation & Local Development Setup

### System Prerequisites
Ensure the underlying security scanning binaries are installed on your host system:

#### 1. Install Nmap & Nuclei
- **Ubuntu / Debian**:
  ```bash
  sudo apt-get update && sudo apt-get install -y nmap wget unzip
  # Download precompiled Nuclei binary
  wget https://github.com/projectdiscovery/nuclei/releases/download/v3.3.8/nuclei_3.3.8_linux_amd64.zip
  unzip nuclei_3.3.8_linux_amd64.zip
  sudo mv nuclei /usr/local/bin/
  rm nuclei_3.3.8_linux_amd64.zip
  nuclei -update-templates
  ```

- **macOS (Homebrew)**:
  ```bash
  brew install nmap nuclei
  nuclei -update-templates
  ```

- **Arch Linux**:
  ```bash
  sudo pacman -S nmap nuclei
  nuclei -update-templates
  ```

---

### Step-by-Step Setup

#### 1. Clone the Repository
```bash
git clone https://github.com/prithvi-01x/XenoraSec.git
cd XenoraSec
```

#### 2. Configure Environment Variables
```bash
cp .env.example .env
# Edit .env with your favorite editor to configure database and optional Groq API key
nano .env
```

#### 3. Backend Setup
```bash
# Using standard Python venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Start the FastAPI server on port 8000
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 4. Frontend Setup
In a new terminal:
```bash
cd frontend
npm install
npm run dev
```

Visit **[http://localhost:5173](http://localhost:5173)** in your browser. The frontend will automatically connect to the backend running at `http://localhost:8000`.

---

## 🚢 Production Deployment

### 1. Deploying to Render via Blueprint (`render.yaml`)

XenoraSec includes a turnkey `render.yaml` blueprint:

1. Fork this repository to your GitHub account.
2. Log in to [Render](https://render.com/) and navigate to **Blueprints**.
3. Connect your repository: Render will detect `render.yaml` and provision:
   - **`xenorasec-backend`**: Docker Web Service running the optimized `Dockerfile.render` with precompiled Nuclei and Nmap.
   - **`xenorasec-frontend`**: Static Site serving compiled React SPA with client-side SPA routing rewrites.
4. Add any custom environment variables (such as `GROQ_API_KEY`) via the Render Dashboard.

### 2. Turnkey Multi-Container Production (Docker Compose & Nginx)

For on-premise, cloud VPS (AWS, GCP, DigitalOcean, Hetzner), or air-gapped deployments, XenoraSec provides a production-grade multi-container orchestration via `docker-compose.yml`:

```
┌─────────────────────────────────────────────────────────────────┐
│                      Client Browser / Ingress                   │
└────────────────────────────────┬────────────────────────────────┘
                                 │ HTTP :80
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Frontend Nginx Proxy                        │
│  - Serves compiled React 19 SPA static assets                   │
│  - Gzip compression for JS/CSS bundles                          │
│  - SPA fallback: try_files $uri $uri/ /index.html               │
│  - Reverse Proxy: /api/* -> backend:8000                        │
│  - WebSocket Upgrade: /api/scan/*/ws -> backend:8000            │
│  - Health Probe: /health -> backend:8000/health                 │
└────────────────────────────────┬────────────────────────────────┘
                                 │ internal network
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Backend FastAPI Service                     │
│  - Python 3.12 runtime with Nmap & Nuclei v3.3.8 pre-installed  │
│  - Non-root unprivileged execution                              │
│  - SQLite WAL persistence on mounted volume                     │
│  - Autonomous background scan workers & concurrency slots       │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│               Persistent Storage (scans_data Volume)            │
│  - Mount: /data/scans.db (WAL + SHM index files)                │
└─────────────────────────────────────────────────────────────────┘
```

#### Quick Start with Docker Compose
```bash
# 1. Copy sample environment
cp .env.example .env

# 2. Build and launch services in background
docker compose up -d --build

# 3. Check container health status
docker compose ps

# 4. View real-time container logs
docker compose logs -f
```
The application will be accessible at **`http://localhost`** (or your server's IP address on port 80).

#### Architecture Highlights:
- **Zero-Configuration Reverse Proxy**: Nginx automatically handles API routing, eliminating CORS issues in production environments.
- **WebSocket Streaming Support**: Full connection upgrade headers (`Upgrade $http_upgrade`, `Connection "Upgrade"`) allow seamless terminal streaming.
- **Persistent SQLite WAL Volume**: Database data is stored in the Docker volume `scans_data` mounted at `/data/scans.db`, ensuring scan records survive container restarts and updates without corruption.
- **Production Health Checks**: Both containers feature automated Docker health checks (`/health` endpoint probe) to ensure zero-downtime restarts.
- **Development Overrides**: Copy `docker-compose.override.yml.example` to `docker-compose.override.yml` to mount local directories for live reloading during development:
  ```bash
  cp docker-compose.override.yml.example docker-compose.override.yml
  docker compose up
  ```

---

## 🔄 CI/CD Automation Pipeline

XenoraSec incorporates an automated continuous integration and testing pipeline orchestrated via **GitHub Actions** (`.github/workflows/ci.yml`). Every commit and pull request targeting the `main` branch undergoes automated matrix validation:

```text
┌─────────────────────────────────────────────────────────────┐
│                 GitHub Actions CI Workflow                  │
└──────────────┬───────────────────────────────┬──────────────┘
               │                               │
        ┌──────▼──────┐                 ┌──────▼──────┐
        │ Backend CI  │                 │ Frontend CI │
        └──────┬──────┘                 └──────┬──────┘
               │                               │
    ├─ Python 3.11 Matrix           ├─ Node.js 20 Setup
    ├─ Python 3.12 Matrix           ├─ Dependency Cache
    ├─ pip Dependencies             ├─ ESLint Verification (npm run lint)
    └─ Pytest Suite (pytest -v)     ├─ TypeScript Strict Check (tsc -b)
                                    └─ Production Bundle (npm run build)
               │                               │
               └───────────────┬───────────────┘
                               │
                        ┌──────▼──────┐
                        │ Compose CI  │
                        └──────┬──────┘
                               │
                        └─ Docker Compose Validation (docker compose config)
```

### 1. Multi-Version Python Matrix Testing
- **Runtime Coverage**: Executes the full asynchronous backend test suite on both **Python 3.11** and **Python 3.12**.
- **Pytest Suite Execution**: Runs 97+ unit, integration, and security regression tests covering SSRF prevention, Michaelis-Menten risk calculation, SQLite WAL concurrency, CIDR subnet expansion, batch queues, and Asset Inventory CRUD operations.

### 2. Frontend Strict Verification
- **Static Linting**: Runs ESLint (`npm run lint`) to enforce coding standards, hook dependencies, and prevent syntax anti-patterns.
- **TypeScript Type Verification**: Executes `tsc -b` in strict mode to guarantee zero type errors or broken interfaces across API clients, hooks, and views.
- **Production Asset Compilation**: Bundles the application using Vite (`npm run build`) to ensure client assets compile with zero minification errors or broken module imports.

### 3. Container Configuration Validation
- Validates `docker-compose.yml` syntax and environment variable interpolation using `docker compose config`, ensuring deployment configurations stay robust.

---

## 💻 Frontend Tour & Mobile Responsiveness

The XenoraSec frontend is built with React 19, TypeScript, and Tailwind CSS to deliver an ultra-fast, responsive security operations dashboard:

### 1. Tactical Dark Cyber-Defense Interface
- **Dark-First Theme**: Purpose-built palette featuring `#090d16` canvas, `#0e1526` surfaces, and `#1e2c47` borders with custom webkit tactical scrollbars.
- **Monospace Telemetry**: Employs `JetBrains Mono` for precise readability of targets, port ranges, CVE tags, CVSS ratings, and timestamps.
- **Collapsible Navigation & Queue Status**: Live worker queue gauges and backend connection heartbeat embedded directly in the persistent sidebar.
- **Architecture Documentation**: For design tokens and components, see [UI Architecture](docs/UI_ARCHITECTURE.md), [Component Reference](docs/UI_COMPONENTS.md), and [Design Tokens](docs/DESIGN_TOKENS.md).

### 2. Mobile-First Adaptive Interface
- **Responsive Drawer Navigation**: On smartphones and tablets, the 240px tactical sidebar cleanly collapses into a sliding drawer accessible via the top navigation hamburger button, with an animated backdrop overlay.
- **Dynamic Content Flow**: Prevents horizontal overflow on smaller screens while keeping complex data tables (ports, CVSS metrics) fully scrollable.

### 3. Intelligent Target Specification
- **Format Recognition Badges**: Dynamically identifies whether the input is an **IPv4 Address**, **Domain Host**, **Web URL**, or **Localhost** as you type.
- **Proactive Input Linting**: Validates IP octets (0-255) and domain boundaries in real time, showing immediate contextual feedback prior to network dispatch.
- **One-Click Test Presets**: Quick-fill buttons for fast testing and demonstrations (`scanme.nmap.org`, `https://example.com`).

### 4. Interactive Scan Findings & Intelligence
- **Real-Time Polling & SSE Stream**: TanStack Query automatically polls background scan state, with live execution logs streamed via `LiveTerminal` SSE channel.
- **Multi-Dimensional Severity Filtering**: Filter findings instantly by severity level (Critical, High, Medium, Low, Info) or full-text query.
- **Deep Vulnerability Inspection**: Click any finding to inspect its matching template ID, CVSS score, CWE tags, matched path, and official external vulnerability references.
- **One-Click Report Export**: Comprehensive export modal for compiling and downloading PDF, HTML, Markdown, and JSON vulnerability dossiers.

---

## 🧪 Testing & Quality Assurance

XenoraSec maintains a rigorous automated test suite covering security controls, mathematical modeling, and concurrent operations:

### Backend Test Suite (Pytest)

The test suite includes 25+ automated unit and integration tests:

```bash
# Run all tests with verbose output
pytest -v

# Run a specific test module
pytest tests/test_security.py
pytest tests/test_ai_service.py
```

#### Test Coverage Matrix

| Test Module | Focus Area | Key Invariants Verified |
| :--- | :--- | :--- |
| **`test_security.py`** | SSRF & Input Gate | Validates loopback blocking, DNS resolution, private IP rejection, and domain regex |
| **`test_rate_limit.py`** | Anti-Spoofing | Verifies proxy header gating, trusted peer checks, and sliding-window limits |
| **`test_cancellation.py`** | Subprocess Safety | Ensures `process.kill()` executes on `asyncio.CancelledError` |
| **`test_ai_service.py`** | Risk Scoring | Proves Michaelis-Menten half-saturation point ($S=15 \implies 5.0$) & Groq fallback |
| **`test_database.py`** | DB Concurrency | Checks WAL mode, 30s busy timeout, and concurrent multi-session execution |
| **`test_api.py`** | REST API Endpoints | End-to-end route tests for `/health`, `/queue`, `/history`, and partial retries |

### Frontend Build & Type Verification

```bash
cd frontend
# TypeScript compilation & production build
npm run build

# Run ESLint quality checks
npm run lint
```

---

## 📚 Documentation & API

- **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Architecture**: **[Architecture.md](Architecture.md)** (Design & Deployment)
- **Testing**: **[TESTING_GUIDE.md](TESTING_GUIDE.md)**
- **Changelog**: **[changelog.md](changelog.md)**

---

## ❓ Troubleshooting & FAQ

### 1. `Nmap not installed` or `Nuclei not installed`
**Issue**: Backend returns error stating scanner is missing from system.  
**Resolution**: Ensure both binaries are present in your system PATH:
```bash
which nmap && which nuclei
nmap --version
nuclei -version
```
If missing, follow the [Installation](#-installation--local-development-setup) instructions for your operating system.

---

### 2. `Target resolves to private/internal IP (X.X.X.X), which is not allowed`
**Issue**: Scans against internal hosts or test domains fail immediately with HTTP 400.  
**Resolution**: XenoraSec enables SSRF defense by default. If you are authorized to audit internal private networks (e.g. staging or home lab):
```env
# Inside your .env file:
ALLOW_PRIVATE_IP_SCANNING=True
ALLOW_LOCALHOST_SCANNING=True
```
Restart the backend service to apply.

---

### 3. `sqlite3.OperationalError: database is locked`
**Issue**: Occurs if another process locked `scans.db` without WAL mode enabled.  
**Resolution**: XenoraSec automatically applies `PRAGMA journal_mode=WAL` and a 30-second busy timeout. Ensure the process directory has write permissions so SQLite can create the `-wal` and `-shm` auxiliary files:
```bash
chmod 664 scans.db*
```

---

### 4. `Rate limit exceeded: 10 requests per minute` (HTTP 429)
**Issue**: Frequent API calls or automated frontend testing trigger rate limiting.  
**Resolution**: Increase the per-minute threshold or configure reverse proxy header trust in `.env`:
```env
RATE_LIMIT_PER_MINUTE=60
TRUST_PROXY_HEADERS=True
```

---

### 5. Updating Nuclei Templates
**Issue**: Scans miss newly disclosed CVEs.  
**Resolution**: Regularly sync the community templates repository:
```bash
nuclei -update-templates
```

---

## 📁 Project Structure

```
xenorasec/
├── app/                  # FastAPI Backend
├── frontend/             # React Frontend
├── Screenshots/          # Images
├── docs/                 # Documentation
├── .env.example          # Config template
├── requirements.txt      # Python deps
└── README.md             # This file
```

---

## 🗺️ Product Roadmap

- [x] **Asynchronous Dual-Engine Orchestration** (Nmap + Nuclei v3.3.8)
- [x] **Deterministic Michaelis-Menten Risk Scoring Model**
- [x] **Optional Groq Cloud LLM Integration** (Llama 3.3 70B)
- [x] **Zero-Trust SSRF & DNS Rebinding Protection**
- [x] **SQLite WAL Mode & High-Concurrency Hardening**
- [x] **Mobile Responsive Navigation Drawer & Real-Time Input Badges**
- [x] **Automated PDF / HTML / Markdown / JSON Security Report Generation**
- [x] **Production Containerization (Docker Compose & Nginx Reverse Proxy)**
- [x] **GitHub Actions CI/CD Multi-Version Matrix Testing**
- [x] **Multi-Target CIDR Subnet Scanning & Batch Execution**
- [x] **Asset Inventory & Attack Surface Management (ASM)**
- [ ] **Webhook Notifications** (Slack, Discord, Microsoft Teams, Generic Webhook)
- [ ] **Recurring Scheduled Scans** (Cron-like interval scanning)
- [ ] **Multi-Node Distributed Worker Queue** (Redis + Celery support)
- [ ] **Custom Nuclei Private Git Template Repository Ingestion**

---

## 🔒 Security Disclosure Policy

The security of XenoraSec and its users is paramount. If you discover a vulnerability or security flaw:

1. **Do not open a public GitHub issue**.
2. Privately submit a detailed advisory through [GitHub Security Advisories](https://github.com/prithvi-01x/XenoraSec/security/advisories/new) or contact the maintainer directly.
3. Include detailed reproduction steps, proof-of-concept payload, and the environment affected.
4. We follow coordinated disclosure and will acknowledge receipt within 48 hours and work with you on an expedited patch.

---

## 🤝 Contributing & Community

We warmly welcome community contributions from security researchers and developers!

1. **Fork** the repository on GitHub.
2. Create a feature branch (`git checkout -b feature/amazing-feature`).
3. Ensure backend tests pass (`pytest`) and frontend builds cleanly (`npm run build`).
4. Commit your changes following [Conventional Commits](https://www.conventionalcommits.org/) format.
5. Push to your branch (`git push origin feature/amazing-feature`).
6. Open a Pull Request detailing the changes made and tests performed.

---

## 📄 License & Acknowledgements

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

### Acknowledgements
- [Nmap Security Scanner](https://nmap.org/) by Gordon Lyon (Fyodor)
- [Nuclei Vulnerability Scanner](https://github.com/projectdiscovery/nuclei) by the ProjectDiscovery team
- [FastAPI](https://fastapi.tiangolo.com/) by Sebastián Ramírez
- [Groq](https://groq.com/) for low-latency LPU AI inference

<p align="center">
  <b>Built with 🛡️ for ethical hackers, defense engineers, and DevSecOps professionals.</b>
</p>