"""Numbers a chapter states that no fact-bearing document states.

Eight canon defects across four drafted chapters on one run were every one
of them a clock time or a bare number derivable from the outline's fact
table (draft findings 2026-08-17, #2). Nothing mechanical looked for them.
This does not know which unmatched numbers are legitimate inventions and
does not need to: a short "not found" list a drafter eyeballs is the point.
"""
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).parent.parent / "plugin/autoauthor/shared/scripts"
sys.path.insert(0, str(SCRIPTS))

import continuity_check  # noqa: E402

CLI = SCRIPTS / "continuity_check.py"

OUTLINE = """# Outline

## Facts the story must not contradict
- The receive window opens at 04:02 and closes at 14:02.
- Pua is fifty-two at the start; Mele left in 2091.
- Eight blocks have arrived in eighty years.
"""

CHAPTER = """# Chapter 2: The Window

At 03:30 she read the front of the block. Pua had been sixty then.
Eight of them in eighty years, she thought, twenty-six characters each.
The window opened at 04:02.
"""


def test_extracts_clock_times_and_integers_and_number_words():
    found = continuity_check.numbers_in(CHAPTER)
    keys = {n.key for n in found}
    assert "03:30" in keys
    assert "04:02" in keys
    assert 60 in keys      # "sixty"
    assert 26 in keys      # "twenty-six"
    assert 80 in keys      # "eighty"


def test_reports_unmatched_numbers_and_matched_ones_separately(tmp_path):
    (tmp_path / "outline.md").write_text(OUTLINE)
    (tmp_path / "chapters").mkdir()
    (tmp_path / "chapters/ch_02.md").write_text(CHAPTER)
    result = subprocess.run(
        [sys.executable, str(CLI), "chapters/ch_02.md"],
        capture_output=True, text=True, cwd=tmp_path)
    assert result.returncode == 1, result.stdout + result.stderr
    out = result.stdout
    assert "NOT FOUND" in out
    assert "03:30" in out.split("NOT FOUND", 1)[1]
    assert "sixty" in out.split("NOT FOUND", 1)[1]
    assert "04:02" in out.split("NOT FOUND", 1)[0]   # matched


def test_clean_chapter_exits_zero(tmp_path):
    (tmp_path / "outline.md").write_text(OUTLINE)
    (tmp_path / "chapters").mkdir()
    (tmp_path / "chapters/ch_01.md").write_text(
        "# Chapter 1\n\nThe window opened at 04:02. Eight blocks in eighty years.\n")
    result = subprocess.run(
        [sys.executable, str(CLI), "chapters/ch_01.md"],
        capture_output=True, text=True, cwd=tmp_path)
    assert result.returncode == 0, result.stdout + result.stderr


def test_small_number_words_are_ignored_by_default():
    found = continuity_check.numbers_in("One of the two doors. Three keys.")
    assert {n.key for n in found} == {3}


def test_clock_keys_normalise_leading_zero():
    found = continuity_check.numbers_in("At 4:02 the window opened; at 04:02 it was open.")
    by_text = {n.text: n.key for n in found}
    assert by_text["4:02"] == "04:02"
    assert by_text["04:02"] == "04:02"


def test_words_to_int_handles_scales_and_rejects_bad_joins():
    w = continuity_check.words_to_int
    assert w("twenty-six") == 26
    assert w("two hundred") == 200
    assert w("three hundred thousand") == 300000
    assert w("one hundred and twenty") == 120
    assert w("nineteen eighty") is None
    assert w("twenty ten") is None


def test_and_joins_only_after_a_scale_word():
    found = continuity_check.numbers_in("One hundred and twenty came; eight and eighty stayed.")
    keys = {n.key for n in found}
    assert 120 in keys
    assert 88 not in keys
    assert 8 in keys and 80 in keys


def test_scene_headers_are_skipped_but_time_headings_are_read():
    found = continuity_check.numbers_in(
        "# Chapter 4: Forty\n## Scene 3\n### 14:02\n\nThe window closed at 14:02.\n")
    keys = {n.key for n in found}
    assert 4 not in keys and 40 not in keys and 3 not in keys
    assert "14:02" in keys
    assert min(n.line for n in found if n.key == "14:02") == 3


def test_missing_chapter_file_exits_two(tmp_path):
    (tmp_path / "outline.md").write_text(OUTLINE)
    result = subprocess.run(
        [sys.executable, str(CLI), "chapters/ch_09.md"],
        capture_output=True, text=True, cwd=tmp_path)
    assert result.returncode == 2, result.stdout + result.stderr
    assert "ERROR" in result.stderr
    assert "Traceback" not in result.stderr


def test_no_fact_files_exits_two(tmp_path):
    (tmp_path / "chapters").mkdir()
    (tmp_path / "chapters/ch_01.md").write_text("# Chapter 1\n\nAt 04:02.\n")
    result = subprocess.run(
        [sys.executable, str(CLI), "chapters/ch_01.md"],
        capture_output=True, text=True, cwd=tmp_path)
    assert result.returncode == 2, result.stdout + result.stderr
    assert "ERROR" in result.stderr


def test_facts_flag_overrides_defaults(tmp_path):
    (tmp_path / "outline.md").write_text("# Outline\n\n- Nothing numeric here.\n")
    (tmp_path / "notes.md").write_text("- Mele left in 2091.\n")
    (tmp_path / "chapters").mkdir()
    (tmp_path / "chapters/ch_03.md").write_text("# Ch 3\n\nShe left in 2091.\n")
    default = subprocess.run(
        [sys.executable, str(CLI), "chapters/ch_03.md"],
        capture_output=True, text=True, cwd=tmp_path)
    assert default.returncode == 1, default.stdout + default.stderr
    explicit = subprocess.run(
        [sys.executable, str(CLI), "chapters/ch_03.md", "--facts", "notes.md"],
        capture_output=True, text=True, cwd=tmp_path)
    assert explicit.returncode == 0, explicit.stdout + explicit.stderr
    assert "notes.md" in explicit.stdout


def test_reads_every_fact_bearing_file_that_exists(tmp_path):
    (tmp_path / "outline.md").write_text("# Outline\n")
    (tmp_path / "canon.md").write_text("- The ship left in 2091. (ch_01)\n")
    (tmp_path / "chapters").mkdir()
    (tmp_path / "chapters/ch_03.md").write_text("# Ch 3\n\nShe left in 2091.\n")
    result = subprocess.run(
        [sys.executable, str(CLI), "chapters/ch_03.md"],
        capture_output=True, text=True, cwd=tmp_path)
    assert result.returncode == 0, result.stdout + result.stderr
