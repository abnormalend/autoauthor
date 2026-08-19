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


def _short_story_project(tmp_path, words):
    (tmp_path / "chapters").mkdir()
    (tmp_path / "edit_logs").mkdir()
    (tmp_path / "voice.md").write_text("# Voice\n")
    (tmp_path / "chapters/ch_02.md").write_text(
        "# Chapter 2: Short\n\n" + ("word " * words).strip() + "\n")


def test_cuts_target_clamps_to_the_floor(tmp_path, monkeypatch):
    """1,000 words with 500 cuttable would ask for 500; the floor for a
    1,200-word unit is 600."""
    monkeypatch.chdir(tmp_path)
    _short_story_project(tmp_path, 1000)
    (tmp_path / "edit_logs/ch02_cuts.json").write_text(json.dumps({
        "cuts": [{"type": "REDUNDANT", "action": "CUT", "text": "word word",
                  "reason": "repeats", "words_saved": 500}],
        "total_cuttable_words": 500, "overall_fat_percentage": 50,
        "one_sentence_verdict": "half of it is fat"}))
    r = subprocess.run([sys.executable, str(SCRIPT), "--cuts", "2",
                        "--chapter-words", "1200", "--dry-run"],
                       capture_output=True, text=True, cwd=tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "~600 words" in r.stdout
    assert "floor 600" in r.stdout


def test_a_chapter_under_the_floor_is_told_not_to_compress(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _short_story_project(tmp_path, 500)
    (tmp_path / "edit_logs/reader_panel.json").write_text(json.dumps({
        "readers": {"editor": {"cut_candidate": "Chapter 2"}},
        "consensus": [], "disagreements": []}))
    r = subprocess.run([sys.executable, str(SCRIPT), "--panel", "2",
                        "--chapter-words", "1200", "--dry-run"],
                       capture_output=True, text=True, cwd=tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "words (already at or under the floor 600" in r.stdout
    assert "do not compress" in r.stdout
    assert "~600 words" not in r.stdout      # not clamped UP to the floor


def _panel_project(tmp_path, readers, wc=1500):
    import json
    (tmp_path / "chapters").mkdir()
    (tmp_path / "edit_logs").mkdir()
    (tmp_path / "voice.md").write_text("# Voice\n")
    for n in (2, 3, 4):
        (tmp_path / f"chapters/ch_0{n}.md").write_text(
            f"# Chapter {n}: T\n\n" + ("word " * wc).strip() + "\n")
    (tmp_path / "edit_logs/reader_panel.json").write_text(json.dumps(
        {"readers": readers, "consensus": [], "disagreements": []}))


def _brief(tmp_path, ch):
    r = subprocess.run([sys.executable, str(SCRIPT), "--panel", str(ch),
                        "--chapter-words", "1200", "--dry-run"],
                       capture_output=True, text=True, cwd=tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr
    return r.stdout


def test_zero_padded_chapter_mentions_match(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _panel_project(tmp_path, {"editor": {"cut_candidate": "Chapter 03 repeats the lookup device."}})
    assert "COMPRESS" in _brief(tmp_path, 3)


def test_an_item_is_attributed_to_the_first_chapter_it_names(tmp_path, monkeypatch):
    """'Chapter 2's roster scene is weak; chapter 3 then has to carry it' is a
    chapter-2 item. It must not appear in chapter 3's brief."""
    monkeypatch.chdir(tmp_path)
    _panel_project(tmp_path, {"genre_reader": {
        "worst_scene": "Chapter 2's roster scene is weak; chapter 3 then has to carry it. Fix: break it."}})
    assert "Dramatize" in _brief(tmp_path, 2)
    assert "Dramatize" not in _brief(tmp_path, 3)


def test_character_level_items_go_under_their_own_heading_not_into_changes(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _panel_project(tmp_path, {"writer": {"thinnest_character": "Ikaika is thinnest; I never learn what he wants."}})
    out = _brief(tmp_path, 4)
    assert "Deepen character" not in out
    assert "CHARACTER NOTES" in out and "Ikaika" in out


def test_character_item_naming_a_chapter_still_goes_under_character_notes(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _panel_project(tmp_path, {"writer": {"thinnest_character": "Ikaika in Chapter 4 is thinnest."}})
    out = _brief(tmp_path, 4)
    assert "Deepen character" not in out
    assert "CHARACTER NOTES" in out and "Ikaika" in out


def test_plural_chapters_mention_is_attributed_to_the_first_only(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _panel_project(tmp_path, {"editor": {"momentum_loss": "Chapters 2 and 3 both drag."}})
    assert "TIGHTEN" in _brief(tmp_path, 2)
    assert "TIGHTEN" not in _brief(tmp_path, 3)


def test_compress_target_is_labelled_an_upper_bound(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _panel_project(tmp_path, {"editor": {"cut_candidate": "Chapter 2 could go."}}, wc=1762)
    out = _brief(tmp_path, 2)
    assert "upper bound" in out
    assert "repetition" in out.lower()
