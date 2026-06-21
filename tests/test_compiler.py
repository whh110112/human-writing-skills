import unittest

from humanwriting.compiler import compile_prompt
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
            modules=["narrative-bridges", "relationship-state", "embodied-emotion", "vocal-rhythm"],
            review=True,
        )
        self.assertIn("Technique Module: narrative-bridges", prompt)
        self.assertIn("Technique Module: relationship-state", prompt)
        self.assertIn("Technique Module: embodied-emotion", prompt)
        self.assertIn("Technique Module: vocal-rhythm", prompt)
        self.assertIn("Technique Module: editor-loop", prompt)
        self.assertIn("Technique Module: ai-trace-rubric", prompt)


if __name__ == "__main__":
    unittest.main()
