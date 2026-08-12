#!/usr/bin/env python3
"""Resolve a novel project's genre packs and print the merged config as JSON.

Run from the novel project directory:
  python3 resolve_genre.py           # reads ./state.json, prints JSON
  python3 resolve_genre.py --check   # validate only, print nothing on success

Search order for each pack name: ./genres/<name>.md first, then the plugin's
shared/genres/<name>.md. The project wins, so a one-off pack for a single
novel needs no plugin change.

Exit 0 on success; 1 with a message on stderr for any resolution, validation,
or conflict error.

Output schema (the JSON printed on stdout when --check is not given) — six
skills parse this, none of which can see this module's source:

  packs             — [{"name", "role", "path"}, ...], one entry per
                       loaded pack, in resolution order: primary first,
                       then secondary (if any), then modifiers in
                       state.json's genre_modifiers order.
  primary_label     — the primary pack's own 'label' field, verbatim.
  display_label     — every loaded pack's 'label', joined with a space,
                       in the same order as 'packs' — this is what should
                       be shown to a reader (a title page, a status
                       line), not 'primary_label' alone.
  label_parts       — the list display_label was joined from, for a
                       caller that wants to lay the parts out itself.
  pillar_label      — the primary pack's 'pillar_label'.
  weights           — the primary pack's 'weights' dict
                       (pillar/character/structure/craft -> int, sums to
                       100).
  beat_system       — the primary pack's 'beat_system', or "save-the-cat"
                       if it didn't declare one.
  shape             — the primary pack's 'shape' dict (chapters/words
                       ranges, chapter_words, pov_default), or {} if it
                       declared none.
  content_register  — merged content_register dicts from every loaded
                       pack (primary, secondary, and modifiers alike);
                       see merge() for the collision rule.
  artifacts         — the union of every non-modifier pack's 'artifacts'
                       list, in first-seen order; a modifier's own
                       'artifacts' entries are deliberately excluded —
                       see merge().
"""
import argparse
import json
import sys
from pathlib import Path

# NAME_RE is shared with validate_pack rather than redefined here: a name
# this resolver would reject must be the same name the authoring-time
# validator rejects, or a pack validates clean and then fails at resolve
# time. Rejecting anything else before it reaches a path join also stops a
# name like "../outside" from escaping the genres/ directory it's looked up
# in, and turns a state.json typo into a clear message instead of a
# baffling "unknown genre pack" for a name that was never a real attempt at
# one.
from genre_pack import (NAME_RE, PackError, format_names, pack_names_in,
                        parse_pack, validate_pack)

DEFAULT_GENRE = "general"
PLUGIN_GENRES = Path(__file__).resolve().parent.parent / "genres"


def fail(message):
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_state(project):
    path = project / "state.json"
    if not path.exists():
        fail(f"no state.json in {project} — run this from a novel project "
             "directory")
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        fail(f"state.json is not valid JSON: {e}")
    if not isinstance(state, dict):
        fail(f"state.json must be a JSON object, got a JSON "
             f"{type(state).__name__}")
    return state


def known_names(project):
    return pack_names_in(PLUGIN_GENRES) | pack_names_in(project / "genres")


def find_pack(project, name, names):
    if not NAME_RE.fullmatch(name or ""):
        fail(f"invalid genre pack name {name!r}; use lowercase letters, "
             "digits, and hyphens only")
    for candidate in (project / "genres" / f"{name}.md",
                      PLUGIN_GENRES / f"{name}.md"):
        if candidate.exists():
            return candidate
    fail(f"unknown genre pack {name!r}; looked in {project / 'genres'} and "
         f"{PLUGIN_GENRES}; known packs: {format_names(sorted(names))}")


def load_pack(project, name, role, names):
    path = find_pack(project, name, names)
    try:
        pack = parse_pack(path)
    except PackError as e:
        fail(str(e))
    errors = validate_pack(pack, known_names=names)
    if errors:
        fail(f"{path} is invalid:\n  " + "\n  ".join(errors))
    if role not in pack["meta"].get("role", []):
        fail(f"pack {name!r} does not declare role {role!r} (it declares "
             f"{format_names(pack['meta'].get('role') or [])}); add "
             f"{role!r} to its 'role' list, or choose a different pack "
             "for that slot")
    pack["used_as"] = role
    return pack


def resolve(project):
    state = load_state(project)
    names = known_names(project)

    packs = [load_pack(project, state.get("genre") or DEFAULT_GENRE,
                       "primary", names)]
    if state.get("genre_secondary"):
        packs.append(load_pack(project, state["genre_secondary"],
                               "secondary", names))

    modifiers = state.get("genre_modifiers") or []
    # A repeated modifier means state.json is wrong, not that the author
    # wants it applied twice — silently deduping would let a doubled genre
    # string reach the merged label (and the book's title page at export)
    # without anyone noticing.
    dupes = sorted({m for m in modifiers if modifiers.count(m) > 1})
    if dupes:
        fail(f"genre_modifiers lists {format_names(dupes)} more than "
             "once; remove one of them from state.json")
    for modifier in modifiers:
        packs.append(load_pack(project, modifier, "modifier", names))

    check_conflicts(packs)
    return packs


def check_conflicts(packs):
    # The same pack filling two slots (e.g. genre and genre_secondary both
    # "fantasy") is the same failure the genre_modifiers duplicate guard
    # above prevents, one slot over — it must be caught here too, since a
    # pack can legally declare more than one role and so pass load_pack's
    # role check in both slots.
    loaded_list = [p["meta"]["name"] for p in packs]
    dupes = sorted({n for n in loaded_list if loaded_list.count(n) > 1})
    if dupes:
        fail(f"pack(s) {format_names(dupes)} fill more than one slot; a "
             "pack may be used once — check genre, genre_secondary, and "
             "genre_modifiers in state.json")

    loaded = set(loaded_list)
    for pack in packs:
        name = pack["meta"]["name"]
        clashes = sorted(
            set(pack["meta"].get("conflicts_with") or []) & loaded)
        if clashes:
            fail(f"pack {name!r} conflicts with loaded pack(s) "
                 f"{format_names(clashes)}")


def merge(packs):
    # The primary owns every scalar structural field (pillar_label,
    # weights, beat_system, shape) — it's the pack that owns pillar
    # dimensions and book shape by definition (see genre_pack.py's
    # PRIMARY_ONLY_FIELDS), so a secondary or modifier's copy of these,
    # if it even has one, is never consulted.
    primary = packs[0]
    meta = primary["meta"]

    content_register = {}
    artifacts = []
    for pack in packs:
        # content_register merges across every loaded pack, not just the
        # primary — it's the orthogonal axis a modifier exists to set (an
        # "explicit" heat-level modifier layered onto a primary that
        # declares none). Two packs setting the SAME key to DIFFERENT
        # values is a real authoring conflict, not something merge() can
        # silently resolve: this field is what tells the LLM subagents
        # doing the actual writing where the content boundaries are, and
        # the merged value is all they ever see.
        for key, value in (pack["meta"].get("content_register") or {}).items():
            if key in content_register and content_register[key] != value:
                fail(f"packs disagree on content_register {key!r}: "
                     f"{content_register[key]!r} vs {value!r}; add a "
                     "'conflicts_with' entry or drop one modifier")
            content_register[key] = value
        # A modifier's own 'artifacts' entries are excluded from the
        # union: artifacts are per-book deliverables (a clue ledger, a
        # heat-tracking sheet) that the primary/secondary genre owns:
        # letting every modifier add its own would mean a heat-level or
        # age-category modifier — an orthogonal axis, not a genre — could
        # spawn project files the pipeline never asked for.
        for artifact in pack["meta"].get("artifacts") or []:
            if artifact not in artifacts and pack["used_as"] != "modifier":
                artifacts.append(artifact)

    label_parts = [p["meta"]["label"] for p in packs]
    return {
        "packs": [{"name": p["meta"]["name"], "role": p["used_as"],
                   "path": str(p["path"])} for p in packs],
        "primary_label": meta["label"],
        "display_label": " ".join(label_parts),
        "label_parts": label_parts,
        # pillar_label and weights use direct indexing, not .get(): both
        # are guaranteed present here. packs[0] is always loaded with
        # role="primary" (load_pack enforces it), and validate_pack
        # requires pillar_label on every primary and valid weights on
        # every scoring role (primary is always one, see SCORING_ROLES).
        # A .get() here would tell downstream readers these could be
        # null and leave them no way to handle a case that can't happen.
        "pillar_label": meta["pillar_label"],
        "weights": meta["weights"],
        "beat_system": meta.get("beat_system", "save-the-cat"),
        "shape": meta.get("shape", {}),
        "content_register": content_register,
        "artifacts": artifacts,
    }


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="validate only; print nothing on success")
    args = parser.parse_args(argv)

    packs = resolve(Path.cwd())
    if args.check:
        return 0
    print(json.dumps(merge(packs), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
