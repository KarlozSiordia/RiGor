#!/usr/bin/env python3
"""Build the Claude.ai upload zip for the skill in skills/<skill-name>/.

Checks the skill's frontmatter against the Agent Skills spec and this
project's caps, then lists what the zip would hold. Nothing is written
unless --write is given; unknown or abbreviated arguments are rejected.
No network access and no model call.

    python scripts/package_skill.py                  check and list; writes nothing
    python scripts/package_skill.py --write          also writes dist/<skill-name>.zip
    python scripts/package_skill.py --write --out D  writes D/<skill-name>.zip

The zip holds the skill folder at its root (<skill-name>/SKILL.md, ...), the
layout skill-creator's packager produces, plus the repository's LICENSE as
<skill-name>/LICENSE.txt so the license text travels with the upload.
Entries are sorted and carry a fixed timestamp, so the same files give the
same zip bytes on the same Python build.
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SKILL = "research-integrity-statistics"

# Agent Skills spec (agentskills.io/specification); skill-creator's quick_validate.py
ALLOWED_KEYS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
NAME_MAX = 64
DESCRIPTION_MAX = 1024
COMPATIBILITY_MAX = 500
NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
# The project's line cap on SKILL.md; the spec allows 500 lines
LINE_CAP = 150

EXCLUDE_NAMES = {".gitkeep", ".DS_Store", "Thumbs.db", "desktop.ini"}
EXCLUDE_DIRS = {"__pycache__", ".git"}
EXCLUDE_SUFFIXES = {".pyc"}
FIXED_TIME = (1980, 1, 1, 0, 0, 0)


def read_frontmatter(text: str) -> tuple[dict[str, str], list[str]]:
    """Parse the frontmatter subset this repository uses.

    Top-level 'key: value' lines with single-line values, and indented
    'key: value' lines under 'metadata:'. Anything else is reported as an
    error, so it gets checked with a full YAML validator instead.
    """
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        return {}, ["SKILL.md must start with a '---' line (no BOM, no leading blank line)"]
    close = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if close is None:
        return {}, ["frontmatter has no closing '---' line"]

    fields: dict[str, str] = {}
    errors: list[str] = []
    current = None
    for raw in lines[1:close]:
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if raw[0] in " \t":
            if current != "metadata":
                errors.append(f"indented line outside metadata: {raw.strip()!r}")
            elif not re.match(r"^\s+[A-Za-z0-9_.-]+:\s*\S", raw):
                errors.append(f"metadata entry is not 'key: value': {raw.strip()!r}")
            continue
        match = re.match(r"^([A-Za-z0-9_-]+):(.*)$", raw)
        if not match:
            errors.append(f"line is not 'key: value': {raw!r}")
            continue
        key, value = match.group(1), match.group(2).strip()
        if key in fields:
            errors.append(f"duplicate key: {key}")
        current = key
        if value[:1] in ("|", ">"):
            errors.append(f"{key}: block scalars are outside the subset this script checks")
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        elif value[:1] in ("\"", "'"):
            errors.append(f"{key}: quoted value has no closing quote on the same line")
        elif ": " in value or " #" in value or value.endswith(":"):
            # YAML reads these differently; Claude Code then loads the skill with no description
            errors.append(f"{key}: unquoted value contains ': ' or ' #'; quote it")
        fields[key] = value
    if fields.get("metadata"):
        errors.append("metadata must be a map of indented 'key: value' lines")
    return fields, errors


def check_skill(skill_dir: Path) -> tuple[list[str], dict[str, int]]:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        return [f"missing {skill_md}"], {}
    text = skill_md.read_text(encoding="utf-8")
    fields, errors = read_frontmatter(text)

    unexpected = sorted(set(fields) - ALLOWED_KEYS)
    if unexpected:
        errors.append(f"frontmatter keys outside the spec (upload would fail): {', '.join(unexpected)}")

    name = fields.get("name", "")
    if not name:
        errors.append("name is missing or empty")
    else:
        if len(name) > NAME_MAX:
            errors.append(f"name is {len(name)} characters; the cap is {NAME_MAX}")
        if not NAME_RE.match(name):
            errors.append(f"name {name!r}: lowercase letters, digits and single hyphens only")
        if name != skill_dir.name:
            errors.append(f"name {name!r} does not match the folder name {skill_dir.name!r}")

    description = fields.get("description", "")
    if not description:
        errors.append("description is missing or empty")
    else:
        if len(description) > DESCRIPTION_MAX:
            errors.append(f"description is {len(description)} characters; the cap is {DESCRIPTION_MAX}")
        if "<" in description or ">" in description:
            errors.append("description contains an angle bracket, which skill-creator's validator rejects")

    compatibility = fields.get("compatibility")
    if compatibility is not None and len(compatibility) > COMPATIBILITY_MAX:
        errors.append(f"compatibility is {len(compatibility)} characters; the cap is {COMPATIBILITY_MAX}")

    line_count = len(text.splitlines())
    if line_count > LINE_CAP:
        errors.append(f"SKILL.md has {line_count} lines; the line cap is {LINE_CAP}")

    references = skill_dir / "references"
    if references.is_dir():
        nested = sorted(p.name for p in references.iterdir() if p.is_dir() and p.name not in EXCLUDE_DIRS)
        if nested:
            errors.append(f"references must be one level deep; subfolders found: {', '.join(nested)}")

    info = {"description_chars": len(description), "skill_md_lines": line_count}
    return errors, info


def files_to_pack(skill_dir: Path) -> list[tuple[Path, str]]:
    entries = []
    for path in sorted(skill_dir.rglob("*")):
        rel = path.relative_to(skill_dir)
        if not path.is_file() or any(part in EXCLUDE_DIRS for part in rel.parts):
            continue
        if path.name in EXCLUDE_NAMES or path.suffix in EXCLUDE_SUFFIXES:
            continue
        entries.append((path, f"{skill_dir.name}/{rel.as_posix()}"))
    license_file = REPO_ROOT / "LICENSE"
    if license_file.is_file() and not (skill_dir / "LICENSE.txt").exists():
        entries.append((license_file, f"{skill_dir.name}/LICENSE.txt"))
    return sorted(entries, key=lambda entry: entry[1])


def write_zip(entries: list[tuple[Path, str]], out_path: Path) -> None:
    tmp_path = out_path.with_name(out_path.name + ".tmp")
    with zipfile.ZipFile(tmp_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for source, arcname in entries:
            info = zipfile.ZipInfo(arcname, date_time=FIXED_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            archive.writestr(info, source.read_bytes())
    tmp_path.replace(out_path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check the skill and build its Claude.ai upload zip. Writes nothing without --write.",
        allow_abbrev=False,
    )
    parser.add_argument("--skill", default=DEFAULT_SKILL, help=f"skill folder under skills/ (default: {DEFAULT_SKILL})")
    parser.add_argument("--write", action="store_true", help="write the zip; without this flag nothing is written")
    parser.add_argument("--out", type=Path, help="directory for the zip (default: dist/ in the repository); needs --write")
    args = parser.parse_args(argv)
    if args.out is not None and not args.write:
        parser.error("--out needs --write")
    if not NAME_RE.match(args.skill):
        parser.error("--skill takes a folder name under skills/, not a path")

    skill_dir = REPO_ROOT / "skills" / args.skill
    if not skill_dir.is_dir():
        print(f"error: no skill folder at {skill_dir}", file=sys.stderr)
        return 1

    errors, info = check_skill(skill_dir)
    entries = files_to_pack(skill_dir)
    print(f"skill: {skill_dir.relative_to(REPO_ROOT).as_posix()}")
    for key, value in info.items():
        print(f"  {key}: {value}")
    print("zip entries:")
    for _, arcname in entries:
        print(f"  {arcname}")
    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        return 1
    if not args.write:
        print("Checks passed. Nothing written (add --write to build the zip).")
        return 0

    out_dir = args.out if args.out is not None else REPO_ROOT / "dist"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{args.skill}.zip"
    write_zip(entries, out_path)
    digest = hashlib.sha256(out_path.read_bytes()).hexdigest()
    print(f"Wrote {out_path}")
    print(f"  sha256 {digest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
