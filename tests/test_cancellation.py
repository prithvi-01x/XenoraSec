# tests/test_cancellation.py

import asyncio
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.nmap_scan import NmapScanner
from app.services.nuclei_scan import NucleiScanner


@pytest.mark.asyncio
async def test_nmap_process_killed_on_cancellation():
    scanner = NmapScanner(timeout=10)
    fake_process = AsyncMock()
    fake_process.returncode = None
    fake_process.kill = MagicMock()
    fake_process.communicate.side_effect = asyncio.CancelledError()

    with patch("asyncio.create_subprocess_exec", return_value=fake_process):
        with pytest.raises(asyncio.CancelledError):
            await scanner._execute_scan("example.com")

    # verify process.kill was called
    assert fake_process.kill.called
    assert fake_process.wait.called


@pytest.mark.asyncio
async def test_nuclei_process_killed_on_cancellation():
    scanner = NucleiScanner(timeout=10)
    fake_process = MagicMock()
    fake_process.returncode = None
    fake_process.stdout = AsyncMock()
    fake_process.stdout.read.side_effect = asyncio.CancelledError()
    fake_process.stderr = AsyncMock()
    fake_process.stderr.read = AsyncMock(return_value=b"")
    fake_process.wait = AsyncMock()

    with patch("asyncio.create_subprocess_exec", AsyncMock(return_value=fake_process)):
        with pytest.raises(asyncio.CancelledError):
            await scanner.scan("http://example.com")

    # verify process.kill was called
    assert fake_process.kill.called
    assert fake_process.wait.called


@pytest.mark.asyncio
async def test_nuclei_timeout_returns_timeout_status():
    scanner = NucleiScanner(timeout=0.01)
    fake_process = MagicMock()
    fake_process.returncode = None
    fake_process.kill = MagicMock()
    fake_process.stdout = AsyncMock()
    
    async def slow_read(size):
        await asyncio.sleep(0.05)
        return b""

    fake_process.stdout.read.side_effect = slow_read
    fake_process.stderr = AsyncMock()
    fake_process.stderr.read = AsyncMock(return_value=b"")
    fake_process.wait = AsyncMock()

    with patch("asyncio.create_subprocess_exec", AsyncMock(return_value=fake_process)):
        res = await scanner.scan("http://example.com")
        assert res["status"] == "timeout"
        assert "timed out" in res["error"]
        assert fake_process.kill.called


@pytest.mark.asyncio
async def test_nuclei_process_failure_returns_failed_status():
    scanner = NucleiScanner(timeout=10)
    fake_process = MagicMock()
    fake_process.returncode = 1
    fake_process.stdout = AsyncMock()
    fake_process.stdout.read = AsyncMock(return_value=b"")
    fake_process.stderr = AsyncMock()
    fake_process.stderr.read = AsyncMock(return_value=b"FATAL: bad command line flags\n")
    fake_process.wait = AsyncMock()

    with patch("asyncio.create_subprocess_exec", AsyncMock(return_value=fake_process)):
        res = await scanner.scan("http://example.com")
        assert res["status"] == "failed"
        assert "FATAL: bad command line flags" in res["error"]

