import json
import unittest

from humanwriting.linter import format_lint_report, lint_text


class LinterTests(unittest.TestCase):
    def test_reports_evidence_location_and_transparent_score(self):
        report = lint_text(
            "普通开头。\n命运的齿轮开始转动，空气仿佛凝固。",
            style="fiction",
        )
        rule_ids = {finding.rule_id for finding in report.findings}
        self.assertIn("LEX002", rule_ids)
        self.assertIn("ATM001", rule_ids)
        fate = next(finding for finding in report.findings if finding.rule_id == "LEX002")
        self.assertEqual((fate.line, fate.column), (2, 1))
        self.assertGreater(report.score, 0)
        self.assertIn("not evidence of AI authorship", report.disclaimer)

    def test_masks_code_blocks_block_quotes_and_urls(self):
        report = lint_text(
            "```text\n命运的齿轮开始转动\n```\n"
            "> 空气仿佛凝固\n"
            "https://example.com/delve\n"
            "正文很平静。",
            style="fiction",
        )
        self.assertEqual(report.findings, ())

    def test_allowlist_suppresses_rule_or_category(self):
        by_rule = lint_text("命运的齿轮开始转动。", style="fiction", allow={"LEX002"})
        by_category = lint_text(
            "命运的齿轮开始转动。",
            style="fiction",
            allow={"inflated-vocabulary"},
        )
        self.assertEqual(by_rule.findings, ())
        self.assertEqual(by_category.findings, ())

    def test_false_precision_is_genre_aware(self):
        fiction = lint_text("她的手向上移动了三厘米。", style="fiction")
        academic = lint_text("伤口长度为三厘米。", style="academic-paper")
        forensic_fiction = lint_text("法医鉴定报告写明，伤口长2.3厘米。", style="fiction")
        self.assertIn("PREC001", {finding.rule_id for finding in fiction.findings})
        self.assertNotIn("PREC001", {finding.rule_id for finding in academic.findings})
        self.assertNotIn("PREC001", {finding.rule_id for finding in forensic_fiction.findings})

    def test_json_output_contains_structured_spans(self):
        report = lint_text("In today's fast-paced world, let's dive in.")
        payload = json.loads(format_lint_report(report, "json"))
        self.assertIn("score", payload)
        self.assertIn("findings", payload)
        self.assertIn("start", payload["findings"][0])
        self.assertIn("line", payload["findings"][0])


if __name__ == "__main__":
    unittest.main()
