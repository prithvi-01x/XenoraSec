# Environment Configuration & Security Policy Directives

Reference manual for XenoraSec backend environmental controls and runtime security constraints.

## 1. Engine Concurrency & Limits

- `MAX_CONCURRENT_SCANS`: Maximum parallel scans allowed in the worker pool (Default: `3`).
- `GLOBAL_SCAN_TIMEOUT`: Maximum execution duration per target in seconds (Default: `600s`).
- `NMAP_TIMEOUT`: Maximum time allotted for the Nmap phase in seconds (Default: `180s`).
- `NUCLEI_TIMEOUT`: Maximum time allotted for the Nuclei phase in seconds (Default: `300s`).

## 2. Ingress & Network Defense

- `ALLOW_PRIVATE_IP_SCANNING`: Restricts targeting RFC1918 private subnets (Default: `false`).
- `ALLOW_LOCALHOST_SCANNING`: Controls targeting loopback addresses (Default: `false` in production, `true` for local dev).
- `RATE_LIMIT_PER_MINUTE`: Sliding-window request rate limit per client IP (Default: `10`).
- `TRUST_PROXY_HEADERS`: Validates whether reverse proxy headers (`X-Forwarded-For`) can be trusted for rate-limiting.
