"""
CloudWatch Logger for AI Sakhi
Provides structured logging for user interactions, errors, and session events.
Falls back to Python's standard logging when mock=True or AWS credentials unavailable.
"""

import logging
import json
import time
import threading
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class CloudWatchLogger:
    """
    Structured logger with CloudWatch integration and mock fallback.

    In mock mode (or when AWS credentials are unavailable), all log events
    are written to Python's standard logging system instead of CloudWatch.
    Log events are batched (up to 10 events or 5-second flush interval) for
    efficiency when using the real CloudWatch client.
    """

    MAX_BATCH_SIZE = 10
    FLUSH_INTERVAL_SECONDS = 5

    def __init__(
        self,
        log_group: str,
        aws_region: str = "us-east-1",
        use_mock: bool = True,
    ) -> None:
        self.log_group = log_group
        self.aws_region = aws_region
        self.use_mock = use_mock

        self._client = None
        self._pending_events: List[Dict[str, Any]] = []
        self._lock = threading.Lock()
        self._flush_timer: Optional[threading.Timer] = None

        if not use_mock:
            self._init_cloudwatch()

        logger.info(
            "CloudWatchLogger initialised (mode=%s, log_group=%s)",
            "mock" if self.use_mock else "cloudwatch",
            log_group,
        )

    # ------------------------------------------------------------------
    # Initialisation helpers
    # ------------------------------------------------------------------

    def _init_cloudwatch(self) -> None:
        """Try to create a real boto3 CloudWatch Logs client."""
        try:
            import boto3
            from botocore.exceptions import NoCredentialsError

            self._client = boto3.client("logs", region_name=self.aws_region)
            # Ensure the log group exists
            try:
                self._client.create_log_group(logGroupName=self.log_group)
            except self._client.exceptions.ResourceAlreadyExistsException:
                pass
            logger.info("CloudWatch Logs client ready (group=%s)", self.log_group)
        except Exception as exc:
            logger.warning(
                "CloudWatch unavailable (%s). Falling back to mock mode.", exc
            )
            self.use_mock = True
            self._client = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def log_interaction(
        self,
        session_id: str,
        query: str,
        response: str,
        language: str,
        module_used: str,
        processing_time_ms: int,
    ) -> None:
        """Log a voice/text user interaction."""
        payload = {
            "event_type": "user_interaction",
            "session_id": session_id,
            "query_preview": query[:100] if query else "",
            "response_preview": response[:100] if response else "",
            "language": language,
            "module_used": module_used,
            "processing_time_ms": processing_time_ms,
        }
        self._emit("INFO", payload)

    def log_error(
        self,
        error_type: str,
        error_message: str,
        context_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log an application error with context."""
        payload = {
            "event_type": "error",
            "error_type": error_type,
            "error_message": error_message,
            "context": context_data or {},
        }
        self._emit("ERROR", payload)

    def log_session_event(
        self,
        session_id: str,
        event_type: str,
        data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log a session lifecycle event (created, updated, expired, etc.)."""
        payload = {
            "event_type": "session_event",
            "session_id": session_id,
            "session_event_type": event_type,
            "data": data or {},
        }
        self._emit("INFO", payload)

    def health_check(self) -> Dict[str, Any]:
        """Return the current health/status of the logger."""
        return {
            "status": "healthy",
            "mode": "mock" if self.use_mock else "cloudwatch",
            "log_group": self.log_group,
            "aws_region": self.aws_region,
            "pending_events": len(self._pending_events),
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _emit(self, level: str, payload: Dict[str, Any]) -> None:
        """Route a log event to mock logging or CloudWatch batch."""
        payload["timestamp"] = datetime.now(timezone.utc).isoformat()
        message = json.dumps(payload, ensure_ascii=False)

        if self.use_mock or self._client is None:
            log_fn = logger.error if level == "ERROR" else logger.info
            log_fn("[CloudWatchLogger] %s", message)
            return

        # Real CloudWatch path – batch the event
        event = {
            "timestamp": int(time.time() * 1000),
            "message": message,
        }
        with self._lock:
            self._pending_events.append(event)
            should_flush = len(self._pending_events) >= self.MAX_BATCH_SIZE

        if should_flush:
            self._flush()
        else:
            self._schedule_flush()

    def _schedule_flush(self) -> None:
        """Schedule a deferred flush if one isn't already pending."""
        with self._lock:
            if self._flush_timer is None or not self._flush_timer.is_alive():
                self._flush_timer = threading.Timer(
                    self.FLUSH_INTERVAL_SECONDS, self._flush
                )
                self._flush_timer.daemon = True
                self._flush_timer.start()

    def _flush(self) -> None:
        """Send all pending events to CloudWatch Logs."""
        with self._lock:
            if not self._pending_events:
                return
            events = list(self._pending_events)
            self._pending_events.clear()
            if self._flush_timer and self._flush_timer.is_alive():
                self._flush_timer.cancel()
            self._flush_timer = None

        if self._client is None:
            return

        log_stream = datetime.now(timezone.utc).strftime("%Y/%m/%d")
        try:
            # Ensure the log stream exists
            try:
                self._client.create_log_stream(
                    logGroupName=self.log_group,
                    logStreamName=log_stream,
                )
            except self._client.exceptions.ResourceAlreadyExistsException:
                pass

            self._client.put_log_events(
                logGroupName=self.log_group,
                logStreamName=log_stream,
                logEvents=sorted(events, key=lambda e: e["timestamp"]),
            )
        except Exception as exc:
            logger.error("Failed to flush events to CloudWatch: %s", exc)
            # Re-queue events so they aren't lost silently
            with self._lock:
                self._pending_events = events + self._pending_events
