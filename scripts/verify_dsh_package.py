"""Check the prebuilt DSH tarball's complete runtime and release metadata."""
from __future__ import annotations

import json
import sys
import tarfile
import subprocess
from tempfile import TemporaryDirectory
from pathlib import Path, PurePosixPath


def verify_package(path: str) -> None:
    expected = json.loads(Path(__file__).resolve().parents[1].joinpath("package.json").read_text(encoding="utf-8"))
    with tarfile.open(path, "r:gz") as archive:
        names = set(archive.getnames())
        for entry in archive.getmembers():
            name = entry.name
            parts = PurePosixPath(name).parts
            if not parts or parts[0] != "package" or ".." in parts:
                raise ValueError(f"Unsafe package entry: {name}")
            if "__pycache__" in parts or "node_modules" in parts or ".git" in parts:
                raise ValueError(f"Unexpected runtime material: {name}")
            if not entry.isfile() and not entry.isdir():
                raise ValueError(f"Unsupported package entry: {name}")
        required = {
            "package/package.json", "package/LICENSE",
            "package/plugins/deepseek-harness/index.js",
            "package/plugins/deepseek-harness/adapter.js",
            "package/plugins/deepseek-harness/cordis.patch.yml",
            "package/humanwriting/mcp_server.py", "package/humanwriting/compiler.py",
            "package/humanwriting/audit_storage.py",
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
        with TemporaryDirectory(prefix="dsh-package-check-") as directory:
            # Paths and member types have been validated above; no symlinks are extracted.
            archive.extractall(directory)
            probe = (
                "import sys; sys.path.insert(0, sys.argv[1]); "
                "from humanwriting.mcp_server import handle_message; "
                "from humanwriting.compiler import compile_prompt; "
                "from pathlib import Path; "
                "assert handle_message({'jsonrpc':'2.0','id':1,'method':'ping'}, Path.cwd())['result'] == {}; "
                "[compile_prompt(style=s, task='Write a passage.') for s in ('fiction','academic-paper','formal-document')]"
            )
            subprocess.run([sys.executable, "-I", "-X", "utf8", "-c", probe, str(Path(directory) / "package")],
                           cwd=directory, check=True, timeout=30)
    print(f"DSH package verified: {Path(path).name}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        package = sys.argv[1]
    else:
        root = Path(__file__).resolve().parents[1]
        version = json.loads(root.joinpath("package.json").read_text(encoding="utf-8"))["version"]
        package = str(root / "dist" / f"dsh-advanced-human-writing-{version}.tgz")
    verify_package(package)
