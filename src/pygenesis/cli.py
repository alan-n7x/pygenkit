from __future__ import annotations

import argparse
import sys
from pathlib import Path

from pygenesis.commands.new import create_project


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pygenesis")
    subparsers = parser.add_subparsers(dest="command")

    new_parser = subparsers.add_parser("new")
    new_parser.add_argument("name")

    subparsers.add_parser("version")
    return parser


def main(argv: list[str] | None = None, cwd: str | Path | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "new":
        create_project(args.name, cwd=cwd)
        print("🚀 Creating project...")
        print(f"✔ {args.name}/")
        print("✔ pyproject.toml")
        print("✔ README.md")
        print("✔ src/")
        print("✔ tests/")
        print("Project created successfully.")
        return 0

    if args.command == "version":
        from pygenesis import __version__

        print(__version__)
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
