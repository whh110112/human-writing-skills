import io
import json
import sys
import unittest
from contextlib import redirect_stdout

from humanwriting.cli import main


class CliIntegrationTests(unittest.TestCase):
    def run_cli(self, arguments, stdin_text=""):
        output = io.StringIO()
        previous_stdin = sys.stdin
        sys.stdin = io.StringIO(stdin_text)
        try:
            with redirect_stdout(output):
                code = main(arguments)
        finally:
            sys.stdin = previous_stdin
        return code, output.getvalue()

    def test_lint_reads_stdin_and_emits_github_annotations(self):
        code, output = self.run_cli(
            ["lint", "--draft", "-", "--style", "fiction", "--format", "github"],
            "未来可期。",
        )
        self.assertEqual(code, 0)
        self.assertIn("::warning file=stdin.md", output)
        self.assertIn("CLOSE001", output)

    def test_rule_catalog_has_machine_readable_ids(self):
        code, output = self.run_cli(["list", "--kind", "rule", "--format", "json"])
        catalog = json.loads(output)
        self.assertEqual(code, 0)
        self.assertIn("END002", {item["id"] for item in catalog})
        self.assertIn("ARG001", {item["id"] for item in catalog})

    def test_extract_ledger_accepts_stdin(self):
        code, output = self.run_cli(
            ["extract-ledger", "--draft", "-"],
            "Mara keeps the key and promises to return before dawn.",
        )
        self.assertEqual(code, 0)
        self.assertIn("Continuity Ledger Extraction", output)
        self.assertIn("evidence", output)


if __name__ == "__main__":
    unittest.main()
