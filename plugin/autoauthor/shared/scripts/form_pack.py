"""Form pack parsing and validation. Library module — no CLI.

A form pack says how long one complete work is, and what apparatus that
length earns. Same file format as a genre pack — JSON frontmatter, `## `
prose sections — and parsed by the same code, because there was no reason
to invent a second one.

The distinction that matters, and the one this whole axis exists to keep
straight: a form is a matter of SCALE. It changes which base dimensions
apply, how the genre's criteria are read, which foundation layers get
built, and where the gate sits. It does not change the phase graph. How
many complete works there are and how they relate — standalone,
collection, series — is the STRUCTURE axis, which changes the state schema
and the phases themselves and therefore cannot be a pack at all.

Today only `novel` ships, carrying the values the pipeline already used.
That is deliberate: the machinery lands first and is proved inert, and the
lengths that actually change behaviour arrive after.
"""
import re

from genre_pack import (NAME_RE, RESERVED_DIMENSIONS, format_names,
                        parse_pack)

# Read by the genre packs to pick which of their band sections applies.
# `extended` is the implicit default: a genre pack that declares no band
# section behaves exactly as it does today, which is what lets fifteen
# packs stay untouched while the axis is built.
BANDS = ("compressed", "intermediate", "extended")

# The foundation layers a form may ask for, keyed to the sections of
# skills/foundation/references/layer-guides.md that define them. A form
# names a subset; a short story has no world bible and no foreshadowing
# ledger. Mirrored rather than derived, and pinned by a test, because
# layer-guides.md is prose for a model to read and not a data file.
KNOWN_LAYERS = {
    "voice": "voice discovery",
    "world": "world.md",
    "characters": "characters.md",
    "mystery": "MYSTERY.md",
    "outline": "outline.md part 1",
    "foreshadowing": "outline.md part 2 (foreshadowing ledger)",
    "canon": "canon.md",
}

GATE_KEYS = ("overall", "pillar")

# The template's filename stem, matching genre_pack's convention so a
# forms/ directory can carry an authoring guide without it resolving as a
# form.
TEMPLATE_STEM = "TEMPLATE"


def parse_form(path):
    """Parse a form pack. Same shape as genre_pack.parse_pack.

    Form packs declare no pillar dimensions, so the 'dimensions', 'caps'
    and 'prose_caps' keys come back empty and validate_form rejects a form
    that tries to declare them — pillar dimensions belong to a genre.
    """
    return parse_pack(path)


def validate_form(form):
    """Validate a parsed form pack. Returns human-readable error strings."""
    errors = []
    meta = form["meta"]
    path = form["path"]
    sections = set(form["sections"])

    name = meta.get("name")
    if not isinstance(name, str) or not name:
        errors.append("frontmatter 'name' must be a non-empty string")
    else:
        if not NAME_RE.fullmatch(name):
            errors.append(
                f"frontmatter 'name' is {name!r}; a form name must be "
                "lowercase letters, digits, and hyphens only (e.g. "
                "'short-story')")
        if name != path.stem:
            errors.append(
                f"frontmatter 'name' is {name!r} but the filename stem is "
                f"{path.stem!r}")

    if not isinstance(meta.get("label"), str) or not meta.get("label"):
        errors.append("frontmatter 'label' must be a non-empty string")

    band = meta.get("band")
    if band not in BANDS:
        errors.append(
            f"frontmatter 'band' is {band!r}; must be one of "
            f"{format_names(BANDS)} — this is what a genre pack's band "
            "sections key off")

    errors.extend(_validate_words(meta.get("words"), meta.get("target_words")))
    errors.extend(_validate_gate(meta.get("gate")))
    errors.extend(_validate_layers(meta.get("layers")))
    errors.extend(_validate_base_dimensions(meta.get("base_dimensions")))

    if "role" in meta:
        errors.append(
            "a form pack must not declare 'role' — form is its own axis, "
            "not a primary/secondary/modifier slot")

    if form["dimensions"] or "Pillar Dimensions" in sections:
        errors.append(
            "a form pack must not declare pillar dimensions; those belong "
            "to a genre pack, and a form changes how they are READ, not "
            "what they are")

    for required in ("Framing", "Form Contract"):
        if required not in sections:
            errors.append(f"form pack must have a '## {required}' section")

    return errors


def _validate_words(words, target):
    """`words` is the form's definition, `target_words` the value the
    outline aims at. Both live here rather than on a genre pack because
    length is what a form IS."""
    errors = []
    if (not isinstance(words, list) or len(words) != 2
            or not all(isinstance(v, int) and not isinstance(v, bool)
                       for v in words)):
        return ["frontmatter 'words' must be a two-integer range"]
    if words[0] <= 0:
        errors.append("'words' floor must be positive")
    if words[0] > words[1]:
        errors.append(f"'words' range {words} is not ordered low..high")
    if not isinstance(target, int) or isinstance(target, bool):
        errors.append("frontmatter 'target_words' must be an integer")
    elif not words[0] <= target <= words[1]:
        errors.append(
            f"'target_words' {target} is outside this form's own 'words' "
            f"range {words}")
    return errors


def _validate_gate(gate):
    """The bars the foundation loop exits on.

    A form owns these because they are length economics: the gate is the
    highest bar in the pipeline on the reasoning that a weak plan costs
    more later, and at 5,000 words a weak plan costs an afternoon.
    """
    if gate is None:
        return ["frontmatter 'gate' is required (overall and pillar)"]
    if not isinstance(gate, dict):
        return ["frontmatter 'gate' must be a JSON object with "
                f"{format_names(GATE_KEYS)}"]
    errors = []
    for key in GATE_KEYS:
        if key not in gate:
            errors.append(f"'gate' missing key {key!r}")
            continue
        value = gate[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            errors.append(f"gate.{key} must be a number")
        elif not 0 <= value <= 10:
            errors.append(f"gate.{key} is {value}; must be between 0 and 10")
    return errors


def _validate_layers(layers):
    if not isinstance(layers, list) or not layers:
        return ["frontmatter 'layers' must be a non-empty list of layer "
                f"names; known layers: {format_names(sorted(KNOWN_LAYERS))}"]
    errors = []
    unknown = [layer for layer in layers if layer not in KNOWN_LAYERS]
    if unknown:
        errors.append(
            f"'layers' names unknown layer(s) {format_names(unknown)}; "
            f"known layers: {format_names(sorted(KNOWN_LAYERS))}")
    dupes = sorted({layer for layer in layers if layers.count(layer) > 1})
    if dupes:
        errors.append(f"'layers' repeats {format_names(dupes)}")
    return errors


def _validate_base_dimensions(base):
    """Which base dimensions this length applies.

    `drop` is the point of the field: `foreshadowing_balance` scores a
    ledger a short story has no room to keep, and scoring it anyway
    penalizes the story for being correctly what it is.
    """
    if base is None:
        return []
    if not isinstance(base, dict):
        return ["'base_dimensions' must be a JSON object with 'drop' and "
                "'add' lists"]
    errors = []
    unknown_keys = sorted(set(base) - {"drop", "add"})
    if unknown_keys:
        errors.append(
            f"'base_dimensions' has unknown key(s) {format_names(unknown_keys)}; "
            "only 'drop' and 'add' are read")
    for key in ("drop", "add"):
        value = base.get(key, [])
        if not isinstance(value, list) or not all(
                isinstance(v, str) for v in value):
            errors.append(f"'base_dimensions.{key}' must be a list of strings")
            continue
        if key == "drop":
            unknown = [d for d in value if d not in RESERVED_DIMENSIONS]
            if unknown:
                errors.append(
                    f"'base_dimensions.drop' names {format_names(unknown)}, "
                    "which are not base dimensions; droppable: "
                    f"{format_names(sorted(RESERVED_DIMENSIONS))}")
        else:
            clash = sorted(set(value) & RESERVED_DIMENSIONS)
            if clash:
                errors.append(
                    f"'base_dimensions.add' names {format_names(clash)}, "
                    "which already exist as base dimensions")
            malformed = [d for d in value
                         if not re.fullmatch(r"[a-z][a-z0-9_]*", d)]
            if malformed:
                errors.append(
                    f"'base_dimensions.add' key(s) {format_names(malformed)} "
                    "must be lowercase identifiers, like the dimensions they "
                    "sit beside")
    return errors


def ranges_overlap(a, b):
    """Do two inclusive [low, high] ranges share any value?

    Overlap, not containment, is the right relation between a form's word
    band and a genre's declared range. A genre saying it runs long is not
    a contradiction of the form — it is a statement about where in the
    form it sits, and the part that spills past the form's ceiling is what
    a longer form would be for. Containment would reject a genre that
    legitimately straddles the boundary; overlap still catches the real
    error, which is a genre whose range lies wholly outside the form.
    """
    return a[0] <= b[1] and b[0] <= a[1]
