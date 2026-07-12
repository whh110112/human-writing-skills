from __future__ import annotations

from pathlib import Path

from .protection import build_protection_manifest, detect_serious_document
from .reference import DEFAULT_REFERENCE_BUDGET, build_reference_pack
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
LOGIC_AUDIT_MODULES = ["logic-causality-audit"]
CHARACTER_AUDIT_MODULES = ["character-consistency-audit"]
PROOFREAD_AUDIT_MODULES = ["proofreading-audit"]
REFERENCE_STYLE_AUDIT_MODULES = ["reference-style-alignment"]
PROTECTED_CONTENT_MODULES = ["protected-content"]
AUDIT_PROFILES = {
    "full",
    "logic",
    "character",
    "physical",
    "relationship",
    "ai-trace",
    "numbers",
    "proofread",
    "style-match",
}


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
    reference_paths: list[str] | None = None,
    reference_style: str | None = None,
    reference_budget: int = DEFAULT_REFERENCE_BUDGET,
    protect_content: bool = False,
    protect_terms: list[str] | None = None,
) -> str:
    skill = load_skill(style)
    if skill.kind != "style":
        raise ValueError(f"'{style}' is a module, not a primary style skill.")
    selected_modules = load_many(modules or [])
    context = read_optional(context_path)
    reference_pack = build_reference_pack(
        reference_paths,
        reference_style,
        task=task,
        budget=reference_budget,
    )
    if reference_pack.active:
        append_missing(selected_modules, REFERENCE_STYLE_AUDIT_MODULES)
    protection_requested = protect_content or bool(protect_terms) or any(
        module.name == "protected-content" for module in selected_modules
    )
    auto_protection, auto_protection_reason = detect_serious_document(
        text=context,
        document_type=style,
        task=task,
    )
    protection_active = protection_requested or auto_protection
    protection_reason = (
        "Explicit protection was requested."
        if protection_requested
        else auto_protection_reason
    )
    if protection_active:
        append_missing(selected_modules, PROTECTED_CONTENT_MODULES)
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
    blocks = [
        CORE_DIRECTIVE.strip(),
        CONTINUITY_DIRECTIVE.strip(),
        f"# Selected Skill: {skill.name}\n\n{skill.content}",
    ]
    for module in selected_modules:
        blocks.append(f"# Technique Module: {module.name}\n\n{module.content}")
    if context:
        blocks.append(f"# Project Context\n\n{context}")
    if reference_pack.active:
        blocks.append(reference_pack.block)
    if protection_active:
        blocks.append(f"# Protection Activation\n\n{protection_reason}")
        protected_source = "\n".join(part for part in [context, task] if part)
        blocks.append(build_protection_manifest(protected_source, protect_terms))
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
    reference_paths: list[str] | None = None,
    reference_style: str | None = None,
    reference_budget: int = DEFAULT_REFERENCE_BUDGET,
    protect_content: bool = False,
    protect_terms: list[str] | None = None,
    document_type: str = "auto",
    auto_protect: bool = True,
) -> str:
    selected_modules = load_many(modules or [])
    draft = read_optional(draft_path)
    requested_profiles = set(profiles or ["full"])
    reference_pack = build_reference_pack(
        reference_paths,
        reference_style,
        budget=reference_budget,
    )
    if reference_pack.active:
        requested_profiles.add("style-match")
    if number_sense:
        requested_profiles.add("numbers")
    unknown_profiles = requested_profiles - AUDIT_PROFILES
    if unknown_profiles:
        raise ValueError(f"Unknown audit profile: {', '.join(sorted(unknown_profiles))}")
    if "style-match" in requested_profiles and not reference_pack.active:
        raise ValueError("The style-match profile requires --reference or --reference-style.")
    physical_enabled = "physical" in requested_profiles or (
        "full" in requested_profiles and strict_continuity
    )
    relationship_enabled = bool(requested_profiles & {"full", "relationship"})
    ai_trace_enabled = bool(requested_profiles & {"full", "ai-trace"})
    numbers_enabled = bool(requested_profiles & {"full", "numbers"})
    logic_enabled = bool(requested_profiles & {"full", "logic"})
    character_enabled = bool(requested_profiles & {"full", "character"})
    proofread_enabled = bool(requested_profiles & {"full", "proofread"})
    style_match_enabled = "style-match" in requested_profiles

    if logic_enabled:
        append_missing(selected_modules, LOGIC_AUDIT_MODULES)
    if character_enabled:
        append_missing(selected_modules, CHARACTER_AUDIT_MODULES)
    if physical_enabled:
        append_missing(selected_modules, PHYSICAL_AUDIT_MODULES)
    if relationship_enabled:
        append_missing(selected_modules, RELATIONSHIP_AUDIT_MODULES)
    if ai_trace_enabled:
        append_missing(selected_modules, AI_TRACE_AUDIT_MODULES)
    if numbers_enabled:
        append_missing(selected_modules, ["natural-measurement"])
    if proofread_enabled:
        append_missing(selected_modules, PROOFREAD_AUDIT_MODULES)
    if style_match_enabled:
        append_missing(selected_modules, REFERENCE_STYLE_AUDIT_MODULES)
    protection_requested = protect_content or bool(protect_terms) or any(
        module.name == "protected-content" for module in selected_modules
    )
    auto_protection, auto_protection_reason = detect_serious_document(
        text=draft,
        document_type=document_type,
    )
    protection_active = protection_requested or (auto_protect and auto_protection)
    protection_reason = (
        "Explicit protection was requested."
        if protection_requested
        else auto_protection_reason
    )
    if protection_active:
        append_missing(selected_modules, PROTECTED_CONTENT_MODULES)

    context = read_optional(context_path)
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
    if reference_pack.active:
        blocks.append(reference_pack.block)
    if protection_active:
        blocks.append(f"# Protection Activation\n\n{protection_reason}")
        blocks.append(build_protection_manifest(draft, protect_terms))
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
    if logic_enabled:
        task_lines.append(
            "For logic, map trigger -> action or inference -> result -> consequence and check "
            "time, knowledge, motive, rules, resources, and unresolved costs."
        )
    if character_enabled:
        task_lines.append(
            "For character consistency, compare goals, voice, knowledge, competence, boundaries, "
            "status, and recent change gates before calling a deviation an error."
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
    if proofread_enabled:
        task_lines.append(
            "For proofreading, separate definite mechanical errors from house-style choices and "
            "intentional voice; do not rewrite plot or characterization."
        )
    if style_match_enabled:
        task_lines.append(
            "For reference style, build an evidence-backed style card, compare the draft on each "
            "dimension, and flag copying or context contamination as well as stylistic drift."
        )
    blocks.append("\n".join(task_lines))
    return "\n\n---\n\n".join(blocks) + "\n"
