# Autonovel Skills Plugin Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convert the autonovel pipeline into a self-contained Claude Code plugin (`plugin/autonovel/`) with 7 phase skills, replacing the 18 Anthropic-API wrapper scripts with skill instructions while preserving the mechanical scripts.

**Architecture:** Skill-per-phase plus a router skill. All craft docs, rubrics, templates, and mechanical scripts ship inside the plugin under `shared/`, referenced from skills via `${CLAUDE_PLUGIN_ROOT}`. Novels live in their own directories with their own git repos; every script operates on the current working directory (the novel project), never on the script's own location. Evaluation runs as clean-room subagent judges reading rubric files, plus the mechanical slop scorer as a real script.

**Tech Stack:** Claude Code plugin (plugin.json + marketplace.json), markdown skills, stdlib-only Python 3 scripts, pytest for script tests, LaTeX (tectonic) + pandoc for export.

**Spec:** `docs/superpowers/specs/2026-08-05-autonovel-skills-design.md`

---

## Key facts for the implementing engineer

- **Plugin manifests:** `.claude-plugin/plugin.json` requires only `{"name": ...}`. Skills auto-discovered at `skills/<name>/SKILL.md`, invoked as `/autonovel:<name>`. Skill content may use `${CLAUDE_PLUGIN_ROOT}` (plugin install dir) — use it for every reference to `shared/`. Plugins cannot reference files outside their own directory after install, which is why everything ships under `plugin/autonovel/`.
- **Local testing:** `/plugin marketplace add /Users/brent/code/autonovel/plugin` then `/plugin install autonovel@autonovel-dev`. Validate with `claude plugin validate <path>`.
- **Novel project layout** (created by novel-seed, consumed by everything else): `seed.txt`, `voice.md`, `world.md`, `characters.md`, `outline.md`, `canon.md`, `MYSTERY.md`, `state.json`, `results.tsv`, `arc_summary.md`, `chapters/ch_NN.md`, `eval_logs/`, `edit_logs/`, `briefs/`, `typeset/`.
- **results.tsv columns** (keep exactly): `timestamp	phase	score	words	keep_discard	description`
- **De-Bells rule:** the original scripts leak content from the first novel ("Cass", "Cantamura", "tonal law", "House of Bells", "72,422 words", "under-note", "needle behind left eye", chapter counts like `range(1, 20)`). Every ported prompt/rubric/script must be generic. Grep for `cass|cantamura|bells|tonal|under-note` in everything you create under `plugin/` before committing — zero hits allowed (case-insensitive).
- **Judge subagent pattern** (used by several skills; the skills' text in this plan already embeds it): dispatch a fresh `general-purpose` agent whose prompt is ONLY: (1) read a rubric file, (2) read specific project files by absolute path, (3) return ONLY the JSON the rubric specifies. No drafting context, no conversation history.
- **Commit style for this work:** conventional-ish messages, commit after every task, all on `master` of this repo.

---

## Task 1: Scaffold plugin structure and manifests

**Files:**
- Create: `plugin/.claude-plugin/marketplace.json`
- Create: `plugin/autonovel/.claude-plugin/plugin.json`

- [ ] **Step 1: Create the directory tree**

```bash
mkdir -p plugin/.claude-plugin plugin/autonovel/.claude-plugin plugin/autonovel/skills plugin/autonovel/shared/craft plugin/autonovel/shared/rubrics plugin/autonovel/shared/templates plugin/autonovel/shared/scripts plugin/autonovel/shared/typeset
```

- [ ] **Step 2: Write `plugin/autonovel/.claude-plugin/plugin.json`**

```json
{
  "name": "autonovel",
  "description": "Autonomous novel-writing pipeline: seed, foundation, drafting, revision, review, and export skills with score-gated iteration and clean-room subagent judges.",
  "version": "0.1.0",
  "author": { "name": "Brent Rogers" }
}
```

- [ ] **Step 3: Write `plugin/.claude-plugin/marketplace.json`** (makes `plugin/` a local marketplace for dev testing; the marketplace repo will get its own entry later)

```json
{
  "name": "autonovel-dev",
  "owner": { "name": "Brent Rogers" },
  "plugins": [
    {
      "name": "autonovel",
      "source": "./autonovel",
      "description": "Autonomous novel-writing pipeline skills"
    }
  ]
}
```

- [ ] **Step 4: Validate**

Run: `claude plugin validate plugin`
Expected: validation passes (plugin has no skills yet — that's fine; if the validator requires at least one skill, defer validation to Task 8 and note it in the commit message).

- [ ] **Step 5: Commit**

```bash
git add plugin && git commit -m "feat: scaffold autonovel plugin structure and manifests"
```

---

## Task 2: Move craft docs and templates into the plugin

**Files:**
- Move: `CRAFT.md`, `ANTI-SLOP.md`, `ANTI-PATTERNS.md` → `plugin/autonovel/shared/craft/`
- Copy: `voice.md`, `world.md`, `characters.md`, `outline.md`, `canon.md`, `MYSTERY.md` → `plugin/autonovel/shared/templates/`
- Create: `plugin/autonovel/shared/templates/state.json`

Rationale for copy-not-move on templates: the repo-root copies are deleted in Task 17 along with the wrapper scripts; keeping them until then lets the old workflow docs stay coherent during the port.

- [ ] **Step 1: Move the craft docs (single source of truth moves into the plugin)**

```bash
git mv CRAFT.md ANTI-SLOP.md ANTI-PATTERNS.md plugin/autonovel/shared/craft/
```

- [ ] **Step 2: Copy the templates**

```bash
cp voice.md world.md characters.md outline.md canon.md MYSTERY.md plugin/autonovel/shared/templates/
```

- [ ] **Step 3: Verify templates are story-clean**

Run: `grep -ril 'cass\|cantamura\|bells\|tonal\|under-note' plugin/autonovel/shared/`
Expected: no output. (Pre-verified: root templates are clean; only `landing/index.html` and `typeset/novel.tex` leak, and neither is copied here.)

- [ ] **Step 4: Write `plugin/autonovel/shared/templates/state.json`** — the existing root `state.json` plus two counters the revise/review skills need:

```json
{
  "phase": "foundation",
  "current_focus": null,
  "iteration": 0,
  "foundation_score": 0.0,
  "lore_score": 0.0,
  "chapters_drafted": 0,
  "chapters_total": 0,
  "novel_score": 0.0,
  "revision_cycle": 0,
  "review_round": 0,
  "debts": []
}
```

- [ ] **Step 5: Commit**

```bash
git add -A && git commit -m "feat: move craft docs and templates into plugin shared/"
```

---

## Task 3: Extract the mechanical slop scorer as a standalone CLI

**Files:**
- Create: `plugin/autonovel/shared/scripts/slop_score.py`
- Create: `tests/test_slop_score.py`
- Create: `tests/fixtures/sloppy_chapter.md`
- Create: `tests/fixtures/clean_chapter.md`
- Modify: `pyproject.toml` (add pytest dev dependency)

The scorer is `evaluate.py` lines 45–239: the constant lists (`TIER1_BANNED`, `TIER2_SUSPICIOUS`, `TIER3_FILLER`, `TRANSITION_OPENERS`, `FICTION_AI_TELLS`, `STRUCTURAL_AI_TICS`, `TELLING_PATTERNS`) and the `slop_score(text)` function. Copy them **verbatim** — the tuned weights are the product of a full novel's production; do not "improve" them.

- [ ] **Step 1: Add pytest**

```bash
uv add --dev pytest
```

- [ ] **Step 2: Write the fixtures**

`tests/fixtures/sloppy_chapter.md` — must trip tier1, fiction tells, and telling patterns:

```markdown
# Chapter 1: The Test

He felt a sense of dread as he began to delve into the tapestry of the myriad
secrets. She felt angry. He couldn't help but feel that the weight of it all
was too much. Her eyes widened. A wave of fear washed over him.

However, the silence was heavy. Furthermore, the air was thick with tension.
Moreover, he let out a breath he didn't know he was holding.

He walked to the door. He opened the door slowly. He looked outside quietly.
He saw the garden there. He closed the door again.
```

`tests/fixtures/clean_chapter.md` — plain, varied prose with none of the patterns:

```markdown
# Chapter 1: The Forge

Iron sang under the hammer. Marta counted strikes the way her mother had
counted stitches — by feel, not number. Four more and the blade would tell
her what it wanted.

The apprentice dropped the tongs. Again.

"Pick them up." She didn't turn around. The boy had good hands and no
patience, which was better than the reverse, though not by much. Outside,
carts ground past on the cobbles, and somebody was selling plums, loudly,
at the wrong end of the street for plums.
```

- [ ] **Step 3: Write the failing test** — `tests/test_slop_score.py`:

```python
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
```

- [ ] **Step 4: Run test to verify it fails**

Run: `uv run pytest tests/test_slop_score.py -v`
Expected: FAIL (script does not exist yet).

- [ ] **Step 5: Write `plugin/autonovel/shared/scripts/slop_score.py`**

Structure (stdlib only, no dotenv/httpx):

```python
#!/usr/bin/env python3
"""Mechanical slop scorer — regex-based AI-tell detection. No LLM, no network.

Usage:
  python3 slop_score.py chapters/ch_01.md [more files...]
  python3 slop_score.py chapters/*.md

Prints a JSON report to stdout:
  {"files": [{"path": ..., <slop_score() dict fields>}...],
   "summary": {"worst_file": ..., "max_penalty": N, "mean_penalty": N}}

The slop_penalty (0-10) is subtracted from LLM-judge chapter scores by the
autonovel skills. Verbatim port of the scorer from autonovel evaluate.py.
"""
import json
import re
import sys
from pathlib import Path

# === BEGIN verbatim copy of evaluate.py lines 47-239 ===
# TIER1_BANNED = [...]           <- copy exactly
# TIER2_SUSPICIOUS = [...]       <- copy exactly
# TIER3_FILLER = [...]           <- copy exactly
# TRANSITION_OPENERS = [...]     <- copy exactly
# FICTION_AI_TELLS = [...]       <- copy exactly
# STRUCTURAL_AI_TICS = [...]     <- copy exactly
# TELLING_PATTERNS = [...]       <- copy exactly
# def slop_score(text): ...      <- copy exactly
# === END verbatim copy ===


def main():
    paths = sys.argv[1:]
    if not paths:
        print("usage: slop_score.py <file> [file...]", file=sys.stderr)
        sys.exit(1)
    reports = []
    for p in paths:
        text = Path(p).read_text()
        r = slop_score(text)
        r["path"] = str(p)
        reports.append(r)
    penalties = [r["slop_penalty"] for r in reports]
    worst = max(reports, key=lambda r: r["slop_penalty"])
    print(json.dumps({
        "files": reports,
        "summary": {
            "worst_file": worst["path"],
            "max_penalty": max(penalties),
            "mean_penalty": round(sum(penalties) / len(penalties), 2),
        },
    }, indent=2))


if __name__ == "__main__":
    main()
```

Replace the `=== BEGIN/END ===` comment block with the actual constants and function copied verbatim from `evaluate.py:47-239` (the version at commit `d165f26`; open the file and copy, do not retype). One adjustment: `slop_score()` returns tuples inside lists (`tier1_hits` etc.) — tuples serialize to JSON arrays, which the tests expect as `[w for w, _ in ...]` after `json.loads` gives lists-of-lists; that works unchanged.

- [ ] **Step 6: Run tests to verify they pass**

Run: `uv run pytest tests/test_slop_score.py -v`
Expected: 3 passed. If `test_sloppy_chapter_scores_high_penalty` fails on the threshold, the fixture didn't trip enough detectors — add more tier1 words to the fixture rather than loosening the assertion below 4.0.

- [ ] **Step 7: Commit**

```bash
git add plugin/autonovel/shared/scripts/slop_score.py tests pyproject.toml uv.lock
git commit -m "feat: extract mechanical slop scorer as standalone CLI with tests"
```

---

## Task 4: Port apply_cuts.py to CWD-based operation

**Files:**
- Create: `plugin/autonovel/shared/scripts/apply_cuts.py` (from root `apply_cuts.py`)
- Create: `tests/test_apply_cuts.py`

The only functional change: `BASE = Path(__file__).resolve().parent` becomes `BASE = Path.cwd()` so it operates on the novel project the user is standing in. Everything else (quote matching, whitespace normalization, type filters, dry-run) is kept verbatim.

- [ ] **Step 1: Write the failing test** — `tests/test_apply_cuts.py`:

```python
import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "plugin/autonovel/shared/scripts/apply_cuts.py"

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
            "quote": "smelled of tallow and wet wool",
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
    text = (tmp_path / "chapters/ch_03.md").read_text()
    assert "tallow and wet wool" in text  # under MIN_QUOTE_LEN, skipped


def test_dry_run_modifies_nothing(tmp_path):
    setup_project(tmp_path)
    before = (tmp_path / "chapters/ch_03.md").read_text()
    run_in(tmp_path, "all", "--dry-run")
    assert (tmp_path / "chapters/ch_03.md").read_text() == before
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_apply_cuts.py -v`
Expected: FAIL (script not found).

- [ ] **Step 3: Create the ported script**

```bash
cp apply_cuts.py plugin/autonovel/shared/scripts/apply_cuts.py
```

Then edit `plugin/autonovel/shared/scripts/apply_cuts.py` line 18:

```python
# was: BASE = Path(__file__).resolve().parent
BASE = Path.cwd()
```

And update the module docstring's first line to: `"""Apply adversarial edit cuts to chapter files in the current novel project (CWD)."""`

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_apply_cuts.py -v`
Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add plugin/autonovel/shared/scripts/apply_cuts.py tests/test_apply_cuts.py
git commit -m "feat: port apply_cuts.py into plugin, CWD-based"
```

---

## Task 5: Port gen_brief.py to CWD-based operation

**Files:**
- Create: `plugin/autonovel/shared/scripts/gen_brief.py` (from root `gen_brief.py`)
- Create: `tests/test_gen_brief.py`

`gen_brief.py` is fully mechanical (assembles revision briefs from `eval_logs/`, `edit_logs/`, chapter text, and `voice.md` — no API calls). Same single change as Task 4: CWD-based paths.

- [ ] **Step 1: Write the failing test** — `tests/test_gen_brief.py`:

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_gen_brief.py -v`
Expected: FAIL (script not found).

- [ ] **Step 3: Create the ported script**

```bash
cp gen_brief.py plugin/autonovel/shared/scripts/gen_brief.py
```

Edit `plugin/autonovel/shared/scripts/gen_brief.py` line 18:

```python
# was: BASE_DIR = Path(__file__).parent
BASE_DIR = Path.cwd()
```

(The other path constants on lines 19–23 derive from `BASE_DIR` and need no change.)

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_gen_brief.py -v`
Expected: 1 passed. If the eval-log filename glob in `latest_chapter_eval()` (gen_brief.py:96) doesn't match the fixture name, read that function and adjust the fixture filename to its expected pattern — do not change the script's globbing.

- [ ] **Step 5: Commit**

```bash
git add plugin/autonovel/shared/scripts/gen_brief.py tests/test_gen_brief.py
git commit -m "feat: port gen_brief.py into plugin, CWD-based"
```

---

## Task 6: Port voice_fingerprint.py with configurable vocabulary wells

**Files:**
- Create: `plugin/autonovel/shared/scripts/voice_fingerprint.py` (from root `voice_fingerprint.py`)
- Create: `tests/test_voice_fingerprint.py`

The root script hardcodes the Bells novel's three vocabulary wells (musical/trade/body word sets, lines 18–49) and `range(1, 25)` chapter counts. Port changes: (1) CWD-based, (2) wells loaded from the novel project's `voice_wells.json` (written by the foundation skill during voice discovery), (3) discover chapters by glob, (4) well metrics skipped gracefully when no wells file exists.

- [ ] **Step 1: Write the failing test** — `tests/test_voice_fingerprint.py`:

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_voice_fingerprint.py -v`
Expected: FAIL (script not found).

- [ ] **Step 3: Create the ported script**

Start from `cp voice_fingerprint.py plugin/autonovel/shared/scripts/voice_fingerprint.py`, then make these edits:

1. Replace lines 14–15 with:

```python
BASE_DIR = Path.cwd()
CHAPTERS_DIR = BASE_DIR / "chapters"
```

2. Delete the hardcoded `WELL_MUSICAL`, `WELL_TRADE`, `WELL_BODY` sets (lines 17–49) and add:

```python
def load_wells():
    """Load vocabulary wells from the novel project's voice_wells.json.

    Format: {"well_name": ["word", ...], ...} — written during voice
    discovery by the novel-foundation skill. Returns {} if absent.
    """
    wells_path = BASE_DIR / "voice_wells.json"
    if not wells_path.exists():
        return {}
    raw = json.loads(wells_path.read_text())
    return {name: set(w.lower() for w in words) for name, words in raw.items()}
```

3. In `analyze_chapter(path)`, replace the three `musical_count/trade_count/body_count` lines and the three `well_*_pct` result keys with a generic loop. `analyze_chapter` takes a second parameter `wells`:

```python
def analyze_chapter(path, wells):
    ...
    well_counts = {name: sum(1 for w in lower_words if w in words)
                   for name, words in wells.items()}
    total_well = sum(well_counts.values()) or 1
    ...
    result = { ...all existing non-well metrics unchanged... }
    if wells:
        for name, count in well_counts.items():
            result[f"well_{name}_pct"] = round(count / total_well * 100, 1)
        result["well_total_per_1k"] = round(sum(well_counts.values()) / word_count * 1000, 1) if word_count else 0
    return result
```

4. In `main()`: replace `for ch in range(1, 25)` with glob discovery, pass wells through, and make the summary table print only the always-present columns:

```python
def main():
    wells = load_wells()
    results = {}
    for path in sorted(CHAPTERS_DIR.glob("ch_*.md")):
        key = path.stem  # "ch_01"
        results[key] = analyze_chapter(path, wells)
    if not results:
        print("No chapters found in chapters/", file=sys.stderr)
        sys.exit(1)
    ...
```

The novel-average and outlier logic already iterates over result keys generically — it needs no change beyond skipping when different chapters have different keys (they won't; wells are uniform per run). Keep the printed table but drop the three hardcoded `Mus%/Trd%/Bod%` columns; print well percentages as a separate per-chapter line only when wells exist. Add `import sys` to the imports. Ensure `edit_logs/` is created with `(BASE_DIR / "edit_logs").mkdir(exist_ok=True)` before writing.

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_voice_fingerprint.py -v`
Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add plugin/autonovel/shared/scripts/voice_fingerprint.py tests/test_voice_fingerprint.py
git commit -m "feat: port voice_fingerprint.py with project-defined vocabulary wells"
```

---

## Task 7: Port the typeset toolchain

**Files:**
- Create: `plugin/autonovel/shared/typeset/build_tex.py` (from `typeset/build_tex.py`)
- Create: `plugin/autonovel/shared/typeset/novel.tex` (from `typeset/novel.tex`, de-Bellsed)
- Copy: `typeset/epub_metadata.yaml`, `typeset/epub_style.css`, `typeset/epub_front_matter.md`, `typeset/epub_back_cover.md`, `typeset/epub_colophon.md` → `plugin/autonovel/shared/typeset/`
- Create: `tests/test_build_tex.py`

Root `build_tex.py` hardcodes `/home/jeffq/autonovel/` paths and `range(1, 20)`. Root `novel.tex` hardcodes the Bells title in 8+ places.

- [ ] **Step 1: Write the failing test** — `tests/test_build_tex.py`:

```python
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).parent.parent / "plugin/autonovel/shared/typeset/build_tex.py"

CH1 = """# Chapter 1: The Landing

"Down oars," the pilot said — quietly, as if the cliff could hear.

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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_build_tex.py -v`
Expected: FAIL.

- [ ] **Step 3: Port build_tex.py**

`cp typeset/build_tex.py plugin/autonovel/shared/typeset/build_tex.py`, then edit:

1. Replace lines 6–7:

```python
# was: CHAPTERS_DIR = "/home/jeffq/autonovel/chapters"; OUT_DIR = "/home/jeffq/autonovel/typeset"
import os, re, glob
CHAPTERS_DIR = os.path.join(os.getcwd(), "chapters")
OUT_DIR = os.path.join(os.getcwd(), "typeset")
```

2. Replace the chapter loop header `for n in range(1, 20):` with glob discovery:

```python
chapter_files = sorted(glob.glob(os.path.join(CHAPTERS_DIR, "ch_*.md")))
for path in chapter_files:
    n = int(re.search(r"ch_(\d+)", os.path.basename(path)).group(1))
    with open(path) as f:
        text = f.read()
```

(and delete the old `path = os.path.join(...)` line inside the loop). The ornament lookup (`art_base` block, lines 113–128) keeps working relative to CWD (`<project>/art/...`); leave it — projects without art simply get no ornament.

3. Guard the empty case after the loop:

```python
if not chapters_tex:
    raise SystemExit("No chapters found in chapters/")
```

- [ ] **Step 4: De-Bells novel.tex**

`cp typeset/novel.tex plugin/autonovel/shared/typeset/novel.tex`, then replace every Bells-specific string (lines 40, 102, 136, 144, 186, 188–189, 222 of the original, plus any author-name occurrences) with visible placeholders the export skill fills in: `NOVEL-TITLE`, `NOVEL-TITLE-SHORT`, `NOVEL-AUTHOR`, `NOVEL-EPIGRAPH`, `NOVEL-END-TEXT`. Delete the QR-code block (lines 186–189) entirely. Verify with:

Run: `grep -in 'bells\|nousresearch' plugin/autonovel/shared/typeset/novel.tex`
Expected: no output.

- [ ] **Step 5: Copy the ePub assets**

```bash
cp typeset/epub_metadata.yaml typeset/epub_style.css typeset/epub_front_matter.md typeset/epub_back_cover.md typeset/epub_colophon.md plugin/autonovel/shared/typeset/
grep -ril 'bells\|cass\|cantamura' plugin/autonovel/shared/typeset/ || echo CLEAN
```

If the grep finds hits in the ePub files, replace them with the same `NOVEL-*` placeholders.

- [ ] **Step 6: Run tests to verify they pass**

Run: `uv run pytest tests/test_build_tex.py -v`
Expected: 1 passed.

- [ ] **Step 7: Commit**

```bash
git add plugin/autonovel/shared/typeset tests/test_build_tex.py
git commit -m "feat: port typeset toolchain into plugin, CWD-based and de-Bellsed"
```

## Task 8: Write the evaluation rubrics (foundation, chapter, full-novel)

**Files:**
- Create: `plugin/autonovel/shared/rubrics/foundation.md`
- Create: `plugin/autonovel/shared/rubrics/chapter.md`
- Create: `plugin/autonovel/shared/rubrics/full-novel.md`

These are the judge prompts from `evaluate.py`, converted from Python f-strings into standalone markdown a subagent reads. Conversion rules for all three:

1. **Header block first.** Every rubric starts with this framing (adjust the file list per rubric):

```markdown
# <Name> Rubric

You are a literary critic and novel editor evaluating fiction with
precision. You were given ONLY this rubric and the files listed below —
you have no other context, no stake in the scores, and no memory of how
the text was produced. Judge what is on the page.

INPUT FILES (read all of them from the project directory you were given):
<list>

OUTPUT: Return ONLY a single JSON object matching the schema at the end
of this rubric. No markdown fences, no preamble, no commentary.
```

2. **Replace f-string placeholders with file reads.** `{voice}` → "the project's `voice.md`" in the INPUT FILES list; same for world/characters/outline/canon/chapter files. The chapter rubric's `{chapter_outline}` and `{prev_chapter_tail}` become instructions: "Extract the target chapter's entry from `outline.md`; read the last ~1500 words of the previous chapter file."
3. **Escape cleanup.** The Python source doubles braces (`{{`/`}}`) in the JSON schemas — un-double them.
4. **De-Bells.** Exact replacements:
   - foundation prompt (evaluate.py:398–400): `"(e.g., can Cass hear lies in written documents? What happens during the climax -- what rule resolves it?)"` → `"(e.g., can the protagonist's ability do what the climax requires? What established rule resolves the climactic conflict?)"`
   - chapter prompt (evaluate.py:613–614): `"Does Cass sound like a specific 14-year-old, or like "young protagonist"?"` → `"Does the POV character sound like a specific person of their age and background, or like a stock protagonist?"`
   - chapter prompt (evaluate.py:625): `"Metaphors from Cass's experience"` → `"Metaphors from the POV character's experience"`

- [ ] **Step 1: Write `foundation.md`** — port `FOUNDATION_PROMPT` (evaluate.py:351–515) verbatim under the header block, applying the four conversion rules. INPUT FILES: `voice.md`, `world.md`, `characters.md`, `outline.md`, `canon.md`. Keep the scoring calibration, mandatory gap-finding, all four cross-checks, all 13 dimensions, the JSON schema, the 40/30/20/10 weighting note, and the final self-check paragraph — those calibrations are the product of a full production run.

- [ ] **Step 2: Write `chapter.md`** — port `CHAPTER_PROMPT` (evaluate.py:527–670) the same way. INPUT FILES: `voice.md`, `world.md` (note: "you may skim; prioritize rules over lore detail"), `characters.md`, `canon.md`, `outline.md` (extract the target chapter's entry), the previous chapter file (last ~1500 words), and the target chapter file. Add one line the Python version handled in code: "The invoking skill runs a separate mechanical slop scan; do not attempt to compensate for it — score the prose on its merits."

- [ ] **Step 3: Write `full-novel.md`** — port `FULL_NOVEL_PROMPT` (evaluate.py:715–756). INPUT FILES: `voice.md`, `world.md`, `characters.md`, `outline.md`, and `arc_summary.md` (chapter-by-chapter summaries — the invoking skill maintains this file). Keep all 7 dimensions and the JSON schema including `weakest_chapter` and `top_suggestion`.

- [ ] **Step 4: Verify no leakage**

Run: `grep -in 'cass\|cantamura\|bells\|tonal\|under-note' plugin/autonovel/shared/rubrics/*.md`
Expected: no output.

- [ ] **Step 5: Commit**

```bash
git add plugin/autonovel/shared/rubrics
git commit -m "feat: add foundation, chapter, and full-novel judge rubrics"
```

---

## Task 9: Write the revision-phase rubrics (adversarial edit, reader panel, manuscript review)

**Files:**
- Create: `plugin/autonovel/shared/rubrics/adversarial-edit.md`
- Create: `plugin/autonovel/shared/rubrics/reader-panel.md`
- Create: `plugin/autonovel/shared/rubrics/manuscript-review.md`

(The spec calls the third one `opus-review.md`; name it `manuscript-review.md` — the model is chosen by the invoking skill, not baked into the filename. Note this rename when comparing against the spec.)

- [ ] **Step 1: Write `adversarial-edit.md`** — port the system prompt (adversarial_edit.py:37–42, the "ruthless literary editor" persona) and `EDIT_PROMPT` (adversarial_edit.py:90–131) using the Task 8 header-block pattern. INPUT FILES: the single target chapter file. Keep the six cut types (FAT / REDUNDANT / OVER-EXPLAIN / GENERIC / TELL / STRUCTURAL), the 10-word-minimum quote rule, and the full JSON schema (`cuts[]`, `total_cuttable_words`, `tightest_passage`, `loosest_passage`, `overall_fat_percentage`, `one_sentence_verdict`). Add: "Quotes must be copied EXACTLY from the chapter text, minimum 25 characters, because a mechanical script applies them by literal string matching — a paraphrased quote is a wasted cut."

- [ ] **Step 2: Write `reader-panel.md`** — port the four persona system prompts (reader_panel.py:24–77: editor, genre_reader, writer, first_reader) and `READER_PROMPT` (reader_panel.py:79–111). Structure the file as:

```markdown
# Reader Panel Rubric

The invoking skill dispatches FOUR separate subagents, one per persona
below. Each subagent is told its persona name; adopt ONLY your assigned
persona's mindset, then answer the questions.

INPUT FILES: `arc_summary.md` (chapter-by-chapter summaries with opening/
closing passages and key dialogue).

## Persona: The Editor
<editor system prompt verbatim>
## Persona: The Genre Reader
<verbatim>
## Persona: The Writer
<verbatim>
## Persona: The First Reader
<verbatim>

## The Questions (all personas answer the same ten)
<READER_PROMPT questions, de-Bellsed>

OUTPUT: Return ONLY the JSON object with the ten keys.
```

De-Bells edits to the questions: the prompt's framing line `"The full novel is 72,422 words across 24 chapters"` → `"Word and chapter counts are stated at the top of arc_summary.md."`; the `earned_ending` question (reader_panel.py:93) `"Does Cass's choice in Ch 22 land? Does the final image in Ch 24 mirror Ch 1 in a way that satisfies?"` → `"Does the protagonist's climactic choice land? Does the final chapter's closing image answer the opening chapter in a way that satisfies?"`; the `cut_candidate` question's `"~7,000 words"` → `"roughly 10% of its length"`.

- [ ] **Step 3: Write `manuscript-review.md`** — the dual-persona review. Content:

```markdown
# Manuscript Review Rubric

You are reviewing a complete novel manuscript. You have no other context.

INPUT: the file `manuscript.md` in the project directory (the full novel,
chapters concatenated in order).

Read the below novel. Review it first as a literary critic (like a
newspaper book review, including a star rating out of five) and then as
a professor of fiction. In the later review, give specific, actionable
suggestions for any defects you find, as a NUMBERED list. Be fair but
honest. You don't *have* to find defects.

For each numbered item in the professor's review, end the item with a
bracketed tag line in exactly this format so the review can be parsed:
[severity: major|moderate|minor] [type: compression|addition|mechanical|structural|revision] [qualified: yes|no]

"qualified: yes" means the criticism is hedged — you consider it a cost
of a deliberate and defensible choice rather than a defect (phrases like
"individually fine", "costs of ambition", "a deliberate choice").

OUTPUT: The two reviews as markdown (NOT JSON — this rubric is the
exception). Critic review first under "## Critic", professor review
under "## Professor", numbered items with tag lines.
```

This ports review.py's prompt (review.py:34–36) while replacing its fragile regex severity-classification (review.py:95–182) with self-tagging by the reviewer — the invoking skill counts tags instead of pattern-matching prose.

- [ ] **Step 4: Verify no leakage**

Run: `grep -in 'cass\|cantamura\|bells\|72,422\|Ch 22\|Ch 24' plugin/autonovel/shared/rubrics/*.md`
Expected: no output.

- [ ] **Step 5: Commit**

```bash
git add plugin/autonovel/shared/rubrics
git commit -m "feat: add adversarial-edit, reader-panel, and manuscript-review rubrics"
```

## Shared conventions for Tasks 10–16 (the skills)

Every SKILL.md below follows these conventions — they're stated once here and the skill texts assume them:

- **Project check:** "the project" means the current working directory. A valid project has `state.json` and `voice.md`. Skills other than `novel-seed` start by verifying this and stop with guidance if it fails.
- **Judge dispatch:** "dispatch a judge subagent with rubric R over files F" means: use the Agent tool (subagent_type `general-purpose`, run synchronously) with a prompt of exactly this shape — no other context:

  > Read the rubric at `${CLAUDE_PLUGIN_ROOT}/shared/rubrics/<R>` and follow it exactly. The project directory is `<absolute path>`. The input files are: `<absolute paths F>`. Return ONLY the output the rubric specifies.

  If the returned JSON is malformed, re-dispatch once with "Your previous output was not valid JSON. Return ONLY the JSON object." still-bad → record the iteration as unscored in results.tsv (`keep_discard=noscore`) and continue.
- **Keep/discard:** after producing a change and scoring it — if the relevant score improved (or first attempt), `git add -A && git commit`; if it regressed, `git reset --hard HEAD~1`. Either way append a row to `results.tsv`: `<ISO timestamp>\t<phase>\t<score>\t<total chapter word count>\t<keep|discard|noscore>\t<one-line description>`.
- **Dirty-state guard:** if `git status --porcelain` is non-empty at skill start, stop and ask the user before touching anything.
- **Completion notification:** at phase end (success, plateau, or attempt-limit stop), send a Pushover notification via the pushover skill: title `autonovel: <phase>`, message with the headline result and next step.
- **Skill file paths:** each task creates `plugin/autonovel/skills/<name>/SKILL.md` (plus `references/` files where listed). After each skill task: `claude plugin validate plugin` → expect pass, then commit.
- **Skill authoring quality:** before writing the first SKILL.md (Task 10), the implementer invokes the superpowers:writing-skills skill and applies its conventions (description phrasing that triggers correctly, imperative instructions, no dead references) to all seven skills.

---

## Task 10: novel-seed skill

**Files:**
- Create: `plugin/autonovel/skills/novel-seed/SKILL.md`
- Create: `plugin/autonovel/skills/novel-seed/references/seed-prompts.md`

- [ ] **Step 1: Write `references/seed-prompts.md`** — port both prompts from seed.py verbatim: the system persona (seed.py:40–46), `GENERATE_PROMPT` (seed.py:59–95) and `RIFF_PROMPT` (seed.py:97–115), un-templated (`{count}` → "ten" in the generate prompt; the riff prompt keeps a `<the user's idea>` slot described in prose). These are already generic — no de-Bells needed.

- [ ] **Step 2: Write `SKILL.md`**:

```markdown
---
name: novel-seed
description: Start a new novel project — generate seed concepts, pick one, and initialize a project directory with its own git repo, templates, and pipeline state. Use when the user wants to start a new novel, generate story seed ideas, or riff on a story concept.
---

# Novel Seed — Start a New Novel Project

Creates a standalone novel project directory (its own private git repo —
novel content never lives in the plugin or any public repo) and writes the
chosen seed concept. This is the only autonovel skill that runs outside an
existing project.

## Steps

1. **Location.** Ask the user where the project should live unless they
   already said. Default suggestion: `~/novels/<tag>` where `<tag>` is a
   short kebab-case slug. Never nest inside another git repo.

2. **Initialize the project:**
   - `mkdir -p <dir> && cd <dir> && git init`
   - Copy every file from `${CLAUDE_PLUGIN_ROOT}/shared/templates/` into it
     (voice.md, world.md, characters.md, outline.md, canon.md, MYSTERY.md,
     state.json).
   - `mkdir chapters eval_logs edit_logs briefs`
   - Create `results.tsv` containing exactly this header line:
     `timestamp	phase	score	words	keep_discard	description`

3. **Generate concepts.** Read `references/seed-prompts.md` (in this
   skill's directory). If the user supplied an idea, use the riff prompt
   (5 variations); otherwise the generate prompt (10 concepts). Write the
   concepts yourself, in-session, following every constraint in the prompt
   — the diversity requirements and the DO-NOT list are hard rules.

4. **Selection.** Present the concepts compactly (title + hook + cost)
   and ask the user to pick, remix, or reroll. If the user asked for a
   fully autonomous run, pick the concept with the strongest interlock
   between the magic's cost and the central tension, and say which you
   picked and why.

5. **Write `seed.txt`** with the full chosen concept. Verify it contains
   all four required elements — world-differentiator, central tension,
   cost/constraint, sensory hook — and strengthen any that are missing
   before saving.

6. **Commit:** `git add -A && git commit -m "seed: <title>"`

7. **Report:** project path, chosen title/hook, and next step:
   `cd <dir>` then `/autonovel:novel-foundation`.
```

- [ ] **Step 3: Validate and commit**

Run: `claude plugin validate plugin` → pass.

```bash
git add plugin/autonovel/skills/novel-seed
git commit -m "feat: add novel-seed skill"
```

---

## Task 11: novel router skill

**Files:**
- Create: `plugin/autonovel/skills/novel/SKILL.md`

- [ ] **Step 1: Write `SKILL.md`**:

```markdown
---
name: novel
description: Show the status of an autonovel project and what to run next. Use when the user asks where their novel stands, wants to resume novel work, says "continue the novel", or needs to know which pipeline phase comes next.
---

# Novel — Pipeline Status and Router

Read-only. This skill NEVER modifies project files, commits, or resets.

## Steps

1. **Locate the project.** The project is the current working directory
   if it contains `state.json` and `voice.md`. If not, say this isn't a
   novel project and offer: start one with `/autonovel:novel-seed`, or
   have the user `cd` to (or name) an existing project. `seed.txt` is
   OPTIONAL — projects imported or hand-built without one are valid.

2. **Gather state** (read, don't infer):
   - `state.json` — phase, iteration, scores, revision_cycle,
     review_round, debts
   - last 15 lines of `results.tsv`
   - `git log --oneline -10` and `git status --porcelain`
   - chapter count: `ls chapters/ch_*.md | wc -l` and total words
   - newest files in `eval_logs/`, `edit_logs/`, `briefs/`

3. **Report** in a short table + prose: current phase and iteration;
   scores against their gates (foundation > 7.5 AND lore > 7.0;
   chapters > 6.0; revision plateau Δ < 0.5 across 2 cycles); chapters
   drafted vs planned; pending debts from state.json; and a WARNING if
   the git tree is dirty (uncommitted work from an interrupted run —
   the user should inspect before any phase skill runs).

4. **Recommend exactly one next action:**
   - phase `foundation` → `/autonovel:novel-foundation`
   - phase `drafting`  → `/autonovel:novel-draft`
   - phase `revision`  → `/autonovel:novel-revise`; but if
     `revision_cycle >= 3` and the last two full-novel scores in
     results.tsv differ by < 0.5 → `/autonovel:novel-review`
   - phase `review`    → `/autonovel:novel-review`
   - phase `export`    → `/autonovel:novel-export`
   - phase `done`      → congratulate; point at the PDF/ePub outputs.
```

- [ ] **Step 2: Validate and commit**

Run: `claude plugin validate plugin` → pass.

```bash
git add plugin/autonovel/skills/novel
git commit -m "feat: add novel router skill"
```

---

## Task 12: novel-foundation skill

**Files:**
- Create: `plugin/autonovel/skills/novel-foundation/SKILL.md`
- Create: `plugin/autonovel/skills/novel-foundation/references/layer-guides.md`

- [ ] **Step 1: Write `references/layer-guides.md`** — one `##` section per layer, ported from the gen scripts' prompts with the story-specific section names genericized:

- `## world.md` — from gen_world.py:52–122. Replace the Bells-specific section headers: `"### Hard Rules (Tonal Law)"` → `"### Hard Rules"` with instruction "name the magic system what the seed calls it"; `"### Soft Magic (Cass's Gift)"` → `"### Soft Magic / The Protagonist's Exception"` described generically ("what the protagonist perceives or does that others can't, how it works, what it costs THEM specifically"); `"Cantamura's physical layout"` → `"the primary setting's physical layout"`. Keep everything else verbatim: craft requirements, all 8 document sections, the IMPORTANT list (specificity, costs, iceberg, interconnection, 3000–4000 word target).
- `## characters.md` — from gen_characters.py's prompt (read the file; same port pattern): wound/want/need/lie chains, three-slider profiles, arc types, distinct speech patterns with example lines, one secret each.
- `## outline.md part 1` — from gen_outline.py's prompt: Save the Cat beats at % marks, per-chapter beats/POV/emotional arc, try-fail cycle types (yes-but / no-and), MICE threads closing in reverse order, escalating stakes.
- `## outline.md part 2 (foreshadowing ledger)` — from gen_outline_part2.py's prompt: every plant with its planned payoff chapter, ledger must balance.
- `## voice discovery` — from program.md:169–178 verbatim (write 5 trial passages in different registers, select, refine, exemplars + anti-exemplars into voice.md Part 2), plus: "After filling voice.md Part 2, also write `voice_wells.json` in the project root: `{\"<well_name>\": [words...], ...}` listing 2–4 vocabulary wells (domains the POV character thinks in) with 30–60 words each. The mechanical voice fingerprint script reads this file."
- `## MYSTERY.md` — the central secret the reader discovers; the author must know the full answer (no "to be revealed" handwaving — the foundation rubric scores that as a gap).
- `## canon.md` — from gen_canon.py's prompt: extract every hard fact from world.md/characters.md/outline.md into categorized, sourced entries; target 400+ entries before exiting foundation.

- [ ] **Step 2: Write `SKILL.md`**:

```markdown
---
name: novel-foundation
description: Run the foundation phase of an autonovel project — build and iterate the world bible, characters, outline, voice, mystery, and canon until they pass the score gates. Use when a novel project is in the foundation phase or the user asks to build/improve the novel's foundation.
---

# Novel Foundation — Phase 1

Builds the five planning layers and iterates until
`foundation_score > 7.5 AND lore_score > 7.0`. No prose chapters are
written in this phase. Typical runs take 5–15 iterations.

## Setup

1. Verify the project (state.json + voice.md in CWD) and clean git tree.
   Confirm `state.json` phase is `foundation` (if later, ask before
   re-running foundation).
2. Required reading, every session, before writing anything:
   - `${CLAUDE_PLUGIN_ROOT}/shared/craft/CRAFT.md`
   - `${CLAUDE_PLUGIN_ROOT}/shared/craft/ANTI-SLOP.md`
   - the project's `voice.md` Part 1 (guardrails)
   - `references/layer-guides.md` in this skill's directory
   - the project's `seed.txt` if present; otherwise derive the premise
     from whatever layer docs already exist (imported projects).

## First iteration (empty templates)

Fill the layers IN THIS ORDER, following the matching section of
layer-guides.md for each: world.md → characters.md → outline.md part 1 →
foreshadowing ledger (outline.md part 2) → voice discovery (voice.md
Part 2 + voice_wells.json) → MYSTERY.md → canon.md. Every hard fact you
add to any layer gets a canon.md entry at the same time.

## Iteration loop

1. **Evaluate:** dispatch a judge subagent with rubric `foundation.md`
   over voice.md, world.md, characters.md, outline.md, canon.md.
   Save the JSON verbatim to `eval_logs/<UTC yyyymmdd_hhmmss>_foundation.json`.
2. **Gate check:** if `overall_score > 7.5` AND `lore_score > 7.0` →
   exit loop.
3. **Target the weakest dimension** (the rubric names it and gives
   top_3_improvements). Revise THAT layer's document. While revising, run
   the cross-layer consistency checks: outline references only lore that
   exists; character abilities match magic rules; the foreshadowing
   ledger balances; canon captures all new facts.
4. **Keep/discard** per the shared convention (phase=foundation, score=
   overall_score). A discarded iteration still counts — record it, and
   attack the same dimension differently next time.
5. **Iteration cap:** after 15 iterations without passing the gate, stop
   and report the best score, the stubborn dimension, and options.

## Fight the Stability Trap (from program.md — these are hard rules)

Characters must end truly different from how they began. Let bad things
stay bad. Allow irreversible loss. Withhold information. Create genuine
moral ambiguity. If a choice has no real cost, it is not a real choice.

## Exit

Set state.json: `phase: "drafting"`, `chapters_total: <count from
outline>`, reset `iteration: 0`. Commit. Notify (pushover): final scores,
iterations used, next step `/autonovel:novel-draft`.
```

- [ ] **Step 3: Validate and commit**

Run: `claude plugin validate plugin` → pass. Then `grep -in 'cass\|cantamura\|tonal' plugin/autonovel/skills/novel-foundation/` → no output.

```bash
git add plugin/autonovel/skills/novel-foundation
git commit -m "feat: add novel-foundation skill with layer guides"
```

---

## Task 13: novel-draft skill

**Files:**
- Create: `plugin/autonovel/skills/novel-draft/SKILL.md`
- Create: `plugin/autonovel/skills/novel-draft/references/drafting-rules.md`

- [ ] **Step 1: Write `references/drafting-rules.md`** — port draft_chapter.py's writer system prompt (lines 32–40) and the 24 numbered writing instructions (lines 110–153), de-Bellsed:

- Rule 2 `"locked to Cass's POV"` → `"locked to the chapter's designated POV character (from the outline)"`
- Rule 5 `"what Cass hears, smells, feels physically"` → `"what the POV character hears, smells, feels physically"`
- Rule 6 (the under-note/needle rule) → generalize the principle it encodes: `"Magic and its costs manifest as SPECIFIC physical sensation defined in world.md — never vague discomfort. Use the exact established sensations."`
- Rule 11 `"Metaphors from Cass's experience: sound, bronze, craft..."` → `"Metaphors from the POV character's experience — their trade, their body, their world. Pull vocabulary from the wells in voice_wells.json."`
- Rule 21 `"Do NOT end with Cass outside listening to his father work"` → `"Do NOT reuse an ending shape from any previous chapter. Find the ending that belongs to THIS chapter specifically."`
- Rule 24's `"A 14-year-old does not speak in polished epigrams"` → `"Characters speak like their documented age and background, not in polished epigrams."`

All other rules verbatim (they're already generic). Keep the 1–13 core rules and 14–24 anti-pattern rules as two labeled groups, because the anti-pattern group exists to counter freshness decay after chapter ~6.

- [ ] **Step 2: Write `SKILL.md`**:

```markdown
---
name: novel-draft
description: Run the drafting phase of an autonovel project — write chapters sequentially with per-chapter evaluation, slop scoring, and keep/discard gates. Use when a novel project is in the drafting phase or the user asks to draft chapters.
---

# Novel Draft — Phase 2

Writes chapters in outline order. Keep at score > 6.0 (after slop
penalty), max 5 attempts per chapter. Forward progress over perfection:
a 6.0 ships; revision is Phase 3's job.

## Setup

1. Verify project, clean git tree, `state.json` phase is `drafting`.
2. Required reading: `${CLAUDE_PLUGIN_ROOT}/shared/craft/CRAFT.md`,
   `ANTI-SLOP.md`, `ANTI-PATTERNS.md`; the project's `voice.md` (both
   parts); `references/drafting-rules.md` in this skill's directory.
3. Resume point: next chapter = highest existing `chapters/ch_NN.md` + 1.

## Per-chapter loop (repeat for each chapter through chapters_total)

1. **Load context — exactly this, fresh each chapter:**
   - voice.md (full), world.md (full), characters.md (full)
   - THIS chapter's outline entry (including its Plants list)
   - the previous chapter's last ~1000 words
   - the NEXT chapter's outline entry (first ~10 lines, for continuity)
2. **Write `chapters/ch_NN.md`** — the complete chapter, target ~3,200
   words (or the outline entry's stated target), following every rule in
   drafting-rules.md. Title line format: `# Chapter N: <Title>`.
3. **Mechanical score:**
   `python3 ${CLAUDE_PLUGIN_ROOT}/shared/scripts/slop_score.py chapters/ch_NN.md`
4. **Judge:** dispatch a judge subagent with rubric `chapter.md` over the
   layer files + this chapter (+ previous chapter). Save JSON to
   `eval_logs/<timestamp>_chNN.json`.
5. **Final score** = judge `overall_score` minus the script's
   `slop_penalty` (floor 0). This mirrors the original pipeline's
   independent mechanical adjustment.
6. **Gate:** score > 6.0 → keep (commit `draft: ch NN (<score>)`, log to
   results.tsv). Otherwise discard (`git checkout -- chapters/ eval_logs/`
   or reset if committed), and retry with a DIFFERENT approach informed
   by the judge's three_weakest_sentences and top_3_revisions — up to 5
   attempts, then keep the best-scoring attempt anyway, log it as
   `keep (best-of-5)`, and move on.
7. **Canon:** append the judge's `new_canon_entries` to canon.md
   (sourced: `[ch NN]`). If writing revealed a lore gap, log a debt in
   state.json: `{"trigger": "ch_NN: <gap>", "affected": [files],
   "status": "pending"}`.
8. Update state.json `chapters_drafted`.

## Post-draft cleanup (after the last chapter)

1. Slop pass over everything:
   `python3 ${CLAUDE_PLUGIN_ROOT}/shared/scripts/slop_score.py chapters/ch_*.md`
   Fix every tier-1 hit and any chapter whose penalty > 2.0, by direct
   edit (no rewrites — surgical word/sentence fixes only). Commit.
2. Set state.json `phase: "revision"`, commit.
3. Notify (pushover): chapters drafted, mean/min scores, total words,
   next step `/autonovel:novel-revise`.

## Session-length note

Drafting 20+ chapters exceeds one session. After EVERY chapter commit the
project is resumable: a fresh session in the project directory runs this
skill and picks up at the resume point. Prefer stopping cleanly at a
chapter boundary over drafting into a degraded context.
```

- [ ] **Step 3: Validate and commit**

Run: `claude plugin validate plugin` → pass; leakage grep on the new skill dir → clean.

```bash
git add plugin/autonovel/skills/novel-draft
git commit -m "feat: add novel-draft skill with drafting rules"
```

## Task 14: novel-revise skill

**Files:**
- Create: `plugin/autonovel/skills/novel-revise/SKILL.md`
- Create: `plugin/autonovel/skills/novel-revise/references/revision-playbook.md`

- [ ] **Step 1: Write `references/revision-playbook.md`** — port the structural-revision recipes from PIPELINE.md:216–260 (the a–f consensus-item playbook: cut candidate, missing scene, thin character, weak scene, consistency/timeline, chapter renumbering) and PIPELINE.md:263–301 (the eval-callout patterns: pacing, short chapters, repeated phrases, unresolved threads), plus the danger list from PIPELINE.md:402–410 (over-compression below 1800w — sweet spot 2200–3000w; expansion bloat ~+30% over brief; score chasing after cycle 4; weakest-chapter whack-a-mole — stop after 2 rotations). Also port gen_revision.py's anti-pattern rule block (gen_revision.py:84–95) as the "rewrite rules" section every chapter rewrite must follow. All of this is already generic — port verbatim with markdown cleanup.

- [ ] **Step 2: Write `SKILL.md`**:

```markdown
---
name: novel-revise
description: Run the automated revision phase of an autonovel project — adversarial edit cuts, reader panel, revision briefs, and chapter rewrites in score-gated cycles until scores plateau. Use when a novel project is in the revision phase or the user asks to revise the draft.
---

# Novel Revise — Phase 3a

Revision cycles: diagnose (cuts + panel) → fix (briefs + rewrites) →
measure (full-novel score). Stop on plateau: full-novel score change
< 0.5 across 2 consecutive cycles, minimum 3 cycles, maximum 6.

## Setup

1. Verify project, clean tree, phase `revision`. Read
   `${CLAUDE_PLUGIN_ROOT}/shared/craft/ANTI-PATTERNS.md`, the project's
   voice.md, and `references/revision-playbook.md` (this skill's dir).
2. Resume: state.json `revision_cycle` is the last COMPLETED cycle.

## One cycle (state.json revision_cycle = N)

### Diagnose

1. **arc_summary.md** — regenerate it: for each chapter, 4–6 sentence
   event summary + opening and closing ~100-word passages + 1–2 key
   dialogue exchanges. First line of the file:
   `Novel: <total words> words across <count> chapters.`
   (This replaces build_arc_summary.py; the panel judges read this file.)
2. **Adversarial edit** — for EACH chapter, dispatch a judge subagent
   with rubric `adversarial-edit.md` over that chapter. Save each JSON to
   `edit_logs/chNN_cuts.json` (exact filename — apply_cuts.py globs it).
   Dispatch in parallel batches of 4–6.
3. **Apply mechanical cuts:**
   `python3 ${CLAUDE_PLUGIN_ROOT}/shared/scripts/apply_cuts.py all --types OVER-EXPLAIN REDUNDANT --min-fat 15`
   Review the FAIL lines; apply any failed high-value cuts by hand.
   Commit: `cycle N: adversarial cuts`.
4. **Reader panel** — dispatch FOUR judge subagents (parallel), one per
   persona in rubric `reader-panel.md`, each over arc_summary.md; tell
   each its assigned persona. Assemble
   `edit_logs/reader_panel.json`: `{"readers": {editor: {...}, ...},
   "consensus": [...], "disagreements": [...]}` where consensus = any
   chapter/character/scene named by 3+ readers for the same question.

### Fix (consensus items, priority order per the playbook)

For each consensus item: generate a brief
(`python3 ${CLAUDE_PLUGIN_ROOT}/shared/scripts/gen_brief.py --panel <ch>`
or `--cuts <ch>`; use `--eval <ch>` after evals exist this cycle), then
REWRITE the chapter in-session following the brief + the playbook's
rewrite rules, with the same context recipe as drafting (voice/world/
characters + adjacent chapter boundaries) plus the old chapter text as
raw material. Then re-judge with rubric `chapter.md` + slop script,
keep/discard per shared convention (`cycle N: <item type> ch NN`).

### Measure

1. Dispatch a judge subagent with rubric `full-novel.md` (over layer
   files + arc_summary.md — regenerate summaries for rewritten chapters
   first). Log score to results.tsv (phase=revision).
2. Address the eval's `top_suggestion` if actionable this cycle (playbook
   has the recipes); at most 2 such fixes per cycle.
3. Set state.json `revision_cycle: N`, commit `cycle N complete: <score>`.
4. **Plateau check:** if N >= 3 and |score(N) - score(N-1)| < 0.5 and
   |score(N-1) - score(N-2)| < 0.5 → stop.

## Exit

Set phase `review`. Run the voice fingerprint for the record:
`python3 ${CLAUDE_PLUGIN_ROOT}/shared/scripts/voice_fingerprint.py`.
Commit. Notify: cycles run, score trajectory, next step
`/autonovel:novel-review`.

## Guardrails (from the playbook — non-negotiable)

Never compress a chapter below 1800 words. Expect rewrites to run ~30%
long — brief for shorter than you want. After a weakest-chapter fix,
if the eval names a NEW weakest chapter twice in a row, stop chasing.

## Optional cycle-1 diagnostic: chapter tournament

If the user asks for a deeper diagnosis (or the panel and cuts disagree
about which chapters are weakest), run head-to-head comparisons: dispatch
judge subagents given two chapters each and asked only "which is the
stronger chapter and why — one paragraph, then WINNER: NN". Seed pairings
from the per-chapter judge scores (adjacent ranks play each other).
Rankings inform which chapters get briefs first. Skip this by default —
it is diagnostic, not required.
```

- [ ] **Step 3: Validate and commit**

Run: `claude plugin validate plugin` → pass; leakage grep → clean.

```bash
git add plugin/autonovel/skills/novel-revise
git commit -m "feat: add novel-revise skill with revision playbook"
```

---

## Task 15: novel-review skill

**Files:**
- Create: `plugin/autonovel/skills/novel-review/SKILL.md`

- [ ] **Step 1: Write `SKILL.md`**:

```markdown
---
name: novel-review
description: Run the deep manuscript review loop on an autonovel project — full-novel dual-persona review (literary critic + professor of fiction) with parsed actionable items and stopping conditions. Use when a novel project is in the review phase or the user asks for a full manuscript review.
---

# Novel Review — Phase 3b

The final quality push. A fresh clean-room subagent reads the ENTIRE
manuscript and reviews it twice: as a literary critic, then as a
professor of fiction. Fix the top items; repeat. Maximum 4 rounds
(state.json `review_round` tracks completed rounds).

## One round

1. **Build the manuscript:** concatenate `chapters/ch_*.md` in order,
   separated by `\n\n---\n\n`, into `manuscript.md` (gitignored is fine;
   it's derived).
2. **Review:** dispatch a judge subagent with rubric
   `manuscript-review.md` over manuscript.md. Request the strongest
   available model for this subagent (pass a model override to the Agent
   tool if available — literary judgment is the one place model quality
   dominates). Save the returned markdown to
   `edit_logs/<timestamp>_review.md`.
3. **Parse the tags** (each professor item carries
   `[severity: ...] [type: ...] [qualified: ...]`). Count: total items,
   major-unqualified items, qualified items, star rating.
4. **STOPPING CONDITIONS — stop revising when ANY holds:**
   - zero major unqualified items
   - qualified items > 50% of total items
   - total items <= 2
   - review_round >= 4
   Also recognize the qualitative signal: when the reviewer's language
   shifts from "the novel has problems" to "these are the costs of
   ambition," you are done. An item persisting across 3+ rounds is
   probably structural to the novel's approach — accept it.
5. **Fix the top items** (highest severity, unqualified first):
   - type compression/revision → brief via
     `python3 ${CLAUDE_PLUGIN_ROOT}/shared/scripts/gen_brief.py --eval <ch>`
     (or hand-write the brief from the item text into `briefs/`), rewrite
     the chapter in-session per the novel-revise skill's rewrite rules,
     re-judge with rubric `chapter.md` + slop script, keep/discard.
   - type mechanical (tics, repeated phrases) → grep the phrase across
     all chapters, fix every instance but the strongest, by direct edit.
   - type addition → surgical patch if < 400 words, else brief + rewrite.
   - type structural → present to the user before acting; structural
     changes this late are a decision, not a default.
6. Set `review_round`, commit `review round N: <items> items, <fixed> fixed`,
   log to results.tsv (phase=review, score=stars).

## Exit

Set phase `export`. Commit. Notify: rounds, final star rating, stop
reason, next step `/autonovel:novel-export`.
```

- [ ] **Step 2: Validate and commit**

Run: `claude plugin validate plugin` → pass.

```bash
git add plugin/autonovel/skills/novel-review
git commit -m "feat: add novel-review skill"
```

---

## Task 16: novel-export skill

**Files:**
- Create: `plugin/autonovel/skills/novel-export/SKILL.md`

- [ ] **Step 1: Write `SKILL.md`**:

```markdown
---
name: novel-export
description: Export a finished autonovel project to a typeset PDF and ePub. Use when a novel project reaches the export phase or the user asks to typeset, export, or build the book.
---

# Novel Export — Phase 4

Produces `typeset/novel.pdf` (LaTeX via tectonic) and `<title>.epub`
(pandoc) inside the novel project.

## Steps

1. Verify project and clean tree. **Tool check:** `which tectonic` and
   `which pandoc`. If missing, tell the user:
   `brew install tectonic pandoc` — and stop for whichever is needed.
2. **Normalize chapter titles:** every `chapters/ch_NN.md` must start
   `# Chapter N: <Title>` (single `#`, sequential N matching the
   filename). Fix any drift by direct edit; commit if changed.
3. **Stage the typeset assets:** `mkdir -p typeset`; copy every file
   from `${CLAUDE_PLUGIN_ROOT}/shared/typeset/` into `typeset/` ONLY if
   not already present (a project's customized copies win).
4. **Fill the placeholders** in `typeset/novel.tex` (NOVEL-TITLE,
   NOVEL-TITLE-SHORT, NOVEL-AUTHOR, NOVEL-EPIGRAPH, NOVEL-END-TEXT) and
   `typeset/epub_metadata.yaml` (title/author). Title from outline.md's
   first heading; author from the user (ask once; suggest git
   user.name). Epigraph: choose a resonant NON-SPOILER line from the
   novel text itself and confirm with the user.
5. **Build the LaTeX body:** `python3 typeset/build_tex.py` (the staged
   copy — it reads chapters/ from CWD). Then compile:
   `tectonic typeset/novel.tex`. Fix any LaTeX escaping errors it
   reports by editing build_tex.py's output handling, not the chapters.
6. **Build the ePub:**
   `pandoc typeset/epub_front_matter.md chapters/ch_*.md typeset/epub_colophon.md --metadata-file=typeset/epub_metadata.yaml --css=typeset/epub_style.css --toc -o "<title-slug>.epub"`
7. Set state.json `phase: "done"`. Commit
   `export: <title> — <word count> words`. Notify: word count, output
   paths, and that the novel is done.
```

- [ ] **Step 2: Validate and commit**

Run: `claude plugin validate plugin` → pass.

```bash
git add plugin/autonovel/skills/novel-export
git commit -m "feat: add novel-export skill"
```

---

## Task 17: Remove replaced scripts and update repo docs

**Files:**
- Delete: `seed.py`, `gen_world.py`, `gen_characters.py`, `gen_outline.py`, `gen_outline_part2.py`, `gen_canon.py`, `draft_chapter.py`, `run_drafts.py`, `gen_revision.py`, `adversarial_edit.py`, `compare_chapters.py`, `reader_panel.py`, `review.py`, `build_arc_summary.py`, `build_outline.py`, `evaluate.py`, `run_pipeline.py`, `main.py`, `apply_cuts.py`, `gen_brief.py`, `voice_fingerprint.py`, `typeset/build_tex.py`, `typeset/novel.tex`, `typeset/epub_*`
- Delete: root `voice.md`, `world.md`, `characters.md`, `outline.md`, `canon.md`, `MYSTERY.md`, `state.json`, `results.tsv`, `chapters/.gitkeep`, `program.md`, `WORKFLOW.md`
- Keep untouched: `gen_art.py`, `gen_art_directions.py`, `gen_audiobook.py`, `gen_audiobook_script.py`, `gen_cover_composite.py`, `gen_cover_print.py`, `audiobook_voices.json`, `landing/`, `.env.example` (art/audiobook still need FAL/ElevenLabs keys), `pyproject.toml`, `uv.lock` (art scripts + tests still need them), `CRAFT.md` etc. already moved in Task 2
- Modify: `README.md`

- [ ] **Step 1: Delete the replaced files**

```bash
git rm seed.py gen_world.py gen_characters.py gen_outline.py gen_outline_part2.py gen_canon.py draft_chapter.py run_drafts.py gen_revision.py adversarial_edit.py compare_chapters.py reader_panel.py review.py build_arc_summary.py build_outline.py evaluate.py run_pipeline.py main.py apply_cuts.py gen_brief.py voice_fingerprint.py
git rm typeset/build_tex.py typeset/novel.tex typeset/epub_metadata.yaml typeset/epub_style.css typeset/epub_front_matter.md typeset/epub_back_cover.md typeset/epub_colophon.md
git rm voice.md world.md characters.md outline.md canon.md MYSTERY.md state.json results.tsv chapters/.gitkeep program.md WORKFLOW.md
```

Note: PIPELINE.md, ANTI-* and CRAFT.md content lives on inside the plugin (Task 2) and in the skills; `program.md`'s content was absorbed into the skills in Tasks 12–14. PIPELINE.md itself **stays at root** as historical methodology documentation — add a header line to it: `> Historical reference. The pipeline now ships as Claude Code skills — see plugin/autonovel/.`

- [ ] **Step 2: Rewrite README.md** — keep the project story (what autonovel is, the Bells production history, the two-immune-systems explanation, inspiration links) but replace the Quick Start and the 27-script tool tables with:

```markdown
## Quick Start (Claude Code skills)

This fork packages the pipeline as a Claude Code plugin. No API keys —
Claude Code is the runtime.

    /plugin marketplace add /path/to/autonovel/plugin
    /plugin install autonovel@autonovel-dev

Then, in any directory:

    /autonovel:novel-seed        # create a novel project + pick a seed
    cd ~/novels/<your-novel>
    /autonovel:novel-foundation  # build world/characters/outline/voice
    /autonovel:novel-draft       # write chapters, score-gated
    /autonovel:novel-revise      # adversarial cuts + reader panel cycles
    /autonovel:novel-review      # dual-persona manuscript review loop
    /autonovel:novel-export      # typeset PDF + ePub
    /autonovel:novel             # status + what to run next, anytime

Each novel lives in its own directory with its own git repo. The
art/audiobook scripts (fal.ai / ElevenLabs) remain as standalone Python
tools at the repo root and still use `.env` keys.
```

- [ ] **Step 3: Full-repo leakage and reference check**

Run: `grep -rn 'evaluate\.py\|draft_chapter\|run_pipeline' plugin/ README.md`
Expected: no references to deleted scripts anywhere in the plugin or README (PIPELINE.md's historical references are fine).

- [ ] **Step 4: Run all tests**

Run: `uv run pytest tests/ -v`
Expected: all pass (deletions must not break the plugin scripts' tests).

- [ ] **Step 5: Commit**

```bash
git add -A && git commit -m "feat: remove API-wrapper scripts replaced by skills; update README"
```

---

## Task 18: Install locally and verify the plugin end-to-end

- [ ] **Step 1: Validate manifests**

Run: `claude plugin validate plugin`
Expected: pass, listing the autonovel plugin with 7 skills.

- [ ] **Step 2: Install from the local marketplace** — this must be done in an interactive Claude Code session (the user's, or the implementing session if it has plugin commands available):

```
/plugin marketplace add /Users/brent/code/autonovel/plugin
/plugin install autonovel@autonovel-dev
```

Then verify `claude plugin list --json` shows autonovel, and the skills appear in the session's skill listing as `autonovel:novel`, `autonovel:novel-seed`, etc. If slash commands are unavailable to the implementing session, hand the user these exact commands and wait for confirmation.

- [ ] **Step 3: Verify ${CLAUDE_PLUGIN_ROOT} resolution** — invoke `/autonovel:novel` in a non-project directory; expect the "not a novel project" guidance (proves the skill loads and runs). Then check one skill's rendered content references resolve: the paths under `${CLAUDE_PLUGIN_ROOT}/shared/` must exist in the installed copy.

- [ ] **Step 4: Commit any fixes discovered; no commit if clean.**

---

## Task 19: Smoke test — bounded pipeline run

- [ ] **Step 1: Seed a throwaway project.** Invoke `/autonovel:novel-seed`, target directory `/tmp/novel-smoke` (explicit user-requested tmp location is fine here), auto-pick mode. Verify: directory created, git repo initialized, templates copied, `seed.txt` written, initial commit exists, `results.tsv` has its header.

- [ ] **Step 2: One bounded foundation iteration.** Invoke `/autonovel:novel-foundation` with the instruction "run exactly one iteration then stop regardless of score." Verify afterwards:
  - world.md, characters.md, outline.md, voice.md Part 2, MYSTERY.md, canon.md, `voice_wells.json` all populated
  - `eval_logs/` contains one `*_foundation.json` with numeric `overall_score` and `lore_score`
  - `results.tsv` gained a row; `git log` shows the iteration commit
  - `grep -ril 'cantamura\|house of bells' /tmp/novel-smoke` → no output (the generated novel must be its own story)

- [ ] **Step 3: Mechanical-script integration check** (in the smoke project):

```bash
python3 <plugin-install-path>/shared/scripts/slop_score.py world.md
python3 <plugin-install-path>/shared/scripts/voice_fingerprint.py || true
```

slop_score prints JSON; voice_fingerprint reports "No chapters found" cleanly (no traceback).

- [ ] **Step 4: Report results to the user** — what passed, anything flaky (judge JSON retries, path issues), and the recommendation for the first real novel run. Clean up `/tmp/novel-smoke` only with the user's OK.

- [ ] **Step 5: Final commit + wrap-up.** Any fixes from the smoke test get their own commits (work is on master by prior agreement — no branch-finishing flow). Final checks: `uv run pytest tests/ -v` (all green) and `claude plugin validate plugin` (pass). Summarize for the user what's ready to copy to the marketplace repo (`plugin/autonovel/`).

---

## Deviations log

(The executing engineer appends dated notes here when reality forces a change from the plan.)

- 2026-08-05, Task 2: ANTI-PATTERNS.md contained two story-specific teaching examples ("wrong-pitched bells", "Cass outside listening") that tripped the leakage grep; genericized both in the plugin copy (kept concrete imagery per quality review).
- 2026-08-05, Task 4: the plan's FAT-cut fixture quote was 30 chars — over MIN_QUOTE_LEN=25 — so it would be applied, not skipped. Test fixture shortened to "tallow and wet wool" (19 chars); script untouched.
- 2026-08-05, Tasks 10–16 (skills phase): per superpowers:writing-skills conventions, skill descriptions are trigger-only ("Use when…", no workflow summaries). The writing-skills TDD cycle (baseline pressure-testing per skill) is replaced by the plan's user-approved validation strategy: plugin validate per task, local install (Task 18), bounded smoke run (Task 19).
- 2026-08-05, Task 10: usability review hardened novel-seed beyond the plan draft — pre-existing-directory STOP-and-ask, parent-git-repo nesting check, quoted ${CLAUDE_PLUGIN_ROOT} cp command, absolute-path rule, and seed checklist reworded to seed-prompts.md field names. Apply the same patterns (quoting, absolute paths, safety checks) to Tasks 11–16.
- 2026-08-05, Task 12: two plan bugs fixed in review — the plan's discard command guidance was inverted (correct: `git reset --hard HEAD`; untracked eval logs survive) and the plan's layer order built world/characters/outline before their voice/MYSTERY inputs existed (correct order: voice discovery → world → characters → MYSTERY → outline pt1 → ledger → canon). Also added: resume-mid-foundation path; state.json best-score persistence per kept iteration; lie-shattered-by-climax ledger rule; canon 80–120→400+ reconciliation. CONVENTIONS FOR TASKS 13–16: discard = `git reset --hard HEAD`; persist best scores in state.json each kept step; judge dispatches label target/previous chapter paths; novel-revise logs full-novel evals to results.tsv with description starting "full-eval" so the router can find them.
- 2026-08-05, Task 16: epub_front_matter.md had off-convention placeholders (**NOVEL TITLE**, *Author Name*) — retokenized to NOVEL-*. Export skill's placeholder verification scoped into two passes (NOVEL- across typeset/; bare tokens only in epub_metadata.yaml) after review showed a global bare-token grep false-positives on novel.tex comments and risks corrupting NOVEL-* tokens.
- 2026-08-05, Task 15: review surfaced a pipeline-wide gap — novel-seed projects had no .gitignore, so the untracked-eval_logs invariant the draft/revise skills depend on didn't hold. Added shared/templates/gitignore (installed by novel-seed via mv) covering eval_logs/, edit_logs/, briefs/, manuscript.md, typeset artifacts. novel-review hardened: grep-based item→chapter mapping scoped to compression/addition/revision types, required reading of novel-revise's Fix stage, per-item structural queueing, 4-item/round cap, explicit staging. Star-based stop conditions from review.py deliberately not used (PIPELINE.md's prose conditions are the methodology source).
- 2026-08-05, Task 13: review-driven mechanics fixes beyond the plan — per-attempt scratch copies to eval_logs/ch_NN_attempt_<k>.md (untracked, survive discards) with cp-based best-of-5 restore; attempt rows logged to untracked eval_logs/attempts.tsv and folded into results.tsv at commit time (tracked-file rows would be wiped by discard resets); state.json updated before the commit; noscore = failed attempt; canon tags (ch_NN). Tasks 14/15 reuse these conventions for chapter rewrites.
- 2026-08-05, Task 14: SKILL.md written from a refined spec (superseding the plan's Task 14 draft) that folds in Task 13's conventions for chapter rewrites — scratch-copy attempts, attempts.tsv/results.tsv fold-in at commit, discard via `git reset --hard HEAD`, max-attempts gate — plus a router contract: full-novel eval rows in results.tsv get a `full-eval` description prefix so the plateau check can find them (novel/SKILL.md's plateau line extended in the same commit to say so explicitly). references/revision-playbook.md ports PIPELINE.md's consensus-item playbook (a–f), eval-callout patterns (four), and danger list (four) plus gen_revision.py:84–95's anti-pattern block verbatim; all source sections were already leakage-clean (verified by grep before writing) so no genericization was needed beyond markdown formatting. Added beyond the plan draft: malformed-JSON retry-then-skip handling on adversarial-edit dispatch, and an explicit N=6 hard stop alongside the plateau check.
- 2026-08-05, Task 9: usability fixes beyond transcription — manuscript-review gained half-star rating format, severity calibration, and corrected input phrasing; reader-panel gained a no-persona fail-fast; adversarial-edit clarified composing quote-length rules.
- 2026-08-05, Task 8: beyond pure transcription, clean-room usability review drove additions: chapter.md now specifies a labeled target/previous-chapter dispatch contract (with highest-numbered fallback) and chapter-1 handling; full-novel.md gained a missing-arc_summary fail-fast error object and a scoring-calibration anchor the original prompt lacked. CONTRACT FOR TASKS 13–15: judge-dispatch prompts must label the target and previous chapter file paths.
- 2026-08-05, Task 7: the plan's test fixture opened its first paragraph with quoted dialogue, which is incompatible with make_drop_cap() (pre-existing bug, present in the original script: lettrine markup splits the opening quote). Fixture reworded so dialogue isn't the first character; the drop-cap bug was flagged as a separate follow-up task, not fixed in the port. Also: novel.tex de-Bellsing additionally required removing "Hermes Agent"/nous_logo branding (not in the plan's grep pattern) and a NOVEL-GENRE placeholder for pdfsubject. Note for Task 16: epub_metadata.yaml uses bare TITLE/AUTHOR placeholders while novel.tex and other ePub files use NOVEL-* — the export skill must fill both conventions.

