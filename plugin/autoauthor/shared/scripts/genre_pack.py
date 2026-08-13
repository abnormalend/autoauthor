"""Genre pack parsing and validation. Library module — no CLI.

A genre pack is a markdown file whose first block is JSON frontmatter
delimited by lines of exactly '---', followed by '## ' prose sections.

Frontmatter is JSON rather than YAML because the plugin's scripts are
stdlib-only and Python ships no YAML parser.
"""
import json
import re
from pathlib import Path

import gate_solver

ROLES = {"primary", "secondary", "modifier"}

# The roles that make a pack contribute to scoring (weights, pillar
# dimensions). "modifier" is deliberately excluded — it's an orthogonal
# axis, never a scorer.
SCORING_ROLES = {"primary", "secondary"}

# Dimensions the base rubric already scores. A pack's pillar dimensions may
# not collide with these — that is what stops a literary pack from
# double-counting prose against the base craft category.
#
# Source of truth: plugin/autoauthor/shared/rubrics/base-dimensions.md.
# Mirrored here rather than read from it, because this is a module constant
# used during validation and a validator that does file I/O to answer a
# name-collision question fails in a way nobody expects. The mirror is
# pinned by test_base_dimensions.py, which fails if the two ever disagree.
# A form pack may DROP any of these for its length; they stay reserved
# either way, since a genre reusing a dropped key would still collide the
# moment a longer form loaded.
RESERVED_DIMENSIONS = {
    "character_depth", "character_distinctiveness", "character_secrets",
    "outline_completeness", "foreshadowing_balance",
    "internal_consistency", "voice_clarity", "canon_coverage",
}

WEIGHT_KEYS = ("pillar", "character", "structure", "craft")

# Content intensity axes, each ordered least to most intense.
#
# The order is load-bearing, not decorative: resolve_genre.py clamps a stack
# to the most restrictive level any loaded pack declares, so a `ya` modifier
# over a `romance` primary yields the ya level rather than an error. That is
# only possible because these are scales rather than free strings.
#
# A declared level is a promise checked in BOTH directions — a book that
# promises `explicit` and fades to black has broken its contract exactly as
# one promising `closed-door` and delivering explicit has. That is why the
# vocabulary is closed: "closed-door" and "fade to black" mean the same
# thing, and two packs wording it differently used to read as a genuine
# disagreement and hard-fail the resolve.
CONTENT_AXES = {
    "heat": ("none", "closed-door", "warm", "steamy", "explicit"),
    "violence": ("none", "off-page", "moderate", "graphic"),
    "language": ("none", "mild", "strong", "unrestricted"),
}

# Fields only a primary may declare. A modifier that sets these is trying to
# own structure it is not allowed to own.
PRIMARY_ONLY_FIELDS = ("weights", "pillar_label", "beat_system", "shape")

# Filenames the core autoauthor pipeline (foundation, draft,
# revise, ...) writes into every project directory — mirrored here,
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

# '- <key> [cap N] — <criteria>'  (em dash, not hyphen; the cap optional)
#
# The cap is the floor the criteria can force this dimension down to, and it
# exists as data rather than only as prose because gate_solver.py has to
# read it. A pack's gate is arithmetic over its caps, and a cap written only
# as "score 6 max" halfway through a paragraph is not arithmetic anyone can
# check — which is how two packs shipped with gates their own dimensions
# could not reach.
DIMENSION_RE = re.compile(
    r"^-\s+([a-z][a-z0-9_]*)(?:\s+\[cap\s+(\d+)\])?\s+—", re.M)
# Same shape but with a hyphen or en dash where an em dash belongs — the
# typo autocorrect produces. Never matches a line DIMENSION_RE also matches,
# since the two require different characters in the same position.
DIMENSION_LOOSE_RE = re.compile(
    r"^-\s+([a-z][a-z0-9_]*)(?:\s+\[cap\s+(\d+)\])?\s+[–-]", re.M)

# The house phrasings for a cap in criteria prose. Closed on purpose: the
# declared `[cap N]` is checked against what the prose actually says, and
# that check is only possible if there is a fixed set of ways to say it.
# An author who invents a phrasing gets an error naming these.
#
# Each alternative requires its words adjacent, which is also what keeps
# 'a breach caps `overall_score` at 6' out — several packs say exactly that
# inside a dimension's criteria while cross-referencing their Genre
# Contract, and it is a statement about the weighted mean, not about the
# dimension. Adjacency is doing that work, so there is no separate
# exclusion list to keep in step.
PROSE_CAP_RE = re.compile(
    r"\bscores?\s+(\d+)\s+max\b"
    r"|\bcaps?\s+at\s+(\d+)\b"
    r"|\bscore\s+no\s+(?:higher|more)\s+than\s+(\d+)\b", re.I)
SECTION_RE = re.compile(r"^##\s+(.+?)\s*$", re.M)

# Length bands, and the section a genre pack writes its length-scoped
# criteria under. `extended` has no section: a pack's ordinary criteria ARE
# its extended-length criteria, which is what let fifteen packs stay
# untouched while the form axis was built.
#
# Fallback runs intermediate -> compressed -> none, because a pack that has
# thought about five thousand words has thought about most of what forty
# thousand needs, while the reverse is not true.
BANDS = ("compressed", "intermediate", "extended")
BAND_SECTIONS = {
    "compressed": "At Compressed Length",
    "intermediate": "At Intermediate Length",
}
BAND_FALLBACK = {"intermediate": ("intermediate", "compressed"),
                 "compressed": ("compressed",),
                 "extended": ()}

# A band bullet saying the dimension does not apply at this length. The
# dimension leaves the pillar entirely — and therefore leaves the divisor
# `pillar_score` is a mean over, which is why the cap arithmetic has to be
# recomputed per band rather than assumed from the default.
NOT_SCORED_RE = re.compile(r"^\s*not scored at this band\b", re.I)


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
      'caps'                — {dimension: N} from the '[cap N]' each bullet
                               declares; dimensions declaring none are
                               absent rather than present with a null
      'prose_caps'          — {dimension: N} for the LOWEST cap the same
                               bullet's criteria state in words. Kept
                               separate from 'caps' so the validator can
                               check the declaration against the prose the
                               judge actually reads, which is the only
                               thing stopping the two from drifting apart
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
    dimensions, malformed, caps, prose_caps = _pillar_dimensions(body)
    return {
        "meta": meta,
        "sections": SECTION_RE.findall(_mask_fences(body)),
        "dimensions": dimensions,
        "malformed_dimensions": malformed,
        "caps": caps,
        "prose_caps": prose_caps,
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
    """Return (dimensions, malformed_dimensions, caps, prose_caps) for the
    '## Pillar Dimensions' section — see parse_pack's docstring for the
    contract. Every regex runs against a fence-masked copy of the section
    so example bullets shown inside a fence aren't parsed as real
    dimensions."""
    section = section_body(body, "Pillar Dimensions")
    if section is None:
        return [], [], {}, {}
    return dimension_bullets(section)


def dimension_bullets(section):
    """Parse a block of dimension bullets into
    (dimensions, malformed, caps, prose_caps).

    Three places use this shape and must agree on what it means: a genre
    pack's '## Pillar Dimensions', the base rubric's per-category sections,
    and a form pack's '## Base Dimensions'. They agree because they call
    this.
    """
    masked = _mask_fences(section)
    dimensions, caps, prose_caps = [], {}, {}
    matches = list(DIMENSION_RE.finditer(masked))
    for i, match in enumerate(matches):
        key = match.group(1)
        dimensions.append(key)
        if match.group(2) is not None:
            caps[key] = int(match.group(2))
        # A dimension's criteria run to the next dimension bullet, so
        # indented sub-bullets and continuation lines belong to the
        # dimension above them — which is how the packs are written.
        end = matches[i + 1].start() if i + 1 < len(matches) else len(masked)
        stated = _prose_caps(masked[match.end():end])
        if stated:
            prose_caps[key] = min(stated)
    return (dimensions, [m.group(1) for m in DIMENSION_LOOSE_RE.finditer(masked)],
            caps, prose_caps)


def _prose_caps(criteria):
    """Every score cap the criteria text states, as integers.

    Tiered criteria state more than one; the dimension's cap is the lowest,
    because that is the floor the criteria can force.
    """
    return [int(g) for match in PROSE_CAP_RE.finditer(criteria)
            for g in match.groups() if g]


def band_criteria(pack, band):
    """What this pack scores at `band`, after fallback.

    Returns (dimensions, caps, replaced, dropped, source_band):

      dimensions  — the pillar dimensions still scored, in declaration
                    order, with anything the band drops removed
      caps        — {dimension: N}, the band's restated cap where it
                    restates one and the default cap otherwise
      replaced    — dimensions whose criteria the band section rewrites
      dropped     — dimensions the band section says are not scored here
      source_band — which section actually supplied it, after the
                    intermediate -> compressed fallback, or None

    A band section that names no dimension a pack declares is an authoring
    error rather than a no-op, and validate_pack reports it — silently
    ignoring the section would leave a pack looking length-aware while
    scoring a short story against novel criteria.
    """
    for candidate in BAND_FALLBACK.get(band, ()):
        section = section_body(pack["body"], BAND_SECTIONS[candidate])
        if section is not None:
            return (*_apply_band(pack, section), candidate)
    return (list(pack["dimensions"]), dict(pack["caps"]), [], [], None)


def _apply_band(pack, section):
    keys, _, band_caps, _ = dimension_bullets(section)
    masked = _mask_fences(section)
    matches = list(DIMENSION_RE.finditer(masked))

    dropped = []
    for i, match in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(masked)
        if NOT_SCORED_RE.match(masked[match.end():end].lstrip("— ").lstrip()):
            dropped.append(match.group(1))

    replaced = [k for k in keys if k not in dropped]
    dimensions = [d for d in pack["dimensions"] if d not in dropped]
    caps = {d: band_caps.get(d, pack["caps"].get(d))
            for d in dimensions
            if band_caps.get(d, pack["caps"].get(d)) is not None}
    return dimensions, caps, replaced, dropped


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

    errors.extend(_validate_content_register(meta.get("content_register")))

    errors.extend(_validate_shape(meta.get("shape"), required=is_primary))

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
        errors.extend(_validate_caps(pack["dimensions"], pack["caps"],
                                     pack["prose_caps"], is_primary))
        errors.extend(_validate_bands(pack, is_primary))

    if modifier_only:
        for band, heading in BAND_SECTIONS.items():
            if heading in sections:
                errors.append(
                    f"modifier pack must not have a '## {heading}' section; "
                    "a modifier declares no pillar dimensions, so it has "
                    "none to rescope at a length")

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


def _validate_caps(dimensions, caps, prose_caps, is_primary):
    """Check the declared '[cap N]' values against the criteria and the gate.

    Three failures, in the order an author fixes them:

    1. A cap the criteria state but the bullet does not declare, or the
       reverse, or the two disagreeing. The declaration is what the
       arithmetic reads and the prose is what the judge reads, so a
       divergence means the gate is being computed against a pack that no
       longer exists.
    2. A cap outside 1-9. Ten is not a cap and zero is not a score.
    3. A design whose own caps put the pipeline's gate out of reach. Only
       checked for primaries: `pillar_score` averages the primary's
       dimensions alone, so a secondary's caps never form a gate.
    """
    errors = _cap_agreement(dimensions, caps, prose_caps)

    if is_primary and not errors:
        # Suppressed while the caps themselves are wrong: arithmetic over a
        # cap list that is known to be inaccurate would send the author to
        # fix the dimension count when the real fault is a typo.
        problem = gate_solver.unreachable(len(dimensions),
                                          sorted(caps.values()))
        if problem:
            errors.append(problem)

    return errors


def _cap_agreement(dimensions, caps, prose_caps, where=""):
    """The declared `[cap N]` and the criteria must say the same number.

    The declaration is what tooling reads and the criteria are what the
    judge reads, so a divergence means the gate is computed against a pack
    that no longer exists. Shared by the default criteria and by every
    band section, which restate caps for their own reduced dimension set.
    """
    errors = []
    for key in dimensions:
        declared, stated = caps.get(key), prose_caps.get(key)
        label = f"dimension {key!r}{where}"
        if declared is not None and not (
                gate_solver.MIN_CAP <= declared <= gate_solver.MAX_CAP):
            errors.append(
                f"{label} declares [cap {declared}]; a cap must be "
                f"{gate_solver.MIN_CAP}-{gate_solver.MAX_CAP} "
                "(10 caps nothing, and 0 is not a score)")
        if declared is None and stated is not None:
            errors.append(
                f"{label} states a cap of {stated} in its criteria but "
                f"declares none; write '- {key} [cap {stated}] — ...' so the "
                "gate arithmetic can see it")
        elif declared is not None and stated is None:
            errors.append(
                f"{label} declares [cap {declared}] but its criteria never "
                "state it; a judge reads the criteria, so say it there too — "
                "'score N max', 'caps at N', or 'score no higher than N'")
        elif (declared is not None and stated is not None
                and declared != stated):
            errors.append(
                f"{label} declares [cap {declared}] but its criteria can "
                f"force it to {stated}; the declared cap is the LOWEST tier "
                "the criteria can reach")
    return errors


def _validate_bands(pack, is_primary):
    """Check each length-scoped section a pack declares.

    Dropping a dimension at a band changes N, and every pack's cap
    arithmetic is calibrated against its own N — so a band that removes
    two of five dimensions is a different design with a different ceiling,
    and has to be checked as one. This is the check the form spec calls
    the single highest-value addition, because it is the defect class that
    has already bitten twice.
    """
    errors = []
    declared = set(pack["dimensions"])

    for band, heading in BAND_SECTIONS.items():
        section = section_body(pack["body"], heading)
        if section is None:
            continue
        keys, malformed, band_caps, band_prose = dimension_bullets(section)
        where = f" in '## {heading}'"

        if malformed:
            errors.append(
                f"dimension(s) {format_names(sorted(malformed))}{where} use a "
                "hyphen or en dash; an em dash (—) is required")
        unknown = sorted(set(keys) - declared)
        if unknown:
            errors.append(
                f"'## {heading}' names {format_names(unknown)}, which this "
                "pack does not declare under '## Pillar Dimensions'; a band "
                "section rewrites existing criteria, it cannot introduce a "
                "dimension")
        if not keys:
            errors.append(
                f"'## {heading}' names no dimension; either say what changes "
                "at this length or delete the section, because an empty one "
                "leaves the pack looking length-aware while scoring a short "
                "work against criteria written for a long one")
            continue

        dimensions, caps, _, dropped, _ = band_criteria(pack, band)
        # 'not scored at this band' bullets carry no criteria and so no cap.
        scored_here = [k for k in keys if k not in dropped]
        errors.extend(_cap_agreement(scored_here,
                                     {k: band_caps.get(k) for k in scored_here
                                      if band_caps.get(k) is not None},
                                     band_prose, where))

        if not dimensions:
            errors.append(
                f"'## {heading}' drops every dimension, leaving no pillar to "
                "score and `pillar_score` a mean over nothing")
            continue

        if is_primary and not errors:
            ceiling = gate_solver.max_gate(len(dimensions),
                                           sorted(caps.values()))
            if ceiling is None:
                errors.append(
                    f"at {band} length this pack scores {len(dimensions)} "
                    f"dimension(s) with {gate_solver.format_caps(sorted(caps.values()))}, "
                    "and no gate between 4.0 and 9.9 is reachable. Dropping a "
                    "dimension shrinks the divisor the caps are calibrated "
                    "against — restate the caps for the reduced set, or drop "
                    "one fewer")
    return errors


def _validate_content_register(register):
    """Validate a pack's declared content intensity levels.

    The vocabulary is closed on purpose. An open one lets two packs write
    the same level differently ("closed-door" vs "fade to black"), which
    reads as a disagreement to the resolver and cannot be ordered, so a
    stack cannot be clamped to its most restrictive level.
    """
    if register is None:
        return []
    if not isinstance(register, dict):
        return ["'content_register' must be a JSON object mapping an axis "
                f"to a level; axes are {format_names(sorted(CONTENT_AXES))}"]
    errors = []
    for axis, level in register.items():
        if axis not in CONTENT_AXES:
            errors.append(
                f"unknown content_register axis {axis!r}; valid axes are "
                f"{format_names(sorted(CONTENT_AXES))}")
            continue
        if level not in CONTENT_AXES[axis]:
            errors.append(
                f"content_register.{axis} is {level!r}; valid levels are "
                f"{format_names(CONTENT_AXES[axis])} (least to most intense)")
    return errors


def _validate_shape(shape, required=False):
    """Validate a pack's `shape`.

    Required on primaries: layer-guides.md tells the outliner to take its
    word targets from `shape`, and drafting-rules.md takes its per-chapter
    target from `shape.chapter_words`. A primary without `shape` leaves
    both instructions pointing at nothing, so this fails at authoring time
    rather than mid-draft.

    Two things moved here with the form axis:

    `words` is keyed by BAND. Length is the form's to own, but a genre
    still has a length within a form — a romantasy runs 110,000-140,000
    where a cozy runs 75,000, and collapsing every pack onto one form
    default would lose a real genre fact. A band a pack says nothing about
    takes the form's own range.

    `chapters` is DERIVED, from the effective target over `chapter_words`,
    and declaring it is an error. Several packs' declared chapter ranges
    only partially intersected their own word ranges — `mystery` spanned
    70,400-83,200 against a declared 80,000-95,000, so most of its chapter
    range could not reach its own word floor. Deriving the count makes that
    class of inconsistency unrepresentable rather than merely fixed.
    """
    if shape is None:
        if required:
            return ["frontmatter 'shape' is required for primary packs "
                    "(words, chapter_words, pov_default) — the outline and "
                    "drafting steps read their targets from it"]
        return []
    if not isinstance(shape, dict):
        return ["'shape' must be a JSON object"]
    errors = []
    if required:
        for key in ("words", "chapter_words", "pov_default"):
            if key not in shape:
                errors.append(f"shape.{key} is required for primary packs")
    if "chapters" in shape:
        errors.append(
            "shape.chapters is derived from the effective word target and "
            "shape.chapter_words — remove it; a declared count can "
            "contradict the word range, and several packs' did")
    if "chapter_words" in shape and not (
            isinstance(shape["chapter_words"], int)
            and not isinstance(shape["chapter_words"], bool)
            and shape["chapter_words"] > 0):
        errors.append("shape.chapter_words must be a positive integer")
    if "pov_default" in shape and not (
            isinstance(shape.get("pov_default"), str)
            and shape["pov_default"].strip()):
        errors.append("shape.pov_default must be a non-empty string")
    errors.extend(_validate_band_words(shape.get("words")))
    return errors


def _validate_band_words(words):
    if words is None:
        return []
    if not isinstance(words, dict):
        return ["shape.words must be a JSON object keyed by band "
                f"({format_names(BANDS)}), e.g. "
                '{"extended": [80000, 95000]} — length is band-scoped now, '
                "and a bare range cannot say which length it describes"]
    errors = []
    unknown = sorted(set(words) - set(BANDS))
    if unknown:
        errors.append(
            f"shape.words has unknown band(s) {format_names(unknown)}; "
            f"valid bands: {format_names(BANDS)}")
    if not words:
        errors.append("shape.words declares no band; give at least one")
    for band, rng in words.items():
        if (not isinstance(rng, list) or len(rng) != 2
                or not all(isinstance(v, int) and not isinstance(v, bool)
                           for v in rng)):
            errors.append(f"shape.words.{band} must be a two-integer range")
        elif rng[0] > rng[1]:
            errors.append(
                f"shape.words.{band} range {rng} is not ordered low..high")
        elif rng[0] <= 0:
            errors.append(f"shape.words.{band} floor must be positive")
    return errors
