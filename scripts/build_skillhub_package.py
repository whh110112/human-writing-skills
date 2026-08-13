"""Build a SkillHub-compatible copy of the tracked skill files."""

from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path


DISPLAY_NAME = "Advanced Human Writing & AI Humanizer"
SUMMARY = (
    "Executable multilingual AI humanizer with deterministic lint, fix, verify, "
    "prompt compilation, staged review, and opt-in long-form continuity modules."
)
DESCRIPTION = (
    "Humanize, write, rewrite, or audit fiction and serious prose with a Python CLI, "
    "deterministic text checks, protected-content verification, staged pipelines, "
    "and selectively loaded writing instructions."
)
TAGS = [
    "ai-humanizer",
    "human-writing",
    "fiction-editing",
    "story-continuity",
    "proofreading",
    "multilingual-writing",
]


def project_version(root: Path) -> str:
    pyproject = root.joinpath("pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r'^version\s*=\s*"([^"]+)"', pyproject, re.MULTILINE)
    if not match:
        raise ValueError("Could not read the project version from pyproject.toml")
    return match.group(1)


def tracked_files(root: Path) -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    files = []
    for raw_path in result.stdout.decode("utf-8").split("\0"):
        if not raw_path or raw_path.startswith(".github/"):
            continue
        path = root.joinpath(raw_path)
        if path.is_file():
            files.append(Path(raw_path))
    return files


def skillhub_frontmatter(version: str) -> str:
    tags = ", ".join(TAGS)
    return (
        "---\n"
        "name: human-writing-skills\n"
        "slug: human-writing-skills\n"
        f"version: {version}\n"
        f"displayName: {DISPLAY_NAME}\n"
        f"summary: {SUMMARY}\n"
        f"description: {DESCRIPTION}\n"
        f"tags: [{tags}]\n"
        "license: MIT\n"
        "homepage: https://github.com/whh110112/human-writing-skills\n"
        "---\n"
    )


def replace_frontmatter(text: str, version: str) -> str:
    match = re.match(r"\A---\r?\n.*?\r?\n---\r?\n", text, re.DOTALL)
    if not match:
        raise ValueError("SKILL.md does not contain valid front matter")
    return skillhub_frontmatter(version) + text[match.end() :]


def build_package(root: Path, output: Path, version: str | None = None) -> Path:
    root = root.resolve()
    output = output.resolve()
    if output == root:
        raise ValueError("Output directory must not replace the repository root")
    if output.exists() and any(output.iterdir()):
        raise ValueError(f"Output directory is not empty: {output}")
    output.mkdir(parents=True, exist_ok=True)

    resolved_version = version or project_version(root)
    for relative in tracked_files(root):
        source = root.joinpath(relative)
        destination = output.joinpath(relative)
        destination.parent.mkdir(parents=True, exist_ok=True)
        if relative.as_posix() == "SKILL.md":
            text = source.read_text(encoding="utf-8")
            destination.write_text(
                replace_frontmatter(text, resolved_version), encoding="utf-8", newline="\n"
            )
        else:
            destination.write_bytes(source.read_bytes())
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--version")
    args = parser.parse_args()
    package = build_package(args.root, args.output, args.version)
    print(package)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
