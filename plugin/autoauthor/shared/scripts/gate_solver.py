"""Gate reachability arithmetic for genre packs.

TEMPLATE.md states the calibration policy in prose and then asks the pack
author to check it by hand:

    Reject any design where two caps firing requires a 9. One cap should
    leave the gate clearly reachable; two should be hard but possible;
    three should block, because three real defects ought to.

This module inverts that. The author declares the caps as data — `[cap N]`
on each pillar dimension — and this computes the highest gate the design
can actually support. A pack whose ceiling sits below the pipeline's gate
is arithmetically unreachable: no book, however good, can exit the
foundation loop, because the arithmetic and not the writing is what stops
it.

That defect has shipped twice. One pack released with five dimensions
capped at 4, 4 and 6, a ceiling of 6.3 against a pipeline gating at 7.0;
another with four dimensions and three caps at 5, ceiling 6.4. The first
took a subagent reading criteria prose across five dimensions to find.
This module finds both in microseconds, and tests/test_gate_solver.py
pins the arithmetic for each.

Pure arithmetic and no imports, so it can be read and trusted on its own.
The CLI at the bottom imports the pack parser lazily, which is also what
keeps genre_pack.py free to import this module without a cycle.
"""

# The pipeline's foundation gate on `pillar_score`. Mirrored from
# skills/foundation/SKILL.md, which is where the loop actually reads it;
# a pack cannot be judged reachable or not without knowing the bar.
PILLAR_GATE = 7.0

# Above this, integer scores force a 9 out of the uncapped dimensions, and
# this rubric reserves 9+ for work where the judge "genuinely struggled to
# find flaws". An average of exactly 8.0 is fine — three 8s reach it.
POLICY_CEILING = 8.0

# A cap is a ceiling the criteria can force a dimension down to. 10 is not
# a cap (it constrains nothing) and 0 would make the dimension unscorable.
MIN_CAP, MAX_CAP = 1, 9

# Gates worth searching, in tenths. The top is 9.9 rather than 10.0 because
# a gate of 10.0 is unreachable by definition — scores are integers capped
# at 10 and the gate is strict.
GATE_TENTHS = range(40, 100)

INFEASIBLE = float("inf")


def required(n_dimensions, caps, gate):
    """What the uncapped dimensions must average, per number of caps firing.

    Returns `(need, averages)` where `need` is the smallest integer pillar
    sum that clears `gate`, and `averages[k - 1]` is the average the
    remaining dimensions must reach when the `k` lowest caps fire together.

    The k lowest caps are used because they are the worst case: a design
    that survives its two most punishing caps co-firing survives any other
    pair.

    Two boundary values in `averages`:

    - `0.0` — every dimension is capped and the caps alone already clear
      the gate. Nothing is required of anyone, because there is no one
      left to require it of.
    - `inf` — every dimension is capped and the caps do not clear the
      gate, so no score anywhere can rescue it.

    Arithmetic runs in tenths rather than on floats. `int(7.4 * 5)` is one
    unlucky representation away from 36 instead of 37, and the resulting
    off-by-one would move a pack's ceiling silently — which is the exact
    class of defect this module exists to catch.
    """
    need = round(gate * 10) * n_dimensions // 10 + 1
    averages = []
    for k in range(1, len(caps) + 1):
        capped = sum(sorted(caps)[:k])
        rest = n_dimensions - k
        if rest > 0:
            averages.append((need - capped) / rest)
        else:
            averages.append(0.0 if capped >= need else INFEASIBLE)
    return need, averages


def max_gate(n_dimensions, caps, policy_ceiling=POLICY_CEILING):
    """The highest gate, in 0.1 steps, that this design can support.

    Applies TEMPLATE's policy: one cap firing must stay reachable and two
    must require no 9. Three or more are deliberately not checked — three
    real defects are supposed to block the book.

    Returns None when no gate in `GATE_TENTHS` qualifies, which means the
    design cannot be rescued by lowering the gate and the dimensions
    themselves have to change. A pack with no caps at all returns the top
    of the range, because nothing constrains it.
    """
    best = None
    for tenths in GATE_TENTHS:
        gate = tenths / 10
        _, averages = required(n_dimensions, caps, gate)
        # averages[:2] covers all three cases without branching: no caps
        # (nothing to check), one cap, or two-or-more.
        if all(avg <= policy_ceiling for avg in averages[:2]):
            best = gate
    return best


def unreachable(n_dimensions, caps, gate=PILLAR_GATE,
                policy_ceiling=POLICY_CEILING):
    """Explain why `gate` is out of reach for this design, or return None.

    The message names the arithmetic AND the remedy, because an author who
    is told only "unreachable" reaches for the thing TEMPLATE explicitly
    warns against — softening the cap that was doing the work.
    """
    if not caps:
        return None
    ceiling = max_gate(n_dimensions, caps, policy_ceiling)
    if ceiling is not None and ceiling >= gate:
        return None

    need, averages = required(n_dimensions, caps, gate)
    shown = format_caps(caps)
    parts = [f"pillar gate {gate} is unreachable: {n_dimensions} dimension(s) "
             f"with {shown}, so the pillar sum must reach {need}"]
    for k, avg in enumerate(averages[:2], start=1):
        if avg <= policy_ceiling:
            continue
        rest = n_dimensions - k
        if rest <= 0:
            parts.append(
                f"{k} cap(s) firing leaves no dimension able to make up the "
                f"difference")
        else:
            parts.append(
                f"{k} cap(s) firing requires the remaining {rest} to average "
                f"{avg:.2f}, and scores are integers")
    parts.append(
        f"the highest gate this design supports is "
        f"{'none in 4.0-9.9' if ceiling is None else ceiling}")
    parts.append(
        "add a dimension rather than softening a cap — see TEMPLATE.md, "
        "'Dimension count is the lever, not cap severity'")
    return "; ".join(parts)


def format_caps(caps):
    """'caps at 5, 5, 6' — lowest first, matching the order they fire in."""
    if not caps:
        return "no caps"
    return "caps at " + ", ".join(str(c) for c in sorted(caps))


def _main(argv):
    """Report the ceiling for each pack file named on the command line."""
    from pathlib import Path

    import genre_pack

    paths = [Path(a) for a in argv[1:]]
    if not paths:
        print(f"usage: {Path(argv[0]).name} <pack.md> [pack.md ...]")
        return 2

    failed = False
    for path in sorted(paths):
        # The advertised glob over a genres/ directory sweeps up TEMPLATE.md,
        # which has no frontmatter and is not a pack. Same skip
        # validate_genre_pack.py makes, silently here because this command
        # is a report rather than a check of what you named.
        if path.stem == genre_pack.TEMPLATE_STEM:
            continue
        try:
            pack = genre_pack.parse_pack(path)
        except genre_pack.PackError as e:
            print(f"{path}: {e}")
            failed = True
            continue
        if not pack["dimensions"]:
            continue
        # One row per band the pack actually supports. A band drops
        # dimensions, which shrinks the divisor the caps are calibrated
        # against, so each is a separate design and gets its own ceiling.
        for band in genre_pack.BANDS:
            dimensions, caps, _, _, source = genre_pack.band_criteria(
                pack, band)
            if band != "extended" and source is None:
                continue
            caps = sorted(caps.values())
            ceiling = max_gate(len(dimensions), caps)
            _, averages = required(len(dimensions), caps, PILLAR_GATE)
            at_gate = ", ".join(f"k={k}:{avg:.2f}"
                                for k, avg in enumerate(averages[:2], start=1))
            # Only the default design is checked against the pipeline's
            # floor. A band's gate comes from the FORM beside it, which is
            # not known here — the resolver checks that pairing.
            problem = unreachable(len(dimensions), caps) if band == "extended" \
                else None
            mark = "FAIL" if problem else "ok  "
            label = f"{path.stem}/{band}"
            print(f"{mark} {label:32} N={len(dimensions)} "
                  f"{format_caps(caps):28} [{at_gate}]  ceiling {ceiling}")
            if problem:
                print(f"       {problem}")
                failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    import sys

    sys.exit(_main(sys.argv))
