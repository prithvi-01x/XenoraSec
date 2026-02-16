# AI Vulnerability Scanner - Full Stack

A professional, SaaS-level AI-powered vulnerability scanner. This project combines a high-performance **FastAPI** backend with a modern **React + Vite** frontend to provide a comprehensive security scanning solution.

## 🚀 Overview

This application allows users to perform security scans on targets (IPs, domains, or URLs). It orchestrates industry-standard tools and uses AI to provide intelligent risk analysis and scoring.

### Key Components:
- **FastAPI Backend**: Orchestrates Nmap, Nuclei, and AI analysis.
- **React Frontend**: A stunning, responsive dashboard built with Vite, Tailwind CSS, and Chart.js.
- **AI Risk Analysis**: Intelligent scoring based on scan findings.
- **SQLite/PostgreSQL**: Reliable storage for scan history and results.

---

## ✨ Features

### 🛡️ Security Scanning
- **Nmap Integration**: Comprehensive port scanning and service detection.
- **Nuclei Integration**: Advanced vulnerability detection using templates.
- **AI Risk Scoring**: Automated analysis of findings to determine overall risk levels.
- **Target Validation**: Sanitization and validation to prevent misuse.
- **Private IP Protection**: Configurable blocking of private/internal network scanning.

### 🖥️ Modern Dashboard
- **Real-time Monitoring**: Track active scans and their progress.
- **Interactive Visualizations**: Beautiful charts for risk distribution and scan trends.
- **Detailed Reports**: In-depth view of findings, metadata, and AI-generated insights.
- **Scan History**: Searchable and paginated history of all past scans.
- **Dark Mode UI**: Sleek, professional aesthetic for security analysts.

### ⚙️ Architecture & Reliability
- **Unified Status Lifecycle**: Consistent scan states (pending, running, completed, failed, etc.).
- **Concurrency Control**: Semaphore-based limits to prevent server overload.
- **Rate Limiting**: Protect the API from abuse.
- **Structured Logging**: Production-ready logging for debugging and monitoring.
- **Async Safety**: Fully asynchronous backend for high performance.

---

## 📁 Project Structure

```text
vuln-gui/
├── app/                  # FastAPI Backend
│   ├── core/             # Configuration, Logging, Security
│   ├── db/               # Database Models & CRUD operations
│   ├── routes/           # API Endpoints
│   ├── schemas/          # Pydantic Data Models
│   ├── services/         # Scanner & AI Business Logic
│   └── main.py           # Backend Entry Point
├── frontend/             # React + Vite Frontend
│   ├── src/              # Source code (Components, Pages, Services)
│   ├── public/           # Static assets
│   └── index.html        # Entry HTML
├── requirements.txt      # Python Dependencies
├── .env                  # Environment Variables (Backend)
└── scans.db              # SQLite Database (Auto-generated)
```

---

## 🛠️ Installation & Setup

### Prerequisites
- **Python 3.10+**
- **Node.js 18+**
- **Nmap**: `sudo apt-get install nmap`
- **Nuclei**: [Install Guide](https://github.com/projectdiscovery/nuclei#installation)

### 1. Backend Setup
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env  # If .env.example exists, otherwise create .env
```

### 2. Frontend Setup
```bash
cd frontend
npm install
```

---

## 🚀 Running the Application

### Start Backend
From the root directory:
```bash
python main.py
# Or using uvicorn directly
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
The API will be available at `http://localhost:8000`.

### Start Frontend
From the `frontend` directory:
```bash
npm run dev
```
The dashboard will be available at `http://localhost:5173`.

---

## ⚙️ Configuration

The backend is configured via environment variables in the `.env` file:

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite+aiosqlite:///./scans.db` | DB connection string |
| `MAX_CONCURRENT_SCANS` | `3` | Max parallel scans |
| `GLOBAL_SCAN_TIMEOUT` | `600` | Total scan timeout (seconds) |
| `ALLOW_PRIVATE_IP_SCANNING` | `False` | Security toggle for internal IPs |
| `GROQ_API_KEY` | `your_key` | Required for AI Risk Analysis |

---

## 📊 Risk Scoring Algorithm

Findings are weighted based on severity:
- **Critical**: 5.0
- **High**: 3.0
- **Medium**: 2.0
- **Low**: 1.0

**Formula:**
`base_score = Σ(severity_wait) + (open_ports * 0.05)`
`normalized_score = 10 * (base_score / (base_score + 15))`

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.