#!/usr/bin/env python3
"""Medical Agent project execution watchdog.

This process monitors execution continuity. It does not force an iteration every
10 minutes. A healthy task is left alone; a stalled/failed task is classified
for recovery. Actual task execution is intentionally separated from monitoring.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

STATE_PATH = Path(os.environ.get("PROJECT_STATE", "PROJECT_STATE.json"))
STALL_SECONDS = int(os.environ.get("STALL_SECONDS", "1200"))


def now() -> datetime:
    return datetime.now(timezone.utc)


def parse_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def load_state() -> dict:
    with STATE_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def classify(state: dict) -> tuple[str, str]:
    status = state.get("task_status")
    if state.get("human_intervention_required") or status == "WAITING_FOR_HUMAN":
        return "WAITING_FOR_HUMAN", "human decision/approval is required; do not auto-recover"
    if status in {"COMPLETED", "IDLE"}:
        return status, "no active execution requiring recovery"
    if status == "FAILED":
        return "RECOVERY_REQUIRED", "task reports FAILED"
    progress = parse_ts(state.get("last_progress_at"))
    heartbeat = parse_ts(state.get("heartbeat_at"))
    current = now()
    if status == "RUNNING":
        if heartbeat is None:
            return "RECOVERY_REQUIRED", "RUNNING without heartbeat"
        if (current - heartbeat).total_seconds() > STALL_SECONDS:
            return "RECOVERY_REQUIRED", "heartbeat is stale"
        if progress is None:
            return "RECOVERY_REQUIRED", "RUNNING without last_progress_at"
        if (current - progress).total_seconds() > STALL_SECONDS:
            return "RECOVERY_REQUIRED", "no effective progress within stall threshold"
        return "HEALTHY", "heartbeat and effective progress are current"
    if status in {"STALLED", "BLOCKED", "AGENT_DEAD", "TOOL_ERROR", "ENV_ERROR"}:
        return "RECOVERY_REQUIRED", f"task status is {status}"
    return "REVIEW_REQUIRED", f"unknown task status: {status!r}"


def main() -> int:
    if not STATE_PATH.exists():
        print(f"ERROR: state file not found: {STATE_PATH}")
        return 2
    try:
        state = load_state()
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: cannot load project state: {exc}")
        return 2

    classification, reason = classify(state)
    print(f"watchdog={classification}; reason={reason}")

    # CI-safe behavior: monitoring never silently mutates project state.
    # Recovery is delegated to an execution/recovery service in a later phase.
    if classification == "RECOVERY_REQUIRED":
        print("ACTION: recovery required; invoke the configured execution/recovery runner.")
        return 10
    if classification == "REVIEW_REQUIRED":
        return 11
    return 0


if __name__ == "__main__":
    sys.exit(main())
