import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from humanwriting.compiler import compile_audit_prompt, compile_prompt
from humanwriting.skills import list_module_skills, list_skills, list_style_skills, load_skill


class CompilerTests(unittest.TestCase):
    def test_lists_builtin_skills(self):
        skills = list_skills()
        self.assertIn("fiction", skills)
        self.assertIn("webnovel", skills)

    def test_lists_style_and_module_skills(self):
        self.assertIn("fiction", list_style_skills())
        self.assertIn("embodied-emotion", list_module_skills())
        self.assertIn("narrative-bridges", list_module_skills())
        self.assertIn("relationship-state", list_module_skills())
        self.assertIn("natural-measurement", list_module_skills())
        self.assertIn("forensic-physical-audit", list_module_skills())
        self.assertIn("occupancy-capacity", list_module_skills())

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

    def test_review_adds_number_sense_for_narrative_styles(self):
        fiction_prompt = compile_prompt("fiction", "Write the next scene.", review=True)
        news_prompt = compile_prompt("news-report", "Write the report.", review=True)
        self.assertIn("Technique Module: natural-measurement", fiction_prompt)
        self.assertNotIn("Technique Module: natural-measurement", news_prompt)

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
        self.assertIn("Technique Module: physical-continuity-audit", prompt)

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
        self.assertIn("Audit Module: natural-measurement", prompt)
        self.assertIn("Draft To Audit", prompt)
        self.assertIn("behind the glass", prompt)
        self.assertIn("flats, then heels", prompt)


if __name__ == "__main__":
    unittest.main()
