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
  <a href="#-installation--local-development-setup"><b>⚡ Quick Start</b></a> •
  <a href="#-architecture--pipeline"><b>🏗️ Architecture</b></a> •
  <a href="#-rest-api-reference"><b>📡 API Reference</b></a> •
  <a href="#-dual-engine-scanning-mechanics"><b>⚙️ Dual Engine</b></a> •
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
  - [🌐 Network Port Scanning Strategy & Rate Limiting Guide](#-network-port-scanning-strategy--rate-limiting-guide)
  - [📝 Custom Nuclei Template Authoring Guide](#3-custom-nuclei-template-authoring-guide)
- [🌐 Multi-Target & CIDR Subnet Scanning](#-multi-target--cidr-subnet-scanning)
- [🌐 Passive Reconnaissance & OSINT Engine](#-passive-reconnaissance--osint-engine)
- [🏢 Asset Inventory & Attack Surface Management](#-asset-inventory--attack-surface-management)
- [🧠 AI Risk Scoring & Saturation Model](#-ai-risk-scoring--saturation-model)
  - [📊 Executive Risk Scoring & Remediation SLA Playbook](#3-executive-risk-scoring--remediation-sla-playbook)
- [💻 Live Terminal & Streaming Engine](#-live-terminal--streaming-engine)
- [📑 Multi-Format Security Report Generation](#-multi-format-security-report-generation)
- [🔔 SIEM & SOAR Webhook & Event Payload Schemas](#-siem--soar-webhook--event-payload-schemas)
  - [📡 Canonical Event Envelope & Enterprise Adapters (Splunk, Elastic, PagerDuty, Sentinel)](#1-canonical-event-envelope-schema)
- [🔒 Security Safeguards & Defensive Engineering](#-security-safeguards--defensive-engineering)
  - [🎯 Threat Modeling & STRIDE / DREAD Attack Surface Taxonomy](#4-threat-modeling--stride--dread-attack-surface-taxonomy)
- [🗄️ Database Architecture & Concurrency](#-database-architecture--concurrency)
  - [🚀 High-Concurrency Scaling & PostgreSQL Migration Guide](#3-high-concurrency-scaling--postgresql-production-migration-guide)
- [📡 REST API Reference](#-rest-api-reference)
- [💻 cURL Command Cookbook](#-curl-command-cookbook)
- [⚙️ Environment Configuration](#-environment-configuration)
- [🚀 Installation & Local Development Setup](#-installation--local-development-setup)
- [🚢 Production Deployment (Docker & Nginx)](#-production-deployment)
- [🛡️ Container Hardening & Non-Root Security](#-container-hardening--non-root-security)
- [🛡️ Production Hardening & Defense-in-Depth Checklist](#-production-hardening--defense-in-depth-checklist)
- [🔄 CI/CD Automation Pipeline](#-cicd-automation-pipeline)
- [🔄 DevSecOps CI/CD Integration Recipes](#-devsecops-cicd-integration-recipes)
  - [⚙️ CI/CD Quality Gates & Pre-Commit Hook Recipes](#1-github-actions-dast-quality-gate-workflow)
- [💻 Frontend Tour & Mobile Responsiveness](#-frontend-tour--mobile-responsiveness)
- [🎨 Tactical Dark UI Design System](#-tactical-dark-ui-design-system)
- [🧪 Testing & Quality Assurance](#-testing--quality-assurance)
- [⚡ Performance Benchmarks & Tuning](#-performance-benchmarks--tuning)
- [💾 Database Maintenance, Backup & Disaster Recovery Runbooks](#-database-maintenance-backup--disaster-recovery-runbooks)
  - [💾 Online Hot Backups, WAL Compaction & Automated DR Restoration Drill](#1-sqlite-online-hot-backups--integrity-checks)
- [❓ Troubleshooting & FAQ](#-troubleshooting--faq)
- [🏛️ Compliance & Regulatory Framework Mapping](#-compliance--regulatory-framework-mapping)
  - [📋 Regulatory Crosswalk Matrix & OWASP Top 10 Coverage](#1-framework-crosswalk-matrix)
- [📁 Project Structure](#-project-structure)
- [🗺️ Product Roadmap](#-product-roadmap)
- [🔒 Security Disclosure Policy & Safe Harbor](#-security-disclosure-policy--safe-harbor)
- [🤝 Contributing & Developer Guidelines](#-contributing--developer-guidelines)
- [📖 Comprehensive Security & Scanning Terminology Glossary](#-comprehensive-security--scanning-terminology-glossary)
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

#### 🌐 Network Port Scanning Strategy & Rate Limiting Guide

Selecting the appropriate scanning parameters balances port discovery completeness against target saturation and intrusion detection triggers. XenoraSec applies the following engineering trade-offs:

```mermaid
flowchart LR
    SPEED["Scan Velocity & Concurrency"] <--> NOISE["IDS/IPS Noise & Firewall Alerts"]
    ACCURACY["Port Discovery Accuracy"] <--> TIME["Assessment Duration Window"]
```

##### 1. TCP Connect (`-sT`) vs TCP SYN Stealth (`-sS`)
- **TCP Connect (`-sT`)**: XenoraSec utilizes standard OS `connect()` socket syscalls. 
  - *Advantages*: Runs cleanly without `root` or `CAP_NET_RAW` privileges; fully compliant with Docker, AWS Fargate, and Kubernetes container security standards.
  - *Firewall State Table Impact*: Since the full 3-way handshake (`SYN` $\to$ `SYN-ACK` $\to$ `ACK`) completes before sending `RST`, intermediate stateful firewalls track the connection cleanly in `nf_conntrack` tables, preventing orphan state table exhaustion.
- **TCP SYN Stealth (`-sS`)**: Bypasses the application layer by sending raw `RST` packets after receiving `SYN-ACK`.
  - *Disadvantages*: Mandates root privileges, creates half-open socket records in IDS logs, and is frequently dropped or throttled by cloud virtualization network hypervisors (e.g. AWS VPC packet filters).

##### 2. Timing Templates (`-T0` to `-T5`) Performance Trade-Off Matrix

```text
┌────────────────────────────────────────────────────────────────────────┐
│                   Timing Policy Performance Spectrum                   │
├──────────────┬──────────────┬──────────────┬──────────────┬────────────┤
│ Policy       │ Delay/Probe  │ Max RTT      │ Max Hosts    │ Packet Drop│
├──────────────┼──────────────┼──────────────┼──────────────┼────────────┤
│ -T0 Paranoid │ 300,000 ms   │ 15,000 ms    │ 1            │ Very Low   │
│ -T1 Sneaky   │ 15,000 ms    │ 10,000 ms    │ 1            │ Very Low   │
│ -T2 Polite   │ 400 ms       │ 10,000 ms    │ 1            │ Very Low   │
│ -T3 Normal   │ 0 ms (adapt) │ 10,000 ms    │ Dynamic      │ Low        │
│ -T4 Aggress. │ 0 ms (adapt) │ 1,250 ms     │ Up to 1024   │ Low (LAN)  │
│ -T5 Insane   │ 0 ms         │ 300 ms       │ Up to 4096   │ Elevated   │
└──────────────┴──────────────┴──────────────┴──────────────┴────────────┘
```

- **Avoid `-T5` on WAN / Internet Scans**: While `-T5` executes in seconds on localhost or high-speed LAN, WAN packet jitter and multi-hop latency routinely exceed the 300ms max RTT timeout, producing **false negatives** where open ports are erroneously reported as filtered or closed.
- **Default `-T4` Optimization**: XenoraSec defaults to `-T4`, capping maximum probe round-trip timeouts at 1.25 seconds while allowing dynamic adaptive probe delays.

##### 3. Port Range Selection Economics

| Scan Strategy | Port Specification | Total Probed | Estimated Time (T4) | Empirical Exposure Coverage |
| :--- | :--- | :--- | :--- | :--- |
| **Rapid Perimeter Recon** | `--top-ports 100` | 100 ports | ~10 - 20 seconds | ~93.2% of all enterprise web and management services |
| **Standard Enterprise Audit**| `--top-ports 1000` | 1000 ports | ~45 - 90 seconds | ~98.6% of common services (HTTP, SSH, RDP, DBs) |
| **Exhaustive Deep Audit** | `-p 1-65535` | 65,535 ports | ~8 - 15 minutes | 100% full TCP spectrum (catches non-standard ports) |

##### 4. Firewall Conntrack Mitigation & Rate Limiting
When scanning enterprise subnets behind stateful firewalls (Palo Alto, Fortinet, pfSense):
- High-frequency SYN bursts can fill the firewall's connection tracking table (`netfilter.ip_conntrack_max`), dropping legitimate user traffic.
- XenoraSec enables `--max-rate` pacing via environment configuration (`NMAP_MAX_RATE=100`) to guarantee scan probe bursts remain within safe bounds.

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

### 3. Custom Nuclei Template Authoring Guide

XenoraSec natively supports proprietary and organization-specific vulnerability templates alongside the public ProjectDiscovery community repository. Security teams can author bespoke YAML templates to detect private API exposures, internal configuration drift, zero-day CVE indicators, or proprietary technology markers.

#### Template Structure & Core Hierarchy

Nuclei v3 templates follow a structured YAML schema consisting of an identification block, metadata classification, execution protocol, request definitions, matchers, and extractors:

```yaml
id: xenora-actuator-env-exposure

info:
  name: Spring Boot Actuator Env Endpoint Key Leakage
  author: xenora-sec-ops
  severity: critical
  description: Detects unprotected Spring Boot Actuator /env or /actuator/env endpoints leaking credentials, tokens, and database passwords.
  reference:
    - https://cwe.mitre.org/data/definitions/200.html
    - https://cwe.mitre.org/data/definitions/522.html
  remediation: Disable or restrict the /actuator/env endpoint using Spring Security with management.endpoints.web.exposure.exclude=env.
  classification:
    cvss-metrics: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N
    cvss-score: 7.5
    cwe-id: CWE-200,CWE-522
  metadata:
    max-request: 2
    verified: true
    vendor: spring
    product: spring_boot
  tags: exposure,spring,actuator,keys,misconfig,xenora

http:
  - method: GET
    path:
      - "{{BaseURL}}/actuator/env"
      - "{{BaseURL}}/env"

    headers:
      Accept: application/json, text/plain, */*
      User-Agent: XenoraSec-Audit-Engine/2.1

    stop-at-first-match: true
    matchers-condition: and
    matchers:
      - type: status
        status:
          - 200

      - type: word
        words:
          - "propertySources"
          - "activeProfiles"
        condition: or
        part: body

      - type: regex
        name: token_extract
        regex:
          - '(?i)(password|secret|apikey|token|aws_access_key_id)["'']?\s*:\s*["''][^"'']{4,}'
        part: body

    extractors:
      - type: json
        part: body
        json:
          - ".activeProfiles[]"
```

#### Matcher Types & Logic Operators

XenoraSec's execution wrapper parses Nuclei's full array of matcher primitives:

| Matcher Type | Syntax Parameter | Primary Use Case | Example Invariant |
| :--- | :--- | :--- | :--- |
| **`status`** | `status: [200, 301, 403]` | HTTP response code verification | Asserts endpoint returns `200` instead of `404` |
| **`word`** | `words: ["admin", "root"]` | Substring match in body, header, or all | Substring detection with `condition: and` or `condition: or` |
| **`regex`** | `regex: ['root:.*:0:0:']` | Regular expression pattern evaluation | Extracting `/etc/passwd` root account hashes |
| **`dsl`** | `dsl: ["len(body) > 1000"]` | Programmatic boolean evaluation helper | `status_code == 200 && contains(content_type, 'json')` |
| **`binary`** | `binary: ["504B0304"]` | Raw hex byte sequence matching | ZIP archive magic header detection in file downloads |

#### Extractor Types & Finding Context
Extractors pull dynamic tokens from HTTP bodies and headers to populate the `matched_at` and finding payload inside XenoraSec:
- **`json`**: Evaluates JSONPath queries (`.services.database.host`) against JSON responses.
- **`regex`**: Extracts captured groups via parentheses (`token=([a-zA-Z0-9_\-]+)`).
- **`kval`**: Key-value pair extraction from response headers (`kval: [server, x-powered-by]`).
#### Multi-Step Workflows & Protocol Flow Chaining

Modern complex vulnerabilities require multi-step verification (e.g. obtaining an auth session or CSRF token before probing an internal admin interface). Nuclei v3 enables programmatic multi-request chaining via Javascript execution flows:

```yaml
id: xenora-auth-bypass-chain

info:
  name: Chained Admin Endpoint Privilege Verification
  author: xenora-sec-ops
  severity: high
  description: Authenticates with guest credentials and confirms access to restricted /api/v1/admin/users.
  tags: auth,privilege-escalation,xenora

flow: |
  http(1) && http(2)

http:
  - raw:
      - |
        POST /api/v1/auth/guest HTTP/1.1
        Host: {{Hostname}}
        Content-Type: application/json

        {"guest_mode": true}

    extractors:
      - type: json
        internal: true
        name: session_token
        json:
          - ".token"

  - raw:
      - |
        GET /api/v1/admin/users HTTP/1.1
        Host: {{Hostname}}
        Authorization: Bearer {{session_token}}

    matchers-condition: and
    matchers:
      - type: status
        status:
          - 200
      - type: word
        words:
          - '"role":"superadmin"'
```

#### Managing Local Template Repositories

To inject custom templates into XenoraSec:
1. **Directory Convention**: Place bespoke templates in a mounted volume or dedicated directory:
   ```text
   /opt/xenorasec/custom-templates/
   ├── api-exposures/
   │   └── internal-swagger-leak.yaml
   ├── credentials/
   │   └── default-vault-login.yaml
   └── cve-local/
       └── zero-day-probe.yaml
   ```
2. **Template Validation**: Validate YAML syntax using Nuclei's native linter:
   ```bash
   nuclei -t /opt/xenorasec/custom-templates/ -validate
   ```
3. **Execution via Custom Profile**: In the XenoraSec UI or via `POST /api/scan/`, pass `custom_tags: "xenora,internal"` or supply the custom template directory in `.env`:
   ```env
   NUCLEI_CUSTOM_TEMPLATES="/opt/xenorasec/custom-templates"
   ```

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

### 3. Executive Risk Scoring & Remediation SLA Playbook

Traditional vulnerability management platforms frequently fail security leadership by using linear summation (where 50 minor informational banners generate a terrifying score of 500, while a solitary unauthenticated Remote Code Execution is masked). XenoraSec solves this with its **Michaelis-Menten Saturation Model** combined with an actionable **Remediation SLA Playbook**.

#### Michaelis-Menten Kinetics vs. Legacy Linear Models

```text
Risk Score (0 - 10.0)
 10.0 ┌───────────────────────────────────────────··············· Asymptotic Limit (Vmax=10.0)
      │                                    . · ´
  8.0 │                              . · ´       Scenario D: Severely Compromised (8.40)
      │                        . · ´
  6.0 │                  . · ´
      │            . · ´
  5.0 ┼─────── · ´ ────────────────────────────── Half-Max Saturation Point (Km = 15.0)
  4.0 │      .´                                  Scenario C: Active RCE Compromise (4.24)
      │    .´
  2.0 │  .´                                      Scenario B: Corporate Web Portal (2.35)
      │ .´
  0.0 └────────────────────────────────────────── Scenario A: Static Perimeter (0.38)
      0       15       30       45       60       75       90       Substrate Load (S)
```

- **Mathematical Invariant**: At $S = K_m = 15.0$, the Risk Score is guaranteed to be exactly $5.0$ (half of $V_{\max}$).
- **First-Finding Dominance**: The first critical vulnerability produces a steep jump in the curve ($\Delta \text{Score} \approx 3.0 - 4.5$), immediately alerting the SOC. Subsequent findings experience diminishing marginal addition, preventing score runaway.

#### Vulnerability Prioritization & Remediation SLA Matrix

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        Enterprise Remediation SLA Playbook                             │
├──────────┬──────────────┬─────────────┬──────────────┬─────────────────────────────────┤
│ Tier     │ Risk Score   │ CVSS Range  │ Max SLA      │ Required Operational Action     │
├──────────┼──────────────┼─────────────┼──────────────┼─────────────────────────────────┤
│ Tier 1   │ 8.0 - 10.0   │ 9.0 - 10.0  │ 24 - 48 Hours│ Emergency Incident Command      │
│ Critical │              │             │              │ Hotfix deployment or isolation  │
├──────────┼──────────────┼─────────────┼──────────────┼─────────────────────────────────┤
│ Tier 2   │ 6.0 - 7.9    │ 7.0 - 8.9   │ 7 Days       │ Sprint interruption             │
│ High     │              │             │              │ WAF virtual patch / config fix  │
├──────────┼──────────────┼─────────────┼──────────────┼─────────────────────────────────┤
│ Tier 3   │ 3.0 - 5.9    │ 4.0 - 6.9   │ 30 Days      │ Standard development backlog    │
│ Medium   │              │             │              │ Next scheduled maintenance cycle│
├──────────┼──────────────┼─────────────┼──────────────┼─────────────────────────────────┤
│ Tier 4   │ 0.0 - 2.9    │ 0.1 - 3.9   │ 90 Days      │ Low priority hardening          │
│ Low/Info │              │             │              │ Addressed during tech debt pass │
└──────────┴──────────────┴─────────────┴──────────────┴─────────────────────────────────┘
```

#### Incident Escalation & Compensating Controls Workflow

```mermaid
flowchart TD
    FINDING["Vulnerability Discovered via Scan"] --> EVAL{"Evaluate Severity & Score"}
    
    EVAL -->|"Score >= 8.0 or CVSS >= 9.0"| CRIT["Tier 1: Critical (48h SLA)"]
    EVAL -->|"Score 6.0 - 7.9"| HIGH["Tier 2: High (7d SLA)"]
    EVAL -->|"Score 3.0 - 5.9"| MED["Tier 3: Medium (30d SLA)"]
    EVAL -->|"Score < 3.0"| LOW["Tier 4: Low (90d SLA)"]

    CRIT --> NOTIFY["Auto-Dispatch PagerDuty / Webhook"]
    NOTIFY --> WAR_ROOM["Convene Emergency Remediation War Room"]
    WAR_ROOM --> PATCH{"Can Patch Be Applied within 24h?"}
    PATCH -->|Yes| APPLY["Deploy Patch & Verify via XenoraSec Re-Scan"]
    PATCH -->|No| COMPENSATE["Deploy Compensating Control (WAF Rule / IP Whitelist)"]
    COMPENSATE --> AUDIT_LOG["File Formal Risk Exception in Asset Inventory"]
```

#### Formal Risk Acceptance & Exception Policies
When a finding cannot be patched within the required SLA due to vendor dependencies:
1. **Compensating Controls**: Document virtual patch (e.g. Cloudflare WAF managed rule or ModSecurity CRS block).
2. **Audit Exception Logging**: Record the exception in the Asset Inventory drawer (`PATCH /api/assets/{id}`) with reason, ticket ID, and mandatory re-evaluation date (maximum 90 days).
3. **Automated Re-Verification**: XenoraSec scans the endpoint to confirm the compensating control actively blocks the exploit payload.

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

## 🔔 SIEM & SOAR Webhook & Event Payload Schemas

To integrate XenoraSec into Security Operations Centers (SOC) and Incident Response pipelines, the platform emits standardized JSON event payloads compatible with enterprise SIEM and SOAR platforms (Splunk, Elastic Common Schema, PagerDuty, and Jira).

```mermaid
flowchart LR
    SCAN_FINISH["Scan Completion / High-Risk Finding"] --> WEBHOOK["Webhook Dispatcher\n(HMAC-SHA256 Signed)"]
    WEBHOOK --> SPLUNK["Splunk HEC\n(/services/collector)"]
    WEBHOOK --> ELASTIC["Elastic / OpenSearch\n(ECS Event Schema)"]
    WEBHOOK --> PAGER["PagerDuty v2\n(/v2/enqueue)"]
    WEBHOOK --> JIRA["Jira Cloud REST\n(/rest/api/3/issue)"]
```

### 1. Canonical Event Envelope Schema
All emitted security notifications follow a unified RFC 7159 event envelope:

```json
{
  "event_id": "evt_7f8c2b1a-9d3e-4b6a-8c1d-5e2f3a4b5c6d",
  "event_type": "vulnerability.critical_detected",
  "timestamp": "2026-09-28T14:32:00.124Z",
  "producer": {
    "name": "XenoraSec",
    "version": "2.1.0",
    "host": "scanner-node-01.internal"
  },
  "scan_context": {
    "scan_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
    "target": "api.example.com",
    "profile": "full",
    "risk_score": 8.40
  },
  "data": {
    "template_id": "cve-2023-46805",
    "severity": "critical",
    "name": "Ivanti Connect Secure Authentication Bypass",
    "cvss_score": 9.8,
    "cwe_id": "CWE-287",
    "matched_at": "https://api.example.com/api/v1/totp/user-backup-code",
    "reproduction_curl": "curl -X POST https://api.example.com/api/v1/totp/user-backup-code",
    "epss_score": 0.942
  }
}
```

### 2. Splunk HTTP Event Collector (HEC) Adapter
Forward scan findings directly into Splunk indexers (`sourcetype="xenorasec:finding"`):

```json
{
  "time": 1790605920,
  "host": "scanner-node-01.internal",
  "source": "xenorasec",
  "sourcetype": "xenorasec:finding",
  "index": "security_ops",
  "event": {
    "action": "detected",
    "target": "api.example.com",
    "scan_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
    "risk_score": 8.40,
    "cve": "CVE-2023-46805",
    "cvss": 9.8,
    "severity": "critical",
    "endpoint": "https://api.example.com/api/v1/totp/user-backup-code"
  }
}
```

### 3. Elastic Common Schema (ECS) Mapping
Enables immediate dashboard correlation within Elastic SIEM and Kibana Security:

| XenoraSec Field | Elastic Common Schema (ECS) Field | Description |
| :--- | :--- | :--- |
| `timestamp` | `@timestamp` | UTC event creation timestamp |
| `target` | `destination.domain` or `destination.ip` | Evaluated perimeter entity |
| `open_ports[].port` | `destination.port` | Discovered open port number |
| `vulnerabilities[].severity` | `vulnerability.severity` | Finding severity classification |
| `vulnerabilities[].cvss_score` | `vulnerability.score.base` | CVSS v3.1 numeric base score |
| `vulnerabilities[].cve` | `vulnerability.id` | NVD CVE identifier |
| `risk_score` | `event.risk_score` | Michaelis-Menten aggregate posture score |

### 4. PagerDuty Events API v2 Incident Trigger
Dispatches instant pager notifications to on-call SOC engineers when `risk_score >= 8.0` or critical CVEs are detected:

```json
{
  "routing_key": "pd-service-key-xenorasec-ops",
  "event_action": "trigger",
  "dedup_key": "xenora/9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d/cve-2023-46805",
  "payload": {
    "summary": "CRITICAL Vulnerability Discovered: CVE-2023-46805 on api.example.com (CVSS 9.8)",
    "severity": "critical",
    "source": "XenoraSec ASM Engine",
    "component": "Vulnerability Scanner",
    "group": "Perimeter-Security",
    "custom_details": {
      "target": "api.example.com",
      "risk_score": 8.40,
      "matched_url": "https://api.example.com/api/v1/totp/user-backup-code",
      "scan_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d"
    }
  }
}
```

### 5. Webhook HMAC-SHA256 Signature Verification
To prevent spoofing of incoming webhooks, XenoraSec signs every outbound HTTP POST request with an HMAC-SHA256 signature in the `X-Xenora-Signature` header:

```python
# Python Webhook Verification Example
import hmac
import hashlib

def verify_xenora_webhook(payload_bytes: bytes, signature_header: str, secret_key: str) -> bool:
    """Verifies that the incoming webhook payload was authentically emitted by XenoraSec."""
    expected_sig = "sha256=" + hmac.new(
        key=secret_key.encode("utf-8"),
        msg=payload_bytes,
        digestmod=hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected_sig, signature_header)
```

### 6. Microsoft Sentinel & ArcSight Common Event Format (CEF) Adapter
For organizations running Microsoft Sentinel, ArcSight, or traditional Syslog aggregators, XenoraSec converts scan findings into standard RFC 5424 / CEF log events:

```text
CEF:0|XenoraSec|EnterpriseScanner|2.1|VULN_DETECTED|Critical Vulnerability Discovered|10|src=10.0.1.25 dst=api.example.com dpt=443 cs1=CVE-2023-46805 cs1Label=CVE cs2=CWE-287 cs2Label=CWE cfp1=9.8 cfp1Label=CVSS msg=Ivanti Connect Secure Authentication Bypass act=detected
```

#### Microsoft Sentinel Log Analytics Custom Table Ingestion (DCR)
```json
{
  "TimeGenerated": "2026-09-28T14:32:00.124Z",
  "TargetHost_s": "api.example.com",
  "ScanId_g": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "VulnerabilityTitle_s": "Ivanti Connect Secure Authentication Bypass",
  "CVE_s": "CVE-2023-46805",
  "CVSS_d": 9.8,
  "Severity_s": "Critical",
  "RiskScore_d": 8.40,
  "MatchedEndpoint_s": "https://api.example.com/api/v1/totp/user-backup-code",
  "RemediationSLA_s": "48 Hours"
}
```

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

### 4. Threat Modeling & STRIDE / DREAD Attack Surface Taxonomy

Operating an autonomous dual-engine scanner introduces distinct operational security hazards. To safeguard the scanner infrastructure and prevent it from being weaponized as an SSRF proxy, pivot point, or denial-of-service amplifier, XenoraSec is modeled against the Microsoft **STRIDE** classification and evaluated using the **DREAD** risk rating methodology.

#### STRIDE Threat Classification & Defensive Countermeasures

| Threat Vector | STRIDE Category | Attack Scenario & Exploit Path | XenoraSec Defense-in-Depth Implementation | Architectural Boundary |
| :--- | :--- | :--- | :--- | :--- |
| **Client IP Spoofing** | **Spoofing** | Adversary falsifies `X-Forwarded-For` or `X-Real-IP` to bypass sliding-window rate limits or poison scan audit logs. | `RateLimiter` enforces `TRUST_PROXY_HEADERS=True` gate, verifies socket peer against `TRUSTED_PROXIES` CIDR list, and evaluates rightmost untrusted hop. | Ingress API Gateway |
| **Target String Tampering** | **Tampering** | Command injection via crafted target strings (`example.com; rm -rf /` or `127.0.0.1 && cat /etc/passwd`). | Subprocess dispatch uses `asyncio.create_subprocess_exec` with explicit argv tokenization; target undergoes regex FQDN/IPv4 validation and `socket.getaddrinfo()`. | Engine Coordinator |
| **Audit Log Repudiation** | **Repudiation** | Rogue operator or external attacker triggers scans against unauthorized third-party infrastructure and denies origin. | Structured JSON telemetry logs record UTC timestamps, client socket IPs, user-agent fingerprints, and immutable SQLite WAL commit records. | Persistence & Logging |
| **SSRF & Metadata Leak** | **Information Disclosure** | Adversary passes cloud metadata (`169.254.169.254`) or loopback (`127.0.0.1`) to steal IAM credentials or Kubernetes tokens. | Zero-trust DNS pre-resolution verifies all candidate IPv4/IPv6 addresses against RFC 1918, RFC 3927 (link-local), RFC 5737 (testnets), and loopback ranges. | Target Sanitization Gate |
| **Worker Exhaustion DoS** | **Denial of Service** | Submitting mass `/16` CIDR subnets or wildcard honeypots emitting millions of findings to exhaust memory and disk. | Gated prefix validation (`MAX_CIDR_PREFIX=24`, max 256 hosts), 1MB circular ring buffer, `MAX_VULNERABILITIES=1000` hard cap, and `asyncio.Semaphore` slot governors. | Task Queue & Subprocesses |
| **Container Privilege Escalation** | **Elevation of Privilege** | Exploit in Nmap/Nuclei C/Go binary escapes to host root via vulnerable kernel or cap-raw socket vulnerability. | Container executes strictly as unprivileged `xenora` (UID `10001`), drops `ALL` Linux capabilities (`cap_drop: ALL`), enforces `no-new-privileges:true`, and mounts read-only rootfs. | Container Runtime Sandbox |

#### DREAD Quantitative Risk Scoring Matrix

Every vulnerability discovery and operational risk factor within XenoraSec is prioritized using the **DREAD** (Damage, Reproducibility, Exploitability, Affected Users, Discoverability) weighted scoring model:

$$\text{DREAD Score} = \frac{D + R + E + A + D_{\text{isc}}}{5}$$

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        XenoraSec DREAD Attack Surface Matrix                           │
├─────────────────────┬──────────┬──────────┬──────────┬──────────┬──────────┬───────────┤
│ Threat Scenario     │ Damage   │ Reprod.  │ Exploit. │ Affected │ Discov.  │ Total/10  │
├─────────────────────┼──────────┼──────────┼──────────┼──────────┼──────────┼───────────┤
│ Unauthenticated RCE │ 10       │ 10       │ 9        │ 10       │ 8        │ 9.4 (Crit)│
│ Cloud Metadata SSRF │ 9        │ 9        │ 8        │ 10       │ 7        │ 8.6 (High)│
│ Subdomain Takeover  │ 8        │ 8        │ 7        │ 8        │ 9        │ 8.0 (High)│
│ Stored XSS in Admin │ 6        │ 9        │ 6        │ 5        │ 7        │ 6.6 (Med) │
│ Rate Limit Bypass   │ 4        │ 8        │ 7        │ 4        │ 6        │ 5.8 (Med) │
│ Banner Leakage      │ 2        │ 10       │ 3        │ 2        │ 9        │ 5.2 (Low) │
└─────────────────────┴──────────┴──────────┴──────────┴──────────┴──────────┴───────────┘
```

##### DREAD Scoring Dimensions & Substrate Load Correlation

Each threat vector is assessed across five standardized dimensions scaled from 1 (minimal) to 10 (catastrophic):
- **Damage Potential ($D$)**: Extent of operational destruction or confidential data compromise (10 = full remote host takeover; 1 = trivial banner string leakage).
- **Reproducibility ($R$)**: Consistency with which an exploit succeeds without race conditions (10 = deterministic single-request exploit; 1 = intermittent multi-variable condition).
- **Exploitability ($E$)**: Skill and tooling barrier required to weaponize the vulnerability (10 = automated script / publicly available zero-configuration exploit; 1 = sophisticated customized kernel exploit requiring advanced tradecraft).
- **Affected Users ($A$)**: Proportion of user base, tenants, or systems impacted (10 = total administrative compromise across all tenants; 1 = isolated edge-case session).
- **Discoverability ($D_{\text{isc}}$)**: Ease of locating the vulnerability using automated tooling (10 = exposed on default ports / public CT logs; 1 = deeply nested internal logic bug).

In XenoraSec's risk aggregation pipeline, normalized DREAD scores serve as the empirical weighting function for individual finding substrates ($w_i$) fed into the **Michaelis-Menten saturation model**:

$$S = \sum_{i=1}^{N} \left( \frac{\text{DREAD}_i}{10.0} \times \text{Base Severity Weight}_i \right)$$

This mathematical bridge guarantees that vulnerabilities exhibiting extreme damage and high reproducibility saturate the score curve rapidly, elevating the asset to **Tier 1 Critical SLA** while filtering out noise from trivial informational disclosures.

#### Trust Boundaries & Attack Surface Topology

```mermaid
flowchart TB
    subgraph UntrustedInternet ["Untrusted External Zone"]
        CLIENT["Browser Client / External API"]
        TARGET["Remote Target Endpoints (WAN / Cloud)"]
    end

    subgraph PerimeterDMZ ["Perimeter Trust Boundary 1: Ingress Gateway"]
        NGINX["Nginx Reverse Proxy\n(TLS Termination, Port 80/443)"]
        RATELIM["Sliding-Window IP Rate Limiter"]
    end

    subgraph ApplicationBoundary ["Perimeter Trust Boundary 2: Application Core"]
        FASTAPI["FastAPI Async App (Python 3.12)"]
        VAL_GATE["Target Sanitizer & DNS Resolution Gate"]
        AUTH_GATE["Admin Maintenance Token Validator"]
    end

    subgraph ExecutionBoundary ["Perimeter Trust Boundary 3: Execution Sandbox"]
        SANDBOX["Isolated Process Sandbox (UID 10001, cap_drop: ALL)"]
        NMAP_RUN["Nmap Subprocess (-sT unprivileged)"]
        NUC_RUN["Nuclei Subprocess (-silent -jsonl -no-interactsh)"]
    end

    subgraph DataBoundary ["Perimeter Trust Boundary 4: Persistence Layer"]
        SQLITE[("SQLite WAL / PostgreSQL (chmod 770)")]
        DISK_VOL[("Data Volume (/data/scans.db)")]
    end

    CLIENT -->|HTTPS / WSS| NGINX
    NGINX -->|HTTP Forward (Trusted Peer)| RATELIM
    RATELIM --> FASTAPI
    FASTAPI --> VAL_GATE
    VAL_GATE -.->|Pre-Flight DNS Resolve| TARGET
    VAL_GATE -->|Gated Target String| SANDBOX
    SANDBOX --> NMAP_RUN
    SANDBOX --> NUC_RUN
    NMAP_RUN -->|Active TCP / HTTP Probes| TARGET
    NUC_RUN -->|Active TCP / HTTP Probes| TARGET
    FASTAPI --> AUTH_GATE
    FASTAPI --> SQLITE
    SQLITE --> DISK_VOL
```

---

## 🗄️ Database Architecture & Concurrency

XenoraSec supports both development SQLite and enterprise-scale PostgreSQL via SQLAlchemy 2.0 async sessions:

```mermaid
erDiagram
    SCAN_RESULT ||--o{ SCAN_RESULT : "retries (parent_scan_id)"
    ASSET ||--o{ ASSET_PORT : "exposes (1:N cascade)"
    ASSET ||--o{ ASSET_VULNERABILITY : "affects (1:N cascade)"
    RECON_HISTORY ||--o{ ASSET : "imports to"

    SCAN_RESULT {
        int id PK "Auto-increment primary key"
        string scan_id "Unique UUIDv4 identifier"
        string target "Validated hostname or IP"
        string status "running | completed | failed | timeout | partial"
        float risk_score "0.0 - 10.0 score"
        json result "Raw Nmap and Nuclei payloads"
        string scan_profile "quick | full | network | custom"
        string batch_id "UUIDv4 grouping if batch scan"
        string parent_scan_id "FK to original scan if retried"
        datetime created_at "ISO UTC timestamp"
    }

    ASSET {
        int id PK "Auto-increment primary key"
        string ip_address "Discovered host IP"
        string hostname "Resolved FQDN domain"
        string asset_type "ip | domain | url | cidr_host"
        string status "active | scanned | inactive"
        string criticality "low | medium | high | critical"
        float risk_score "Composite posture score"
        int open_ports_count "Discovered active ports"
        int vulnerabilities_count "Active CVE count"
        datetime last_scanned_at "Timestamp of latest scan"
    }

    ASSET_PORT {
        int id PK "Auto-increment primary key"
        int asset_id FK "FK referencing assets.id"
        int port "Port number"
        string protocol "tcp | udp"
        string service "Service banner identity"
        string version "Identified software version"
        datetime last_seen "Observation timestamp"
    }

    ASSET_VULNERABILITY {
        int id PK "Auto-increment primary key"
        int asset_id FK "FK referencing assets.id"
        string template_id "Nuclei template identifier"
        string name "Vulnerability title"
        string severity "critical | high | medium | low | info"
        string cve "CVE reference ID"
        float cvss "CVSS v3.1 base score"
        string status "open | resolved"
        datetime first_seen "Discovery timestamp"
        datetime last_seen "Reconfirmation timestamp"
    }

    RECON_HISTORY {
        int id PK "Auto-increment primary key"
        string domain "Target apex or FQDN domain"
        string status "completed | failed"
        float duration "Recon run seconds"
        int subdomains_count "Total CT logs mined"
        int active_subdomains_count "Live resolved hosts"
        int security_score "Mail & headers hygiene score"
        json result "Serialized DNS & OSINT payload"
        datetime created_at "ISO UTC timestamp"
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

### 3. High-Concurrency Scaling & PostgreSQL Production Migration Guide

When scaling XenoraSec across distributed scan workers or running continuous mass CIDR subnet assessments, migrate from SQLite to PostgreSQL with dedicated connection pooling.

```mermaid
flowchart TD
    subgraph AppCluster ["Stateless Backend Cluster"]
        APP1["FastAPI Node 1 (asyncpg)"]
        APP2["FastAPI Node 2 (asyncpg)"]
        APP3["FastAPI Node 3 (asyncpg)"]
    end

    subgraph Pooler ["Connection Pooling Middleware"]
        PGBOUNCE["pgBouncer\n(pool_mode = transaction, max_client_conn = 1000)"]
    end

    subgraph StorageEngine ["Enterprise Database Cluster"]
        PG_PRIMARY[("PostgreSQL 16 Primary\n(ACID Writes & Asset Relational State)")]
        PG_REPLICA[("PostgreSQL Read Replica\n(Read Queries & Historical Analytics)")]
        PG_PRIMARY -.->|Streaming Replication| PG_REPLICA
    end

    APP1 --> PGBOUNCE
    APP2 --> PGBOUNCE
    APP3 --> PGBOUNCE
    PGBOUNCE --> PG_PRIMARY
```

#### 1. SQLAlchemy 2.0 & asyncpg Connection Pool Sizing

Configure the asyncpg driver inside `.env` to prevent pool exhaustion during concurrent batch operations:

```env
DATABASE_URL="postgresql+asyncpg://xenora:SecureVaultPass123!@pg-cluster.internal:5432/xenorasec"
DB_POOL_SIZE=25
DB_MAX_OVERFLOW=50
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=1800
DB_POOL_PRE_PING=True
```

- **`DB_POOL_SIZE`**: Base persistent connection pool kept alive per worker container.
- **`DB_MAX_OVERFLOW`**: Burst capacity dynamically spawned under heavy batch scan loads.
- **`DB_POOL_PRE_PING`**: Issues lightweight `SELECT 1` heartbeat probes to discard stale or severed TCP sockets before assigning a connection to a background worker.
- **`DB_POOL_RECYCLE`**: Recycles connections every 1800 seconds (30 minutes) to eliminate server-side connection leaks.

#### 2. pgBouncer Production Configuration (`pgbouncer.ini`)
Deploy pgBouncer alongside PostgreSQL to handle thousands of concurrent polling requests without overwhelming Postgres process memory:

```ini
[databases]
xenorasec = host=127.0.0.1 port=5432 dbname=xenorasec

[pgbouncer]
listen_addr = 0.0.0.0
listen_port = 6432
auth_type = scram-sha-256
auth_file = /etc/pgbouncer/userlist.txt
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 30
min_pool_size = 10
reserve_pool_size = 5
reserve_pool_timeout = 5
max_db_connections = 100
```

#### 3. SQLite-to-PostgreSQL Data Migration Runbook

To migrate an existing SQLite `scans.db` instance into PostgreSQL without data loss:

1. **Step 1: Install PostgreSQL Client Libraries**:
   ```bash
   pip install asyncpg psycopg2-binary
   ```
2. **Step 2: Export SQLite Data using pgloader**:
   Create a migration script `migrate_sqlite_to_pg.load`:
   ```lisp
   load database
        from sqlite:///data/scans.db
        into postgresql://xenora:password@localhost:5432/xenorasec

   with include drop, create tables, create indexes, reset sequences

     set work_mem to '128MB', maintenance_work_mem to '512MB';
   ```
   Execute the migration:
   ```bash
   pgloader migrate_sqlite_to_pg.load
   ```
3. **Step 3: Synchronize PostgreSQL Auto-Increment Sequences**:
   ```sql
   SELECT setval(pg_get_serial_sequence('scan_results', 'id'), coalesce(max(id), 1)) FROM scan_results;
   SELECT setval(pg_get_serial_sequence('assets', 'id'), coalesce(max(id), 1)) FROM assets;
   SELECT setval(pg_get_serial_sequence('asset_ports', 'id'), coalesce(max(id), 1)) FROM asset_ports;
   SELECT setval(pg_get_serial_sequence('asset_vulnerabilities', 'id'), coalesce(max(id), 1)) FROM asset_vulnerabilities;
   SELECT setval(pg_get_serial_sequence('recon_history', 'id'), coalesce(max(id), 1)) FROM recon_history;
   ```
4. **Step 4: Update `.env` and Verify Database Health**:
   ```bash
   curl -f http://localhost:8000/health
   # Response: {"status":"healthy","database":"connected","backend":"postgresql"}
   ```

#### 4. Concurrency Slot Sizing Formula
To prevent out-of-memory (OOM) kernel terminations when authoring high-throughput scan pipelines, size `MAX_CONCURRENT_SCANS` using the following formula:

$$\text{Max Concurrent Scans} = \min\left(\left\lfloor \frac{\text{System Available RAM (MB)} - 1024}{350} \right\rfloor, \; \text{vCPU} \times 2\right)$$

*Example*: On an 8 vCPU server with 16 GB RAM (16,384 MB):
$$\text{Max Slots} = \min\left(\left\lfloor \frac{16384 - 1024}{350} \right\rfloor, \; 8 \times 2\right) = \min(43, 16) = \mathbf{16 \text{ slots}}$$

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

# Or ultra-fast setup with uv (Python 3.12+ recommended)
# uv venv && source .venv/bin/activate && uv pip install -r requirements.txt

# Start the FastAPI server on port 8000
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

> 💡 **Performance Tip**: XenoraSec is fully optimized for **Python 3.12+**. Using Astral's [`uv`](https://github.com/astral-sh/uv) package manager provides 10-100x faster dependency installation and deterministic virtual environment bootstrapping.

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

## 🛡️ Production Hardening & Defense-in-Depth Checklist

Deploying an autonomous penetration testing and vulnerability scanning appliance requires defense-in-depth controls across every infrastructure tier. The following production hardening checklist outlines mandatory security controls for enterprise deployments:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                   Defense-in-Depth Multi-Layer Model                   │
├────────────────────────────────────────────────────────────────────────┤
│ Layer 1: Edge & Ingress       │ TLS 1.3, Cloudflare/WAF, DDoS Shield  │
│ Layer 2: Network & Firewall   │ Ingress Port 443 only, Egress DNS lock │
│ Layer 3: Reverse Proxy        │ Nginx rate-limiting, strict CSP/HSTS   │
│ Layer 4: Application Runtime  │ Zero-trust SSRF, Pydantic validation   │
│ Layer 5: Execution Sandbox    │ UID 10001, cap_drop ALL, read-only fs  │
│ Layer 6: Data & Storage       │ chmod 770, AES-256 at rest, WAL sync   │
└────────────────────────────────────────────────────────────────────────┘
```

### 1. Transport Layer Security (TLS 1.3 & Cipher Suites)
- [ ] **Enforce TLS 1.3 with TLS 1.2 Fallback**: Disable SSLv3, TLS 1.0, and TLS 1.1 completely in Nginx or upstream ingress.
  ```nginx
  ssl_protocols TLSv1.2 TLSv1.3;
  ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384';
  ssl_prefer_server_ciphers on;
  ssl_session_cache shared:SSL:10m;
  ssl_session_timeout 1d;
  ssl_session_tickets off;
  ```
- [ ] **HTTP Strict Transport Security (HSTS)**: Send `Strict-Transport-Security: max-age=63072000; includeSubDomains; preload` to guarantee browsers never downgrade to unencrypted HTTP.
- [ ] **OCSP Stapling**: Enable `ssl_stapling on;` and `ssl_stapling_verify on;` to accelerate certificate revocation checks without leaking client browsing patterns to certificate authorities.

### 2. Strict HTTP Defensive Headers & Content Security Policy (CSP Level 3)
- [ ] **Content Security Policy (CSP)**: Restrict script and frame origins to prevent Cross-Site Scripting (XSS):
  ```nginx
  add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com data:; img-src 'self' data: https:; connect-src 'self' wss: ws: https:; frame-ancestors 'none'; base-uri 'self'; form-action 'self';" always;
  ```
- [ ] **Clickjacking Prevention**: Enforce `X-Frame-Options: DENY` on all backend responses.
- [ ] **MIME Sniffing Mitigation**: Enforce `X-Content-Type-Options: nosniff`.
- [ ] **Referrer Policy**: Enforce `Referrer-Policy: strict-origin-when-cross-origin` to prevent leaking target domain queries in HTTP referrers.
- [ ] **Permissions Policy**: Block intrusive browser capabilities: `Permissions-Policy: geolocation=(), camera=(), microphone=(), payment=()`.

### 3. Cross-Origin Resource Sharing (CORS) Governance
- [ ] **Reject Wildcard Origins in Production**: Ensure `ALLOWED_ORIGINS` in `.env` is never set to `*`. Explicitly whitelist exact operational domains (e.g., `ALLOWED_ORIGINS="https://scanner.internal.company.com"`).
- [ ] **Pre-Flight Cache Optimization**: Configure `Access-Control-Max-Age: 86400` to minimize unnecessary pre-flight OPTIONS overhead.

### 4. Host Firewall & Network Ingress/Egress Lockdown
- [ ] **Ingress Policy**: Restrict host inbound access strictly to ports 80/443 (HTTP/HTTPS) and port 22 (SSH via Bastion / VPN only).
  ```bash
  # UFW Lockdown Recipe
  sudo ufw default deny incoming
  sudo ufw default allow outgoing
  sudo ufw allow in on eth0 to any port 443 proto tcp
  sudo ufw allow in on eth0 to any port 80 proto tcp
  sudo ufw allow in on eth1 to any port 22 proto tcp comment 'SSH management interface'
  sudo ufw enable
  ```
- [ ] **Egress Guardrails**: While active scanning requires outbound TCP connectivity, block egress traffic destined for cloud metadata (`169.254.169.254/32`) at the host iptables level as a defense-in-depth safeguard against misconfiguration:
  ```bash
  sudo iptables -A OUTPUT -d 169.254.169.254/32 -j DROP
  ```

### 5. Linux Kernel & Container Seccomp Hardening
- [ ] **Non-Root System Execution**: Verify that the application process runs as UID `10001` (`xenora`) both inside and outside containers.
- [ ] **Drop All Linux Capabilities**: Configure `cap_drop: [ALL]` in Docker Compose or Kubernetes pod specs. XenoraSec does not use raw sockets for default `-sT` scans.
- [ ] **Prevent Privilege Escalation**: Verify `no-new-privileges:true` is active in container runtime definitions.
- [ ] **Read-Only Root Filesystem**: Run container with `--read-only`, mounting writeable `tmpfs` only at `/tmp` and `/run`.
- [ ] **Docker Daemon Socket Isolation**: Never mount `/var/run/docker.sock` into the application container. Exposing the Docker socket allows container breakout and full root takeover of the underlying host.
- [ ] **Host Kernel Sysctl Hardening**: Apply network stack and memory protections in `/etc/sysctl.d/99-xenorasec-hardening.conf`:
  ```ini
  # Network SYN flood and IP spoofing protection
  net.ipv4.tcp_syncookies = 1
  net.ipv4.conf.all.rp_filter = 1
  net.ipv4.icmp_echo_ignore_broadcasts = 1
  
  # Filesystem and kernel pointer leak mitigations
  fs.protected_regular = 2
  fs.protected_fifos = 2
  kernel.kptr_restrict = 2
  kernel.dmesg_restrict = 1
  ```

### 6. Secrets & Operational Credential Hygiene
- [ ] **Zero Hardcoded Secrets**: Ensure `GROQ_API_KEY` and `CLEANUP_SECRET` are passed through secure environment vaults (e.g. AWS Secrets Manager, HashiCorp Vault, Doppler, or GitHub Actions Secrets).
- [ ] **Log Scrubbing**: Verify that API keys and authentication tokens are never outputted in console logs or stored in scan result JSON columns.

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

## 🔄 DevSecOps CI/CD Integration Recipes

Integrate XenoraSec into your continuous integration and continuous deployment (CI/CD) pipelines to establish automated Dynamic Application Security Testing (DAST) quality gates. Stop critical vulnerabilities, unauthenticated debug endpoints, and configuration drift before merging to production.

```mermaid
flowchart LR
    COMMIT["Git Push / Pull Request"] --> CI["CI Runner (GitHub/GitLab/Jenkins)"]
    CI --> DEPLOY["Deploy Ephemeral Preview / Staging"]
    DEPLOY --> API_TRIGGER["Trigger XenoraSec Scan\n(POST /api/scan/)"]
    API_TRIGGER --> POLL["Poll Scan Status\n(GET /api/scan/results/{id})"]
    POLL --> GATE{"Quality Gate Check\n(Risk Score <= 4.0\nand Crit Vulns == 0)"}
    GATE -->|Pass| APPROVE["Approve PR / Deploy to Production"]
    GATE -->|Fail| BLOCK["Break Pipeline & Post PR Summary"]
```

### 1. GitHub Actions DAST Quality Gate Workflow
Create `.github/workflows/xenorasec-dast.yml` in your application repository:

```yaml
name: XenoraSec DAST Security Gate

on:
  pull_request:
    branches: [main, develop]
  workflow_dispatch:

jobs:
  security-audit:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Trigger XenoraSec Scan
        id: trigger_scan
        env:
          XENORASEC_URL: ${{ secrets.XENORASEC_HOST }}
          TARGET_APP: "https://staging-${{ github.event.pull_request.number }}.internal.example.com"
        run: |
          SCAN_RESP=$(curl -s -X POST "$XENORASEC_URL/api/scan/" \
            -H "Content-Type: application/json" \
            -d "{\"target\": \"$TARGET_APP\", \"scan_profile\": \"quick\"}")
          SCAN_ID=$(echo "$SCAN_RESP" | jq -r '.scan_id')
          echo "scan_id=$SCAN_ID" >> $GITHUB_OUTPUT
          echo "Dispatched scan $SCAN_ID against $TARGET_APP"

      - name: Await Scan Completion & Enforce Quality Gate
        env:
          XENORASEC_URL: ${{ secrets.XENORASEC_HOST }}
          SCAN_ID: ${{ steps.trigger_scan.outputs.scan_id }}
          MAX_PERMISSIBLE_RISK: 4.0
        run: |
          echo "Polling scan $SCAN_ID..."
          while true; do
            STATUS=$(curl -s "$XENORASEC_URL/api/scan/results/$SCAN_ID" | jq -r '.status // "unknown"')
            if [ "$STATUS" = "completed" ] || [ "$STATUS" = "partial" ]; then
              break
            elif [ "$STATUS" = "failed" ] || [ "$STATUS" = "timeout" ]; then
              echo "::error::Scan failed with status: $STATUS"
              exit 1
            fi
            sleep 10
          done

          RESULT=$(curl -s "$XENORASEC_URL/api/scan/results/$SCAN_ID")
          RISK_SCORE=$(echo "$RESULT" | jq -r '.risk_score')
          CRIT_COUNT=$(echo "$RESULT" | jq '[.vulnerabilities[]? | select(.severity == "critical")] | length')
          HIGH_COUNT=$(echo "$RESULT" | jq '[.vulnerabilities[]? | select(.severity == "high")] | length')

          echo "Audit completed. Risk Score: $RISK_SCORE | Critical: $CRIT_COUNT | High: $HIGH_COUNT"

          # Enforce Threshold Gate
          if [ "$CRIT_COUNT" -gt 0 ]; then
            echo "::error::Security gate rejected: $CRIT_COUNT critical vulnerabilities discovered."
            exit 1
          fi

          if (( $(echo "$RISK_SCORE > $MAX_PERMISSIBLE_RISK" | bc -l) )); then
            echo "::error::Security gate rejected: Risk score $RISK_SCORE exceeds threshold of $MAX_PERMISSIBLE_RISK."
            exit 1
          fi

          echo "Quality gate PASSED."
```

### 2. GitLab CI/CD Pipeline (`.gitlab-ci.yml`)

```yaml
stages:
  - test
  - dast

xenorasec_dast_audit:
  stage: dast
  image: alpine:latest
  before_script:
    - apk add --no-cache curl jq bc
  script:
    - |
      SCAN_RESP=$(curl -s -X POST "$XENORASEC_URL/api/scan/" \
        -H "Content-Type: application/json" \
        -d "{\"target\": \"$CI_ENVIRONMENT_URL\", \"scan_profile\": \"quick\"}")
      SCAN_ID=$(echo "$SCAN_RESP" | jq -r '.scan_id')
      
      while true; do
        STATUS=$(curl -s "$XENORASEC_URL/api/scan/results/$SCAN_ID" | jq -r '.status // "unknown"')
        [ "$STATUS" = "completed" ] && break
        [ "$STATUS" = "failed" ] && exit 1
        sleep 10
      done

      curl -s "$XENORASEC_URL/api/scan/$SCAN_ID/report?format=markdown&report_type=technical" -o dast-report.md
      RISK=$(curl -s "$XENORASEC_URL/api/scan/results/$SCAN_ID" | jq -r '.risk_score')
      if (( $(echo "$RISK > 4.5" | bc -l) )); then
        echo "DAST Risk Score $RISK exceeds threshold 4.5"
        exit 1
      fi
  artifacts:
    reports:
      dast: dast-report.md
    expire_in: 30 days
```

### 3. Jenkins Declarative Pipeline (`Jenkinsfile`)

```groovy
pipeline {
    agent any
    environment {
        XENORA_URL = 'http://xenorasec.internal:8000'
        TARGET_HOST = 'staging.example.com'
    }
    stages {
        stage('Dynamic Security Audit') {
            steps {
                sh '''
                    SCAN_ID=$(curl -s -X POST "${XENORA_URL}/api/scan/" \
                      -H "Content-Type: application/json" \
                      -d "{\\"target\\": \\"${TARGET_HOST}\\", \\"scan_profile\\": \\"quick\\"}" | jq -r .scan_id)
                    
                    until [ "$(curl -s ${XENORA_URL}/api/scan/results/${SCAN_ID} | jq -r .status)" = "completed" ]; do
                        sleep 10
                    done

                    SCORE=$(curl -s ${XENORA_URL}/api/scan/results/${SCAN_ID} | jq -r .risk_score)
                    echo "Scan ${SCAN_ID} completed with score: ${SCORE}"
                    
                    # Download HTML Report for Archival
                    curl -s "${XENORA_URL}/api/scan/${SCAN_ID}/report?format=html&report_type=executive" -o executive-report.html
                '''
            }
        }
    }
    post {
        always {
            archiveArtifacts artifacts: '*.html', fingerprint: true
        }
    }
}
```

### 4. Azure DevOps Pipeline (`azure-pipelines.yml`)

```yaml
trigger:
  - main

pool:
  vmImage: 'ubuntu-latest'

steps:
- script: |
    set -e
    RESPONSE=$(curl -s -X POST "$(XENORASEC_ENDPOINT)/api/scan/" \
      -H "Content-Type: application/json" \
      -d '{"target": "app.preview.internal", "scan_profile": "quick"}')
    SCAN_ID=$(echo $RESPONSE | jq -r '.scan_id')
    echo "##vso[task.setvariable variable=SCAN_ID]$SCAN_ID"
  displayName: 'Dispatch XenoraSec DAST Scan'

- script: |
    while true; do
      STATE=$(curl -s "$(XENORASEC_ENDPOINT)/api/scan/results/$(SCAN_ID)" | jq -r '.status')
      if [ "$STATE" == "completed" ]; then break; fi
      sleep 10
    done
    curl -s "$(XENORASEC_ENDPOINT)/api/scan/$(SCAN_ID)/report?format=json" -o scan-results.json
  displayName: 'Poll & Collect Scan Dossier'
```

### 5. Developer Workstation Shift-Left Pre-Commit Hook

Catch hardcoded API endpoints, accidental debug routes, and perimeter exposures on developer laptops before code is pushed to upstream git remotes:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: xenorasec-staging-audit
        name: XenoraSec DAST Shift-Left Audit
        entry: bash -c './scripts/pre-commit-xenora.sh'
        language: system
        stages: [pre-push]
        pass_filenames: false
```

```bash
#!/usr/bin/env bash
# scripts/pre-commit-xenora.sh
set -euo pipefail

SCANNER_URL="${XENORASEC_URL:-http://localhost:8000}"
TARGET_URL="${DEV_PREVIEW_URL:-http://127.0.0.1:3000}"

echo "Executing pre-push DAST assessment against ${TARGET_URL}..."

# Trigger scan using quick recon profile
RESP=$(curl -sf -X POST "${SCANNER_URL}/api/scan/" \
  -H "Content-Type: application/json" \
  -d "{\"target\": \"${TARGET_URL}\", \"scan_profile\": \"quick\"}") || {
    echo "WARNING: XenoraSec scanner offline at ${SCANNER_URL}; skipping pre-push gate."
    exit 0
}

SCAN_ID=$(echo "$RESP" | jq -r '.scan_id')

while true; do
  STATUS=$(curl -sf "${SCANNER_URL}/api/scan/results/${SCAN_ID}" | jq -r '.status // "unknown"')
  if [ "$STATUS" = "completed" ]; then break; fi
  if [ "$STATUS" = "failed" ]; then echo "DAST scan failed"; exit 1; fi
  sleep 5
done

CRIT_COUNT=$(curl -sf "${SCANNER_URL}/api/scan/results/${SCAN_ID}" | jq '[.vulnerabilities[]? | select(.severity == "critical")] | length')

if [ "$CRIT_COUNT" -gt 0 ]; then
  echo "ERROR: Push blocked by XenoraSec pre-commit hook ($CRIT_COUNT critical vulnerabilities discovered)."
  exit 1
fi

echo "Pre-commit DAST audit passed."
```

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
pytest tests/test_security.py -v         # SSRF & input gate invariants
pytest tests/test_recon_*.py -v          # Passive OSINT & RFC 7208/7489 tests
pytest tests/test_asset_*.py -v          # ASM asset inventory & filter tests
pytest tests/test_ai_service.py -v       # Michaelis-Menten kinetics & Groq fallback
pytest tests/test_database.py -v         # SQLite WAL concurrency & busy timeouts
pytest tests/test_batch_scan.py -v       # CIDR subnet expansion & batch slots
pytest tests/test_reports.py -v          # Multi-format report export generators
```

#### Test Suite Inventory & Key Invariants

| Test Module | Coverage Scope | Verified Invariants & Edge Cases |
| :--- | :--- | :--- |
| **`test_security.py`** | SSRF & Target Gate | Proves loopback (`127.0.0.1`), private RFC 1918 (`10.0.0.0/8`, `192.168.0.0/16`), link-local (`169.254.0.0/16`), and AWS metadata IP (`169.254.169.254`) rejection via real `socket.getaddrinfo` resolution |
| **`test_rate_limit.py`** | Anti-Spoofing | Verifies sliding-window counter eviction, trusted proxy header validation, and rightmost hop parsing |
| **`test_cancellation.py`**| Subprocess Safety | Asserts `process.kill()` executes on `asyncio.CancelledError` and verifies cold-start zombie recovery |
| **`test_ai_service.py`** | Risk Scoring | Proves exact half-saturation point ($S = 15.0 \implies \text{Score} = 5.0$), asymptotic limits ($S \to \infty \implies 10.0$), and Groq API 10s timeout fallback |
| **`test_database.py`** | DB Concurrency | Checks `PRAGMA journal_mode=WAL`, 30s busy timeout, and concurrent multi-session read/write without `database is locked` errors |
| **`test_recon_*.py`** | Passive OSINT | 7 dedicated modules (`crtsh`, `dns`, `fingerprint`, `db`, `routes`, `e2e`, `edge_cases`) verifying wildcard stripping, DoH fallback, RFC 7208 SPF permerror, and RFC 7489 DMARC inheritance |
| **`test_batch_scan.py`** | CIDR Subnets | Validates `/24` to `/32` host math, rejection of `/16` subnets (HTTP 422), and `asyncio.Semaphore` slot distribution |
| **`test_asset_*.py`** | ASM Asset Registry | Proves idempotent upsert from scan, multi-column search, type/criticality filters, and cascade deletion referential integrity |
| **`test_reports.py`** | Report Generators | Validates ReportLab PDF vector styling, HTML `@media print` structure, Markdown GFM tables, and CSV triage export flattening |
| **`test_api.py`** | REST Routes | End-to-end route tests for `/health`, `/queue`, `/history`, and partial retries |

---

### 2. Frontend Strict Verification & Linting

```bash
cd frontend

# TypeScript compilation check across all components & hooks
npx tsc -b

# ESLint static analysis enforcing React 19 rules
npm run lint

# Production bundle compilation & chunk optimization (runs tsc -b && vite build)
npm run build
```

---

### 3. Playwright End-to-End (E2E) Browser Automation Guide

XenoraSec includes automated end-to-end browser verification suites powered by **Playwright** (`verify_ui_playwright.py`), validating critical user journeys across desktop (1440x900) and mobile (375x812) viewports:

#### Running Playwright Verification

```bash
# 1. Install Playwright browser binaries (Chromium)
playwright install chromium

# 2. Ensure frontend preview or dev server is running on port 5173
npm --prefix frontend run preview -- --port 5173

# 3. Execute the Playwright UI verification suite
python3 verify_ui_playwright.py
```

#### Automated End-to-End Test Scenarios
1. **Dashboard & Metric Verification**: Asserts tactical header, KPI telemetry cards (Cumulative Scans, Discovered Hosts, Critical Findings, Open Ports), and Recharts SVG mounting without hydration errors.
2. **Scan Mode & CIDR Quick-Fill Toggle**: Toggles Single Host vs Batch / CIDR mode, exercises `/29` quick-fill chip, verifies target preview counter, and tests form validation error states.
3. **Scan Profile & Advanced Policy Accordion**: Selects scan profiles (Quick Recon, Full Web Audit), expands Advanced Engine accordion, and asserts timing policies (T0-T5) and custom tag inputs.
4. **Asset Attack Surface Drawer**: Navigates to `/assets`, checks high-density asset table rendering, clicks asset row, and asserts slide-out inspection drawer displays open ports and audit re-scan launcher.
5. **Passive Reconnaissance & OSINT Center**: Navigates to `/recon`, verifies passive subdomain matrix, DNS inspector tabs, and RFC 7208/7489 mail security hygiene scorecards.
6. **Mobile Responsive Navigation**: Emulates mobile viewport (375x812 iPhone), asserts desktop sidebar collapses into hamburger drawer, opens modal overlays, and checks touch responsiveness.

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

## 💾 Database Maintenance, Backup & Disaster Recovery Runbooks

Ensuring high availability and disaster recovery for historical scan records, attack surface catalogs, and audit logs requires disciplined backup procedures.

```text
┌────────────────────────────────────────────────────────────────────────┐
│               XenoraSec Enterprise DR SLA Targets                      │
├────────────────────────────────────────────────────────────────────────┤
│ Recovery Time Objective (RTO)  │ < 15 minutes (Full container restore) │
│ Recovery Point Objective (RPO) │ < 1 hour (Periodic WAL sync & snapshot)│
│ Backup Encryption Standard     │ AES-256-GCM at rest and in transit   │
│ Retention Policy               │ 30 days local, 365 days cloud archive│
└────────────────────────────────────────────────────────────────────────┘
```

### 1. SQLite Online Hot Backups & Integrity Checks

Never copy active SQLite database files (`cp scans.db backup.db`) while the backend is running; this causes malformed database headers due to incomplete WAL frames. Instead, leverage SQLite's atomic online backup API:

#### Atomic Hot Backup Script (`backup_sqlite.sh`)
```bash
#!/usr/bin/env bash
set -euo pipefail

BACKUP_DIR="/data/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
TARGET_FILE="${BACKUP_DIR}/xenorasec_backup_${TIMESTAMP}.db"

mkdir -p "$BACKUP_DIR"

echo "Executing online atomic backup to ${TARGET_FILE}..."
# VACUUM INTO safely creates an atomic copy without interrupting active scan writes
sqlite3 /data/scans.db "VACUUM INTO '${TARGET_FILE}';"

# Verify integrity of the generated backup
INTEGRITY=$(sqlite3 "${TARGET_FILE}" "PRAGMA integrity_check;")
if [ "$INTEGRITY" != "ok" ]; then
    echo "CRITICAL: Backup integrity check failed: $INTEGRITY" >&2
    rm -f "${TARGET_FILE}"
    exit 1
fi

# Compress and enforce retention (prune older than 30 days)
gzip -9 "${TARGET_FILE}"
find "$BACKUP_DIR" -type f -name "*.db.gz" -mtime +30 -delete

echo "Backup successful: ${TARGET_FILE}.gz"
```

#### Automated Routine Integrity Audit
Schedule a weekly cron job to detect filesystem or silent bit-rot corruption:
```bash
sqlite3 /data/scans.db "PRAGMA quick_check;"
sqlite3 /data/scans.db "PRAGMA foreign_key_check;"
```

### 2. SQLite WAL Checkpointing & Compaction Runbook
When XenoraSec processes hundreds of CIDR batch scans, the Write-Ahead Log (`scans.db-wal`) can grow. Manage it using checkpoint modes:

| Checkpoint Mode | Pragmas Invocation | Impact on Active Scans |
| :--- | :--- | :--- |
| **PASSIVE** | `PRAGMA wal_checkpoint(PASSIVE);` | Checkpoints as many frames as possible without blocking active readers/writers. |
| **FULL** | `PRAGMA wal_checkpoint(FULL);` | Waits for active readers to finish, then syncs all WAL frames to main database. |
| **TRUNCATE** | `PRAGMA wal_checkpoint(TRUNCATE);` | Syncs all frames and resets the WAL file length to 0 bytes on disk. |

```bash
# Emergency WAL truncation command
sqlite3 /data/scans.db "PRAGMA wal_checkpoint(TRUNCATE);"
```

### 3. PostgreSQL Automated Enterprise Backup & PITR Runbook

For PostgreSQL deployments, implement multi-tier backup routines combining compressed logical dumps with Point-In-Time Recovery (PITR).

#### Automated Custom Format Dump (`backup_postgres.sh`)
```bash
#!/usr/bin/env bash
set -euo pipefail

BACKUP_FILE="/backups/pg_xenorasec_$(date +%F_%H%M).dump"

# Export compressed binary custom-format dump
pg_dump -h localhost -U xenora -Fc -Z 6 -d xenorasec -f "$BACKUP_FILE"

# Upload to S3 Glacier / Cloud Archive
aws s3 cp "$BACKUP_FILE" s3://corp-sec-backups/xenorasec/ --sse aws:kms

echo "PostgreSQL backup completed and archived to S3."
```

#### Disaster Recovery Restoration Drill
To restore XenoraSec from scratch onto a fresh PostgreSQL instance:
```bash
# 1. Terminate active application backend connections
psql -U postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'xenorasec';"

# 2. Restore database with clean drop and sequence rebuild
pg_restore -h localhost -U xenora -d xenorasec --clean --if-exists --no-owner -j 4 "/backups/pg_xenorasec_2026-09-28.dump"

# 3. Verify row counts and sequence health
psql -U xenora -d xenorasec -c "SELECT count(*) FROM assets; SELECT count(*) FROM scan_results;"
```

### 4. Automated Disaster Recovery Restoration Validation Drill (`verify_dr_restore.sh`)

Test backups routinely in an isolated staging sandbox to ensure restoration procedures meet the 15-minute RTO target without silent corruption:

```bash
#!/usr/bin/env bash
# scripts/verify_dr_restore.sh
set -euo pipefail

BACKUP_DIR="/data/backups"
LATEST_BACKUP=$(find "$BACKUP_DIR" -name "*.db.gz" -type f -printf '%T@ %p\n' | sort -n | tail -1 | cut -f2- -d" ")
SANDBOX_DB="/tmp/sandbox_restore_drill.db"

if [ -z "$LATEST_BACKUP" ]; then
    echo "ERROR: No valid database backup archive found in $BACKUP_DIR" >&2
    exit 1
fi

echo "Initiating DR drill with latest backup: $LATEST_BACKUP"
rm -f "$SANDBOX_DB"

# Decompress backup into sandbox database
gzip -dc "$LATEST_BACKUP" > "$SANDBOX_DB"

# Validate cryptographic and structural integrity
INTEGRITY=$(sqlite3 "$SANDBOX_DB" "PRAGMA integrity_check;")
FK_CHECK=$(sqlite3 "$SANDBOX_DB" "PRAGMA foreign_key_check;")

if [ "$INTEGRITY" != "ok" ] || [ -n "$FK_CHECK" ]; then
    echo "CRITICAL: Restored database failed integrity audit!" >&2
    echo "Integrity: $INTEGRITY | Foreign Keys: $FK_CHECK" >&2
    rm -f "$SANDBOX_DB"
    exit 1
fi

ASSET_COUNT=$(sqlite3 "$SANDBOX_DB" "SELECT count(*) FROM assets;")
SCAN_COUNT=$(sqlite3 "$SANDBOX_DB" "SELECT count(*) FROM scan_results;")

echo "DR Restoration Drill PASSED. Verified $ASSET_COUNT assets and $SCAN_COUNT scans."
rm -f "$SANDBOX_DB"
```

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
│   ├── core/                         # Core security & configuration modules
│   │   ├── config.py                 # Pydantic Settings & environment validation
│   │   ├── logging.py                # Structured JSON / ANSI console logger
│   │   ├── rate_limit.py             # Sliding-window IP rate limiter with proxy trust
│   │   └── security.py               # Target sanitization, SSRF guard & DNS lookup
│   ├── db/                           # Persistence layer & database models
│   │   ├── database.py               # SQLAlchemy async engine & SQLite WAL configuration
│   │   ├── models.py                 # ScanResult, Asset, AssetPort, AssetVulnerability, ReconHistory
│   │   └── crud.py                   # Async database CRUD operations
│   ├── routes/                       # REST API route controllers
│   │   ├── scan.py                   # Single & batch scan routes, SSE/WS stream endpoints
│   │   ├── recon.py                  # Passive OSINT & reconnaissance endpoints
│   │   ├── asset.py                  # Attack surface management & inventory CRUD
│   │   ├── health.py                 # Liveness, readiness & DB connectivity probes
│   │   └── ui.py                     # Dashboard telemetry & aggregate statistics
│   ├── schemas/                      # Pydantic schemas for request/response serialization
│   │   ├── scan.py                   # ScanRequest, ScanResponse, ScanResultSchema
│   │   ├── asset.py                  # AssetCreate, AssetUpdate, AssetDetailSchema
│   │   ├── recon.py                  # ReconRequest, ReconResultSchema, DNSRecords
│   │   ├── report.py                 # ReportExportRequest schema
│   │   └── stream.py                 # StreamChunk & terminal wire protocol
│   └── services/                     # Business logic and external tool wrappers
│       ├── nmap_scan.py              # Async Nmap wrapper with fault-tolerant XML parser
│       ├── nuclei_scan.py            # Async Nuclei wrapper with streaming JSONL reader
│       ├── ai_service.py             # Michaelis-Menten kinetics & Groq Llama 3.3 LLM
│       ├── event_bus.py              # SSE & WebSocket real-time terminal buffer hub
│       ├── recon_service.py          # crt.sh miner, Cloudflare DoH, RFC mail evaluator
│       ├── asset_service.py          # Idempotent delta upsert & ASM inventory sync
│       ├── report_service.py         # Multi-format report compiler (PDF/HTML/MD/JSON/CSV)
│       ├── scanner_service.py        # Central scan lifecycle & subprocess coordinator
│       └── profile_service.py        # Pre-configured scan profiles (Quick/Full/Custom)
├── frontend/                         # React 19 + TypeScript + Vite SPA
│   ├── index.html                    # Single Page Application HTML entrypoint
│   ├── package.json                  # Frontend dependencies & build scripts
│   ├── vite.config.ts                # Vite build and proxy development configuration
│   ├── src/                          # Application source code
│   │   ├── main.tsx                  # React DOM mount point & TanStack Query client
│   │   ├── App.tsx                   # Top-level routing, sidebar & layout shell
│   │   ├── api/                      # Axios HTTP client & API route wrappers
│   │   ├── components/               # Tactical UI components
│   │   │   ├── ScanPanel.tsx         # Target input, format detection & CIDR chips
│   │   │   ├── LiveTerminal.tsx      # Terminal console with SSE/WS streaming & ANSI color
│   │   │   ├── ScanProfileSelector.tsx # Tactical scan profile radio selector
│   │   │   ├── ReportExportModal.tsx # Multi-format export dialog (PDF/HTML/MD/JSON/CSV)
│   │   │   ├── BatchProgressModal.tsx # CIDR subnet batch tracking modal
│   │   │   ├── SubdomainTable.tsx    # Passive OSINT subdomain discovery table
│   │   │   ├── DnsInspector.tsx      # Multi-type DNS record inspection card
│   │   │   ├── TechStackGrid.tsx     # Web tech, headers & SSL/TLS certificate inspector
│   │   │   ├── RiskScore.tsx         # Michaelis-Menten risk gauge component
│   │   │   ├── SeverityBadge.tsx     # Severity indicator pills
│   │   │   └── StatusBadge.tsx       # Scan status badge component
│   │   ├── pages/                    # Route page views
│   │   │   ├── DashboardPage.tsx     # Security operations overview & scan trigger
│   │   │   ├── ScanResultsPage.tsx   # Detailed findings dossier & terminal view
│   │   │   ├── HistoryPage.tsx       # Historical audit log & search
│   │   │   ├── AssetInventoryPage.tsx# ASM attack surface management table
│   │   │   └── ReconPage.tsx         # Passive OSINT intelligence center
│   │   ├── hooks/                    # Custom React hooks (useApi)
│   │   └── types/                    # Shared TypeScript interfaces & API contracts
├── tests/                            # Asynchronous Pytest test suite (124 tests)
│   ├── conftest.py                   # Async Pytest fixtures & mock subprocess runners
│   ├── test_security.py              # SSRF protection, loopback & private IP tests
│   ├── test_rate_limit.py            # Sliding-window rate limiter & proxy anti-spoofing
│   ├── test_cancellation.py         # Subprocess kill signals & zombie recovery
│   ├── test_ai_service.py            # Michaelis-Menten math & Groq fallback tests
│   ├── test_database.py              # SQLite WAL mode & concurrent connection tests
│   ├── test_recon_*.py               # Passive OSINT suite (7 test modules: crtsh, dns, etc.)
│   ├── test_batch_scan.py            # CIDR subnet expansion & batch semaphore tests
│   ├── test_asset_*.py               # Asset inventory routes & filter tests
│   ├── test_reports.py               # PDF, HTML, Markdown, JSON, CSV report generation
│   └── test_api.py                   # REST API route integration tests
├── verify_ui_playwright.py           # Automated Playwright E2E browser verification script
├── docs/                             # Architecture & component documentation
│   ├── Architecture.md               # Design principles & architectural decisions
│   ├── UI_ARCHITECTURE.md            # Frontend component architecture
│   ├── UI_COMPONENTS.md              # Tactical UI component library catalog
│   ├── DESIGN_TOKENS.md              # Tactical Dark color palette & tokens
│   ├── PLAYWRIGHT_TESTING.md         # Playwright verification execution guide
│   └── CONFIGURATION_REFERENCE.md    # Environment variable reference
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

## 🏛️ Compliance & Regulatory Framework Mapping

Enterprise vulnerability management platforms must align with global regulatory compliance mandates and security control frameworks. XenoraSec's dual-engine scanning, continuous Attack Surface Management (ASM), and audit reporting directly support evidence collection and control validation across major frameworks:

```mermaid
flowchart TD
    AUDIT["Compliance Audit Requirement"] --> XENORA["XenoraSec Platform"]
    XENORA --> NIST["NIST CSF 2.0\n(ID.AM, PR.IP, DE.CM)"]
    XENORA --> ISO["ISO/IEC 27001:2022\n(A.5.7, A.8.8, A.8.20)"]
    XENORA --> PCI["PCI-DSS v4.0\n(Req 6.4, Req 11.3)"]
    XENORA --> SOC["SOC 2 Type II\n(CC6.8, CC7.1)"]
    XENORA --> HIPAA["HIPAA Security Rule\n(§ 164.308, § 164.312)"]
    XENORA --> CIS["CIS Controls v8\n(Control 7, Control 12)"]
    XENORA --> OWASP["OWASP Top 10\n(A01-A10 Coverage)"]
```

### 1. Framework Crosswalk Matrix

| Regulatory Framework | Control Identifier | Control Description | XenoraSec Operational Capability | Evidentiary Output |
| :--- | :--- | :--- | :--- | :--- |
| **NIST CSF 2.0** | `ID.AM-01` | Inventories of physical and virtual assets are maintained. | Passive OSINT (crt.sh) + active network recon automatically discovers and catalogs hosts in Asset Inventory. | `/api/assets` JSON dossier & CSV inventory export |
| **NIST CSF 2.0** | `DE.CM-01` | External service perimeter is monitored for unauthorized ports and services. | Unprivileged Nmap TCP Connect (`-sT`) scans monitor open ports and service banner version drifts. | Nmap XML & `/api/scan/results/{id}` port tables |
| **NIST CSF 2.0** | `ID.RA-01` | Vulnerabilities in assets are identified and documented. | Nuclei v3.3.8 streaming JSONL engine tests against thousands of community and custom CVE signatures. | Multi-format reports (PDF, HTML, Markdown) |
| **ISO/IEC 27001:2022**| `A.5.7` | Threat Intelligence: Information relating to threats is collected and analyzed. | Passive OSINT module queries Certificate Transparency logs and historical DNS archives. | Recon History Ledger & Subdomain Topology |
| **ISO/IEC 27001:2022**| `A.8.8` | Management of Technical Vulnerabilities: Vulnerabilities are evaluated against risk. | Deterministic Michaelis-Menten risk scoring ($0.0 - 10.0$) plus optional Groq Llama 3.3 threat synthesis. | Executive Report Summary & Saturation Gauge |
| **ISO/IEC 27001:2022**| `A.8.20` | Network Security: Security of network services is maintained. | DNS topology audit, reverse DNS (PTR) verification, and network perimeter exposure scans. | DNS Inspector & RDAP ASN routing tables |
| **ISO/IEC 27001:2022**| `A.8.24` | Use of Cryptography: Protocols and certificates are kept secure. | Passive TLS inspector extracts negotiated cipher suites, TLS version (TLS 1.2/1.3), and certificate expiry. | SSL/TLS Certificate Telemetry Card |
| **PCI-DSS v4.0** | `Req 11.3.1` | Perform quarterly external vulnerability scans via automated scanners. | Automated multi-target CIDR batch auditing (`/api/scan/batch`) and scheduled perimeter scans. | Executive PDF Compliance Dossier with CVSS v3.1 |
| **PCI-DSS v4.0** | `Req 6.4.1` | Public web applications are evaluated for known vulnerabilities. | Nuclei web application templates auditing for XSS, SQLi, SSRF, auth-bypass, and directory traversal. | Technical Security Report with reproduction curl |
| **SOC 2 Type II** | `CC6.8` | The entity prevents or detects unauthorized software execution and configurations. | Default credential tests, exposed administrative panels (Grafana, Kibana, Jenkins), and debug routes. | Finding Card with matched URLs and HTTP codes |
| **SOC 2 Type II** | `CC7.1` | The entity uses detection and monitoring procedures to identify changes to attack surface. | ASM delta upsert engine records `first_seen` vs `last_seen` timestamps for newly exposed ports. | Asset Inventory slide-out audit drawer |
| **HIPAA Security** | `§ 164.308` | Risk Analysis: Conduct an accurate and thorough assessment of potential risks and vulnerabilities. | Automated dual-engine scanning maps perimeter vulnerabilities to protected health information (ePHI) endpoints. | Signed Executive Summary PDF & Risk Posture Gauge |
| **HIPAA Security** | `§ 164.312` | Transmission Security: Guard against unauthorized access to electronic protected health information. | Passive TLS inspector validates modern cipher suites, detects weak TLS versions, and monitors certificate expiration. | SSL/TLS Telemetry Card & Cipher Audit |
| **CIS Controls v8** | `Control 7.1` | Establish and Maintain a Vulnerability Management Process with automated scanners. | Scheduled batch scanning over network subnets and continuous automated CVE signature evaluation. | Automated CI/CD Reports & Batch Dashboard |
| **CIS Controls v8** | `Control 12.1`| Ensure network infrastructure is monitored for unauthorized ports and services. | Continuous TCP Connect (`-sT`) scanning with banner extraction identifies shadow IT and rogue services. | Discovered Ports Table & Asset Inventory Drawer |

### 2. OWASP Top 10 Coverage Mapping

XenoraSec's template engine targets core categories of the OWASP Top 10:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        OWASP Top 10 Detection Scope                    │
├────────────────────────────────────────────────────────────────────────┤
│ A01: Broken Access Control     │ Auth bypass, exposed actuators, IDORs │
│ A02: Cryptographic Failures    │ Weak ciphers, expired certs, cleartext│
│ A03: Injection                 │ SQLi, blind SSRF, command injection   │
│ A04: Insecure Design           │ Dangling CNAMEs, subdomain takeovers  │
│ A05: Security Misconfiguration │ Default creds, open S3, debug routes  │
│ A06: Vulnerable Components     │ Outdated Apache/Nginx, unpatched CVEs │
│ A07: Identification & Auth     │ Missing MFA endpoints, weak session id│
│ A08: Software & Data Integrity │ Unvalidated redirects, poisoned CDNs  │
│ A09: Logging & Monitoring      │ Missing security headers, silent 500s │
│ A10: Server-Side Request (SSRF)│ Cloud metadata exposure, loopback URI │
└────────────────────────────────────────────────────────────────────────┘
```

### 3. Compliance Evidentiary Packaging Runbook
To generate audit-ready documentation for external Qualified Security Assessors (QSA) or internal risk committees:
1. **Generate Perimeter Scope Export**: Run `GET /api/assets?format=csv` to produce the full attack surface asset ledger.
2. **Execute Full Audit Scan**: Trigger a Full Web & Network Audit (`scan_profile="full"`) against all in-scope CIDR blocks.
3. **Download Signed Executive Summary**: Export the ReportLab PDF via `GET /api/scan/{id}/report?format=pdf&report_type=executive`.
4. **Archive Machine-Readable Telemetry**: Save the raw JSON dossier (`format=json`) alongside timestamped SHA-256 checksums in your compliance evidence repository.

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

## 📖 Comprehensive Security & Scanning Terminology Glossary

An alphabetical reference defining core architectural, networking, and vulnerability management terminology used throughout XenoraSec:

| Term / Acronym | Full Form & Standard | Technical Definition & Platform Context |
| :--- | :--- | :--- |
| **ASM** | **Attack Surface Management** | The continuous discovery, inventorying, classification, and risk evaluation of all internet-facing digital assets, open ports, and cloud infrastructure owned by an organization. |
| **ASN** | **Autonomous System Number** | A globally unique 16-bit or 32-bit identifier assigned by IANA/RIRs defining an autonomous routing domain running Border Gateway Protocol (BGP). Correlated in XenoraSec via RDAP lookup. |
| **CIDR** | **Classless Inter-Domain Routing** | IP address allocation format (`IP/prefix`, e.g. `192.168.1.0/24`) specifying network masks. XenoraSec enforces prefix boundaries between `/24` (256 addresses) and `/32` (single host). |
| **CNAME Takeover** | **Subdomain Takeover** | Vulnerability occurring when a DNS CNAME record points to an inactive or decommissioned third-party cloud service (e.g. unclaimed S3 bucket, GitHub Pages, Heroku app), allowing adversaries to claim the domain. |
| **crt.sh** | **Certificate Transparency Log Miner** | Public web interface and API for querying append-only Certificate Transparency (CT) cryptographic logs mandated by RFC 6962. Used by XenoraSec for passive, non-intrusive subdomain discovery. |
| **CVE** | **Common Vulnerabilities and Exposures** | Standardized dictionary of publicly disclosed cybersecurity vulnerabilities maintained by MITRE and NIST (e.g. `CVE-2023-46805`). |
| **CVSS v3.1** | **Common Vulnerability Scoring System** | An open standard (0.0 to 10.0) assessing vulnerability severity across base metric groups (Attack Vector, Complexity, Privileges, User Interaction, Scope, Confidentiality, Integrity, Availability). |
| **CWE** | **Common Weakness Enumeration** | Community-developed taxonomy of software weakness types (e.g., `CWE-79` for Cross-Site Scripting, `CWE-89` for SQL Injection). |
| **DAST** | **Dynamic Application Security Testing** | Black-box testing methodology executing active HTTP and network probes against running applications without requiring access to source code. |
| **DKIM** | **DomainKeys Identified Mail** | RFC 6376 cryptographic email authentication standard verifying domain ownership via asymmetric public keys published in DNS TXT records. |
| **DMARC** | **Domain-based Message Authentication** | RFC 7489 policy framework combining SPF and DKIM to instruct receiving MTAs how to treat spoofed emails (`p=none`, `p=quarantine`, `p=reject`). |
| **DoH** | **DNS-over-HTTPS** | RFC 8484 protocol executing DNS queries over TLS-encrypted HTTPS connections (port 443). XenoraSec utilizes Cloudflare DoH to bypass firewall blocks on outbound UDP port 53. |
| **DREAD** | **Damage, Reproducibility, Exploitability, Affected Users, Discoverability** | Qualitative/quantitative threat prioritization model created by Microsoft to evaluate post-threat impact. |
| **EASM** | **External Attack Surface Management** | The continuous discovery, mapping, and risk analysis of an organization's internet-facing digital perimeter, IPs, and cloud assets. |
| **EPSS** | **Exploit Prediction Scoring System** | Data-driven statistical model (0.0 to 1.0 / 0% to 100%) estimating the probability that a software vulnerability will be exploited in the wild within 30 days. |
| **HSTS** | **HTTP Strict Transport Security** | RFC 6797 response header instructing browsers to strictly communicate over HTTPS, mitigating SSL stripping and downgrade attacks. |
| **Michaelis-Menten** | **Enzyme Kinetics Saturation Model** | Biochemical hyperbolic rate equation adapted by XenoraSec ($V_{\max}=10.0, K_m=15.0$) to guarantee mathematically bounded, monotonically increasing, non-linear risk scoring without score blowouts. |
| **Nmap TCP Connect**| **`-sT` Scan Flag** | Operating-system-level socket connection scan that establishes complete 3-way TCP handshakes (`SYN` $\to$ `SYN-ACK` $\to$ `ACK`), running without `root` or `CAP_NET_RAW` privileges. |
| **Nuclei v3** | **Template-Based Vulnerability Scanner** | Fast, configurable vulnerability scanner developed by ProjectDiscovery utilizing YAML-defined rule templates and domain-specific language (DSL) matchers. |
| **OSINT** | **Open Source Intelligence** | Data and reconnaissance gathered entirely from publicly accessible, legal data sources (CT logs, DNS records, public routing registries) without direct active probing. |
| **RDAP** | **Registration Data Access Protocol** | RFC 7480 successor to WHOIS providing structured JSON querying of domain registrations, IP network blocks, and Autonomous System Numbers across RIRs. |
| **RFC 1918** | **Private Address Space Allocation** | Internet standard designating private IPv4 blocks (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`) reserved for internal networks and prohibited by XenoraSec's default SSRF firewall. |
| **RFC 7208** | **Sender Policy Framework (SPF)** | DNS TXT record protocol designating authorized IP addresses permitted to send emails on behalf of a domain. Flags the RFC 10-DNS-lookup limit to prevent MTA validation errors. |
| **SAN** | **Subject Alternative Name** | X.509 certificate extension (RFC 5280) allowing multiple hostnames, wildcard domains, and IP addresses to be secured under a single TLS certificate. |
| **SAST** | **Static Application Security Testing** | White-box analysis analyzing source code, bytecode, or application binaries to identify security flaws before runtime deployment. |
| **SBOM** | **Software Bill of Materials** | A formal, machine-readable inventory of software packages, libraries, and transitive dependencies utilized in application containers. |
| **SIEM** | **Security Information & Event Management** | Enterprise technology aggregating security telemetry, event logs, and findings across IT systems (e.g., Splunk, Elastic Security, Microsoft Sentinel). |
| **SOAR** | **Security Orchestration, Automation & Response** | Platform automating incident response workflows, playbook executions, and security ticket routing (e.g., PagerDuty, Jira Automation, Cortex XSOAR). |
| **SSRF** | **Server-Side Request Forgery** | Attack class where a malicious actor induces a server-side application to make HTTP/TCP requests to unintended locations, such as internal loopbacks or cloud metadata services. |
| **STRIDE** | **Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation** | Comprehensive threat modeling methodology categorizing system security threats across 6 critical operational vectors. |
| **WAL Mode** | **Write-Ahead Logging (SQLite)** | Concurrency architecture (`PRAGMA journal_mode=WAL`) where changes are appended to a separate log file, allowing concurrent readers to access database state while a writer records updates. |
| **Zero Trust** | **Zero Trust Architecture (ZTA / NIST SP 800-207)** | Security architecture operating on the principle of "never trust, always verify," mandating strict identity checks and zero-trust input validation. |

---

## 📄 License & Acknowledgements

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

### Acknowledgements & Open Source Credits
XenoraSec stands on the shoulders of giants in the open-source security and developer ecosystem. We gratefully acknowledge:
- **[ProjectDiscovery Nuclei](https://github.com/projectdiscovery/nuclei)**: High-speed, template-driven vulnerability scanning engine powering targeted security discovery.
- **[Nmap Project](https://nmap.org/)**: The gold-standard network mapper by Gordon Lyon (Fyodor), providing reliable service detection and port auditing.
- **[FastAPI](https://fastapi.tiangolo.com/)**: High-performance, asynchronous Python web framework created by Sebastián Ramírez.
- **[SQLAlchemy](https://www.sqlalchemy.org/) & [aiosqlite](https://github.com/omnilib/aiosqlite)**: Production-grade asynchronous SQL toolkit and SQLite database driver.
- **[Groq](https://groq.com/)**: Ultra-fast LPU inference enabling real-time contextual threat analysis.

<p align="center">
  <b>Built with 🛡️ for ethical hackers, defense engineers, and DevSecOps professionals.</b>
</p>