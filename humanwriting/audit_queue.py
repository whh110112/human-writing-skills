"""Durable task coordination for externally run long-form reviewers.

The queue stores only task ownership and receipt metadata. Drafts and reviewer
reports remain in the package created by :mod:`humanwriting.longform`, so a
project can be inspected and repaired without a database service.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .longform import validate_long_form_report, verify_long_form_package


STATE_FILENAME = "agent-state.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _load_plan(package_dir: str | Path) -> tuple[Path, dict[str, Any], list[dict[str, Any]]]:
    package = Path(package_dir).resolve()
    plan_path = package / "agent-plan.json"
    if not plan_path.is_file():
        raise ValueError("Chunk audit package is missing agent-plan.json.")
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    tasks = plan.get("tasks")
    if not isinstance(tasks, list) or not all(isinstance(task, dict) for task in tasks):
        raise ValueError("Chunk audit agent plan contains no valid tasks.")
    return package, plan, tasks


def _find_task(tasks: list[dict[str, Any]], task_id: str) -> dict[str, Any]:
    for task in tasks:
        if task.get("task_id") == task_id:
            return task
    raise ValueError(f"Unknown audit task: {task_id}")


def _state_path(package: Path) -> Path:
    return package / STATE_FILENAME


def _package_path(package: Path, value: str, label: str) -> Path:
    candidate = (package / value).resolve()
    try:
        candidate.relative_to(package)
    except ValueError as exc:
        raise ValueError(f"Task {label} must stay within the audit package.") from exc
    return candidate


def _load_state(package: Path) -> dict[str, Any]:
    state_path = _state_path(package)
    if not state_path.exists():
        return {"schema": 1, "tasks": {}}
    state = json.loads(state_path.read_text(encoding="utf-8"))
    if not isinstance(state, dict) or not isinstance(state.get("tasks"), dict):
        raise ValueError("Agent state file is malformed.")
    return state


def _write_state(package: Path, state: dict[str, Any]) -> None:
    state_path = _state_path(package)
    temporary = state_path.with_suffix(".tmp")
    temporary.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(state_path)


def _report_error(package: Path, task: dict[str, Any]) -> str | None:
    report_value = task.get("report")
    if not isinstance(report_value, str):
        return "no report path"
    report_path = _package_path(package, report_value, "report path")
    if not report_path.is_file():
        return "report is missing"
    return validate_long_form_report(task, report_path.read_text(encoding="utf-8"))


def _dependency_error(package: Path, tasks: list[dict[str, Any]], task: dict[str, Any]) -> str | None:
    for dependency_id in task.get("depends_on", []):
        dependency = _find_task(tasks, dependency_id)
        error = _report_error(package, dependency)
        if error:
            return f"dependency {dependency_id} is not complete: {error}"
    if task.get("required_before_reconciliation") is False:
        coverage = verify_long_form_package(str(package))
        if not coverage["ready_for_reconciliation"]:
            return "coverage verification has not passed"
    return None


def list_audit_tasks(package_dir: str | Path) -> dict[str, Any]:
    """Return planned tasks with live, deterministic readiness information."""

    package, plan, tasks = _load_plan(package_dir)
    state = _load_state(package)
    rows: list[dict[str, Any]] = []
    for task in tasks:
        task_id = str(task.get("task_id", "unknown"))
        error = _dependency_error(package, tasks, task)
        receipt_error = _report_error(package, task)
        entry = state["tasks"].get(task_id, {})
        rows.append(
            {
                "task_id": task_id,
                "kind": task.get("kind"),
                "chunk_index": task.get("chunk_index"),
                "depends_on": task.get("depends_on", []),
                "report": task.get("report"),
                "status": entry.get("status", "pending"),
                "agent_id": entry.get("agent_id"),
                "ready": error is None and receipt_error is not None,
                "dependency_error": error,
                "receipt_error": receipt_error,
            }
        )
    return {
        "package_dir": str(package),
        "mode": plan.get("mode", "unknown"),
        "tasks": rows,
    }


def claim_audit_task(package_dir: str | Path, task_id: str, agent_id: str = "anonymous") -> dict[str, Any]:
    """Claim a ready task so parallel reviewers do not duplicate one another."""

    package, _, tasks = _load_plan(package_dir)
    task = _find_task(tasks, task_id)
    dependency_error = _dependency_error(package, tasks, task)
    if dependency_error:
        raise ValueError(f"Task {task_id} is not ready: {dependency_error}")
    if _report_error(package, task) is None:
        raise ValueError(f"Task {task_id} already has a valid completed report.")

    state = _load_state(package)
    current = state["tasks"].get(task_id, {})
    current_agent = current.get("agent_id")
    if current.get("status") == "claimed" and current_agent != agent_id:
        raise ValueError(f"Task {task_id} is already claimed by {current_agent}.")
    state["tasks"][task_id] = {
        "status": "claimed",
        "agent_id": agent_id,
        "claimed_at": _utc_now(),
    }
    _write_state(package, state)
    return {
        "task_id": task_id,
        "agent_id": agent_id,
        "prompt": task.get("prompt"),
        "report": task.get("report"),
        "instructions": "Write the full reviewer report, including a complete Coverage Receipt, then submit it with submit_audit_report.",
    }


def submit_audit_report(
    package_dir: str | Path,
    task_id: str,
    report_markdown: str,
    agent_id: str = "anonymous",
) -> dict[str, Any]:
    """Store a reviewer report only when its receipt proves complete coverage."""

    package, _, tasks = _load_plan(package_dir)
    task = _find_task(tasks, task_id)
    dependency_error = _dependency_error(package, tasks, task)
    if dependency_error:
        raise ValueError(f"Task {task_id} cannot be submitted: {dependency_error}")
    receipt_error = validate_long_form_report(task, report_markdown)
    if receipt_error:
        raise ValueError(f"Task {task_id} report is invalid: {receipt_error}")

    state = _load_state(package)
    current = state["tasks"].get(task_id, {})
    current_agent = current.get("agent_id")
    if current.get("status") == "claimed" and current_agent != agent_id:
        raise ValueError(f"Task {task_id} is claimed by {current_agent}; {agent_id} cannot submit it.")

    report_value = task.get("report")
    if not isinstance(report_value, str):
        raise ValueError(f"Task {task_id} has no report path.")
    report_path = _package_path(package, report_value, "report path")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report_markdown.rstrip() + "\n", encoding="utf-8")
    digest = hashlib.sha256(report_markdown.encode("utf-8")).hexdigest()
    state["tasks"][task_id] = {
        "status": "submitted",
        "agent_id": agent_id,
        "submitted_at": _utc_now(),
        "report_sha256": digest,
    }
    _write_state(package, state)
    return {
        "task_id": task_id,
        "report": report_value,
        "report_sha256": digest,
        "status": "submitted",
    }


def get_reconciliation_task(package_dir: str | Path) -> dict[str, Any]:
    """Return the final editor task only after every required receipt has passed."""

    package, _, tasks = _load_plan(package_dir)
    verification = verify_long_form_package(str(package))
    if not verification["ready_for_reconciliation"]:
        raise ValueError("Coverage verification has not passed; reconciliation is unavailable.")
    reconciliation = next(
        (task for task in tasks if task.get("required_before_reconciliation") is False),
        None,
    )
    if reconciliation is None:
        raise ValueError("Chunk audit package has no reconciliation task.")
    prompt_value = reconciliation.get("prompt")
    if not isinstance(prompt_value, str):
        raise ValueError("Reconciliation task has no prompt path.")
    prompt_path = _package_path(package, prompt_value, "prompt path")
    if not prompt_path.is_file():
        raise ValueError("Reconciliation prompt is missing from the package.")
    return {
        "task_id": reconciliation.get("task_id"),
        "prompt": reconciliation.get("prompt"),
        "report": reconciliation.get("report"),
        "content": prompt_path.read_text(encoding="utf-8"),
        "verification": verification,
    }
