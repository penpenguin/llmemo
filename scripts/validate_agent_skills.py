#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import subprocess
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
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"').strip("'")
    return data


def skill_dirs(root: Path) -> list[Path]:
    return sorted(
        path for path in root.iterdir() if path.is_dir() and not path.name.startswith(".")
    )


def validate_skill_dir(skill_dir: Path) -> list[str]:
    errors: list[str] = []
    skill_file = skill_dir / "SKILL.md"

    if not skill_file.is_file():
        return [f"{skill_dir.name}: Missing SKILL.md"]

    try:
        meta = parse_simple_frontmatter(skill_file.read_text(encoding="utf-8"))
    except ValueError as exc:
        return [f"{skill_dir.name}: {exc}"]

    for key in ("name", "description"):
        if not meta.get(key):
            errors.append(
                f"{skill_dir.name}: Missing required SKILL.md frontmatter field: {key}"
            )

    local_validator = skill_dir / "scripts" / "validate_skill_bundle.py"
    if local_validator.is_file():
        result = subprocess.run(
            [sys.executable, str(local_validator), str(skill_dir)],
            cwd=skill_dir,
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            output = (result.stdout + result.stderr).strip()
            errors.append(f"{skill_dir.name}: local validator failed: {output}")

    return errors


def validate(root: Path) -> list[str]:
    if not root.is_dir():
        return [f"Skills root does not exist: {root}"]

    dirs = skill_dirs(root)
    if not dirs:
        return [f"No skill bundles found under {root}"]

    errors: list[str] = []
    for skill_dir in dirs:
        errors.extend(validate_skill_dir(skill_dir))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate .agents/skills bundles.")
    parser.add_argument("root", nargs="?", default=".agents/skills")
    args = parser.parse_args()

    errors = validate(Path(args.root).resolve())
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(f"OK: validated {args.root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
