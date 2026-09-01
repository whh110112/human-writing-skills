import json
import threading
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.request import Request, urlopen

from http.server import ThreadingHTTPServer

from humanwriting.mcp_server import TOOLS, _http_handler, call_tool, handle_message


def complete_report(task_id: str) -> str:
    return (
        "# Review Findings\n\n"
        "No contradiction was found in the assigned material.\n\n"
        "# Coverage Receipt\n\n"
        f"- Task ID: `{task_id}`\n"
        "- Scope: assigned body\n"
        "- Coverage: complete\n"
        "- Units checked: every assigned paragraph\n"
        "- Confirmed findings: 0\n"
        "- Unchecked or blocked material: none\n"
    )


class McpServerTests(unittest.TestCase):
    def test_initialize_lists_tools_and_blocks_path_escape(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            initialized = handle_message(
                {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}, root
            )
            listed = handle_message({"jsonrpc": "2.0", "id": 2, "method": "tools/list"}, root)
            escaped = handle_message(
                {
                    "jsonrpc": "2.0",
                    "id": 3,
                    "method": "tools/call",
                    "params": {
                        "name": "read_project_context",
                        "arguments": {"path": "../outside.md"},
                    },
                },
                root,
            )

        self.assertEqual(initialized["result"]["serverInfo"]["name"], "advanced-human-writing")
        self.assertEqual(len(listed["result"]["tools"]), len(TOOLS))
        self.assertTrue(escaped["result"]["isError"])
        self.assertIn("within the configured project root", escaped["result"]["content"][0]["text"])

    def test_agents_claim_submit_verify_then_unlock_reconciliation(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            draft = root / "novel.md"
            ledger = root / "ledger.md"
            draft.write_text(
                ("“你要走吗？”她问。\n\n他没有回答。\n\n" + "雨落在窗外。" * 300)
                + ("\n\n" + "他沿着河岸继续走。" + "天色渐暗。" * 300),
                encoding="utf-8",
            )
            ledger.write_text("两人仍因信件争执。", encoding="utf-8")
            plan_result = call_tool(
                "plan_long_form_audit",
                {
                    "draft_path": "novel.md",
                    "output_dir": "audit",
                    "style": "fiction",
                    "context_path": "ledger.md",
                    "agent_mode": "deep",
                    "chunk_size": 2000,
                },
                root,
            )
            package = Path(json.loads(plan_result["content"][0]["text"])["package_dir"])
            listed = json.loads(
                call_tool("list_audit_tasks", {"package_dir": "audit"}, root)["content"][0]["text"]
            )
            baseline = next(task for task in listed["tasks"] if task["task_id"] == "baseline")
            self.assertTrue(baseline["ready"])
            with self.assertRaisesRegex(ValueError, "not ready"):
                call_tool(
                    "claim_audit_task",
                    {"package_dir": "audit", "task_id": "reconcile", "agent_id": "final-editor"},
                    root,
                )

            plan = json.loads((package / "agent-plan.json").read_text(encoding="utf-8"))
            for task in plan["tasks"]:
                if not task["required_before_reconciliation"]:
                    continue
                agent_id = f"worker-{task['task_id']}"
                call_tool(
                    "claim_audit_task",
                    {"package_dir": "audit", "task_id": task["task_id"], "agent_id": agent_id},
                    root,
                )
                call_tool(
                    "submit_audit_report",
                    {
                        "package_dir": "audit",
                        "task_id": task["task_id"],
                        "agent_id": agent_id,
                        "report_markdown": complete_report(task["task_id"]),
                    },
                    root,
                )

            verification = json.loads(
                call_tool("verify_audit_coverage", {"package_dir": "audit"}, root)["content"][0]["text"]
            )
            reconciliation = json.loads(
                call_tool("get_reconciliation_task", {"package_dir": "audit"}, root)["content"][0]["text"]
            )
            state = json.loads((package / "agent-state.json").read_text(encoding="utf-8"))

        self.assertTrue(verification["ready_for_reconciliation"])
        self.assertEqual(reconciliation["task_id"], "reconcile")
        self.assertIn("Reconciliation", reconciliation["content"])
        self.assertEqual(len(state["tasks"]), verification["planned"])

    def test_submit_rejects_a_blocked_receipt(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            draft = root / "draft.md"
            draft.write_text("正文。" * 1200, encoding="utf-8")
            call_tool(
                "plan_long_form_audit",
                {"draft_path": "draft.md", "output_dir": "audit", "style": "fiction", "chunk_size": 2000},
                root,
            )
            with self.assertRaisesRegex(ValueError, "coverage is blocked"):
                call_tool(
                    "submit_audit_report",
                    {
                        "package_dir": "audit",
                        "task_id": "baseline",
                        "report_markdown": complete_report("baseline").replace(
                            "Coverage: complete", "Coverage: blocked"
                        ),
                    },
                    root,
                )

    def test_tampered_task_report_path_cannot_leave_audit_package(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            draft = root / "draft.md"
            draft.write_text("正文。" * 1200, encoding="utf-8")
            call_tool(
                "plan_long_form_audit",
                {"draft_path": "draft.md", "output_dir": "audit", "style": "fiction", "chunk_size": 2000},
                root,
            )
            plan_path = root / "audit" / "agent-plan.json"
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
            plan["tasks"][0]["report"] = "../outside.md"
            plan_path.write_text(json.dumps(plan), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "within the audit package"):
                call_tool("list_audit_tasks", {"package_dir": "audit"}, root)

    def test_http_transport_requires_bearer_token_and_serves_mcp(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            server = ThreadingHTTPServer(("127.0.0.1", 0), _http_handler(root, "test-token"))
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            port = server.server_address[1]
            payload = json.dumps(
                {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
            ).encode("utf-8")
            request = Request(
                f"http://127.0.0.1:{port}/mcp",
                data=payload,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": "Bearer test-token",
                },
                method="POST",
            )
            try:
                with urlopen(request, timeout=5) as response:
                    received = json.loads(response.read())
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

        self.assertEqual(received["result"]["serverInfo"]["name"], "advanced-human-writing")


if __name__ == "__main__":
    unittest.main()
