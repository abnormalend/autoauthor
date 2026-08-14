"""Computing the aggregate instead of asking a judge for it.

Every scoring rubric asks its judge for a mean alongside the dimensions,
and a mean is arithmetic. A live revision cycle returned dimensions of
7, 8, 7, 7, 7, 8, 8 — 7.43 — with `work_score: 7`, against a phase that
stops when that number moves less than 0.5. Two rounds of prompt wording
made the judge report it correctly; this removes the class.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).parent.parent / "plugin/autoauthor/shared/scripts"
sys.path.insert(0, str(SCRIPTS))

import score_verdict  # noqa: E402

CLI = SCRIPTS / "score_verdict.py"

FLAT = {k: {"score": s, "note": "..."} for k, s in (
    ("arc_completion", 7), ("pacing_curve", 7), ("theme_coherence", 8),
    ("foreshadowing_resolution", 8), ("pillar_consistency", 7),
    ("voice_consistency", 8), ("overall_engagement", 7))}

WEIGHTS = {"pillar": 40, "character": 25, "structure": 25, "craft": 10}


def nested(pillar, character, structure, craft):
    def block(scores):
        return {f"d{i}": {"score": s} for i, s in enumerate(scores)}
    return {"pillar": block(pillar), "character": block(character),
            "structure": block(structure), "craft": block(craft)}


def test_the_case_this_was_built_for():
    """The exact numbers from the live cycle."""
    value, detail = score_verdict.compute(dict(FLAT, work_score=7))
    assert value == 7.43
    assert detail["dimensions"]["arc_completion"] == 7


def test_a_flat_verdict_is_an_unweighted_mean():
    value, _ = score_verdict.compute({"a": {"score": 6}, "b": {"score": 9}})
    assert value == 7.5


def test_a_weighted_verdict_weights_the_category_means_not_the_dimensions():
    """A category with three dimensions does not thereby get three times
    the say — that is what the weight is for, and averaging the flat list
    would silently let dimension COUNT decide the outcome."""
    verdict = nested([8, 8, 8], [4], [4], [4])
    value, detail = score_verdict.compute(verdict, WEIGHTS)
    assert detail["category_means"] == {"pillar": 8.0, "character": 4.0,
                                        "structure": 4.0, "craft": 4.0}
    assert value == round((8 * 40 + 4 * 25 + 4 * 25 + 4 * 10) / 100, 2)


def test_a_weighted_verdict_without_weights_says_so():
    with pytest.raises(ValueError, match="weights are needed"):
        score_verdict.compute(nested([8], [8], [8], [8]))


def test_a_dropped_category_does_not_break_the_weighting():
    """A form may empty a category. The remaining weights renormalize
    rather than the mean being computed against a share that is not
    there."""
    verdict = nested([8], [6], [], [])
    value, detail = score_verdict.compute(verdict, WEIGHTS)
    assert set(detail["category_means"]) == {"pillar", "character"}
    assert value == round((8 * 40 + 6 * 25) / 65, 2)


def test_a_verdict_with_no_dimensions_is_an_error():
    with pytest.raises(ValueError, match="no dimension scores"):
        score_verdict.compute({"note": "nothing here"})


def test_the_reported_value_is_found_whatever_the_rubric_calls_it():
    for key in score_verdict.AGGREGATE_KEYS:
        assert score_verdict.reported({key: 7.43}) == (key, 7.43)
    assert score_verdict.reported({"weakest_dimension": "x"}) == (None, None)


# --- the CLI, which is what a skill invokes --------------------------------

def run(tmp_path, verdict, *args):
    path = tmp_path / "v.json"
    path.write_text(json.dumps(verdict), encoding="utf-8")
    return subprocess.run([sys.executable, str(CLI), str(path), *args],
                          capture_output=True, text=True)


def test_agreement_exits_zero(tmp_path):
    result = run(tmp_path, dict(FLAT, work_score=7.43))
    assert result.returncode == 0
    assert "computed: 7.43" in result.stdout


def test_disagreement_exits_one_and_names_the_number_to_record(tmp_path):
    result = run(tmp_path, dict(FLAT, work_score=7))
    assert result.returncode == 1
    assert "record 7.43, not 7.0" in result.stderr


def test_rounding_in_the_last_place_is_not_a_disagreement(tmp_path):
    """Judges report two decimals; 7.43 against a true 7.428 is agreement,
    not a defect to flag."""
    assert run(tmp_path, dict(FLAT, work_score=7.43)).returncode == 0


def test_a_verdict_with_no_aggregate_still_computes(tmp_path):
    """Useful on its own: the skill can record a number the judge never
    reported."""
    result = run(tmp_path, FLAT)
    assert result.returncode == 0
    assert "reported: none" in result.stdout


def test_quiet_prints_only_the_number(tmp_path):
    result = run(tmp_path, dict(FLAT, work_score=7), "--quiet")
    assert result.stdout.strip() == "7.43"


def test_an_unreadable_file_exits_two(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text("not json", encoding="utf-8")
    result = subprocess.run([sys.executable, str(CLI), str(path)],
                            capture_output=True, text=True)
    assert result.returncode == 2
