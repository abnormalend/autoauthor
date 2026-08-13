"""The base dimensions, and which of them a form applies.

Every work is scored on its genre's pillar dimensions plus three further
categories — character, structure, craft — that used to be written into
`rubrics/foundation.md` as a fixed list. They are a fixed list no longer,
for the same reason the pillar dimensions stopped being one: the criteria
assume a novel. `foreshadowing_balance` scores a ledger, `canon_coverage`
assumes a canon file, `character_depth` wants a causally linked
wound/want/need/lie chain. A five-thousand-word story plants and pays
within a page and often gives one character at one moment, and scoring it
against a ledger it should not keep penalizes it for being correctly what
it is.

So a form pack selects. It drops what its length cannot earn and may add
dimensions of its own, and this module turns that declaration into the
list the judge is actually handed.

The criteria stay in prose, in `rubrics/base-dimensions.md`, because a
judge reads them. Only the selection is data.
"""
from pathlib import Path

from genre_pack import (PackError, dimension_bullets, format_names,
                        section_body)

# The scored categories other than the pillar. Order is load-bearing: it is
# the order the rubric lists them in, and the order the rubric breaks a tie
# in `weakest_dimension` by.
CATEGORIES = ("character", "structure", "craft")

# The '## ' heading each category lives under in base-dimensions.md.
# Title-cased so the file reads as prose to the judge who follows it.
CATEGORY_HEADINGS = {category: category.title() for category in CATEGORIES}

BASE_DIMENSIONS_PATH = (Path(__file__).resolve().parent.parent
                        / "rubrics" / "base-dimensions.md")

MIN_CAP, MAX_CAP = 1, 9


def parse_base_dimensions(path=None):
    """Read base-dimensions.md.

    Returns {category: {"dimensions": [...], "caps": {}, "prose_caps": {}}}
    — per category, the same three things parse_pack returns for a genre
    pack's pillar section.

    Raises PackError on a missing or empty category section. A silently
    empty category would drop a third of the rubric with nothing failing,
    which is the failure mode this whole project keeps producing.
    """
    path = Path(path) if path else BASE_DIMENSIONS_PATH
    try:
        body = path.read_text(encoding="utf-8-sig")
    except OSError as e:
        raise PackError(f"{path}: cannot read base dimensions: {e}") from e

    parsed = {}
    for category in CATEGORIES:
        heading = CATEGORY_HEADINGS[category]
        section = section_body(body, heading)
        if section is None:
            raise PackError(
                f"{path}: no '## {heading}' section; the base rubric needs "
                f"one per category ({format_names(CATEGORIES)})")
        dimensions, malformed, caps, prose_caps = dimension_bullets(section)
        if malformed:
            raise PackError(
                f"{path}: base dimension(s) "
                f"{format_names(sorted(malformed))} under '## {heading}' use "
                "a hyphen or en dash; an em dash (—) is required")
        if not dimensions:
            raise PackError(f"{path}: '## {heading}' declares no dimensions")
        parsed[category] = {"dimensions": dimensions, "caps": caps,
                            "prose_caps": prose_caps}
    return parsed


def all_keys(parsed):
    """Every base dimension key, across categories."""
    return {key for entry in parsed.values() for key in entry["dimensions"]}


def category_of(parsed, key):
    """Which category a base dimension key belongs to, or None."""
    for category in CATEGORIES:
        if key in parsed[category]["dimensions"]:
            return category
    return None


def validate_base_dimensions(parsed):
    """Check the file's caps the way a genre pack's are checked.

    Returns human-readable error strings. There is no reachability
    arithmetic here: base caps constrain `overall_score`, which is a
    weighted mean across four categories, not the pillar gate. What must
    hold is that a declared cap and the criteria a judge reads say the same
    number — the declaration is what tooling sees and the prose is what
    decides the score.
    """
    errors = []
    for category in CATEGORIES:
        entry = parsed[category]
        for key in entry["dimensions"]:
            declared = entry["caps"].get(key)
            stated = entry["prose_caps"].get(key)
            if declared is not None and not MIN_CAP <= declared <= MAX_CAP:
                errors.append(
                    f"{category}.{key} declares [cap {declared}]; a cap must "
                    f"be {MIN_CAP}-{MAX_CAP}")
            if declared is None and stated is not None:
                errors.append(
                    f"{category}.{key} states a cap of {stated} in its "
                    f"criteria but declares none; write "
                    f"'- {key} [cap {stated}] — ...'")
            elif declared is not None and stated is None:
                errors.append(
                    f"{category}.{key} declares [cap {declared}] but its "
                    "criteria never state it")
            elif (declared is not None and stated is not None
                    and declared != stated):
                errors.append(
                    f"{category}.{key} declares [cap {declared}] but its "
                    f"criteria can force it to {stated}; the declared cap is "
                    "the LOWEST tier the criteria can reach")

    dupes = _duplicate_keys(parsed)
    if dupes:
        errors.append(
            f"base dimension key(s) {format_names(dupes)} appear in more than "
            "one category; a key names exactly one dimension")
    return errors


def _duplicate_keys(parsed):
    seen, dupes = set(), set()
    for category in CATEGORIES:
        for key in parsed[category]["dimensions"]:
            (dupes if key in seen else seen).add(key)
    return sorted(dupes)


def resolve_for_form(parsed, form_meta):
    """Apply a form's drops and adds. Returns (scored, dropped).

    `scored` is {category: [key, ...]} in the file's own order, with the
    form's additions appended to their declared category. `dropped` is the
    flat sorted list of keys the form removed — reported so that a
    dimension missing from a verdict is explicable, rather than looking
    like a judge that forgot one.
    """
    base = form_meta.get("base_dimensions") or {}
    drop = set(base.get("drop") or [])
    add = base.get("add") or {}

    scored, dropped = {}, []
    for category in CATEGORIES:
        declared = parsed[category]["dimensions"]
        scored[category] = ([k for k in declared if k not in drop]
                            + list(add.get(category) or []))
        dropped.extend(k for k in declared if k in drop)
    return scored, sorted(dropped)


def added_keys(form_meta):
    """Every key a form adds, flat, in category order."""
    add = (form_meta.get("base_dimensions") or {}).get("add") or {}
    return [key for category in CATEGORIES
            for key in (add.get(category) or [])]


def form_added_criteria(form):
    """Keys the form's own '## Base Dimensions' section writes criteria for.

    A form that adds a dimension has to say what it means somewhere, and a
    judge only ever reads prose — so an added key with no bullet here is a
    dimension nobody can score.
    """
    section = section_body(form["body"], "Base Dimensions")
    if section is None:
        return []
    return dimension_bullets(section)[0]


def empty_categories(scored):
    """Categories a form has emptied.

    An empty category is not merely tidy-looking: the primary pack's
    `weights` still assign it a share of `overall_score`, and the mean of
    no dimensions is undefined.
    """
    return [category for category in CATEGORIES if not scored[category]]
