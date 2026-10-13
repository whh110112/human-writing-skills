"""Check the prebuilt DSH tarball's complete runtime and release metadata."""
from __future__ import annotations

import json
import sys
import tarfile
from pathlib import Path, PurePosixPath


def verify_package(path: str) -> None:
    expected = json.loads(Path(__file__).resolve().parents[1].joinpath("package.json").read_text(encoding="utf-8"))
    with tarfile.open(path, "r:gz") as archive:
        names = set(archive.getnames())
        for name in names:
            parts = PurePosixPath(name).parts
            if not parts or parts[0] != "package" or ".." in parts:
                raise ValueError(f"Unsafe package entry: {name}")
            if "__pycache__" in parts or "node_modules" in parts or ".git" in parts:
                raise ValueError(f"Unexpected runtime material: {name}")
        required = {
            "package/package.json", "package/LICENSE",
            "package/plugins/deepseek-harness/index.js",
            "package/plugins/deepseek-harness/adapter.js",
            "package/plugins/deepseek-harness/cordis.patch.yml",
            "package/humanwriting/mcp_server.py", "package/humanwriting/compiler.py",
            "package/humanwriting/review.py", "package/skills/generation-quality.md",
            "package/skills/fiction.md", "package/skills/academic-paper.md",
            "package/skills/formal-document.md",
        }
        missing = required - names
        if missing:
            raise ValueError(f"Incomplete DSH runtime: {sorted(missing)}")
        manifest = json.load(archive.extractfile("package/package.json"))
        assert manifest["name"] == "dsh-advanced-human-writing"
        assert manifest["version"] == expected["version"]
        assert manifest["dsh"]["bundle"]["patch"] == "./plugins/deepseek-harness/cordis.patch.yml"
        assert not any(key in manifest.get("scripts", {}) for key in ("preinstall", "install", "postinstall", "prepare"))
    print(f"DSH package verified: {Path(path).name}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        package = sys.argv[1]
    else:
        root = Path(__file__).resolve().parents[1]
        version = json.loads(root.joinpath("package.json").read_text(encoding="utf-8"))["version"]
        package = str(root / "dist" / f"dsh-advanced-human-writing-{version}.tgz")
    verify_package(package)
