import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "plugin/autoauthor/shared/scripts/apply_cuts.py"

CHAPTER = """# Chapter 3: The Meeting

The council chamber smelled of tallow and wet wool. Aldric took his seat
without being asked, which was itself an answer to the question nobody
had voiced yet.

He realized then that the meeting had been arranged specifically so that
he would feel the full weight of his isolation, and that every person in
the room already knew what he was only now beginning to understand.

"Late," said the chancellor.
"""

CUTS = {
    "cuts": [
        {
            "quote": "He realized then that the meeting had been arranged specifically so that he would feel the full weight of his isolation, and that every person in the room already knew what he was only now beginning to understand.",
            "type": "OVER-EXPLAIN",
            "reason": "narrator explains what the scene already shows",
            "action": "CUT",
            "rewrite": None,
        },
        {
            "quote": "tallow and wet wool",
            "type": "FAT",
            "reason": "too short a quote to apply safely",
            "action": "CUT",
            "rewrite": None,
        },
    ],
    "overall_fat_percentage": 20,
}


def setup_project(tmp_path):
    (tmp_path / "chapters").mkdir()
    (tmp_path / "edit_logs").mkdir()
    (tmp_path / "chapters/ch_03.md").write_text(CHAPTER)
    (tmp_path / "edit_logs/ch03_cuts.json").write_text(json.dumps(CUTS))


def run_in(tmp_path, *args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True, text=True, cwd=tmp_path,
    )


def test_applies_over_explain_cut_from_cwd(tmp_path):
    setup_project(tmp_path)
    result = run_in(tmp_path, "3", "--types", "OVER-EXPLAIN")
    assert result.returncode == 0, result.stdout + result.stderr
    text = (tmp_path / "chapters/ch_03.md").read_text()
    assert "He realized then" not in text
    assert "tallow and wet wool" in text  # FAT cut filtered out by --types


def test_short_quote_is_skipped_not_applied(tmp_path):
    setup_project(tmp_path)
    result = run_in(tmp_path, "3")
    assert result.returncode == 0, result.stdout + result.stderr
    text = (tmp_path / "chapters/ch_03.md").read_text()
    assert "tallow and wet wool" in text  # under MIN_QUOTE_LEN, skipped
    assert "He realized then" not in text  # OVER-EXPLAIN cut applied in unfiltered run


def test_dry_run_modifies_nothing(tmp_path):
    setup_project(tmp_path)
    before = (tmp_path / "chapters/ch_03.md").read_text()
    result = run_in(tmp_path, "all", "--dry-run")
    assert result.returncode == 0, result.stdout + result.stderr
    assert (tmp_path / "chapters/ch_03.md").read_text() == before


REWRITE_CUTS = {
    "cuts": [
        {
            "quote": "He realized then that the meeting had been arranged specifically so that he would feel the full weight of his isolation, and that every person in the room already knew what he was only now beginning to understand.",
            "type": "OVER-EXPLAIN",
            "reason": "narrator explains what the scene already shows; needs replacement prose, not deletion",
            "action": "REWRITE",
            "rewrite": "He said nothing. The chancellor did not look up.",
        },
    ],
    "overall_fat_percentage": 20,
}


def test_rewrite_cut_is_skipped_not_deleted(tmp_path):
    (tmp_path / "chapters").mkdir()
    (tmp_path / "edit_logs").mkdir()
    (tmp_path / "chapters/ch_03.md").write_text(CHAPTER)
    (tmp_path / "edit_logs/ch03_cuts.json").write_text(json.dumps(REWRITE_CUTS))

    result = run_in(tmp_path, "3")
    assert result.returncode == 0, result.stdout + result.stderr
    text = (tmp_path / "chapters/ch_03.md").read_text()
    assert "He realized then" in text
    assert "SKIP [REWRITE]" in result.stdout


def test_protect_file_skips_cuts_that_touch_a_protected_line(tmp_path):
    """A protected substring anywhere in a cut's quote — or a quote that is a
    fragment of a protected line — is skipped and reported, not applied.
    Whitespace is normalised on both sides."""
    setup_project(tmp_path)
    (tmp_path / "edit_logs/protected.md").write_text(
        "# protected\n"
        "\n"
        "every person in the room   already knew\n"   # ws-normalised match
    )
    result = run_in(tmp_path, "3", "--protect-file", "edit_logs/protected.md")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "PROTECT" in result.stdout
    text = (tmp_path / "chapters/ch_03.md").read_text()
    assert "He realized then" in text  # the OVER-EXPLAIN cut was NOT applied


def test_protect_file_lines_starting_with_hash_or_blank_are_ignored(tmp_path):
    setup_project(tmp_path)
    (tmp_path / "edit_logs/protected.md").write_text("# nothing here\n\n")
    result = run_in(tmp_path, "3", "--protect-file", "edit_logs/protected.md")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "He realized then" not in (tmp_path / "chapters/ch_03.md").read_text()
