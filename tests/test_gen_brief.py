import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "plugin/autoauthor/shared/scripts/gen_brief.py"

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


# --- genre-aware diction rule ---------------------------------------------

def test_brief_names_the_project_genre_in_the_diction_rule(tmp_path):
    setup_project(tmp_path)
    (tmp_path / "state.json").write_text(json.dumps({"genre": "fantasy"}))
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--eval", "5"],
        capture_output=True, text=True, cwd=tmp_path,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "no generic fantasy diction" in (tmp_path / "briefs/ch05_eval.md").read_text()


def test_brief_falls_back_to_neutral_diction_rule(tmp_path):
    setup_project(tmp_path)
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--eval", "5"],
        capture_output=True, text=True, cwd=tmp_path,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "no generic genre diction" in (tmp_path / "briefs/ch05_eval.md").read_text()


def test_unknown_genre_falls_back_rather_than_naming_it(tmp_path):
    """A brief must never fail, or leak an unresolvable name, on bad state."""
    setup_project(tmp_path)
    (tmp_path / "state.json").write_text(json.dumps({"genre": "nosuchgenre"}))
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--eval", "5"],
        capture_output=True, text=True, cwd=tmp_path,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    brief = (tmp_path / "briefs/ch05_eval.md").read_text()
    assert "no generic genre diction" in brief
    assert "nosuchgenre" not in brief


def test_malformed_state_json_does_not_break_the_brief(tmp_path):
    setup_project(tmp_path)
    (tmp_path / "state.json").write_text("{not json}")
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--eval", "5"],
        capture_output=True, text=True, cwd=tmp_path,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "no generic genre diction" in (tmp_path / "briefs/ch05_eval.md").read_text()


def test_compress_target_clamps_to_half_the_unit_length(tmp_path, monkeypatch):
    """55% of a 1,100-word scene is 605; the floor for a 1,200-word unit is
    600, so the target is 605. For a 900-word scene 55% is 495 and the
    floor wins: 600. Without --chapter-words the floor is the novel's 1800."""
    import json
    monkeypatch.chdir(tmp_path)
    (tmp_path / "chapters").mkdir()
    (tmp_path / "edit_logs").mkdir()
    (tmp_path / "voice.md").write_text("# Voice\n")
    (tmp_path / "chapters/ch_02.md").write_text(
        "# Chapter 2: Short\n\n" + ("word " * 900).strip() + "\n")
    (tmp_path / "edit_logs/reader_panel.json").write_text(json.dumps({
        "readers": {"editor": {"cut_candidate": "Chapter 2"}},
        "consensus": ["cut_candidate: chapter 2"],
        "disagreements": []}))
    r = subprocess.run([sys.executable, str(SCRIPT), "--panel", "2",
                        "--chapter-words", "1200", "--dry-run"],
                       capture_output=True, text=True, cwd=tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "~600 words" in r.stdout          # 495 clamped up to the 600 floor
    assert "floor 600" in r.stdout


def test_compress_target_floor_defaults_to_the_novel_1800(tmp_path, monkeypatch):
    import json
    monkeypatch.chdir(tmp_path)
    (tmp_path / "chapters").mkdir()
    (tmp_path / "edit_logs").mkdir()
    (tmp_path / "voice.md").write_text("# Voice\n")
    (tmp_path / "chapters/ch_02.md").write_text(
        "# Chapter 2: Short\n\n" + ("word " * 2400).strip() + "\n")
    (tmp_path / "edit_logs/reader_panel.json").write_text(json.dumps({
        "readers": {"editor": {"cut_candidate": "Chapter 2"}},
        "consensus": [], "disagreements": []}))
    r = subprocess.run([sys.executable, str(SCRIPT), "--panel", "2", "--dry-run"],
                       capture_output=True, text=True, cwd=tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "~1800 words" in r.stdout         # 1320 clamped up to 1800
