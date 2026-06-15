from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class Skill:
    name: str
    path: Path
    content: str


def default_skills_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "skills"


def list_skills(skills_dir: Path | None = None) -> list[str]:
    root = skills_dir or default_skills_dir()
    return sorted(path.stem for path in root.glob("*.md"))


def load_skill(name: str, skills_dir: Path | None = None) -> Skill:
    root = skills_dir or default_skills_dir()
    path = root / f"{name}.md"
    if not path.exists():
        available = ", ".join(list_skills(root)) or "none"
        raise FileNotFoundError(f"Unknown style '{name}'. Available styles: {available}")
    return Skill(name=name, path=path, content=path.read_text(encoding="utf-8").strip())


def load_many(names: Iterable[str], skills_dir: Path | None = None) -> list[Skill]:
    return [load_skill(name, skills_dir) for name in names]
