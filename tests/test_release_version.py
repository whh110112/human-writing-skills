import importlib.util
import json
import re
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from humanwriting import __version__

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("release_version", ROOT / "scripts/check_release_version.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ReleaseVersionTests(unittest.TestCase):
    def test_core_version_must_match_checkout_and_reject_plugin_tags(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "pyproject.toml").write_text('version = "0.16.1"\n', encoding="utf-8")
            for valid in ("v0.16.1", "0.16.1"):
                self.assertEqual(MODULE.check_version(valid, root), "0.16.1")
            for invalid in ("dsh-v0.2.1", "0.16.0", "vgarbage", "0.16.1\nmalformed"):
                with self.assertRaises(ValueError):
                    MODULE.check_version(invalid, root)

    def test_repo_versions_and_dsh_install_links_stay_in_sync(self):
        self.assertEqual(MODULE.check_version(__version__, ROOT), __version__)
        root_pkg = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
        sub_pkg = json.loads((ROOT / "plugins/deepseek-harness/package.json").read_text(encoding="utf-8"))
        dsh_version = root_pkg["version"]
        self.assertEqual(sub_pkg["version"], dsh_version)
        expected_tag = f"dsh-v{dsh_version}"
        for rel_path in (
            "README.md",
            "README.zh-CN.md",
            "plugins/deepseek-harness/README.md",
            "plugins/deepseek-harness/README.zh-CN.md",
            "plugins/deepseek-harness/RELEASE.md",
        ):
            content = (ROOT / rel_path).read_text(encoding="utf-8")
            tags = set(re.findall(r"dsh-v\d+\.\d+\.\d+", content))
            self.assertEqual(tags, {expected_tag}, f"{rel_path} has stale DSH release tag(s): {tags}")
