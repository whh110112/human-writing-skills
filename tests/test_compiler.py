import unittest

from humanwriting.compiler import compile_prompt
from humanwriting.skills import list_skills, load_skill


class CompilerTests(unittest.TestCase):
    def test_lists_builtin_skills(self):
        skills = list_skills()
        self.assertIn("fiction", skills)
        self.assertIn("webnovel", skills)

    def test_load_skill_content(self):
        skill = load_skill("news-report")
        self.assertEqual(skill.name, "news-report")
        self.assertIn("News Report Skill", skill.content)

    def test_compile_prompt_contains_style_and_task(self):
        prompt = compile_prompt("fiction", "Write the next scene.")
        self.assertIn("Core Directive", prompt)
        self.assertIn("Fiction Skill", prompt)
        self.assertIn("Write the next scene.", prompt)


if __name__ == "__main__":
    unittest.main()
