# Telemetry Architecture & Streaming Protocols

A guide on how XenoraSec streams engine output and system telemetry from FastAPI to React.

## 1. Server-Sent Events (SSE) Stream Architecture

FastAPI provides an endpoint `/api/scan/{scan_id}/logs/stream` which connects to the active scan process logger.

- **Reconnection Resiliency**: The backend maintains an in-memory circular buffer of the last 1,000 log events per scan. If an operator refreshes or loses connection, the stream reconnects and replays buffered events before switching to real-time events.
- **Stage Tagging**: Each log entry is stamped with an execution stage:
  - `init`: Process spawning and target validation.
  - `nmap`: Host discovery and port scanning output.
  - `nuclei`: Vulnerability template matches and CVE identification.
  - `ai`: Contextual risk scoring and Groq LLM synthesis.

## 2. Worker Queue Telemetry

The frontend queries `/health` and `/api/scan/queue` periodically via TanStack Query to keep operators informed of engine capacity:

- `scans_running`: Currently active concurrent scan tasks.
- `max_concurrent_scans`: Hardware/policy ceiling (default: 3).
- `available_slots`: Remaining scan capacity before queue saturation.
