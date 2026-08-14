#!/usr/bin/env python3
"""Compute a verdict's aggregate score from its dimension scores.

  python3 score_verdict.py eval_logs/<file>.json
  python3 score_verdict.py <file>.json --weights '{"pillar":20,...}'

Every scoring rubric asks its judge for an aggregate alongside the
dimensions, and the aggregate is a MEAN OF THE DIMENSIONS — arithmetic,
not judgement. A judge is qualified to score a dimension and has no
particular claim to averaging seven of them, so this does the averaging
and reports any disagreement.

The need is not hypothetical. A live revision cycle returned dimension
scores of 7, 8, 7, 7, 7, 8, 8 — mean 7.43 — with `work_score: 7`. The
revision phase stops when that number changes by less than 0.5 across two
cycles, so the reported figure was wrong by most of the threshold it was
about to be compared against. Two rounds of prompt-wording fixes made the
judge report it correctly; computing it removes the class of defect
instead of asking again more firmly.

Exit 0 when the reported aggregate matches the computed one, 1 when they
disagree by more than TOLERANCE, 2 on a file this cannot read. The
computed value is printed either way, and it is the one to record.
"""
import argparse
import json
import sys
from pathlib import Path

# Judges report two decimals, so anything larger than half a unit in the
# last place is a real disagreement rather than a rounding artefact.
TOLERANCE = 0.005

# The aggregate key each rubric emits. A verdict carrying none of these is
# not a scoring verdict.
AGGREGATE_KEYS = ("overall_score", "work_score", "collection_score",
                  "series_score")

# Foundation's verdict nests dimensions under weighted categories; every
# other rubric puts them at the top level. The nesting is the reason this
# takes a --weights option at all.
WEIGHTED_CATEGORIES = ("pillar", "character", "structure", "craft")


def dimension_scores(node):
    """{key: score} for the {"score": N, ...} entries directly under node."""
    return {k: v["score"] for k, v in node.items()
            if isinstance(v, dict) and isinstance(v.get("score"), (int, float))}


def compute(verdict, weights=None):
    """(computed_aggregate, detail).

    Flat verdicts are an unweighted mean of their dimensions. A verdict
    with weighted categories is the weighted mean of the category means —
    which is what makes a category's weight mean anything, and which is
    also why an empty category would make the result undefined rather
    than merely odd.
    """
    categories = {c: dimension_scores(verdict[c]) for c in WEIGHTED_CATEGORIES
                  if isinstance(verdict.get(c), dict)}
    categories = {c: d for c, d in categories.items() if d}

    if categories:
        if not weights:
            raise ValueError(
                "this verdict has weighted categories "
                f"({', '.join(sorted(categories))}) so the weights are "
                "needed; pass --weights with the primary pack's weights "
                "object from resolve_genre.py")
        missing = [c for c in categories if c not in weights]
        if missing:
            raise ValueError(f"no weight given for {', '.join(missing)}")
        means = {c: sum(d.values()) / len(d) for c, d in categories.items()}
        total = sum(weights[c] for c in means)
        if total <= 0:
            raise ValueError("weights for the scored categories sum to zero")
        value = sum(means[c] * weights[c] for c in means) / total
        return round(value, 2), {"category_means": {c: round(m, 2)
                                                    for c, m in means.items()},
                                 "weights_used": {c: weights[c] for c in means}}

    flat = dimension_scores(verdict)
    if not flat:
        raise ValueError("no dimension scores found in this verdict")
    return round(sum(flat.values()) / len(flat), 2), {"dimensions": flat}


def reported(verdict):
    for key in AGGREGATE_KEYS:
        if key in verdict and isinstance(verdict[key], (int, float)):
            return key, float(verdict[key])
    return None, None


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("verdict", help="path to an eval JSON")
    parser.add_argument("--weights", help="JSON weights object, for a "
                                          "verdict with scored categories")
    parser.add_argument("--quiet", action="store_true",
                        help="print only the computed value")
    args = parser.parse_args(argv)

    try:
        verdict = json.loads(Path(args.verdict).read_text(encoding="utf-8"))
        weights = json.loads(args.weights) if args.weights else None
        value, detail = compute(verdict, weights)
    except (OSError, json.JSONDecodeError, ValueError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    key, said = reported(verdict)
    if args.quiet:
        print(f"{value:.2f}")
    else:
        for label, values in detail.items():
            print(f"{label}: {values}")
        print(f"computed: {value:.2f}")
        print(f"reported: {key} = {said}" if key else "reported: none")

    if said is not None and abs(said - value) > TOLERANCE:
        print(f"DISAGREES by {abs(said - value):.2f} — record {value:.2f}, "
              f"not {said}. The aggregate is the mean of the dimensions, "
              "and the dimensions are what the judge actually assessed.",
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
