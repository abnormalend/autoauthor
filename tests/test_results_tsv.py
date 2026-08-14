"""results.tsv's score column has one meaning, in every phase.

Found on the first end-to-end run: the review phase wrote the critic's
star rating (out of 5) into the column every other phase fills with a
0-10 score. The run read 8.25 -> 7.0 -> 7.43 -> 4.0 -> 4.5, which looks
like the book falling apart, when 4.5 stars is 9.0 and the best number in
the sequence.
"""
import re
from pathlib import Path

SKILLS = Path(__file__).parent.parent / "plugin/autoauthor/skills"

# The row format each phase documents for results.tsv. The score field is
# the third column.
ROW_RE = re.compile(r"`<ISO timestamp>\\t(?P<phase>\w[\w-]*)\\t(?P<score>[^\\]*)\\t")


def documented_rows():
    for skill in sorted(SKILLS.iterdir()):
        md = skill / "SKILL.md"
        if not md.exists():
            continue
        for m in ROW_RE.finditer(md.read_text(encoding="utf-8")):
            yield skill.name, m.group("phase"), m.group("score").strip("<> ")


def test_no_phase_writes_a_rating_on_a_different_scale():
    """A five-point rating in a ten-point column is unreadable, and the
    reader that suffers is `status`, which reports scores against gates."""
    offenders = [(s, p, f) for s, p, f in documented_rows()
                 if "star" in f.lower() and "x 2" not in f and "*2" not in f]
    assert not offenders, (
        "these phases write a star rating straight into the 0-10 score "
        f"column: {offenders}")


def test_the_review_phase_converts_and_keeps_the_raw_rating():
    review = (SKILLS / "review/SKILL.md").read_text(encoding="utf-8")
    assert "<stars x 2>" in review, "review must double the rating"
    assert "/5 stars" in review, (
        "the raw rating must survive in the description, where it carries "
        "its own units")


def test_the_guard_reads_the_rows_it_thinks_it_does():
    rows = list(documented_rows())
    assert len(rows) >= 3, f"only found {rows}"
    assert {p for _, p, _ in rows} >= {"foundation", "review"}
