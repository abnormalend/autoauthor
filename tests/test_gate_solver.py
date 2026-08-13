"""The gate arithmetic, and the two shipped defects it exists to catch.

The values pinned here come from TEMPLATE.md's own calibration table and
from the form spec's worked examples. They are arithmetic, not judgement,
so pinning them is safe in a way that pinning a judge's score never is.
"""
import json
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).parent.parent / "plugin/autoauthor/shared/scripts"
sys.path.insert(0, str(SCRIPTS))

import gate_solver  # noqa: E402


# --- TEMPLATE's own table ------------------------------------------------
#
# The prose these check has been in TEMPLATE.md since the genre work, and
# was the only statement of the policy until this module existed.

def test_four_dimensions_capped_at_five_needs_a_nine():
    """TEMPLATE: '4 dimensions, caps at 5 | 8.00 | 9.50 — needs a 10 and a 9'."""
    need, averages = gate_solver.required(4, [5, 5], 7.0)
    assert need == 29
    assert averages == [8.0, 9.5]


def test_five_dimensions_capped_at_six_is_the_safe_shape():
    """TEMPLATE: '5 dimensions, caps at 6 | 7.50 | 8.00'."""
    need, averages = gate_solver.required(5, [6, 6], 7.0)
    assert need == 36
    assert averages == [7.5, 8.0]


def test_the_lowest_caps_are_the_ones_assumed_to_co_fire():
    """Worst case, not first-declared: a 4 and a 6 fire as 4 then 4+6."""
    _, averages = gate_solver.required(5, [6, 4, 6, 4], 7.0)
    assert averages[0] == pytest.approx((36 - 4) / 4)
    assert averages[1] == pytest.approx((36 - 8) / 3)


# --- The ceilings the form spec worked out by hand ------------------------

@pytest.mark.parametrize("label,n,caps,expected", [
    ("fantasy, extended, after the 0.3.0 fix", 5, [6, 6], 7.1),
    ("fantasy, extended, AS FIRST SHIPPED", 5, [4, 4, 6], 6.3),
    ("romantasy, extended", 6, [6, 6, 6], 7.3),
    ("fantasy, compressed, 2 dimensions", 2, [6], 6.9),
    ("romance, compressed, 3 dimensions", 3, [6, 6], 6.6),
])
def test_max_gate_matches_the_spec_table(label, n, caps, expected):
    assert gate_solver.max_gate(n, caps) == pytest.approx(expected), label


def test_the_defect_this_module_was_built_for():
    """fantasy shipped a design gating at 7.0 that topped out at 6.3.

    This is the whole argument for structured caps. A subagent found it by
    reading criteria prose across five dimensions; the arithmetic finds it
    without reading anything.
    """
    assert gate_solver.max_gate(5, [4, 4, 6]) < gate_solver.PILLAR_GATE
    problem = gate_solver.unreachable(5, [4, 4, 6])
    assert problem is not None
    assert "9.33" in problem          # what two caps firing would demand
    assert "6.3" in problem           # the highest gate it can support
    assert "TEMPLATE" in problem      # and where to read the remedy


# --- Boundaries ----------------------------------------------------------

def test_an_average_of_exactly_eight_is_allowed():
    """Three 8s average 8.0. The policy bars a required 9, not a required 8."""
    assert gate_solver.required(5, [6, 6], 7.0)[1][1] == 8.0
    assert gate_solver.max_gate(5, [6, 6]) >= 7.0


def test_a_design_with_no_caps_is_unconstrained():
    assert gate_solver.max_gate(5, []) == pytest.approx(9.9)
    assert gate_solver.unreachable(5, []) is None


def test_caps_alone_can_clear_the_gate_when_nothing_is_left_over():
    """Every dimension capped, and the caps still clear the bar.

    The prototype in the spec returned inf here — it divided by a
    zero-sized remainder and called the result impossible, when in fact
    nothing further is required precisely because nothing is left.
    """
    # Three dimensions capped at 8, gate 7.0: need 22, caps give 24.
    _, averages = gate_solver.required(3, [8, 8, 8], 7.0)
    assert averages[2] == 0.0
    assert gate_solver.unreachable(3, [8, 8, 8]) is None


def test_caps_alone_can_also_fail_to_clear_it():
    _, averages = gate_solver.required(3, [6, 6, 6], 7.0)
    assert averages[2] == gate_solver.INFEASIBLE


def test_three_caps_firing_is_not_checked_because_it_is_meant_to_block():
    """TEMPLATE: 'three should block, because three real defects ought to.'"""
    # k=3 is infeasible here and the ceiling is still computed from k=1, k=2.
    assert gate_solver.required(5, [6, 6, 6], 7.0)[1][2] > 8.0
    assert gate_solver.max_gate(5, [6, 6, 6]) == pytest.approx(7.1)


# --- Arithmetic that must not drift --------------------------------------

def test_need_is_the_smallest_integer_that_strictly_clears_the_gate():
    """Guards the tenths arithmetic against float representation error.

    int(7.4 * 5) is one unlucky float away from 36 instead of 37, and that
    off-by-one would move a pack's ceiling silently.
    """
    for tenths in gate_solver.GATE_TENTHS:
        gate = tenths / 10
        for n in range(1, 9):
            need, _ = gate_solver.required(n, [], gate)
            assert need > gate * n
            assert need - 1 <= gate * n


def test_raising_the_gate_never_makes_a_design_easier():
    previous = 0.0
    for tenths in gate_solver.GATE_TENTHS:
        _, averages = gate_solver.required(5, [6, 6], tenths / 10)
        assert averages[0] >= previous
        previous = averages[0]


def test_max_gate_returns_none_when_no_gate_in_range_works():
    """Two dimensions, both capped low: even 4.0 cannot be reached."""
    assert gate_solver.max_gate(2, [1, 1]) is None
    problem = gate_solver.unreachable(2, [1, 1])
    assert "no dimension able to make up the difference" in problem


def test_the_pipeline_gate_is_the_one_that_is_actually_enforced():
    """PILLAR_GATE is mirrored, not owned — by two files, and this is the
    only thing keeping the three in step.

    It is the floor every pack must be able to reach at authoring time,
    when no form is in play. The `novel` form declares the same number as
    the gate the loop exits on, and the foundation skill states it. A form
    that gates HIGHER than a genre can reach is caught separately, at
    resolve time, where both packs are known.
    """
    plugin = Path(__file__).parent.parent / "plugin/autoauthor"
    skill = (plugin / "skills/foundation/SKILL.md").read_text(encoding="utf-8")
    assert f"pillar_score > {gate_solver.PILLAR_GATE}" in skill

    novel = json.loads((plugin / "shared/forms/novel.md")
                       .read_text(encoding="utf-8").split("---")[1])
    assert novel["gate"]["pillar"] == gate_solver.PILLAR_GATE
