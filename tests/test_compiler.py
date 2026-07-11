import unittest
from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

from humanwriting.cli import main
from humanwriting.compiler import compile_audit_prompt, compile_prompt
from humanwriting.skills import (
    default_skills_dir,
    list_module_skills,
    list_skills,
    list_style_skills,
    load_skill,
)


class CompilerTests(unittest.TestCase):
    def test_lists_builtin_skills(self):
        skills = list_skills()
        self.assertIn("fiction", skills)
        self.assertIn("webnovel", skills)

    def test_default_skills_resource_contains_core_files(self):
        root = default_skills_dir()
        self.assertTrue(root.joinpath("fiction.md").is_file())
        self.assertTrue(root.joinpath("relationship-stance-audit.md").is_file())

    def test_lists_style_and_module_skills(self):
        self.assertIn("fiction", list_style_skills())
        self.assertIn("embodied-emotion", list_module_skills())
        self.assertIn("narrative-bridges", list_module_skills())
        self.assertIn("relationship-state", list_module_skills())
        self.assertIn("natural-measurement", list_module_skills())
        self.assertIn("forensic-physical-audit", list_module_skills())
        self.assertIn("occupancy-capacity", list_module_skills())
        self.assertIn("relationship-stance-audit", list_module_skills())
        self.assertIn("cliche-phrase-audit", list_module_skills())
        self.assertIn("formulaic-structure-audit", list_module_skills())
        self.assertIn("prose-progress-audit", list_module_skills())

    def test_load_skill_content(self):
        skill = load_skill("news-report")
        self.assertEqual(skill.name, "news-report")
        self.assertEqual(skill.kind, "style")
        self.assertIn("News Report Skill", skill.content)

    def test_compile_prompt_contains_style_and_task(self):
        prompt = compile_prompt("fiction", "Write the next scene.")
        self.assertIn("Core Directive", prompt)
        self.assertIn("Beat bridge", prompt)
        self.assertIn("Relationship state", prompt)
        self.assertIn("Fiction Skill", prompt)
        self.assertIn("Write the next scene.", prompt)

    def test_compile_prompt_can_add_modules(self):
        prompt = compile_prompt(
            "fiction",
            "Write the next scene.",
            modules=[
                "narrative-bridges",
                "relationship-state",
                "natural-measurement",
                "embodied-emotion",
                "vocal-rhythm",
            ],
            review=True,
        )
        self.assertIn("Technique Module: narrative-bridges", prompt)
        self.assertIn("Technique Module: relationship-state", prompt)
        self.assertIn("Technique Module: natural-measurement", prompt)
        self.assertIn("Technique Module: embodied-emotion", prompt)
        self.assertIn("Technique Module: vocal-rhythm", prompt)
        self.assertIn("Technique Module: editor-loop", prompt)
        self.assertIn("Technique Module: ai-trace-rubric", prompt)
        self.assertNotIn("Technique Module: relationship-stance-audit", prompt)
        self.assertNotIn("Technique Module: cliche-phrase-audit", prompt)
        self.assertNotIn("Technique Module: formulaic-structure-audit", prompt)
        self.assertNotIn("Technique Module: prose-progress-audit", prompt)

    def test_deep_review_adds_detailed_audits_and_is_larger(self):
        compact = compile_prompt("fiction", "Write the next scene.", review=True)
        deep = compile_prompt("fiction", "Write the next scene.", deep_review=True)
        self.assertIn("Technique Module: cliche-phrase-audit", deep)
        self.assertIn("Technique Module: formulaic-structure-audit", deep)
        self.assertIn("Technique Module: prose-progress-audit", deep)
        self.assertIn("Technique Module: relationship-stance-audit", deep)
        self.assertIn("Technique Module: natural-measurement", deep)
        self.assertLess(len(compact), len(deep))

    def test_compact_review_stays_within_generation_prompt_budget(self):
        context = Path(__file__).resolve().parent.parent / "examples" / "story-ledger.md"
        prompt = compile_prompt(
            "webnovel",
            "Continue the next chapter.",
            context_path=str(context),
            review=True,
            strict_continuity=True,
        )
        self.assertLess(len(prompt), 22000)

    def test_duplicate_modules_are_loaded_once(self):
        prompt = compile_prompt(
            "fiction",
            "Write the next scene.",
            modules=["vocal-rhythm", "vocal-rhythm"],
        )
        self.assertEqual(prompt.count("# Technique Module: vocal-rhythm"), 1)

    def test_only_deep_review_adds_number_sense_for_narrative_styles(self):
        fiction_prompt = compile_prompt("fiction", "Write the next scene.", review=True)
        deep_fiction_prompt = compile_prompt("fiction", "Write the next scene.", deep_review=True)
        deep_news_prompt = compile_prompt("news-report", "Write the report.", deep_review=True)
        self.assertNotIn("Technique Module: natural-measurement", fiction_prompt)
        self.assertIn("Technique Module: natural-measurement", deep_fiction_prompt)
        self.assertNotIn("Technique Module: natural-measurement", deep_news_prompt)

    def test_number_sense_can_be_explicitly_added(self):
        prompt = compile_prompt("news-report", "Write the report.", number_sense=True)
        self.assertIn("Technique Module: natural-measurement", prompt)

    def test_compile_prompt_can_add_strict_continuity_modules(self):
        prompt = compile_prompt(
            "fiction",
            "Write a car scene.",
            strict_continuity=True,
        )
        self.assertIn("Technique Module: occupancy-capacity", prompt)
        self.assertIn("Technique Module: spatial-blocking", prompt)
        self.assertIn("Technique Module: appearance-prop-continuity", prompt)
        self.assertNotIn("Technique Module: physical-continuity-audit", prompt)

    def test_compile_audit_prompt_extracts_draft_and_modules(self):
        with TemporaryDirectory() as directory:
            draft = Path(directory) / "draft.md"
            draft.write_text(
                "Lao Gao looked from the front row toward Yanzi behind the glass. "
                "Later, he touched Yanzi in the rear seat. Yanzi wore flats, then heels.",
                encoding="utf-8",
            )
            prompt = compile_audit_prompt(str(draft), number_sense=True)
        self.assertIn("Audit Directive", prompt)
        self.assertIn("Audit Module: forensic-physical-audit", prompt)
        self.assertIn("Audit Module: occupancy-capacity", prompt)
        self.assertIn("Audit Module: spatial-blocking", prompt)
        self.assertIn("Audit Module: relationship-stance-audit", prompt)
        self.assertIn("Audit Module: cliche-phrase-audit", prompt)
        self.assertIn("Audit Module: formulaic-structure-audit", prompt)
        self.assertIn("Audit Module: prose-progress-audit", prompt)
        self.assertIn("Audit Module: natural-measurement", prompt)
        self.assertIn("Draft To Audit", prompt)
        self.assertIn("behind the glass", prompt)
        self.assertIn("flats, then heels", prompt)

    def test_no_strict_continuity_removes_all_physical_audits(self):
        with TemporaryDirectory() as directory:
            draft = Path(directory) / "draft.md"
            draft.write_text("A said B was trustworthy.", encoding="utf-8")
            prompt = compile_audit_prompt(str(draft), strict_continuity=False)
        self.assertNotIn("Audit Module: forensic-physical-audit", prompt)
        self.assertNotIn("Audit Module: physical-continuity-audit", prompt)
        self.assertNotIn("forensic physical continuity audit", prompt)
        self.assertIn("Audit Module: relationship-stance-audit", prompt)
        self.assertIn("Audit Module: ai-trace-rubric", prompt)

    def test_relationship_profile_does_not_load_unrelated_audits(self):
        with TemporaryDirectory() as directory:
            draft = Path(directory) / "draft.md"
            draft.write_text("A praised C in front of B.", encoding="utf-8")
            prompt = compile_audit_prompt(str(draft), profiles=["relationship"])
        self.assertIn("Audit Module: relationship-state", prompt)
        self.assertIn("Audit Module: relationship-stance-audit", prompt)
        self.assertNotIn("Audit Module: forensic-physical-audit", prompt)
        self.assertNotIn("Audit Module: ai-trace-rubric", prompt)

    def test_numbers_profile_only_loads_number_audit(self):
        with TemporaryDirectory() as directory:
            draft = Path(directory) / "draft.md"
            draft.write_text("Her hand moved three centimeters.", encoding="utf-8")
            prompt = compile_audit_prompt(str(draft), profiles=["numbers"])
        self.assertIn("Audit Module: natural-measurement", prompt)
        self.assertNotIn("Audit Module: forensic-physical-audit", prompt)
        self.assertNotIn("Audit Module: ai-trace-rubric", prompt)

    def test_cli_reports_missing_draft_without_traceback(self):
        stderr = StringIO()
        with redirect_stderr(stderr), self.assertRaises(SystemExit) as raised:
            main(["audit", "--draft", "missing-draft.md"])
        self.assertEqual(raised.exception.code, 2)
        self.assertIn("missing-draft.md", stderr.getvalue())
        self.assertNotIn("Traceback", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
