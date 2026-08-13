import importlib.util
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_skillhub_package.py"
SPEC = importlib.util.spec_from_file_location("build_skillhub_package", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class SkillHubPackageTests(unittest.TestCase):
    def test_builds_executable_package_with_skillhub_metadata(self):
        with TemporaryDirectory() as directory:
            output = Path(directory) / "skill"
            MODULE.build_package(ROOT, output, "9.8.7")

            skill = output.joinpath("SKILL.md").read_text(encoding="utf-8")
            self.assertIn("slug: human-writing-skills", skill)
            self.assertIn("version: 9.8.7", skill)
            self.assertIn("displayName: Advanced Human Writing & AI Humanizer", skill)
            self.assertTrue(output.joinpath("humanwriting", "cli.py").is_file())
            self.assertTrue(output.joinpath("humanwriting", "linter.py").is_file())
            self.assertTrue(output.joinpath("skills", "fiction.md").is_file())
            self.assertTrue(output.joinpath("tests", "test_linter.py").is_file())
            self.assertFalse(output.joinpath(".github").exists())

    def test_refuses_to_mix_with_nonempty_output(self):
        with TemporaryDirectory() as directory:
            output = Path(directory) / "skill"
            output.mkdir()
            output.joinpath("existing.txt").write_text("keep", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "not empty"):
                MODULE.build_package(ROOT, output)


if __name__ == "__main__":
    unittest.main()
