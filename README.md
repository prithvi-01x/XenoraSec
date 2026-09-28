# 🛡️ XenoraSec - Advanced Vulnerability Scanner

> **Next-Generation Autonomous Security Assessment & Threat Surface Discovery Engine**

<p align="center">
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white" alt="Python Versions"></a>
  <a href="https://fastapi.tiangolo.com/"><img src="https://img.shields.io/badge/FastAPI-0.109-009688.svg?logo=fastapi&logoColor=white" alt="FastAPI"></a>
  <a href="https://react.dev/"><img src="https://img.shields.io/badge/React-19+-61DAFB.svg?logo=react&logoColor=black" alt="React 19"></a>
  <a href="https://www.typescriptlang.org/"><img src="https://img.shields.io/badge/TypeScript-5.0+-3178C6.svg?logo=typescript&logoColor=white" alt="TypeScript 5"></a>
  <a href="https://tailwindcss.com/"><img src="https://img.shields.io/badge/TailwindCSS-3.4+-06B6D4.svg?logo=tailwindcss&logoColor=white" alt="TailwindCSS"></a>
  <a href="https://www.docker.com/"><img src="https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white" alt="Docker"></a>
  <a href="https://groq.com/"><img src="https://img.shields.io/badge/AI-Groq%20%2B%20Llama%203.3-F05A28.svg" alt="Groq AI"></a>
  <a href="https://github.com/prithvi-01x/XenoraSec/actions/workflows/ci.yml"><img src="https://github.com/prithvi-01x/XenoraSec/actions/workflows/ci.yml/badge.svg" alt="CI Status"></a>
  <a href="https://nmap.org/"><img src="https://img.shields.io/badge/Engine-Nmap%207.94+-blue.svg" alt="Nmap"></a>
  <a href="https://github.com/projectdiscovery/nuclei"><img src="https://img.shields.io/badge/Engine-Nuclei%20v3.3.8-purple.svg" alt="Nuclei"></a>
  <a href="https://github.com/prithvi-01x/XenoraSec"><img src="https://img.shields.io/badge/Security-SSRF%20Guarded-success.svg" alt="Security Guarded"></a>
</p>

<p align="center">
  <a href="#-quick-start"><b>⚡ Quick Start</b></a> •
  <a href="#-architecture"><b>🏗️ Architecture</b></a> •
  <a href="#-rest-api-reference"><b>📡 API Reference</b></a> •
  <a href="#-dual-engine-scanning"><b>⚙️ Dual Engine</b></a> •
  <a href="#-passive-reconnaissance--osint-engine"><b>🌐 Passive OSINT</b></a> •
  <a href="#-asset-inventory--attack-surface-management"><b>🏢 Asset Management</b></a> •
  <a href="#-production-deployment"><b>🚢 Docker</b></a>
</p>

<p align="center">
  <img src="Screenshots/17.png" width="900" alt="XenoraSec Platform Dashboard">
</p>

---

### 📊 Executive Platform Summary

| Dimension | XenoraSec Specification | Industry Standard / Alternative Scanners |
| :--- | :--- | :--- |
| **Core Architecture** | Fully non-blocking `asyncio` backend (FastAPI + React 19) | Threaded or synchronous WSGI blocking architectures |
| **Active Reconnaissance** | Unprivileged `-sT -sV` TCP connect scanning with fault-tolerant XML parser | Raw root-requiring `-sS` scans prone to cloud container drops |
| **Vulnerability Detection** | Line-by-line JSONL streaming engine (Nuclei v3.3.8) with ring-buffer cap | Monolithic batch execution buffering hundreds of MB in RAM |
| **Passive OSINT & Recon** | crt.sh CT mining, Cloudflare DoH, RFC 7208/7489 email hygiene, TLS telemetry | Fragmented CLI tools requiring separate bash scripting |
| **Risk Scoring Model** | Bounded Michaelis-Menten saturation ($V_{\max}=10, K_m=15$) + Groq Llama 3.3 | Unbounded linear additions or arbitrary subjective thresholds |
| **Concurrency & Storage** | SQLite Write-Ahead Logging (WAL) + 30s busy timeout / PostgreSQL asyncpg | File-locking SQLite errors during concurrent browser polling |
| **Streaming UI Telemetry** | Server-Sent Events (SSE) & WebSocket interactive terminal replay | Polling-only spinner modals with zero raw tool visibility |
| **Defensive Safeguards** | Zero-trust SSRF, DNS pre-resolution, proxy anti-spoofing, zombie cleanup | Permissive internal network loops and reverse-proxy spoof vulnerabilities |

---

## 📑 Table of Contents

- [🔍 Overview](#-overview)
- [✨ Key Features](#-key-features)
- [🏗️ Architecture & Pipeline](#-architecture--pipeline)
- [⚙️ Dual-Engine Scanning Mechanics](#-dual-engine-scanning-mechanics)
- [🌐 Multi-Target & CIDR Subnet Scanning](#-multi-target--cidr-subnet-scanning)
- [🌐 Passive Reconnaissance & OSINT Engine](#-passive-reconnaissance--osint-engine)
- [🏢 Asset Inventory & Attack Surface Management](#-asset-inventory--attack-surface-management)
- [🧠 AI Risk Scoring & Saturation Model](#-ai-risk-scoring--saturation-model)
- [💻 Live Terminal & Streaming Engine](#-live-terminal--streaming-engine)
- [📑 Multi-Format Security Report Generation](#-multi-format-security-report-generation)
- [🔒 Security Safeguards & Defensive Engineering](#-security-safeguards--defensive-engineering)
- [🗄️ Database Architecture & Concurrency](#-database-architecture--concurrency)
- [📡 REST API Reference](#-rest-api-reference)
- [💻 cURL Command Cookbook](#-curl-command-cookbook)
- [⚙️ Environment Configuration](#-environment-configuration)
- [🚀 Installation & Local Development Setup](#-installation--local-development-setup)
- [🚢 Production Deployment (Docker & Nginx)](#-production-deployment)
- [🛡️ Container Hardening & Non-Root Security](#-container-hardening--non-root-security)
- [🔄 CI/CD Automation Pipeline](#-cicd-automation-pipeline)
- [💻 Frontend Tour & Mobile Responsiveness](#-frontend-tour--mobile-responsiveness)
- [🎨 Tactical Dark UI Design System](#-tactical-dark-ui-design-system)
- [🧪 Testing & Quality Assurance](#-testing--quality-assurance)
- [⚡ Performance Benchmarks & Tuning](#-performance-benchmarks--tuning)
- [❓ Troubleshooting & FAQ](#-troubleshooting--faq)
- [📁 Project Structure](#-project-structure)
- [🗺️ Product Roadmap](#-product-roadmap)
- [🔒 Security Disclosure Policy & Safe Harbor](#-security-disclosure-policy--safe-harbor)
- [🤝 Contributing & Developer Guidelines](#-contributing--developer-guidelines)
- [📄 License & Acknowledgements](#-license--acknowledgements)

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
8. **Passive Reconnaissance & OSINT Intelligence Engine**: Autonomous Certificate Transparency log mining (crt.sh), SAN/wildcard certificate decomposition, asynchronous multi-record DNS resolution (A, AAAA, CNAME, MX, TXT, NS, SOA, PTR), SPF/DMARC mail spoofing hygiene scoring, passive HTTP/HTTPS tech stack fingerprinter (server tokens, cookie heuristics, meta tags, CMS signatures), defensive security headers grading, and direct 1-click sync to Asset Inventory.

### 🏗️ Architecture & Pipeline
```mermaid
flowchart TB
    subgraph Client ["Client Layer (Browser & Mobile)"]
        UI["React 19 + Vite SPA"]
        TQ["TanStack Query (Auto-Polling & Cache)"]
        TERM["Live Terminal Component (SSE / WS Replay)"]
        UI <--> TQ
        UI <--> TERM
    end

    subgraph SecurityGate ["Security & Ingress Gate"]
        RL["Sliding-Window Rate Limiter\n(Proxy Header Validation)"]
        VAL["Target Sanitizer & DNS Resolver\n(SSRF / Rebinding Guard)"]
        SEM["Concurrency Slot Governor\n(MAX_CONCURRENT_SCANS)"]
    end

    subgraph Core ["FastAPI Asynchronous Backend"]
        ROUTER["REST API Routes\n(/api/scan, /api/recon, /api/assets)"]
        TASK["Background Task Worker\n(_run_and_store_scan)"]
        HUB["Live Terminal Streaming Hub\n(1000-Line Circular Buffer)"]
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

    subgraph Persistence ["Persistence Layer & State"]
        DB[("SQLite (WAL Mode + 30s Busy Timeout)\n/ PostgreSQL asyncpg")]
        ASM[("Asset Inventory Registry\n(assets, ports, vulns)")]
    end

    Client -->|HTTP / JSON| RL
    RL --> VAL
    VAL --> SEM
    SEM --> ROUTER
    ROUTER -->|Spawn Background Task| TASK
    TASK -->|Async Exec & Stream| NMAP
    TASK -->|Async Stream JSONL| NUCLEI
    NMAP -->|Lines / Ports| HUB
    NUCLEI -->|Findings / Logs| HUB
    HUB -.->|SSE / WebSocket| TERM
    NMAP --> Analysis
    NUCLEI --> Analysis
    HEUR --> AGG
    GROQ -.->|Optional Fallback| AGG
    AGG -->|Atomic Transaction| DB
    AGG -->|Delta Upsert| ASM
    ROUTER -.->|Poll State| DB
```

#### Detailed Scan Request Lifecycle & Sequence Flow
```mermaid
sequenceDiagram
    autonumber
    actor User as Security Analyst (Browser)
    participant RateGate as RateLimiter & Proxy Guard
    participant ValGate as SSRF & DNS Sanitizer
    participant Router as FastAPI Router (/api/scan)
    participant Worker as Background Worker
    participant StreamHub as Terminal Streaming Hub
    participant Nmap as Nmap Subprocess (-sT -sV)
    participant Nuclei as Nuclei Subprocess (-jsonl)
    participant AISvc as AI Risk Service (MM + Groq)
    participant DB as SQLite WAL / Postgres

    User->>RateGate: POST /api/scan/ {target: "example.com"}
    RateGate->>RateGate: Verify Client IP & Sliding Window Quota
    RateGate->>ValGate: Forward Target String
    ValGate->>ValGate: socket.getaddrinfo() & RFC 1918 / Loopback Check
    ValGate->>Router: Sanitized Hostname & Resolved IP
    Router->>DB: INSERT scan_result (status="running")
    Router->>Worker: Dispatch asyncio.create_task(_run_and_store_scan)
    Router-->>User: HTTP 200 {scan_id, status: "running"}

    par Parallel Dual Engine Scanning
        Worker->>Nmap: Exec async subprocess (-sT -sV -Pn -oX -)
        Worker->>Nuclei: Exec async subprocess (-jsonl -silent -no-interactsh)
        loop Live Stdout Streaming
            Nmap-->>StreamHub: Stdout line (Port discovery)
            Nuclei-->>StreamHub: Stdout JSONL (Vulnerability match)
            StreamHub-->>User: SSE / WebSocket event broadcast
        end
    end

    Nmap-->>Worker: XML completed / EOF
    Nuclei-->>Worker: JSONL stream completed / EOF
    Worker->>Worker: Parse XML (Port table) & JSONL (Vuln list)
    Worker->>AISvc: Compute Composite Risk (MM Formula)
    opt Groq LLM Enabled
        AISvc->>AISvc: Query Groq Llama 3.3 70B (10s timeout fallback)
    end
    AISvc-->>Worker: Final Risk Score (0.0 - 10.0) & AI Summary
    Worker->>DB: UPDATE scan_result (status="completed", score, findings)
    Worker->>DB: Upsert Asset Inventory (host, open ports, CVE associations)
    User->>Router: GET /api/scan/results/{scan_id}
    Router->>DB: SELECT scan_result
    DB-->>Router: Result Record
    Router-->>User: Final Scan Dossier & Risk Intelligence
```

#### Subsystem: Event-Driven Real-Time Telemetry Pipeline
```mermaid
flowchart LR
    subgraph Execution ["Subprocess Execution"]
        PROC1["Nmap stdout"]
        PROC2["Nuclei stdout"]
    end

    subgraph Hub ["In-Memory Streaming Hub"]
        RING["1000-Line Circular Ring Buffer"]
        FANOUT["Async Broadcast Queue (fanout)"]
        ANSI["ANSI Color & Control Code Sanitizer"]
    end

    subgraph Transports ["Transport Protocols"]
        SSE["Server-Sent Events (SSE)\ntext/event-stream"]
        WS["WebSocket Server\nFull-Duplex Text Frames"]
    end

    subgraph ClientTerminal ["Frontend Interactive Console"]
        UI_TERM["Terminal Output Grid"]
        AUTO_SCROLL["Smart Auto-Scroll Lock"]
        SEARCH["In-Buffer RegEx Search"]
    end

    PROC1 --> ANSI
    PROC2 --> ANSI
    ANSI --> RING
    RING --> FANOUT
    FANOUT --> SSE
    FANOUT --> WS
    SSE --> UI_TERM
    WS --> UI_TERM
    UI_TERM --> AUTO_SCROLL
    UI_TERM --> SEARCH
```

---

## ⚙️ Dual-Engine Scanning Mechanics

XenoraSec integrates two premier security tools through asynchronous streaming wrappers designed for resilience, thread-safety, and minimal memory footprints:

```mermaid
flowchart TD
    subgraph Orchestration ["Asynchronous Scan Coordinator"]
        INIT["Scan Intake & Parameter Normalization"]
        DISPATCH["Parallel Subprocess Launcher\n(asyncio.create_subprocess_exec)"]
        INIT --> DISPATCH
    end

    subgraph NmapSubsystem ["Engine 1: Nmap Network Recon"]
        NMAP_EXEC["nmap -sT -sV -Pn --open -T4 -oX -"]
        NMAP_STREAM["Stdout Async Line Reader"]
        NMAP_XML["Fault-Tolerant XML Parser\n(Auto-Closing Tag Recovery)"]
        NMAP_EXEC --> NMAP_STREAM --> NMAP_XML
    end

    subgraph NucleiSubsystem ["Engine 2: Nuclei v3 Vulnerability Engine"]
        NUC_EXEC["nuclei -target <tgt> -jsonl -silent -no-interactsh -rl 50"]
        NUC_STREAM["Streaming Line Parser (JSONL)"]
        NUC_BUF["Adaptive 1MB Ring-Buffer & 1000-Finding Cap"]
        NUC_EXEC --> NUC_STREAM --> NUC_BUF
    end

    subgraph Aggregator ["Result Serialization & Normalization"]
        PORT_MAP["Open Ports & Services Schema"]
        VULN_MAP["Vulnerability Finding Schema\n(CVE, CVSS, Severity, Matched Path)"]
        SYNTH["Unified Threat Topology Synthesis"]
    end

    DISPATCH --> NMAP_EXEC
    DISPATCH --> NUC_EXEC
    NMAP_XML --> PORT_MAP --> SYNTH
    NUC_BUF --> VULN_MAP --> SYNTH
```

### 1. Nmap Network & Service Recon Engine

#### Non-Root Architecture & TCP Connect Scans
Unlike traditional scanners that mandate `sudo` / `CAP_NET_RAW` privileges for SYN stealth packets (`-sS`), XenoraSec defaults to standard **TCP Connect** (`-sT`). This provides key production benefits:
- **Cloud & Container Agnostic**: Runs effortlessly inside unprivileged Docker containers, AWS ECS tasks, and Kubernetes pods where raw socket creation is strictly forbidden.
- **Socket Cleanliness**: Fully completes the three-way handshake (`SYN` $\to$ `SYN-ACK` $\to$ `ACK` $\to$ `RST`), ensuring OS kernel network stacks manage TCP state gracefully without leaking kernel memory or leaving half-open connections.

#### Timing Templates & Concurrency Policy Matrix
XenoraSec supports dynamic timing templates configured via the `NMAP_TIMING` environment variable or per-scan overrides:

| Timing Policy | Flag | Min / Max Probe Delay | Initial / Max RTT Timeout | Host Concurrency | Primary Use Case |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Paranoid** | `-T0` | 5 minutes / 5 minutes | 5 seconds / 15 seconds | 1 host | Evading aggressive IDS/IPS packet counters |
| **Sneaky** | `-T1` | 15 seconds / 15 seconds | 1.5 seconds / 10 seconds | 1 host | Low-noise stealth assessment |
| **Polite** | `-T2` | 400 ms / 1 second | 1 second / 10 seconds | 1 host | Minimizing target server load and bandwidth |
| **Normal** | `-T3` | 0 ms / 1 second | 100 ms / 10 seconds | Dynamic | Default standard network audit |
| **Aggressive** | `-T4` | 0 ms / 10 ms | 100 ms / 1.25 seconds | Up to 1024 | **XenoraSec Default**: High-speed reliable LAN/Cloud scanning |
| **Insane** | `-T5` | 0 ms / 5 ms | 50 ms / 300 ms | Up to 4096 | High-speed local subnets, local development tests |

#### Port Selection & Range Syntax
- **Top Ports**: Accepts standard shortcuts such as `--top-ports 100` (rapid recon) or `--top-ports 1000` (standard profile).
- **Custom Port Ranges**: Accepts comma-separated ports and ranges (`22,80,443,8000-8080,8443`).
- **Full Port Audits**: When designated in custom profiles, supports all 65,535 TCP ports (`-p 1-65535`).

#### Fault-Tolerant XML Streaming Parser
Standard Python XML libraries (`xml.etree.ElementTree`) fail catastrophically if an XML document is incomplete or abruptly truncated. XenoraSec's `NmapParser` implements a defensive state-machine parser:
1. **Real-Time Extraction**: Streams output line-by-line, tracking `<host>`, `<port>`, `<service>`, and `<state>` tags.
2. **Auto-Recovery on Truncation**: If the scan times out or is cancelled, the parser checks for missing root/host closing tags (`</ports>`, `</host>`, `</nmaprun>`) and synthetically injects them to produce well-formed XML.
3. **Graceful Degraded Output**: Preserves any open port records discovered prior to the termination signal instead of zeroing the results.

---

### 2. Nuclei Vulnerability & Misconfiguration Engine

XenoraSec integrates **Nuclei v3.3.8**, the industry-standard template-driven vulnerability scanner maintained by ProjectDiscovery.

#### Template Hierarchy & Detection Categories
XenoraSec categorizes and dispatches Nuclei templates across modular security vectors:

| Template Category | Filter Tag | Detection Scope & Risk Class |
| :--- | :--- | :--- |
| **CVE Signatures** | `cve,cves` | Documented Common Vulnerabilities & Exposures across enterprise software |
| **Default Credentials** | `default-login,auth-bypass` | Exposed administrative login portals with factory or weak credentials |
| **Exposed Panels** | `panel,dashboard` | Exposed management consoles (Grafana, Kibana, Jenkins, Kubernetes, Docker) |
| **Cloud Misconfigurations**| `cloud,aws,azure,gcp` | Public S3 buckets, open Firebase databases, exposed metadata endpoints |
| **Subdomain Takeovers** | `takeover,cname` | Dangling CNAME records pointing to unclaimed S3, GitHub, Heroku, or Fastly endpoints |
| **Secrets & Token Leaks**| `token,keys,exposure` | Hardcoded API keys, JWT tokens, `.git` directory exposure, `.env` file leaks |
| **Network Protocols** | `ssl,dns,tls,network` | Weak cipher suites, expired TLS certificates, open DNS recursion |

#### Streaming JSONL Ingestion & Adaptive Ring Buffer
- **Line-by-Line JSONL Stream**: Nuclei is executed with `-jsonl -silent -no-interactsh`, emitting discrete JSON lines over stdout. This bypasses the need to write multi-gigabyte temporary files to disk.
- **Adaptive 1MB Ring-Buffer**: Output lines are collected into an in-memory buffer capped at `MAX_BUFFER_SIZE = 1_048_576` bytes. If the incoming buffer exceeds this threshold, the oldest 50% of the buffer is purged while strictly preserving newline boundaries.
- **Vulnerability Safety Cap**: `MAX_VULNERABILITIES = 1000` terminates the ingest loop if a target emits excessive findings (e.g. honeypots or wildcard servers), returning an HTTP warning rather than crashing the worker.
- **JSON Error Tolerance Threshold**: If upstream JSON decoding errors account for $\ge 20\%$ of lines received, the scan state is marked as `PARTIAL` rather than `FAILED`. Valid findings are preserved and surfaced to the analyst.

---

## 🌐 Multi-Target & CIDR Subnet Scanning

XenoraSec provides enterprise-grade mass scanning capabilities supporting both multi-target lists and standard IPv4 Classless Inter-Domain Routing (CIDR) subnet notations.

```mermaid
flowchart TD
    subgraph Submission ["Ingress Batch Submission"]
        INPUT["User Ingestion String\n(CIDR Subnets, Multi-line Hostnames, IPs)"]
        PARSE["Delimiter Normalizer\n(Split on comma, newline, whitespace)"]
        DEDUP["Deduplication & Canonical Trimming"]
        INPUT --> PARSE --> DEDUP
    end

    subgraph Expansion ["CIDR Prefix Expansion & Validation"]
        DEDUP --> CHECK_CIDR{"Is CIDR Notation?"}
        CHECK_CIDR -->|Yes| EVAL_PREFIX{"Prefix >= /24?"}
        EVAL_PREFIX -->|No (e.g. /16)| REJECT["Reject HTTP 422\n(Exceeds MAX_CIDR_PREFIX=24)"]
        EVAL_PREFIX -->|Yes| EXPAND["ipaddress.ip_network\n(Calculate Usable Host IPs)"]
        CHECK_CIDR -->|No| SINGLE["Direct Hostname / IP"]
        EXPAND --> BATCH_MANIFEST["Batch Target Manifest (Up to 256 Targets)"]
        SINGLE --> BATCH_MANIFEST
    end

    subgraph QueueOrchestration ["Concurrency Controlled Queue"]
        BATCH_MANIFEST --> DISPATCHER["Batch Task Worker"]
        DISPATCHER --> SEM["asyncio.Semaphore(BATCH_CONCURRENCY=3)"]
        SEM --> W1["Worker Slot 1\n(Nmap + Nuclei)"]
        SEM --> W2["Worker Slot 2\n(Nmap + Nuclei)"]
        SEM --> W3["Worker Slot 3\n(Nmap + Nuclei)"]
    end

    subgraph Aggregation ["Batch Telemetry Aggregator"]
        W1 --> BATCH_STATE[("Batch State Record\n(total, completed, failed, mean_risk)")]
        W2 --> BATCH_STATE
        W3 --> BATCH_STATE
    end
```

### 1. Subnet Notation & Prefix Governance

Network security teams frequently need to assess complete subnets or IP blocks without manually listing every host:

| CIDR Prefix | Subnet Mask | Usable Host Count | Network & Broadcast Addresses | Default Assessment Time |
| :--- | :--- | :--- | :--- | :--- |
| **`/32`** | `255.255.255.255` | 1 host | Host route (single host) | ~30 - 60 seconds |
| **`/31`** | `255.255.255.254` | 2 hosts | RFC 3021 Point-to-Point link | ~1 - 2 minutes |
| **`/30`** | `255.255.255.252` | 2 usable hosts | Excludes .0 network and .3 broadcast | ~1 - 2 minutes |
| **`/29`** | `255.255.255.248` | 6 usable hosts | Excludes network and broadcast | ~3 - 5 minutes |
| **`/28`** | `255.255.255.240` | 14 usable hosts | Excludes network and broadcast | ~6 - 10 minutes |
| **`/27`** | `255.255.255.224` | 30 usable hosts | Excludes network and broadcast | ~15 - 20 minutes |
| **`/26`** | `255.255.255.192` | 62 usable hosts | Excludes network and broadcast | ~30 - 45 minutes |
| **`/25`** | `255.255.255.128` | 126 usable hosts | Excludes network and broadcast | ~1 - 1.5 hours |
| **`/24`** | `255.255.255.0` | 254 usable hosts | Full Class C subnet boundary | ~2 - 3 hours |

- **Defensive Prefix Guard**: To prevent accidental denial of service or database lockups, subnets broader than `/24` (such as `/16` with 65,534 hosts or `/8` with 16 million hosts) are rejected immediately at the API gate with HTTP 422:
  ```json
  {
    "detail": "Subnet mask /16 exceeds maximum allowed width (/24). Maximum allowed hosts per batch is 256."
  }
  ```
- **Network Boundary Exclusion**: Standard CIDR expansion automatically strips network (`.0`) and broadcast (`.255`) addresses to avoid transmitting non-routable packets.

---

### 2. Multi-Target List Ingestion & Sanitization
Targets can be supplied in flexible formats:
- **Flexible Delimiters**: Supports comma-delimited strings (`192.168.1.1, 192.168.1.2`), newline-separated lists, or mixed arrays combining domains, individual IPs, and CIDRs.
- **De-duplication & Trimming**: Automatically removes whitespace, carriage returns, and duplicate entries while preserving initial submission order.
- **Per-Target Zero-Trust Validation**: Each expanded target in the batch independently traverses the SSRF, DNS resolution, and blacklist/whitelist gating rules before queue intake.
- **Fault-Isolated Execution**: If one host in a 50-target batch fails DNS resolution or times out, that single scan is recorded as `FAILED`, while the remaining 49 scans continue executing without interruption.

---

### 3. Asynchronous Batch Queue & Concurrency Slots
- **Non-Blocking Ingestion**: Calling `POST /api/scan/batch` dispatches scans across background workers and returns immediately with a unique `batch_id` and scan manifest.
- **Controlled Worker Concurrency**: Scans are scheduled via `BATCH_CONCURRENCY` (default: 3) using an `asyncio.Semaphore`. This prevents local network interface exhaustion, file descriptor starvation, and SQLite lock contention.
- **Live Progress Telemetry**: The status endpoint `GET /api/scan/batch/{batch_id}` provides real-time counts (`total`, `completed`, `running`, `failed`, `pending`) and the aggregated arithmetic mean risk score across all batch targets:
  $$\bar{R}_{\text{batch}} = \frac{1}{N_{\text{completed}}} \sum_{i=1}^{N_{\text{completed}}} \text{RiskScore}_i$$

---

### 4. Interactive Frontend Batch Management
- **Target Mode Switcher**: Easily toggle between **Single Target** and **Multi-Target / Subnet** directly from the main `ScanPanel`.
- **Quick-Fill CIDR Chips**: One-click helper chips (`/30`, `/29`, `/28`, `/24`) for rapid testing and automated mask insertion.
- **Live Target Counter**: Real-time reactive preview displays the total number of detected valid targets, invalid targets, and estimated total scans before launching.
- **Batch Telemetry Modal**: A real-time popup monitor tracking per-scan progress, live execution state badges, target links, and final risk score summaries.

---

## 🌐 Passive Reconnaissance & OSINT Engine

Modern attack surface mapping begins long before the first active port probe or vulnerability template is transmitted. XenoraSec integrates a dedicated, asynchronous **Passive Reconnaissance & OSINT Engine** designed to discover shadow infrastructure, map domain topologies, audit email security posture, and fingerprint web applications without alerting target Intrusion Detection Systems (IDS/IPS) or violating non-intrusive assessment boundaries.

### 1. High-Level OSINT Architecture & Workflow

The engine orchestrates four parallel analysis pipelines coordinated by `ReconEngine` (`app/services/recon_service.py`):

```mermaid
flowchart TD
    subgraph Ingestion ["Recon Dispatch & Parameter Ingestion"]
        REQ["Recon Request\n(Domain, Flags: Subdomains, DNS, TechStack)"]
        VAL["Domain Sanitizer & FQDN Parser"]
        REQ --> VAL
    end

    subgraph Phase1 ["Phase 1: Passive Subdomain Discovery"]
        CRT["crt.sh CT Log Scraper\n(Exponential Backoff & Jitter)"]
        PDNS["Passive DNS Fallback Provider\n(Cloudflare DoH / HackerTarget)"]
        SAN["SAN & Wildcard Normalizer\n(Regex Strip & Deduplication)"]
        RES["Async Bulk DNS Resolver\n(A & AAAA Record Mapping)"]
        
        VAL --> CRT
        VAL --> PDNS
        CRT --> SAN
        PDNS --> SAN
        SAN --> RES
    end

    subgraph Phase2 ["Phase 2: DNS & Network Topology"]
        DNS["Async Multi-Record Resolver\n(A, AAAA, CNAME, MX, TXT, NS, SOA)"]
        PTR["Reverse DNS (PTR) Resolution"]
        ASN["ASN & IP Geolocation Enrichment"]
        MAIL["Mail Posture Evaluator\n(SPF & DMARC Syntax & Policy Scoring)"]
        
        VAL --> DNS
        DNS --> PTR
        DNS --> ASN
        DNS --> MAIL
    end

    subgraph Phase3 ["Phase 3: Passive Tech Stack Fingerprinting"]
        HTTP["Async HTTP/HTTPS Response Probe\n(Header & Server Token Harvester)"]
        COOKIES["Session & Framework Cookie Heuristics"]
        HTML["HTML Meta Tags & Script Signatures"]
        CMS["CMS & Frontend Framework Engine"]
        SEC["Defensive Security Headers Grader\n(HSTS, CSP, X-Frame, X-Content)"]
        
        VAL --> HTTP
        HTTP --> COOKIES
        HTTP --> HTML
        HTTP --> CMS
        HTTP --> SEC
    end

    subgraph Integration ["Persistence & Tactical Action"]
        HIST[("Recon History Ledger\n(recon_history Table)")]
        ASSET["Asset Inventory Sync\n(1-Click Bulk Ingestion)"]
        SCAN["Dual-Engine Active Scan\n(Nmap / Nuclei Pivot)"]
        
        RES --> HIST
        MAIL --> HIST
        SEC --> HIST
        HIST --> ASSET
        ASSET --> SCAN
    end
```

### 2. Core Architectural Principles
- **True Passive Discovery**: External infrastructure discovery relies strictly on public Certificate Transparency logs and historical DNS archives; zero packets are sent directly to unmapped subdomains during discovery.
- **Fail-Soft Asynchronous Concurrency**: Discovery, DNS querying, and HTTP fingerprinting run concurrently via `asyncio.gather(return_exceptions=True)`. If crt.sh experiences temporary rate limiting or timeout, the engine automatically pivots to passive DNS fallbacks without aborting the audit.
- **Resilient DNS-over-HTTPS (DoH)**: Leverages dnspython with Cloudflare DoH (`https://cloudflare-dns.com/dns-query`) fallback, guaranteeing record resolution even in restricted container environments where egress UDP port 53 is blocked.
- **Persistent Tactical Intelligence**: Results are serialized into strongly-typed Pydantic schemas (`app/schemas/recon.py`) and recorded in the database `recon_history` table for historical delta analysis and rapid one-click export into the Asset Inventory.

### 3. Passive Subdomain Discovery & crt.sh Pipeline

Modern organizations deploy services across hundreds of ephemeral subdomains that are invisible to traditional dictionary brute-force attacks. XenoraSec leverages cryptographic Certificate Transparency logs to discover the true, unredacted attack perimeter:

- **Certificate Transparency (CT) Log Mining**:
  - Connects to public Certificate Transparency logs via the crt.sh REST API (`https://crt.sh/?q=%.{domain}&output=json`).
  - Utilizes exponential backoff with randomized jitter ($\Delta t = 2^{\text{attempt}} + \text{rand}(0.1, 0.8)$) across 3 retry attempts to handle sporadic upstream load shedding without failing the user's recon request.
- **SAN & Wildcard Normalization Engine**:
  - Extracts both `common_name` and multi-line `name_value` Subject Alternative Name (SAN) fields.
  - Strips leading wildcards (`*.internal.example.com` $\to$ `internal.example.com`), URI schemes (`https://`), trailing slashes, and port specifications.
  - Enforces strict target-domain boundary filtering, discarding unrelated domain certificates that frequently share multi-tenant SAN entries.
  - De-duplicates hostnames while annotating their verified discovery sources (`crt.sh`, `passive_dns`).
- **Cloudflare DNS-over-HTTPS (DoH) Resilient Resolver**:
  - When crt.sh experiences downtime or in locked-down environments where egress UDP port 53 is blocked, the engine routes queries to Cloudflare DoH (`https://cloudflare-dns.com/dns-query` with `Accept: application/dns-json`).
  - Implements DNS response code validation (`NOERROR`, `NXDOMAIN`, `SERVFAIL`).
- **Asynchronous DNS Resolution & IP Mapping**:
  - If `resolve_subdomains` is enabled, an asynchronous worker pool leverages `dnspython` to query A and AAAA records across all discovered subdomains concurrently (`asyncio.Semaphore(20)`).
  - Maps live IPv4/IPv6 addresses to each subdomain record.
  - Accurately tracks resolution status (`is_resolvable: true/false`), allowing analysts to immediately distinguish active infrastructure from dead DNS tombstones or stale CNAME takeover candidates.

---

### 4. DNS Topology, RDAP Referrals & Mail Posture Analysis

DNS records define the routing backbone, hosting infrastructure, and email authenticity of a target organization. XenoraSec's `DNSResolver` performs automated multi-record extraction, RDAP IP/ASN routing correlation, and email spoofing risk calculation:

| Record Type | Assessment Focus | Security Significance & Audit Invariant |
| :--- | :--- | :--- |
| **A / AAAA** | Direct host IP resolution (IPv4 & IPv6) | Uncovers dual-stack exposure and Origin IP addresses behind CDNs |
| **CNAME** | Canonical name routing & CDN aliases | Pinpoints dangling CNAME records vulnerable to Subdomain Takeover |
| **MX** | Mail Exchanger priority and gateways | Identifies mail providers (Google Workspace, Microsoft 365, Proofpoint) |
| **TXT** | Verification tokens & security policies | Discloses domain ownership, site-verification tokens, SPF/DMARC policies |
| **NS** | Authoritative Nameservers | Reveals DNS providers (Cloudflare, Route53, Akamai) and zone glue records |
| **SOA** | Start of Authority parameters | Zone serials, refresh/retry timers, and primary authoritative administrator |
| **PTR** | Reverse DNS mapping | Correlates IP addresses back to canonical cloud hostnames and PTR validation |

#### 🌐 RDAP Referral Routing & ASN Geolocation
For discovered IP endpoints, XenoraSec queries the Registration Data Access Protocol (RDAP) via authoritative Regional Internet Registries (RIRs: ARIN, RIPE, APNIC, LACNIC, AFRINIC):
- **Autonomous System Numbers (ASN)**: Resolves the upstream BGP AS Number (e.g. `AS13335 Cloudflare, Inc.`, `AS16509 Amazon.com`).
- **IP Network Blocks**: Identifies CIDR allocation blocks (`104.16.0.0/12`) and network registration name (`CLOUDFLARENET`).
- **Country & Geolocation**: Extracts authoritative country codes for geo-fencing compliance and data sovereignty audits.

#### 📬 SPF (RFC 7208) & DMARC (RFC 7489) Spoofing Risk Evaluator
Email spoofing remains a primary attack vector in initial access and executive impersonation. XenoraSec performs deep programmatic evaluation against RFC standards:

```mermaid
flowchart TD
    TXT["TXT DNS Records"] --> SPF_PARSE["Parse v=spf1 Record"]
    TXT --> DMARC_PARSE["Query _dmarc.{domain}"]

    subgraph SPFEval ["RFC 7208 SPF Syntax & Rule Engine"]
        SPF_PARSE --> COUNT_CHECK{"Multiple SPF Records?"}
        COUNT_CHECK -->|Yes| SPF_FAIL["RFC PermError (Domain Spoofable)"]
        COUNT_CHECK -->|No| MECH_CHECK{"All Mechanism Qualifier?"}
        MECH_CHECK -->|"-all"| SPF_PASS["Compliant HardFail (Secure)"]
        MECH_CHECK -->|"~all"| SPF_WARN["SoftFail Warning (Weak)"]
        MECH_CHECK -->|"?all" or "+all"| SPF_CRIT["Neutral / Pass (Critical Spoof Risk)"]
    end

    subgraph DMARCEval ["RFC 7489 DMARC Policy Tree"]
        DMARC_PARSE --> REC_EXISTS{"DMARC Record Published?"}
        REC_EXISTS -->|No| PARENT_CHECK{"Parent Domain Has DMARC?"}
        PARENT_CHECK -->|No| DMARC_NONE["No DMARC (Critical Spoofing Risk)"]
        PARENT_CHECK -->|Yes (sp=)| DMARC_SUB["Inherit Parent Subdomain Policy"]
        REC_EXISTS -->|Yes| POL_CHECK{"Inspect p= Policy"}
        POL_CHECK -->|"p=reject"| DMARC_REJECT["Strict Rejection (High Compliance)"]
        POL_CHECK -->|"p=quarantine"| DMARC_QUAR["Spam Quarantine (Moderate)"]
        POL_CHECK -->|"p=none"| DMARC_MONITOR["Monitoring Only (Zero Enforcement)"]
    end

    SPF_PASS --> METRIC["Composite Mail Security Score (0 - 100)"]
    SPF_WARN --> METRIC
    SPF_CRIT --> METRIC
    DMARC_REJECT --> METRIC
    DMARC_QUAR --> METRIC
    DMARC_MONITOR --> METRIC
    DMARC_NONE --> METRIC
```

- **RFC 7208 10-Lookup Limit**: Flags SPF records approaching or exceeding the 10 DNS lookup limit (`include`, `a`, `mx`, `ptr`, `exists`), which triggers client-side `PermError` in MTAs.
- **DKIM Selector Scanning**: Scans common selector prefixes (`google._domainkey`, `k1._domainkey`, `selector1._domainkey`) for cryptographic public key publication.
- **Unified Mail Security Verdict**: Generates an authoritative classification:
  - **`High Compliance` (80-100)**: `v=spf1 ... -all` with `p=reject` or `p=quarantine` (`pct=100`) and active forensic reporting (`rua=`).
  - **`Moderate` (50-79)**: Softfail `~all` or `p=quarantine` with partial rollout.
  - **`Vulnerable` (0-49)**: Missing DMARC, `p=none` monitoring, or permissive `+all` allowing unauthenticated impersonation.

---

### 5. Passive Tech Stack Fingerprinting & Security Headers Matrix

XenoraSec reconstructs the remote application architecture using non-intrusive heuristics, examining response metadata without sending aggressive fuzzing payloads:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                   Passive Fingerprint Ingestion Engine                  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
       ┌────────────────────────────┼────────────────────────────┐
       ▼                            ▼                            ▼
┌──────────────┐             ┌──────────────┐             ┌──────────────┐
│Server Headers│             │Cookie Schemes│             │HTML & Script │
│ - Nginx      │             │ - PHPSESSID  │             │ - Next.js    │
│ - Apache     │             │ - laravel    │             │ - WordPress  │
│ - Cloudflare │             │ - csrftoken  │             │ - React/Vue  │
│ - Envoy/K8s  │             │ - ASP.NET_   │             │ - Tailwind   │
└──────────────┘             └──────────────┘             └──────────────┘
```

- **Server Tokens & Infrastructure Headers**: Parses `Server`, `X-Powered-By`, `X-AspNet-Version`, `Via`, and `X-Generator` tokens with confidence weights.
- **Session & Framework Cookie Heuristics**: Detects frameworks by signature cookies (`PHPSESSID` $\to$ PHP, `laravel_session` $\to$ Laravel, `csrftoken` / `sessionid` $\to$ Django, `connect.sid` $\to$ Express/Node.js, `ASP.NET_SessionId` $\to$ ASP.NET, `JSESSIONID` $\to$ Java/Spring, `session` $\to$ Flask/Python).
- **DOM Signatures & CMS Markers**: Inspects HTML `<meta name="generator">` tags, script paths (`/wp-content/`, `/sites/default/`, `/_next/static/`), and framework markers (`data-reactroot`, `__vue_app__`).
- **Cryptographic TLS / SSL Metrics**: Probes HTTPS endpoints to extract real cryptographic negotiation parameters:
  - *Protocol Version*: Negotiated protocol (`TLSv1.3`, `TLSv1.2`).
  - *Certificate Identity*: Common Name (Subject) and Issuing Certificate Authority (CA).
  - *Validity & Expiry Monitoring*: Start date, expiration date, and remaining validity window in days.
- **Defensive Security Headers Score**: Evaluates 6 vital defensive headers:
  1. `Strict-Transport-Security` (HSTS & max-age duration)
  2. `Content-Security-Policy` (CSP presence & default-src restrictions)
  3. `X-Frame-Options` (Clickjacking defense: DENY / SAMEORIGIN)
  4. `X-Content-Type-Options` (MIME sniffing prevention: nosniff)
  5. `Referrer-Policy` (Information leakage mitigation)
  6. `Permissions-Policy` (Browser API restriction)

### 6. Interactive OSINT Intelligence Center & Asset Pivot

XenoraSec provides a full-featured tactical web console located at `/recon`, seamlessly linking passive discovery directly into active scanning and asset governance workflows:

- **Tactical Recon Dispatcher**:
  - Live domain query input with configurable toggle switches for subdomains, active DNS resolution, multi-record extraction, and web tech stack fingerprinting.
  - Asynchronous execution status indicators with timing telemetry.
- **Subdomain Discovery Matrix**:
  - Instant client-side filtering by subdomain name, live resolution status, and discovery source (`crt.sh`, `passive_dns`).
  - IP badge indicators displaying resolved IPv4/IPv6 addresses and quick-copy utilities.
  - Direct 1-click **"Audit Target"** launcher pivoting any discovered subdomain directly into active Nmap/Nuclei scanning.
  - Multi-select checkbox controls with bulk CSV export and instant **"Import to Assets"** synchronization.
- **DNS & Network Topology Inspector**:
  - Tabular breakdown organized across 5 record categories: `A / AAAA`, `MX Gateways`, `TXT & Policies`, `Nameservers (NS)`, and `IP ASN Blocks`.
  - Integrated Mail Security Card highlighting SPF syntax, DMARC enforcement policies, and an automated spoofing risk verdict (`Low`, `Medium`, `High`).
- **Tech Stack & Security Headers Card**:
  - Categorized technology cards (Servers, Frameworks, CMS, Cloud/CDN) with detection confidence percentages.
  - Defensive security headers scorecard evaluating HSTS, CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, and Permissions-Policy with remediation guidance.
- **Audit History & Quick Recon Shortcut**:
  - Slide-out history ledger reviewing prior recon audits for quick inspection without re-running queries.
  - Dedicated OSINT Quick Recon banner embedded directly on the main Operations Dashboard (`/`) for immediate access.

---

## 🏢 Asset Inventory & Attack Surface Management

XenoraSec transforms ephemeral scan results into a persistent, living Attack Surface Management (ASM) repository. Rather than losing port discoveries and CVE findings in isolated scan logs, assets are centrally tracked, classified, and monitored over time.

### 1. Automated Finding Ingestion & Delta Sync

Whenever any scan completes (whether launched individually, via a multi-target CIDR batch, or synced from passive OSINT):
- **Autonomous Indexing**: The backend service parses Nmap port tables and Nuclei vulnerability lists, automatically creating or updating asset records in the `assets` table.
- **Idempotent Upsert State Machine**: Repeated assessments of the same host do not clutter the database with duplicate assets. Instead, `upsert_asset_from_scan` performs an intelligent delta update:
  - Updates host metadata (`last_scanned_at`, `risk_score`, severity distribution counters).
  - Synchronizes open ports, updating service/version information and `last_seen` timestamps.
  - Links discovered vulnerabilities, preserving `first_seen` audit history and marking re-confirmed CVEs.

```mermaid
flowchart TD
    SCAN_FINISH["Scan Execution Finishes (Nmap + Nuclei)"] --> EXTRACT["Extract Host IP & FQDN"]
    EXTRACT --> QUERY{"Asset Exists in assets Table?"}
    QUERY -->|No| INSERT["INSERT new Asset Record\n(status: 'scanned', criticality: 'medium')"]
    QUERY -->|Yes| UPDATE["UPDATE Asset Metadata\n(last_scanned_at, risk_score, counts)"]
    
    INSERT --> PORT_LOOP["Iterate Discovered Ports"]
    UPDATE --> PORT_LOOP

    PORT_LOOP --> PORT_QUERY{"Port Already Linked?"}
    PORT_QUERY -->|No| INSERT_PORT["INSERT AssetPort\n(port, protocol, service, version)"]
    PORT_QUERY -->|Yes| UPDATE_PORT["UPDATE AssetPort\n(version, last_seen = NOW())"]

    INSERT_PORT --> VULN_LOOP["Iterate Discovered Vulnerabilities"]
    UPDATE_PORT --> VULN_LOOP

    VULN_LOOP --> VULN_QUERY{"Vulnerability Exists for Asset?"}
    VULN_QUERY -->|No| INSERT_VULN["INSERT AssetVulnerability\n(status: 'active', first_seen: NOW())"]
    VULN_QUERY -->|Yes| CONFIRM_VULN["UPDATE AssetVulnerability\n(status: 'active', last_seen: NOW(), reconfirmed: true)"]

    INSERT_VULN --> STATS_RECALC["Recalculate Perimeter KPI Metrics"]
    CONFIRM_VULN --> STATS_RECALC
```

### 2. Relational Entity Architecture & Indexing Strategy

```text
┌────────────────────────────────────────────────────────┐
│                        Asset                           │
│  - id: Integer (PK)                                    │
│  - ip_address: String (Indexed, b-tree)                │
│  - hostname: String (Nullable, Indexed)                │
│  - asset_type: 'ip' | 'domain' | 'url' | 'cidr_host'   │
│  - status: 'active' | 'scanned' | 'inactive'           │
│  - criticality: 'low' | 'medium' | 'high' | 'critical' │
│  - risk_score: Float (0.0 - 10.0, Indexed)             │
│  - open_ports_count, vulns_count, severity counters    │
│  - tags: JSON List / notes: Text                       │
│  - created_at, updated_at, last_scanned_at: Timestamp  │
└───────────────────────────┬────────────────────────────┘
                            │ 1:N Relationships (Cascade Delete)
             ┌──────────────┴──────────────┐
             ▼                             ▼
┌─────────────────────────┐   ┌──────────────────────────────┐
│       AssetPort         │   │      AssetVulnerability      │
│ - id: Integer (PK)      │   │ - id: Integer (PK)           │
│ - asset_id: Integer (FK)│   │ - asset_id: Integer (FK)     │
│ - port: Integer         │   │ - template_id: String        │
│ - protocol: 'tcp'|'udp' │   │ - name: String               │
│ - service: String       │   │ - severity: SeverityEnum     │
│ - product: String       │   │ - cvss: Float (Nullable)     │
│ - version: String       │   │ - cve: String (Nullable)     │
│ - last_seen: Timestamp  │   │ - matched_at: String         │
│                         │   │ - status: 'active'|'resolved'│
│                         │   │ - first_seen, last_seen      │
└─────────────────────────┘   └──────────────────────────────┘
```

- **Composite Query Optimization**: Indexes on `(criticality, risk_score)` and `(status, last_scanned_at)` ensure sub-millisecond filtering even across thousands of indexed enterprise assets.
- **Referential Integrity**: All child ports and vulnerabilities use foreign key constraints with `ON DELETE CASCADE`.

---

### 3. Business Criticality Classification & Triage Governance

Security teams can govern their perimeter through customizable criticality tiers:

| Criticality Tier | Target Types | Scanning Cadence | Remediation SLA |
| :--- | :--- | :--- | :--- |
| **`Critical`** | Production auth gateways, payment processors, core databases | Daily continuous audits | 24 Hours |
| **`High`** | Public APIs, customer dashboards, primary mail servers | Weekly scans | 7 Days |
| **`Medium`** | Staging environments, corporate blogs, documentation sites | Bi-weekly scans | 30 Days |
| **`Low`** | Internal sandbox servers, retired test infrastructure | Monthly scans | Best effort |

### 4. Lifecycle Operations & Tactical Re-Scanning
- **1-Click Deep Audit**: Re-trigger active assessments directly against any registered asset via `POST /api/assets/{id}/scan`, automatically inheriting preferred scan profiles and options.
- **Perimeter Metric Aggregation**: Rapidly query overall posture statistics with `GET /api/assets/stats`, returning real-time counts across asset types, risk bands, open ports, and active vulnerabilities.
- **Interactive Asset Inspection Drawer**: In the web UI, clicking any asset opens a slide-out drawer presenting open port matrices, version tags, CVSS severity charts, and CVE references with direct links to NVD and GitHub Security Advisories.

---

## 🧠 AI Risk Scoring & Saturation Model

Security teams need risk scores that are both **contextually intelligent** and **mathematically predictable**. Traditional scanners often use arbitrary unbounded sums (where 20 low-severity bugs produce an alarming "score 100") or simplistic step functions that hide nuances. XenoraSec implements a hybrid evaluation system marrying biochemical enzyme saturation kinetics with large language model context.

### 1. The Michaelis-Menten Mathematical Saturation Model

Adapted from the Michaelis-Menten biochemical kinetics model ($\text{rate} = \frac{V_{\max} \cdot [S]}{K_m + [S]}$), XenoraSec models the relationship between cumulative vulnerability exposure ($S$) and organizational risk ($\text{Score} \in [0.0, 10.0]$):

$$\text{Risk Score} = V_{\max} \cdot \left( \frac{S}{S + K_m} \right)$$

Where:
- **$V_{\max} = 10.0$**: The theoretical asymptotic risk score ceiling (perfect compromise).
- **$K_m = 15.0$**: The half-saturation constant — exactly $15.0$ units of raw vulnerability exposure are required to yield a balanced midpoint score of $5.0$.
- **$S$**: The accumulated raw vulnerability and network exposure score.

```text
Risk Score (0 - 10)
  10.0 ┤                                        . - - - - - - - Asymptote Vmax = 10.0
   9.0 ┤                                  . · ´
   8.0 ┤                            . · ´
   7.0 ┤                      . · ´
   6.0 ┤                . · ´
   5.0 ┤----------. · ´ (Km = 15.0, Score = 5.0)
   4.0 ┤        . ´
   3.0 ┤      . ´
   2.0 ┤    . ´
   1.0 ┤  . ´
   0.0 ┼──┴─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────►
       0    5   10   15   20   25   30   35   40   45   50   Raw Score (S)
```

#### Raw Exposure ($S$) Formulation

$$S = \sum_{v \in V} \text{BaseWeight}(\text{severity}_v) + \sum_{v \in V} \left( \text{CVSS}_v \times 0.15 \right) + \min\left( \text{open\_ports} \times 0.05, 1.0 \right)$$

| Finding Component | Base Weight | Modifier / Cap | Description |
| :--- | :--- | :--- | :--- |
| **Critical Finding** | `5.0` | N/A | Remotely exploitable RCE, unauthenticated admin takeover, SQLi |
| **High Finding** | `3.0` | N/A | Privileged data exfiltration, SSRF, major auth flaws |
| **Medium Finding** | `2.0` | N/A | Reflected XSS, CSRF, insecure transport cipher suites |
| **Low Finding** | `1.0` | N/A | Information disclosure, verbose error stacks |
| **Info / Unknown** | `0.5` | N/A | Software version banners, DNS zone metadata |
| **CVSS Modifier** | Variable | $\times 0.15$ | Weight proportional to official CVSS v3.1 base score |
| **Open Port Surface**| Variable | $\min(P \times 0.05, 1.0)$ | Perimeter footprint factor (capped at 1.0 point across 20+ open ports) |

#### Step-by-Step Worked Scenarios

##### Scenario A: Low-Exposure Perimeter Asset
- **Asset**: Static landing page with 2 open ports (80, 443) and 1 informational header finding (`http-missing-security-headers`, CVSS 0.0).
- **Calculation**:
  $$S = 0.5 + (0.0 \times 0.15) + \min(2 \times 0.05, 1.0) = 0.5 + 0.0 + 0.10 = 0.60$$
  $$\text{Risk Score} = 10.0 \times \left( \frac{0.60}{0.60 + 15.0} \right) = 10.0 \times \frac{0.60}{15.60} \approx \mathbf{0.38} \quad \text{(Low Risk)}$$

##### Scenario B: Typical Corporate Web Portal
- **Asset**: Web application with 3 open ports (80, 443, 8080), 1 Medium finding (`cve-2023-xxxx` XSS, CVSS 6.1), and 1 Low finding (`tls-weak-cipher`, CVSS 3.7).
- **Calculation**:
  $$S = [2.0 + (6.1 \times 0.15)] + [1.0 + (3.7 \times 0.15)] + \min(3 \times 0.05, 1.0)$$
  $$S = [2.0 + 0.915] + [1.0 + 0.555] + 0.15 = 2.915 + 1.555 + 0.15 = 4.62$$
  $$\text{Risk Score} = 10.0 \times \left( \frac{4.62}{4.62 + 15.0} \right) = 10.0 \times \frac{4.62}{19.62} \approx \mathbf{2.35} \quad \text{(Medium Risk)}$$

##### Scenario C: Active Remote Code Execution (RCE) Compromise
- **Asset**: Internal API gateway with 5 open ports, 1 Critical finding (`log4shell` RCE, CVSS 10.0), and 1 High finding (SSRF, CVSS 8.6).
- **Calculation**:
  $$S = [5.0 + (10.0 \times 0.15)] + [3.0 + (8.6 \times 0.15)] + \min(5 \times 0.05, 1.0)$$
  $$S = [5.0 + 1.50] + [3.0 + 1.29] + 0.25 = 6.50 + 4.29 + 0.25 = 11.04$$
  $$\text{Risk Score} = 10.0 \times \left( \frac{11.04}{11.04 + 15.0} \right) = 10.0 \times \frac{11.04}{26.04} \approx \mathbf{4.24} \quad \text{(Elevated)}$$

##### Scenario D: Severely Compromised Host (Asymptotic Saturation)
- **Asset**: Multi-vulnerability testbed with 15 open ports, 4 Critical RCEs (CVSS 9.8), 6 High vulnerabilities (CVSS 7.5), and 10 Medium findings.
- **Calculation**:
  $$S = 4 \times [5.0 + 1.47] + 6 \times [3.0 + 1.125] + 10 \times [2.0 + 0.75] + 0.75 = 25.88 + 24.75 + 27.50 + 0.75 = 78.88$$
  $$\text{Risk Score} = 10.0 \times \left( \frac{78.88}{78.88 + 15.0} \right) = 10.0 \times \frac{78.88}{93.88} \approx \mathbf{8.40} \quad \text{(Critical)}$$

#### Mathematical Guarantees
1. **Strict Monotonicity**: Adding any discovery strictly increases the score: $\frac{\partial \text{Score}}{\partial S} = \frac{V_{\max} \cdot K_m}{(S + K_m)^2} > 0$ for all $S \ge 0$.
2. **Asymptotic Boundedness**: For any infinite collection of vulnerabilities, $\lim_{S \to \infty} \text{Score} = V_{\max} = 10.0$. The score cannot exceed 10.0.
3. **Diminishing Marginal Risk**: The derivative $\frac{\partial \text{Score}}{\partial S}$ decreases monotonically with $S$, ensuring the first critical vulnerability has the largest marginal impact.

---

### 2. Groq Cloud LLM Contextual Analysis & Circuit Breaker

While the Michaelis-Menten formula establishes reproducible quantitative scoring, real-world risk depends on **attack chaining** (e.g. how an open SSH port links with leaked credentials or how a web SSRF accesses an internal metadata service).

```mermaid
flowchart LR
    FINDINGS["Scan Discoveries\n(Ports + Nuclei JSONL)"] --> MM["Michaelis-Menten Evaluator\n(Deterministic Baseline)"]
    FINDINGS --> PROMPT["Contextual Threat Prompt Builder"]
    PROMPT --> GROQ["Groq Cloud API\n(Llama 3.3 70B Versatile)"]
    GROQ -->|Success <= 10s| SYNTH["Synthesized Security Brief\n(Attack Paths & Exploit Chain)"]
    GROQ -->|Timeout / Quota / 5xx| FALLBACK["Circuit Breaker Fallback\n(Return Deterministic Baseline)"]
    MM --> SYNTH
    MM --> FALLBACK
```

#### Prompt Engineering & Structured Inference
When `GROQ_API_KEY` is provided, `AIService` issues an inference request to `llama-3.3-70b-versatile` running on Groq's low-latency LPU infrastructure:
- **Zero-Temperature Determinism**: Configured with `temperature: 0.1` and `response_format: {"type": "json_object"}`.
- **Threat Vector Synthesis**: The model evaluates whether open service versions (e.g. OpenSSH 7.2p2) correlate with web application CVEs.
- **Fail-Safe Circuit Breaker**:
  - A strict **10-second timeout** (`timeout=10.0`) wraps the HTTP client call.
  - If Groq returns HTTP 429 (rate limited), HTTP 503, invalid JSON, or times out, the exception is caught and logged.
  - The scan status remains `COMPLETED`, returning the Michaelis-Menten score with `ai_augmented: false` without delaying scan delivery.

---

## 💻 Live Terminal & Streaming Engine

Traditional security scanners hide process execution behind generic spinning loaders, leaving engineers blind to intermediate discoveries, hung processes, or long-running service probes. XenoraSec features an interactive **Live Terminal Streaming Engine** providing transparent, real-time command output straight from `stdout`/`stderr` of running Nmap and Nuclei subprocesses.

```mermaid
flowchart TD
    subgraph Capture ["Subprocess Output Capture"]
        P1["Nmap Subprocess"] -->|asyncio.StreamReader| S1["Nmap Stream Task"]
        P2["Nuclei Subprocess"] -->|asyncio.StreamReader| S2["Nuclei Stream Task"]
    end

    subgraph Hub ["ScanStreamHub (Memory Managed)"]
        S1 --> SANITIZE["ANSI Code Normalizer & Sanitizer"]
        S2 --> SANITIZE
        SANITIZE --> RING["1000-Line Circular Deque Replay Buffer"]
        SANITIZE --> BROADCAST["Async Broadcast Queue (Pub/Sub)"]
    end

    subgraph Channels ["Streaming Ingress & Transports"]
        BROADCAST --> SSE["SSE Transport\n(text/event-stream)"]
        BROADCAST --> WS["WebSocket Transport\n(/api/scan/{id}/ws)"]
    end

    subgraph ClientLayer ["Interactive Frontend Console"]
        SSE -.-> CONSOLE["React LiveTerminal Component"]
        WS -.-> CONSOLE
        RING -->|Initial History Replay on Connect| CONSOLE
    end
```

### 1. Dual Transport Architecture: SSE & WebSockets

XenoraSec supports both unidirectional Server-Sent Events (SSE) and full-duplex WebSockets:

| Dimension | Server-Sent Events (SSE) | WebSocket Channel |
| :--- | :--- | :--- |
| **Endpoint** | `GET /api/scan/{scan_id}/stream` | `WS /api/scan/{scan_id}/ws` |
| **MIME / Protocol** | `text/event-stream` (HTTP/1.1 or HTTP/2) | `RFC 6455` bidirectional binary/text frames |
| **Connection Overhead** | Minimal; standard HTTP request with Keep-Alive | Handshake upgrade required (`Upgrade: websocket`) |
| **Proxy Compatibility** | Works through any standard HTTP reverse proxy | Requires proxy upgrade headers in Nginx / Cloudflare |
| **Use Case** | Lightweight browser telemetry and headless cURL monitoring | Interactive low-latency bi-directional terminal controls |

#### Standard Event Payload Format
Every emitted line is packaged as a structured JSON object:

```json
{
  "scan_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "timestamp": "2026-09-28T13:42:15.102Z",
  "source": "nuclei",
  "level": "warning",
  "message": "[cve-2023-46805] [http] [critical] https://target.example.com/api/v1/totp/user-backup-code",
  "ansi_formatted": "\u001b[31m[cve-2023-46805]\u001b[0m \u001b[33m[critical]\u001b[0m ...",
  "offset": 142
}
```

### 2. 1000-Line Circular Replay Buffer

Network fluctuations or tab reloads should never cause an analyst to miss critical log output:
- **In-Memory Ring-Buffer**: Each running scan maintains a `collections.deque(maxlen=1000)` buffer in memory.
- **Replay Handshake on Connect**: When a new SSE connection or WebSocket client attaches, the streaming hub immediately replays the entire ring-buffer in sequence before attaching the client to live broadcast frames.
- **Automatic Garbage Collection**: When a scan transitions to a terminal state (`completed`, `failed`, `partial`), the in-memory stream buffer is flushed to disk and memory structures are deallocated after a 5-minute client retention window.

### 3. ANSI Escape Formatting & Terminal UX
- **Safe ANSI Normalization**: Scans produce colored ANSI escape sequences (`\x1b[32m` green for open ports, `\x1b[31m` red for critical vulnerabilities). XenoraSec strips dangerous control codes (such as terminal reset or cursor repositions) while rendering safe CSS color classes.
- **Smart Auto-Scroll Lock**: The terminal console automatically locks to the bottom while streaming. If the user scrolls up to inspect an earlier line, auto-scroll pauses automatically and displays a "Scroll to bottom" badge.
- **Real-Time Subprocess Demuxing**: Output lines are tagged by engine source (`[nmap]` vs `[nuclei]`), allowing engineers to filter the terminal view to inspect specific scanner output on the fly.

---

## 📑 Multi-Format Security Report Generation

Security assessments must be communicated across varied stakeholders — from C-level executives needing strategic exposure metrics to DevSecOps engineers requiring verbatim reproduction payloads. XenoraSec incorporates a dedicated, multi-format export engine (`app/services/report_generator.py`) capable of generating audit-ready deliverables in five standardized formats.

```mermaid
flowchart TD
    SCAN_DATA["Normalized Scan Record\n(Ports, CVEs, Risk Score, LLM Brief)"] --> REP_DISPATCH{"Report Formatter"}
    
    REP_DISPATCH -->|format=pdf| PDF["ReportLab PDF Engine\n(Vector Palette, Cover Page, Page Numbers)"]
    REP_DISPATCH -->|format=html| HTML["Standalone HTML5 Engine\n(Embedded CSS, @media print, Dark Theme)"]
    REP_DISPATCH -->|format=markdown| MD["GitHub-Flavored Markdown\n(Tables, Badges, Task Lists)"]
    REP_DISPATCH -->|format=json| JSON["Machine-Readable JSON\n(Strict Pydantic Schema / SIEM Integration)"]
    REP_DISPATCH -->|format=csv| CSV["Tabular CSV Flattener\n(Spreadsheet Triage & Jira Import)"]

    PDF --> OUT["FastAPI Response Stream\nContent-Disposition: attachment"]
    HTML --> OUT
    MD --> OUT
    JSON --> OUT
    CSV --> OUT
```

### 1. Supported Document Formats

| Format | Content-Type | Styling & Architecture | Target Audience |
| :--- | :--- | :--- | :--- |
| **PDF** | `application/pdf` | Built with **ReportLab**; incorporates vector corporate cover, severity color keys, header/footer page counts, and page-break guards (`KeepTogether`) | External clients, compliance auditors, board presentations |
| **HTML** | `text/html` | Standalone zero-dependency HTML document with embedded tactical CSS, interactive collapsible findings, and print-to-PDF styles (`@media print`) | Browser distribution, internal corporate wikis, offline reading |
| **Markdown**| `text/markdown` | GitHub-Flavored Markdown (GFM) formatted with UTF-8 status chips, code fences, and collapsible `<details>` blocks | Engineering tickets (GitHub Issues, GitLab MRs, Jira task descriptions) |
| **JSON** | `application/json` | Pure serialized Pydantic output containing raw scanner payloads, timestamps, CVSS metadata, and AI synthesis | Automated CI/CD quality gates, Splunk, Elastic SIEM, SOAR pipelines |
| **CSV** | `text/csv` | Flat tabular schema mapping each discovered port and vulnerability to a distinct row with CVSS, severity, and host identifiers | Risk spreadsheets, bulk vulnerability tracking, SOC spreadsheets |

### 2. Report Modes: Technical vs. Executive

XenoraSec provides two distinct rendering perspectives for each format:

#### 🛠️ Technical Mode (`report_type=technical`)
- **Full Spectrum Visibility**: Every discovered open port, service banner, protocol handshake, and template vulnerability is itemized.
- **Remediation Payloads**: Includes matched URI endpoints, curl reproduction commands, CVE / CWE references, and EPSS likelihood scores where available.
- **Raw Subprocess Artifacts**: Appends execution logs, runtime timing metrics, and Nmap command parameters.

#### 👔 Executive Mode (`report_type=executive`)
- **Strategic Exposure Score**: Prominently features the Michaelis-Menten risk gauge ($0.0 - 10.0$) with executive plain-English interpretation (`Low`, `Medium`, `Elevated`, `Critical`).
- **Severity Breakdown Matrix**: Visual table outlining aggregate critical, high, medium, and low findings.
- **Top 5 Priority Action Items**: Summarizes highest-impact remediation milestones to eliminate 80% of identified risk surface.
- **Sanitized Complexity**: Hides lengthy raw packet dumps, technical regexes, and template strings to maintain clarity for management review.

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

XenoraSec provides a clean, fully documented OpenAPI (Swagger) interface accessible at `/docs` and ReDoc at `/redoc`.

### Core Endpoints

| Method | Endpoint | Parameters & Body Schema | Description | Status Codes |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/api/scan/` | JSON: `{target, scan_profile?, port_range?, custom_tags?, timing_template?}` | Initiate an individual security scan | `200 OK`, `400 Bad Request`, `422 Unprocessable`, `429 Too Many Requests`, `503 Service Unavailable` |
| `POST` | `/api/scan/batch` | JSON: `{raw_targets, scan_profile?, batch_name?}` | Ingest and queue batch audit across host lists or CIDR blocks | `200 OK`, `400 Bad Request`, `422 Unprocessable`, `429 Too Many Requests`, `503 Service Unavailable` |
| `GET` | `/api/scan/batch/{batch_id}` | Path: `batch_id` (UUID) | Poll live batch progress counters, per-scan status, and aggregate mean risk score | `200 OK`, `404 Not Found` |
| `GET` | `/api/scan/results/{scan_id}` | Path: `scan_id` (UUID) | Fetch full findings dossier: open ports, CVEs, CVSS scores, risk metrics | `200 OK`, `400 Bad Request`, `404 Not Found` |
| `GET` | `/api/scan/{scan_id}/stream` | Path: `scan_id` (UUID) | Real-time Server-Sent Events (SSE) stream (`text/event-stream`) of scanner output | `200 OK`, `404 Not Found` |
| `WS` | `/api/scan/{scan_id}/ws` | Path: `scan_id` (UUID) | Interactive bi-directional WebSocket console for real-time terminal output | `101 Switching Protocols`, `404 Not Found` |
| `GET` | `/api/scan/{scan_id}/report` | Query: `format` (`pdf`\|`html`\|`markdown`\|`json`\|`csv`), `report_type` (`technical`\|`executive`) | Compile and download audit security report with disposition attachment | `200 OK`, `400 Bad Request`, `404 Not Found` |
| `GET` | `/api/scan/history` | Query: `limit=50`, `offset=0`, `status?`, `batch_id?` | Paginated historical scan ledger with filtering capabilities | `200 OK`, `400 Bad Request` |
| `POST` | `/api/scan/{scan_id}/retry` | Path: `scan_id` (UUID) | Re-queue a failed, partial, or timed-out scan with original options | `200 OK`, `400 Bad Request`, `404 Not Found`, `503 Service Unavailable` |
| `POST` | `/api/scan/{scan_id}/cancel` | Path: `scan_id` (UUID) | Send immediate SIGKILL termination to active subprocess workers | `200 OK`, `400 Bad Request`, `404 Not Found` |
| `DELETE`| `/api/scan/{scan_id}` | Path: `scan_id` (UUID) | Permanently purge a scan record and its associated finding cache | `200 OK`, `400 Bad Request`, `404 Not Found` |
| `GET` | `/api/scan/profiles` | None | Retrieve pre-configured scan profiles (Quick, Full Web, Network Discovery) | `200 OK` |
| `GET` | `/api/scan/templates` | None | List available Nuclei v3 template categories, severity tags, and count | `200 OK` |
| `GET` | `/api/scan/queue` | None | Query current concurrency slot occupancy and pending scan queue size | `200 OK` |
| `POST` | `/api/scan/cleanup` | JSON: `{secret, days_older_than}` | Administrative maintenance route to purge scan records older than N days | `200 OK`, `403 Forbidden`, `503 Unavailable` |
| `GET` | `/api/assets` | Query: `limit=50`, `offset=0`, `criticality?`, `status?`, `search?` | Query ASM asset inventory registry with multi-column filtering | `200 OK` |
| `GET` | `/api/assets/stats` | None | Retrieve high-level attack surface posture metrics, KPI counts, severity breakdown | `200 OK` |
| `GET` | `/api/assets/{id}` | Path: `id` (Integer) | Inspect specific asset entity with linked open ports and confirmed CVE findings | `200 OK`, `404 Not Found` |
| `PATCH` | `/api/assets/{id}` | Path: `id`, JSON: `{criticality?, status?, notes?, tags?}` | Update asset business criticality rating, operational status, or custom tags | `200 OK`, `400 Bad Request`, `404 Not Found` |
| `DELETE`| `/api/assets/{id}` | Path: `id` (Integer) | Delete asset entity with cascading removal of linked ports and vulnerabilities | `200 OK`, `404 Not Found` |
| `POST` | `/api/assets/{id}/scan` | Path: `id` (Integer) | Launch automated re-scan against registered asset inheriting default profile | `200 OK`, `404 Not Found`, `503 Service Unavailable` |
| `POST` | `/api/recon/` | JSON: `{domain, include_subdomains, resolve_subdomains, include_dns, include_tech_stack}` | Initiate asynchronous passive OSINT reconnaissance audit | `200 OK`, `400 Bad Request`, `500 Server Error` |
| `GET` | `/api/recon/{domain}` | Path: `domain` (FQDN string) | Retrieve most recent cached or completed OSINT assessment dossier for domain | `200 OK`, `404 Not Found` |
| `GET` | `/api/recon/history` | Query: `limit=20`, `offset=0` | Paginated OSINT audit history records with discovery source breakdown | `200 OK` |
| `POST` | `/api/recon/{domain}/import-to-assets` | Path: `domain`, JSON: `{subdomains[], criticality?, tags?}` | Bulk-import discovered OSINT subdomains directly into Asset Inventory | `200 OK`, `400 Bad Request`, `404 Not Found` |
| `GET` | `/health` | None | Application liveness probe and database connection health verification | `200 OK`, `503 Service Unavailable` |

#### Standard API Error Envelope Format
All error responses emitted by the platform conform to the standard RFC 7807 problem details specification:
```json
{
  "detail": "Target '192.168.1.1' resolves to private IP address (192.168.1.1), which is prohibited by server policy (ALLOW_PRIVATE_IP_SCANNING=False)."
}
```

## 💻 cURL Command Cookbook

A comprehensive collection of copy-pasteable cURL commands and real-world JSON response payloads covering every endpoint in the XenoraSec API.

#### 1. Launch a New Scan (Standard or Custom Profile)
```bash
# Standard default scan against target
curl -X POST "http://localhost:8000/api/scan/" \
     -H "Content-Type: application/json" \
     -d '{
       "target": "example.com",
       "scan_profile": "custom",
       "port_range": "80,443,8080,8443",
       "custom_tags": "cve,misconfig,takeover",
       "timing_template": "T4"
     }'
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

#### 2. Query Scan Results & Complete Risk Intelligence
```bash
curl -s "http://localhost:8000/api/scan/results/9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d"
```
**Response (`200 OK`):**
```json
{
  "scan_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "target": "example.com",
  "status": "completed",
  "risk_score": 6.84,
  "duration": 42.18,
  "created_at": "2026-09-28T13:40:00Z",
  "open_ports": [
    {"port": 80, "protocol": "tcp", "service": "http", "product": "nginx", "version": "1.24.0"},
    {"port": 443, "protocol": "tcp", "service": "ssl/http", "product": "nginx", "version": "1.24.0"}
  ],
  "vulnerabilities": [
    {
      "template_id": "cve-2023-46805",
      "name": "Ivanti Connect Secure Auth Bypass",
      "severity": "critical",
      "cvss_score": 9.8,
      "cwe_id": "CWE-287",
      "matched_at": "https://example.com/api/v1/totp/user-backup-code",
      "curl_command": "curl -X POST https://example.com/api/v1/totp/user-backup-code"
    }
  ],
  "ai_analysis": {
    "model": "llama-3.3-70b-versatile",
    "summary": "Critical authentication bypass detected on public gateway; immediate patching recommended.",
    "attack_paths": ["Public URI /api/v1/totp -> Remote Pre-Auth Access"]
  }
}
```

#### 3. Real-Time Terminal Streaming (SSE & WebSocket)
```bash
# Server-Sent Events (SSE) live stream
curl -N "http://localhost:8000/api/scan/9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d/stream"

# Interactive WebSocket console stream
wscat -c "ws://localhost:8000/api/scan/9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d/ws"
```
**SSE Stream Chunk Sample:**
```text
data: {"source":"nmap","line":"Discovered open port 443/tcp on 93.184.216.34","level":"info"}

data: {"source":"nuclei","line":"[cve-2023-46805] [critical] https://example.com/api/v1/totp/user-backup-code","level":"warning"}
```

#### 4. Cancel a Running Scan
```bash
curl -X POST "http://localhost:8000/api/scan/9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d/cancel"
```
**Response (`200 OK`):**
```json
{
  "scan_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "status": "cancelled",
  "message": "Scan cancelled by user request"
}
```

#### 5. Retry a Failed or Partial Scan
```bash
curl -X POST "http://localhost:8000/api/scan/9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d/retry"
```
**Response (`200 OK`):**
```json
{
  "scan_id": "3f81e2b1-910a-4c22-b5e1-89d123456789",
  "parent_scan_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "status": "running",
  "message": "Scan re-queued successfully"
}
```

#### 6. Multi-Target & CIDR Batch Operations
```bash
# Ingest CIDR block and extra hosts into batch queue
curl -X POST "http://localhost:8000/api/scan/batch" \
     -H "Content-Type: application/json" \
     -d '{
       "raw_targets": "192.168.1.0/29\napi.example.com",
       "scan_profile": "quick",
       "batch_name": "Perimeter Audit Q3"
     }'
```
**Response (`200 OK`):**
```json
{
  "batch_id": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
  "total_targets": 7,
  "message": "Batch scan registered with 7 targets",
  "targets": ["192.168.1.1", "192.168.1.2", "192.168.1.3", "192.168.1.4", "192.168.1.5", "192.168.1.6", "api.example.com"]
}
```

```bash
# Poll batch progress and aggregate mean risk score
curl -s "http://localhost:8000/api/scan/batch/a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d"
```
**Response (`200 OK`):**
```json
{
  "batch_id": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
  "batch_name": "Perimeter Audit Q3",
  "status": "running",
  "total": 7,
  "completed": 5,
  "running": 2,
  "failed": 0,
  "pending": 0,
  "mean_risk_score": 3.82
}
```

#### 7. Generate & Download Multi-Format Reports
```bash
# Download publication PDF
curl -O -J "http://localhost:8000/api/scan/{scan_id}/report?format=pdf&report_type=technical"

# Download standalone interactive HTML
curl -O -J "http://localhost:8000/api/scan/{scan_id}/report?format=html&report_type=technical"

# Download GitHub Markdown summary
curl -O -J "http://localhost:8000/api/scan/{scan_id}/report?format=markdown&report_type=executive"

# Export flat CSV findings
curl -O -J "http://localhost:8000/api/scan/{scan_id}/report?format=csv&report_type=technical"
```

#### 8. Asset Inventory Management (ASM)
```bash
# Query paginated inventory with filters
curl -s "http://localhost:8000/api/assets?criticality=high&status=active&limit=10"

# Query attack surface posture KPI metrics
curl -s "http://localhost:8000/api/assets/stats"

# Inspect specific asset with linked ports and active CVEs
curl -s "http://localhost:8000/api/assets/42"

# Update asset criticality rating and notes
curl -X PATCH "http://localhost:8000/api/assets/42" \
     -H "Content-Type: application/json" \
     -d '{"criticality": "critical", "notes": "Production API Ingress Gateway"}'

# Trigger an immediate automated re-scan of an asset
curl -X POST "http://localhost:8000/api/assets/42/scan"
```

#### 9. Passive Reconnaissance & OSINT API
```bash
# Launch passive OSINT discovery on domain
curl -X POST "http://localhost:8000/api/recon/" \
     -H "Content-Type: application/json" \
     -d '{
       "domain": "example.com",
       "include_subdomains": true,
       "resolve_subdomains": true,
       "include_dns": true,
       "include_tech_stack": true
     }'

# Retrieve cached OSINT assessment dossier for domain
curl -s "http://localhost:8000/api/recon/example.com"

# Query historical OSINT audits
curl -s "http://localhost:8000/api/recon/history?limit=10"

# Bulk import discovered subdomains directly into Asset Inventory
curl -X POST "http://localhost:8000/api/recon/example.com/import-to-assets" \
     -H "Content-Type: application/json" \
     -d '{
       "subdomains": ["api.example.com", "auth.example.com", "vpn.example.com"],
       "criticality": "high",
       "tags": ["recon-import", "perimeter"]
     }'
```

#### 10. Concurrency Queue & Liveness Probe
```bash
# Query current concurrency slot usage
curl -s "http://localhost:8000/api/scan/queue"
# Response: {"active_scans": 2, "max_concurrent_scans": 3, "pending_queue": 1}

# Liveness probe
curl -s "http://localhost:8000/health"
# Response: {"status": "ok", "database": "connected", "scanner_ready": true}
```

---

## ⚙️ Environment Configuration

All backend operational settings in XenoraSec can be configured via environment variables or declared inside a `.env` file in the project root. The application validates configurations at boot time using **Pydantic Settings**.

### 1. Categorized Configuration Reference

#### 🖥️ Server & Network Ingress
| Variable | Type | Default | Validation & Permitted Values | Production Recommendation | Security Implication |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`APP_NAME`** | `string` | `"XenoraSec"` | Any non-empty string | `"XenoraSec Enterprise"` | Affects report headers and API schemas |
| **`DEBUG`** | `boolean` | `false` | `true`, `false`, `1`, `0` | `false` | When true, enables verbose stack traces in HTTP responses |
| **`ALLOWED_ORIGINS`** | `string` | `http://localhost:5173,...` | Comma-separated URI strings | Strict production FQDN | Restricts cross-origin browser requests |
| **`TRUST_PROXY_HEADERS`**| `boolean`| `false` | `true`, `false` | `true` (when behind Nginx/Cloudflare) | Protects against `X-Forwarded-For` spoofing |
| **`TRUSTED_PROXIES`** | `string` | `"127.0.0.1"` | Comma-separated IP addresses | Direct upstream proxy IPs | Restricts which remote sockets can supply client IPs |

#### 🗄️ Persistence & Database Layer
| Variable | Type | Default | Validation & Permitted Values | Production Recommendation | Security Implication |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`DATABASE_URL`** | `string` | `sqlite+aiosqlite:///./scans.db` | Valid SQLAlchemy async URI | PostgreSQL with asyncpg | Dictates storage backend & concurrency scale |
| **`DB_POOL_SIZE`** | `integer`| `5` | Integer $\ge 1$ | `10` to `20` (Postgres) | Manages database connection pool ceiling |
| **`DB_MAX_OVERFLOW`** | `integer`| `10` | Integer $\ge 0$ | `20` | Maximum surge connections permitted |

#### ⚙️ Scanner Timing & Resource Throttling
| Variable | Type | Default | Validation & Permitted Values | Production Recommendation | Security Implication |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`MAX_CONCURRENT_SCANS`** | `integer`| `3` | `1` to `32` | `3` to `8` (based on CPU/RAM) | Prevents host exhaustion from simultaneous scans |
| **`GLOBAL_SCAN_TIMEOUT`** | `integer`| `600` | Seconds ($60 \le t \le 3600$) | `600` (10 minutes) | Hard ceiling killing hung subprocesses |
| **`NMAP_TIMEOUT`** | `integer`| `180` | Seconds ($30 \le t \le 1800$) | `180` (3 minutes) | Maximum runtime allocated to Nmap phase |
| **`NMAP_TIMING`** | `string` | `"T4"` | `"T0"`, `"T1"`, `"T2"`, `"T3"`, `"T4"`, `"T5"` | `"T4"` | Balances packet pacing vs detection avoidance |
| **`NUCLEI_TIMEOUT`** | `integer`| `300` | Seconds ($60 \le t \le 2400$) | `300` (5 minutes) | Maximum runtime allocated to Nuclei phase |
| **`NUCLEI_RATE_LIMIT`** | `integer`| `50` | Requests/sec ($1 \le rl \le 500$) | `50` to `100` | Limits HTTP request burst rate against targets |
| **`MAX_VULNERABILITIES`**| `integer`| `1000` | Integer ($50 \le v \le 10000$) | `1000` | Safety circuit breaker against honeypot DoS |

#### 🛡️ Network Security & Perimeter Policy
| Variable | Type | Default | Validation & Permitted Values | Production Recommendation | Security Implication |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`ALLOW_LOCALHOST_SCANNING`**| `boolean`| `false` | `true`, `false` | `false` | **CRITICAL**: Set true only in isolated local dev |
| **`ALLOW_PRIVATE_IP_SCANNING`**| `boolean`| `false` | `true`, `false` | `false` | **CRITICAL**: Controls RFC 1918 internal scanning |
| **`MAX_CIDR_PREFIX`** | `integer`| `24` | Prefix mask ($24 \le p \le 32$) | `24` | Prevents denial of service from wide subnets |
| **`MAX_BATCH_TARGETS`**| `integer`| `256` | Integer ($1 \le m \le 1024$) | `256` | Limits maximum hosts submitted in one batch |
| **`BATCH_CONCURRENCY`**| `integer`| `3` | Worker slots ($1 \le c \le 16$) | `3` to `5` | Regulates parallel sub-scans in a batch |

#### 🚦 Rate Limiting & Access Security
| Variable | Type | Default | Validation & Permitted Values | Production Recommendation | Security Implication |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`RATE_LIMIT_ENABLED`**| `boolean`| `true` | `true`, `false` | `true` | Safeguards API from automated volumetric abuse |
| **`RATE_LIMIT_PER_MINUTE`**| `integer`| `10` | Requests/min ($1 \le r \le 1000$) | `30` to `60` | Per-client IP sliding window allowance |
| **`RATE_LIMIT_PER_HOUR`**| `integer`| `100` | Requests/hour ($10 \le r \le 50000$) | `300` | Hourly burst allowance |
| **`CLEANUP_SECRET`** | `string` | `null` | String $\ge 16$ characters | Strong random token | Required in header to invoke `/api/scan/cleanup` |

#### 🧠 AI Risk Intelligence
| Variable | Type | Default | Validation & Permitted Values | Production Recommendation | Security Implication |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`GROQ_API_KEY`** | `string` | `null` | `gsk_...` Groq API key | Provide for LLM analysis | Securely stored; never echoed in API output |
| **`GROQ_MODEL`** | `string` | `"llama-3.3-70b-versatile"` | Supported Groq model string | `"llama-3.3-70b-versatile"` | Selects LLM model weights for threat inference |

---

### 2. Hardened Production Configuration Example (`.env.production`)

```env
# Core Production Settings
APP_NAME="XenoraSec Enterprise"
DEBUG=False
ALLOWED_ORIGINS="https://scanner.internal.company.com"

# Reverse Proxy Trust (Required behind Nginx / Cloudflare)
TRUST_PROXY_HEADERS=True
TRUSTED_PROXIES="127.0.0.1,172.20.0.0/16"

# Database Concurrency (PostgreSQL asyncpg recommended for multi-node)
DATABASE_URL="sqlite+aiosqlite:////data/scans.db"

# Perimeter Safety Guards
ALLOW_LOCALHOST_SCANNING=False
ALLOW_PRIVATE_IP_SCANNING=False
MAX_CIDR_PREFIX=24
MAX_BATCH_TARGETS=256
BATCH_CONCURRENCY=3

# Subprocess Performance & Timeouts
MAX_CONCURRENT_SCANS=4
GLOBAL_SCAN_TIMEOUT=600
NMAP_TIMEOUT=180
NMAP_TIMING="T4"
NUCLEI_TIMEOUT=300
NUCLEI_RATE_LIMIT=75
MAX_VULNERABILITIES=1000

# Rate Limiting & Admin Maintenance
RATE_LIMIT_ENABLED=True
RATE_LIMIT_PER_MINUTE=30
RATE_LIMIT_PER_HOUR=300
CLEANUP_SECRET="e9a7c3b2f1d84e5a9c0b1a2e3f4d5c6b7a8"

# AI Inference (Optional)
GROQ_API_KEY="gsk_prod_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
GROQ_MODEL="llama-3.3-70b-versatile"
```

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

### System Prerequisites & Scanner Toolchain
Ensure the underlying security scanning binaries (`nmap` and `nuclei`) are installed on your host system:

#### 1. Ubuntu / Debian / Kali Linux
```bash
sudo apt-get update && sudo apt-get install -y nmap wget unzip python3-venv python3-pip nodejs npm

# Install precompiled Nuclei v3.3.8 binary
wget https://github.com/projectdiscovery/nuclei/releases/download/v3.3.8/nuclei_3.3.8_linux_amd64.zip
unzip nuclei_3.3.8_linux_amd64.zip
sudo mv nuclei /usr/local/bin/
rm nuclei_3.3.8_linux_amd64.zip

# Initialize official community vulnerability templates
nuclei -update-templates
```

#### 2. Fedora / RHEL / Rocky Linux
```bash
sudo dnf install -y nmap wget unzip python3 python3-pip nodejs

# Install Nuclei
wget https://github.com/projectdiscovery/nuclei/releases/download/v3.3.8/nuclei_3.3.8_linux_amd64.zip
unzip nuclei_3.3.8_linux_amd64.zip
sudo mv nuclei /usr/local/bin/
rm nuclei_3.3.8_linux_amd64.zip
nuclei -update-templates
```

#### 3. Arch Linux / Manjaro
```bash
sudo pacman -Syu nmap nuclei python nodejs npm
nuclei -update-templates
```

#### 4. macOS (Apple Silicon & Intel via Homebrew)
```bash
# Install toolchain via Homebrew
brew update
brew install nmap nuclei python@3.12 node

# Sync community templates
nuclei -update-templates
```

#### 5. Windows 11 / 10 (WSL2 Ubuntu Recommended)
Native Windows execution of low-level security tools often faces socket capability hurdles. We strongly recommend running inside **Windows Subsystem for Linux 2 (WSL2)**:
```powershell
# In Windows PowerShell (Administrator):
wsl --install -d Ubuntu-24.04
```
Inside the WSL2 Ubuntu shell, follow the **Ubuntu / Debian** instructions above. Ensure `.wslconfig` in your Windows user directory includes:
```ini
[wsl2]
networkingMode=mirrored
dnsTunneling=true
```
This enables seamless localhost port mirroring between Windows browsers and the FastAPI backend (`http://localhost:8000`).

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

#### Architecture Highlights & Nginx Directives:
- **Zero-Configuration Reverse Proxy**: Nginx automatically proxies API calls, eliminating CORS preflight overhead and cross-origin security friction in production environments.
- **WebSocket & SSE Telemetry Upgrades**: Explicitly configured for low-latency streaming without proxy buffer clipping:
  ```nginx
  # Dedicated SSE streaming configuration (disables proxy buffering)
  location ~ ^/api/scan/([a-f0-9\-]+)/stream$ {
      proxy_pass http://backend:8000;
      proxy_http_version 1.1;
      proxy_set_header Connection "";
      proxy_buffering off;
      proxy_cache off;
      chunked_transfer_encoding on;
      proxy_read_timeout 600s;
  }

  # Dedicated WebSocket upgrade configuration
  location ~ ^/api/scan/([a-f0-9\-]+)/ws$ {
      proxy_pass http://backend:8000;
      proxy_http_version 1.1;
      proxy_set_header Upgrade $http_upgrade;
      proxy_set_header Connection "upgrade";
      proxy_read_timeout 3600s;
  }
  ```
- **Static Asset Caching & SPA Routing**: Compiled JavaScript and CSS bundles are served with `Cache-Control "public, max-age=31536000, immutable"`, while `index.html` uses `try_files $uri $uri/ /index.html` with `no-cache` to ensure instant client updates.
- **Persistent SQLite WAL Volume**: Database data is stored in the Docker volume `scans_data` mounted at `/data/scans.db`, ensuring scan records survive container restarts and updates without corruption.
- **Automated Container Health Probes**:
  ```yaml
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
    interval: 30s
    timeout: 5s
    retries: 3
    start_period: 10s
  ```
- **Development Overrides**: Copy `docker-compose.override.yml.example` to `docker-compose.override.yml` to mount local directories for live reloading during development:
  ```bash
  cp docker-compose.override.yml.example docker-compose.override.yml
  docker compose up
  ```

---

## 🛡️ Container Hardening & Non-Root Security

Security tools that audit infrastructure must themselves adhere to the highest standard of defense-in-depth. XenoraSec enforces rigorous container hardening to eliminate privilege escalation risks:

```mermaid
flowchart TD
    subgraph ContainerBoundary ["Hardened Container Sandbox (UID 10001)"]
        APP["FastAPI Application"]
        NMAP_BIN["Nmap Binary (-sT unprivileged)"]
        NUC_BIN["Nuclei Binary (v3.3.8)"]
    end

    subgraph SecurityControls ["Defensive Guardrails"]
        USER["Unprivileged User: xenora (UID 10001)"]
        CAPS["Linux Capabilities: cap_drop: ALL"]
        ROOTFS["Read-Only Root Filesystem (read_only: true)"]
        TMPFS["Scoped tmpfs: /tmp (noexec, nosuid, 64MB)"]
        VOL["Persistent Volume /data (chmod 770, chown 10001:10001)"]
    end

    USER --> ContainerBoundary
    CAPS --> ContainerBoundary
    ROOTFS --> ContainerBoundary
    TMPFS --> ContainerBoundary
    VOL --> ContainerBoundary
```

### 1. Dedicated Unprivileged Execution (`UID 10001`)
- **No Root User**: Both the backend Dockerfile and Render container create and execute as a dedicated unprivileged system user:
  ```dockerfile
  RUN groupadd -g 10001 xenora && \
      useradd -u 10001 -g xenora -s /bin/bash -m xenora
  USER xenora:xenora
  ```
- **Exploit Containment**: If a zero-day vulnerability in Nmap, Nuclei, or an upstream Python library were triggered, the attacker is trapped inside an unprivileged user context without access to `/etc`, host sockets, or host devices.

### 2. Capability Dropping (`cap_drop: ALL`)
- **Zero Raw Sockets**: Traditional vulnerability scanners require `CAP_NET_RAW` to forge SYN packets. XenoraSec's architecture uses `-sT` (TCP Connect), allowing **all Linux capabilities to be completely dropped**:
  ```yaml
  security_opt:
    - no-new-privileges:true
  cap_drop:
    - ALL
  ```

### 3. Read-Only Root Filesystem & Tmpfs Mounts
- In production, containers can run with an immutable root filesystem (`read_only: true`).
- Ephemeral writes for scanner scratch files are strictly restricted to locked-down memory `tmpfs` mounts:
  ```yaml
  read_only: true
  tmpfs:
    - /tmp:rw,noexec,nosuid,size=64M
    - /run:rw,noexec,nosuid,size=16M
  ```

### 4. Volume Permissions & SQLite Storage Isolation
- The persistent database volume is mounted at `/data` with ownership pre-assigned to `10001:10001`.
- SQLite WAL and SHM shared memory files are isolated inside `/data/scans.db*`, preventing write access to application source directories (`/app`).

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

## 🎨 Tactical Dark UI Design System

XenoraSec's frontend is crafted using an intentional **Tactical Cyber-Defense Design System**, engineered for high situational awareness during lengthy penetration testing engagements and SOC monitoring shifts.

### 1. Design Tokens & Palette Specifications

| Token Name | HEX Code | CSS Variable | Semantic Usage |
| :--- | :--- | :--- | :--- |
| **Canvas Background** | `#090d16` | `--color-canvas` | Deep background canvas preventing eye strain in dark environments |
| **Card Surface** | `#0e1526` | `--color-surface` | Primary container surface for scan cards, panels, and modal shells |
| **Elevated Surface** | `#141e34` | `--color-surface-elevated` | Dropdown menus, tooltips, and interactive drawer overlays |
| **Subtle Border** | `#1e2c47` | `--color-border-subtle` | Structural dividing lines and non-active input borders |
| **Highlight Border**| `#2e446d` | `--color-border-highlight` | Hover states, active tabs, and focus-ring indicator lines |
| **Cyber Cyan Accent**| `#00f0ff` | `--color-accent-cyan` | Active scan indicators, primary buttons, and link hovers |
| **Electric Violet** | `#8b5cf6` | `--color-accent-violet` | AI / Groq LLM intelligence badges and badge borders |

#### Severity Token Color Matrix
Finding badges, progress indicators, and CVSS indicators use standardized color scales:

```text
CRITICAL : #ef4444 (Red-500)     │ Background: rgba(239, 68, 68, 0.12)  │ Border: #dc2626
HIGH     : #f97316 (Orange-500)  │ Background: rgba(249, 115, 22, 0.12) │ Border: #ea580c
MEDIUM   : #eab308 (Yellow-500)  │ Background: rgba(234, 179, 8, 0.12)  │ Border: #ca8a04
LOW      : #3b82f6 (Blue-500)    │ Background: rgba(59, 130, 246, 0.12) │ Border: #2563eb
INFO     : #64748b (Slate-500)   │ Background: rgba(100, 116, 139, 0.12)│ Border: #475569
```

### 2. Typography Hierarchy

- **Telemetry & Monospace**: `JetBrains Mono`, `Fira Code`, monospace. Applied to targets, IP addresses, CIDR masks, port numbers, CVE signatures, and live terminal stream lines with tabular figures (`font-variant-numeric: tabular-nums`).
- **Interface & Display**: `Inter`, system-ui, -apple-system, sans-serif. Applied to executive summaries, section headings, and operational controls.
- **Font Scale**: Standardized from `text-xs` (0.75rem / 12px) for timestamp telemetry to `text-2xl` (1.5rem / 24px) for dashboard KPI counters.

### 3. Core Component Architecture

- **`ScanPanel`**: Target input bar featuring reactive format detection (IP/Domain/URL/CIDR), one-click test target presets, custom port range inputs, and Nmap timing radio buttons.
- **`LiveTerminal`**: Hardware-accelerated terminal output box with ANSI escape sequence parsing, auto-scroll toggle, source filter chips (`All`, `Nmap`, `Nuclei`), and fullscreen popout modal.
- **`FindingCard`**: Collapsible vulnerability card featuring CVSS rating pill, CWE badges, template identifier, matched URL path, reproduction curl command snippet, and NVD external references.
- **`AssetTable`**: High-density ASM table with multi-criteria search, criticality badge selectors, status pills, and slide-out asset detail drawer.
- **`MetricCard`**: High-contrast KPI tile presenting real-time risk scores, active scan counts, and circular SVG saturation meters.

### 4. Accessibility & Responsive Breakpoints
- **WCAG 2.1 AA Contrast**: All body text and severity badges maintain at least a $4.5:1$ contrast ratio against the `#0e1526` surface background.
- **Fluid Layout**: Uses Tailwind CSS breakpoints (`sm: 640px`, `md: 768px`, `lg: 1024px`, `xl: 1280px`). On mobile displays, the sidebar collapses into a gesture-friendly sliding drawer with backdrop blur.

---

## 🧪 Testing & Quality Assurance

XenoraSec enforces a zero-regression policy across backend security guards, mathematical risk formulas, and frontend user workflows through a multi-tier testing pipeline:

```mermaid
flowchart TD
    subgraph TestingPyramid ["Testing Pyramid"]
        E2E["Playwright E2E Browser Tests\n(Live UI, Drawer, Terminal SSE, Downloads)"]
        INTEG["Integration Tests (Pytest + AsyncClient)\n(REST API, Batch Queues, DB Concurrency)"]
        UNIT["Unit Tests (Pytest & Vitest)\n(SSRF Guard, MM Formula, RFC SPF/DMARC)"]
        STATIC["Static Code Analysis\n(Ruff, MyPy, TypeScript Strict, ESLint)"]
    end

    STATIC --> UNIT --> INTEG --> E2E
```

### 1. Backend Test Suite (Pytest & Coverage)

The backend features an asynchronous test suite covering unit invariants, database concurrency, and network security filters:

```bash
# Run full test suite with verbose reporting and timing
pytest -v

# Run with test coverage analysis and missing line identification
pytest --cov=app --cov-report=term-missing --cov-report=html

# Run specific functional test categories
pytest tests/test_security.py -v       # SSRF & input gate invariants
pytest tests/test_recon.py -v          # Passive OSINT & RFC 7208/7489 tests
pytest tests/test_ai_service.py -v     # Michaelis-Menten kinetics & Groq fallback
pytest tests/test_database.py -v       # SQLite WAL concurrency & busy timeouts
pytest tests/test_batch_scan.py -v     # CIDR subnet expansion & batch slots
```

#### Test Suite Inventory & Key Invariants

| Test Module | Coverage Scope | Verified Invariants & Edge Cases |
| :--- | :--- | :--- |
| **`test_security.py`** | SSRF & Target Gate | Proves loopback (`127.0.0.1`), private RFC 1918 (`10.0.0.0/8`, `192.168.0.0/16`), link-local (`169.254.0.0/16`), and AWS metadata IP (`169.254.169.254`) rejection via real `socket.getaddrinfo` resolution |
| **`test_rate_limit.py`** | Anti-Spoofing | Verifies sliding-window counter eviction, trusted proxy header validation, and rightmost hop parsing |
| **`test_cancellation.py`**| Subprocess Safety | Asserts `process.kill()` executes on `asyncio.CancelledError` and verifies cold-start zombie recovery |
| **`test_ai_service.py`** | Risk Scoring | Proves exact half-saturation point ($S = 15.0 \implies \text{Score} = 5.0$), asymptotic limits ($S \to \infty \implies 10.0$), and Groq API 10s timeout fallback |
| **`test_database.py`** | DB Concurrency | Checks `PRAGMA journal_mode=WAL`, 30s busy timeout, and concurrent multi-session read/write without `database is locked` errors |
| **`test_recon.py`** | Passive OSINT | Verifies crt.sh wildcard stripping, Cloudflare DoH fallback on timeout, RFC 7208 SPF permerror detection, and RFC 7489 DMARC subdomain inheritance |
| **`test_batch_scan.py`** | CIDR Subnets | Validates `/24` to `/32` host math, rejection of `/16` subnets (HTTP 422), and `asyncio.Semaphore` slot distribution |
| **`test_assets.py`** | ASM Asset Registry | Proves idempotent upsert from scan, port state updates, vulnerability lifecycle tracking, and cascade deletion integrity |
| **`test_api.py`** | REST Routes | End-to-end route tests for `/health`, `/queue`, `/history`, and partial retries |

---

### 2. Frontend Strict Verification & Linting

```bash
cd frontend

# TypeScript compilation check across all components & hooks
npm run type-check

# ESLint static analysis enforcing React 19 rules
npm run lint

# Production bundle compilation & chunk optimization
npm run build
```

---

### 3. Playwright End-to-End (E2E) Browser Automation Guide

XenoraSec includes end-to-end browser test suites powered by **Playwright** (`tests/e2e/`), automating critical user journeys across desktop and mobile viewports:

#### Running Playwright Tests
```bash
# Install Playwright browser dependencies (Chromium, Firefox, WebKit)
npx playwright install --with-deps

# Run all E2E tests headlessly
npx playwright test

# Run tests in interactive UI mode with time-travel debugger
npx playwright test --ui

# Inspect visual HTML test execution report
npx playwright show-report
```

#### Automated End-to-End Test Scenarios
1. **Target Submission Journey**: Types target string, verifies dynamic format badge (`DOMAIN`), triggers scan, and asserts redirection to live progress view.
2. **CIDR Batch Management**: Selects CIDR mode, clicks `/29` quick-fill chip, verifies target preview counter shows 6 hosts, submits batch, and validates batch progress modal.
3. **Live Terminal Streaming**: Attaches to running scan SSE channel, verifies terminal console displays green port records and yellow/red vulnerability stream entries.
4. **Interactive Asset Drawer**: Navigates to `/assets`, filters by `Critical` status, clicks host row, and asserts slide-out inspection drawer displays open ports and CVE references.
5. **Multi-Format Report Export**: Clicks Export button, selects PDF / HTML / Markdown options, and verifies browser download triggers with valid file attachments.
6. **Mobile Responsive Navigation**: Emulates mobile viewport (375x812 iPhone), asserts desktop sidebar collapses into hamburger button, opens drawer, and verifies responsive table scroll.

---

## 📚 Documentation & API

- **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Architecture**: **[Architecture.md](Architecture.md)** (Design & Deployment)
- **Testing**: **[TESTING_GUIDE.md](TESTING_GUIDE.md)**
- **Changelog**: **[changelog.md](changelog.md)**

---

## ⚡ Performance Benchmarks & Tuning

XenoraSec is engineered for high throughput and predictable resource consumption, scaling from single-host edge appliances up to enterprise vulnerability management clusters.

```mermaid
flowchart LR
    subgraph Sizing ["Infrastructure Sizing"]
        EDGE["Edge / Dev Node\n(2 vCPU / 2GB RAM)\nMAX_CONCURRENT_SCANS=2"]
        PROD["Production Host\n(4 vCPU / 8GB RAM)\nMAX_CONCURRENT_SCANS=4"]
        ENT["Enterprise Cluster\n(8+ vCPU / 16GB+ RAM)\nMAX_CONCURRENT_SCANS=8+"]
    end

    subgraph Tuning ["Performance Knobs"]
        DB_WAL["SQLite WAL + synchronous=NORMAL"]
        BUF_CAP["Nuclei 1MB Ring-Buffer Cap"]
        SEM_GATING["asyncio.Semaphore Concurrency Slots"]
    end

    Sizing --> Tuning
```

### 1. Empirical Execution Benchmarks

Tested on a standard cloud compute instance (4 vCPU, 8GB RAM, NVMe storage, Ubuntu 24.04 LTS):

| Scan Scenario | Target Footprint | Scan Profile | Avg Duration | Peak Worker RAM | CPU Utilization |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Single Web Endpoint** | 1 FQDN (`example.com`) | Quick Recon (`-T4`, top 100 ports, core CVEs) | 32 seconds | 115 MB | 28% of 1 core |
| **Full Web Audit** | 1 FQDN (`example.com`) | Full Audit (all ports, all Nuclei templates) | 3 min 15 sec | 240 MB | 65% of 1 core |
| **Subnet `/29` Block** | 6 usable IP hosts | Standard Profile (`BATCH_CONCURRENCY=3`) | 2 min 45 sec | 285 MB | 55% aggregate |
| **Subnet `/28` Block** | 14 usable IP hosts | Standard Profile (`BATCH_CONCURRENCY=3`) | 5 min 50 sec | 410 MB | 68% aggregate |
| **Enterprise Batch** | 50 heterogeneous hosts | Quick Profile (`BATCH_CONCURRENCY=5`) | 16 min 20 sec | 580 MB | 82% aggregate |
| **Passive OSINT Audit**| 1 Domain (crt.sh + DoH)| Subdomains + DNS + Headers + TLS Inspection | 4.8 seconds | 45 MB | < 10% |

### 2. Hardware Resource Sizing Recommendations

| Deployment Tier | Minimum vCPU | RAM | Disk / Storage | Recommended DB | Maximum Concurrency |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Developer / Edge** | 2 vCPU | 2 GB | 10 GB SSD | SQLite WAL Mode | `MAX_CONCURRENT_SCANS=2` |
| **Team Production** | 4 vCPU | 8 GB | 50 GB NVMe | SQLite WAL Mode | `MAX_CONCURRENT_SCANS=4` |
| **Enterprise Cluster**| 8+ vCPU | 16+ GB | 100+ GB NVMe | PostgreSQL `asyncpg` | `MAX_CONCURRENT_SCANS=10+` |

### 3. SQLite High-Concurrency Tuning Invariants

When using SQLite (the default backend), XenoraSec automatically initializes the database engine with tuned PRAGMAs:
```sql
PRAGMA journal_mode = WAL;          -- Permits simultaneous readers during active writes
PRAGMA synchronous = NORMAL;        -- Eliminates redundant disk fsyncs while maintaining durability
PRAGMA busy_timeout = 30000;        -- Waits up to 30,000ms (30s) during lock contention
PRAGMA wal_autocheckpoint = 1000;   -- Checkpoints WAL log every 1000 pages (~4MB)
```

#### Periodic WAL Maintenance
For deployments running hundreds of scans monthly, trigger an atomic maintenance checkpoint to keep WAL file size compact:
```bash
sqlite3 scans.db "PRAGMA wal_checkpoint(TRUNCATE);"
```

### 4. When to Migrate to PostgreSQL
While SQLite with WAL mode easily handles thousands of scans and multi-client browser polling, upgrade to PostgreSQL when:
- Deploying multiple backend container replicas behind a load balancer.
- Ingesting continuous mass CIDR batch scans exceeding 500 targets daily.
- Integrating real-time SIEM streaming writes across distributed remote workers.

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

### 6. Cloudflare DoH / DNS Resolution Timeouts in Locked Environments
**Issue**: Passive recon fails to resolve subdomains or throws `dns.resolver.LifetimeTimeout` in enterprise cloud networks where outbound UDP/TCP port 53 is blocked by corporate firewall rules.  
**Resolution**: XenoraSec automatically falls back to **Cloudflare DNS-over-HTTPS (DoH)** via standard HTTPS port 443 (`https://cloudflare-dns.com/dns-query`). Ensure outbound egress HTTPS (port 443) is permitted in your security group. You can verify DoH connectivity manually:
```bash
curl -H "Accept: application/dns-json" "https://cloudflare-dns.com/dns-query?name=example.com&type=A"
```

---

### 7. Nuclei High Memory Usage or OOM Kills on Wildcard Targets
**Issue**: Targets returning wildcard HTTP 200 responses for every URI cause Nuclei to trigger thousands of template matches, consuming container RAM.  
**Resolution**: XenoraSec implements two protective circuit breakers:
1. `MAX_VULNERABILITIES=1000` (configurable in `.env`) automatically caps total findings ingested per scan.
2. The stdout ring-buffer automatically halves oldest buffered entries when exceeding 1MB.
For constrained edge devices (2GB RAM), reduce the concurrency and rate limits:
```env
NUCLEI_RATE_LIMIT=25
MAX_VULNERABILITIES=500
```

---

### 8. `Nmap: Operation not permitted` or Raw Socket Permission Errors
**Issue**: Running Nmap inside Docker produces raw packet socket permissions errors (`dnet: Failed to open device`).  
**Resolution**: XenoraSec strictly enforces unprivileged **TCP Connect** (`-sT`) scans by default, which relies entirely on the kernel `connect()` syscall and requires **zero special privileges or `CAP_NET_RAW` capabilities**. If you observe this error, ensure custom scan profiles do not pass raw socket flags (`-sS`, `-sU`, `-O`) without container capabilities.

---

### 9. WebSocket / SSE Terminal Disconnections Behind Reverse Proxies
**Issue**: The live terminal console disconnects after 60 seconds with `1006 Abnormal Closure` when running behind Cloudflare or AWS ALB.  
**Resolution**: Upstream reverse proxies typically terminate idle HTTP/WebSocket connections after 60 seconds. XenoraSec maintains periodic client heartbeat pings. Ensure your Nginx or ingress controller configures extended timeouts:
```nginx
proxy_read_timeout 600s;
proxy_send_timeout 600s;
```
If using Cloudflare, ensure **WebSockets** is toggled ON under **Network** settings in the Cloudflare Dashboard.

---

### 10. `crt.sh 502 Bad Gateway` or Transient Upstream Rate Limits
**Issue**: Passive subdomain enumeration occasionally logs upstream crt.sh errors.  
**Resolution**: Public Certificate Transparency endpoints experience heavy global traffic. XenoraSec's `ReconEngine` incorporates built-in exponential backoff with randomized jitter ($\Delta t = 2^n + \text{rand}(0.1, 0.8)$) and automatically pivots to secondary passive DNS sources without aborting the audit.

---

### 11. Cold-Start Zombie Process Cleanups after Unscheduled Node Reboot
**Issue**: Host machine was abruptly rebooted during an active scan, leaving records frozen in `RUNNING` status.  
**Resolution**: XenoraSec includes an automated cold-start recovery hook in `app/main.py`. During application startup, the engine queries the database for any dangling `RUNNING` scans and transitions them to `FAILED` with the audit reason:
`"Scan interrupted by system restart or process termination"`.

---

## 📁 Project Structure

```text
xenorasec/
├── app/                              # FastAPI Asynchronous Backend
│   ├── __init__.py
│   ├── main.py                       # Application factory, lifespan hooks, zombie recovery
│   ├── core/                         # Core runtime components & middlewares
│   │   ├── config.py                 # Pydantic Settings & environment validation
│   │   ├── database.py               # SQLAlchemy async engine & SQLite WAL configuration
│   │   ├── rate_limit.py             # Sliding-window IP rate limiter with proxy trust
│   │   └── security.py               # Target sanitization, SSRF guard & DNS lookup
│   ├── api/                          # REST API route handlers
│   │   ├── v1/
│   │   │   ├── scan.py               # Single & batch scan routes, stream endpoints
│   │   │   ├── recon.py              # Passive OSINT & reconnaissance endpoints
│   │   │   └── assets.py             # Attack surface management & inventory CRUD
│   ├── models/                       # SQLAlchemy ORM entity definitions
│   │   ├── scan.py                   # ScanResult, BatchScan database models
│   │   ├── asset.py                  # Asset, AssetPort, AssetVulnerability models
│   │   └── recon.py                  # ReconHistory ledger database model
│   ├── schemas/                      # Pydantic schemas for request/response serialization
│   │   ├── scan.py                   # ScanRequest, ScanResponse, ScanResultSchema
│   │   ├── asset.py                  # AssetCreate, AssetUpdate, AssetDetailSchema
│   │   └── recon.py                  # ReconRequest, ReconResultSchema, DNSRecords
│   └── services/                     # Business logic and external tool wrappers
│       ├── nmap_scanner.py           # Async Nmap wrapper with fault-tolerant XML parser
│       ├── nuclei_scanner.py         # Async Nuclei wrapper with streaming JSONL reader
│       ├── ai_service.py             # Michaelis-Menten kinetics & Groq Llama 3.3 LLM
│       ├── stream_hub.py             # SSE & WebSocket real-time terminal buffer hub
│       ├── recon_service.py          # crt.sh miner, Cloudflare DoH, RFC mail evaluator
│       ├── asset_service.py          # Idempotent delta upsert & ASM inventory sync
│       └── report_generator.py       # Multi-format security report compiler (PDF/HTML/MD/JSON)
├── frontend/                         # React 19 + TypeScript + Vite SPA
│   ├── index.html                    # Single Page Application HTML entrypoint
│   ├── package.json                  # Frontend dependencies & build scripts
│   ├── vite.config.ts                # Vite build and proxy development configuration
│   ├── tailwind.config.js            # Tactical Dark theme design tokens & colors
│   ├── nginx.conf                    # Production reverse proxy, caching & SSE/WS upgrades
│   └── src/                          # Application source code
│       ├── main.tsx                  # React DOM mount point & TanStack Query client
│       ├── App.tsx                   # Top-level routing, sidebar & drawer shell
│       ├── components/               # Tactical UI components
│       │   ├── ScanPanel.tsx         # Target input, format detection & CIDR chips
│       │   ├── LiveTerminal.tsx      # Terminal console with SSE/WS streaming & ANSI color
│       │   ├── FindingCard.tsx       # Severity badge, CVSS pill & reproduction curl
│       │   ├── AssetTable.tsx        # High-density ASM asset table & sorting
│       │   ├── AssetDetailDrawer.tsx # Slide-out service & CVE inspection drawer
│       │   ├── ReconPanel.tsx        # OSINT dispatcher, subdomain matrix & mail score
│       │   └── ReportModal.tsx       # Multi-format export dialog (PDF/HTML/MD/JSON/CSV)
│       ├── hooks/                    # Reusable custom React hooks
│       │   ├── useScanStream.ts      # SSE and WebSocket streaming client hook
│       │   └── useAssetInventory.ts  # TanStack query wrapper for ASM endpoints
│       └── types/                    # Shared TypeScript interfaces & API contracts
├── tests/                            # Test automation suite
│   ├── conftest.py                   # Async Pytest fixtures & mock subprocess runners
│   ├── test_security.py              # SSRF protection, loopback & private IP tests
│   ├── test_rate_limit.py            # Sliding-window rate limiter & proxy anti-spoofing
│   ├── test_cancellation.py         # Subprocess kill signals & zombie recovery
│   ├── test_ai_service.py            # Michaelis-Menten math & Groq fallback tests
│   ├── test_database.py              # SQLite WAL mode & concurrent connection tests
│   ├── test_recon.py                 # crt.sh parsing, DoH fallback & RFC 7208/7489 tests
│   ├── test_batch_scan.py            # CIDR subnet expansion & batch semaphore tests
│   ├── test_assets.py                # Asset delta upsert & lifecycle state tests
│   ├── test_api.py                   # REST API route integration tests
│   └── e2e/                          # Playwright end-to-end browser tests
├── docs/                             # Architecture & component documentation
│   ├── UI_ARCHITECTURE.md
│   ├── UI_COMPONENTS.md
│   └── DESIGN_TOKENS.md
├── docker-compose.yml                # Multi-container production deployment
├── docker-compose.override.yml.example # Local development live-reload overrides
├── Dockerfile                        # Multi-stage production backend container
├── Dockerfile.render                 # Render blueprint cloud container
├── render.yaml                       # Turnkey Render Blueprint specification
├── requirements.txt                  # Python dependencies
├── .env.example                      # Configuration template
└── README.md                         # Comprehensive documentation
```

---

## 🗺️ Product Roadmap

### Completed Milestones
- [x] **Asynchronous Dual-Engine Orchestration** (Nmap + Nuclei v3.3.8 streaming wrappers)
- [x] **Deterministic Michaelis-Menten Risk Scoring Model** ($V_{\max}=10.0, K_m=15.0$)
- [x] **Optional Groq Cloud LLM Integration** (Llama 3.3 70B zero-temperature inference)
- [x] **Zero-Trust SSRF & DNS Rebinding Protection** (Socket pre-resolution & RFC gating)
- [x] **SQLite WAL Mode & High-Concurrency Hardening** (30s busy timeout, non-blocking polling)
- [x] **Mobile Responsive Navigation Drawer & Real-Time Input Badges**
- [x] **Automated PDF / HTML / Markdown / JSON Security Report Generation**
- [x] **Production Containerization (Docker Compose & Nginx Reverse Proxy)**
- [x] **GitHub Actions CI/CD Multi-Version Matrix Testing** (Python 3.11, 3.12, Node 20)
- [x] **Multi-Target CIDR Subnet Scanning & Batch Execution** (/24 to /32 boundaries)
- [x] **Asset Inventory & Attack Surface Management (ASM)** (Idempotent delta upsert)
- [x] **Passive Reconnaissance & OSINT Engine** (crt.sh CT mining, DoH, RFC 7208/7489)

### Version 2.2 (Upcoming Q4 2026)
- [ ] **Webhook Event Dispatcher**: Real-time webhook notifications (Slack, Discord, Microsoft Teams, Splunk) with HMAC-SHA256 signature verification headers.
- [ ] **Automated Recurring Scans**: Built-in cron scheduler for daily, weekly, or monthly continuous perimeter audits.
- [ ] **Custom Nuclei Private Git Template Ingestion**: Securely clone and sync proprietary vulnerability templates from private GitHub / GitLab repositories using deploy keys.
- [ ] **SIEM Syslog Forwarder**: Real-time CEF and RFC 5424 syslog emitter for enterprise SIEM ingestion (Splunk, Elastic, Sentinel).

### Version 3.0 (Long-Term Horizon)
- [ ] **Distributed Multi-Node Worker Cluster**: Celery + Redis task fabric enabling distributed worker nodes across cloud regions.
- [ ] **Cloud Asset Discovery Integrations**: Native AWS Route53, Cloudflare DNS, and Azure Resource Graph automated asset synchronizers.
- [ ] **Automated Remediation Verification**: Closed-loop re-testing that automatically re-executes only the failed Nuclei templates to verify patch application.

---

## 🔒 Security Disclosure Policy & Safe Harbor

The security of XenoraSec and its users is paramount. If you discover a vulnerability or security flaw, please review our coordinated disclosure guidelines:

### 1. Reporting Channels & PGP Key
- **Primary Channel**: Privately submit an advisory via [GitHub Security Advisories](https://github.com/prithvi-01x/XenoraSec/security/advisories/new).
- **Secondary Channel**: Email `security@xenorasec.io` (or maintainer direct email) encrypted with our PGP key:
  ```text
  Key Fingerprint: 4E5A 9B0C 1A2E 3F4D 5C6B  7A8F 9A7C 3B2F 1D84 E5A9
  ```
- **Do not open public GitHub issues** for zero-day vulnerabilities or security bypasses.

### 2. Response SLAs & Coordinated Disclosure Timeline
- **Initial Acknowledgment**: Within **48 hours** of initial receipt.
- **Triage & Reproducibility Assessment**: Within **5 business days**.
- **Fix Deployment & Patch Release**: Critical vulnerabilities patched within **14 business days**.
- **Public Disclosure**: Coordinated release following a **90-day window** (or sooner upon agreed mutual timeline and patch availability).

### 3. Safe Harbor Commitment
We consider research conducted under this policy to be authorized. We commit not to pursue legal action against researchers who:
- Make a good-faith effort to avoid privacy violations, data destruction, and service interruption.
- Give us reasonable time to remediate the vulnerability before public disclosure.
- Strictly interact only with systems/accounts they personally own or have explicit authorization to test.

---

## 🤝 Contributing & Developer Guidelines

We warmly welcome community contributions from security researchers, systems developers, and DevSecOps practitioners!

### 1. Contribution Workflow
1. **Fork** the repository and create your feature branch:
   ```bash
   git checkout -b feature/dynamic-nuclei-filters
   ```
2. **Setup Pre-commit & Testing Environment**:
   ```bash
   pip install -r requirements.txt
   cd frontend && npm install && cd ..
   ```
3. **Execute Test Verification**:
   ```bash
   pytest -v
   cd frontend && npm run type-check && npm run lint && cd ..
   ```
4. **Commit with Conventional Commits & DCO**:
   All commits must adhere to the [Conventional Commits](https://www.conventionalcommits.org/) standard and include a Developer Certificate of Origin (`-s` sign-off):
   ```bash
   git commit -s -m "feat(scanner): add custom nuclei tag exclusion filters"
   ```
5. **Open a Pull Request**: Detail the rationale, link related issues, and provide test evidence.

### 2. Code Style & Quality Standards
- **Python**: Formatted with `black` (line length 88), linted with `ruff`, strict type hinting with `mypy`.
- **Frontend**: Clean React 19 functional components, strict TypeScript, Tailwind CSS utility styling without ad-hoc inline styles.
- **API Changes**: Any modifications to `/api` routes must include corresponding Pydantic schema validation and Swagger docstrings.

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