"""A small dependency-free MCP server for verified long-form writing audits.

The server intentionally coordinates files that already belong to one writing
project. It does not call a model or send manuscript content to a third party.
Agents receive bounded task prompts, submit explicit coverage receipts, and
cannot unlock reconciliation while required reviews are incomplete.
"""

from __future__ import annotations

import argparse
import json
import sys
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from .audit_queue import (
    claim_audit_task,
    get_reconciliation_task,
    list_audit_tasks,
    submit_audit_report,
)
from .compiler import compile_audit_prompt_text, compile_humanize_prompt_text
from .ledger import compile_ledger_extraction_prompt_text
from .linter import lint_text
from .longform import verify_long_form_package, write_long_form_audit
from .protection import compare_protected_content
from .skills import list_style_skills
from .statistics import analyze_style_statistics


SERVER_INFO = {"name": "advanced-human-writing", "version": "0.15.1"}
PROTOCOL_VERSION = "2025-03-26"
MAX_CONTEXT_CHARACTERS = 20000
MAX_TEXT_CHARACTERS = 80000

PROMPTS = [
    ("humanize-quick", "Compile a compact rewrite prompt for one supplied passage."),
    ("humanize-deep", "Compile a deeper rewrite prompt for one supplied passage."),
    ("dialogue-audit", "Compile a fiction dialogue, register, and response-linkage audit."),
    ("continuity-audit", "Compile a fiction continuity audit with physical and relationship checks."),
    ("style-match", "Compile a rewrite prompt with an explicit style direction."),
    ("serious-rewrite", "Compile a protected rewrite prompt for news, academic, legal, or technical prose."),
    ("extract-ledger", "Compile an evidence-backed continuity-ledger extraction prompt."),
]


def _tool(name: str, description: str, properties: dict[str, Any], required: list[str]) -> dict[str, Any]:
    return {
        "name": name,
        "description": description,
        "inputSchema": {
            "type": "object",
            "properties": properties,
            "required": required,
            "additionalProperties": False,
        },
    }


TOOLS = [
    _tool(
        "plan_long_form_audit",
        "Split a local manuscript or report into bounded review tasks, reports, and a verified agent plan.",
        {
            "draft_path": {"type": "string", "description": "Path relative to the configured project root."},
            "output_dir": {"type": "string", "description": "Empty package directory relative to the project root."},
            "style": {"type": "string", "enum": list_style_skills()},
            "context_path": {"type": "string", "description": "Optional outline, ledger, or report plan."},
            "reference_paths": {"type": "array", "items": {"type": "string"}},
            "source_paths": {"type": "array", "items": {"type": "string"}},
            "agent_mode": {"type": "string", "enum": ["standard", "deep"], "default": "deep"},
            "translationese": {"type": "boolean", "default": False},
            "chunk_size": {"type": "integer", "minimum": 2000},
        },
        ["draft_path", "output_dir", "style"],
    ),
    _tool(
        "list_audit_tasks",
        "List review tasks, dependencies, claims, receipt validity, and readiness for one audit package.",
        {"package_dir": {"type": "string"}},
        ["package_dir"],
    ),
    _tool(
        "claim_audit_task",
        "Claim one ready review task. The returned prompt is the complete bounded assignment for that agent.",
        {
            "package_dir": {"type": "string"},
            "task_id": {"type": "string"},
            "agent_id": {"type": "string", "default": "anonymous"},
        },
        ["package_dir", "task_id"],
    ),
    _tool(
        "submit_audit_report",
        "Submit a full review report. It must include a complete Coverage Receipt with no blocked material.",
        {
            "package_dir": {"type": "string"},
            "task_id": {"type": "string"},
            "report_markdown": {"type": "string"},
            "agent_id": {"type": "string", "default": "anonymous"},
        },
        ["package_dir", "task_id", "report_markdown"],
    ),
    _tool(
        "verify_audit_coverage",
        "Verify every required review report before final reconciliation. A blocked or incomplete receipt fails the gate.",
        {"package_dir": {"type": "string"}},
        ["package_dir"],
    ),
    _tool(
        "get_reconciliation_task",
        "Return the final cross-chapter reconciliation prompt only after coverage verification passes.",
        {"package_dir": {"type": "string"}},
        ["package_dir"],
    ),
    _tool(
        "read_project_context",
        "Read a bounded local outline, continuity ledger, source note, or approved style reference from the project root.",
        {
            "path": {"type": "string"},
            "max_characters": {"type": "integer", "minimum": 1, "maximum": MAX_CONTEXT_CHARACTERS, "default": 8000},
        },
        ["path"],
    ),
    _tool(
        "lint_text",
        "Run deterministic writing-pattern checks on supplied text and return evidence locations. This is not an authorship detector.",
        {
            "text": {"type": "string", "description": "Text to inspect; kept in the local MCP process."},
            "style": {"type": "string", "enum": ["general", *list_style_skills()], "default": "general"},
            "allow": {"type": "array", "items": {"type": "string"}, "default": []},
        },
        ["text"],
    ),
    _tool(
        "get_style_statistics",
        "Calculate language-aware sentence variation, lexical diversity, and transition density for supplied text.",
        {
            "text": {"type": "string", "description": "Text to analyze locally."},
            "style": {"type": "string", "enum": ["general", *list_style_skills()], "default": "general"},
        },
        ["text"],
    ),
    _tool(
        "verify_protected_content",
        "Compare source and rewritten text for changed numbers, citations, URLs, code, quotes, and named terms.",
        {
            "source_text": {"type": "string"},
            "candidate_text": {"type": "string"},
            "terms": {"type": "array", "items": {"type": "string"}, "default": []},
        },
        ["source_text", "candidate_text"],
    ),
    _tool(
        "compile_humanize_prompt",
        "Compile a local AI-ready humanization prompt from supplied text without sending it to a model.",
        {
            "draft": {"type": "string"},
            "style": {"type": "string", "enum": list_style_skills()},
            "mode": {"type": "string", "enum": ["quick", "deep"], "default": "quick"},
            "task": {"type": "string"},
            "context_text": {"type": "string"},
        },
        ["draft", "style"],
    ),
    _tool(
        "compile_audit_prompt",
        "Compile a bounded single-document audit prompt from supplied text without sending it to a model.",
        {
            "draft": {"type": "string"},
            "document_type": {"type": "string", "default": "auto"},
            "profiles": {"type": "array", "items": {"type": "string"}, "default": ["full"]},
            "context_text": {"type": "string"},
        },
        ["draft"],
    ),
    _tool(
        "compile_ledger_extraction",
        "Compile a candidate-ledger extraction prompt that separates observed facts from inference and requires evidence.",
        {
            "draft": {"type": "string"},
            "existing_ledger": {"type": "string"},
        },
        ["draft"],
    ),
]


def _safe_path(root: Path, value: str) -> Path:
    candidate = Path(value)
    resolved = candidate.resolve() if candidate.is_absolute() else (root / candidate).resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError("Path must stay within the configured project root.") from exc
    return resolved


def _path_list(root: Path, value: Any, label: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"{label} must be a list of project-relative paths.")
    return [str(_safe_path(root, item)) for item in value]


def _text_result(value: Any, is_error: bool = False) -> dict[str, Any]:
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=2)
    result: dict[str, Any] = {"content": [{"type": "text", "text": text}]}
    if is_error:
        result["isError"] = True
    return result


def call_tool(name: str, arguments: dict[str, Any], root: Path) -> dict[str, Any]:
    """Execute one project-local coordination operation and return MCP tool content."""

    if not isinstance(arguments, dict):
        raise ValueError("Tool arguments must be an object.")
    if name == "lint_text":
        text = _bounded_string(arguments, "text", MAX_TEXT_CHARACTERS)
        style = _optional_string(arguments, "style", "general")
        allow = _string_list(arguments, "allow")
        return _text_result(lint_text(text, style=style, allow=set(allow)).to_dict())
    if name == "get_style_statistics":
        text = _bounded_string(arguments, "text", MAX_TEXT_CHARACTERS)
        style = _optional_string(arguments, "style", "general")
        return _text_result(analyze_style_statistics(text, style=style).to_dict())
    if name == "verify_protected_content":
        source = _bounded_string(arguments, "source_text", MAX_TEXT_CHARACTERS)
        candidate = _bounded_string(arguments, "candidate_text", MAX_TEXT_CHARACTERS)
        return _text_result(compare_protected_content(source, candidate, terms=_string_list(arguments, "terms")).to_dict())
    if name == "compile_humanize_prompt":
        return _text_result(
            compile_humanize_prompt_text(
                _bounded_string(arguments, "draft", MAX_TEXT_CHARACTERS),
                style=_string(arguments, "style"),
                mode=_optional_string(arguments, "mode", "quick"),
                task=_optional_nullable_string(arguments, "task"),
                context_text=_optional_nullable_string(arguments, "context_text", MAX_CONTEXT_CHARACTERS),
            )
        )
    if name == "compile_audit_prompt":
        return _text_result(
            compile_audit_prompt_text(
                _bounded_string(arguments, "draft", MAX_TEXT_CHARACTERS),
                document_type=_optional_string(arguments, "document_type", "auto"),
                profiles=_string_list(arguments, "profiles") or ["full"],
                context_text=_optional_nullable_string(arguments, "context_text", MAX_CONTEXT_CHARACTERS),
            )
        )
    if name == "compile_ledger_extraction":
        return _text_result(
            compile_ledger_extraction_prompt_text(
                _bounded_string(arguments, "draft", MAX_TEXT_CHARACTERS),
                _optional_nullable_string(arguments, "existing_ledger", MAX_CONTEXT_CHARACTERS) or "",
            )
        )
    if name == "plan_long_form_audit":
        draft = _safe_path(root, _string(arguments, "draft_path"))
        output = _safe_path(root, _string(arguments, "output_dir"))
        context_value = arguments.get("context_path")
        context = _safe_path(root, context_value) if isinstance(context_value, str) else None
        chunk_size = arguments.get("chunk_size", 8000)
        if not isinstance(chunk_size, int):
            raise ValueError("chunk_size must be an integer.")
        mode = arguments.get("agent_mode", "deep")
        if not isinstance(mode, str):
            raise ValueError("agent_mode must be a string.")
        translationese = arguments.get("translationese", False)
        if not isinstance(translationese, bool):
            raise ValueError("translationese must be a boolean.")
        output_path, chunks = write_long_form_audit(
            str(draft),
            str(output),
            style=_string(arguments, "style"),
            context_path=str(context) if context else None,
            reference_paths=_path_list(root, arguments.get("reference_paths"), "reference_paths"),
            source_paths=_path_list(root, arguments.get("source_paths"), "source_paths"),
            chunk_size=chunk_size,
            agent_mode=mode,
            translationese=translationese,
        )
        return _text_result(
            {
                "package_dir": str(output_path),
                "chunk_count": len(chunks),
                "next_action": "Claim and complete the baseline task, then use list_audit_tasks to fan out ready reviews.",
            }
        )
    if name == "list_audit_tasks":
        return _text_result(list_audit_tasks(_safe_path(root, _string(arguments, "package_dir"))))
    if name == "claim_audit_task":
        return _text_result(
            claim_audit_task(
                _safe_path(root, _string(arguments, "package_dir")),
                _string(arguments, "task_id"),
                _optional_string(arguments, "agent_id", "anonymous"),
            )
        )
    if name == "submit_audit_report":
        return _text_result(
            submit_audit_report(
                _safe_path(root, _string(arguments, "package_dir")),
                _string(arguments, "task_id"),
                _string(arguments, "report_markdown"),
                _optional_string(arguments, "agent_id", "anonymous"),
            )
        )
    if name == "verify_audit_coverage":
        return _text_result(verify_long_form_package(str(_safe_path(root, _string(arguments, "package_dir")))))
    if name == "get_reconciliation_task":
        return _text_result(get_reconciliation_task(_safe_path(root, _string(arguments, "package_dir"))))
    if name == "read_project_context":
        path = _safe_path(root, _string(arguments, "path"))
        limit = arguments.get("max_characters", 8000)
        if not isinstance(limit, int) or not 1 <= limit <= MAX_CONTEXT_CHARACTERS:
            raise ValueError(f"max_characters must be between 1 and {MAX_CONTEXT_CHARACTERS}.")
        if not path.is_file():
            raise ValueError("Context path is not a file.")
        text = path.read_text(encoding="utf-8")
        return _text_result(
            {
                "path": str(path),
                "truncated": len(text) > limit,
                "content": text[:limit],
            }
        )
    raise ValueError(f"Unknown tool: {name}")


def _string(arguments: dict[str, Any], name: str) -> str:
    value = arguments.get(name)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string.")
    return value


def _optional_string(arguments: dict[str, Any], name: str, default: str) -> str:
    value = arguments.get(name, default)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string.")
    return value


def _optional_nullable_string(arguments: dict[str, Any], name: str, maximum: int | None = None) -> str | None:
    value = arguments.get(name)
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"{name} must be a string.")
    if maximum is not None and len(value) > maximum:
        raise ValueError(f"{name} must be at most {maximum} characters.")
    return value


def _bounded_string(arguments: dict[str, Any], name: str, maximum: int) -> str:
    value = _string(arguments, name)
    if len(value) > maximum:
        raise ValueError(f"{name} must be at most {maximum} characters.")
    return value


def _string_list(arguments: dict[str, Any], name: str) -> list[str]:
    value = arguments.get(name, [])
    if not isinstance(value, list) or not all(isinstance(item, str) and item.strip() for item in value):
        raise ValueError(f"{name} must be a list of non-empty strings.")
    return value


def _prompt_descriptors() -> list[dict[str, Any]]:
    return [
        {
            "name": name,
            "description": description,
            "arguments": [
                {"name": "draft", "description": "Text to analyze or rewrite.", "required": True},
                {"name": "style", "description": "Optional style such as fiction or news-report.", "required": False},
                {"name": "context", "description": "Optional ledger or prior-context text.", "required": False},
            ],
        }
        for name, description in PROMPTS
    ]


def get_prompt(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    draft = _bounded_string(arguments, "draft", MAX_TEXT_CHARACTERS)
    context = _optional_nullable_string(arguments, "context", MAX_CONTEXT_CHARACTERS)
    requested_style = _optional_string(arguments, "style", "fiction")
    if name == "humanize-quick":
        prompt = compile_humanize_prompt_text(draft, style=requested_style, context_text=context)
    elif name == "humanize-deep":
        prompt = compile_humanize_prompt_text(draft, style=requested_style, mode="deep", context_text=context)
    elif name == "dialogue-audit":
        prompt = compile_audit_prompt_text(
            draft,
            document_type="fiction",
            profiles=["voice", "register"],
            context_text=context,
        )
    elif name == "continuity-audit":
        prompt = compile_audit_prompt_text(
            draft,
            document_type="fiction",
            profiles=["full"],
            strict_continuity=True,
            context_text=context,
        )
    elif name == "style-match":
        prompt = compile_humanize_prompt_text(
            draft,
            style=requested_style,
            task="Rewrite with the explicitly supplied style direction while preserving facts and avoiding phrase copying.",
            context_text=context,
        )
    elif name == "serious-rewrite":
        prompt = compile_humanize_prompt_text(
            draft,
            style=requested_style if requested_style != "fiction" else "news-report",
            context_text=context,
            protect_content=True,
        )
    elif name == "extract-ledger":
        prompt = compile_ledger_extraction_prompt_text(draft, context or "")
    else:
        raise ValueError(f"Unknown prompt: {name}")
    return {
        "description": dict(PROMPTS)[name],
        "messages": [{"role": "user", "content": {"type": "text", "text": prompt}}],
    }


def handle_message(message: dict[str, Any], root: Path) -> dict[str, Any] | None:
    """Handle the MCP methods needed by current Agent hosts."""

    request_id = message.get("id")
    method = message.get("method")
    if not isinstance(method, str):
        return _error(request_id, -32600, "Invalid Request: method is required")
    if method == "notifications/initialized":
        return None
    if method == "initialize":
        return _result(
            request_id,
            {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {"tools": {"listChanged": False}, "prompts": {"listChanged": False}},
                "serverInfo": SERVER_INFO,
                "instructions": "Use project-local paths only. Plan bounded reviews, submit complete receipts, verify coverage, then reconcile.",
            },
        )
    if method == "ping":
        return _result(request_id, {})
    if method == "tools/list":
        return _result(request_id, {"tools": TOOLS})
    if method == "prompts/list":
        return _result(request_id, {"prompts": _prompt_descriptors()})
    if method == "prompts/get":
        params = message.get("params", {})
        if not isinstance(params, dict) or not isinstance(params.get("name"), str):
            return _error(request_id, -32602, "prompts/get requires a prompt name")
        try:
            return _result(request_id, get_prompt(params["name"], params.get("arguments", {})))
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            return _result(request_id, _text_result(f"{type(exc).__name__}: {exc}", is_error=True))
    if method == "tools/call":
        params = message.get("params", {})
        if not isinstance(params, dict) or not isinstance(params.get("name"), str):
            return _error(request_id, -32602, "tools/call requires a tool name")
        try:
            return _result(request_id, call_tool(params["name"], params.get("arguments", {}), root))
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            return _result(request_id, _text_result(f"{type(exc).__name__}: {exc}", is_error=True))
    return _error(request_id, -32601, f"Method not found: {method}")


def _result(request_id: Any, result: dict[str, Any]) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def _error(request_id: Any, code: int, message: str) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}


def run_stdio(root: Path) -> None:
    for line in sys.stdin:
        try:
            message = json.loads(line)
            if not isinstance(message, dict):
                raise ValueError("JSON-RPC messages must be objects.")
            response = handle_message(message, root)
        except (ValueError, json.JSONDecodeError) as exc:
            response = _error(None, -32700, f"Parse error: {exc}")
        if response is not None:
            print(json.dumps(response, ensure_ascii=False), flush=True)


def _http_handler(root: Path, auth_token: str | None):
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self) -> None:  # noqa: N802 - HTTP method name is defined by BaseHTTPRequestHandler.
            if self.path != "/mcp":
                self.send_error(HTTPStatus.NOT_FOUND)
                return
            if auth_token and self.headers.get("Authorization") != f"Bearer {auth_token}":
                self.send_error(HTTPStatus.UNAUTHORIZED)
                return
            length = self.headers.get("Content-Length")
            try:
                body_length = int(length) if length else 0
                message = json.loads(self.rfile.read(body_length))
                if not isinstance(message, dict):
                    raise ValueError("JSON-RPC messages must be objects.")
                response = handle_message(message, root)
            except (ValueError, json.JSONDecodeError) as exc:
                response = _error(None, -32700, f"Parse error: {exc}")
            if response is None:
                self.send_response(HTTPStatus.ACCEPTED)
                self.end_headers()
                return
            payload = json.dumps(response, ensure_ascii=False).encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def log_message(self, format: str, *args: Any) -> None:
            return

    return Handler


def run_http(root: Path, host: str, port: int, auth_token: str | None) -> None:
    if host not in {"127.0.0.1", "::1", "localhost"} and not auth_token:
        raise ValueError("A non-loopback HTTP server requires --auth-token.")
    server = ThreadingHTTPServer((host, port), _http_handler(root, auth_token))
    print(f"Human Writing MCP listening on http://{host}:{port}/mcp", file=sys.stderr)
    server.serve_forever()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="human-writing-mcp",
        description="Serve verified, project-local long-form writing audit tools over MCP.",
    )
    parser.add_argument("--root", default=".", help="Workspace root allowed to the MCP server. Default: current directory.")
    parser.add_argument("--http", action="store_true", help="Serve a JSON MCP endpoint instead of stdio.")
    parser.add_argument("--host", default="127.0.0.1", help="HTTP bind host. Default: 127.0.0.1.")
    parser.add_argument("--port", type=int, default=8765, help="HTTP bind port. Default: 8765.")
    parser.add_argument("--auth-token", help="Bearer token required for HTTP requests. Required on non-loopback hosts.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = Path(args.root).resolve()
    if not root.is_dir():
        raise SystemExit("--root must be an existing directory.")
    if args.http:
        try:
            run_http(root, args.host, args.port, args.auth_token)
        except ValueError as exc:
            raise SystemExit(str(exc)) from exc
        return 0
    run_stdio(root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
