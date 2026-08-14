import re
from pathlib import Path

RUBRICS = Path(__file__).parent.parent / "plugin/autoauthor/shared/rubrics"

# A rubric that emits an aggregate `<something>_score` in its JSON schema
# is computing a mean, and a mean reported as an integer is a defect with
# a history: 0.2.0 fixed it for `foundation.md`, and the first real
# drafting run found `chapter.md` still doing it — four chapters whose
# dimensions averaged 7.22, 7.33, 7.22 and 7.00 all reported 7.0.
AGGREGATE_RE = re.compile(r'"([a-z_]*score)": N(?:\.NN)?')
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
        # The type has to be IN THE SCHEMA, not only in a paragraph after
        # it. A live run proved the difference: full-novel.md carried the
        # instruction as its closing paragraph, the judge read the file
        # and still returned `"work_score": 7` for dimensions averaging
        # 7.43. A judge filling a template copies the template's token.
        for key in found:
            assert f'"{key}": N.NN' in text, (
                f'{path.name} writes "{key}": N in its JSON schema; a '
                "trailing paragraph does not override the token a judge "
                "is copying")
    assert checked >= 5, f"only {checked} scoring rubrics found"


def test_the_guard_would_notice_a_new_rubric_that_forgot():
    assert aggregates('"work_score": N') == {"work_score"}
    assert aggregates('"work_score": N.NN') == {"work_score"}
    assert aggregates('"score": N') == set()
