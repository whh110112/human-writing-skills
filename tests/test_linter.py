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

    def test_reports_dense_imagery_fragment_runs_and_detail_inventory(self):
        text = (
            "他三十八岁，身高一米八，体重七十五公斤，职业是律师。\n\n"
            "雨像旧胶片，灯仿佛一只眼，门如同一张嘴，风宛如叹息。\n\n"
            "深圳。\n\n酒店。\n\n深夜。\n\n电话响了。"
        )
        report = lint_text(text, style="fiction")
        rule_ids = {finding.rule_id for finding in report.findings}
        self.assertTrue({"INFO001", "IMG001", "PARA001"} <= rule_ids)

    def test_new_texture_rules_do_not_run_for_serious_styles(self):
        text = "患者三十八岁，身高一米八，体重七十五公斤，职业是律师。"
        report = lint_text(text, style="academic-paper")
        self.assertFalse({"INFO001", "IMG001", "PARA001"} & {item.rule_id for item in report.findings})

    def test_allowlist_suppresses_structural_texture_rules(self):
        text = "雨像旧胶片，灯仿佛一只眼，门如同一张嘴，风宛如叹息。"
        by_rule = lint_text(text, style="fiction", allow={"IMG001"})
        by_category = lint_text(text, style="fiction", allow={"imagery-density"})
        self.assertNotIn("IMG001", {item.rule_id for item in by_rule.findings})
        self.assertNotIn("IMG001", {item.rule_id for item in by_category.findings})

    def test_reports_cinematic_opening_and_repeated_vague_introspection(self):
        text = (
            "第一章 抵达\n\n"
            "傍晚六点半，临港机场二号航站楼，落日照着玻璃。她身穿深色制服，"
            "心里莫名有一股说不清的感觉。\n\n"
            "她不知道为什么没有回信。后来又莫名地笑了一下。"
        )
        report = lint_text(text, style="webnovel")
        rule_ids = {item.rule_id for item in report.findings}
        self.assertTrue({"OPEN002", "EMO003"} <= rule_ids)

    def test_reports_repeated_scenic_chapter_resets(self):
        text = (
            "第一章 到站\n\n清晨，临港车站下着雨。她穿着灰色外套，走进大厅。\n\n"
            "第二章 见面\n\n傍晚，滨江酒店亮起灯光。她换上黑色西装，走向前台。\n\n"
            "第三章 离开\n\n夜里，城南码头吹着冷风。她穿着长裙，站在路口。"
        )
        report = lint_text(text, style="webnovel")
        self.assertIn("RESET001", {item.rule_id for item in report.findings})

    def test_new_scene_rules_are_narrative_only_and_allowlisted(self):
        text = (
            "傍晚六点半，临港机场二号航站楼，落日照着玻璃。"
            "她身穿深色制服，心里莫名有一股说不清的感觉。"
        )
        serious = lint_text(text, style="news-report")
        allowed = lint_text(text, style="fiction", allow={"cinematic-opening-stack"})
        self.assertNotIn("OPEN002", {item.rule_id for item in serious.findings})
        self.assertNotIn("OPEN002", {item.rule_id for item in allowed.findings})


if __name__ == "__main__":
    unittest.main()
