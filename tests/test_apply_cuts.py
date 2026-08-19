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


def test_protect_file_partial_overlap_is_a_hit(tmp_path):
    """A cut whose tail is the head of a protected line (or vice versa) by
    20+ chars takes the protected line's opening clause with it."""
    setup_project(tmp_path)
    # Protected line begins inside the OVER-EXPLAIN quote and runs past its end.
    (tmp_path / "edit_logs/protected.md").write_text(
        "what he was only now beginning to understand. \"Late,\" said the chancellor.\n"
    )
    result = run_in(tmp_path, "3", "--protect-file", "edit_logs/protected.md")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "PROTECT" in result.stdout
    assert "He realized then" in (tmp_path / "chapters/ch_03.md").read_text()


def test_protect_file_quote_that_is_a_fragment_of_a_protected_line(tmp_path):
    """A REDUNDANT cut that quotes part of a protected sentence would remove
    part of it; that is a hit in the q-in-p direction. Curly quotes on
    either side are normalised."""
    (tmp_path / "chapters").mkdir()
    (tmp_path / "edit_logs").mkdir()
    (tmp_path / "chapters/ch_03.md").write_text(CHAPTER)
    cuts = {
        "cuts": [{
            "quote": "so that he would feel the full weight of his isolation",
            "type": "REDUNDANT", "reason": "restates", "action": "CUT", "rewrite": None,
        }],
        "overall_fat_percentage": 20,
    }
    (tmp_path / "edit_logs/ch03_cuts.json").write_text(json.dumps(cuts))
    (tmp_path / "edit_logs/protected.md").write_text(
        "He realized then that the meeting had been arranged specifically so "
        "that he would feel the full weight of his isolation, and that every "
        "person in the room already knew what he was only now beginning to "
        "understand.\n"
    )
    result = run_in(tmp_path, "3", "--protect-file", "edit_logs/protected.md")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "PROTECT [REDUNDANT]" in result.stdout
    assert "full weight of his isolation" in (tmp_path / "chapters/ch_03.md").read_text()


def test_protect_file_curly_quotes_normalise():
    sys.path.insert(0, str(SCRIPT.parent))
    import apply_cuts
    hit = apply_cuts.protected_by(
        "“Late,” said the chancellor. He didn’t look up from the ledger.",
        ['"Late," said the chancellor. He didn\'t look up from the ledger.'],
    )
    assert hit is not None


def test_protect_file_missing_path_is_a_usage_error_not_a_traceback(tmp_path):
    setup_project(tmp_path)
    result = run_in(tmp_path, "3", "--protect-file", "edit_logs/nope.md")
    assert result.returncode == 2
    assert "Traceback" not in result.stderr
    assert "not found" in result.stderr
    assert "Diagnose step 2" in result.stderr


def test_all_warns_when_cuts_files_span_more_than_twelve_hours(tmp_path):
    import os
    import time
    setup_project(tmp_path)
    (tmp_path / "chapters/ch_04.md").write_text(CHAPTER)
    stale = tmp_path / "edit_logs/ch04_cuts.json"
    stale.write_text(json.dumps(CUTS))
    old = time.time() - 13 * 3600
    os.utime(stale, (old, old))
    result = run_in(tmp_path, "all", "--dry-run")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "span more than 12h" in result.stderr
    assert "Diagnose step 3" in result.stderr


def test_all_does_not_warn_when_cuts_files_are_from_one_run(tmp_path):
    setup_project(tmp_path)
    (tmp_path / "chapters/ch_04.md").write_text(CHAPTER)
    (tmp_path / "edit_logs/ch04_cuts.json").write_text(json.dumps(CUTS))
    result = run_in(tmp_path, "all", "--dry-run")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "span more than" not in result.stderr


def test_verify_protected_reports_lines_no_longer_in_any_chapter(tmp_path):
    setup_project(tmp_path)
    (tmp_path / "edit_logs/protected.md").write_text(
        "# ch03\nThe council chamber smelled of tallow and wet wool.\n"
        "This sentence was reworded out of existence.\n")
    result = run_in(tmp_path, "--verify-protected", "edit_logs/protected.md")
    assert result.returncode == 1, result.stdout + result.stderr
    assert "NOT FOUND" in result.stdout
    assert "reworded out of existence" in result.stdout
    assert "tallow and wet wool" not in result.stdout.split("NOT FOUND", 1)[1]


def test_verify_protected_exits_zero_when_every_line_is_present(tmp_path):
    setup_project(tmp_path)
    (tmp_path / "edit_logs/protected.md").write_text(
        "The council chamber smelled of tallow and wet wool.\n")
    result = run_in(tmp_path, "--verify-protected", "edit_logs/protected.md")
    assert result.returncode == 0, result.stdout + result.stderr


def test_rewrite_skip_message_prints_the_rewrite(tmp_path):
    import json
    setup_project(tmp_path)
    cuts = json.loads((tmp_path / "edit_logs/ch03_cuts.json").read_text())
    cuts["cuts"][0]["action"] = "REWRITE"
    cuts["cuts"][0]["rewrite"] = "He realized the meeting had been arranged."
    (tmp_path / "edit_logs/ch03_cuts.json").write_text(json.dumps(cuts))
    result = run_in(tmp_path, "3")
    assert "REWRITE cuts are applied by hand" in result.stdout
    assert "He realized the meeting had been arranged." in result.stdout
