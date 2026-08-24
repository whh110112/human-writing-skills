from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .compiler import compile_audit_prompt, compile_humanize_prompt, compile_prompt
from .detection import PIPELINE_PROFILES
from .fixer import fix_file, format_fix_report
from .linter import format_lint_report, lint_file
from .longform import (
    DEFAULT_BASELINE_BUDGET,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_CONTEXT_BUDGET,
    DEFAULT_OVERLAP_SIZE,
    write_long_form_audit,
)
from .pipeline import write_audit_pipeline
from .protection import compare_protected_files, format_protection_report
from .reference import DEFAULT_REFERENCE_BUDGET
from .source import DEFAULT_SOURCE_BUDGET
from .statistics import analyze_style_file, format_style_statistics
from .skills import list_module_skills, list_skills, list_style_skills


def add_reference_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--reference",
        action="append",
        default=[],
        help="Reference text file for style matching. Can be repeated.",
    )
    parser.add_argument(
        "--reference-style",
        help="Explicit high-level style direction. Activates reference style alignment.",
    )
    parser.add_argument(
        "--reference-budget",
        type=int,
        default=DEFAULT_REFERENCE_BUDGET,
        help=f"Maximum sampled reference characters. Default: {DEFAULT_REFERENCE_BUDGET}.",
    )


def add_source_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--source",
        action="append",
        default=[],
        help="Factual source file for serious-document grounding. Can be repeated.",
    )
    parser.add_argument(
        "--source-budget",
        type=int,
        default=DEFAULT_SOURCE_BUDGET,
        help=f"Maximum sampled factual-source characters. Default: {DEFAULT_SOURCE_BUDGET}.",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="human-writing-skills",
        description="Compile writing SKILLS and continuity context into AI-ready instructions.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="List available writing skills.")
    list_parser.add_argument(
        "--kind",
        choices=["all", "style", "module"],
        default="all",
        help="Filter skills by kind.",
    )

    build = subparsers.add_parser("build", help="Build an instruction pack.")
    build.add_argument("--style", required=True, help="Skill name, such as fiction or news-report.")
    build.add_argument(
        "--module",
        action="append",
        default=[],
        help="Optional technique module. Can be provided multiple times.",
    )
    build.add_argument(
        "--review",
        action="store_true",
        help="Add a compact editor loop and AI-trace rubric.",
    )
    build.add_argument(
        "--deep-review",
        action="store_true",
        help="Add compact review plus relationship, cliche, structure, progress, and narrative number audits.",
    )
    build.add_argument(
        "--strict-continuity",
        action="store_true",
        help="Add occupancy, spatial blocking, and appearance/prop generation guards.",
    )
    build.add_argument(
        "--number-sense",
        action="store_true",
        help="Add dynamic number necessity review for false precision.",
    )
    build.add_argument("--context", help="Optional Markdown continuity ledger or source notes.")
    build.add_argument(
        "--original",
        help="Original text file for a rewrite. Activates semantic-fidelity protection.",
    )
    build.add_argument("--task", required=True, help="Writing task to perform.")
    build.add_argument(
        "--protect-content",
        action="store_true",
        help="Explicitly protect factual spans; serious academic/news output enables this automatically.",
    )
    build.add_argument(
        "--protect-term",
        action="append",
        default=[],
        help="Exact term that generated prose must preserve. Can be repeated.",
    )
    add_reference_arguments(build)
    add_source_arguments(build)

    humanize = subparsers.add_parser(
        "humanize",
        help="Build a focused rewrite prompt that reduces formulaic AI tone without flattening voice.",
    )
    humanize.add_argument("--draft", required=True, help="Original Markdown/text file to humanize.")
    humanize.add_argument(
        "--style",
        required=True,
        choices=list_style_skills(),
        help="Genre contract for the rewrite.",
    )
    humanize.add_argument(
        "--mode",
        choices=["quick", "deep"],
        default="quick",
        help="Quick loads the minimum rewrite stack; deep adds structural editor passes.",
    )
    humanize.add_argument(
        "--task",
        help="Optional rewrite direction. The default preserves language, genre, meaning, and voice.",
    )
    humanize.add_argument("--context", help="Optional continuity ledger or prior chapters.")
    humanize.add_argument(
        "--module",
        action="append",
        default=[],
        help="Optional extra technique module. Can be repeated.",
    )
    humanize.add_argument(
        "--strict-continuity",
        action="store_true",
        help="Add occupancy, spatial blocking, and appearance/prop rewrite guards.",
    )
    humanize.add_argument(
        "--with-examples",
        action="store_true",
        help="Load the on-demand before/after example library.",
    )
    humanize.add_argument(
        "--protect-content",
        action="store_true",
        help="Explicitly protect factual spans; serious document styles enable this automatically.",
    )
    humanize.add_argument(
        "--protect-term",
        action="append",
        default=[],
        help="Exact term the rewrite must preserve. Can be repeated.",
    )
    add_reference_arguments(humanize)
    add_source_arguments(humanize)

    audit = subparsers.add_parser("audit", help="Build a forensic audit pack for an existing draft.")
    audit.add_argument("--draft", required=True, help="Markdown/text file containing the draft to audit.")
    audit.add_argument("--context", help="Optional Markdown continuity ledger or source notes.")
    audit.add_argument(
        "--original",
        help="Pre-rewrite original. Automatically adds the fidelity profile.",
    )
    audit.add_argument(
        "--module",
        action="append",
        default=[],
        help="Optional extra audit module. Can be provided multiple times.",
    )
    audit.add_argument(
        "--profile",
        action="append",
        choices=["full", *PIPELINE_PROFILES],
        help="Audit profile. Can be repeated. Defaults to full.",
    )
    audit.add_argument(
        "--strict-continuity",
        default=True,
        action="store_true",
        help="Include physical checks in the default full profile. Enabled by default.",
    )
    audit.add_argument(
        "--no-strict-continuity",
        dest="strict_continuity",
        action="store_false",
        help="Remove physical checks from the default full profile.",
    )
    audit.add_argument(
        "--numbers",
        action="store_true",
        help="Legacy alias that adds the numbers profile to the selected audit.",
    )
    add_reference_arguments(audit)
    add_source_arguments(audit)
    audit.add_argument(
        "--document-type",
        choices=["auto", "general", "fiction", "webnovel", "self-media", "argumentative", "academic-paper", "formal-document", "news-report", "legal", "technical"],
        default="auto",
        help="Controls serious-document protection. Auto requires strong textual evidence.",
    )
    audit.add_argument(
        "--protect-content",
        action="store_true",
        help="Add a manifest for numbers, citations, equations, URLs, code, quotes, and explicit terms.",
    )
    audit.add_argument(
        "--protect-term",
        action="append",
        default=[],
        help="Exact protected term. Can be repeated.",
    )

    pipeline = subparsers.add_parser(
        "pipeline",
        help="Write independent multi-stage audit prompt files for a draft.",
    )
    pipeline.add_argument("--draft", required=True, help="Markdown/text draft to audit.")
    pipeline.add_argument("--context", help="Optional continuity ledger or source notes.")
    pipeline.add_argument(
        "--original",
        help="Pre-rewrite original. Adds one isolated fidelity stage.",
    )
    pipeline.add_argument(
        "--output-dir",
        help="Output directory. Defaults to <draft-name>-audit-pipeline.",
    )
    add_reference_arguments(pipeline)
    add_source_arguments(pipeline)
    pipeline.add_argument(
        "--document-type",
        choices=["auto", "general", "fiction", "webnovel", "self-media", "argumentative", "academic-paper", "formal-document", "news-report", "legal", "technical"],
        default="auto",
        help="Controls serious-document protection. Auto requires strong textual evidence.",
    )
    pipeline.add_argument(
        "--protect-content",
        action="store_true",
        help="Include a protected-content manifest in every generated stage.",
    )
    pipeline.add_argument(
        "--protect-term",
        action="append",
        default=[],
        help="Exact protected term. Can be repeated.",
    )
    pipeline.add_argument(
        "--lint-style",
        choices=["general", *list_style_skills()],
        default="general",
        help="Genre tolerance profile for the deterministic preflight lint.",
    )
    pipeline.add_argument(
        "--lint-allow",
        action="append",
        default=[],
        help="Allowed lint rule id or category. Can be repeated.",
    )
    pipeline.add_argument(
        "--with-stats",
        action="store_true",
        help="Also write optional deterministic style-statistics preflight files.",
    )
    selection = pipeline.add_mutually_exclusive_group()
    selection.add_argument(
        "--auto",
        action="store_true",
        help="Keep core stages and add optional stages only when the draft contains matching cues.",
    )
    selection.add_argument(
        "--stage",
        action="append",
        choices=PIPELINE_PROFILES,
        help="Explicit stage. Can be repeated. Without --auto or --stage, the established broad stages are written.",
    )

    chunk_audit = subparsers.add_parser(
        "chunk-audit",
        help="Split a long manuscript or report into bounded style and continuity audit passes.",
    )
    chunk_audit.add_argument("--draft", required=True, help="Long Markdown/text draft to audit.")
    chunk_audit.add_argument(
        "--style",
        required=True,
        choices=list_style_skills(),
        help="Genre contract used for style-drift interpretation.",
    )
    chunk_audit.add_argument(
        "--context",
        "--outline",
        dest="context",
        help="Outline, character bible, report plan, or continuity ledger used as canonical context.",
    )
    chunk_audit.add_argument(
        "--output-dir",
        help="Output directory. Defaults to <draft-name>-long-form-audit.",
    )
    chunk_audit.add_argument(
        "--chunk-size",
        type=int,
        default=DEFAULT_CHUNK_SIZE,
        help=f"Maximum target characters in each unique audit body. Default: {DEFAULT_CHUNK_SIZE}.",
    )
    chunk_audit.add_argument(
        "--overlap",
        type=int,
        default=DEFAULT_OVERLAP_SIZE,
        help=f"Read-only lead-in characters from the preceding block. Default: {DEFAULT_OVERLAP_SIZE}.",
    )
    chunk_audit.add_argument(
        "--baseline-chunk",
        type=int,
        default=1,
        help="One-based candidate manuscript chunk used as the style baseline when no reference file is supplied.",
    )
    chunk_audit.add_argument(
        "--context-budget",
        type=int,
        default=DEFAULT_CONTEXT_BUDGET,
        help=f"Maximum sampled outline/context characters per audit prompt. Default: {DEFAULT_CONTEXT_BUDGET}.",
    )
    chunk_audit.add_argument(
        "--baseline-budget",
        type=int,
        default=DEFAULT_BASELINE_BUDGET,
        help=f"Maximum sampled baseline/reference characters per audit prompt. Default: {DEFAULT_BASELINE_BUDGET}.",
    )
    chunk_audit.add_argument(
        "--reference",
        action="append",
        default=[],
        help="Explicit approved style reference. Can be repeated; overrides the baseline chunk for style evidence.",
    )
    chunk_audit.add_argument(
        "--reference-style",
        help="Explicit high-level style direction. Never activates without this flag or --reference.",
    )

    lint = subparsers.add_parser(
        "lint",
        help="Run deterministic writing-pattern checks with evidence locations.",
    )
    lint.add_argument("--draft", required=True, help="Markdown/text file to inspect.")
    lint.add_argument(
        "--style",
        choices=["general", *list_style_skills()],
        default="general",
        help="Genre tolerance profile.",
    )
    lint.add_argument(
        "--format",
        choices=["markdown", "json"],
        default="markdown",
        help="Output format.",
    )
    lint.add_argument(
        "--allow",
        action="append",
        default=[],
        help="Allowed rule id or category. Can be repeated.",
    )
    lint.add_argument(
        "--fail-score",
        type=int,
        help="Return exit code 1 when the transparent pattern score reaches this value.",
    )

    stats = subparsers.add_parser(
        "stats",
        help="Report optional language-aware style statistics without authorship claims.",
    )
    stats.add_argument("--draft", required=True, help="Markdown/text file to inspect.")
    stats.add_argument(
        "--style",
        choices=["general", *list_style_skills()],
        default="general",
        help="Genre tolerance profile.",
    )
    stats.add_argument(
        "--format",
        choices=["markdown", "json"],
        default="markdown",
        help="Output format.",
    )

    fix = subparsers.add_parser(
        "fix",
        help="Preview conservative mechanical fixes; semantic rewriting is never automatic.",
    )
    fix.add_argument("--draft", required=True, help="Markdown/text file to inspect.")
    fix_mode = fix.add_mutually_exclusive_group()
    fix_mode.add_argument(
        "--preview",
        action="store_true",
        help="Preview only. This is the default when no write option is supplied.",
    )
    fix_mode.add_argument(
        "--apply",
        action="store_true",
        help="Write the conservative candidate back to the original file.",
    )
    fix.add_argument(
        "--output",
        help="Write the conservative candidate to a separate file.",
    )
    fix.add_argument(
        "--format",
        choices=["markdown", "json"],
        default="markdown",
        help="Preview/report format.",
    )

    verify = subparsers.add_parser(
        "verify",
        help="Compare protected numbers, citations, equations, URLs, code, quotes, and terms after rewriting.",
    )
    verify.add_argument("--source", required=True, help="Original source file.")
    verify.add_argument("--candidate", required=True, help="Rewritten candidate file.")
    verify.add_argument(
        "--protect-term",
        action="append",
        default=[],
        help="Additional exact term to compare. Can be repeated.",
    )
    verify.add_argument(
        "--format",
        choices=["markdown", "json"],
        default="markdown",
        help="Output format.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "list":
        if args.kind == "style":
            skills = list_style_skills()
        elif args.kind == "module":
            skills = list_module_skills()
        else:
            skills = list_skills()
        for skill in skills:
            print(skill)
        return 0

    if args.command == "build":
        try:
            prompt = compile_prompt(
                style=args.style,
                task=args.task,
                context_path=args.context,
                modules=args.module,
                review=args.review,
                strict_continuity=args.strict_continuity,
                number_sense=args.number_sense,
                deep_review=args.deep_review,
                reference_paths=args.reference,
                reference_style=args.reference_style,
                reference_budget=args.reference_budget,
                source_paths=args.source,
                source_budget=args.source_budget,
                original_path=args.original,
                protect_content=args.protect_content,
                protect_terms=args.protect_term,
            )
        except (FileNotFoundError, OSError, ValueError) as exc:
            parser.error(str(exc))
        print(prompt, end="")
        return 0

    if args.command == "humanize":
        try:
            prompt = compile_humanize_prompt(
                draft_path=args.draft,
                style=args.style,
                mode=args.mode,
                task=args.task,
                context_path=args.context,
                modules=args.module,
                strict_continuity=args.strict_continuity,
                with_examples=args.with_examples,
                reference_paths=args.reference,
                reference_style=args.reference_style,
                reference_budget=args.reference_budget,
                source_paths=args.source,
                source_budget=args.source_budget,
                protect_content=args.protect_content,
                protect_terms=args.protect_term,
            )
        except (FileNotFoundError, OSError, ValueError) as exc:
            parser.error(str(exc))
        print(prompt, end="")
        return 0

    if args.command == "audit":
        try:
            prompt = compile_audit_prompt(
                draft_path=args.draft,
                context_path=args.context,
                modules=args.module,
                strict_continuity=args.strict_continuity,
                number_sense=args.numbers,
                profiles=args.profile,
                reference_paths=args.reference,
                reference_style=args.reference_style,
                reference_budget=args.reference_budget,
                source_paths=args.source,
                source_budget=args.source_budget,
                original_path=args.original,
                protect_content=args.protect_content,
                protect_terms=args.protect_term,
                document_type=args.document_type,
            )
        except (FileNotFoundError, OSError, ValueError) as exc:
            parser.error(str(exc))
        print(prompt, end="")
        return 0

    if args.command == "pipeline":
        output_dir = args.output_dir or f"{Path(args.draft).stem}-audit-pipeline"
        try:
            output, stages = write_audit_pipeline(
                args.draft,
                output_dir,
                context_path=args.context,
                stages=args.stage,
                auto=args.auto,
                reference_paths=args.reference,
                reference_style=args.reference_style,
                reference_budget=args.reference_budget,
                source_paths=args.source,
                source_budget=args.source_budget,
                original_path=args.original,
                protect_content=args.protect_content,
                protect_terms=args.protect_term,
                document_type=args.document_type,
                lint_style=args.lint_style,
                lint_allow=set(args.lint_allow),
                with_stats=args.with_stats,
            )
        except (FileNotFoundError, OSError, ValueError) as exc:
            parser.error(str(exc))
        print(f"Wrote {len(stages)} independent audit stages to {output.resolve()}")
        for stage in stages:
            print(f"{stage.order:02d} {stage.profile}: {stage.reason}")
        return 0

    if args.command == "chunk-audit":
        output_dir = args.output_dir or f"{Path(args.draft).stem}-long-form-audit"
        try:
            output, chunks = write_long_form_audit(
                args.draft,
                output_dir,
                style=args.style,
                context_path=args.context,
                reference_paths=args.reference,
                reference_style=args.reference_style,
                chunk_size=args.chunk_size,
                overlap=args.overlap,
                baseline_chunk=args.baseline_chunk,
                context_budget=args.context_budget,
                baseline_budget=args.baseline_budget,
            )
        except (FileNotFoundError, OSError, ValueError) as exc:
            parser.error(str(exc))
        print(f"Wrote {len(chunks)} bounded long-form audit prompts to {output.resolve()}")
        print("Run 00-baseline-prompt.md first, then numbered chunks, then 9999-reconcile-prompt.md.")
        return 0

    if args.command == "lint":
        try:
            report = lint_file(args.draft, style=args.style, allow=set(args.allow))
        except (FileNotFoundError, OSError, ValueError) as exc:
            parser.error(str(exc))
        print(format_lint_report(report, args.format), end="")
        if args.fail_score is not None and report.score >= args.fail_score:
            return 1
        return 0

    if args.command == "stats":
        try:
            report = analyze_style_file(args.draft, style=args.style)
        except (FileNotFoundError, OSError, ValueError) as exc:
            parser.error(str(exc))
        print(format_style_statistics(report, args.format), end="")
        return 0

    if args.command == "fix":
        if args.preview and args.output:
            parser.error("--preview cannot be combined with --output.")
        if args.apply and args.output:
            parser.error("--apply cannot be combined with --output.")
        try:
            report = fix_file(args.draft, output_path=args.output, apply=args.apply)
        except (FileNotFoundError, OSError, ValueError) as exc:
            parser.error(str(exc))
        print(format_fix_report(report, args.format), end="")
        return 0

    if args.command == "verify":
        try:
            report = compare_protected_files(
                args.source,
                args.candidate,
                terms=args.protect_term,
            )
        except (FileNotFoundError, OSError, ValueError) as exc:
            parser.error(str(exc))
        print(format_protection_report(report, args.format), end="")
        return 0 if report.ok else 1

    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
