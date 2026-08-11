import json
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

from humanwriting.cli import main
from humanwriting.statistics import analyze_style_statistics, format_style_statistics


class StatisticsTests(unittest.TestCase):
    def test_reports_language_aware_metrics_without_authorship_claim(self):
        text = "。".join(["这句话长度相同而且结构重复" for _ in range(8)]) + "。"
        report = analyze_style_statistics(text, style="fiction")
        self.assertEqual(report.language, "zh")
        self.assertEqual(report.sentence_length_cv, 0.0)
        self.assertTrue(report.warnings)
        self.assertIn("not evidence of AI authorship", report.disclaimer)

    def test_varied_text_has_more_sentence_burstiness(self):
        uniform = "One sentence repeats here. Same sentence repeats now. One sentence repeats here. Same sentence repeats now. One sentence repeats here. Same sentence repeats now."
        varied = "Stop. The next sentence takes its time because the speaker changes direction halfway through the thought. Then rain. Nobody answers the phone, although it rings until the battery dies. Morning comes quietly."
        self.assertGreater(
            analyze_style_statistics(varied).sentence_length_cv,
            analyze_style_statistics(uniform).sentence_length_cv,
        )

    def test_json_output_is_structured(self):
        payload = json.loads(format_style_statistics(analyze_style_statistics("短句。再来一句。"), "json"))
        self.assertIn("sentence_length_cv", payload)
        self.assertIn("warnings", payload)

    def test_cli_stats_emits_structured_json(self):
        with TemporaryDirectory() as directory:
            draft = Path(directory) / "draft.md"
            draft.write_text("短句。再来一句。第三句更长一些。", encoding="utf-8")
            stdout = StringIO()
            with redirect_stdout(stdout):
                self.assertEqual(
                    main(["stats", "--draft", str(draft), "--format", "json"]), 0
                )
            self.assertIn("sentence_length_cv", json.loads(stdout.getvalue()))


if __name__ == "__main__":
    unittest.main()
