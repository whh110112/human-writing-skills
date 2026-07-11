from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .compiler import compile_audit_prompt, read_optional
from .detection import PIPELINE_PROFILES, ProfileDecision, detect_audit_profiles


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
) -> tuple[list[str], list[ProfileDecision]]:
    if stages:
        selected = list(dict.fromkeys(stages))
        unknown = set(selected) - set(PIPELINE_PROFILES)
        if unknown:
            raise ValueError(f"Unknown pipeline stage: {', '.join(sorted(unknown))}")
        decisions = [
            ProfileDecision(profile, profile in selected, "Explicitly selected by the user.")
            for profile in PIPELINE_PROFILES
        ]
        return selected, decisions
    if auto:
        decisions = detect_audit_profiles(draft)
        return [decision.profile for decision in decisions if decision.selected], decisions
    decisions = [
        ProfileDecision(profile, True, "Included in the complete default pipeline.")
        for profile in PIPELINE_PROFILES
    ]
    return list(PIPELINE_PROFILES), decisions


def build_audit_pipeline(
    draft_path: str,
    context_path: str | None = None,
    stages: list[str] | None = None,
    auto: bool = False,
) -> tuple[list[AuditStage], list[ProfileDecision]]:
    draft = read_optional(draft_path)
    selected, decisions = select_pipeline_profiles(draft, stages=stages, auto=auto)
    reason_by_profile = {decision.profile: decision.reason for decision in decisions}
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
) -> tuple[Path, list[AuditStage]]:
    pipeline, decisions = build_audit_pipeline(
        draft_path,
        context_path=context_path,
        stages=stages,
        auto=auto,
    )
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

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
            "logic -> character/relationship -> physical -> AI trace -> numbers -> proofreading.",
            "Re-run affected downstream stages after any structural rewrite.",
            "",
        ]
    )
    (output / "README.md").write_text(manifest, encoding="utf-8")
    return output, pipeline
