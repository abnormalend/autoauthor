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

# A fenced block, ``` or ~~~ (3+), opened and closed by matching markers.
# Used to blank fenced regions before structural matching so a pack author
# showing example syntax in a fence (e.g. under '## Artifacts') can't be
# mistaken for a real heading or dimension line. An unclosed fence simply
# doesn't match and masks nothing — that is an acceptable, safe failure.
FENCE_RE = re.compile(r"^(?P<f>```+|~~~+).*?^(?P=f)[ \t]*$", re.M | re.S)

# '- <key> — <criteria>'  (em dash, not hyphen)
DIMENSION_RE = re.compile(r"^-\s+([a-z][a-z0-9_]*)\s+—", re.M)
# Same shape but with a hyphen or en dash where an em dash belongs — the
# typo autocorrect produces. Never matches a line DIMENSION_RE also matches,
# since the two require different characters in the same position.
DIMENSION_LOOSE_RE = re.compile(r"^-\s+([a-z][a-z0-9_]*)\s+[–-]\s", re.M)
SECTION_RE = re.compile(r"^##\s+(.+?)\s*$", re.M)


class PackError(Exception):
    """Malformed pack. The message is user-facing."""


def _mask_fences(text):
    """Same-length copy of text with fenced blocks blanked to spaces
    (newlines preserved), so structural regexes skip fenced content while
    offsets into the mask still index the corresponding original text."""
    return FENCE_RE.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), text)


def parse_pack(path):
    """Parse a pack file.

    Returns a dict:
      'meta'                — the frontmatter, as a dict
      'sections'            — '## ' heading names, in order, outside fences
      'dimensions'          — '## Pillar Dimensions' keys written with the
                               required em dash, in order
      'malformed_dimensions'— keys in that same section written with a
                               hyphen or en dash instead of an em dash;
                               Task 2's validator turns these into a
                               specific error rather than silently
                               undercounting real dimensions
      'path'                — the Path passed in
      'body'                — the file's content after the frontmatter,
                               verbatim (not masked) — later phases feed
                               this prose to LLM judges

    Headings and dimension bullets inside fenced code blocks (``` or ~~~)
    are ignored when locating sections and dimensions, but 'sections' and
    'body' still return the original, unmasked text.

    Raises PackError if the file is unreadable or the frontmatter is broken.
    """
    path = Path(path)
    try:
        text = path.read_text(encoding="utf-8-sig")
    except OSError as e:
        raise PackError(f"{path}: cannot read pack file: {e}") from e
    meta, body = _split_frontmatter(text, path)
    dimensions, malformed = _pillar_dimensions(body)
    return {
        "meta": meta,
        "sections": SECTION_RE.findall(_mask_fences(body)),
        "dimensions": dimensions,
        "malformed_dimensions": malformed,
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
        raise PackError(
            f"{path}:{e.lineno + 1}: frontmatter is not valid JSON: "
            f"{e.msg} (column {e.colno})") from e
    if not isinstance(meta, dict):
        raise PackError(
            f"{path}: frontmatter must be a JSON object "
            f"(got a JSON {type(meta).__name__})")
    return meta, "\n".join(lines[close + 1:])


def section_body(body, heading):
    """Text under '## <heading>' up to the next '## ', or None if absent.

    A '## <heading>' or '## ' line inside a fenced code block (``` or ~~~)
    does not count as a boundary. The returned text is sliced from the
    original body, so any fences nested inside the matched section are
    preserved verbatim.
    """
    mask = _mask_fences(body)
    match = re.search(rf"^##\s+{re.escape(heading)}\s*$", mask, re.M)
    if not match:
        return None
    rest_mask = mask[match.end():]
    nxt = re.search(r"^##\s+", rest_mask, re.M)
    end = match.end() + (nxt.start() if nxt else len(rest_mask))
    return body[match.end():end]


def _pillar_dimensions(body):
    """Return (dimensions, malformed_dimensions) for the '## Pillar
    Dimensions' section — see parse_pack's docstring for the contract.
    Both regexes run against a fence-masked copy of the section so example
    bullets shown inside a fence aren't parsed as real dimensions."""
    section = section_body(body, "Pillar Dimensions")
    if section is None:
        return [], []
    masked = _mask_fences(section)
    return DIMENSION_RE.findall(masked), DIMENSION_LOOSE_RE.findall(masked)
