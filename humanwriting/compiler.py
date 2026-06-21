from __future__ import annotations

from pathlib import Path

from .skills import load_many, load_skill


CORE_DIRECTIVE = """# Core Directive

Write with a human editor's priorities: intention, specificity, continuity, and rhythm.
Avoid generic filler, repetitive sentence frames, inflated transitions, empty certainty,
summary paragraphs that merely restate the prompt, and precision that does not fit
the genre or narrator.

Before drafting, identify the active context, genre promise, reader expectation, and
the one thing this passage must change. During drafting, preserve established facts.
After drafting, revise once for cadence, concrete detail, and continuity.
Use exact measurements, counts, and numbers when the context earns them; otherwise
prefer felt, relational, or scene-specific scale.
"""


CONTINUITY_DIRECTIVE = """# Continuity Protocol

Maintain a running ledger while generating long text:

- Fixed facts: names, dates, locations, relationships, rules, timeline
- Active threads: unresolved conflicts, questions, clues, promises, arguments
- Relationship state: what each important person knows, wants, hides, owes, refuses,
  and can use as leverage
- Voice anchors: diction, point of view, formality, humor, pacing, taboo phrases
- Scene or section state: where the previous output ended and what must connect next
- Beat bridge: what residue from the previous beat enters the next beat, what changes,
  and what pressure or question remains open
- Change log: what became newly true in the current passage

If context is missing, make the smallest possible assumption and mark it as an assumption.
Do not overwrite established facts for convenience.
Scene and paragraph transitions should be earned by cause, perception, object continuity,
or changed character state rather than generic connective phrasing.
"""


def read_optional(path: str | None) -> str:
    if not path:
        return ""
    return Path(path).read_text(encoding="utf-8").strip()


def compile_prompt(
    style: str,
    task: str,
    context_path: str | None = None,
    modules: list[str] | None = None,
    review: bool = False,
) -> str:
    skill = load_skill(style)
    if skill.kind != "style":
        raise ValueError(f"'{style}' is a module, not a primary style skill.")
    selected_modules = load_many(modules or [])
    if review and "editor-loop" not in [module.name for module in selected_modules]:
        selected_modules.append(load_skill("editor-loop"))
    if review and "ai-trace-rubric" not in [module.name for module in selected_modules]:
        selected_modules.append(load_skill("ai-trace-rubric"))
    context = read_optional(context_path)
    blocks = [
        CORE_DIRECTIVE.strip(),
        CONTINUITY_DIRECTIVE.strip(),
        f"# Selected Skill: {skill.name}\n\n{skill.content}",
    ]
    for module in selected_modules:
        blocks.append(f"# Technique Module: {module.name}\n\n{module.content}")
    if context:
        blocks.append(f"# Project Context\n\n{context}")
    blocks.append(f"# Task\n\n{task.strip()}")
    blocks.append(
        "# Output Contract\n\n"
        "Return only the requested writing unless the user asks for notes. "
        "Keep continuity with the context above. Make the prose feel edited, lived-in, "
        "and specific to the genre rather than broadly polished."
    )
    return "\n\n---\n\n".join(blocks) + "\n"
