"""Decision logger — JSON Lines format per execution run."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


class DecisionLogger:
    """
    Appends one JSON object per decision to a .jsonl file.

    File naming: {decision_log_path}/{execution_id}.jsonl
    Each line is a serialized DecisionLogEntry.
    """

    def __init__(self, decision_log_path: Path | str) -> None:
        self.decision_log_path = Path(decision_log_path)
        self.decision_log_path.mkdir(parents=True, exist_ok=True)
        self._execution_id: str | None = None
        self._file_handle: Any = None

    @property
    def execution_id(self) -> str:
        if self._execution_id is None:
            raise RuntimeError("Execution ID not set. Call attach_to_execution() first.")
        return self._execution_id

    @execution_id.setter
    def execution_id(self, value: str) -> None:
        self._execution_id = value

    def attach_to_execution(self, execution_id: str) -> None:
        """Associate this logger with a specific execution."""
        self._execution_id = execution_id
        log_file = self._log_file()
        self._file_handle = open(log_file, "a", encoding="utf-8")
        logger.debug("decision_logger_attached", execution_id=execution_id, path=str(log_file))

    def _log_file(self) -> Path:
        return self.decision_log_path / f"{self.execution_id}.jsonl"

    def log(
        self,
        stage: str,
        category: str,
        subject: str,
        options_considered: list[dict[str, Any]] | None = None,
        selected: str = "",
        reason: str = "",
        confidence: float = 1.0,
        user_visible: bool = True,
        user_approved: bool = False,
    ) -> str:
        """Append a decision entry to the JSONL file. Returns the decision_id."""
        if self._file_handle is None:
            raise RuntimeError("Logger not attached to execution. Call attach_to_execution() first.")

        decision_id = f"dec-{uuid.uuid4().hex[:8]}"
        entry = {
            "decision_id": decision_id,
            "execution_id": self.execution_id,
            "stage": stage,
            "category": category,
            "subject": subject,
            "options_considered": options_considered or [],
            "selected": selected,
            "reason": reason,
            "confidence": confidence,
            "user_visible": user_visible,
            "user_approved": user_approved,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        line = json.dumps(entry, ensure_ascii=False)
        self._file_handle.write(line + "\n")
        self._file_handle.flush()
        logger.debug("decision_logged", decision_id=decision_id, stage=stage, category=category)
        return decision_id

    def close(self) -> None:
        """Close the file handle."""
        if self._file_handle is not None:
            self._file_handle.close()
            self._file_handle = None

    def read(self, execution_id: str | None = None) -> list[dict[str, Any]]:
        """Read all decision entries for an execution."""
        eid = execution_id or self.execution_id
        log_file = self.decision_log_path / f"{eid}.jsonl"
        if not log_file.exists():
            return []

        entries = []
        with open(log_file, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    entries.append(json.loads(line))
        return entries

    def __enter__(self) -> "DecisionLogger":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()