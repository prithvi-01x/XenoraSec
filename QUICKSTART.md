# 🚀 Quick Start Guide - AI Vulnerability Scanner v2.0

## ⚡ 5-Minute Setup

### 1. Extract Archive

```bash
tar -xzf refactored_scanner_v2.tar.gz
cd refactored_scanner
```

### 2. Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python packages
pip install -r requirements.txt
```

### 3. Install System Tools

```bash
# Nmap
sudo apt-get update && sudo apt-get install -y nmap

# Nuclei (option 1: using Go)
go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest

# Nuclei (option 2: binary download)
wget https://github.com/projectdiscovery/nuclei/releases/latest/download/nuclei_linux_amd64.zip
unzip nuclei_linux_amd64.zip
sudo mv nuclei /usr/local/bin/
```

### 4. Configure

```bash
# Copy example config
cp .env.example .env

# Edit if needed (defaults work for local testing)
nano .env
```

### 5. Run

```bash
# Start server
python main.py

# Or using uvicorn directly
uvicorn main:app --reload
```

Server starts at: **http://localhost:8000**

---

## 🧪 Test the API

### 1. Health Check

```bash
curl http://localhost:8000/health
```

Expected:
```json
{
  "status": "ok",
  "version": "2.0.0",
  "timestamp": "2024-01-01T12:00:00Z",
  "database": "connected"
}
```

### 2. Start a Scan

```bash
curl -X POST http://localhost:8000/scan/ \
  -H "Content-Type: application/json" \
  -d '{"target": "scanme.nmap.org"}'
```

Response:
```json
{
  "scan_id": "550e8400-e29b-41d4-a716-446655440000",
  "target": "scanme.nmap.org",
  "status": "running",
  "message": "Scan started successfully"
}
```

### 3. Check Results

```bash
# Replace {scan_id} with actual ID from step 2
curl http://localhost:8000/scan/results/{scan_id}
```

### 4. View History

```bash
curl http://localhost:8000/scan/history?limit=10
```

### 5. View API Docs

Open in browser:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 📊 Example Complete Scan

```bash
# Start scan
SCAN_ID=$(curl -s -X POST http://localhost:8000/scan/ \
  -H "Content-Type: application/json" \
  -d '{"target": "scanme.nmap.org"}' | jq -r '.scan_id')

echo "Scan ID: $SCAN_ID"

# Wait for completion (typically 60-120 seconds)
while true; do
  STATUS=$(curl -s http://localhost:8000/scan/results/$SCAN_ID | jq -r '.status')
  echo "Status: $STATUS"
  
  if [ "$STATUS" != "running" ]; then
    break
  fi
  
  sleep 5
done

# Get full results
curl -s http://localhost:8000/scan/results/$SCAN_ID | jq '.'
```

---

## 🎯 Key Features to Try

### 1. Rate Limiting

```bash
# Try making 15 requests quickly
for i in {1..15}; do
  curl -X POST http://localhost:8000/scan/ \
    -H "Content-Type: application/json" \
    -d '{"target": "example.com"}'
done
# After 10, you'll get 429 Too Many Requests
```

### 2. Retry Failed Scan

```bash
# If a scan fails, retry it
curl -X POST http://localhost:8000/scan/{failed_scan_id}/retry
```

### 3. Queue Status

```bash
# Check scan queue
curl http://localhost:8000/scan/queue
```

### 4. Cleanup Old Scans

```bash
# Delete scans older than 7 days
curl -X POST "http://localhost:8000/scan/cleanup?days=7"
```

---

## ⚙️ Configuration Tips

### Development Settings

```bash
# .env
DEBUG=True
LOG_LEVEL=DEBUG
LOG_FORMAT=simple
ALLOW_LOCALHOST_SCANNING=True
RATE_LIMIT_ENABLED=False
```

### Production Settings

```bash
# .env
DEBUG=False
LOG_LEVEL=INFO
LOG_FORMAT=structured
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db
MAX_CONCURRENT_SCANS=10
RATE_LIMIT_ENABLED=True
ALLOW_PRIVATE_IP_SCANNING=False
```

---

## 🐛 Troubleshooting

### Issue: Nmap not found

```bash
# Install nmap
sudo apt-get install nmap

# Verify
nmap --version
```

### Issue: Nuclei not found

```bash
# Check PATH
echo $PATH

# Add to PATH
export PATH=$PATH:$HOME/go/bin

# Or move to system location
sudo mv ~/go/bin/nuclei /usr/local/bin/
```

### Issue: Database locked (SQLite)

```bash
# Stop all running instances
pkill -f "python main.py"
pkill -f "uvicorn"

# Delete lock
rm scans.db-wal scans.db-shm

# Or switch to PostgreSQL in production
```

### Issue: Port 8000 already in use

```bash
# Use different port
uvicorn main:app --port 8080

# Or kill existing process
lsof -ti:8000 | xargs kill -9
```

---

## 📚 Next Steps

1. **Read ARCHITECTURE.md** - Understand design decisions
2. **Read CHANGELOG.md** - See all improvements
3. **Customize `.env`** - Adjust settings for your use case
4. **Set up PostgreSQL** - For production deployment
5. **Configure monitoring** - Use structured logs with ELK/Grafana
6. **Add authentication** - Implement API key auth
7. **Deploy with Docker** - See README.md for Dockerfile

---

## 🔗 Useful Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API info |
| `/docs` | GET | Swagger UI |
| `/health` | GET | Health check |
| `/scan/` | POST | Start scan |
| `/scan/results/{id}` | GET | Get results |
| `/scan/history` | GET | List scans |
| `/scan/{id}/retry` | POST | Retry scan |
| `/scan/queue` | GET | Queue status |
| `/scan/cleanup` | POST | Cleanup old |

---

## 💡 Pro Tips

1. **Use jq**: Format JSON responses nicely
   ```bash
   curl http://localhost:8000/scan/history | jq '.'
   ```

2. **Watch logs**: Monitor scan progress
   ```bash
   tail -f scanner.log
   ```

3. **Test locally first**: Use localhost/scanme.nmap.org
   ```bash
   curl -X POST http://localhost:8000/scan/ \
     -H "Content-Type: application/json" \
     -d '{"target": "127.0.0.1"}'
   ```

4. **Check queue before scanning**: Avoid 503 errors
   ```bash
   curl http://localhost:8000/scan/queue
   ```

5. **Use pagination**: For large history
   ```bash
   curl "http://localhost:8000/scan/history?limit=20&offset=40"
   ```

---

## ✅ Checklist

- [ ] Extract archive
- [ ] Install Python dependencies
- [ ] Install Nmap
- [ ] Install Nuclei
- [ ] Copy .env.example to .env
- [ ] Start server
- [ ] Test health endpoint
- [ ] Run test scan
- [ ] View API docs
- [ ] Configure for your environment

---

## 🎉 You're Ready!

The scanner is now running and ready to detect vulnerabilities. Check out the full documentation in README.md for advanced features and production deployment.

**Need help?** Check:
- README.md - Full documentation
- ARCHITECTURE.md - Design decisions
- CHANGELOG.md - All improvements
- .env.example - Configuration options
