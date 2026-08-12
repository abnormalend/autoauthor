#!/usr/bin/env python3
"""Genre pack parsing and validation. Library module — no CLI.

A genre pack is a markdown file whose first block is JSON frontmatter
delimited by lines of exactly '---', followed by '## ' prose sections.

Frontmatter is JSON rather than YAML because the plugin's scripts are
stdlib-only and Python ships no YAML parser.
"""
import json
import re
from pathlib import Path

ROLES = {"primary", "secondary", "modifier"}

# Dimensions the base rubric already scores. A pack's pillar dimensions may
# not collide with these — that is what stops a literary pack from
# double-counting prose against the base craft category.
RESERVED_DIMENSIONS = {
    "character_depth", "character_distinctiveness", "character_secrets",
    "outline_completeness", "foreshadowing_balance",
    "internal_consistency", "voice_clarity", "canon_coverage",
}

WEIGHT_KEYS = ("pillar", "character", "structure", "craft")

# Fields only a primary may declare. A modifier that sets these is trying to
# own structure it is not allowed to own.
PRIMARY_ONLY_FIELDS = ("weights", "pillar_label", "beat_system", "shape")

CORE_PROJECT_FILES = {
    "seed.txt", "voice.md", "world.md", "characters.md", "outline.md",
    "canon.md", "MYSTERY.md", "state.json", "results.tsv", "arc_summary.md",
    "manuscript.md", "voice_wells.json", "import_source.md",
}

# '- <key> — <criteria>'  (em dash, not hyphen)
DIMENSION_RE = re.compile(r"^-\s+([a-z][a-z0-9_]*)\s+—", re.M)
SECTION_RE = re.compile(r"^##\s+(.+?)\s*$", re.M)


class PackError(Exception):
    """Malformed pack. The message is user-facing."""


def parse_pack(path):
    """Parse a pack file.

    Returns {'meta': dict, 'sections': [str], 'dimensions': [str],
             'path': Path, 'body': str}.
    Raises PackError if the file is unreadable or the frontmatter is broken.
    """
    path = Path(path)
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as e:
        raise PackError(f"{path}: cannot read pack file: {e}")
    meta, body = _split_frontmatter(text, path)
    return {
        "meta": meta,
        "sections": SECTION_RE.findall(body),
        "dimensions": _pillar_dimensions(body),
        "path": path,
        "body": body,
    }


def _split_frontmatter(text, path):
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise PackError(f"{path}: missing '---' frontmatter opener on line 1")
    close = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            close = i
            break
    if close is None:
        raise PackError(f"{path}: frontmatter never closed with '---'")
    raw = "\n".join(lines[1:close])
    try:
        meta = json.loads(raw)
    except json.JSONDecodeError as e:
        raise PackError(f"{path}: frontmatter is not valid JSON: {e}")
    if not isinstance(meta, dict):
        raise PackError(f"{path}: frontmatter must be a JSON object")
    return meta, "\n".join(lines[close + 1:])


def section_body(body, heading):
    """Text under '## <heading>' up to the next '## ', or None if absent."""
    match = re.search(rf"^##\s+{re.escape(heading)}\s*$", body, re.M)
    if not match:
        return None
    rest = body[match.end():]
    nxt = re.search(r"^##\s+", rest, re.M)
    return rest[:nxt.start()] if nxt else rest


def _pillar_dimensions(body):
    section = section_body(body, "Pillar Dimensions")
    if section is None:
        return []
    return DIMENSION_RE.findall(section)
