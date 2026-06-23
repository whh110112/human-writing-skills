from __future__ import annotations

import argparse
import sys

from .compiler import compile_prompt
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
        help="Add the editor loop and AI trace rubric modules.",
    )
    build.add_argument(
        "--strict-continuity",
        action="store_true",
        help="Add spatial blocking, appearance/prop continuity, and physical audit modules.",
    )
    build.add_argument("--context", help="Optional Markdown continuity ledger or source notes.")
    build.add_argument("--task", required=True, help="Writing task to perform.")
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
        print(
            compile_prompt(
                args.style,
                args.task,
                args.context,
                args.module,
                args.review,
                args.strict_continuity,
            ),
            end="",
        )
        return 0

    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
