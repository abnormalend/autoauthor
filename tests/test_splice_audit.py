"""Splice damage after mechanical cuts.

Six mechanical cuts in one cycle produced five defects; two were outside
the checklist the skill named, and one (trailing whitespace) survived a
whole cycle. Re-implemented three times in one session with different
checks each time — hence a script (revision findings 2026-08-17, #4).
"""
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).parent.parent / "plugin/autoauthor/shared/scripts"
sys.path.insert(0, str(SCRIPTS))

import splice_audit  # noqa: E402

CLI = SCRIPTS / "splice_audit.py"

BEFORE = """# Chapter 4

"Okay," Pua said, and put the phone down, and did not look at anyone. She called the room.

There was nobody in the room for it, not really, and her mother had gone back to work.

Kalei went past it with the cooler. Her mother worked here.

Somebody said "ho" very quietly.
"""

# The trailing space after "work." is deliberate (the trailing-whitespace
# check); it is concatenated explicitly so an editor cannot strip it.
AFTER = (
    "# Chapter 4\n"
    "\n"
    '"Okay," Pua said, and put the phone down,  She called the room.\n'
    "\n"
    "There was nobody in the room for it, , and her mother had gone back to work. \n"
    "\n"
    "Kalei went past it with the cooler. Her mother worked here.\n"
    "\n"
    ' Somebody said "ho" very quietly.\n'
)


def test_finds_each_defect_class_only_in_changed_paragraphs():
    findings = splice_audit.audit(BEFORE, AFTER)
    kinds = {f.kind for f in findings}
    assert "glued-sentence" in kinds        # ", She"
    assert "double-space" in kinds
    assert "doubled-comma" in kinds
    assert "trailing-whitespace" in kinds
    assert "leading-whitespace" in kinds
    # unchanged paragraph is not audited
    assert not any("cooler" in f.text for f in findings)


def test_proper_noun_after_comma_is_not_a_glued_sentence():
    before = "She left, Kalei said, and that was that.\n"
    after = "She left, Kalei said.\n"
    kinds = {f.kind for f in splice_audit.audit(before, after)}
    assert "glued-sentence" not in kinds   # 'Kalei' follows a comma in BEFORE


def test_terminal_punctuation_and_dangling_comma():
    before = "He waited for the answer, and it came.\n"
    after = "He waited for the answer,\n"
    kinds = {f.kind for f in splice_audit.audit(before, after)}
    assert "ends-on-comma" in kinds
    after2 = "He waited for the answer\n"
    kinds2 = {f.kind for f in splice_audit.audit(before, after2)}
    assert "no-terminal-punctuation" in kinds2


def test_cli_exits_one_on_findings_and_zero_when_clean(tmp_path):
    (tmp_path / "before").mkdir()
    (tmp_path / "chapters").mkdir()
    (tmp_path / "before/ch_04.md").write_text(BEFORE)
    (tmp_path / "chapters/ch_04.md").write_text(AFTER)
    r = subprocess.run([sys.executable, str(CLI), "chapters/ch_04.md",
                        "--before-dir", "before"],
                       capture_output=True, text=True, cwd=tmp_path)
    assert r.returncode == 1, r.stdout + r.stderr
    assert "glued-sentence" in r.stdout
    (tmp_path / "chapters/ch_04.md").write_text(BEFORE)
    r = subprocess.run([sys.executable, str(CLI), "chapters/ch_04.md",
                        "--before-dir", "before"],
                       capture_output=True, text=True, cwd=tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr


def test_cli_defaults_to_git_head_for_the_before_text(tmp_path):
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    (tmp_path / "chapters").mkdir()
    (tmp_path / "chapters/ch_04.md").write_text(BEFORE)
    subprocess.run(["git", "add", "-A"], cwd=tmp_path, check=True)
    subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t",
                    "commit", "-qm", "before"], cwd=tmp_path, check=True)
    (tmp_path / "chapters/ch_04.md").write_text(AFTER)
    r = subprocess.run([sys.executable, str(CLI), "chapters/ch_04.md"],
                       capture_output=True, text=True, cwd=tmp_path)
    assert r.returncode == 1, r.stdout + r.stderr
    assert "doubled-comma" in r.stdout


def test_cut_dialogue_tag_leaves_ends_on_comma_and_no_space_after_quote():
    before = '"Yes," she said, looking away.\n\n"No," he said, and left.\n'
    after = '"Yes,"looking away.\n\n"No,"\n'
    kinds = {f.kind for f in splice_audit.audit(before, after)}
    assert "no-space-after-quote" in kinds   # "Yes,"looking
    assert "ends-on-comma" in kinds          # "No,"
    assert "no-terminal-punctuation" not in kinds


def test_doubled_word_already_in_before_is_allowed_and_scene_breaks_skipped():
    before = "What she had had was enough, and she said so.\n\n* * *\n\nHe went home.\n"
    after = "What she had had was enough.\n\n* * *\n\nHe went went home.\n"
    findings = splice_audit.audit(before, after)
    doubled = [f for f in findings if f.kind == "doubled-word"]
    assert len(doubled) == 1 and "went went" in doubled[0].text
    assert not any("* * *" in f.text for f in findings)


def test_colon_and_dash_are_terminal():
    before = "He listed them: a, b, c.\n\nShe stopped—\n"
    after = "He listed them:\n\nShe stopped —\n"
    kinds = {f.kind for f in splice_audit.audit(before, after)}
    assert "no-terminal-punctuation" not in kinds


def test_cli_from_a_subdirectory_still_finds_the_head_text(tmp_path):
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    (tmp_path / "chapters").mkdir()
    (tmp_path / "sub").mkdir()
    (tmp_path / "chapters/ch_04.md").write_text(BEFORE)
    subprocess.run(["git", "add", "-A"], cwd=tmp_path, check=True)
    subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t",
                    "commit", "-qm", "before"], cwd=tmp_path, check=True)
    (tmp_path / "chapters/ch_04.md").write_text(AFTER)
    r = subprocess.run([sys.executable, str(CLI), "../chapters/ch_04.md"],
                       capture_output=True, text=True, cwd=tmp_path / "sub")
    assert r.returncode == 1, r.stdout + r.stderr
    assert "WARNING: no pre-cut text" not in r.stderr
    assert "cooler" not in r.stdout          # unchanged paragraph not audited
    # An absolute path resolves too.
    r = subprocess.run([sys.executable, str(CLI), str(tmp_path / "chapters/ch_04.md")],
                       capture_output=True, text=True, cwd=tmp_path / "sub")
    assert r.returncode == 1, r.stdout + r.stderr
    assert "cooler" not in r.stdout


def test_cli_warns_when_there_is_no_before_text_and_errors_on_missing_chapter(tmp_path):
    (tmp_path / "chapters").mkdir()
    (tmp_path / "chapters/ch_04.md").write_text(AFTER)
    r = subprocess.run([sys.executable, str(CLI), "chapters/ch_04.md",
                        "--before-dir", "nowhere"],
                       capture_output=True, text=True, cwd=tmp_path)
    assert "WARNING: no pre-cut text for chapters/ch_04.md" in r.stderr
    r = subprocess.run([sys.executable, str(CLI), "chapters/ch_99.md"],
                       capture_output=True, text=True, cwd=tmp_path)
    assert r.returncode == 2
    assert "Traceback" not in r.stderr
    assert "not found" in r.stderr
