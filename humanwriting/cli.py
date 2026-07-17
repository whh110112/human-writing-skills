from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .compiler import compile_audit_prompt, compile_prompt
from .detection import PIPELINE_PROFILES
from .linter import format_lint_report, lint_file
from .pipeline import write_audit_pipeline
from .protection import compare_protected_files, format_protection_report
from .reference import DEFAULT_REFERENCE_BUDGET
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

    audit = subparsers.add_parser("audit", help="Build a forensic audit pack for an existing draft.")
    audit.add_argument("--draft", required=True, help="Markdown/text file containing the draft to audit.")
    audit.add_argument("--context", help="Optional Markdown continuity ledger or source notes.")
    audit.add_argument(
        "--module",
        action="append",
        default=[],
        help="Optional extra audit module. Can be provided multiple times.",
    )
    audit.add_argument(
        "--profile",
        action="append",
        choices=[
            "full",
            "logic",
            "character",
            "voice",
            "serial",
            "texture",
            "physical",
            "relationship",
            "ai-trace",
            "numbers",
            "proofread",
            "style-match",
        ],
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
    audit.add_argument(
        "--document-type",
        choices=["auto", "general", "fiction", "webnovel", "self-media", "argumentative", "academic-paper", "news-report", "legal", "technical"],
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
        "--output-dir",
        help="Output directory. Defaults to <draft-name>-audit-pipeline.",
    )
    add_reference_arguments(pipeline)
    pipeline.add_argument(
        "--document-type",
        choices=["auto", "general", "fiction", "webnovel", "self-media", "argumentative", "academic-paper", "news-report", "legal", "technical"],
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
        help="Explicit stage. Can be repeated. Without --auto or --stage, all stages are written.",
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
                protect_content=args.protect_content,
                protect_terms=args.protect_term,
                document_type=args.document_type,
                lint_style=args.lint_style,
                lint_allow=set(args.lint_allow),
            )
        except (FileNotFoundError, OSError, ValueError) as exc:
            parser.error(str(exc))
        print(f"Wrote {len(stages)} independent audit stages to {output.resolve()}")
        for stage in stages:
            print(f"{stage.order:02d} {stage.profile}: {stage.reason}")
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
