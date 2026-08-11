from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class OriginalPack:
    active: bool
    block: str
    source_name: str
    character_count: int


def build_original_pack(path: str | None = None) -> OriginalPack:
    if not path:
        return OriginalPack(False, "", "", 0)

    source = Path(path)
    content = source.read_text(encoding="utf-8").strip()
    if not content:
        raise ValueError(f"Original rewrite file is empty: {source}")

    block = "\n".join(
        [
            "# Original Text For Rewrite Comparison",
            "",
            f"Original: {source.name}",
            "This text is the authority for meaning, claims, entities, chronology, polarity,",
            "uncertainty, causality, and constraints. Do not invent specificity to make it vivid.",
            "Do not imitate its style unless it was separately supplied as a style reference.",
            "",
            content,
        ]
    )
    return OriginalPack(True, block, source.name, len(content))
