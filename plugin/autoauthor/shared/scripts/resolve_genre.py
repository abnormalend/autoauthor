#!/usr/bin/env python3
"""Resolve a novel project's genre packs and print the merged config as JSON.

Run from the novel project directory:
  python3 resolve_genre.py           # reads ./state.json, prints JSON
  python3 resolve_genre.py --check   # validate only, print nothing on success

Search order for each pack name: ./genres/<name>.md first, then the plugin's
shared/genres/<name>.md. The project wins, so a one-off pack for a single
novel needs no plugin change.

DEFAULTING — read this before treating exit 0 as "the project has a genre".
A state.json whose 'genre' is null, absent, or an empty string resolves to
the 'general' pack, silently and successfully. That is deliberate: it keeps
a hand-built project usable without a genre step. But it means a clean exit
proves only that SOME pack resolved, never that anyone chose one — and the
shipped state.json template ships '"genre": null'. A caller that needs to
know a genre was actually chosen must inspect state.json's 'genre' itself
and treat null/missing as unset, not infer it from this script's exit code
or from primary_label. 'genre_secondary' defaults to none and
'genre_modifiers' to the empty list under the same rule.

Exit 0 on success; 1 with a message on stderr for any resolution, validation,
or conflict error.

Output schema (the JSON printed on stdout when --check is not given) — six
skills parse this, none of which can see this module's source:

  packs             — [{"name", "role", "path"}, ...], one entry per
                       loaded pack, in resolution order: primary first,
                       then secondary (if any), then modifiers in
                       state.json's genre_modifiers order.
  primary_label     — the primary pack's own 'label' field, verbatim.
  display_label     — the loaded packs' 'label' values, joined with a
                       space, skipping any whose every word already
                       appeared (so a 'paranormal-romance' primary with a
                       'romance' secondary reads "Paranormal Romance",
                       not "Paranormal Romance Romance"),
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
  content_register  — merged intensity levels from every loaded pack
                       (primary, secondary, and modifiers alike), clamped
                       per axis to the MOST RESTRICTIVE level any of them
                       declares. Axes and their ordered scales are defined
                       by CONTENT_AXES in genre_pack.py.
  content_register_sources
                    — which pack each surviving level came from, so a
                       caller can explain a clamp the user did not expect
                       (a ya modifier pulling a romance's heat down).
  artifacts         — the union of every non-modifier pack's 'artifacts'
                       list, in first-seen order; a modifier's own
                       'artifacts' entries are deliberately excluded —
                       see merge().
  form              — {"name", "label", "band", "words", "target_words",
                       "gate", "layers", "path"} from the resolved form
                       pack. 'band' is what a genre pack's length-scoped
                       sections key off; 'gate' is the pair the foundation
                       loop exits on; 'layers' is which planning documents
                       get built at this length. A state.json with no
                       'form' resolves to 'novel', under the same
                       defaulting rule as 'genre' above and with the same
                       caveat — a clean exit never proves anyone chose it.
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
import form_pack
import gate_solver
from genre_pack import (CONTENT_AXES, NAME_RE, PackError, format_names,
                        pack_names_in,
                        parse_pack, validate_pack)

DEFAULT_GENRE = "general"
DEFAULT_FORM = "novel"
PLUGIN_GENRES = Path(__file__).resolve().parent.parent / "genres"
PLUGIN_FORMS = Path(__file__).resolve().parent.parent / "forms"


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


def load_form(project, name):
    """Resolve the form pack, project copy winning, same as a genre pack."""
    if not NAME_RE.fullmatch(name or ""):
        fail(f"invalid form name {name!r}; use lowercase letters, digits, "
             "and hyphens only")
    for candidate in (project / "forms" / f"{name}.md",
                      PLUGIN_FORMS / f"{name}.md"):
        if candidate.exists():
            break
    else:
        known = ({p.stem for p in PLUGIN_FORMS.glob("*.md")}
                 | {p.stem for p in (project / "forms").glob("*.md")}
                 ) - {form_pack.TEMPLATE_STEM}
        fail(f"unknown form {name!r}; looked in {project / 'forms'} and "
             f"{PLUGIN_FORMS}; known forms: {format_names(sorted(known))}")
    try:
        form = form_pack.parse_form(candidate)
    except PackError as e:
        fail(str(e))
    errors = form_pack.validate_form(form)
    if errors:
        fail(f"{candidate} is invalid:\n  " + "\n  ".join(errors))
    return form


def check_form_against_primary(form, primary):
    """The two places a form and a genre have to agree.

    Both are cross-pack facts, so neither can be checked when either pack
    is validated on its own — which is why they live here and not in
    validate_form or validate_pack.
    """
    meta, name = form["meta"], primary["meta"]["name"]

    words = (primary["meta"].get("shape") or {}).get("words")
    if words and not form_pack.ranges_overlap(words, meta["words"]):
        fail(f"genre {name!r} runs {words[0]:,}-{words[1]:,} words and the "
             f"{meta['name']!r} form is {meta['words'][0]:,}-"
             f"{meta['words'][1]:,}; there is no length that satisfies "
             "both. Choose a form that fits the genre, or a genre pack "
             "written for this length.")

    # The gate the loop actually enforces has to be one the pack's own
    # caps can reach. gate_solver rejects a pack below the 7.0 floor at
    # authoring time; this catches a FORM that raises the bar above what
    # the genre beside it can support, which no single-pack check can see.
    ceiling = gate_solver.max_gate(len(primary["dimensions"]),
                                   sorted(primary["caps"].values()))
    gate = meta["gate"]["pillar"]
    if ceiling is not None and gate > ceiling:
        fail(f"form {meta['name']!r} gates the pillar at {gate}, but genre "
             f"{name!r} tops out at {ceiling} — with its caps, no book can "
             "clear that bar. Lower the form's gate or give the genre pack "
             "more dimensions (see TEMPLATE.md, Calibration).")


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

    form = load_form(project, state.get("form") or DEFAULT_FORM)
    check_form_against_primary(form, packs[0])
    return packs, form


def check_conflicts(packs):
    # The same pack filling two slots (genre and genre_secondary naming the
    # same pack) is the same failure the genre_modifiers duplicate guard
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


def _label_parts(packs):
    """Every loaded pack's label, minus any that says nothing new.

    A naive join renders 'Paranormal Romance' + 'Romance' as "Paranormal
    Romance Romance" on the title page at export, because a hybrid pack's
    label legitimately contains its parent's. Drop a part only when EVERY
    word in it has already appeared — 'Romance' after 'Paranormal Romance'
    goes, 'Historical' after 'Romance' stays. Comparison is case-folded on
    whole words, so a label is never dropped for sharing a prefix.
    """
    parts, seen = [], set()
    for pack in packs:
        label = pack["meta"]["label"]
        words = {w.casefold() for w in label.split()}
        if words and words <= seen:
            continue
        seen |= words
        parts.append(label)
    return parts


def merge(packs, form):
    # The primary owns every scalar structural field (pillar_label,
    # weights, beat_system, shape) — it's the pack that owns pillar
    # dimensions and book shape by definition (see genre_pack.py's
    # PRIMARY_ONLY_FIELDS), so a secondary or modifier's copy of these,
    # if it even has one, is never consulted.
    primary = packs[0]
    meta = primary["meta"]

    content_register, register_sources = _merge_content_register(packs)
    artifacts = []
    for pack in packs:
        # A modifier's own 'artifacts' entries are excluded from the
        # union: artifacts are per-book deliverables (a clue ledger, a
        # heat-tracking sheet) that the primary/secondary genre owns:
        # letting every modifier add its own would mean a heat-level or
        # age-category modifier — an orthogonal axis, not a genre — could
        # spawn project files the pipeline never asked for.
        for artifact in pack["meta"].get("artifacts") or []:
            if artifact not in artifacts and pack["used_as"] != "modifier":
                artifacts.append(artifact)

    label_parts = _label_parts(packs)
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
        "content_register_sources": register_sources,
        "artifacts": artifacts,
        # The form's own frontmatter, passed through rather than folded
        # into the keys above. `shape` stays the genre's: a form owns how
        # long the whole work is, a genre owns chapter granularity, and
        # collapsing them here would make it impossible for a caller to
        # tell which pack asked for what.
        "form": {
            "name": form["meta"]["name"],
            "label": form["meta"]["label"],
            "band": form["meta"]["band"],
            "words": form["meta"]["words"],
            "target_words": form["meta"]["target_words"],
            "gate": form["meta"]["gate"],
            "layers": form["meta"]["layers"],
            "path": str(form["path"]),
        },
    }


def _merge_content_register(packs):
    """Clamp a stack to the most restrictive level each pack declares.

    content_register merges across every loaded pack, not just the primary —
    it is the orthogonal axis a modifier exists to set (a heat-level modifier
    over a primary that declares none). Two packs setting the same axis to
    different levels is NOT an authoring error: a `ya` modifier over a
    romance primary is the normal case, and the right answer is the ya level.

    Because CONTENT_AXES orders each scale, that resolves deterministically
    to the lower index — the more restrictive level — rather than to whichever
    pack happened to load last, and rather than to a hard failure. Restrictive
    is the safe direction: a book that under-delivers on heat disappoints,
    while one that over-delivers can breach an age-category promise.

    Returns (levels, sources), where sources names the pack each surviving
    level came from so a caller can explain a clamp it did not expect.
    """
    levels, sources = {}, {}
    for pack in packs:
        name = pack["meta"]["name"]
        for axis, level in (pack["meta"].get("content_register") or {}).items():
            scale = CONTENT_AXES[axis]  # validate_pack guarantees membership
            if axis not in levels or scale.index(level) < scale.index(levels[axis]):
                levels[axis] = level
                sources[axis] = name
    return levels, sources


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="validate only; print nothing on success")
    args = parser.parse_args(argv)

    packs, form = resolve(Path.cwd())
    if args.check:
        return 0
    print(json.dumps(merge(packs, form), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
