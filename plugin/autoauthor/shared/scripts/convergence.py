#!/usr/bin/env python3
"""Cross-work convergence: do the works in a collection read alike?

Run from a container project directory:
  python3 convergence.py                 # writes edit_logs/convergence.json
  python3 convergence.py --quiet         # write the file, print nothing

The one measurement a per-work judge structurally cannot make. Every judge
in this pipeline sees exactly one work, by design — a clean-room judge with
no memory of how the text was produced is what makes its verdict worth
anything. But N works written to one voice document by one model WILL
converge: the same opening move, the same emotional register, the same
reach for the same images. Nothing that reads one work at a time can see
it, and every reader of the finished book will.

So this measures across works instead. For each prose metric it computes
the coefficient of variation across the collection: high variance is
HEALTHY, because the works are doing different things, and a CV near zero
means every work reads alike on that dimension.

It is the mechanical half of the collection pass, and it is an accelerant
rather than a precondition — a pass that skips it makes a judge eyeball
things an instrument could have measured.
"""
import argparse
import json
import statistics
import sys
from pathlib import Path

import structure
import voice_fingerprint

# Below this, treat the metric as converged. Chosen to be loose enough
# that ordinary shared authorship does not trip it and tight enough to
# catch a genuine sameness.
CONVERGENCE_THRESHOLD = 0.15

# Metrics that converge because the SLATE said so, not because the works
# read alike. Reporting these as convergence sends a judge hunting for
# prose repetition that is not there.
#
# `word_count` converges whenever the works share a target length, which
# is the normal case and is now guaranteed rather than likely — the form
# owns `target_words` and every work in a collection inherits the same
# form. `sentence_count`, `paragraph_count` and `avg_paragraph_length` are
# downstream of it. `min_sentence` is worse than uninformative: the
# shortest sentence in any work of any length is almost always three
# words, so it reports a CV of 0.0 on essentially every collection.
#
# Measured on autoanthology's first real collection pass: seven metrics
# flagged as converged, five of them from this list, and only one of the
# seven was something the rubric's routing guidance knew what to do with.
SCALE_METRICS = frozenset({
    "word_count", "sentence_count", "paragraph_count",
    "avg_paragraph_length", "min_sentence", "max_sentence",
    "section_breaks",
})

OUTPUT = Path("edit_logs/convergence.json")


def work_prose(work_dir):
    """Every drafted chapter of one work, oldest first."""
    chapters = sorted((work_dir / "chapters").glob("ch_*.md"))
    return [p for p in chapters if p.stat().st_size > 0]


def analyze_work(work_dir, wells):
    """Metrics for one work, its chapters pooled.

    Pooled rather than averaged: a collection's unit is the work, and a
    work whose chapters vary internally is not converged with its
    neighbours just because their means happen to match. Concatenating
    measures the thing a reader experiences.
    """
    chapters = work_prose(work_dir)
    if not chapters:
        return None
    pooled = work_dir / ".convergence_pooled.md"
    pooled.write_text("\n\n".join(p.read_text(encoding="utf-8")
                                  for p in chapters), encoding="utf-8")
    try:
        return voice_fingerprint.analyze_chapter(pooled, wells)
    finally:
        pooled.unlink(missing_ok=True)


def convergence_report(per_work):
    """(convergence, converged_style, converged_scale).

    The split matters, and is the correction autoanthology's first real
    run produced: only the STYLE list is evidence about voice. A converged
    scale metric usually means the form set one target, which is a
    question about range if it is anything at all, and never a question
    about repetition.

    Metrics whose mean is zero across the collection are omitted — a CV is
    undefined there, and reporting one would be noise. Needs two works.
    """
    rows = [r for r in per_work.values() if r]
    if len(rows) < 2:
        return {}, [], []
    convergence = {}
    for key in rows[0]:
        values = [r[key] for r in rows if key in r]
        if len(values) < 2:
            continue
        mean = statistics.mean(values)
        if mean == 0:
            continue
        convergence[key] = round(statistics.stdev(values) / abs(mean), 3)
    hits = [k for k, cv in convergence.items() if cv < CONVERGENCE_THRESHOLD]
    return (convergence,
            sorted(k for k in hits if k not in SCALE_METRICS),
            sorted(k for k in hits if k in SCALE_METRICS))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quiet", action="store_true",
                        help="write the file without printing a summary")
    args = parser.parse_args(argv)

    project = Path.cwd()
    try:
        state = structure.read_state(project)
        if not structure.is_container(state):
            print("not a container project — convergence is a measurement "
                  "ACROSS works, and a standalone project has one",
                  file=sys.stderr)
            return 2
        children = structure.ordered_children(project, state)
    except structure.StructureError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    wells = voice_fingerprint.load_wells()
    per_work = {child.name: analyze_work(child, wells) for child in children}
    drafted = {name: row for name, row in per_work.items() if row}

    convergence, style, scale = convergence_report(drafted)
    report = {
        "works": list(per_work),
        "drafted": sorted(drafted),
        "undrafted": sorted(set(per_work) - set(drafted)),
        "per_work": drafted,
        "convergence": convergence,
        "converged_metrics": style,
        "converged_scale_metrics": scale,
        "threshold": CONVERGENCE_THRESHOLD,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(report, indent=2), encoding="utf-8")

    if not args.quiet:
        print(f"{len(drafted)} of {len(per_work)} works drafted -> {OUTPUT}")
        if len(drafted) < 2:
            print("  need two drafted works before convergence means anything")
        for key in style:
            print(f"  CONVERGED {key}: cv={convergence[key]}")
        for key in scale:
            print(f"  (scale) {key}: cv={convergence[key]} — expected; the "
                  "form set one target")
        if drafted and not style:
            print("  no style metric converged")
    return 0


if __name__ == "__main__":
    sys.exit(main())
