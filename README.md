# 🛡️ XenoraSec - Advanced Vulnerability Scanner

A professional, production-ready AI-powered vulnerability scanner with a modern web interface. This project combines a high-performance **FastAPI** backend with a sleek **React + Vite** frontend to provide comprehensive security scanning capabilities.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5+-3178C6.svg)](https://www.typescriptlang.org/)

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Running the Application](#-running-the-application)
- [API Documentation](#-api-documentation)
- [Project Structure](#-project-structure)
- [Security](#-security)
- [Troubleshooting](#-troubleshooting)
- [Production Deployment](#-production-deployment)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🚀 Overview

This application performs comprehensive security scans on targets (domains, IPs, or URLs) by orchestrating industry-standard tools like **Nmap** and **Nuclei**, then uses AI-powered analysis to provide intelligent risk scoring and actionable insights.

### Key Components

- **FastAPI Backend**: Async Python backend orchestrating security tools
- **React Frontend**: Modern, responsive SPA with real-time updates
- **AI Risk Analysis**: Intelligent scoring based on vulnerability severity and CVSS
- **Database**: SQLite (development) / PostgreSQL (production)
- **Security Tools**: Nmap for port scanning, Nuclei for vulnerability detection

---

## ✨ Features

### 🛡️ Security Scanning

- **Nmap Integration**: Comprehensive port scanning and service detection
- **Nuclei Integration**: Advanced vulnerability detection using 1000+ templates
- **AI Risk Scoring**: Automated analysis with severity-weighted scoring
- **Target Validation**: Input sanitization and security controls
- **Private IP Protection**: Configurable blocking of internal network scanning
- **Localhost Protection**: Optional localhost scanning restrictions
- **Rate Limiting**: API protection against abuse (10 req/min, 100 req/hour)

### 🖥️ Modern Dashboard

- **Real-time Monitoring**: Track active scans with live progress updates
- **Interactive Visualizations**: Beautiful charts using Chart.js
- **Detailed Reports**: In-depth vulnerability findings with metadata
- **Scan History**: Searchable, filterable, paginated history
- **Dark Mode UI**: Professional aesthetic optimized for security analysts
- **Responsive Design**: Works on desktop, tablet, and mobile

### ⚙️ Architecture & Reliability

- **Async-First Design**: Fully asynchronous for high performance
- **Concurrency Control**: Semaphore-based limits (default: 3 concurrent scans)
- **Unified Status Lifecycle**: Consistent states (running, completed, failed, partial, timeout)
- **Structured Logging**: Production-ready JSON logging
- **Error Recovery**: XML parsing fallback for partial results
- **Health Checks**: Kubernetes-ready liveness and readiness probes
- **Type Safety**: Pydantic models for request/response validation

---

## 🏗️ Architecture

```
┌─────────────┐      HTTP/REST      ┌──────────────┐
│   React     │ ←─────────────────→ │   FastAPI    │
│  Frontend   │      (CORS)         │   Backend    │
└─────────────┘                     └──────────────┘
                                           │
                                           ├─→ Nmap (Port Scanning)
                                           ├─→ Nuclei (Vuln Detection)
                                           ├─→ AI Service (Risk Scoring)
                                           └─→ Database (SQLite/PostgreSQL)
```

**Tech Stack:**
- **Backend**: Python 3.10+, FastAPI, SQLAlchemy (async), Pydantic
- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, Chart.js
- **Database**: SQLite (dev), PostgreSQL (prod) with asyncpg
- **Tools**: Nmap, Nuclei

---

## 📦 Prerequisites

Before you begin, ensure you have the following installed:

### Required

1. **Python 3.10 or higher**
   ```bash
   python3 --version  # Should be 3.10+
   ```

2. **Node.js 18 or higher**
   ```bash
   node --version  # Should be 18+
   npm --version
   ```

3. **Nmap** (Network Scanner)
   ```bash
   # Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install nmap
   
   # macOS
   brew install nmap
   
   # Verify installation
   nmap --version
   ```

4. **Nuclei** (Vulnerability Scanner)
   ```bash
   # Using Go
   go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
   
   # Or download binary from releases
   # https://github.com/projectdiscovery/nuclei/releases
   
   # Verify installation
   nuclei -version
   
   # Update templates (recommended)
   nuclei -update-templates
   ```

### Optional

- **PostgreSQL** (for production)
- **Git** (for cloning the repository)

---

## 🔧 Installation

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd xenorasec
```

### Step 2: Backend Setup

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep -E "fastapi|sqlalchemy|asyncpg"
```

### Step 3: Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install Node.js dependencies
npm install

# Return to root directory
cd ..
```

### Step 4: Environment Configuration

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your preferred settings
nano .env  # or use your favorite editor
```

**Minimum required configuration:**

```bash
# .env
APP_NAME="XenoraSec"
DEBUG=True

# Database (SQLite for development)
DATABASE_URL="sqlite+aiosqlite:///./scans.db"

# Security
ALLOW_LOCALHOST_SCANNING=True
ALLOW_PRIVATE_IP_SCANNING=False

# Rate Limiting
RATE_LIMIT_ENABLED=True
RATE_LIMIT_PER_MINUTE=10

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=structured
```

---

## ⚙️ Configuration

### Backend Configuration (.env)

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_NAME` | "XenoraSec" | Application name |
| `DEBUG` | `False` | Enable debug mode (set to `True` for development) |
| `DATABASE_URL` | `sqlite+aiosqlite:///./scans.db` | Database connection string |
| `MAX_CONCURRENT_SCANS` | `3` | Maximum parallel scans |
| `GLOBAL_SCAN_TIMEOUT` | `600` | Total scan timeout in seconds |
| `ALLOW_LOCALHOST_SCANNING` | `True` | Allow scanning localhost/127.0.0.1 |
| `ALLOW_PRIVATE_IP_SCANNING` | `False` | Allow scanning private IP ranges |
| `RATE_LIMIT_ENABLED` | `True` | Enable API rate limiting |
| `RATE_LIMIT_PER_MINUTE` | `10` | Requests per minute per IP |
| `RATE_LIMIT_PER_HOUR` | `100` | Requests per hour per IP |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `LOG_FORMAT` | `structured` | Log format (structured or simple) |
| `SCAN_RETENTION_DAYS` | `30` | Days to keep old scans |
| `ALLOWED_ORIGINS` | `http://localhost:5173` | CORS allowed origins (comma-separated) |

### Frontend Configuration

For development, the frontend automatically connects to `http://localhost:8000`.

For production, create `frontend/.env.production`:

```bash
# Leave empty for same-origin requests (recommended)
VITE_API_BASE_URL=

# Or set to your API URL if on different domain
# VITE_API_BASE_URL=https://api.yourdomain.com
```

### PostgreSQL Configuration (Production)

For production deployments with PostgreSQL:

```bash
# Install PostgreSQL driver (already in requirements.txt)
pip install asyncpg==0.29.0

# Update DATABASE_URL in .env
DATABASE_URL="postgresql+asyncpg://username:password@localhost:5432/vuln_scanner"
```

---

## 🚀 Running the Application

### Development Mode

#### Option 1: Using Separate Terminals (Recommended)

**Terminal 1 - Backend:**
```bash
# Activate virtual environment
source venv/bin/activate

# Start FastAPI backend
python app/main.py

# Or use uvicorn directly with auto-reload
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Frontend:**
```bash
# Navigate to frontend directory
cd frontend

# Start Vite dev server
npm run dev
```

#### Option 2: Using Background Process

```bash
# Start backend in background
source venv/bin/activate
python app/main.py &

# Start frontend
cd frontend
npm run dev
```

### Accessing the Application

- **Frontend Dashboard**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation (Swagger)**: http://localhost:8000/docs
- **API Documentation (ReDoc)**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

### Stopping the Application

```bash
# If running in foreground, press Ctrl+C in each terminal

# If running in background, find and kill the process
ps aux | grep "python app/main.py"
kill <process_id>
```

---

## 📚 API Documentation

### Interactive API Docs

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

#### Scan Operations

```bash
# Start a new scan
POST /api/scan/
{
  "target": "example.com",
  "options": {
    "allow_private": false,
    "allow_localhost": true
  }
}

# Get scan results
GET /api/scan/results/{scan_id}

# Get scan history
GET /api/scan/history?limit=10&offset=0&status=completed

# Retry failed scan
POST /api/scan/{scan_id}/retry

# Delete scan
DELETE /api/scan/{scan_id}

# Cleanup old scans
POST /api/scan/cleanup?days=30

# Get queue info
GET /api/scan/queue
```

#### Health & Monitoring

```bash
# Health check
GET /health

# Readiness probe
GET /health/ready

# Liveness probe
GET /health/live
```

### Example Usage with cURL

```bash
# Start a scan
curl -X POST "http://localhost:8000/api/scan/" \
  -H "Content-Type: application/json" \
  -d '{"target": "scanme.nmap.org"}'

# Get results (replace {scan_id} with actual ID)
curl "http://localhost:8000/api/scan/results/{scan_id}"

# Get scan history
curl "http://localhost:8000/api/scan/history?limit=5"
```

---

## 📁 Project Structure

```
xenorasec/
├── app/                          # Backend (FastAPI)
│   ├── core/                     # Core functionality
│   │   ├── config.py            # Configuration management
│   │   ├── logging.py           # Structured logging
│   │   ├── rate_limit.py        # Rate limiting
│   │   └── security.py          # Security utilities
│   ├── db/                       # Database layer
│   │   ├── database.py          # Database connection
│   │   ├── models.py            # SQLAlchemy models
│   │   └── crud.py              # CRUD operations
│   ├── routes/                   # API endpoints
│   │   ├── health.py            # Health checks
│   │   ├── scan.py              # Scan operations
│   │   └── ui.py                # UI routes
│   ├── schemas/                  # Pydantic models
│   │   └── scan.py              # Request/response schemas
│   ├── services/                 # Business logic
│   │   ├── ai_service.py        # Risk scoring
│   │   ├── nmap_scan.py         # Nmap integration
│   │   ├── nuclei_scan.py       # Nuclei integration
│   │   └── scanner_service.py   # Orchestration
│   └── main.py                   # Application entry point
│
├── frontend/                     # Frontend (React + Vite)
│   ├── src/
│   │   ├── api/                 # API client
│   │   │   └── client.ts        # Axios configuration
│   │   ├── components/          # React components
│   │   │   ├── Dashboard/       # Dashboard components
│   │   │   ├── ScanForm/        # Scan creation form
│   │   │   └── ...
│   │   ├── pages/               # Page components
│   │   │   ├── Dashboard.tsx
│   │   │   ├── ScanDetail.tsx
│   │   │   └── ScanHistory.tsx
│   │   ├── types/               # TypeScript types
│   │   │   └── api.ts
│   │   ├── App.tsx              # Main app component
│   │   └── main.tsx             # Entry point
│   ├── public/                  # Static assets
│   ├── index.html               # HTML template
│   ├── package.json             # Node dependencies
│   ├── tsconfig.json            # TypeScript config
│   └── vite.config.ts           # Vite configuration
│
├── .env                          # Environment variables (create from .env.example)
├── .env.example                  # Environment template
├── requirements.txt              # Python dependencies
├── README.md                     # This file
├── BUG_FIX_CHANGELOG.md         # Recent bug fixes
├── BUG_FIX_SUMMARY.md           # Bug fix summary
└── verify_bug_fixes.py          # Verification script
```

---

## 🔒 Security

### Security Features

1. **Input Validation**: All inputs sanitized and validated
2. **CORS Protection**: Configurable allowed origins
3. **Rate Limiting**: Prevents API abuse
4. **Private IP Blocking**: Prevents scanning internal networks (configurable)
5. **Localhost Protection**: Optional localhost scanning restrictions
6. **SQL Injection Protection**: Parameterized queries and wildcard escaping
7. **Security Bypass Prevention**: Client options can only be MORE restrictive

### Security Best Practices

1. **Never commit `.env` file** - Contains sensitive configuration
2. **Use strong database passwords** in production
3. **Enable HTTPS** in production deployments
4. **Set `ALLOW_PRIVATE_IP_SCANNING=False`** in production
5. **Configure `ALLOWED_ORIGINS`** for production domains
6. **Keep Nuclei templates updated**: `nuclei -update-templates`
7. **Monitor rate limiting logs** for abuse attempts

### Environment Variables for Production

```bash
# Production .env
DEBUG=False
ALLOW_PRIVATE_IP_SCANNING=False
RATE_LIMIT_ENABLED=True
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
DATABASE_URL=postgresql+asyncpg://user:password@host:5432/dbname
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. "Nmap not found" Error

**Problem**: Backend can't find Nmap executable

**Solution**:
```bash
# Install Nmap
sudo apt-get install nmap  # Ubuntu/Debian
brew install nmap          # macOS

# Verify installation
which nmap
nmap --version
```

#### 2. "Nuclei not found" Error

**Problem**: Backend can't find Nuclei executable

**Solution**:
```bash
# Install Nuclei
go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest

# Add Go bin to PATH
export PATH=$PATH:$(go env GOPATH)/bin

# Verify installation
which nuclei
nuclei -version

# Update templates
nuclei -update-templates
```

#### 3. CORS Errors in Frontend

**Problem**: Frontend can't connect to backend

**Solution**:
```bash
# Check ALLOWED_ORIGINS in .env
ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# Restart backend after changing .env
```

#### 4. Database Connection Error

**Problem**: Can't connect to database

**Solution**:
```bash
# For SQLite (development)
# Ensure DATABASE_URL is correct in .env
DATABASE_URL=sqlite+aiosqlite:///./scans.db

# For PostgreSQL (production)
# Ensure asyncpg is installed
pip install asyncpg==0.29.0

# Check connection string format
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/dbname
```

#### 5. Port Already in Use

**Problem**: Port 8000 or 5173 already in use

**Solution**:
```bash
# Find process using port
lsof -i :8000  # or :5173

# Kill the process
kill -9 <PID>

# Or use different ports
uvicorn app.main:app --port 8001
npm run dev -- --port 5174
```

#### 6. Module Not Found Errors

**Problem**: Python can't find modules

**Solution**:
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt

# Verify installation
pip list
```

#### 7. Frontend Build Errors

**Problem**: npm install or build fails

**Solution**:
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Update npm
npm install -g npm@latest
```

### Debug Mode

Enable debug mode for detailed error messages:

```bash
# In .env
DEBUG=True
LOG_LEVEL=DEBUG
```

Then check logs:
```bash
# Backend logs
tail -f server.log

# Or view in console when running
python app/main.py
```

---

## 🚢 Production Deployment

### Pre-Deployment Checklist

- [ ] Set `DEBUG=False` in .env
- [ ] Configure `ALLOWED_ORIGINS` with production domains
- [ ] Set up PostgreSQL database
- [ ] Install `asyncpg` driver
- [ ] Update `DATABASE_URL` to PostgreSQL connection string
- [ ] Set `ALLOW_PRIVATE_IP_SCANNING=False`
- [ ] Enable rate limiting
- [ ] Configure HTTPS/SSL
- [ ] Set up reverse proxy (nginx/Apache)
- [ ] Configure firewall rules
- [ ] Set up monitoring and logging
- [ ] Create database backups

### Backend Deployment

```bash
# Install production dependencies
pip install -r requirements.txt

# Set production environment variables
export DEBUG=False
export ALLOWED_ORIGINS=https://yourdomain.com
export DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db

# Run with production server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Or use gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Frontend Deployment

```bash
cd frontend

# Build for production
npm run build

# Output will be in frontend/dist/
# Serve with nginx, Apache, or any static file server
```

### Docker Deployment (Optional)

Create `Dockerfile` for backend:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y nmap

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app/ ./app/
COPY .env .

# Install Nuclei
RUN go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Nginx Configuration Example

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    # Frontend
    location / {
        root /path/to/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # Health checks
    location /health {
        proxy_pass http://localhost:8000;
    }
}
```

---

## 🧪 Testing

### Run Verification Script

```bash
# Verify all bug fixes are implemented
python3 verify_bug_fixes.py
```

### Manual Testing

```bash
# 1. Start backend and frontend
# 2. Open http://localhost:5173
# 3. Create a scan with target: scanme.nmap.org
# 4. Wait for scan to complete
# 5. View results and verify data
# 6. Check scan history
# 7. Test filters and pagination
```

### API Testing with cURL

```bash
# Health check
curl http://localhost:8000/health

# Start scan
curl -X POST http://localhost:8000/api/scan/ \
  -H "Content-Type: application/json" \
  -d '{"target": "scanme.nmap.org"}'

# Get scan history
curl http://localhost:8000/api/scan/history
```

---

## 📊 Risk Scoring Algorithm

The AI risk scoring system uses a weighted algorithm:

### Severity Weights
- **Critical**: 5.0
- **High**: 3.0
- **Medium**: 2.0
- **Low**: 1.0
- **Info**: 0.5

### Formula

```
base_score = Σ(severity_weight) + (CVSS_scores * 1.5) + (open_ports * 0.05)
normalized_score = 10 * (base_score / (base_score + 15))
final_score = min(normalized_score, 10.0)
```

### Risk Levels
- **Critical**: 8.0 - 10.0
- **High**: 6.0 - 7.9
- **Medium**: 4.0 - 5.9
- **Low**: 2.0 - 3.9
- **Minimal**: 0.0 - 1.9

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 for Python code
- Use TypeScript for frontend code
- Add type hints to all Python functions
- Write meaningful commit messages
- Update documentation for new features
- Add tests for new functionality

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 📞 Support

For issues, questions, or contributions:

1. Check the [Troubleshooting](#-troubleshooting) section
2. Review [API Documentation](#-api-documentation)
3. Check recent [Bug Fixes](BUG_FIX_SUMMARY.md)
4. Open an issue on GitHub

---

## 🎯 Roadmap

- [ ] Multi-target scanning
- [ ] Scheduled scans
- [ ] Email notifications
- [ ] PDF report generation
- [ ] Custom Nuclei templates
- [ ] Integration with SIEM systems
- [ ] User authentication and authorization
- [ ] Team collaboration features

---

## 🙏 Acknowledgments

- **Nmap** - Network scanning tool
- **Nuclei** - Vulnerability scanner by ProjectDiscovery
- **FastAPI** - Modern Python web framework
- **React** - UI library
- **Vite** - Frontend build tool

---

**Built with ❤️ for Security Professionals**

*Last Updated: 2026-02-16*