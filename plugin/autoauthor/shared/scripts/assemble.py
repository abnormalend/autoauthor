#!/usr/bin/env python3
"""Assemble a container's works into one manuscript, in the running order.

Run from a container project directory:
  python3 assemble.py            # writes assembled/ and reports
  python3 assemble.py --check    # report only, write nothing

The bridge between "a collection resolves" and "a collection is a book".
Export builds a PDF and an ePub out of `chapters/ch_NN.md`; a container has
no `chapters/` of its own, only `works/<name>/chapters/`. This writes the
one the export step expects, in the order the container declares, with each
work introduced by its own title.

Only a structure that assembles as ONE BOOK is assembled — a collection is
a book made of works and is bound as one; a series is books, plural, and
each volume exports on its own. Binding a series into a single volume is an
omnibus, which is a legitimate thing to want and never the default, because
every volume was written to be a book.

Chapter numbering restarts nowhere: the assembled sequence is gapless from
1, because that is what the typesetter needs and what a reader of a bound
book sees. Each work's own numbering stays untouched in its own directory.
"""
import argparse
import json
import re
import sys
from pathlib import Path

import structure

ASSEMBLED = Path("assembled")

# `# Chapter N: Title` — what export normalizes every chapter to, and what
# has to be rewritten when a chapter's number changes on its way into the
# bound book.
HEADING_RE = re.compile(r"^#\s+Chapter\s+\d+\s*:\s*(?P<title>.+?)\s*$", re.M)


def work_title(work_dir):
    """What to call this work on its half-title page.

    Its own state.json `title` if it has one, else the directory name with
    any ordering prefix stripped and the hyphens turned back into spaces.
    A collection's directories are conventionally `01-slug`, and the `01`
    is a filing convention rather than part of the title.

    The fallback is a fallback. A work whose title lives only in its
    directory name gets a half-title of "Porter" above a story called
    "The Warm Key", silently, in a bound book that builds without
    complaint — which is why `foundation` records the title as soon as
    the work has one.
    """
    state_path = work_dir / "state.json"
    if state_path.exists():
        try:
            title = json.loads(state_path.read_text(encoding="utf-8")).get("title")
        except (OSError, json.JSONDecodeError):
            title = None
        if isinstance(title, str) and title.strip():
            return title.strip()
    stem = re.sub(r"^\d+[-_]", "", work_dir.name)
    return stem.replace("-", " ").replace("_", " ").title()


def work_chapters(work_dir):
    return [p for p in sorted((work_dir / "chapters").glob("ch_*.md"))
            if p.stat().st_size > 0]


def assemble(container, state, write=True):
    """Write `assembled/ch_NN.md` for every chapter, in running order.

    Returns a list of {work, title, chapters, first, last} — enough for the
    caller to report what went where, which matters because a bound book
    silently missing a story is the failure this whole path risks.
    """
    kind = structure.structure_of(state)
    if not structure.ASSEMBLES_AS_ONE_BOOK.get(kind, True):
        raise structure.StructureError(
            f"a {kind} does not assemble into one book — each volume is a "
            "book and exports on its own. Run export from inside a volume. "
            "(An omnibus is a real thing to want; it is not this, and it "
            "would need its own front matter and its own decisions.)")

    children = structure.ordered_children(container, state)
    if write:
        for stale in ASSEMBLED.glob("ch_*.md"):
            stale.unlink()
        ASSEMBLED.mkdir(exist_ok=True)

    report, number = [], 0
    for work in children:
        chapters = work_chapters(work)
        title = work_title(work)
        entry = {"work": work.name, "title": title,
                 "chapters": len(chapters), "first": None, "last": None}
        for index, source in enumerate(chapters):
            number += 1
            entry["first"] = entry["first"] or number
            entry["last"] = number
            if write:
                _write_chapter(source, number, title, first=index == 0)
        report.append(entry)
    return report


def _write_chapter(source, number, work_title_text, first):
    """One chapter, renumbered for the bound sequence.

    The first chapter of each work carries a half-title above its own
    heading, which is how a reader knows a new story has started. Every
    other chapter is copied with only its number rewritten — the prose is
    never touched, and a chapter whose heading does not match the expected
    shape is copied verbatim rather than guessed at.
    """
    text = source.read_text(encoding="utf-8")
    match = HEADING_RE.search(text)
    if match:
        text = (text[:match.start()]
                + f"# Chapter {number}: {match.group('title')}"
                + text[match.end():])
    if first:
        text = f"## {work_title_text}\n\n" + text
    (ASSEMBLED / f"ch_{number:02d}.md").write_text(text, encoding="utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="report what would be assembled, write nothing")
    args = parser.parse_args(argv)

    project = Path.cwd()
    try:
        state = structure.read_state(project)
        if not structure.is_container(state):
            print("not a container project — there is nothing to assemble, "
                  "and export reads chapters/ directly", file=sys.stderr)
            return 2
        report = assemble(project, state, write=not args.check)
    except structure.StructureError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    total = sum(entry["chapters"] for entry in report)
    empty = [entry["work"] for entry in report if not entry["chapters"]]
    for entry in report:
        span = (f"ch {entry['first']}-{entry['last']}" if entry["chapters"]
                else "NOTHING DRAFTED")
        print(f"  {entry['work']:24} {entry['title'][:34]:34} {span}")
    print(f"{total} chapters from {len(report)} works"
          + ("" if args.check else f" -> {ASSEMBLED}/"))
    if empty:
        print(f"WARNING: {', '.join(empty)} contributed no chapters; the "
              "bound book would be missing them", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
