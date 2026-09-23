# tests/test_streaming.py

import pytest
import asyncio
from fastapi.testclient import TestClient
from app.main import app
from app.services.event_bus import ScanEventBus, scan_event_bus
from app.schemas.stream import StreamStage, StreamLogLevel


@pytest.mark.asyncio
async def test_scan_event_bus_pub_sub():
    bus = ScanEventBus(buffer_size=10)
    scan_id = "test-scan-123"

    queue = await bus.subscribe(scan_id)
    assert bus.active_subscribers_count(scan_id) == 1

    # Emit log
    await bus.emit_log(
        scan_id=scan_id,
        message="Port 443 open",
        stage=StreamStage.NMAP,
        level=StreamLogLevel.SUCCESS,
        details={"port": 443}
    )

    msg = await asyncio.wait_for(queue.get(), timeout=1.0)
    assert msg.event == "log"
    assert msg.data.message == "Port 443 open"
    assert msg.data.stage == StreamStage.NMAP
    assert msg.data.level == StreamLogLevel.SUCCESS

    # Check history
    history = bus.get_history(scan_id)
    assert len(history) == 1
    assert history[0].data.message == "Port 443 open"

    lines = bus.get_formatted_terminal_lines(scan_id)
    assert len(lines) == 1
    assert "[NMAP]" in lines[0]
    assert "Port 443 open" in lines[0]

    await bus.unsubscribe(scan_id, queue)
    assert bus.active_subscribers_count(scan_id) == 0


@pytest.mark.asyncio
async def test_scan_event_bus_circular_buffer():
    bus = ScanEventBus(buffer_size=3)
    scan_id = "test-scan-buffer"

    for i in range(5):
        await bus.emit_log(scan_id=scan_id, message=f"Log {i}")

    history = bus.get_history(scan_id)
    assert len(history) == 3
    assert history[0].data.message == "Log 2"
    assert history[2].data.message == "Log 4"


def test_sse_endpoint_with_history():
    client = TestClient(app)
    
    # Start a scan or create one via API
    res = client.post("/api/scan/", json={"target": "example.com", "scan_profile": "quick"})
    assert res.status_code == 200
    scan_id = res.json()["scan_id"]

    # Pre-populate some logs in the event bus and emit done event
    asyncio.run(scan_event_bus.emit_log(
        scan_id=scan_id,
        message="Test event 1",
        stage=StreamStage.NMAP
    ))
    asyncio.run(scan_event_bus.emit_log(
        scan_id=scan_id,
        message="Scan completed",
        stage=StreamStage.COMPLETE,
        event_name="done"
    ))

    # Request the stream
    stream_res = client.get(f"/api/scan/{scan_id}/stream")
    assert stream_res.status_code == 200
    assert "text/event-stream" in stream_res.headers["content-type"]
    assert "Test event 1" in stream_res.text
    assert "Scan completed" in stream_res.text


def test_websocket_endpoint_with_history():
    client = TestClient(app)
    
    # Create scan
    res = client.post("/api/scan/", json={"target": "example.com", "scan_profile": "quick"})
    assert res.status_code == 200
    scan_id = res.json()["scan_id"]

    # Pre-populate log
    asyncio.run(scan_event_bus.emit_log(
        scan_id=scan_id,
        message="WS Test event",
        stage=StreamStage.INIT
    ))

    with client.websocket_connect(f"/api/scan/{scan_id}/ws") as websocket:
        messages = []
        for _ in range(4):
            data = websocket.receive_json()
            assert data["event"] == "log"
            messages.append(data["data"]["message"])
            if "WS Test event" in data["data"]["message"]:
                break

        assert any("WS Test event" in m for m in messages)

        # Test ping/pong
        websocket.send_text("ping")
        resp = websocket.receive_text()
        assert resp == "pong"


def test_stream_invalid_scan_id():
    client = TestClient(app)
    res = client.get("/api/scan/invalid-uuid-format!/stream")
    assert res.status_code == 400


def test_stream_nonexistent_scan():
    client = TestClient(app)
    res = client.get("/api/scan/00000000-0000-0000-0000-000000000000/stream")
    assert res.status_code == 404
