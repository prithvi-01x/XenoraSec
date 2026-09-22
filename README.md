# 🛡️ XenoraSec - Advanced Vulnerability Scanner

> **Next-Generation Autonomous Security Assessment & Threat Surface Discovery Engine**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg?logo=react&logoColor=black)](https://reactjs.org/)
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
- [AI Risk Scoring Model](#-ai-risk-scoring-model)
- [Security & Defensive Safeguards](#-security--defensive-safeguards)
- [Database Architecture](#-database-architecture)
- [REST API Reference](#-rest-api-reference)
- [Environment Configuration](#-environment-configuration)
- [Installation & Quick Start](#-quick-start)
- [Production Deployment](#-production-deployment)
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

### 🏗️ Architecture
```mermaid
graph LR
    U[User] --> F[React Frontend]
    F <-->|REST API| B[FastAPI Backend]
    B -->|Schema| D[(Database)]
    B -->|Async| S{Scanners}
    S --> N[Nmap]
    S --> V[Nuclei]
    S --> A[AI Risk Analysis]
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

- **🛡️ Security Scanning**: Nmap & Nuclei integration with AI risk scoring
- **🖥️ Modern Dashboard**: Real-time progress, interactive charts, dark mode
- **⚙️ Reliability**: Async-first design, rate limiting, health checks
- **🔒 Security**: Input validation, CORS protection and also private IP blocking

---

## 🚀 Quick Start

**Prerequisites**: Python 3.10+, Node.js 18+, Nmap, Nuclei.

```bash
# 1. Clone & Setup
git clone https://github.com/prithvi-01x/XenoraSec.git
cd xenorasec
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 2. Setup Frontend
cd frontend && npm install && cd ..

# 3. Configure
cp .env.example .env

# 4. Run
# Terminal 1: Backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
# Terminal 2: Frontend
cd frontend && npm run dev
```

Visit **http://localhost:5173** to start scanning.
Detailed guide: **[QUICKSTART.md](QUICKSTART.md)**.

---

## 📚 Documentation & API

- **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Architecture**: **[Architecture.md](Architecture.md)** (Design & Deployment)
- **Testing**: **[TESTING_GUIDE.md](TESTING_GUIDE.md)**
- **Changelog**: **[changelog.md](changelog.md)**

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

## 🤝 Contributing & License

Contributions are welcome! Please fork and submit a PR.
This project is licensed under the **MIT License**.

**Built with ❤️ for security professionals**