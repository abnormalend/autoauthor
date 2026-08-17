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

import base_dimensions
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

# `layers` is what FOUNDATION builds, and only that. Drafting may create
# a document the form never listed, and the first real short-story run did
# exactly that: it wrote a `canon.md` for a form whose layers are voice,
# characters and outline, because facts established on the page have to be
# recorded somewhere and the collection's shared bible has to be fed from
# below. That is correct behaviour, not drift — planning a canon for five
# thousand words is waste, and keeping one while writing them is not.
#
# The project file each layer produces, for `seed` to scaffold only what
# the form actually calls for. A short story that is handed an empty
# `world.md` and an empty `canon.md` has been handed two documents its
# form deliberately does not build — and the foundation rubric now tells
# its judge not to go looking for a file it was not named, so leaving
# them there is at best clutter and at worst a judge marking down a
# five-line template.
#
# `foreshadowing` maps to the same file as `outline`: it is part two of
# that document, not a document of its own.
LAYER_FILES = {
    "voice": ("voice.md",),
    "world": ("world.md",),
    "characters": ("characters.md",),
    "mystery": ("MYSTERY.md",),
    "outline": ("outline.md",),
    "foreshadowing": ("outline.md",),
    "canon": ("canon.md",),
}


def layer_files(layers):
    """The project files a form's layers call for, deduplicated."""
    out = []
    for layer in layers:
        for name in LAYER_FILES.get(layer, ()):
            if name not in out:
                out.append(name)
    return out

GATE_KEYS = ("overall", "pillar")

# How many foundation iterations a form allows before the loop stops
# regardless of the gate, when the form does not declare its own.
DEFAULT_ITERATION_CAP = 15

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
    unit = meta.get("chapter_words")
    if unit is not None and not (isinstance(unit, int)
                                 and not isinstance(unit, bool) and unit > 0):
        errors.append("'chapter_words' must be a positive integer; a form "
                      "declares one only to override the genre's, which a "
                      "compressed form must because its unit is not a "
                      "chapter")
    cap = meta.get("iteration_cap")
    if cap is not None and not (isinstance(cap, int)
                                and not isinstance(cap, bool) and cap > 0):
        errors.append("'iteration_cap' must be a positive integer; it is "
                      "how many foundation iterations this length can "
                      "earn before the plan cannot be much righter than "
                      "the work")
    errors.extend(_validate_base_dimensions(meta.get("base_dimensions"), form))

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


def _validate_base_dimensions(base, form=None):
    """Which base dimensions this length applies.

    `drop` is the point of the field: `foreshadowing_balance` scores a
    ledger a short story has no room to keep, and scoring it anyway
    penalizes the story for being correctly what it is.

    `add` is keyed by CATEGORY rather than being a flat list, because a
    dimension that belongs to no category has no weight and cannot reach
    `overall_score`. The criteria for an added dimension live in this
    form's own '## Base Dimensions' section — frontmatter says which
    category, prose says what it means, exactly as a genre pack works.
    """
    if base is None:
        return []
    if not isinstance(base, dict):
        return ["'base_dimensions' must be a JSON object with a 'drop' list "
                "and an 'add' object keyed by category"]
    errors = []
    unknown_keys = sorted(set(base) - {"drop", "add"})
    if unknown_keys:
        errors.append(
            f"'base_dimensions' has unknown key(s) {format_names(unknown_keys)}; "
            "only 'drop' and 'add' are read")

    drop = base.get("drop", [])
    if not isinstance(drop, list) or not all(isinstance(d, str) for d in drop):
        errors.append("'base_dimensions.drop' must be a list of strings")
    else:
        unknown = [d for d in drop if d not in RESERVED_DIMENSIONS]
        if unknown:
            errors.append(
                f"'base_dimensions.drop' names {format_names(unknown)}, "
                "which are not base dimensions; droppable: "
                f"{format_names(sorted(RESERVED_DIMENSIONS))}")

    add = base.get("add", {})
    if not isinstance(add, dict):
        return errors + [
            "'base_dimensions.add' must be a JSON object keyed by category "
            f"({format_names(base_dimensions.CATEGORIES)}), e.g. "
            '{"structure": ["compression"]} — a dimension in no category '
            "carries no weight"]

    unknown_categories = sorted(set(add) - set(base_dimensions.CATEGORIES))
    if unknown_categories:
        errors.append(
            f"'base_dimensions.add' has unknown categor(ies) "
            f"{format_names(unknown_categories)}; valid: "
            f"{format_names(base_dimensions.CATEGORIES)}")

    added = []
    for category, keys in add.items():
        if not isinstance(keys, list) or not all(
                isinstance(k, str) for k in keys):
            errors.append(
                f"'base_dimensions.add.{category}' must be a list of strings")
            continue
        added.extend(keys)

    clash = sorted(set(added) & RESERVED_DIMENSIONS)
    if clash:
        errors.append(
            f"'base_dimensions.add' names {format_names(clash)}, which "
            "already exist as base dimensions")
    malformed = [k for k in added if not re.fullmatch(r"[a-z][a-z0-9_]*", k)]
    if malformed:
        errors.append(
            f"'base_dimensions.add' key(s) {format_names(malformed)} must be "
            "lowercase identifiers, like the dimensions they sit beside")
    dupes = sorted({k for k in added if added.count(k) > 1})
    if dupes:
        errors.append(
            f"'base_dimensions.add' declares {format_names(dupes)} in more "
            "than one category")

    if form is not None and added:
        defined = set(base_dimensions.form_added_criteria(form))
        undefined = [k for k in added if k not in defined]
        if undefined:
            errors.append(
                f"'base_dimensions.add' names {format_names(undefined)} with "
                "no criteria; add a '- <key> — ...' bullet under a "
                "'## Base Dimensions' section in this form — a judge scores "
                "from prose, and a dimension with none cannot be scored")
    return errors


def effective_shape(form_meta, genre_shape, band):
    """Reconcile a form's length with a genre's, for one band.

    The division of labour: a FORM owns how long the whole work is, a
    GENRE owns chapter granularity — 1,900-word chapters in one genre
    against 3,200 in another is a genre fact, not a length fact — and the
    chapter COUNT belongs to neither, because it follows from both.

    A genre may still narrow the length within a form, per band, and most
    do: one pack runs 110,000-140,000 where another runs 75,000, and
    collapsing every pack onto one form default would lose that. Where the
    genre says nothing about this band, the form's own range and target
    apply unchanged.

    Returns the resolved shape plus `words_source`, naming which pack the
    range came from, so an unexpected target is explicable.
    """
    # A form may override chapter granularity, and a compressed one must:
    # the genre owns it at novel length, where a chapter is the genre's own
    # unit, but a five-thousand-word story's unit is a scene and dividing
    # it by a novel genre's 3,200-word chapters yields one and a
    # remainder. Where the form says nothing, the genre's value stands.
    chapter_words = (form_meta.get("chapter_words")
                     or genre_shape.get("chapter_words"))
    chapter_words_source = ("form" if form_meta.get("chapter_words")
                            else "genre")

    genre_words = (genre_shape.get("words") or {}).get(band)
    if genre_words:
        words, source = genre_words, "genre"
        target = _round_to(sum(words) / 2, 1000)
        # A genre range may legitimately straddle the form's ceiling — see
        # ranges_overlap — but the target it implies must be a length the
        # form actually covers, or the work is being aimed outside its own
        # form.
        target = min(max(target, form_meta["words"][0]), form_meta["words"][1])
    else:
        words, source = form_meta["words"], "form"
        target = form_meta["target_words"]

    chapters = max(1, round(target / chapter_words)) if chapter_words else None
    return {
        "words": words,
        "words_source": source,
        "target_words": target,
        "chapter_words": chapter_words,
        "chapter_words_source": chapter_words_source,
        "chapters": chapters,
        "pov_default": genre_shape.get("pov_default"),
    }


def _round_to(value, step):
    return int(round(value / step) * step)


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
