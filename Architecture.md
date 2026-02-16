# Architectural Decisions & Rationale

## 🏗️ Core Design Principles

### 1. **Single Source of Truth**

**Decision**: All scan state persisted in database, no in-memory caching.

**Rationale**:
- Survives restarts
- Enables horizontal scaling
- No state synchronization issues
- Audit trail for compliance

**Trade-offs**:
- Slightly higher latency per request
- Database becomes critical path
- More database load

**Mitigation**:
- Database indexes for performance
- Connection pooling
- Async queries

---

### 2. **Unified Status Enum**

**Decision**: Single `ScanStatus` enum used across all layers.

**Rationale**:
- Eliminates mapping errors
- Type-safe status checks
- Clear contract between layers
- Easier debugging

**Implementation**:
```python
class ScanStatus(str, Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"
    TIMEOUT = "timeout"
```

---

### 3. **Centralized Configuration**

**Decision**: Pydantic BaseSettings with environment variables.

**Rationale**:
- 12-factor app compliance
- Type-safe configuration
- Easy deployment (Docker, K8s)
- Clear defaults
- Self-documenting

**Benefits**:
- No code changes between environments
- Validation at startup
- IDE autocomplete for settings

---

### 4. **Async-First Architecture**

**Decision**: Async/await throughout entire stack.

**Rationale**:
- Non-blocking I/O for scans
- Handle many concurrent requests
- Efficient resource usage
- FastAPI native support

**Implementation**:
- AsyncSession for database
- Async subprocess for scanners
- AsyncIO gather for parallel scans
- Async context managers

---

### 5. **Semaphore-Based Concurrency Control**

**Decision**: Global semaphore limiting concurrent scans.

**Rationale**:
- Prevent resource exhaustion
- Predictable memory usage
- Fair queuing
- Simple implementation

**Alternative Considered**: Celery task queue
- **Why Not**: Adds complexity, requires Redis/RabbitMQ
- **When to Switch**: If scaling beyond single server

---

### 6. **Background Task Pattern**

**Decision**: `asyncio.create_task()` for scan execution.

**Rationale**:
- FastAPI BackgroundTasks too limited
- Need independent DB session
- Better error isolation
- Can implement retry logic

**Implementation**:
```python
asyncio.create_task(
    _run_and_store_scan(scan_id, target, metadata)
)
```

**Each task**:
- Creates own DB session
- Handles all errors
- Updates scan status
- Logs comprehensively

---

### 7. **Target Validation & Preparation**

**Decision**: Separate validation and preparation functions.

**Rationale**:
- Nmap needs hostname (no scheme)
- Nuclei needs full URL (with scheme)
- Security checks once, upfront
- Clear separation of concerns

**Flow**:
1. User submits target
2. Validate and extract metadata
3. Prepare Nmap target (strip scheme)
4. Prepare Nuclei target (ensure scheme)
5. Pass to scanners

---

### 8. **Structured Logging**

**Decision**: JSON structured logs in production.

**Rationale**:
- Machine-parseable
- Log aggregation friendly (ELK, Splunk)
- Context fields (scan_id, target)
- Searchable

**Format**:
```json
{
  "timestamp": "2024-01-01T12:00:00Z",
  "level": "INFO",
  "logger": "app.services.scanner",
  "message": "Scan completed",
  "scan_id": "...",
  "target": "example.com",
  "duration": 45.2
}
```

---

### 9. **Error Handling Strategy**

**Decision**: Fail gracefully, always update database.

**Rationale**:
- User sees meaningful status
- No orphaned "running" scans
- Audit trail of failures
- Can retry failed scans

**Pattern**:
```python
try:
    result = await run_scan()
    await update_scan_result()
except Exception as e:
    await mark_scan_failed()
```

---

### 10. **Rate Limiting Design**

**Decision**: In-memory sliding window, per-IP.

**Rationale**:
- Simple, no dependencies
- Fast (no external calls)
- Good enough for single-server

**When to Upgrade**: Redis-backed for multi-server.

**Implementation**:
- Deque of timestamps per IP
- Remove expired timestamps
- Check count against limits

---

### 11. **Database Index Strategy**

**Decision**: Composite indexes on common query patterns.

**Indexes Created**:
```python
Index('ix_scan_status_created', 'status', 'created_at')
Index('ix_scan_risk_created', 'risk_score', 'created_at')
Index('ix_scan_target_created', 'target', 'created_at')
```

**Rationale**:
- History queries: status + time
- Risk queries: score + time
- Target search: target + time

---

### 12. **Risk Scoring Normalization**

**Decision**: Sigmoid-like normalization to 0-10 scale.

**Formula**:
```python
normalized = 10.0 * (score / (score + 15.0))
```

**Rationale**:
- Prevents score inflation
- Lower scores more sensitive
- Upper bound is 10.0
- Smooth curve

**Alternative Considered**: Linear scaling
- **Why Not**: Doesn't handle outliers well

---

### 13. **Memory Safety in Nuclei**

**Decision**: Multiple safety caps.

**Caps**:
1. Buffer size limit (1MB)
2. Max vulnerabilities (1000)
3. Timeout (300s)

**Rationale**:
- Prevent memory exhaustion
- Protect against malicious targets
- Predictable resource usage

---

### 14. **PostgreSQL-First Design**

**Decision**: Support both SQLite and PostgreSQL.

**Rationale**:
- SQLite for development
- PostgreSQL for production
- Same code works for both
- Easy Supabase integration

**Compatibility**:
- No DB-specific SQL
- AsyncIO drivers for both
- Connection pooling for Postgres
- NullPool for SQLite

---

### 15. **Pydantic Schemas Everywhere**

**Decision**: All API inputs/outputs use Pydantic.

**Benefits**:
- Automatic validation
- OpenAPI documentation
- Type hints
- Clear contracts

**Organization**:
- Request schemas: `ScanCreateRequest`
- Response schemas: `ScanResultResponse`
- Shared enums: `ScanStatus`

---

### 16. **Health Check Design**

**Decision**: Multiple health endpoints.

**Endpoints**:
- `/health` - Full health check
- `/health/ready` - Kubernetes readiness
- `/health/live` - Kubernetes liveness

**Rationale**:
- Kubernetes native support
- Can check DB connectivity
- Separate concerns (ready vs alive)

---

### 17. **Scan Retry Pattern**

**Decision**: Create new scan, link to parent.

**Rationale**:
- Preserves history
- Can analyze retry success rate
- Simple implementation
- Clear parent-child relationship

**Schema**:
```python
parent_scan_id = Column(String(36), nullable=True)
```

---

### 18. **Global Timeout Pattern**

**Decision**: Wrap entire scan in `asyncio.wait_for()`.

**Rationale**:
- Prevents hung scans
- Simple implementation
- Works with any scan logic
- Clear timeout status

**Implementation**:
```python
await asyncio.wait_for(
    _execute_scan(),
    timeout=GLOBAL_SCAN_TIMEOUT
)
```

---

## 🔄 Future Improvements

### Short-term (v2.1)

1. **Redis Rate Limiting**
   - Multi-server support
   - Persistent limits

2. **Webhook Notifications**
   - Callback on scan completion
   - Email notifications

3. **Scan Templates**
   - Saved scan configurations
   - Severity filters

### Mid-term (v2.5)

1. **Celery Task Queue**
   - Better job distribution
   - Priority queues
   - Scheduled scans

2. **S3 Result Storage**
   - Offload large results
   - Long-term archival

3. **Grafana Dashboards**
   - Metrics export
   - Performance monitoring

### Long-term (v3.0)

1. **Multi-tenant Support**
   - Organization isolation
   - Per-org rate limits
   - RBAC

2. **Custom Scanner Integration**
   - Plugin system
   - Custom vulnerability checks

3. **Machine Learning Risk Scoring**
   - Train on historical data
   - Predictive risk modeling

---

## 📊 Performance Characteristics

### Current Limits

| Metric | Value | Configurable |
|--------|-------|--------------|
| Max concurrent scans | 3 | Yes |
| Request rate limit | 10/min | Yes |
| Global scan timeout | 600s | Yes |
| Max vulnerabilities | 1000 | Yes |
| Buffer size | 1MB | Yes |

### Expected Performance

| Operation | Latency | Throughput |
|-----------|---------|------------|
| Start scan | <50ms | Limited by rate |
| Get results | <10ms | 1000+ req/s |
| Scan history | <50ms | 500+ req/s |
| Full scan | 60-300s | 3 concurrent |

### Scaling Profile

**Single Server**:
- 3 concurrent scans
- 10 requests/min
- ~500 scans/day

**With Horizontal Scaling**:
- N × 3 concurrent scans
- Load balancer
- Shared PostgreSQL
- Redis rate limiting

---

## 🎯 Design Goals Achieved

✅ **Production-Ready**: Error handling, logging, monitoring
✅ **Secure**: Validation, rate limiting, safe defaults
✅ **Scalable**: Async, stateless, horizontally scalable
✅ **Maintainable**: Clear structure, documented, type-safe
✅ **Testable**: Dependency injection, clear interfaces
✅ **Observable**: Structured logs, health checks, metrics-ready

---

## 📚 References

- [FastAPI Best Practices](https://fastapi.tiangolo.com/tutorial/)
- [SQLAlchemy Async](https://docs.sqlalchemy.org/en/14/orm/extensions/asyncio.html)
- [Pydantic Settings](https://docs.pydantic.dev/latest/usage/settings/)
- [12-Factor App](https://12factor.net/)
- [Nmap Documentation](https://nmap.org/docs.html)
- [Nuclei Documentation](https://nuclei.projectdiscovery.io/)

---

## 📊 Risk Scoring Algorithm

The AI risk scoring system uses a weighted algorithm to calculate a normalized risk score (0-10) for each target.

### Severity Weights
- **Critical**: 5.0
- **High**: 3.0
- **Medium**: 2.0
- **Low**: 1.0
- **Info**: 0.5

### Calculation Formula
```python
# Base score calculation
base_score = sum(severity_weight) + (CVSS_scores * 1.5) + (open_ports * 0.05)
normalized_score = 10 * (base_score / (base_score + 15))
```

This normalization ensures that scores never exceed 10.0 and critical findings have maximum impact.

---

## 🚢 Production Deployment Architecture

For production environments, the recommended architecture is:

```
[Load Balancer] -> [Nginx Reverse Proxy] -> [Uvicorn Workers] -> [FastAPI App]
                                                                     |
                                                                     v
                                                             [PostgreSQL DB]
```

### Deployment Checklist
1. **Database**: Use PostgreSQL with `asyncpg` driver
2. **Server**: Run behind Nginx with SSL/TLS
3. **Workers**: Run multiple Uvicorn workers (`workers = 2 * CPU + 1`)
4. **Security**: Set `DEBUG=False`, `ALLOW_PRIVATE_IP_SCANNING=False`, `RATE_LIMIT_ENABLED=True`
