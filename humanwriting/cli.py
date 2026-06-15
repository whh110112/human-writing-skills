from __future__ import annotations

import argparse
import sys

from .compiler import compile_prompt
from .skills import list_skills


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="human-writing-skills",
        description="Compile writing SKILLS and continuity context into AI-ready instructions.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list", help="List available writing skills.")

    build = subparsers.add_parser("build", help="Build an instruction pack.")
    build.add_argument("--style", required=True, help="Skill name, such as fiction or news-report.")
    build.add_argument("--context", help="Optional Markdown continuity ledger or source notes.")
    build.add_argument("--task", required=True, help="Writing task to perform.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "list":
        for skill in list_skills():
            print(skill)
        return 0

    if args.command == "build":
        print(compile_prompt(args.style, args.task, args.context), end="")
        return 0

    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
