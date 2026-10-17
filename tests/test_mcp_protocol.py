import io
import json
import threading
import unittest
from contextlib import redirect_stdout
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from humanwriting.mcp_server import MAX_HTTP_BODY_BYTES, _http_handler, handle_message, run_stdio


class McpProtocolTests(unittest.TestCase):
    def test_malformed_prompt_does_not_kill_stdio_server(self):
        messages = [
            {"jsonrpc": "2.0", "id": 1, "method": "prompts/get", "params": {"name": "humanize-quick", "arguments": None}},
            {"jsonrpc": "2.0", "id": 2, "method": "ping"},
        ]
        output = io.StringIO()
        with patch("sys.stdin", io.StringIO("\n".join(map(json.dumps, messages)))), redirect_stdout(output):
            run_stdio(Path.cwd())
        responses = list(map(json.loads, output.getvalue().splitlines()))
        self.assertEqual(responses[0]["error"]["code"], -32602)
        self.assertEqual(responses[1]["result"], {})

    def test_batches_notifications_and_invalid_envelopes(self):
        root = Path.cwd()
        notification = {"jsonrpc": "2.0", "method": "notifications/cancelled"}
        ping = {"jsonrpc": "2.0", "id": 3, "method": "ping"}
        self.assertIsNone(handle_message(notification, root))
        self.assertIsNone(handle_message([notification], root))
        self.assertEqual(handle_message([notification, ping], root), [handle_message(ping, root)])
        for invalid in ([], 3, {"method": "ping"}, {"jsonrpc": "2.0", "id": {}, "method": "ping"}):
            self.assertEqual(handle_message(invalid, root)["error"]["code"], -32600)

    def test_http_origin_auth_lengths_and_methods(self):
        with TemporaryDirectory() as directory:
            server = ThreadingHTTPServer(("127.0.0.1", 0), _http_handler(Path(directory), "secret"))
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            def request(method="POST", extra=None, body=b'{}'):
                headers = {"Content-Type": "application/json", "Authorization": "Bearer secret"}
                headers.update(extra or {})
                conn = HTTPConnection(*server.server_address, timeout=5)
                try:
                    conn.request(method, "/mcp", body=body, headers=headers)
                    response = conn.getresponse()
                    response.read()
                    return response.status
                finally:
                    conn.close()
            try:
                self.assertEqual(request(extra={"Origin": "https://untrusted.example"}), 403)
                self.assertEqual(request(extra={"Authorization": "Bearer wrong"}), 401)
                self.assertEqual(request(extra={"Content-Length": "-1"}), 400)
                self.assertEqual(request(extra={"Content-Length": "abc"}), 400)
                self.assertEqual(request(extra={"Content-Length": str(MAX_HTTP_BODY_BYTES + 1)}), 413)
                self.assertEqual(request(extra={"Content-Type": "text/plain"}), 415)
                self.assertEqual(request(method="GET"), 405)
                self.assertEqual(request(body=b'{"jsonrpc":"2.0","method":"notifications/cancelled"}'), 202)
                self.assertEqual(request(body=b'{"jsonrpc":"2.0","id":1,"method":"ping"}'), 200)
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)
