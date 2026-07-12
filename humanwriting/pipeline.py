from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .compiler import compile_audit_prompt, read_optional
from .detection import PIPELINE_PROFILES, ProfileDecision, detect_audit_profiles
from .linter import format_lint_report, lint_file
from .protection import detect_serious_document
from .reference import DEFAULT_REFERENCE_BUDGET, build_reference_pack


@dataclass(frozen=True)
class AuditStage:
    order: int
    profile: str
    reason: str
    prompt: str


def select_pipeline_profiles(
    draft: str,
    stages: list[str] | None = None,
    auto: bool = False,
    reference_active: bool = False,
) -> tuple[list[str], list[ProfileDecision]]:
    if stages:
        selected = list(dict.fromkeys(stages))
        unknown = set(selected) - set(PIPELINE_PROFILES)
        if unknown:
            raise ValueError(f"Unknown pipeline stage: {', '.join(sorted(unknown))}")
        if "style-match" in selected and not reference_active:
            raise ValueError("The style-match stage requires --reference or --reference-style.")
        decisions = []
        for profile in PIPELINE_PROFILES:
            is_selected = profile in selected
            reason = "Explicitly selected by the user."
            if profile == "style-match" and not reference_active:
                reason = "No explicit reference material or style direction was supplied."
            decisions.append(ProfileDecision(profile, is_selected, reason))
        return selected, decisions
    if auto:
        decisions = detect_audit_profiles(draft, reference_active=reference_active)
        return [decision.profile for decision in decisions if decision.selected], decisions
    decisions = []
    selected = []
    for profile in PIPELINE_PROFILES:
        include = profile != "style-match" or reference_active
        reason = (
            "Included in the complete default pipeline."
            if include
            else "No explicit reference material or style direction was supplied."
        )
        decisions.append(ProfileDecision(profile, include, reason))
        if include:
            selected.append(profile)
    return selected, decisions


def build_audit_pipeline(
    draft_path: str,
    context_path: str | None = None,
    stages: list[str] | None = None,
    auto: bool = False,
    reference_paths: list[str] | None = None,
    reference_style: str | None = None,
    reference_budget: int = DEFAULT_REFERENCE_BUDGET,
    protect_content: bool = False,
    protect_terms: list[str] | None = None,
    document_type: str = "auto",
) -> tuple[list[AuditStage], list[ProfileDecision]]:
    draft = read_optional(draft_path)
    reference_pack = build_reference_pack(
        reference_paths,
        reference_style,
        budget=reference_budget,
    )
    selected, decisions = select_pipeline_profiles(
        draft,
        stages=stages,
        auto=auto,
        reference_active=reference_pack.active,
    )
    reason_by_profile = {decision.profile: decision.reason for decision in decisions}
    auto_protection, _ = detect_serious_document(draft, document_type=document_type)
    protection_profile = None
    if auto_protection and selected:
        protection_profile = "proofread" if "proofread" in selected else selected[-1]
    pipeline = [
        AuditStage(
            order=index,
            profile=profile,
            reason=reason_by_profile[profile],
            prompt=compile_audit_prompt(
                draft_path,
                context_path=context_path,
                strict_continuity=False,
                profiles=[profile],
                reference_paths=reference_paths if profile == "style-match" else None,
                reference_style=reference_style if profile == "style-match" else None,
                reference_budget=reference_budget,
                protect_content=protect_content,
                protect_terms=protect_terms,
                document_type=document_type,
                auto_protect=profile == protection_profile,
            ),
        )
        for index, profile in enumerate(selected, start=1)
    ]
    return pipeline, decisions


def write_audit_pipeline(
    draft_path: str,
    output_dir: str,
    context_path: str | None = None,
    stages: list[str] | None = None,
    auto: bool = False,
    reference_paths: list[str] | None = None,
    reference_style: str | None = None,
    reference_budget: int = DEFAULT_REFERENCE_BUDGET,
    protect_content: bool = False,
    protect_terms: list[str] | None = None,
    document_type: str = "auto",
    lint_style: str = "general",
    lint_allow: set[str] | None = None,
) -> tuple[Path, list[AuditStage]]:
    pipeline, decisions = build_audit_pipeline(
        draft_path,
        context_path=context_path,
        stages=stages,
        auto=auto,
        reference_paths=reference_paths,
        reference_style=reference_style,
        reference_budget=reference_budget,
        protect_content=protect_content,
        protect_terms=protect_terms,
        document_type=document_type,
    )
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    lint_report = lint_file(draft_path, style=lint_style, allow=lint_allow)
    (output / "00-pattern-lint.md").write_text(
        format_lint_report(lint_report, "markdown"), encoding="utf-8"
    )
    (output / "00-pattern-lint.json").write_text(
        format_lint_report(lint_report, "json"), encoding="utf-8"
    )

    rows = []
    for stage in pipeline:
        filename = f"{stage.order:02d}-{stage.profile}.md"
        (output / filename).write_text(stage.prompt, encoding="utf-8")
        rows.append(f"| {stage.order} | `{stage.profile}` | {stage.reason} | `{filename}` |")

    decision_rows = [
        f"| `{decision.profile}` | {'yes' if decision.selected else 'no'} | {decision.reason} |"
        for decision in decisions
    ]
    manifest = "\n".join(
        [
            "# Audit Pipeline",
            "",
            "Run every stage in a fresh model conversation or independent API request.",
            "Do not carry the model's hidden conversation memory between stages.",
            "Save each stage report, then reconcile them after all selected stages finish.",
            "每个阶段都应放进新的模型会话或独立 API 请求；全部完成后再汇总报告。",
            "Start with `00-pattern-lint.md` for deterministic evidence spans. Its score is",
            "a transparent editing heuristic, not evidence of AI authorship.",
            f"Pattern lint style: `{lint_style}`; score: `{lint_report.score}`; findings: `{len(lint_report.findings)}`.",
            "",
            "| Order | Profile | Why selected | Prompt file |",
            "| --- | --- | --- | --- |",
            *rows,
            "",
            "## Selection Decisions",
            "",
            "| Profile | Selected | Reason |",
            "| --- | --- | --- |",
            *decision_rows,
            "",
            "## Final Reconciliation",
            "",
            "Merge confirmed findings only after all stages finish. Deduplicate findings,",
            "resolve conflicts using quoted draft evidence, and apply repairs in this order:",
            "logic -> character/relationship -> physical -> AI trace -> style match -> numbers -> proofreading.",
            "Re-run affected downstream stages after any structural rewrite.",
            "",
        ]
    )
    (output / "README.md").write_text(manifest, encoding="utf-8")
    return output, pipeline
