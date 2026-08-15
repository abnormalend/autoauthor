import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "plugin/autoauthor/shared/scripts/slop_score.py"
FIXTURES = Path(__file__).parent / "fixtures"


def run_scorer(*args):
    result = subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def test_sloppy_chapter_scores_high_penalty():
    out = run_scorer(str(FIXTURES / "sloppy_chapter.md"))
    report = out["files"][0]
    assert report["slop_penalty"] >= 4.0
    tier1_words = [w for w, _ in report["tier1_hits"]]
    assert "delve" in tier1_words
    assert "tapestry" in tier1_words
    assert report["telling_violations"] >= 1
    assert len(report["fiction_ai_tells"]) >= 3


def test_clean_chapter_scores_low_penalty():
    out = run_scorer(str(FIXTURES / "clean_chapter.md"))
    report = out["files"][0]
    assert report["slop_penalty"] <= 1.5
    assert report["tier1_hits"] == []


def test_multiple_files_and_summary():
    out = run_scorer(str(FIXTURES / "sloppy_chapter.md"), str(FIXTURES / "clean_chapter.md"))
    assert len(out["files"]) == 2
    assert out["summary"]["worst_file"].endswith("sloppy_chapter.md")
    assert out["summary"]["max_penalty"] >= out["summary"]["mean_penalty"]


# --- genre-specific banned phrases -----------------------------------------
# Every genre grows stock diction the general tiers don't cover — erotica's
# purple euphemisms are the motivating case. Only the pack knows what it is.

def _pack_with_banned(tmp_path, *phrases):
    pack = tmp_path / "testgenre.md"
    body = "\n".join(f"- {p}" for p in phrases)
    pack.write_text(
        "---\n{}\n---\n\n## Drafting Rules\n\n25. Something.\n\n"
        f"BANNED PHRASES:\n{body}\n",
        encoding="utf-8")
    return pack


def test_genre_banned_phrases_add_penalty(tmp_path):
    pack = _pack_with_banned(tmp_path, "quivering member", "velvet heat")
    chapter = tmp_path / "ch_01.md"
    chapter.write_text("His quivering member. " * 5 + "The velvet heat. " * 3,
                       encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(chapter), "--genre-pack", str(pack)],
        capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    report = json.loads(result.stdout)["files"][0]
    assert report["slop_penalty"] > 0
    assert sorted(h[0] for h in report["genre_banned_hits"]) == [
        "quivering member", "velvet heat"]


def test_same_text_is_clean_without_the_pack(tmp_path):
    """The phrases are genre-specific — they must not be penalized globally."""
    chapter = tmp_path / "ch_01.md"
    chapter.write_text("His quivering member. " * 5, encoding="utf-8")
    result = subprocess.run([sys.executable, str(SCRIPT), str(chapter)],
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(result.stdout)["files"][0]["genre_banned_hits"] == []


def test_pack_without_banned_phrases_marker_is_fine(tmp_path):
    pack = tmp_path / "testgenre.md"
    pack.write_text("---\n{}\n---\n\n## Drafting Rules\n\n25. Something.\n",
                    encoding="utf-8")
    chapter = tmp_path / "ch_01.md"
    chapter.write_text("Ordinary prose about a river. " * 10, encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(chapter), "--genre-pack", str(pack)],
        capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    assert json.loads(result.stdout)["files"][0]["genre_banned_hits"] == []


def test_missing_pack_file_does_not_break_scoring(tmp_path):
    """Scoring must never fail because of genre resolution."""
    chapter = tmp_path / "ch_01.md"
    chapter.write_text("Ordinary prose about a river. " * 10, encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(chapter),
         "--genre-pack", str(tmp_path / "nope.md")],
        capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr


def test_banned_phrase_is_caught_across_a_line_wrap(tmp_path):
    """Chapter files are hard-wrapped prose.

    Matching against raw text missed any phrase straddling a newline, and
    the longer the phrase the likelier that was — so the scan undercounted
    exactly the florid constructions a genre banned list exists to catch.
    """
    pack = _pack_with_banned(tmp_path, "she came undone")
    chapter = tmp_path / "ch_01.md"
    chapter.write_text("She came\nundone in his arms.\n", encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(chapter), "--genre-pack", str(pack)],
        capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    hits = json.loads(result.stdout)["files"][0]["genre_banned_hits"]
    assert [h[0] for h in hits] == ["she came undone"]


def test_wrapped_and_flat_text_score_identically(tmp_path):
    pack = _pack_with_banned(tmp_path, "waves of pleasure")
    flat = tmp_path / "flat.md"
    wrapped = tmp_path / "wrapped.md"
    flat.write_text("Waves of pleasure. " * 3, encoding="utf-8")
    wrapped.write_text("Waves of\npleasure. " * 3, encoding="utf-8")
    scores = []
    for path in (flat, wrapped):
        r = subprocess.run(
            [sys.executable, str(SCRIPT), str(path), "--genre-pack", str(pack)],
            capture_output=True, text=True)
        assert r.returncode == 0, r.stdout + r.stderr
        scores.append(json.loads(r.stdout)["files"][0]["genre_banned_hits"])
    assert scores[0] == scores[1] != []


# --- Tier 1 multi-word phrases ---------------------------------------------
# `load-bearing` is a Claude tell rather than a corpus-derived one, and the
# token loop cannot see it or its phrasal cousins. See TIER1_PHRASES.

def _score(tmp_path, body, name="ch_01.md"):
    chapter = tmp_path / name
    chapter.write_text(body, encoding="utf-8")
    return run_scorer(str(chapter))["files"][0]


def test_load_bearing_is_a_tier1_hit(tmp_path):
    report = _score(tmp_path, "The lie was load-bearing. She knew it.\n")
    assert [h[0] for h in report["tier1_hits"]] == [r"load-\s*bearing"]


def test_a_literal_load_bearing_down_is_not_a_hit(tmp_path):
    """The hyphen is what makes it the metaphor.

    "the load bearing down on her" is a sentence a person writes. Penalising
    it would train the drafter away from real prose to catch a tell that
    isn't there.
    """
    report = _score(tmp_path, "She felt the load bearing down on her.\n")
    assert report["tier1_hits"] == []


def test_bears_the_load_variants_are_caught(tmp_path):
    for phrase in ("bears the load", "bear the load", "bearing the load"):
        report = _score(tmp_path, f"His silence {phrase} of the marriage.\n")
        assert [h[0] for h in report["tier1_hits"]] == [r"bear(?:s|ing)? the load"], phrase


def test_tier1_phrase_survives_a_line_break(tmp_path):
    """A hard wrap must not hide the hit — the same failure the genre list had.

    Chapters are wrapped prose, so the phrase that straddles a newline is
    the common case, not the exotic one.
    """
    wrapped = _score(tmp_path, "The lie was load-\nbearing. She knew it.\n")
    assert wrapped["tier1_hits"] != []
    split = _score(tmp_path, "His silence bears the\nload of the marriage.\n")
    assert split["tier1_hits"] != []


def test_clean_prose_has_no_phrase_hits(tmp_path):
    report = _score(tmp_path, "The wall held the roof up. She knew it.\n")
    assert report["tier1_hits"] == []
