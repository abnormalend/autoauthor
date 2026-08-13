"""The structure axis: how many complete works there are, and how they relate.

The distinction this exists to keep straight, and the one the form work
kept insisting on: SCALE is a pack, because it changes which dimensions
apply. STRUCTURE is not, because it changes the state schema and the phase
graph, and no pack can do either. A collection has a story list, a
cross-work phase before export, and a directory per work; none of that is
expressible as criteria.

    standalone   one work                today's pipeline, and the default
    collection   N works + a variety pass
    series       N works + a continuity and arc pass
    serial       one work, released in parts (not yet)

`collection` and `series` are the same machine pointed at opposite goals.
Both are a container directory, a shared bible, N child works, and one
cross-work phase. The cross-work check is the whole difference: a
collection wants VARIETY and independence — no trick twice, and every work
standing alone — while a series wants CONTINUITY and ARC, where nothing
contradicts what came before and each volume both advances the whole and
closes itself.

That inversion reaches further than the rubric. In a collection, works
that read alike is the defect; in a series it is the point, and what wants
watching is the volume that reads unlike its neighbours.

A container project is one directory holding a shared bible and a `works/`
directory of children. Each child is an ordinary project — its own
state.json, its own layers, its own phase — and the container owns exactly
two things the children cannot: what unifies them, and what order they go
in.

Both container and child use `state.json`, rather than the `series.json`
the design sketched. One filename, one parser, and `structure` is what
tells them apart — a second config format would have been a second thing
to keep in step.

INHERITANCE runs downward and is the opposite of the pack precedent. With
packs the project copy wins, because specificity is the point. With genre,
form and canon the CONTAINER wins, because coherence is: a collection
whose third story is in a different genre is not a collection.
"""
import json
from pathlib import Path

# Ordered least to most machinery, which is also the order they ship in.
STRUCTURES = ("standalone", "collection", "series")

# Structures whose project is a container of child works rather than a
# work itself.
CONTAINER_STRUCTURES = frozenset({"collection", "series"})

DEFAULT_STRUCTURE = "standalone"

WORKS_DIR = "works"
BIBLE_DIR = "bible"

# Bible files a structure cannot do without. A collection needs somewhere
# to state what binds it; a series needs that plus the two documents its
# cross-work pass reads — the facts that must stay true, and what each
# volume owes the whole.
REQUIRED_BIBLE = {
    "collection": ("voice.md",),
    "series": ("voice.md", "canon.md", "arc.md"),
}

# Whether the running order is an editorial choice or a fact about the
# story. Reordering a collection is a legitimate fix the cross-work pass
# can recommend; reordering a series is not a fix, it is a different
# series.
ORDER_IS_EDITORIAL = {"collection": True, "series": False}

# How far up to look for a container before concluding there is not one.
# A child sits exactly one level under `works/`, so two is enough and the
# bound keeps a stray state.json elsewhere in a home directory from being
# adopted as a parent.
SEARCH_DEPTH = 2

# Keys a child inherits from its container when it does not set them
# itself. Deliberately short: these are the facts that make N works one
# book, and a child overriding any of them has stopped being part of it.
INHERITED_KEYS = ("genre", "genre_secondary", "genre_modifiers", "form")


class StructureError(Exception):
    """Malformed container or child. The message is user-facing."""


def structure_of(state):
    """A state.json's structure, defaulting like `genre` and `form` do.

    Absent or null means `standalone`, which is what makes every project
    created before this axis existed keep working untouched.
    """
    value = state.get("structure") or DEFAULT_STRUCTURE
    if value not in STRUCTURES:
        raise StructureError(
            f"unknown structure {value!r}; valid: {', '.join(STRUCTURES)}")
    return value


def is_container(state):
    return structure_of(state) in CONTAINER_STRUCTURES


def read_state(directory):
    path = Path(directory) / "state.json"
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except OSError as e:
        raise StructureError(f"cannot read {path}: {e}") from e
    except json.JSONDecodeError as e:
        raise StructureError(f"{path} is not valid JSON: {e}") from e
    if not isinstance(state, dict):
        raise StructureError(f"{path} must be a JSON object")
    return state


def find_container(start):
    """The container this directory is a work of, or None.

    Returns (container_dir, container_state). A directory is a child only
    if it sits directly under its candidate's `works/` — proximity alone
    is not enough, or a project created inside another project's tree
    would silently inherit its genre.
    """
    start = Path(start).resolve()
    for _ in range(SEARCH_DEPTH):
        parent = start.parent
        if parent == start:
            return None
        candidate = parent.parent if parent.name == WORKS_DIR else None
        if candidate and (candidate / "state.json").exists():
            state = read_state(candidate)
            if is_container(state):
                return candidate, state
        start = parent
    return None


def child_dirs(container):
    """Every work directory under a container, in filesystem order.

    Order on disk is not the running order — that is the container's to
    declare, and `works` in its state.json holds it. This is only what
    exists.
    """
    works = Path(container) / WORKS_DIR
    if not works.is_dir():
        return []
    return sorted(p for p in works.iterdir()
                  if p.is_dir() and (p / "state.json").exists())


def ordered_children(container, state):
    """The child directories in the container's declared running order.

    Raises if the declared order and what exists on disk disagree, rather
    than silently exporting a book with a story missing or an order
    nobody chose. A collection's order is a real editorial decision — the
    opener and the closer do specific work — so a mismatch is a fault,
    not a thing to paper over.
    """
    on_disk = {p.name: p for p in child_dirs(container)}
    declared = state.get("works") or []
    if not isinstance(declared, list) or not all(
            isinstance(slug, str) for slug in declared):
        raise StructureError(
            "'works' in the container's state.json must be a list of "
            "directory names, in running order")

    missing = [slug for slug in declared if slug not in on_disk]
    extra = sorted(set(on_disk) - set(declared))
    if missing:
        raise StructureError(
            f"'works' names {', '.join(missing)}, which "
            f"{'does' if len(missing) == 1 else 'do'} not exist under "
            f"{WORKS_DIR}/")
    if extra:
        raise StructureError(
            f"{', '.join(extra)} {'exists' if len(extra) == 1 else 'exist'} "
            f"under {WORKS_DIR}/ but {'is' if len(extra) == 1 else 'are'} "
            "not in 'works'; add to the running order or remove")
    duplicates = sorted({s for s in declared if declared.count(s) > 1})
    if duplicates:
        raise StructureError(
            f"'works' lists {', '.join(duplicates)} more than once")
    return [on_disk[slug] for slug in declared]


def inherit(container_state, child_state):
    """A child's effective state: its own keys, filled in from above.

    Only INHERITED_KEYS cross the boundary. Phase and scores are the
    child's own — the whole point of the layout is that each work is a
    real project that can be at its own phase — and the container's
    `works` and `collection_score` mean nothing to a child.
    """
    merged = dict(child_state)
    inherited = []
    for key in INHERITED_KEYS:
        if merged.get(key) in (None, [], "") and key in container_state:
            merged[key] = container_state[key]
            inherited.append(key)
    merged["_inherited"] = inherited
    return merged


def _bible_reason(kind, name):
    return {
        "voice.md": "every work is written to it, and without one they are "
                    "written to whatever the last one happened to sound like",
        "canon.md": "continuity is checked against it. A volume may ADD to "
                    "series canon and may never contradict it, and there is "
                    "nothing to contradict if nobody wrote it down",
        "arc.md": "it says what each volume owes the whole. Without it the "
                  "cross-work pass can check that nothing contradicts and "
                  "cannot check that anything progressed",
    }.get(name, "it is required")


def validate_container(directory, state):
    """Check a container project. Returns human-readable error strings."""
    errors = []
    directory = Path(directory)

    kind = structure_of(state)

    if not (directory / BIBLE_DIR).is_dir():
        errors.append(
            f"no {BIBLE_DIR}/ directory; a container holds the material its "
            "works share, and without it every work rebuilds the same world "
            "slightly differently")
    else:
        for name in REQUIRED_BIBLE.get(kind, ()):
            if not (directory / BIBLE_DIR / name).exists():
                errors.append(
                    f"no {BIBLE_DIR}/{name}; a {kind} needs it — "
                    + _bible_reason(kind, name))

    if not (directory / WORKS_DIR).is_dir():
        errors.append(f"no {WORKS_DIR}/ directory")
        return errors

    try:
        children = ordered_children(directory, state)
    except StructureError as e:
        errors.append(str(e))
        return errors

    if not children:
        errors.append(
            f"no works under {WORKS_DIR}/; a collection of nothing is a "
            "container waiting for its first story, which is fine — but "
            "nothing downstream can run yet")

    for child in children:
        child_state = read_state(child)
        own = {k for k in INHERITED_KEYS if child_state.get(k) not in (None, [], "")}
        if own:
            errors.append(
                f"{WORKS_DIR}/{child.name} sets {', '.join(sorted(own))} "
                "itself; those are the container's, because they are what "
                "make these works one book")
        if structure_of(child_state) != "standalone":
            errors.append(
                f"{WORKS_DIR}/{child.name} declares a structure of its own; "
                "containers do not nest")
    return errors
