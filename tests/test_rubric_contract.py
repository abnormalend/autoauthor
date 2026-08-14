import re
from pathlib import Path

RUBRICS = Path(__file__).parent.parent / "plugin/autoauthor/shared/rubrics"

# A rubric that emits an aggregate `<something>_score` in its JSON schema
# is computing a mean, and a mean reported as an integer is a defect with
# a history: 0.2.0 fixed it for `foundation.md`, and the first real
# drafting run found `chapter.md` still doing it — four chapters whose
# dimensions averaged 7.22, 7.33, 7.22 and 7.00 all reported 7.0.
AGGREGATE_RE = re.compile(r'"([a-z_]*score)": N')
NOT_AGGREGATES = {"score"}   # a per-dimension score, which IS an integer


def aggregates(text):
    return {m for m in AGGREGATE_RE.findall(text) if m not in NOT_AGGREGATES}


def test_every_computed_score_is_reported_as_a_decimal():
    """The defect this catches is silent and it degrades the gates.

    Drafting compares against a fractional bar. Revision stops on a CHANGE
    of less than 0.5 across two cycles — a test that cannot work on
    integers, because an integer cannot express a change smaller than 1.
    """
    checked = 0
    for path in sorted(RUBRICS.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        found = aggregates(text)
        if not found:
            continue
        checked += 1
        assert "NUMERIC FORMAT" in text, (
            f"{path.name} emits {sorted(found)} but never says how to "
            "format it; a judge will round to an integer")
        assert "DECIMAL" in text, f"{path.name} does not require decimals"
    assert checked >= 5, f"only {checked} scoring rubrics found"


def test_the_guard_would_notice_a_new_rubric_that_forgot():
    assert aggregates('"work_score": N') == {"work_score"}
    assert aggregates('"score": N') == set()
