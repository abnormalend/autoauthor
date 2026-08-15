"""A foreshadowing ledger may not cite a chapter that does not carry the plant.

The shakedown fixtures are judged instruments, and a ledger row pointing at a
chapter whose entry does not contain what the row claims is the defect judges
kept finding in them: `F7` cited a credit rule ch 3 never recited, `F8` quoted
a line of Halim's that existed only in the cell citing it. Both were real, and
both survived nine clean-room judgings before anyone said so.

Fixing the class rather than the two instances found a third — `F2` credited
Turi's "It isn't gone, boy. It's in me." to ch 2, where he says his other
aphorism instead — which twelve judges had missed. That is the argument for a
mechanical check: a judge reads for meaning and forgives a citation, and this
does not.

Deliberately narrow. It verifies only what can be verified without reading for
sense: that a quoted line attributed to a chapter appears in that chapter, and
that every chapter a row cites exists. Whether an unquoted recurrence is
*really* present in the chapter it names is a semantic question, judges do
raise it, and a regex would either miss it or cry wolf. See
`test_required_reading_is_clean.py` for the same reasoning about scope.
"""
import re
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures/shakedown"

# `**ch 3 — 7% — Sahra — ...` (romantasy) and `### Ch 3: "Title" — ...`
# (dark-romance). The two sets were written by different authors and neither
# format is more correct than the other, so the check reads both.
CHAPTER_RE = re.compile(r"^(?:#{2,4}\s+Ch|\*\*ch)\s*(\d+)\b(.*?)(?=^(?:#{2,4}\s+Ch|\*\*ch)\s*\d+\b|\Z)",
                        re.M | re.S | re.I)

# A ledger row keyed either `| F8 |` or `| 12 |`. The letter suffix matters:
# rows inserted between existing ones are keyed `F8b` so the numbering stays
# stable, and a pattern without it silently skipped the newest row in the set.
LEDGER_ROW_RE = re.compile(r"^\|\s*(F?\d+[a-z]?)\s*\|")

# Chapter columns: plant, recurrences, payoff. Never the thread's name, which
# carries numbers of its own — "Article 11", "clause 9", "2,306 carries" — and
# would otherwise be read as chapter citations.
CHAPTER_COLUMNS = (3, 4, 5)

QUOTED_ATTRIBUTION_RE = re.compile(r"ch (\d+)[^|)]*?\*\"([^\"]{6,120})\"\*", re.I)


def flatten(text):
    """Chapters are hard-wrapped, so a quoted line straddles newlines.

    Matching raw text reported an already-fixed row as still broken, which is
    the same defect 0.16.0 fixed in `slop_score.py`. Collapse first, always.
    """
    return re.sub(r"\s+", " ", text).lower()


def outlines():
    return [pytest.param(path, id=path.parent.name)
            for path in sorted(FIXTURES.glob("*/outline.md"))]


def parse(path):
    text = path.read_text(encoding="utf-8")
    chapters = {int(n): flatten(body) for n, body in CHAPTER_RE.findall(text)}
    rows = [line for line in text.splitlines() if LEDGER_ROW_RE.match(line)]
    return chapters, rows


def cited_chapters(row):
    """Chapter numbers a row points at, from the chapter columns only."""
    cells = row.split("|")
    for index in CHAPTER_COLUMNS:
        if index >= len(cells):
            continue
        cell = cells[index]
        # `ch 17 (...)` when the format labels them, bare `5, 12` when it does not.
        found = re.findall(r"ch (\d+)", cell, re.I) or re.findall(r"\b(\d{1,2})\b", cell)
        for number in found:
            yield int(number)


@pytest.mark.parametrize("path", outlines())
def test_every_quoted_attribution_is_in_the_chapter_it_names(path):
    chapters, rows = parse(path)
    unbacked = []
    for row in rows:
        key = row.split("|")[1].strip()
        for number, quote in QUOTED_ATTRIBUTION_RE.findall(row):
            body = chapters.get(int(number), "")
            needle = flatten(quote).strip(" .,—")[:40]
            if needle not in body:
                unbacked.append(f"{key} -> ch {number}: {quote[:60]!r}")
    assert not unbacked, (
        f"{path.parent.name}: ledger quotes their chapters do not contain — "
        f"{unbacked}")


@pytest.mark.parametrize("path", outlines())
def test_every_cited_chapter_exists(path):
    chapters, rows = parse(path)
    missing = sorted({n for row in rows for n in cited_chapters(row)
                      if n not in chapters})
    assert not missing, (
        f"{path.parent.name}: ledger cites chapters that do not exist: {missing} "
        f"(outline has 1–{max(chapters)})")


@pytest.mark.parametrize("path", outlines())
def test_the_check_is_live(path):
    """A guard that silently examines nothing is worse than no guard.

    Both fixtures are full-length planning sets with real ledgers; if either
    parse falls to zero the format has drifted and the assertions above are
    passing vacuously.
    """
    chapters, rows = parse(path)
    assert len(chapters) >= 30, f"parsed only {len(chapters)} chapters"
    assert len(rows) >= 20, f"parsed only {len(rows)} ledger rows"
    assert any(cited_chapters(row) for row in rows), "no chapter citations found"


def test_at_least_one_fixture_uses_quoted_attributions():
    """The quote check earns its place only if something exercises it.

    Only one of the two ledger formats quotes its evidence, so the corpus-wide
    count is small and a round threshold would be a number picked to pass.
    One is the honest bar: it asserts the check is exercised at all. Format
    drift in the parser is caught by `test_the_check_is_live`, which pins the
    chapter and row counts per fixture.
    """
    total = sum(len(QUOTED_ATTRIBUTION_RE.findall(row))
                for path in FIXTURES.glob("*/outline.md")
                for row in parse(path)[1])
    assert total >= 1, "no quoted attributions anywhere — the check is inert"
