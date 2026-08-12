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
"""
import argparse
import json
import re
import sys
from pathlib import Path

from genre_pack import PackError, _names, parse_pack, validate_pack

DEFAULT_GENRE = "general"
PLUGIN_GENRES = Path(__file__).resolve().parent.parent / "genres"

# A pack name is a bare filename stem: lowercase letters, digits, and
# hyphens. Rejecting anything else before it reaches a path join stops a
# name like "../outside" from escaping the genres/ directory it's looked up
# in, and turns a state.json typo into a clear message instead of a
# baffling "unknown genre pack" for a name that was never a real attempt at
# one.
NAME_RE = re.compile(r"[a-z0-9][a-z0-9-]*")


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
    names = {p.stem for p in PLUGIN_GENRES.glob("*.md")}
    names |= {p.stem for p in (project / "genres").glob("*.md")}
    names.discard("TEMPLATE")
    return names


def find_pack(project, name):
    if not NAME_RE.fullmatch(name or ""):
        fail(f"invalid genre pack name {name!r}; use lowercase letters, "
             "digits, and hyphens only")
    for candidate in (project / "genres" / f"{name}.md",
                      PLUGIN_GENRES / f"{name}.md"):
        if candidate.exists():
            return candidate
    fail(f"unknown genre pack {name!r}; looked in {project / 'genres'} and "
         f"{PLUGIN_GENRES}")


def load_pack(project, name, role, names):
    path = find_pack(project, name)
    try:
        pack = parse_pack(path)
    except PackError as e:
        fail(str(e))
    errors = validate_pack(pack, known_names=names)
    if errors:
        fail(f"{path} is invalid:\n  " + "\n  ".join(errors))
    if role not in pack["meta"].get("role", []):
        fail(f"pack {name!r} does not declare role {role!r} "
             f"(it declares {pack['meta'].get('role')})")
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
        fail(f"genre_modifiers lists {_names(dupes)} more than once")
    for modifier in modifiers:
        packs.append(load_pack(project, modifier, "modifier", names))

    check_conflicts(packs)
    return packs


def check_conflicts(packs):
    loaded = {p["meta"]["name"] for p in packs}
    for pack in packs:
        name = pack["meta"]["name"]
        clashes = sorted(
            set(pack["meta"].get("conflicts_with") or []) & loaded)
        if clashes:
            fail(f"pack {name!r} conflicts with loaded pack(s) "
                 f"{_names(clashes)}")


def merge(packs):
    primary = packs[0]
    meta = primary["meta"]

    content_register = {}
    artifacts = []
    for pack in packs:
        content_register.update(pack["meta"].get("content_register") or {})
        for artifact in pack["meta"].get("artifacts") or []:
            if artifact not in artifacts and pack["used_as"] != "modifier":
                artifacts.append(artifact)

    return {
        "packs": [{"name": p["meta"]["name"], "role": p["used_as"],
                   "path": str(p["path"])} for p in packs],
        "label": meta["label"],
        "label_parts": [p["meta"]["label"] for p in packs],
        "pillar_label": meta.get("pillar_label"),
        "weights": meta.get("weights"),
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
