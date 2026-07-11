from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .compiler import compile_audit_prompt, compile_prompt
from .detection import PIPELINE_PROFILES
from .pipeline import write_audit_pipeline
from .skills import list_module_skills, list_skills, list_style_skills


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
            "physical",
            "relationship",
            "ai-trace",
            "numbers",
            "proofread",
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
                args.style,
                args.task,
                args.context,
                args.module,
                args.review,
                args.strict_continuity,
                args.number_sense,
                args.deep_review,
            )
        except (FileNotFoundError, OSError, ValueError) as exc:
            parser.error(str(exc))
        print(prompt, end="")
        return 0

    if args.command == "audit":
        try:
            prompt = compile_audit_prompt(
                args.draft,
                args.context,
                args.module,
                args.strict_continuity,
                args.numbers,
                args.profile,
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
            )
        except (FileNotFoundError, OSError, ValueError) as exc:
            parser.error(str(exc))
        print(f"Wrote {len(stages)} independent audit stages to {output.resolve()}")
        for stage in stages:
            print(f"{stage.order:02d} {stage.profile}: {stage.reason}")
        return 0

    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
