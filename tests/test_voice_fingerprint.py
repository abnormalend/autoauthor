import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "plugin/autonovel/shared/scripts/voice_fingerprint.py"

CH1 = "# Chapter 1\n\n" + "The rope held. She counted knots and waited for the tide to turn. " * 40
CH2 = "# Chapter 2\n\n" + "Salt crusted the rail. He spat and hauled the net hand over hand. " * 40

WELLS = {
    "sea": ["tide", "salt", "net", "rail", "rope", "knots"],
    "body": ["hand", "spat"],
}


def setup(tmp_path, with_wells=True):
    (tmp_path / "chapters").mkdir()
    (tmp_path / "edit_logs").mkdir()
    (tmp_path / "chapters/ch_01.md").write_text(CH1)
    (tmp_path / "chapters/ch_02.md").write_text(CH2)
    if with_wells:
        (tmp_path / "voice_wells.json").write_text(json.dumps(WELLS))


def run(tmp_path):
    return subprocess.run([sys.executable, str(SCRIPT)],
                          capture_output=True, text=True, cwd=tmp_path)


def test_wells_loaded_from_project_config(tmp_path):
    setup(tmp_path)
    result = run(tmp_path)
    assert result.returncode == 0, result.stdout + result.stderr
    data = json.loads((tmp_path / "edit_logs/voice_fingerprint.json").read_text())
    ch1 = data["chapters"]["ch_01"]
    assert "well_sea_pct" in ch1
    assert "well_body_pct" in ch1
    assert ch1["well_total_per_1k"] > 0


def test_runs_without_wells_file(tmp_path):
    setup(tmp_path, with_wells=False)
    result = run(tmp_path)
    assert result.returncode == 0, result.stdout + result.stderr
    data = json.loads((tmp_path / "edit_logs/voice_fingerprint.json").read_text())
    ch1 = data["chapters"]["ch_01"]
    assert ch1["word_count"] > 0          # core metrics still computed
    assert "well_total_per_1k" not in ch1  # well metrics skipped


def test_chapters_discovered_by_glob(tmp_path):
    setup(tmp_path)
    result = run(tmp_path)
    data = json.loads((tmp_path / "edit_logs/voice_fingerprint.json").read_text())
    assert set(data["chapters"].keys()) >= {"ch_01", "ch_02", "novel_average"}


def test_exits_when_no_chapters_found(tmp_path):
    (tmp_path / "chapters").mkdir()
    result = run(tmp_path)
    assert result.returncode == 1
    assert "No chapters found" in result.stderr
