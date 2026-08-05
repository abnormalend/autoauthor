import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "plugin/autonovel/shared/scripts/gen_brief.py"

CHAPTER = "# Chapter 5: The Descent\n\n" + ("The tunnel narrowed. " * 200)

EVAL_LOG = {
    "overall_score": 5.4,
    "weakest_dimension": "prose_quality",
    "prose_quality": {"score": 5, "weakest_sentence": "The tunnel narrowed.",
                      "fix": "vary the sentence rhythm", "note": "repetitive"},
    "top_3_revisions": ["vary sentence openings", "cut repetition", "add sensory detail"],
    "three_weakest_sentences": ["The tunnel narrowed.", "The tunnel narrowed.", "The tunnel narrowed."],
}

VOICE = """# Voice Profile
## Part 1: Guardrails
- No banned words.
## Part 2: Voice Identity
- Spare, physical, close third person.
"""


def setup_project(tmp_path):
    (tmp_path / "chapters").mkdir()
    (tmp_path / "eval_logs").mkdir()
    (tmp_path / "edit_logs").mkdir()
    (tmp_path / "chapters/ch_05.md").write_text(CHAPTER)
    (tmp_path / "voice.md").write_text(VOICE)
    (tmp_path / "eval_logs/20260101_000000_ch05.json").write_text(json.dumps(EVAL_LOG))


def test_eval_brief_written_to_cwd_project(tmp_path):
    setup_project(tmp_path)
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--eval", "5"],
        capture_output=True, text=True, cwd=tmp_path,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    brief = tmp_path / "briefs/ch05_eval.md"
    assert brief.exists()
    content = brief.read_text()
    assert "prose_quality" in content or "prose quality" in content.lower()
