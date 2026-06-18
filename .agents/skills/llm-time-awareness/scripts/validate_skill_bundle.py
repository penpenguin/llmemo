#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


FRONTMATTER_RE = re.compile(r"\A---\n(?P<body>.*?)\n---\n", re.DOTALL)


def parse_simple_frontmatter(text: str) -> dict[str, str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        raise ValueError("SKILL.md must start with YAML frontmatter bounded by --- lines.")

    data: dict[str, str] = {}
    for raw_line in match.group("body").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"').strip("'")
    return data


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    skill_files = [p for p in root.rglob("*") if p.name.lower() == "skill.md"]

    if len(skill_files) != 1:
        errors.append(f"Expected exactly one SKILL.md/skill.md, found {len(skill_files)}.")
        return errors

    skill_file = skill_files[0]
    if skill_file.parent != root:
        errors.append(f"SKILL.md must be at the bundle root, found at {skill_file.relative_to(root)}.")

    text = skill_file.read_text(encoding="utf-8")
    try:
        meta = parse_simple_frontmatter(text)
    except ValueError as exc:
        errors.append(str(exc))
        meta = {}

    for key in ("name", "description"):
        if not meta.get(key):
            errors.append(f"Missing required SKILL.md frontmatter field: {key}")

    for folder in ("scripts", "references", "assets"):
        if not (root / folder).is_dir():
            errors.append(f"Missing expected folder: {folder}/")

    if not (root / "assets" / "time_context.schema.json").is_file():
        errors.append("Missing assets/time_context.schema.json")

    if not (root / "scripts" / "build_time_context.py").is_file():
        errors.append("Missing scripts/build_time_context.py")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a skill bundle folder.")
    parser.add_argument("root", nargs="?", default=".")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    errors = validate(root)

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"OK: {root.name} looks like a valid skill bundle.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
