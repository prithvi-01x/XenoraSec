# 🚀 Quick Start Guide - XenoraSec

Get up and running in 5 minutes!

---

## ⚡ Prerequisites Check

Before starting, verify you have:

```bash
# Check Python version (need 3.10+)
python3 --version

# Check Node.js version (need 18+)
node --version

# Check if Nmap is installed
nmap --version

# Check if Nuclei is installed
nuclei -version
```

If any are missing, see the [Installation](#-installation) section below.

---

## 🏃 Quick Start (5 Minutes)

### 1. Install Prerequisites (if needed)

```bash
# Install Nmap
sudo apt-get install nmap  # Ubuntu/Debian
# or
brew install nmap          # macOS

# Install Nuclei
go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest

# Update Nuclei templates
nuclei -update-templates
```

### 2. Setup Backend

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
```

### 3. Setup Frontend

```bash
cd frontend
npm install
cd ..
```

### 4. Run the Application

**Terminal 1 - Backend:**
```bash
source venv/bin/activate
python app/main.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### 5. Access the Application

Open your browser and go to:
- **Dashboard**: http://localhost:5173
- **API Docs**: http://localhost:8000/docs

---

## 🎯 First Scan

1. Open http://localhost:5173
2. Enter a target: `scanme.nmap.org`
3. Click "Start Scan"
4. Wait for results (usually 1-2 minutes)
5. View detailed findings and risk score

---

## 📋 Detailed Installation

### Install Python 3.10+

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install python3.10 python3.10-venv python3-pip
```

**macOS:**
```bash
brew install python@3.10
```

**Windows:**
Download from https://www.python.org/downloads/

### Install Node.js 18+

**Ubuntu/Debian:**
```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

**macOS:**
```bash
brew install node@18
```

**Windows:**
Download from https://nodejs.org/

### Install Nmap

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install nmap
```

**macOS:**
```bash
brew install nmap
```

**Windows:**
Download from https://nmap.org/download.html

### Install Nuclei

**Using Go (all platforms):**
```bash
go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest

# Add to PATH if needed
export PATH=$PATH:$(go env GOPATH)/bin

# Update templates
nuclei -update-templates
```

**Or download binary:**
https://github.com/projectdiscovery/nuclei/releases

---

## ⚙️ Basic Configuration

### Minimum .env Configuration

```bash
# .env
APP_NAME="XenoraSec"
DEBUG=True
DATABASE_URL="sqlite+aiosqlite:///./scans.db"
ALLOW_LOCALHOST_SCANNING=True
ALLOW_PRIVATE_IP_SCANNING=False
RATE_LIMIT_ENABLED=True
LOG_LEVEL=INFO
```

### Optional: Advanced Configuration

```bash
# Scanning
MAX_CONCURRENT_SCANS=3
GLOBAL_SCAN_TIMEOUT=600

# Rate Limiting
RATE_LIMIT_PER_MINUTE=10
RATE_LIMIT_PER_HOUR=100

# Data Retention
SCAN_RETENTION_DAYS=30

# CORS (for production)
ALLOWED_ORIGINS=https://yourdomain.com
```

---

## 🐛 Common Issues & Solutions

### Issue: "Nmap not found"

**Solution:**
```bash
# Install Nmap
sudo apt-get install nmap

# Verify
which nmap
nmap --version
```

### Issue: "Nuclei not found"

**Solution:**
```bash
# Install Nuclei
go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest

# Add to PATH
export PATH=$PATH:$(go env GOPATH)/bin

# Verify
which nuclei
nuclei -version
```

### Issue: "Port 8000 already in use"

**Solution:**
```bash
# Find process
lsof -i :8000

# Kill it
kill -9 <PID>

# Or use different port
uvicorn app.main:app --port 8001
```

### Issue: CORS errors

**Solution:**
```bash
# Check .env has correct origins
ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# Restart backend
```

### Issue: Module not found

**Solution:**
```bash
# Ensure venv is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

---

## 📚 Next Steps

1. **Read the full README**: [README.md](README.md)
2. **Explore API docs**: http://localhost:8000/docs
3. **Check bug fixes**: [BUG_FIX_SUMMARY.md](BUG_FIX_SUMMARY.md)
4. **Run verification**: `python3 verify_bug_fixes.py`

---

## 🎓 Usage Examples

### Scan a Public Target

```bash
# Using the UI
1. Go to http://localhost:5173
2. Enter: scanme.nmap.org
3. Click "Start Scan"

# Using API
curl -X POST http://localhost:8000/api/scan/ \
  -H "Content-Type: application/json" \
  -d '{"target": "scanme.nmap.org"}'
```

### View Scan History

```bash
# Using the UI
1. Click "Scan History" in navigation
2. Use filters and search

# Using API
curl http://localhost:8000/api/scan/history?limit=10
```

### Check System Health

```bash
curl http://localhost:8000/health
```

---

## 🔒 Security Notes

- **Never scan targets without permission**
- Set `ALLOW_PRIVATE_IP_SCANNING=False` in production
- Keep Nuclei templates updated: `nuclei -update-templates`
- Use HTTPS in production
- Configure `ALLOWED_ORIGINS` for production domains

---

## 💡 Tips

1. **First scan takes longer** - Nuclei downloads templates
2. **Use scanme.nmap.org** - Safe target for testing
3. **Check logs** - `tail -f server.log` for debugging
4. **Update templates** - Run `nuclei -update-templates` weekly
5. **Monitor resources** - Scans can be CPU/memory intensive

---

## 🆘 Getting Help

1. Check [Troubleshooting](#-common-issues--solutions) above
2. Read the [full README](README.md)
3. Review [API documentation](http://localhost:8000/docs)
4. Check [bug fixes](BUG_FIX_SUMMARY.md)
5. Open an issue on GitHub

---

## ✅ Verification

Run the verification script to ensure everything is set up correctly:

```bash
python3 verify_bug_fixes.py
```

Should output:
```
✅ ALL VERIFICATIONS PASSED!
```

---

**Happy Scanning! 🛡️**

*For detailed documentation, see [README.md](README.md)*
