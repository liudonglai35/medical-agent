#!/usr/bin/env python3
"""Persistent execution adapter for the Medical Agent project.

This is the bridge between the external supervisor and the engineering agent.
The supervisor must provide AGENT_COMMAND. The command is intentionally explicit:
this script never invents privileged actions or silently calls an external service.

Expected contract for AGENT_COMMAND:
- work in the checked-out repository;
- read PROJECT_STATE.json and continue the highest-priority executable task;
- update heartbeat_at / last_progress_at / task_status / next_task / artifacts;
- run tests after changes;
- exit 0 after a valid checkpoint, non-zero on failure.
"""
from __future__ import annotations

import json
import os
import shlex
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

STATE = Path(os.environ.get("PROJECT_STATE", "PROJECT_STATE.json"))
COMMAND = os.environ.get("AGENT_COMMAND", "").strip()


def timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def load() -> dict:
    with STATE.open("r", encoding="utf-8") as f:
        return json.load(f)


def save(data: dict) -> None:
    tmp = STATE.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(STATE)


def main() -> int:
    if not STATE.exists():
        print("ERROR: PROJECT_STATE.json not found", file=sys.stderr)
        return 2
    if not COMMAND:
        print("ERROR: AGENT_COMMAND is not configured; persistent executor is not installed", file=sys.stderr)
        return 20

    state = load()
    if state.get("human_intervention_required") or state.get("task_status") == "WAITING_FOR_HUMAN":
        print("WAITING_FOR_HUMAN: executor will not bypass human approval")
        return 0

    state["task_status"] = "RUNNING"
    state["heartbeat_at"] = timestamp()
    state["last_tool_call_at"] = timestamp()
    state["last_error"] = None
    state["blocked_reason"] = None
    save(state)

    print(f"EXECUTOR: starting {COMMAND}")
    try:
        completed = subprocess.run(
            shlex.split(COMMAND),
            cwd=Path.cwd(),
            check=False,
            text=True,
        )
    except Exception as exc:
        state = load()
        state["task_status"] = "AGENT_DEAD"
        state["last_error"] = f"executor launch failure: {exc}"
        state["recovery_attempts"] = int(state.get("recovery_attempts", 0)) + 1
        state["heartbeat_at"] = timestamp()
        save(state)
        return 21

    state = load()
    state["heartbeat_at"] = timestamp()
    state["last_tool_call_at"] = timestamp()
    if completed.returncode == 0:
        state["last_progress_at"] = timestamp()
        state["last_error"] = None
        # The agent owns semantic task completion. If it did not explicitly
        # complete the task, keep it RUNNING for the next watchdog cycle.
        if state.get("task_status") not in {"COMPLETED", "WAITING_FOR_HUMAN"}:
            state["task_status"] = "RUNNING"
    else:
        state["task_status"] = "FAILED"
        state["last_error"] = f"AGENT_COMMAND exited with code {completed.returncode}"
        state["retry_count"] = int(state.get("retry_count", 0)) + 1
        state["recovery_attempts"] = int(state.get("recovery_attempts", 0)) + 1
    save(state)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
