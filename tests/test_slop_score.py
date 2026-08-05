import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "plugin/autonovel/shared/scripts/slop_score.py"
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
