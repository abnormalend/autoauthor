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

# The roles that make a pack contribute to scoring (weights, pillar
# dimensions). "modifier" is deliberately excluded — it's an orthogonal
# axis, never a scorer.
SCORING_ROLES = {"primary", "secondary"}

# Dimensions the base rubric already scores. A pack's pillar dimensions may
# not collide with these — that is what stops a literary pack from
# double-counting prose against the base craft category.
# Source of truth: plugin/autonovel/shared/rubrics/foundation.md
RESERVED_DIMENSIONS = {
    "character_depth", "character_distinctiveness", "character_secrets",
    "outline_completeness", "foreshadowing_balance",
    "internal_consistency", "voice_clarity", "canon_coverage",
}

WEIGHT_KEYS = ("pillar", "character", "structure", "craft")

# Fields only a primary may declare. A modifier that sets these is trying to
# own structure it is not allowed to own.
PRIMARY_ONLY_FIELDS = ("weights", "pillar_label", "beat_system", "shape")

# Filenames the core autonovel pipeline (novel-foundation, novel-draft,
# novel-revise, ...) writes into every project directory — mirrored here,
# not read from one canonical list, because no single file enumerates them.
# A pack's 'artifacts' list must not collide with these.
CORE_PROJECT_FILES = {
    "seed.txt", "voice.md", "world.md", "characters.md", "outline.md",
    "canon.md", "MYSTERY.md", "state.json", "results.tsv", "arc_summary.md",
    "manuscript.md", "voice_wells.json", "import_source.md",
}

# The template's filename stem — never a real pack name, so every scan of a
# genres/ directory for pack names excludes it.
TEMPLATE_STEM = "TEMPLATE"

# A pack name is a bare filename stem: lowercase letters, digits, and
# hyphens. resolve_genre.py applies this to the names in state.json before
# they reach a path join (so "../outside" can't escape the genres/
# directory); validate_pack applies the same rule to a pack's own 'name'
# field, so an authoring-time check catches 'Cozy_Mystery' instead of
# letting it validate clean and then fail at resolve time.
NAME_RE = re.compile(r"[a-z0-9][a-z0-9-]*")

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


def pack_names_in(directory):
    """Pack names available in a single genres/ directory: the '.md' file
    stems, minus TEMPLATE_STEM. Callers combining more than one directory
    (project genres/ over the plugin's shared/genres/) union the results
    themselves — this function deliberately knows about only one directory
    at a time, so the different ways CLIs combine directories stay visible
    at the call site instead of being hidden behind a shared helper."""
    return {p.stem for p in Path(directory).glob("*.md")} - {TEMPLATE_STEM}


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


def format_names(seq):
    """Render an iterable of values for an error message: 'craft, pillar'
    instead of the default repr "['craft', 'pillar']". Every element is
    coerced with str() so a stray non-string value — an author guessing at
    a richer schema, e.g. a dict where a name string belongs — still
    renders instead of raising."""
    return ", ".join(str(v) for v in seq)


def validate_pack(pack, known_names=None):
    """Validate a parsed pack.

    Returns a list of human-readable error strings; empty means valid.
    known_names, when given, is the set of pack names that exist, used to
    check conflicts_with references.

    Frontmatter-field errors are collected before section/prose errors, so
    an author working top-to-bottom through the list fixes the JSON block
    first and isn't bounced back to it after starting on the prose.
    """
    errors = []
    meta = pack["meta"]
    path = pack["path"]
    sections = set(pack["sections"])

    # --- frontmatter -----------------------------------------------------

    name = meta.get("name")
    if not isinstance(name, str) or not name:
        errors.append("frontmatter 'name' must be a non-empty string")
    else:
        # Both checks run, not one-or-the-other: 'Cozy_Mystery' in
        # Cozy_Mystery.md matches its stem and is still an illegal name,
        # while a legal name in the wrong file is still a mismatch.
        if not NAME_RE.fullmatch(name):
            errors.append(
                f"frontmatter 'name' is {name!r}; a pack name must be "
                "lowercase letters, digits, and hyphens only, starting "
                "with a letter or digit (e.g. 'cozy-mystery') — rename "
                "the file to match")
        if name != path.stem:
            errors.append(
                f"frontmatter 'name' is {name!r} but the filename stem is "
                f"{path.stem!r}")

    if not isinstance(meta.get("label"), str) or not meta.get("label"):
        errors.append("frontmatter 'label' must be a non-empty string")

    role = meta.get("role")
    if not isinstance(role, list) or not role:
        errors.append("frontmatter 'role' must be a non-empty list")
        role = []
    else:
        # Guard against non-string entries (e.g. an author passing a dict)
        # rather than letting them reach a hash/membership test below.
        unknown = [r for r in role if not isinstance(r, str) or r not in ROLES]
        if unknown:
            errors.append(
                f"frontmatter 'role' has unknown role(s) {format_names(unknown)}; "
                f"valid roles: {format_names(sorted(ROLES))}")

    # role_strs drops any non-string junk (already reported above) before
    # any set() is built from it — set(role) directly would raise on an
    # unhashable element such as a dict.
    role_strs = [r for r in role if isinstance(r, str)]
    scoring = bool(set(role_strs) & SCORING_ROLES)
    is_primary = "primary" in role_strs
    modifier_only = (len(role_strs) == len(role)
                     and set(role_strs) == {"modifier"})

    if scoring:
        errors.extend(_validate_weights(meta.get("weights")))

    if is_primary and not meta.get("pillar_label"):
        errors.append(
            "frontmatter 'pillar_label' is required for primary packs")

    if modifier_only:
        for field in PRIMARY_ONLY_FIELDS:
            if field in meta:
                errors.append(
                    f"modifier pack's frontmatter must not declare {field!r}")

    conflicts = meta.get("conflicts_with", [])
    if not isinstance(conflicts, list):
        errors.append("frontmatter 'conflicts_with' must be a list")
    elif known_names is not None:
        unknown = [n for n in conflicts
                  if not isinstance(n, str) or n not in known_names]
        if unknown:
            errors.append(
                f"frontmatter 'conflicts_with' names unknown pack(s) "
                f"{format_names(unknown)}; known packs: {format_names(sorted(known_names))}")

    errors.extend(_validate_shape(meta.get("shape")))

    # meta.get("artifacts", []) rather than `or []` — an explicit
    # "artifacts": null must fail loudly the same way conflicts_with does,
    # not be silently treated as an empty list.
    artifacts = meta.get("artifacts", [])
    if not isinstance(artifacts, list):
        errors.append("frontmatter 'artifacts' must be a list")
    else:
        # Guard against non-string entries (e.g. an author passing a dict)
        # the same way 'role' and 'conflicts_with' already do, rather than
        # silently skipping them — Task 4's merge() puts 'artifacts'
        # straight into its JSON output, and a dict there would become an
        # attempt to create a file literally named "{'file': 'x.md'}".
        non_string = [a for a in artifacts if not isinstance(a, str)]
        if non_string:
            errors.append(
                f"frontmatter 'artifacts' must be a list of strings; "
                f"non-string element(s): {format_names(non_string)}")
        for artifact in artifacts:
            if isinstance(artifact, str) and artifact in CORE_PROJECT_FILES:
                errors.append(
                    f"artifact {artifact!r} collides with a core project file")

    # --- sections / prose --------------------------------------------------

    if is_primary and "Framing" not in sections:
        errors.append("primary pack must have a '## Framing' section")

    if scoring:
        errors.extend(_validate_dimensions(pack["dimensions"],
                                           pack["malformed_dimensions"],
                                           "Pillar Dimensions" in sections))

    if modifier_only and "Pillar Dimensions" in sections:
        errors.append(
            "modifier pack must not have a '## Pillar Dimensions' section")

    return errors


def _validate_weights(weights):
    if weights is None:
        return ["frontmatter 'weights' is required for primary and "
                "secondary packs"]
    if not isinstance(weights, dict):
        return ["frontmatter 'weights' must be a JSON object mapping "
                "pillar/character/structure/craft to integers"]
    missing = [k for k in WEIGHT_KEYS if k not in weights]
    if missing:
        return [f"'weights' missing key(s): {format_names(missing)}"]
    # isinstance(v, int) alone accepts bool (bool is an int subclass in
    # Python) — a stray "weights": {"pillar": true, ...} must be reported
    # as a type error, not silently summed as 1 and reported as a sum
    # mismatch instead.
    bad = [k for k in WEIGHT_KEYS
           if isinstance(weights[k], bool) or not isinstance(weights[k], int)]
    if bad:
        return [f"'weights' values must be integers; non-integer key(s): "
                f"{format_names(bad)}"]
    total = sum(weights[k] for k in WEIGHT_KEYS)
    if total != 100:
        return [f"'weights' sum to {total}, must sum to 100"]
    return []


def _validate_dimensions(dimensions, malformed_dimensions, has_section):
    """dimensions/malformed_dimensions are parse_pack's lists for a scoring
    pack; has_section says whether a '## Pillar Dimensions' heading exists
    at all — required so a missing section produces exactly one message
    instead of also tripping the (contradictory) dimension-count check."""
    if not has_section:
        return ["add a '## Pillar Dimensions' section with 3-6 bullets, "
                "each reading '- <key> — <criteria>' with an em dash"]

    errors = []
    if malformed_dimensions:
        errors.append(
            f"pillar dimension(s) {format_names(sorted(malformed_dimensions))} "
            "use a hyphen or en dash; an em dash (—) is required")
    # Malformed bullets are still bullets an author sees on screen, so they
    # count toward the range check — otherwise a 3-bullet section with one
    # bad dash reports "has 2 dimension(s); need 3-6" right next to the
    # em-dash message, which contradicts what's visibly there.
    total = len(dimensions) + len(malformed_dimensions)
    if not 3 <= total <= 6:
        errors.append(
            f"'## Pillar Dimensions' has {total} dimension(s); "
            "need 3-6, and each bullet must read '- <key> — <criteria>' "
            "with an em dash")
    clash = sorted(set(dimensions) & RESERVED_DIMENSIONS)
    if clash:
        errors.append(
            f"pillar dimension(s) {format_names(clash)} collide with reserved "
            f"base dimensions; reserved: {format_names(sorted(RESERVED_DIMENSIONS))}")
    dupes = sorted({d for d in dimensions if dimensions.count(d) > 1})
    if dupes:
        errors.append(f"duplicate pillar dimension key(s): {format_names(dupes)}")
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
                or not all(isinstance(v, int) and not isinstance(v, bool)
                           for v in rng)):
            errors.append(f"shape.{key} must be a two-integer range")
        elif rng[0] > rng[1]:
            errors.append(f"shape.{key} range {rng} is not ordered low..high")
    return errors
