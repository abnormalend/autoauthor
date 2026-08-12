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

# A fenced block, backtick or tilde, 3 or more of the same character,
# opened and closed by matching markers, with up to 3 spaces of leading
# indent (CommonMark allows this — e.g. a fence indented under a bullet
# in '## Artifacts'). Used to blank fenced regions before structural
# matching so a pack author showing example syntax in a fence can't be
# mistaken for a real heading or dimension line. The closing marker must
# match the opening marker's exact character count via backreference —
# CommonMark itself only requires the closer be at least as long as the
# opener, so this is a deliberate simplification. It fails safe (an
# under-matched fence is simply not masked) rather than over-masking, and
# being strict is exactly what lets a doc nest a short fence inside a
# longer outer one — e.g. TEMPLATE.md wraps a 3-backtick example fence
# inside its own longer outer fence — without either marker being
# mistaken for closing the other. An unclosed fence simply doesn't match
# and masks nothing — an acceptable, safe failure.
FENCE_RE = re.compile(r"^ {0,3}(?P<f>```+|~~~+).*?^ {0,3}(?P=f)[ \t]*$",
                      re.M | re.S)

# '- <key> — <criteria>'  (em dash, not hyphen)
DIMENSION_RE = re.compile(r"^-\s+([a-z][a-z0-9_]*)\s+—", re.M)
# Same shape but with a hyphen or en dash where an em dash belongs — the
# typo autocorrect produces. Never matches a line DIMENSION_RE also matches,
# since the two require different characters in the same position.
DIMENSION_LOOSE_RE = re.compile(r"^-\s+([a-z][a-z0-9_]*)\s+[–-]", re.M)
SECTION_RE = re.compile(r"^##\s+(.+?)\s*$", re.M)


class PackError(Exception):
    """Malformed pack. The message is user-facing."""


def _mask_fences(text):
    """Same-length copy of text with fenced blocks blanked to spaces
    (newlines preserved), so structural regexes skip fenced content while
    offsets into the mask still index the corresponding original text.

    Called more than once on overlapping text (once on a whole body, again
    on a slice of it in _pillar_dimensions) — that's safe because
    section_body locates its slice boundaries in an already-masked copy,
    so a slice can never begin or end in the middle of a fenced region.
    Re-masking a slice therefore always sees the same complete fences the
    first pass saw, never a partial one that could be mismatched."""
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


def validate_pack(pack, known_names=None):
    """Validate a parsed pack.

    Returns a list of human-readable error strings; empty means valid.
    known_names, when given, is the set of pack names that exist, used to
    check conflicts_with references.
    """
    errors = []
    meta = pack["meta"]
    path = pack["path"]
    sections = set(pack["sections"])

    name = meta.get("name")
    if not isinstance(name, str) or not name:
        errors.append("frontmatter 'name' must be a non-empty string")
    elif name != path.stem:
        errors.append(
            f"'name' is {name!r} but the filename stem is {path.stem!r}")

    if not isinstance(meta.get("label"), str) or not meta.get("label"):
        errors.append("frontmatter 'label' must be a non-empty string")

    role = meta.get("role")
    if not isinstance(role, list) or not role:
        errors.append("frontmatter 'role' must be a non-empty list")
        role = []
    else:
        unknown = [r for r in role if r not in ROLES]
        if unknown:
            errors.append(
                f"unknown role(s) {unknown}; valid roles are {sorted(ROLES)}")

    scoring = any(r in ("primary", "secondary") for r in role)
    is_primary = "primary" in role
    modifier_only = set(role) == {"modifier"}

    if scoring:
        errors.extend(_validate_weights(meta.get("weights")))

    if is_primary:
        if not meta.get("pillar_label"):
            errors.append("'pillar_label' is required for primary packs")
        for required in ("Framing", "Pillar Dimensions"):
            if required not in sections:
                errors.append(
                    f"primary pack must have a '## {required}' section")

    if modifier_only:
        for field in PRIMARY_ONLY_FIELDS:
            if field in meta:
                errors.append(f"modifier pack must not declare {field!r}")
        if "Pillar Dimensions" in sections:
            errors.append(
                "modifier pack must not have a '## Pillar Dimensions' section")

    if scoring:
        errors.extend(_validate_dimensions(pack["dimensions"],
                                           pack["malformed_dimensions"]))

    conflicts = meta.get("conflicts_with", [])
    if not isinstance(conflicts, list):
        errors.append("'conflicts_with' must be a list")
    elif known_names is not None:
        unknown = [n for n in conflicts if n not in known_names]
        if unknown:
            errors.append(f"'conflicts_with' names unknown pack(s): {unknown}")

    errors.extend(_validate_shape(meta.get("shape")))

    artifacts = meta.get("artifacts") or []
    if not isinstance(artifacts, list):
        errors.append("'artifacts' must be a list")
    else:
        for artifact in artifacts:
            if artifact in CORE_PROJECT_FILES:
                errors.append(
                    f"artifact {artifact!r} collides with a core project file")

    return errors


def _validate_weights(weights):
    if not isinstance(weights, dict):
        return ["'weights' is required for primary and secondary packs"]
    missing = [k for k in WEIGHT_KEYS if k not in weights]
    if missing:
        return [f"'weights' missing key(s): {missing}"]
    if not all(isinstance(weights[k], int) for k in WEIGHT_KEYS):
        return ["'weights' values must be integers"]
    total = sum(weights[k] for k in WEIGHT_KEYS)
    if total != 100:
        return [f"'weights' sum to {total}, must sum to 100"]
    return []


def _validate_dimensions(dimensions, malformed_dimensions=()):
    errors = []
    if malformed_dimensions:
        errors.append(
            f"pillar dimension(s) {sorted(malformed_dimensions)} use a "
            "hyphen or en dash; an em dash (—) is required")
    if not 3 <= len(dimensions) <= 6:
        errors.append(
            f"'## Pillar Dimensions' has {len(dimensions)} dimension(s); "
            "need 3-6, and each bullet must read '- <key> — <criteria>' "
            "with an em dash")
    clash = sorted(set(dimensions) & RESERVED_DIMENSIONS)
    if clash:
        errors.append(
            f"pillar dimension(s) {clash} collide with reserved base dimensions")
    dupes = sorted({d for d in dimensions if dimensions.count(d) > 1})
    if dupes:
        errors.append(f"duplicate pillar dimension key(s): {dupes}")
    return errors


def _validate_shape(shape):
    if shape is None:
        return []
    if not isinstance(shape, dict):
        return ["'shape' must be a JSON object"]
    errors = []
    for key in ("chapters", "words"):
        rng = shape.get(key)
        if rng is None:
            continue
        if (not isinstance(rng, list) or len(rng) != 2
                or not all(isinstance(v, int) for v in rng)):
            errors.append(f"shape.{key} must be a two-integer range")
        elif rng[0] > rng[1]:
            errors.append(f"shape.{key} range {rng} is not ordered low..high")
    return errors
