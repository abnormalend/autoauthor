import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "plugin/autoauthor/shared/typeset/build_tex.py"

CH1 = """# Chapter 1: The Landing

The pilot's voice cut low. "Down oars," he said — quietly, as if the cliff
could hear.

The boat scraped shingle. Nobody moved.

---

Later, on the headland, Wren counted lights across the water. Five. There
should have been six.
"""


def test_builds_chapters_content_tex(tmp_path):
    (tmp_path / "chapters").mkdir()
    (tmp_path / "typeset").mkdir()
    (tmp_path / "chapters/ch_01.md").write_text(CH1)
    result = subprocess.run([sys.executable, str(SCRIPT)],
                            capture_output=True, text=True, cwd=tmp_path)
    assert result.returncode == 0, result.stdout + result.stderr
    out = (tmp_path / "typeset/chapters_content.tex").read_text()
    assert "\\chapter{The Landing}" in out
    assert "\\scenebreak" in out                     # --- became a scene break
    assert "\\lettrine" in out                       # drop cap applied
    assert "``Down oars,''" in out                   # straight quotes converted


def test_stray_chapter_like_file_is_skipped(tmp_path):
    (tmp_path / "chapters").mkdir()
    (tmp_path / "typeset").mkdir()
    (tmp_path / "chapters/ch_01.md").write_text(CH1)
    (tmp_path / "chapters/ch_notes.md").write_text("# scratch notes\n\nnot a chapter")
    result = subprocess.run([sys.executable, str(SCRIPT)],
                            capture_output=True, text=True, cwd=tmp_path)
    assert result.returncode == 0, result.stdout + result.stderr
    out = (tmp_path / "typeset/chapters_content.tex").read_text()
    assert "scratch notes" not in out
    assert "skipping non-chapter file: ch_notes.md" in result.stdout
