# app/services/event_bus.py

import asyncio
from collections import deque
from typing import Dict, Set, List, Optional, Any
from datetime import datetime, UTC
from app.schemas.stream import ScanLogEvent, ScanStreamMessage, StreamLogLevel, StreamStage
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class ScanEventBus:
    """
    In-memory asynchronous event bus for broadcasting real-time scan logs
    to Server-Sent Events (SSE) and WebSocket clients.
    
    Includes a circular buffer per scan_id to replay history upon connection.
    """

    def __init__(self, buffer_size: Optional[int] = None):
        self.buffer_size = buffer_size or settings.STREAM_LOG_BUFFER_SIZE
        # Active subscriber queues per scan_id: scan_id -> Set[asyncio.Queue]
        self._subscribers: Dict[str, Set[asyncio.Queue]] = {}
        # Historical event buffer per scan_id: scan_id -> deque[ScanLogEvent]
        self._buffers: Dict[str, deque] = {}
        # Lock for thread/coroutine-safe subscriber registration
        self._lock = asyncio.Lock()

    def _get_or_create_buffer(self, scan_id: str) -> deque:
        if scan_id not in self._buffers:
            self._buffers[scan_id] = deque(maxlen=self.buffer_size)
        return self._buffers[scan_id]

    async def emit_log(
        self,
        scan_id: str,
        message: str,
        stage: StreamStage = StreamStage.INIT,
        level: StreamLogLevel = StreamLogLevel.INFO,
        details: Optional[Dict[str, Any]] = None,
        event_name: str = "log"
    ) -> ScanLogEvent:
        """
        Record and publish a scan log event to all active subscribers.
        """
        event = ScanLogEvent(
            scan_id=scan_id,
            timestamp=datetime.now(UTC),
            stage=stage,
            level=level,
            message=message,
            details=details
        )
        
        envelope = ScanStreamMessage(event=event_name, data=event)

        # Store in circular ring buffer for replay
        buffer = self._get_or_create_buffer(scan_id)
        buffer.append(envelope)

        # Broadcast to all connected subscriber queues
        queues = self._subscribers.get(scan_id, set())
        for q in list(queues):
            try:
                q.put_nowait(envelope)
            except asyncio.QueueFull:
                logger.warning(f"Subscriber queue full for scan {scan_id}, dropping message")
            except Exception as e:
                logger.debug(f"Failed to put to queue: {e}")

        return event

    async def subscribe(self, scan_id: str) -> asyncio.Queue:
        """
        Subscribe to live scan events. Returns an asyncio.Queue.
        """
        queue = asyncio.Queue(maxsize=1000)
        async with self._lock:
            if scan_id not in self._subscribers:
                self._subscribers[scan_id] = set()
            self._subscribers[scan_id].add(queue)
        return queue

    async def unsubscribe(self, scan_id: str, queue: asyncio.Queue) -> None:
        """
        Unsubscribe a queue from live scan events.
        """
        async with self._lock:
            if scan_id in self._subscribers:
                self._subscribers[scan_id].discard(queue)
                if not self._subscribers[scan_id]:
                    del self._subscribers[scan_id]

    def get_history(self, scan_id: str) -> List[ScanStreamMessage]:
        """
        Retrieve stored historical log messages for a given scan.
        """
        if scan_id in self._buffers:
            return list(self._buffers[scan_id])
        return []

    def get_formatted_terminal_lines(self, scan_id: str) -> List[str]:
        """
        Retrieve formatted plain-text log lines for terminal view.
        """
        history = self.get_history(scan_id)
        lines = []
        for item in history:
            evt = item.data
            ts = evt.timestamp.strftime("%H:%M:%S")
            stage_badge = f"[{evt.stage.value.upper()}]"
            lines.append(f"{ts} {stage_badge:<10} {evt.message}")
        return lines

    def active_subscribers_count(self, scan_id: str) -> int:
        """Count active listeners for a scan"""
        return len(self._subscribers.get(scan_id, set()))

    def clear_scan(self, scan_id: str) -> None:
        """Clean up buffers and subscribers for a scan"""
        self._buffers.pop(scan_id, None)
        self._subscribers.pop(scan_id, None)


# Global singleton instance
scan_event_bus = ScanEventBus()
