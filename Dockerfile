# Production Dockerfile for XenoraSec Backend
FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install runtime system packages (nmap, wget, unzip, ca-certificates)
RUN apt-get update && apt-get install -y --no-install-recommends \
    nmap \
    wget \
    unzip \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install precompiled Nuclei binary
ARG NUCLEI_VERSION=3.3.8
RUN wget -q "https://github.com/projectdiscovery/nuclei/releases/download/v${NUCLEI_VERSION}/nuclei_${NUCLEI_VERSION}_linux_amd64.zip" \
    && unzip -q "nuclei_${NUCLEI_VERSION}_linux_amd64.zip" nuclei -d /usr/local/bin/ \
    && rm "nuclei_${NUCLEI_VERSION}_linux_amd64.zip" \
    && chmod +x /usr/local/bin/nuclei \
    && nuclei -update-templates || true

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create volume mount directory for SQLite WAL database
RUN mkdir -p /data

# Copy application source
COPY . .

EXPOSE 8000

HEALTHCHECK --interval=15s --timeout=5s --start-period=10s --retries=3 \
    CMD python3 -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
