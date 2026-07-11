from __future__ import annotations

from pathlib import Path

from .skills import load_many, load_skill

NUMBER_SENSE_REVIEW_STYLES = {"fiction", "webnovel", "self-media"}
CORE_REVIEW_MODULES = [
    "editor-loop",
    "ai-trace-rubric",
]
NARRATIVE_REVIEW_MODULES = [
    "relationship-stance-audit",
]
DEEP_REVIEW_MODULES = [
    "cliche-phrase-audit",
    "formulaic-structure-audit",
    "prose-progress-audit",
]
AI_TRACE_AUDIT_MODULES = [
    "ai-trace-rubric",
    "cliche-phrase-audit",
    "formulaic-structure-audit",
    "prose-progress-audit",
]
RELATIONSHIP_AUDIT_MODULES = [
    "relationship-state",
    "relationship-stance-audit",
]
PHYSICAL_AUDIT_MODULES = [
    "forensic-physical-audit",
    "occupancy-capacity",
    "spatial-blocking",
    "appearance-prop-continuity",
    "physical-continuity-audit",
]
AUDIT_PROFILES = {"full", "physical", "relationship", "ai-trace", "numbers"}


CORE_DIRECTIVE = """# Core Directive

Write with a human editor's priorities: intention, specificity, continuity, and rhythm.
Avoid generic filler, repetitive sentence frames, inflated transitions, empty certainty,
summary paragraphs that merely restate the prompt, and precision that does not fit
the genre or narrator.

Before drafting, identify the active context, genre promise, reader expectation, and
the one thing this passage must change. During drafting, preserve established facts.
After drafting, revise once for cadence, concrete detail, physical state, and continuity.
Use exact measurements, counts, and numbers when the context earns them; otherwise
prefer felt, relational, or scene-specific scale.
"""


CONTINUITY_DIRECTIVE = """# Continuity Protocol

Maintain a running ledger while generating long text:

- Fixed facts: names, dates, locations, relationships, rules, timeline
- Active threads: unresolved conflicts, questions, clues, promises, arguments
- Relationship state: what each important person knows, wants, hides, owes, refuses,
  and can use as leverage
- Relationship stance: who may safely mention, praise, criticize, compare, expose,
  or conceal whom in the current audience
- Voice anchors: diction, point of view, formality, humor, pacing, taboo phrases
- Scene or section state: where the previous output ended and what must connect next
- Beat bridge: what residue from the previous beat enters the next beat, what changes,
  and what pressure or question remains open
- Physical state: positions, resource modes/capacity, occupancy, movement gates,
  transformation gates, clothing, props, injuries, reachable objects
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


def append_missing(selected_modules: list, names: list[str]) -> None:
    selected_names = {module.name for module in selected_modules}
    for name in names:
        if name not in selected_names:
            selected_modules.append(load_skill(name))
            selected_names.add(name)


def compile_prompt(
    style: str,
    task: str,
    context_path: str | None = None,
    modules: list[str] | None = None,
    review: bool = False,
    strict_continuity: bool = False,
    number_sense: bool = False,
    deep_review: bool = False,
) -> str:
    skill = load_skill(style)
    if skill.kind != "style":
        raise ValueError(f"'{style}' is a module, not a primary style skill.")
    selected_modules = load_many(modules or [])
    if strict_continuity:
        append_missing(
            selected_modules,
            [
                "occupancy-capacity",
                "spatial-blocking",
                "appearance-prop-continuity",
            ],
        )
    if review or deep_review:
        append_missing(selected_modules, CORE_REVIEW_MODULES)
    if deep_review:
        append_missing(selected_modules, NARRATIVE_REVIEW_MODULES)
        append_missing(selected_modules, DEEP_REVIEW_MODULES)
    if (number_sense or (deep_review and style in NUMBER_SENSE_REVIEW_STYLES)) and "natural-measurement" not in [
        module.name for module in selected_modules
    ]:
        selected_modules.append(load_skill("natural-measurement"))
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


def compile_audit_prompt(
    draft_path: str,
    context_path: str | None = None,
    modules: list[str] | None = None,
    strict_continuity: bool = True,
    number_sense: bool = False,
    profiles: list[str] | None = None,
) -> str:
    selected_modules = load_many(modules or [])
    requested_profiles = set(profiles or ["full"])
    if number_sense:
        requested_profiles.add("numbers")
    unknown_profiles = requested_profiles - AUDIT_PROFILES
    if unknown_profiles:
        raise ValueError(f"Unknown audit profile: {', '.join(sorted(unknown_profiles))}")
    physical_enabled = "physical" in requested_profiles or (
        "full" in requested_profiles and strict_continuity
    )
    relationship_enabled = bool(requested_profiles & {"full", "relationship"})
    ai_trace_enabled = bool(requested_profiles & {"full", "ai-trace"})
    numbers_enabled = "numbers" in requested_profiles

    if physical_enabled:
        append_missing(selected_modules, PHYSICAL_AUDIT_MODULES)
    if relationship_enabled:
        append_missing(selected_modules, RELATIONSHIP_AUDIT_MODULES)
    if ai_trace_enabled:
        append_missing(selected_modules, AI_TRACE_AUDIT_MODULES)
    if numbers_enabled:
        append_missing(selected_modules, ["natural-measurement"])

    context = read_optional(context_path)
    draft = read_optional(draft_path)
    blocks = [
        "# Audit Directive\n\n"
        "You are auditing an existing draft, not generating new prose. "
        "Do not assume the draft is correct. Audit only the selected profiles, extract "
        "evidence before judging, distinguish contradictions from intentional exceptions, "
        "and propose the smallest repair that preserves the author's intent. "
        f"Selected profiles: {', '.join(sorted(requested_profiles))}.",
        CONTINUITY_DIRECTIVE.strip(),
    ]
    for module in selected_modules:
        blocks.append(f"# Audit Module: {module.name}\n\n{module.content}")
    if context:
        blocks.append(f"# Continuity Ledger\n\n{context}")
    blocks.append(f"# Draft To Audit\n\n{draft}")
    task_lines = [
        "# Audit Task",
        "",
        "Return evidence first, then confirmed contradictions, uncertain cases, and a minimal repair plan.",
    ]
    if physical_enabled:
        task_lines.append(
            "For physical continuity, require on-page evidence for movement, occupancy, "
            "resource-mode changes, barriers, reach, clothing, props, and body-state changes."
        )
    if relationship_enabled:
        task_lines.append(
            "For relationship continuity, extract speaker -> listener/audience -> referenced "
            "party and check stance, knowledge, rank, mention policy, secrecy, motive, and consequence."
        )
    if ai_trace_enabled:
        task_lines.append(
            "For AI-trace review, identify exact phrases or paragraph structures before scoring; "
            "do not flag a pattern without quoting or locating its evidence."
        )
    if numbers_enabled:
        task_lines.append(
            "For number sense, classify every exact number before deciding whether to keep, "
            "soften, generalize, or remove it."
        )
    blocks.append("\n".join(task_lines))
    return "\n\n---\n\n".join(blocks) + "\n"
