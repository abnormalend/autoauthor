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
the coefficient of variation across the works.

WHICH DIRECTION IS THE DEFECT DEPENDS ON THE STRUCTURE, and this is the
one place the two containers genuinely invert. A COLLECTION wants variety:
high variance is healthy because the works are doing different things, and
a CV near zero means every work reads alike. A SERIES is one continuous
work in volumes: convergence is the goal, and the signal worth acting on
is the volume that reads unlike its neighbours.

The numbers are the same either way. The report says which reading applies
and computes the outliers a series cares about, so that neither pass has
to remember to invert the other's conclusion — which is exactly the kind
of thing a reader of a JSON file does not remember to do.

It is the mechanical half of the cross-work pass, and an accelerant rather
than a precondition — a pass that skips it makes a judge eyeball things an
instrument could have measured.
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

# How far a work has to sit from its neighbours, as a MODIFIED z-score,
# before it counts as reading unlike them. 3.5 is the Iglewicz-Hoaglin
# convention.
#
# Modified rather than ordinary, and the difference is not pedantry: an
# ordinary z-score measures the outlier against a standard deviation the
# outlier itself inflates, so with four works the largest z-score
# ARITHMETICALLY POSSIBLE is 1.5 — a check written that way can never fire
# at the sizes a series actually has. The median and the median absolute
# deviation are not moved by the point being tested.
DIVERGENCE_THRESHOLD = 3.5

# Constant relating the MAD to the standard deviation of a normal
# distribution, so the threshold reads on the familiar scale.
MAD_TO_SIGMA = 0.6745

# What a low CV means, per structure. Stated in the report rather than
# left to the reader, because the two passes read the same file and one of
# them has to invert it.
INTERPRETATION = {
    "collection": {
        "converged": "defect",
        "note": "A collection wants variety. Metrics with a low CV mean the "
                "works read alike, which is the mechanical signature of the "
                "repetition the collection pass hunts for.",
    },
    "series": {
        "converged": "goal",
        "note": "A series is one continuous work in volumes, so convergence "
                "is expected and wanted. Read `divergent_works` instead: a "
                "volume that reads unlike its neighbours is either a shift "
                "the series earned or a drift nobody noticed.",
    },
}

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


def divergent_works(per_work, threshold=DIVERGENCE_THRESHOLD):
    """Works that read unlike their neighbours, and on which metrics.

    What a series cares about and a collection does not. Returns
    {work: [metric, ...]}, naming only the metrics that put it there, so a
    reader can tell a deliberate POV change from a drift nobody noticed.

    Scale metrics are excluded for the same reason they are excluded from
    convergence: a volume longer than its neighbours is longer, not
    differently written.

    Needs three works. With two, each is the other's outlier.
    """
    rows = {name: row for name, row in per_work.items() if row}
    if len(rows) < 3:
        return {}
    out = {}
    for key in next(iter(rows.values())):
        if key in SCALE_METRICS:
            continue
        values = {name: row[key] for name, row in rows.items() if key in row}
        if len(values) < 3:
            continue
        median = statistics.median(values.values())
        deviations = [abs(v - median) for v in values.values()]
        mad = statistics.median(deviations)
        for name, value in values.items():
            if mad == 0:
                # More than half the works agree exactly. Any work that
                # does not is as divergent as the data can express.
                diverges = value != median
            else:
                diverges = MAD_TO_SIGMA * abs(value - median) / mad > threshold
            if diverges:
                out.setdefault(name, []).append(key)
    return {name: sorted(keys) for name, keys in sorted(out.items())}


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
        kind = structure.structure_of(state)
        children = structure.ordered_children(project, state)
    except structure.StructureError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    wells = voice_fingerprint.load_wells()
    per_work = {child.name: analyze_work(child, wells) for child in children}
    drafted = {name: row for name, row in per_work.items() if row}

    convergence, style, scale = convergence_report(drafted)
    divergent = divergent_works(drafted)
    report = {
        "structure": kind,
        "interpretation": INTERPRETATION[kind],
        "divergent_works": divergent,
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
        marker = ("CONVERGED" if kind == "collection"
                  else "converged (expected in a series)")
        for key in style:
            print(f"  {marker} {key}: cv={convergence[key]}")
        for key in scale:
            print(f"  (scale) {key}: cv={convergence[key]} — expected; the "
                  "form set one target")
        if drafted and not style and kind == "collection":
            print("  no style metric converged")
        for work, keys in divergent.items():
            print(f"  DIVERGENT {work}: {', '.join(keys)}"
                  + ("" if kind == "series" else " — a collection wants this"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
