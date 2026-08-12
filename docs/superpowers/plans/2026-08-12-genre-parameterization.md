# Genre Parameterization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move every fantasy-specific assumption out of the autonovel plugin's base files into swappable genre packs, so the pipeline can write any genre — and specifically so a novel without a magic system can clear the foundation gate.

**Architecture:** A genre pack is one markdown file with a JSON frontmatter block and prose sections. Base rubrics, guides, and templates become genre-neutral and carry explicit hooks telling the reader to consult the resolved pack. A `resolve_genre.py` script owns pack resolution and merging so six skills don't each reimplement it in prose; skills pass the resolved pack paths to their judge subagents alongside the rubric path.

**Tech Stack:** Claude Code plugin (markdown skills), stdlib-only Python 3.12, pytest.

**Spec:** `docs/superpowers/specs/2026-08-12-genre-parameterization-design.md`

**Scope:** This plan covers spec phases 1 and 2 — the mechanism, plus the `general` and `fantasy` packs, base-file surgery, and migration. Phases 3–4 (authoring `science-fiction`, `romance`, `mystery`, `thriller`, `erotica`, `ya`, `cozy`) are genre-authoring work and get their own plan.

---

## Key facts for the implementing engineer

- **Repo root:** `/Users/brent/code/autonovel`. Work on `master`. The plugin lives at `plugin/autonovel/`.
- **Scripts are stdlib-only.** No third-party imports in anything under `plugin/autonovel/shared/scripts/`. This is why pack frontmatter is JSON rather than YAML.
- **Scripts run from the novel project directory,** not the plugin. Existing scripts use `BASE_DIR = Path.cwd()`. Follow that.
- **Tests** live in `tests/`, use pytest, and invoke scripts via `subprocess` with `cwd=tmp_path`. Pattern to copy: `tests/test_gen_brief.py`.
- **Run tests with:** `uv run pytest tests/ -v`
- **Plugin path in skill text** is always `${CLAUDE_PLUGIN_ROOT}`, quoted against spaces: `"${CLAUDE_PLUGIN_ROOT}/shared/..."`.
- **The De-Bells rule** (from the original plan): no content from any specific novel may leak into the machinery. Task 20 adds its enforceable successor for genre.
- **Judge dispatch pattern** used throughout the skills: dispatch a fresh `general-purpose` subagent whose prompt is only (1) read a rubric file, (2) read specific project files by absolute path, (3) return only the JSON the rubric specifies. Genre packs join step (1) as additional static reference material — this preserves the clean-room property.
- **Commit after every task.** Conventional-ish messages.

---

## File structure

**New files:**

| Path | Responsibility |
|---|---|
| `plugin/autonovel/shared/scripts/genre_pack.py` | Library: parse and validate one pack. No CLI. |
| `plugin/autonovel/shared/scripts/validate_genre_pack.py` | CLI wrapper around the validator. |
| `plugin/autonovel/shared/scripts/resolve_genre.py` | CLI: read `state.json`, resolve the pack set, merge, print JSON. |
| `plugin/autonovel/shared/genres/TEMPLATE.md` | Annotated skeleton + authoring guide. |
| `plugin/autonovel/shared/genres/general.md` | Neutral default pack. |
| `plugin/autonovel/shared/genres/fantasy.md` | Lossless port of today's fantasy content. |
| `tests/test_genre_pack.py` | Parser + validator unit tests. |
| `tests/test_resolve_genre.py` | Resolution, merge, conflict tests. |
| `tests/test_no_genre_leak.py` | Guard: no genre terms outside `shared/genres/`. |

`genre_pack.py` is a library because both CLIs need it; splitting it keeps each file focused and each testable on its own. Both CLIs live in the same directory, so a plain `import genre_pack` works — Python puts the script's own directory on `sys.path[0]`.

---

## Task 1: Pack parser

**Files:**
- Create: `plugin/autonovel/shared/scripts/genre_pack.py`
- Test: `tests/test_genre_pack.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_genre_pack.py`:

````python
import json
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).parent.parent / "plugin/autonovel/shared/scripts"
sys.path.insert(0, str(SCRIPTS))

import genre_pack  # noqa: E402


def write_pack(tmp_path, name, meta, body=""):
    """Write a pack file and return its path."""
    path = tmp_path / f"{name}.md"
    path.write_text("---\n" + json.dumps(meta, indent=2) + "\n---\n" + body,
                    encoding="utf-8")
    return path


VALID_PRIMARY_META = {
    "name": "testgenre",
    "label": "Test Genre",
    "role": ["primary"],
    "pillar_label": "Test Pillar",
    "weights": {"pillar": 40, "character": 30, "structure": 20, "craft": 10},
    "beat_system": "save-the-cat",
    "shape": {"chapters": [22, 26], "words": [80000, 95000],
              "chapter_words": 3200, "pov_default": "third limited past"},
    "conflicts_with": [],
    "artifacts": [],
}

VALID_PRIMARY_BODY = """
## Framing

- genre_noun — "test novel"

## Pillar Dimensions

- alpha_dim — First criteria.
- beta_dim — Second criteria.
- gamma_dim — Third criteria.

## Drafting Rules

25. Something genre-specific.
"""


def test_parse_returns_meta_sections_and_dimensions(tmp_path):
    path = write_pack(tmp_path, "testgenre", VALID_PRIMARY_META,
                      VALID_PRIMARY_BODY)
    pack = genre_pack.parse_pack(path)
    assert pack["meta"]["name"] == "testgenre"
    assert pack["sections"] == ["Framing", "Pillar Dimensions", "Drafting Rules"]
    assert pack["dimensions"] == ["alpha_dim", "beta_dim", "gamma_dim"]


def test_sub_headings_are_not_sections(tmp_path):
    # SECTION_RE must stay anchored to exactly '## ', not '#{2,}' — a
    # '### Sub' heading is prose structure inside a section, not a pack
    # section Task 2's validator gates on.
    body = "## Framing\n\n### Sub\n\n- genre_noun — \"test novel\"\n"
    path = write_pack(tmp_path, "testgenre", VALID_PRIMARY_META, body)
    pack = genre_pack.parse_pack(path)
    assert pack["sections"] == ["Framing"]
    assert "Sub" not in pack["sections"]


def test_parse_rejects_missing_frontmatter(tmp_path):
    path = tmp_path / "broken.md"
    path.write_text("# Just a heading\n", encoding="utf-8")
    with pytest.raises(genre_pack.PackError, match="frontmatter opener"):
        genre_pack.parse_pack(path)


def test_parse_rejects_unclosed_frontmatter(tmp_path):
    path = tmp_path / "broken.md"
    path.write_text('---\n{"name": "x"}\n', encoding="utf-8")
    with pytest.raises(genre_pack.PackError, match="never closed"):
        genre_pack.parse_pack(path)


def test_parse_rejects_invalid_json(tmp_path):
    path = tmp_path / "broken.md"
    path.write_text("---\n{not json}\n---\n", encoding="utf-8")
    with pytest.raises(genre_pack.PackError, match="not valid JSON"):
        genre_pack.parse_pack(path)


def test_dimensions_only_read_from_pillar_section(tmp_path):
    body = """
## Framing

- genre_noun — "test novel"

## Pillar Dimensions

- alpha_dim — First.
- beta_dim — Second.
- gamma_dim — Third.

## Canon Categories

- geography — not a dimension.
"""
    path = write_pack(tmp_path, "testgenre", VALID_PRIMARY_META, body)
    pack = genre_pack.parse_pack(path)
    assert pack["dimensions"] == ["alpha_dim", "beta_dim", "gamma_dim"]


# --- Fenced code blocks must not corrupt structural parsing -----------------

FENCED_FAKE_SECTION_BODY = """
## Framing

- genre_noun — "test novel"

## Artifacts

Example format:

```
## Pillar Dimensions

- fake_dim — not real.
```

## Pillar Dimensions

- alpha_dim — First criteria.
- beta_dim — Second criteria.
- gamma_dim — Third criteria.

## Drafting Rules

25. Something genre-specific.
"""


def test_fenced_block_does_not_corrupt_sections_or_dimensions(tmp_path):
    path = write_pack(tmp_path, "testgenre", VALID_PRIMARY_META,
                      FENCED_FAKE_SECTION_BODY)
    pack = genre_pack.parse_pack(path)
    assert pack["sections"] == ["Framing", "Artifacts", "Pillar Dimensions",
                                "Drafting Rules"]
    assert pack["dimensions"] == ["alpha_dim", "beta_dim", "gamma_dim"]
    assert "fake_dim" not in pack["dimensions"]
    # The fenced example is still there for humans/LLM judges to read —
    # masking must not leak into the returned body.
    assert "fake_dim" in pack["body"]
    # section_body must slice the ORIGINAL body: a fence inside a section
    # comes back verbatim, not blanked.
    assert "- fake_dim — not real." in genre_pack.section_body(
        pack["body"], "Artifacts")


INDENTED_FENCE_BODY = """
## Framing

- genre_noun — "test novel"

## Artifacts

- clue_ledger.md — Example format:

  ```
  ## Pillar Dimensions

  - fake_dim — not real.
  ```

## Pillar Dimensions

- alpha_dim — First criteria.
- beta_dim — Second criteria.
- gamma_dim — Third criteria.

## Drafting Rules

25. Something genre-specific.
"""


def test_indented_fence_does_not_corrupt_dimensions(tmp_path):
    path = write_pack(tmp_path, "testgenre", VALID_PRIMARY_META,
                      INDENTED_FENCE_BODY)
    pack = genre_pack.parse_pack(path)
    assert pack["dimensions"] == ["alpha_dim", "beta_dim", "gamma_dim"]
    assert "fake_dim" not in pack["dimensions"]


# --- A hyphen or en dash instead of an em dash must be surfaced, not dropped

def test_malformed_dimension_dash_is_reported_not_silently_dropped(tmp_path):
    body = """
## Framing

- genre_noun — "test novel"

## Pillar Dimensions

- alpha_dim — First criteria.
- beta_dim - Second criteria.
- gamma_dim – Third criteria.

## Drafting Rules

25. Something genre-specific.
"""
    path = write_pack(tmp_path, "testgenre", VALID_PRIMARY_META, body)
    pack = genre_pack.parse_pack(path)
    assert pack["dimensions"] == ["alpha_dim"]
    assert pack["malformed_dimensions"] == ["beta_dim", "gamma_dim"]


# --- JSON frontmatter errors must point at the real file line ---------------

def test_json_error_reports_correct_file_line(tmp_path):
    path = tmp_path / "broken.md"
    # The bad, unquoted token "bad" sits on file line 4 (1-indexed).
    path.write_text('---\n{\n  "name": "x",\n  bad\n}\n---\n', encoding="utf-8")
    with pytest.raises(genre_pack.PackError) as exc_info:
        genre_pack.parse_pack(path)
    assert f"{path}:4:" in str(exc_info.value)


# --- Cheap correctness/hygiene fixes -----------------------------------------

def test_parses_pack_with_utf8_bom(tmp_path):
    path = tmp_path / "testgenre.md"
    content = ("---\n" + json.dumps(VALID_PRIMARY_META, indent=2) + "\n---\n"
              + VALID_PRIMARY_BODY)
    path.write_bytes(b"\xef\xbb\xbf" + content.encode("utf-8"))
    pack = genre_pack.parse_pack(path)
    assert pack["meta"]["name"] == "testgenre"


def test_parse_rejects_non_dict_frontmatter(tmp_path):
    path = tmp_path / "broken.md"
    path.write_text("---\n[1, 2]\n---\n", encoding="utf-8")
    with pytest.raises(genre_pack.PackError, match="must be a JSON object"):
        genre_pack.parse_pack(path)


# --- Untested branches --------------------------------------------------------

def test_section_body_returns_none_for_absent_heading():
    assert genre_pack.section_body("## Foo\n\nbar\n", "Nonexistent") is None


def test_section_body_returns_text_up_to_next_heading():
    body = "## Foo\n\nfoo text\n\n## Bar\n\nbar text\n"
    result = genre_pack.section_body(body, "Foo")
    assert result == "\nfoo text\n\n"
    assert "bar text" not in result


def test_section_body_returns_to_end_of_body_when_no_next_heading():
    body = "## Foo\n\nfoo text to the end\n"
    result = genre_pack.section_body(body, "Foo")
    assert result == "\nfoo text to the end\n"


def test_parse_pack_on_missing_file_reports_cannot_read(tmp_path):
    path = tmp_path / "does_not_exist.md"
    with pytest.raises(genre_pack.PackError, match="cannot read"):
        genre_pack.parse_pack(path)


def test_missing_pillar_dimensions_section_yields_empty_list(tmp_path):
    body = '## Framing\n\n- genre_noun — "test novel"\n'
    path = write_pack(tmp_path, "testgenre", VALID_PRIMARY_META, body)
    pack = genre_pack.parse_pack(path)
    assert pack["dimensions"] == []
    assert pack["malformed_dimensions"] == []


def test_parsed_pack_carries_body_and_path(tmp_path):
    path = write_pack(tmp_path, "testgenre", VALID_PRIMARY_META,
                      VALID_PRIMARY_BODY)
    pack = genre_pack.parse_pack(path)
    assert pack["path"] == path
    assert isinstance(pack["body"], str)
    assert "## Pillar Dimensions" in pack["body"]
````

- [ ] **Step 2: Run the tests to verify they fail**

Run: `uv run pytest tests/test_genre_pack.py -v`
Expected: collection error — `ModuleNotFoundError: No module named 'genre_pack'`

- [ ] **Step 3: Write the parser**

Create `plugin/autonovel/shared/scripts/genre_pack.py`:

````python
"""Genre pack parsing and validation. Library module — no CLI.

A genre pack is a markdown file whose first block is JSON frontmatter
delimited by lines of exactly '---', followed by '## ' prose sections.

Frontmatter is JSON rather than YAML because the plugin's scripts are
stdlib-only and Python ships no YAML parser.
"""
import json
import re
from pathlib import Path

ROLES = {"primary", "secondary", "modifier"}

# Dimensions the base rubric already scores. A pack's pillar dimensions may
# not collide with these — that is what stops a literary pack from
# double-counting prose against the base craft category.
RESERVED_DIMENSIONS = {
    "character_depth", "character_distinctiveness", "character_secrets",
    "outline_completeness", "foreshadowing_balance",
    "internal_consistency", "voice_clarity", "canon_coverage",
}

WEIGHT_KEYS = ("pillar", "character", "structure", "craft")

# Fields only a primary may declare. A modifier that sets these is trying to
# own structure it is not allowed to own.
PRIMARY_ONLY_FIELDS = ("weights", "pillar_label", "beat_system", "shape")

CORE_PROJECT_FILES = {
    "seed.txt", "voice.md", "world.md", "characters.md", "outline.md",
    "canon.md", "MYSTERY.md", "state.json", "results.tsv", "arc_summary.md",
    "manuscript.md", "voice_wells.json", "import_source.md",
}

# A fenced block, backtick or tilde, 3 or more of the same character,
# opened and closed by matching markers, with up to 3 spaces of leading
# indent (CommonMark allows this — e.g. a fence indented under a bullet
# in '## Artifacts'). Used to blank fenced regions before structural
# matching so a pack author showing example syntax in a fence can't be
# mistaken for a real heading or dimension line. The closing marker must
# match the opening marker's exact character count via backreference —
# CommonMark itself only requires the closer be at least as long as the
# opener, so this is a deliberate simplification. It fails safe (an
# under-matched fence is simply not masked) rather than over-masking, and
# being strict is exactly what lets a doc nest a short fence inside a
# longer outer one — e.g. TEMPLATE.md wraps a 3-backtick example fence
# inside its own longer outer fence — without either marker being
# mistaken for closing the other. An unclosed fence simply doesn't match
# and masks nothing — an acceptable, safe failure.
FENCE_RE = re.compile(r"^ {0,3}(?P<f>```+|~~~+).*?^ {0,3}(?P=f)[ \t]*$",
                      re.M | re.S)

# '- <key> — <criteria>'  (em dash, not hyphen)
DIMENSION_RE = re.compile(r"^-\s+([a-z][a-z0-9_]*)\s+—", re.M)
# Same shape but with a hyphen or en dash where an em dash belongs — the
# typo autocorrect produces. Never matches a line DIMENSION_RE also matches,
# since the two require different characters in the same position.
DIMENSION_LOOSE_RE = re.compile(r"^-\s+([a-z][a-z0-9_]*)\s+[–-]", re.M)
SECTION_RE = re.compile(r"^##\s+(.+?)\s*$", re.M)


class PackError(Exception):
    """Malformed pack. The message is user-facing."""


def _mask_fences(text):
    """Same-length copy of text with fenced blocks blanked to spaces
    (newlines preserved), so structural regexes skip fenced content while
    offsets into the mask still index the corresponding original text.

    Called more than once on overlapping text (once on a whole body, again
    on a slice of it in _pillar_dimensions) — that's safe because
    section_body locates its slice boundaries in an already-masked copy,
    so a slice can never begin or end in the middle of a fenced region.
    Re-masking a slice therefore always sees the same complete fences the
    first pass saw, never a partial one that could be mismatched."""
    return FENCE_RE.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), text)


def parse_pack(path):
    """Parse a pack file.

    Returns a dict:
      'meta'                — the frontmatter, as a dict
      'sections'            — '## ' heading names, in order, outside fences
      'dimensions'          — '## Pillar Dimensions' keys written with the
                               required em dash, in order
      'malformed_dimensions'— keys in that same section written with a
                               hyphen or en dash instead of an em dash;
                               Task 2's validator turns these into a
                               specific error rather than silently
                               undercounting real dimensions
      'path'                — the Path passed in
      'body'                — the file's content after the frontmatter,
                               verbatim (not masked) — later phases feed
                               this prose to LLM judges

    Headings and dimension bullets inside fenced code blocks (``` or ~~~)
    are ignored when locating sections and dimensions, but 'sections' and
    'body' still return the original, unmasked text.

    Raises PackError if the file is unreadable or the frontmatter is broken.
    """
    path = Path(path)
    try:
        text = path.read_text(encoding="utf-8-sig")
    except OSError as e:
        raise PackError(f"{path}: cannot read pack file: {e}") from e
    meta, body = _split_frontmatter(text, path)
    dimensions, malformed = _pillar_dimensions(body)
    return {
        "meta": meta,
        "sections": SECTION_RE.findall(_mask_fences(body)),
        "dimensions": dimensions,
        "malformed_dimensions": malformed,
        "path": path,
        "body": body,
    }


def _split_frontmatter(text, path):
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise PackError(f"{path}: missing '---' frontmatter opener on line 1")
    close = None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            close = i
            break
    if close is None:
        raise PackError(f"{path}: frontmatter never closed with '---'")
    raw = "\n".join(lines[1:close])
    try:
        meta = json.loads(raw)
    except json.JSONDecodeError as e:
        raise PackError(
            f"{path}:{e.lineno + 1}: frontmatter is not valid JSON: "
            f"{e.msg} (column {e.colno})") from e
    if not isinstance(meta, dict):
        raise PackError(
            f"{path}: frontmatter must be a JSON object "
            f"(got a JSON {type(meta).__name__})")
    return meta, "\n".join(lines[close + 1:])


def section_body(body, heading):
    """Text under '## <heading>' up to the next '## ', or None if absent.

    A '## <heading>' or '## ' line inside a fenced code block (``` or ~~~)
    does not count as a boundary. The returned text is sliced from the
    original body, so any fences nested inside the matched section are
    preserved verbatim.
    """
    mask = _mask_fences(body)
    match = re.search(rf"^##\s+{re.escape(heading)}\s*$", mask, re.M)
    if not match:
        return None
    rest_mask = mask[match.end():]
    nxt = re.search(r"^##\s+", rest_mask, re.M)
    end = match.end() + (nxt.start() if nxt else len(rest_mask))
    return body[match.end():end]


def _pillar_dimensions(body):
    """Return (dimensions, malformed_dimensions) for the '## Pillar
    Dimensions' section — see parse_pack's docstring for the contract.
    Both regexes run against a fence-masked copy of the section so example
    bullets shown inside a fence aren't parsed as real dimensions."""
    section = section_body(body, "Pillar Dimensions")
    if section is None:
        return [], []
    masked = _mask_fences(section)
    return DIMENSION_RE.findall(masked), DIMENSION_LOOSE_RE.findall(masked)
````

- [ ] **Step 4: Run the tests to verify they pass**

Run: `uv run pytest tests/test_genre_pack.py -v`
Expected: 18 passed

- [ ] **Step 5: Commit**

```bash
git add plugin/autonovel/shared/scripts/genre_pack.py tests/test_genre_pack.py
git commit -m "feat: genre pack parser"
```

---

## Task 2: Pack validator

**Files:**
- Modify: `plugin/autonovel/shared/scripts/genre_pack.py` (append `validate_pack`)
- Test: `tests/test_genre_pack.py` (append)

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_genre_pack.py`:

```python
def validate(tmp_path, name, meta, body=VALID_PRIMARY_BODY, known=None):
    path = write_pack(tmp_path, name, meta, body)
    return genre_pack.validate_pack(genre_pack.parse_pack(path),
                                    known_names=known)


def test_valid_primary_has_no_errors(tmp_path):
    assert validate(tmp_path, "testgenre", VALID_PRIMARY_META) == []


def test_name_must_match_filename(tmp_path):
    meta = {**VALID_PRIMARY_META, "name": "mismatch"}
    errors = validate(tmp_path, "testgenre", meta)
    assert any("filename stem" in e for e in errors)


def test_role_must_be_known(tmp_path):
    meta = {**VALID_PRIMARY_META, "role": ["primary", "bogus"]}
    errors = validate(tmp_path, "testgenre", meta)
    assert any("unknown role" in e for e in errors)


def test_role_must_be_non_empty_list(tmp_path):
    meta = {**VALID_PRIMARY_META, "role": []}
    errors = validate(tmp_path, "testgenre", meta)
    assert any("non-empty list" in e for e in errors)


def test_weights_must_sum_to_100(tmp_path):
    meta = {**VALID_PRIMARY_META,
            "weights": {"pillar": 40, "character": 30, "structure": 20, "craft": 5}}
    errors = validate(tmp_path, "testgenre", meta)
    assert any("must sum to 100" in e for e in errors)


def test_primary_requires_pillar_label(tmp_path):
    meta = {k: v for k, v in VALID_PRIMARY_META.items() if k != "pillar_label"}
    errors = validate(tmp_path, "testgenre", meta)
    assert any("pillar_label" in e for e in errors)


def test_primary_requires_framing_and_pillar_sections(tmp_path):
    errors = validate(tmp_path, "testgenre", VALID_PRIMARY_META,
                      body="## Drafting Rules\n\n25. Something.\n")
    assert any("'## Framing'" in e for e in errors)
    assert any("'## Pillar Dimensions'" in e for e in errors)


def test_modifier_may_not_declare_weights(tmp_path):
    meta = {"name": "testmod", "label": "Test Mod", "role": ["modifier"],
            "weights": {"pillar": 40, "character": 30, "structure": 20, "craft": 10}}
    errors = validate(tmp_path, "testmod", meta,
                      body="## Framing\n\n- comps — Someone.\n")
    assert any("must not declare 'weights'" in e for e in errors)


def test_modifier_may_not_have_pillar_dimensions(tmp_path):
    meta = {"name": "testmod", "label": "Test Mod", "role": ["modifier"]}
    errors = validate(tmp_path, "testmod", meta, body=VALID_PRIMARY_BODY)
    assert any("must not have a '## Pillar Dimensions'" in e for e in errors)


def test_valid_modifier_has_no_errors(tmp_path):
    meta = {"name": "testmod", "label": "Test Mod", "role": ["modifier"],
            "content_register": {"heat": "explicit"},
            "conflicts_with": []}
    body = "## Framing\n\n- comps — Someone.\n\n## Genre Contract\n\n- Something binary.\n"
    assert validate(tmp_path, "testmod", meta, body=body) == []


def test_dimension_count_must_be_three_to_six(tmp_path):
    body = VALID_PRIMARY_BODY.replace("- gamma_dim — Third criteria.\n", "")
    errors = validate(tmp_path, "testgenre", VALID_PRIMARY_META, body=body)
    assert any("need 3-6" in e for e in errors)


def test_dimensions_may_not_collide_with_reserved(tmp_path):
    body = VALID_PRIMARY_BODY.replace("- alpha_dim — First criteria.",
                                      "- voice_clarity — Colliding.")
    errors = validate(tmp_path, "testgenre", VALID_PRIMARY_META, body=body)
    assert any("collide with reserved" in e for e in errors)


def test_conflicts_with_must_resolve(tmp_path):
    meta = {**VALID_PRIMARY_META, "conflicts_with": ["nosuchpack"]}
    errors = validate(tmp_path, "testgenre", meta, known={"testgenre", "general"})
    assert any("unknown pack" in e for e in errors)


def test_shape_range_must_be_ordered(tmp_path):
    meta = {**VALID_PRIMARY_META,
            "shape": {**VALID_PRIMARY_META["shape"], "chapters": [26, 22]}}
    errors = validate(tmp_path, "testgenre", meta)
    assert any("not ordered" in e for e in errors)


def test_artifact_may_not_collide_with_core_file(tmp_path):
    meta = {**VALID_PRIMARY_META, "artifacts": ["canon.md"]}
    errors = validate(tmp_path, "testgenre", meta)
    assert any("collides with a core project file" in e for e in errors)
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `uv run pytest tests/test_genre_pack.py -v`
Expected: FAIL — `AttributeError: module 'genre_pack' has no attribute 'validate_pack'`

- [ ] **Step 3: Write the validator**

A quality-review pass on this task found four call sites that raised
instead of returning an error string (an author guessing at a richer
schema — e.g. a dict in a list where a name string belongs — got a
`TypeError` traceback instead of a message), one message that told an
author "'weights' is required" while a wrong-type `weights` sat right
there on screen, and a dimension-count message that contradicted the
em-dash message when both fired for the same malformed bullet. The block
below is the corrected version; see `genre_pack.py` for the final code.

It also adds one constant to the block Task 1 wrote at the top of the
file — `SCORING_ROLES = {"primary", "secondary"}`, beside `ROLES` — plus
a "source of truth" comment above `RESERVED_DIMENSIONS` pointing at
`plugin/autonovel/shared/rubrics/foundation.md` (so Task 9's rewrite of
that rubric doesn't silently drift out of sync with this list) and a
comment above `CORE_PROJECT_FILES` noting what it mirrors.

A still later pass (after Tasks 6-8 shipped the packs) added a third
thing to the top-of-file block and a matching check to `validate_pack`:
`NAME_RE = re.compile(r"[a-z0-9][a-z0-9-]*")`, moved here from
`resolve_genre.py` (Task 4), which now imports it instead of defining
its own copy. `validate_pack` applies it to a pack's own `name` field,
so `Cozy_Mystery.md` fails at authoring time with a message naming the
rule rather than validating clean and then failing at resolve time with
"invalid genre pack name". The two `name` checks are now an
`if`/`if` pair inside a single `else`, not an `if`/`elif`: a name can
match its filename stem and still be illegal. Tests:
`test_name_must_use_resolver_safe_characters` (asserting the exact
error) and `test_hyphenated_lowercase_name_is_valid`.

A later quality-review pass (during Tasks 3-5) added two more things to
this same top-of-file block: `TEMPLATE_STEM = "TEMPLATE"`, right after
`CORE_PROJECT_FILES`, and a `pack_names_in(directory)` function, right
after the `PackError` class — a single-directory "the `.md` stems here,
minus `TEMPLATE_STEM`" helper that both `validate_genre_pack.py` and
`resolve_genre.py` (Tasks 3-4) use to enumerate a `genres/` directory's
pack names, so the `TEMPLATE` exclusion isn't hand-copied in three
places. That same pass also renamed `_names` below to `format_names` —
once `resolve_genre.py` started importing it (Task 4), the leading
underscore was no longer telling the truth about the function's audience.

Append to `plugin/autonovel/shared/scripts/genre_pack.py` (mentally
splicing `TEMPLATE_STEM`/`pack_names_in` into the positions described
above; they're included here rather than as a separate diff so this
block stays a complete, pasteable unit):

```python
# The template's filename stem — never a real pack name, so every scan of a
# genres/ directory for pack names excludes it.
TEMPLATE_STEM = "TEMPLATE"


def pack_names_in(directory):
    """Pack names available in a single genres/ directory: the '.md' file
    stems, minus TEMPLATE_STEM. Callers combining more than one directory
    (project genres/ over the plugin's shared/genres/) union the results
    themselves — this function deliberately knows about only one directory
    at a time, so the different ways CLIs combine directories stay visible
    at the call site instead of being hidden behind a shared helper."""
    return {p.stem for p in Path(directory).glob("*.md")} - {TEMPLATE_STEM}


def formatformat_names(seq):
    """Render an iterable of values for an error message: 'craft, pillar'
    instead of the default repr "['craft', 'pillar']". Every element is
    coerced with str() so a stray non-string value — an author guessing at
    a richer schema, e.g. a dict where a name string belongs — still
    renders instead of raising."""
    return ", ".join(str(v) for v in seq)


def validate_pack(pack, known_names=None):
    """Validate a parsed pack.

    Returns a list of human-readable error strings; empty means valid.
    known_names, when given, is the set of pack names that exist, used to
    check conflicts_with references.

    Frontmatter-field errors are collected before section/prose errors, so
    an author working top-to-bottom through the list fixes the JSON block
    first and isn't bounced back to it after starting on the prose.
    """
    errors = []
    meta = pack["meta"]
    path = pack["path"]
    sections = set(pack["sections"])

    # --- frontmatter -----------------------------------------------------

    name = meta.get("name")
    if not isinstance(name, str) or not name:
        errors.append("frontmatter 'name' must be a non-empty string")
    elif name != path.stem:
        errors.append(
            f"frontmatter 'name' is {name!r} but the filename stem is "
            f"{path.stem!r}")

    if not isinstance(meta.get("label"), str) or not meta.get("label"):
        errors.append("frontmatter 'label' must be a non-empty string")

    role = meta.get("role")
    if not isinstance(role, list) or not role:
        errors.append("frontmatter 'role' must be a non-empty list")
        role = []
    else:
        # Guard against non-string entries (e.g. an author passing a dict)
        # rather than letting them reach a hash/membership test below.
        unknown = [r for r in role if not isinstance(r, str) or r not in ROLES]
        if unknown:
            errors.append(
                f"frontmatter 'role' has unknown role(s) {format_names(unknown)}; "
                f"valid roles: {format_names(sorted(ROLES))}")

    # role_strs drops any non-string junk (already reported above) before
    # any set() is built from it — set(role) directly would raise on an
    # unhashable element such as a dict.
    role_strs = [r for r in role if isinstance(r, str)]
    scoring = bool(set(role_strs) & SCORING_ROLES)
    is_primary = "primary" in role_strs
    modifier_only = (len(role_strs) == len(role)
                     and set(role_strs) == {"modifier"})

    if scoring:
        errors.extend(_validate_weights(meta.get("weights")))

    if is_primary and not meta.get("pillar_label"):
        errors.append(
            "frontmatter 'pillar_label' is required for primary packs")

    if modifier_only:
        for field in PRIMARY_ONLY_FIELDS:
            if field in meta:
                errors.append(
                    f"modifier pack's frontmatter must not declare {field!r}")

    conflicts = meta.get("conflicts_with", [])
    if not isinstance(conflicts, list):
        errors.append("frontmatter 'conflicts_with' must be a list")
    elif known_names is not None:
        unknown = [n for n in conflicts
                  if not isinstance(n, str) or n not in known_names]
        if unknown:
            errors.append(
                f"frontmatter 'conflicts_with' names unknown pack(s) "
                f"{format_names(unknown)}; known packs: {format_names(sorted(known_names))}")

    errors.extend(_validate_shape(meta.get("shape")))

    # meta.get("artifacts", []) rather than `or []` — an explicit
    # "artifacts": null must fail loudly the same way conflicts_with does,
    # not be silently treated as an empty list.
    artifacts = meta.get("artifacts", [])
    if not isinstance(artifacts, list):
        errors.append("frontmatter 'artifacts' must be a list")
    else:
        # Guard against non-string entries (e.g. an author passing a dict)
        # the same way 'role' and 'conflicts_with' already do, rather than
        # silently skipping them — Task 4's merge() puts 'artifacts'
        # straight into its JSON output, and a dict there would become an
        # attempt to create a file literally named "{'file': 'x.md'}".
        non_string = [a for a in artifacts if not isinstance(a, str)]
        if non_string:
            errors.append(
                f"frontmatter 'artifacts' must be a list of strings; "
                f"non-string element(s): {format_names(non_string)}")
        for artifact in artifacts:
            if isinstance(artifact, str) and artifact in CORE_PROJECT_FILES:
                errors.append(
                    f"artifact {artifact!r} collides with a core project file")

    # --- sections / prose --------------------------------------------------

    if is_primary and "Framing" not in sections:
        errors.append("primary pack must have a '## Framing' section")

    if scoring:
        errors.extend(_validate_dimensions(pack["dimensions"],
                                           pack["malformed_dimensions"],
                                           "Pillar Dimensions" in sections))

    if modifier_only and "Pillar Dimensions" in sections:
        errors.append(
            "modifier pack must not have a '## Pillar Dimensions' section")

    return errors


def _validate_weights(weights):
    if weights is None:
        return ["frontmatter 'weights' is required for primary and "
                "secondary packs"]
    if not isinstance(weights, dict):
        return ["frontmatter 'weights' must be a JSON object mapping "
                "pillar/character/structure/craft to integers"]
    missing = [k for k in WEIGHT_KEYS if k not in weights]
    if missing:
        return [f"'weights' missing key(s): {format_names(missing)}"]
    # isinstance(v, int) alone accepts bool (bool is an int subclass in
    # Python) — a stray "weights": {"pillar": true, ...} must be reported
    # as a type error, not silently summed as 1 and reported as a sum
    # mismatch instead.
    bad = [k for k in WEIGHT_KEYS
           if isinstance(weights[k], bool) or not isinstance(weights[k], int)]
    if bad:
        return [f"'weights' values must be integers; non-integer key(s): "
                f"{format_names(bad)}"]
    total = sum(weights[k] for k in WEIGHT_KEYS)
    if total != 100:
        return [f"'weights' sum to {total}, must sum to 100"]
    return []


def _validate_dimensions(dimensions, malformed_dimensions, has_section):
    """dimensions/malformed_dimensions are parse_pack's lists for a scoring
    pack; has_section says whether a '## Pillar Dimensions' heading exists
    at all — required so a missing section produces exactly one message
    instead of also tripping the (contradictory) dimension-count check."""
    if not has_section:
        return ["add a '## Pillar Dimensions' section with 3-6 bullets, "
                "each reading '- <key> — <criteria>' with an em dash"]

    errors = []
    if malformed_dimensions:
        errors.append(
            f"pillar dimension(s) {format_names(sorted(malformed_dimensions))} "
            "use a hyphen or en dash; an em dash (—) is required")
    # Malformed bullets are still bullets an author sees on screen, so they
    # count toward the range check — otherwise a 3-bullet section with one
    # bad dash reports "has 2 dimension(s); need 3-6" right next to the
    # em-dash message, which contradicts what's visibly there.
    total = len(dimensions) + len(malformed_dimensions)
    if not 3 <= total <= 6:
        errors.append(
            f"'## Pillar Dimensions' has {total} dimension(s); "
            "need 3-6, and each bullet must read '- <key> — <criteria>' "
            "with an em dash")
    clash = sorted(set(dimensions) & RESERVED_DIMENSIONS)
    if clash:
        errors.append(
            f"pillar dimension(s) {format_names(clash)} collide with reserved "
            f"base dimensions; reserved: {format_names(sorted(RESERVED_DIMENSIONS))}")
    dupes = sorted({d for d in dimensions if dimensions.count(d) > 1})
    if dupes:
        errors.append(f"duplicate pillar dimension key(s): {format_names(dupes)}")
    return errors


def _validate_shape(shape):
    if shape is None:
        return []
    if not isinstance(shape, dict):
        return ["'shape' must be a JSON object"]
    errors = []
    for key in ("chapters", "words"):
        rng = shape.get(key)
        if rng is None:
            continue
        if (not isinstance(rng, list) or len(rng) != 2
                or not all(isinstance(v, int) and not isinstance(v, bool)
                           for v in rng)):
            errors.append(f"shape.{key} must be a two-integer range")
        elif rng[0] > rng[1]:
            errors.append(f"shape.{key} range {rng} is not ordered low..high")
    return errors
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `uv run pytest tests/test_genre_pack.py -v`
Expected: 62 passed (56 at the time this task landed, plus the CLI tests
from Task 3 and the two `name`-format tests noted above). The test file's
validate_pack section was reorganized
by subject (name / label / role / weights / primary structure / modifier
restrictions / pillar dimensions / conflicts_with / shape / artifacts)
rather than by which task or plan revision introduced each test; packs
built from a single mutation of the valid baseline assert the exact error
list, not just a substring, so a fix in one branch that trips a second,
contradictory message elsewhere is caught. Coverage beyond the Step 1
block above includes: malformed dimensions, duplicate dimension keys,
weights missing/wrong-type/holding a non-integer or bool, a
`## Pillar Dimensions` section missing for a secondary (not just primary)
pack, shape as a non-object/holding a malformed or boolean range,
conflicts_with and artifacts as non-lists, an explicit `"artifacts": null`
(guarding against a regression to `meta.get("artifacts") or []`),
missing/non-string name and label, non-string elements in `role` and
`conflicts_with` that previously raised `TypeError` instead of returning
an error string, and a non-string element in `artifacts` that is now
reported by name (mirroring `role`/`conflicts_with`) rather than silently
skipped — closed by a later review because Task 4's `merge()` puts
`artifacts` straight into its JSON output, where a dict entry would
become an attempt to create a file literally named `"{'file': 'x.md'}"`.

- [ ] **Step 5: Commit**

```bash
git add plugin/autonovel/shared/scripts/genre_pack.py tests/test_genre_pack.py
git commit -m "feat: genre pack validation rules"
```

---

## Task 3: validate_genre_pack.py CLI

**Files:**
- Create: `plugin/autonovel/shared/scripts/validate_genre_pack.py`
- Test: `tests/test_genre_pack.py` (append)

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_genre_pack.py`:

```python
import subprocess

VALIDATE_CLI = SCRIPTS / "validate_genre_pack.py"


def test_cli_accepts_valid_pack(tmp_path):
    path = write_pack(tmp_path, "testgenre", VALID_PRIMARY_META,
                      VALID_PRIMARY_BODY)
    result = subprocess.run([sys.executable, str(VALIDATE_CLI), str(path)],
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "OK" in result.stdout


def test_cli_rejects_invalid_pack_with_message(tmp_path):
    meta = {**VALID_PRIMARY_META, "name": "mismatch"}
    path = write_pack(tmp_path, "testgenre", meta, VALID_PRIMARY_BODY)
    result = subprocess.run([sys.executable, str(VALIDATE_CLI), str(path)],
                            capture_output=True, text=True)
    assert result.returncode == 1
    assert "filename stem" in result.stdout + result.stderr


def test_cli_validates_all_shipped_packs():
    genres = Path(__file__).parent.parent / "plugin/autonovel/shared/genres"
    packs = sorted(p for p in genres.glob("*.md") if p.stem != "TEMPLATE")
    assert packs, "no genre packs found to validate"
    result = subprocess.run(
        [sys.executable, str(VALIDATE_CLI), *[str(p) for p in packs]],
        capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr


def test_cli_skips_template_so_the_bare_glob_succeeds():
    """The docstring's advertised `genres/*.md` glob picks up TEMPLATE.md,
    which has no frontmatter. The CLI must skip it — visibly — instead of
    failing, since that glob is how a whole genres/ directory gets checked."""
    genres = Path(__file__).parent.parent / "plugin/autonovel/shared/genres"
    paths = sorted(genres.glob("*.md"))
    assert any(p.stem == "TEMPLATE" for p in paths), "TEMPLATE.md is missing"
    result = subprocess.run(
        [sys.executable, str(VALIDATE_CLI), *[str(p) for p in paths]],
        capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    assert "SKIP" in result.stdout
    assert "TEMPLATE.md" in result.stdout
```

Note: `test_cli_validates_all_shipped_packs` will fail until Task 7 writes the first pack. That is expected and intentional — it is the guard that keeps every shipped pack valid. `test_cli_skips_template_so_the_bare_glob_succeeds` likewise fails until Task 6 writes `TEMPLATE.md`; it is the guard that keeps the advertised `genres/*.md` glob usable once the template sits in that directory.

- [ ] **Step 2: Run the tests to verify they fail**

Run: `uv run pytest tests/test_genre_pack.py -k cli -v`
Expected: FAIL — `No such file or directory: '.../validate_genre_pack.py'`

- [ ] **Step 3: Write the CLI**

A later quality-review pass (during Tasks 3-5, once `pack_names_in` was
added to `genre_pack.py` in Task 2 — see above) simplified the
known-names computation below: `known = {p.stem for p in paths}` was
redundant — for any real `.md` argument, that argument's own stem is
already included by the very next loop, which unions in every sibling
`.md` in its parent directory. Dropped, replaced by using
`pack_names_in` per argument's parent directory instead of the inline
glob-and-discard.

Create `plugin/autonovel/shared/scripts/validate_genre_pack.py`:

```python
#!/usr/bin/env python3
"""Validate one or more genre pack files.

Usage:
  python3 validate_genre_pack.py path/to/fantasy.md [more...]
  python3 validate_genre_pack.py "${CLAUDE_PLUGIN_ROOT}/shared/genres/"*.md

That second form is the intended way to check a whole genres/ directory, so
TEMPLATE.md — the authoring guide, which has no frontmatter and is not a
pack — is skipped with a printed note rather than failing the run.

Exit 0 if every pack is valid; 1 otherwise, with errors on stdout.
"""
import sys
from pathlib import Path

from genre_pack import (TEMPLATE_STEM, PackError, pack_names_in, parse_pack,
                        validate_pack)


def main(argv):
    if not argv:
        print("usage: validate_genre_pack.py <pack.md> [more...]",
              file=sys.stderr)
        return 2

    paths = [Path(a) for a in argv]
    # Packs referenced by conflicts_with may live alongside the ones named
    # on the command line, so every sibling .md in each argument's
    # directory counts as known too. There's no separate "add each
    # argument's own stem" step — for any real .md argument, pack_names_in
    # on its own parent directory already includes it.
    known = set()
    for path in paths:
        known |= pack_names_in(path.parent)

    failed = False
    for path in paths:
        # The advertised glob over a genres/ directory sweeps up TEMPLATE.md,
        # which is an authoring guide with no frontmatter and would fail
        # every time. Skip it — but say so, so an author who meant to
        # validate a real pack named TEMPLATE.md isn't left thinking it
        # passed.
        if path.stem == TEMPLATE_STEM:
            print(f"SKIP {path} (authoring template, not a pack)")
            continue
        try:
            pack = parse_pack(path)
        except PackError as e:
            print(f"FAIL {path}\n  {e}")
            failed = True
            continue
        errors = validate_pack(pack, known_names=known)
        if errors:
            failed = True
            print(f"FAIL {path}")
            for error in errors:
                print(f"  {error}")
        else:
            print(f"OK   {path}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `uv run pytest tests/test_genre_pack.py -k "cli and not shipped and not template" -v`
Expected: 2 passed. The `shipped` test still fails — Task 7 fixes it; the `template` test still fails — Task 6 fixes it.

- [ ] **Step 5: Commit**

```bash
git add plugin/autonovel/shared/scripts/validate_genre_pack.py tests/test_genre_pack.py
git commit -m "feat: validate_genre_pack CLI"
```

---

## Task 4: resolve_genre.py — resolution and search path

**Files:**
- Create: `plugin/autonovel/shared/scripts/resolve_genre.py`
- Test: `tests/test_resolve_genre.py`

- [ ] **Step 1: Write the failing tests**

Create `tests/test_resolve_genre.py`:

```python
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).parent.parent.resolve()
SCRIPT = REPO / "plugin/autonovel/shared/scripts/resolve_genre.py"
PLUGIN_GENRES = REPO / "plugin/autonovel/shared/genres"


def run(project, *args):
    return subprocess.run([sys.executable, str(SCRIPT), *args],
                          capture_output=True, text=True, cwd=project)


def write_state(project, **fields):
    state = {"phase": "foundation", "iteration": 0, "foundation_score": 0.0,
             "pillar_score": 0.0, "chapters_drafted": 0, "chapters_total": 0,
             "novel_score": 0.0, "revision_cycle": 0, "review_round": 0,
             "debts": []}
    state.update(fields)
    (project / "state.json").write_text(json.dumps(state), encoding="utf-8")


def write_project_pack(project, name, meta, body):
    genres = project / "genres"
    genres.mkdir(exist_ok=True)
    (genres / f"{name}.md").write_text(
        "---\n" + json.dumps(meta) + "\n---\n" + body, encoding="utf-8")


PRIMARY_BODY = """
## Framing

- genre_noun — "test novel"

## Pillar Dimensions

- alpha_dim — First.
- beta_dim — Second.
- gamma_dim — Third.
"""


def primary_meta(name, **overrides):
    meta = {
        "name": name, "label": name.title(), "role": ["primary"],
        "pillar_label": "Test Pillar",
        "weights": {"pillar": 40, "character": 30, "structure": 20, "craft": 10},
        "beat_system": "save-the-cat",
        "shape": {"chapters": [22, 26], "words": [80000, 95000],
                  "chapter_words": 3200, "pov_default": "third limited past"},
        "conflicts_with": [], "artifacts": [],
    }
    meta.update(overrides)
    return meta


def test_missing_genre_resolves_to_general(tmp_path):
    write_state(tmp_path)
    result = run(tmp_path)
    assert result.returncode == 0, result.stdout + result.stderr
    out = json.loads(result.stdout)
    assert out["packs"][0]["name"] == "general"
    assert out["packs"][0]["role"] == "primary"


def test_resolves_shipped_plugin_pack(tmp_path):
    write_state(tmp_path, genre="fantasy")
    result = run(tmp_path)
    assert result.returncode == 0, result.stdout + result.stderr
    out = json.loads(result.stdout)
    assert out["packs"][0]["name"] == "fantasy"
    assert out["packs"][0]["path"].startswith(str(PLUGIN_GENRES))


def test_project_pack_overrides_plugin_pack(tmp_path):
    write_state(tmp_path, genre="fantasy")
    write_project_pack(tmp_path, "fantasy",
                       primary_meta("fantasy", label="Local Fantasy"),
                       PRIMARY_BODY)
    result = run(tmp_path)
    assert result.returncode == 0, result.stdout + result.stderr
    out = json.loads(result.stdout)
    assert out["primary_label"] == "Local Fantasy"
    assert out["packs"][0]["path"].startswith(str(tmp_path))


def test_unknown_pack_is_an_error(tmp_path):
    write_state(tmp_path, genre="nosuchgenre")
    result = run(tmp_path)
    assert result.returncode == 1
    assert "nosuchgenre" in result.stderr


def test_missing_state_json_is_an_error(tmp_path):
    result = run(tmp_path)
    assert result.returncode == 1
    assert "state.json" in result.stderr


def test_pack_must_declare_the_role_it_is_used_in(tmp_path):
    write_state(tmp_path, genre="modonly")
    write_project_pack(tmp_path, "modonly",
                       {"name": "modonly", "label": "Mod Only",
                        "role": ["modifier"]},
                       "## Framing\n\n- comps — Someone.\n")
    result = run(tmp_path)
    assert result.returncode == 1
    assert "does not declare role 'primary'" in result.stderr


def test_state_json_not_an_object_is_an_error(tmp_path):
    (tmp_path / "state.json").write_text("[1, 2, 3]", encoding="utf-8")
    result = run(tmp_path)
    assert result.returncode == 1
    assert "state.json must be a JSON object" in result.stderr


def test_duplicate_modifier_is_rejected(tmp_path):
    # A repeated modifier means state.json is wrong, not that the author
    # wants it twice — silently deduping would let a doubled genre string
    # reach the book's title page at export without anyone noticing.
    write_state(tmp_path, genre="testprimary",
                genre_modifiers=["testmod", "testmod"])
    write_project_pack(tmp_path, "testprimary", primary_meta("testprimary"),
                       PRIMARY_BODY)
    write_project_pack(
        tmp_path, "testmod",
        {"name": "testmod", "label": "Test Mod", "role": ["modifier"],
         "conflicts_with": []},
        "## Framing\n\n- comps — Someone.\n")
    result = run(tmp_path)
    assert result.returncode == 1
    assert "testmod" in result.stderr
    assert "more than once" in result.stderr


def test_invalid_genre_name_is_rejected(tmp_path):
    write_state(tmp_path, genre="../outside")
    result = run(tmp_path)
    assert result.returncode == 1
    assert "invalid genre pack name" in result.stderr


def test_conflict_message_lists_names_comma_joined_not_as_a_list_repr(tmp_path):
    write_state(tmp_path, genre="testprimary",
                genre_modifiers=["testmod", "testya"])
    write_project_pack(tmp_path, "testprimary", primary_meta("testprimary"),
                       PRIMARY_BODY)
    write_project_pack(
        tmp_path, "testmod",
        {"name": "testmod", "label": "Test Mod", "role": ["modifier"],
         "conflicts_with": ["testya"]},
        "## Framing\n\n- comps — Someone.\n")
    write_project_pack(
        tmp_path, "testya",
        {"name": "testya", "label": "Test YA", "role": ["modifier"],
         "conflicts_with": []},
        "## Framing\n\n- comps — Someone.\n")
    result = run(tmp_path)
    assert result.returncode == 1
    assert "conflicts with loaded pack(s) testya" in result.stderr
    # The old Python-list repr ("['testya']") must be gone.
    assert "['testya']" not in result.stderr


def test_load_pack_reports_every_error_not_just_the_first(tmp_path):
    # A pack with several simultaneous defects must show all of them — an
    # author with five defects should see five, not fix one and re-run to
    # discover the next. Pins the "\n  ".join(errors) behavior in
    # load_pack against a future "simplification" to errors[0].
    write_state(tmp_path, genre="broken")
    write_project_pack(
        tmp_path, "broken",
        {"name": "broken", "label": "", "role": ["primary"]},
        "## Drafting Rules\n\n25. Nothing else here.\n")
    result = run(tmp_path)
    assert result.returncode == 1
    assert "frontmatter 'label' must be a non-empty string" in result.stderr
    assert "frontmatter 'pillar_label' is required" in result.stderr
    assert "'## Framing'" in result.stderr
```

Note: a quality-review pass on this task's first draft found four gaps a
novelist could actually hit: a non-object `state.json` (e.g. a JSON array)
crashed with a raw `AttributeError` instead of a message; a duplicate name
in `genre_modifiers` silently loaded the pack twice, doubling it in the
merged label; a genre name containing a path separator (e.g. `../outside`)
escaped the `genres/` lookup instead of being rejected as malformed; and
the conflict-rejection message rendered Python's list repr
(`['testya']`) instead of the comma-joined style established in Tasks
1-2. The corrected resolver below fixes all four; the five tests above
(state-not-an-object, duplicate-modifier, invalid-name, comma-joined
message, and a pin for the existing multi-error-surfacing behavor) are
the tests that would have caught them.

- [ ] **Step 2: Run the tests to verify they fail**

Run: `uv run pytest tests/test_resolve_genre.py -v`
Expected: FAIL — `No such file or directory: '.../resolve_genre.py'`

- [ ] **Step 3: Write the resolver**

Beyond the four gaps the note above already describes (`state.json`
shape, the duplicate-modifier check, the path-separator name guard, and
the comma-joined message style — also applied to the role-mismatch
message below, alongside concrete next-step guidance, and to the
unknown-pack message, which now lists the known packs), a second
quality-review pass — run after Task 5's tests were also in place, on the
`--check` output contract itself — found two more silent-wrong-output
paths:

- The same pack filling two slots (`genre` and `genre_secondary` both
  `"fantasy"`, which `fantasy.md`'s `role: ["primary", "secondary"]`
  makes a live path once Task 14 wires seed generation) silently doubled
  the label the same way a repeated modifier did — `check_conflicts` now
  rejects any pack name appearing more than once across `packs`.
- Two modifiers disagreeing on the same `content_register` key (e.g. a
  `cozy` pack's `heat: closed-door` against a `steamy` pack's
  `heat: explicit`) resolved silently to whichever loaded last —
  `merge()` now rejects a genuine disagreement (identical values from
  two packs are fine and do not error). Task 5's block below has the
  tests for both.

The block below is the corrected version; see `resolve_genre.py` for the
final code. It also renames the merged output's `label` key to
`primary_label` and adds `display_label` (`" ".join(label_parts)`) — a
key literally named `label` sitting next to `label_parts` invites an
LLM consumer to grab it even though `label_parts` is the one meant for
display; making the
obvious key the correct one closes that gap. `pillar_label` and `weights`
in the merged output now use direct dict indexing on the primary's meta,
not `.get()` — both are guaranteed present by the time `merge()` runs
(the primary must declare role `"primary"`, and `validate_pack` requires
`pillar_label` on any primary and valid `weights` on any scoring role),
so a `.get()` would tell downstream readers these could be null with no
real case where that happens. The module docstring documents the full
ten-key output schema, since six skills parse this JSON and none of them
can see this module's source. `known_names` now builds on `pack_names_in`
(added to `genre_pack.py` in Task 2, see above) instead of repeating the
`{p.stem for p in ...} - {"TEMPLATE"}` glob-and-discard pattern inline.

Create `plugin/autonovel/shared/scripts/resolve_genre.py`:

```python
#!/usr/bin/env python3
"""Resolve a novel project's genre packs and print the merged config as JSON.

Run from the novel project directory:
  python3 resolve_genre.py           # reads ./state.json, prints JSON
  python3 resolve_genre.py --check   # validate only, print nothing on success

Search order for each pack name: ./genres/<name>.md first, then the plugin's
shared/genres/<name>.md. The project wins, so a one-off pack for a single
novel needs no plugin change.

Exit 0 on success; 1 with a message on stderr for any resolution, validation,
or conflict error.

Output schema (the JSON printed on stdout when --check is not given) — six
skills parse this, none of which can see this module's source:

  packs             — [{"name", "role", "path"}, ...], one entry per
                       loaded pack, in resolution order: primary first,
                       then secondary (if any), then modifiers in
                       state.json's genre_modifiers order.
  primary_label     — the primary pack's own 'label' field, verbatim.
  display_label     — every loaded pack's 'label', joined with a space,
                       in the same order as 'packs' — this is what should
                       be shown to a reader (a title page, a status
                       line), not 'primary_label' alone.
  label_parts       — the list display_label was joined from, for a
                       caller that wants to lay the parts out itself.
  pillar_label      — the primary pack's 'pillar_label'.
  weights           — the primary pack's 'weights' dict
                       (pillar/character/structure/craft -> int, sums to
                       100).
  beat_system       — the primary pack's 'beat_system', or "save-the-cat"
                       if it didn't declare one.
  shape             — the primary pack's 'shape' dict (chapters/words
                       ranges, chapter_words, pov_default), or {} if it
                       declared none.
  content_register  — merged content_register dicts from every loaded
                       pack (primary, secondary, and modifiers alike);
                       see merge() for the collision rule.
  artifacts         — the union of every non-modifier pack's 'artifacts'
                       list, in first-seen order; a modifier's own
                       'artifacts' entries are deliberately excluded —
                       see merge().
"""
import argparse
import json
import re
import sys
from pathlib import Path

from genre_pack import (PackError, format_names, pack_names_in, parse_pack,
                        validate_pack)

DEFAULT_GENRE = "general"
PLUGIN_GENRES = Path(__file__).resolve().parent.parent / "genres"

# A pack name is a bare filename stem: lowercase letters, digits, and
# hyphens. Rejecting anything else before it reaches a path join stops a
# name like "../outside" from escaping the genres/ directory it's looked up
# in, and turns a state.json typo into a clear message instead of a
# baffling "unknown genre pack" for a name that was never a real attempt at
# one.
NAME_RE = re.compile(r"[a-z0-9][a-z0-9-]*")


def fail(message):
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_state(project):
    path = project / "state.json"
    if not path.exists():
        fail(f"no state.json in {project} — run this from a novel project "
             "directory")
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        fail(f"state.json is not valid JSON: {e}")
    if not isinstance(state, dict):
        fail(f"state.json must be a JSON object, got a JSON "
             f"{type(state).__name__}")
    return state


def known_names(project):
    return pack_names_in(PLUGIN_GENRES) | pack_names_in(project / "genres")


def find_pack(project, name, names):
    if not NAME_RE.fullmatch(name or ""):
        fail(f"invalid genre pack name {name!r}; use lowercase letters, "
             "digits, and hyphens only")
    for candidate in (project / "genres" / f"{name}.md",
                      PLUGIN_GENRES / f"{name}.md"):
        if candidate.exists():
            return candidate
    fail(f"unknown genre pack {name!r}; looked in {project / 'genres'} and "
         f"{PLUGIN_GENRES}; known packs: {format_names(sorted(names))}")


def load_pack(project, name, role, names):
    path = find_pack(project, name, names)
    try:
        pack = parse_pack(path)
    except PackError as e:
        fail(str(e))
    errors = validate_pack(pack, known_names=names)
    if errors:
        fail(f"{path} is invalid:\n  " + "\n  ".join(errors))
    if role not in pack["meta"].get("role", []):
        fail(f"pack {name!r} does not declare role {role!r} (it declares "
             f"{format_names(pack['meta'].get('role') or [])}); add "
             f"{role!r} to its 'role' list, or choose a different pack "
             "for that slot")
    pack["used_as"] = role
    return pack


def resolve(project):
    state = load_state(project)
    names = known_names(project)

    packs = [load_pack(project, state.get("genre") or DEFAULT_GENRE,
                       "primary", names)]
    if state.get("genre_secondary"):
        packs.append(load_pack(project, state["genre_secondary"],
                               "secondary", names))

    modifiers = state.get("genre_modifiers") or []
    # A repeated modifier means state.json is wrong, not that the author
    # wants it applied twice — silently deduping would let a doubled genre
    # string reach the merged label (and the book's title page at export)
    # without anyone noticing.
    dupes = sorted({m for m in modifiers if modifiers.count(m) > 1})
    if dupes:
        fail(f"genre_modifiers lists {format_names(dupes)} more than "
             "once; remove one of them from state.json")
    for modifier in modifiers:
        packs.append(load_pack(project, modifier, "modifier", names))

    check_conflicts(packs)
    return packs


def check_conflicts(packs):
    # The same pack filling two slots (e.g. genre and genre_secondary both
    # "fantasy") is the same failure the genre_modifiers duplicate guard
    # above prevents, one slot over — it must be caught here too, since a
    # pack can legally declare more than one role and so pass load_pack's
    # role check in both slots.
    loaded_list = [p["meta"]["name"] for p in packs]
    dupes = sorted({n for n in loaded_list if loaded_list.count(n) > 1})
    if dupes:
        fail(f"pack(s) {format_names(dupes)} fill more than one slot; a "
             "pack may be used once — check genre, genre_secondary, and "
             "genre_modifiers in state.json")

    loaded = set(loaded_list)
    for pack in packs:
        name = pack["meta"]["name"]
        clashes = sorted(
            set(pack["meta"].get("conflicts_with") or []) & loaded)
        if clashes:
            fail(f"pack {name!r} conflicts with loaded pack(s) "
                 f"{format_names(clashes)}")


def merge(packs):
    # The primary owns every scalar structural field (pillar_label,
    # weights, beat_system, shape) — it's the pack that owns pillar
    # dimensions and book shape by definition (see genre_pack.py's
    # PRIMARY_ONLY_FIELDS), so a secondary or modifier's copy of these,
    # if it even has one, is never consulted.
    primary = packs[0]
    meta = primary["meta"]

    content_register = {}
    artifacts = []
    for pack in packs:
        # content_register merges across every loaded pack, not just the
        # primary — it's the orthogonal axis a modifier exists to set (an
        # "explicit" heat-level modifier layered onto a primary that
        # declares none). Two packs setting the SAME key to DIFFERENT
        # values is a real authoring conflict, not something merge() can
        # silently resolve: this field is what tells the LLM subagents
        # doing the actual writing where the content boundaries are, and
        # the merged value is all they ever see.
        for key, value in (pack["meta"].get("content_register") or {}).items():
            if key in content_register and content_register[key] != value:
                fail(f"packs disagree on content_register {key!r}: "
                     f"{content_register[key]!r} vs {value!r}; add a "
                     "'conflicts_with' entry or drop one modifier")
            content_register[key] = value
        # A modifier's own 'artifacts' entries are excluded from the
        # union: artifacts are per-book deliverables (a clue ledger, a
        # heat-tracking sheet) that the primary/secondary genre owns:
        # letting every modifier add its own would mean a heat-level or
        # age-category modifier — an orthogonal axis, not a genre — could
        # spawn project files the pipeline never asked for.
        for artifact in pack["meta"].get("artifacts") or []:
            if artifact not in artifacts and pack["used_as"] != "modifier":
                artifacts.append(artifact)

    label_parts = [p["meta"]["label"] for p in packs]
    return {
        "packs": [{"name": p["meta"]["name"], "role": p["used_as"],
                   "path": str(p["path"])} for p in packs],
        "primary_label": meta["label"],
        "display_label": " ".join(label_parts),
        "label_parts": label_parts,
        # pillar_label and weights use direct indexing, not .get(): both
        # are guaranteed present here. packs[0] is always loaded with
        # role="primary" (load_pack enforces it), and validate_pack
        # requires pillar_label on every primary and valid weights on
        # every scoring role (primary is always one, see SCORING_ROLES).
        # A .get() here would tell downstream readers these could be
        # null and leave them no way to handle a case that can't happen.
        "pillar_label": meta["pillar_label"],
        "weights": meta["weights"],
        "beat_system": meta.get("beat_system", "save-the-cat"),
        "shape": meta.get("shape", {}),
        "content_register": content_register,
        "artifacts": artifacts,
    }


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="validate only; print nothing on success")
    args = parser.parse_args(argv)

    packs = resolve(Path.cwd())
    if args.check:
        return 0
    print(json.dumps(merge(packs), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `uv run pytest tests/test_resolve_genre.py -v`
Expected: 9 passed, 2 failed. The two that resolve `general` and `fantasy` from the plugin fail until Tasks 7 and 8 write those packs.

- [ ] **Step 5: Commit**

```bash
git add plugin/autonovel/shared/scripts/resolve_genre.py tests/test_resolve_genre.py
git commit -m "feat: resolve_genre CLI with project-over-plugin search path"
```

---

## Task 5: resolve_genre.py — merge and conflict tests

**Files:**
- Test: `tests/test_resolve_genre.py` (append)

The merge and conflict logic was written in Task 4; this task proves it.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_resolve_genre.py`:

```python
SECONDARY_META = {
    "name": "testsecond", "label": "Test Second",
    "role": ["primary", "secondary"], "pillar_label": "Second Pillar",
    "weights": {"pillar": 20, "character": 40, "structure": 25, "craft": 15},
    "conflicts_with": [], "artifacts": ["second_ledger.md"],
}

MODIFIER_META = {
    "name": "testmod", "label": "Test Mod", "role": ["modifier"],
    "content_register": {"heat": "explicit"},
    "conflicts_with": ["testya"],
    # A modifier may declare artifacts; merge() must ignore them.
    "artifacts": ["mod_ledger.md"],
}

MODIFIER_BODY = "## Framing\n\n- comps — Someone.\n\n## Drafting Rules\n\n25. Body first.\n"


def setup_stack(tmp_path):
    write_state(tmp_path, genre="testprimary", genre_secondary="testsecond",
                genre_modifiers=["testmod"])
    write_project_pack(tmp_path, "testprimary",
                       primary_meta("testprimary", artifacts=["clue_ledger.md"]),
                       PRIMARY_BODY)
    write_project_pack(tmp_path, "testsecond", SECONDARY_META, PRIMARY_BODY)
    write_project_pack(tmp_path, "testmod", MODIFIER_META, MODIFIER_BODY)
    # testmod's conflicts_with names "testya", which must resolve to a real
    # pack for validate_pack's conflicts_with check to pass (Task 2). It is
    # deliberately not in genre_modifiers above, so it's known but not
    # loaded — no conflict fires. test_conflicting_modifiers_are_rejected
    # below is the scenario where it IS loaded and the conflict fires.
    write_project_pack(tmp_path, "testya",
                       {"name": "testya", "label": "Test YA",
                        "role": ["modifier"], "conflicts_with": []},
                       MODIFIER_BODY)


def test_primary_owns_weights_and_shape(tmp_path):
    setup_stack(tmp_path)
    out = json.loads(run(tmp_path).stdout)
    assert out["weights"] == {"pillar": 40, "character": 30,
                              "structure": 20, "craft": 10}
    assert out["shape"]["chapter_words"] == 3200
    assert out["pillar_label"] == "Test Pillar"


def test_label_parts_lists_every_pack_in_order(tmp_path):
    setup_stack(tmp_path)
    out = json.loads(run(tmp_path).stdout)
    assert out["primary_label"] == "Testprimary"
    assert out["display_label"] == "Testprimary Test Second Test Mod"
    assert out["label_parts"] == ["Testprimary", "Test Second", "Test Mod"]


def test_modifier_contributes_content_register(tmp_path):
    setup_stack(tmp_path)
    out = json.loads(run(tmp_path).stdout)
    assert out["content_register"] == {"heat": "explicit"}


def test_artifacts_union_excludes_modifier_contributions(tmp_path):
    setup_stack(tmp_path)
    out = json.loads(run(tmp_path).stdout)
    assert out["artifacts"] == ["clue_ledger.md", "second_ledger.md"]


def test_all_three_pack_paths_reported_with_roles(tmp_path):
    setup_stack(tmp_path)
    out = json.loads(run(tmp_path).stdout)
    assert [(p["name"], p["role"]) for p in out["packs"]] == [
        ("testprimary", "primary"),
        ("testsecond", "secondary"),
        ("testmod", "modifier"),
    ]


def test_conflicting_modifiers_are_rejected(tmp_path):
    write_state(tmp_path, genre="testprimary",
                genre_modifiers=["testmod", "testya"])
    write_project_pack(tmp_path, "testprimary", primary_meta("testprimary"),
                       PRIMARY_BODY)
    write_project_pack(tmp_path, "testmod", MODIFIER_META, MODIFIER_BODY)
    write_project_pack(tmp_path, "testya",
                       {"name": "testya", "label": "Test YA",
                        "role": ["modifier"], "conflicts_with": []},
                       MODIFIER_BODY)
    result = run(tmp_path)
    assert result.returncode == 1
    assert "conflicts with loaded pack" in result.stderr


def test_check_flag_prints_nothing_on_success(tmp_path):
    setup_stack(tmp_path)
    result = run(tmp_path, "--check")
    assert result.returncode == 0
    assert result.stdout.strip() == ""


def test_check_flag_reports_failure_on_bad_stack(tmp_path):
    # --check is currently only exercised on the success path; nothing
    # pinned that it still exits 1 with a message (and no JSON) on a bad
    # stack.
    write_state(tmp_path, genre="nosuchgenre")
    result = run(tmp_path, "--check")
    assert result.returncode == 1
    assert "nosuchgenre" in result.stderr
    assert result.stdout.strip() == ""


def test_same_pack_in_two_slots_is_rejected(tmp_path):
    # A pack declaring role: ["primary", "secondary"] (as the real fantasy
    # pack does) can legally fill either slot, so load_pack's per-slot
    # role check alone can't catch state.json pointing genre and
    # genre_secondary at the same pack — that's the same "silently
    # doubled" failure the genre_modifiers duplicate guard prevents, one
    # slot over, and it must be caught even though nothing here declares
    # a conflicts_with.
    write_state(tmp_path, genre="testsecond", genre_secondary="testsecond")
    write_project_pack(tmp_path, "testsecond", SECONDARY_META, PRIMARY_BODY)
    result = run(tmp_path)
    assert result.returncode == 1
    assert "fill more than one slot" in result.stderr
    assert "testsecond" in result.stderr


def test_content_register_collision_is_rejected(tmp_path):
    # content_register is the only thing six LLM subagents see for where
    # the content boundaries are — two modifiers disagreeing on the same
    # key must not resolve silently to "whichever loaded last".
    write_state(tmp_path, genre="testprimary",
                genre_modifiers=["cozy", "steamy"])
    write_project_pack(tmp_path, "testprimary", primary_meta("testprimary"),
                       PRIMARY_BODY)
    write_project_pack(
        tmp_path, "cozy",
        {"name": "cozy", "label": "Cozy", "role": ["modifier"],
         "content_register": {"heat": "closed-door"}, "conflicts_with": []},
        MODIFIER_BODY)
    write_project_pack(
        tmp_path, "steamy",
        {"name": "steamy", "label": "Steamy", "role": ["modifier"],
         "content_register": {"heat": "explicit"}, "conflicts_with": []},
        MODIFIER_BODY)
    result = run(tmp_path)
    assert result.returncode == 1
    assert "disagree on content_register 'heat'" in result.stderr


def test_content_register_identical_values_do_not_conflict(tmp_path):
    # Two modifiers agreeing on the same key is fine — only a genuine
    # disagreement is an error.
    write_state(tmp_path, genre="testprimary",
                genre_modifiers=["cozy", "alsocozy"])
    write_project_pack(tmp_path, "testprimary", primary_meta("testprimary"),
                       PRIMARY_BODY)
    write_project_pack(
        tmp_path, "cozy",
        {"name": "cozy", "label": "Cozy", "role": ["modifier"],
         "content_register": {"heat": "closed-door"}, "conflicts_with": []},
        MODIFIER_BODY)
    write_project_pack(
        tmp_path, "alsocozy",
        {"name": "alsocozy", "label": "Also Cozy", "role": ["modifier"],
         "content_register": {"heat": "closed-door"}, "conflicts_with": []},
        MODIFIER_BODY)
    result = run(tmp_path)
    assert result.returncode == 0, result.stdout + result.stderr
    out = json.loads(result.stdout)
    assert out["content_register"] == {"heat": "closed-door"}
```

- [ ] **Step 2: Run the tests**

Run: `uv run pytest tests/test_resolve_genre.py -v`
Expected: the eleven tests above pass (22 total including Task 4's eleven);
the two plugin-pack tests still fail pending Tasks 7–8. Four of the eleven
— `test_check_flag_reports_failure_on_bad_stack`,
`test_same_pack_in_two_slots_is_rejected`,
`test_content_register_collision_is_rejected`, and
`test_content_register_identical_values_do_not_conflict` — were added by
the `--check`/output-contract quality-review pass described in Task 4's
Step 3, alongside the original seven.

- [ ] **Step 3: Fix any merge bugs the tests expose**

If `test_artifacts_union_excludes_modifier_contributions` fails, check the `pack["used_as"] != "modifier"` guard in `merge()`. If `test_conflicting_modifiers_are_rejected` fails, check that `check_conflicts` compares against every loaded name, not just the primary. If `test_same_pack_in_two_slots_is_rejected` fails, check that `check_conflicts` computes its own-pack-repeated check from the full `packs` list, not just `conflicts_with` entries. If either `content_register` test fails, check `merge()`'s per-key comparison against the value already accumulated, not just key presence.

Without the `testya.md` fixture added to `setup_stack` above, every test built on it fails validation instead — `MODIFIER_META`'s `conflicts_with: ["testya"]` needs a real, known pack to resolve against (Task 2's `validate_pack` rejects an unknown `conflicts_with` name), even though `testya` is never loaded via `genre_modifiers` in `setup_stack`'s scenario. Known-but-unloaded is the point: it lets `test_conflicting_modifiers_are_rejected` below be the one test that actually loads it and proves the rejection.

- [ ] **Step 4: Commit**

```bash
git add tests/test_resolve_genre.py
git commit -m "test: resolve_genre merge and conflict rules"
```

---

## Task 6: Pack authoring template

**Files:**
- Create: `plugin/autonovel/shared/genres/TEMPLATE.md`

- [ ] **Step 1: Write the template**

A quality-review pass after Tasks 7-8 shipped the packs found that a
novelist could not actually get from this file to a working pack. The
first instruction ("copy this file to `<name>.md`") produced
`missing '---' frontmatter opener on line 1`, because the frontmatter
skeleton sat inside a fenced block under ~35 lines of guide prose; the
guide never said which `state.json` key turns a finished pack on; the
`name` rule omitted the character-class constraint `resolve_genre.py`
enforces; the `weights` guidance never mentioned that the pillar bar is
an independent gate weights cannot move; `## Seed Prompt` had no
skeleton despite both shipped packs sharing a four-part structure with a
load-bearing verbatim sentence; the prose-bullet warning flatly
contradicted `fantasy.md`; `${CLAUDE_PLUGIN_ROOT}` went unexplained for
a non-programmer audience; and nothing stated the `pillar_noun`
no-leading-article convention. The same pass added `## Calibration` —
the cap-versus-gate arithmetic every future pack author has to do. The
corrected template below is the final content; the fix was verified by
authoring a scratch `mystery.md` from this guide alone, which validated
on the first attempt.

Create `plugin/autonovel/shared/genres/TEMPLATE.md`:

````markdown
# Genre Pack Authoring Guide

This file is a guide, not a skeleton — copying it will not produce a
working pack. Create `<name>.md` and paste the block under
[Frontmatter](#frontmatter) below — starting at the `---` line, without
the surrounding backticks — as the very first thing in the file. Then
work down this guide from `## Framing` onward, filling in each `##`
section.

Validate as you go:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/validate_genre_pack.py" <name>.md
```

(`${CLAUDE_PLUGIN_ROOT}` is a variable Claude Code fills in with the
installed plugin's directory. Running the command yourself in a
terminal, substitute the path to `plugin/autonovel` in this repo.)

A pack may live in the plugin (`shared/genres/`) or in a single novel
project (`<project>/genres/`). The project copy wins.

## Roles

`role` is a list, because most packs serve more than one:

- **primary** — owns the pillar dimensions, category weights, plot
  architecture, book shape, and seed prompt.
- **secondary** — contributes additively to a primary. Its weights,
  `pillar_label`, `beat_system`, `shape`, and Plot Architecture are ignored.
- **modifier** — an orthogonal axis (age category, heat level, tone). Only
  its Framing, Genre Contract, Drafting Rules, and `content_register` are
  read. It may not declare `weights`, `pillar_label`, `beat_system`,
  `shape`, or a Pillar Dimensions section.

Romance is `["primary", "secondary"]` — a romance novel, or a romantic
subplot in a fantasy. Erotica is `["primary", "modifier"]`.

A finished pack is switched on from the novel project's `state.json`,
one key per role: `genre` names the primary (defaults to `"general"`
when unset), `genre_secondary` names the single optional secondary, and
`genre_modifiers` is a list of modifier names. A pack must declare the
role of the slot it is used in, and may fill only one slot per project.

## Required

A primary needs `## Framing` and `## Pillar Dimensions`. A modifier needs
neither. Everything else is optional; omit `## Plot Architecture` to inherit
the base Save the Cat structure.

## Calibration

Read this before writing `weights` or `## Pillar Dimensions`.

The foundation loop exits only when BOTH the weighted `overall_score` is
above 7.5 AND the pillar score — the average of *your* pillar
dimensions, on its own — is above 7.0. The pillar bar is an
**independent gate**. `weights` decides how much the pillar contributes
to the overall and nothing else, so lowering `pillar` does not soften
the 7.0 pillar bar; it only removes the pillar's influence on the
overall. A pack that sets `pillar: 15` because "this genre cares less
about worldbuilding" will still refuse to exit the loop on pillar score.

That makes the score caps you write into dimension criteria ("if X,
score 5 max") arithmetic you have to check. Caps are the right tool —
they are what stops a judge from rewarding a real gap — but several low
caps in one section can put the gate out of reach for a book that is
otherwise fine.

Sanity-check before you ship the pack: **if every cap in your section
fired at once, what would the pillar average be, and is it above 7.0?**
Four dimensions capping at 5/5/6/6 average 5.5, so the loop cannot exit
until at least two of those caps stop firing. That is a correct and
useful demand *if* each cap fires only on a genuine defect. A cap an
ordinary competent book trips by accident is mis-set: raise the number
or narrow the trigger — do not delete the cap.

---

## Frontmatter

Paste this into `<name>.md` first, starting at the `---` line. It is JSON
between two `---` lines, not a `##` section — do not add a
`## Frontmatter` heading to your pack.

```
---
{
  "name": "<must match the filename stem>",
  "label": "<human-readable; feeds NOVEL-GENRE at export>",
  "role": ["primary"],
  "pillar_label": "<names the rubric category, e.g. 'Relationship Architecture'>",
  "weights": {"pillar": 40, "character": 30, "structure": 20, "craft": 10},
  "beat_system": "save-the-cat",
  "content_register": {},
  "conflicts_with": [],
  "shape": {
    "chapters": [22, 26],
    "words": [80000, 95000],
    "chapter_words": 3200,
    "pov_default": "third limited past"
  },
  "artifacts": []
}
---
```

`name` must be lowercase letters, digits, and hyphens only, starting
with a letter or digit — `cozy-mystery`, not `Cozy_Mystery` — and must
match the filename stem exactly. Both rules are enforced, so rename the
file and the `name` field together.

`weights` must be integers summing to 100. The four categories it
divides are:

- **pillar** — your own `## Pillar Dimensions`.
- **character** — `character_depth`, `character_distinctiveness`,
  `character_secrets`.
- **structure** — `outline_completeness`, `foreshadowing_balance`.
- **craft** — `internal_consistency`, `voice_clarity`, `canon_coverage`.

Weights set each category's share of `overall_score` and nothing else —
the pillar bar is a separate, independent gate, so lowering `pillar`
makes the pillar no easier to clear (see `## Calibration` above).
Start from 40/30/20/10 and move at most 10-15 points.

`content_register` declares intensity axes and their levels —
`{"heat": "explicit"}`, `{"violence": "off-page"}` — and a declared level
becomes a Genre Contract promise the book must keep. `artifacts` names extra
project files this genre requires; describe each under `## Artifacts`.

## Framing

Terms and personas the rubrics substitute wherever they refer to genre, the
central system, or comparable authors. Use these exact keys.

- genre_noun — "<e.g. 'fantasy novel'>"
- pillar_noun — "<what the prose calls the central system, e.g. 'magic system'>"
- comps — <4-6 authors a genre reader would compare this to>
- seed_persona — <one sentence: who is generating concepts>
- reader_persona — <one sentence: the Genre Reader panel persona>
- writer_persona — <one sentence: the Writer panel persona>

`pillar_noun` is a **bare noun phrase with no leading article** —
`magic system`, not `the magic system`. The rubric prose supplies its own
article around the substitution, so a leading `the` reads as "the the
magic system".

## Pillar Dimensions

Three to six scored dimensions. Each bullet MUST read `- key — criteria`
with an em dash; the validator extracts keys from that shape. Keys must not
collide with the base dimensions (`character_depth`,
`character_distinctiveness`, `character_secrets`, `outline_completeness`,
`foreshadowing_balance`, `internal_consistency`, `voice_clarity`,
`canon_coverage`).

Mind the bullet shape here. The parser reads every **unindented** bullet
in this section whose first word is a bare lowercase identifier —
`- some_key <dash> ...` — as a dimension declaration (or, with the wrong
dash, a malformed one), so a stray prose bullet such as
`- write carefully, judges score 0-10` becomes a dimension key and can
trip the validator. Everything else is safe and welcome: `###`
subsections of supporting prose above the dimension list, bullets
indented by two spaces or more, and bullets whose first word is
capitalized. `fantasy.md` uses all three — two `###` subsections of laws
and measures, full of indented and capitalized prose bullets, sit above
its `### Scored dimensions` list.

Write real rubric criteria, not labels. A judge scores 0-10 against these.
Give each one a concrete test with a number attached, so two judges
reading the same documents land within a point of each other — and read
`## Calibration` above before you set those numbers.

- example_dim — What excellent looks like, what a gap looks like, and one
  concrete test the judge can apply.

## Genre Contract

Binary, checkable promises — not 0-10 scores. A breach caps the score.
`foundation.md` checks these against the outline; `full-novel.md` and
`novel-review` check them against the manuscript.

- <e.g. "The central relationship resolves HEA or HFN.">

## World Sections

Required headings for `world.md`, one per line, in order. Give each one a
`###` body below the list saying what belongs under it — the foundation
agent builds `world.md` from these, and a bare heading tells it nothing.

## Cast Requirements

The roster the foundation loop must build, with the depth each role needs.

## Plot Architecture

Act-by-act shape. Omit this section entirely to inherit the base structure.

## Canon Categories

Categories for `canon.md`. One `###` heading per category, with two or
three example entries as bullets beneath it — each a short, falsifiable
statement followed by its source in parentheses (`world.md`,
`characters.md`, `outline.md`, or `ch_NN`). `novel-seed` renders each
`###` heading here as a `##` section of the project's `canon.md` and the
bullets as its commented-out examples, so the headings must be usable as
section names on their own.

### <Category, e.g. Geography>
- <e.g. "Vael is 12 days' ride north of Tasren. (world.md)">
- <e.g. "The River Kell flows south through Tasren to the sea. (ch_02)">

Most genres want at least Geography, Timeline, Character Facts, Cultural,
and Established In-Story, plus whatever the pillar needs its own category
for (magic system rules, clues and alibis, the relationship's beats).

## Artifacts

One subsection per file named in `artifacts:` — its template, which phase
fills it, and what the rubric checks about it.

## Drafting Rules

Appended to the base 24 in `drafting-rules.md`. Number from 25. May include
a genre-specific banned-phrase list.

## Seed Prompt

What `novel-seed` reads to generate ten concepts. Four parts, in this
order:

1. **The persona block**, introduced by exactly
   `Persona (adopt while generating):` — second person, present tense,
   naming what this genre's concepts must never be.
2. **The required concept fields**, introduced by the sentence
   `Required concept fields (these <genre> fields and phrasings replace
   the neutral scaffold's versions of the same fields):`. That sentence
   is load-bearing — `novel-seed` relies on it to know your fields
   override the neutral scaffold's, so keep the wording and swap only
   `<genre>`. Under it, one block per field: an ALL-CAPS name, a colon,
   and what it must contain. Every pack keeps WORLD, TENSION, THEME, and
   WHY IT'S NOT GENERIC; add or rename the rest for the genre (fantasy
   adds MAGIC/COST, general adds STAKES and WHEN). Every scored pillar
   dimension should have a field feeding it.
3. **The diversity list**, introduced by
   `Aim for DIVERSITY across the ten concepts:` — the axes the ten must
   spread across, so the batch isn't ten variations on one idea.
4. **The DO-NOT list**, introduced by `DO NOT generate:` — this genre's
   exhausted premises, each stated concretely enough to recognize on
   sight.

```
Persona (adopt while generating):

You are <who is generating: the genre's range, what they know>. You
generate novel concepts that are SPECIFIC, SURPRISING, and
STRUCTURALLY SOUND. You never propose <this genre's default cliché>.

Required concept fields (these <genre> fields and phrasings
replace the neutral scaffold's versions of the same fields):

WORLD: <what makes this world specific — make it SENSORY>
<PILLAR FIELD>: <the field this genre's pillar needs — MAGIC/COST,
  STAKES, THE CRIME, whatever your pillar dimensions score>
TENSION: <the central conflict; both PERSONAL and larger, and the
  two in tension with each other>
THEME: <a genuine question with no easy answer — not a message>
WHY IT'S NOT GENERIC: <one sentence>

Aim for DIVERSITY across the ten concepts:
  - <axis: setting, structure, scale, protagonist age, ...>
  - <axis>
  - Mix of tones: <the tones this genre supports>

DO NOT generate:
  - <this genre's most exhausted premise>
  - <the next one>
```
````

- [ ] **Step 2: Verify the template itself is not mistaken for a pack**

Run: `uv run pytest tests/test_genre_pack.py -k shipped -v`
Expected: still fails (no packs yet), but confirm the error names a missing pack rather than `TEMPLATE.md` — the test globs `*.md` and excludes stem `TEMPLATE`.

- [ ] **Step 3: Commit**

```bash
git add plugin/autonovel/shared/genres/TEMPLATE.md
git commit -m "docs: genre pack authoring template"
```

---

## Task 7: The `general` pack

**Files:**
- Create: `plugin/autonovel/shared/genres/general.md`

This is the neutral default. Its low pillar weight is what lets a
contemporary novel clear the foundation gate.

- [ ] **Step 1: Write the pack**

A quality-review pass after this pack shipped made eight corrections,
all of them consequences of `general` being the pack a user gets when
they never chose a genre:

- `pillar_noun` was `"the world of the novel"` — a leading article that
  substitutes into rubric prose as "the the world of the novel". Now the
  bare `"story world"`, matching `fantasy.md`'s bare `"magic system"`.
- `thematic_architecture` and `temporal_grounding` were phrased against a
  manuscript ("without using a word from the manuscript", "if a character
  states the theme aloud anywhere", "a reader should always know"). The
  foundation judge has no manuscript — it gets `voice.md`, `world.md`,
  `characters.md`, `outline.md`, `canon.md`. Both now score "the documents
  you were given", and the theme cap is scoped to the outline and voice.md's
  exemplar passages rather than "anywhere".
- `## World Sections` was six bare headings against `fantasy.md`'s nine
  with `###` bodies — and three of the four pillar dimensions score
  exactly those sections, so the pack was telling the judge what to
  punish and the foundation agent nothing about what to build. All six
  now have `###` bodies.
- `weights` moved from `{pillar: 15, ..., craft: 25}` to
  `{pillar: 20, character: 40, structure: 20, craft: 20}`. The extra
  `craft` weight was meant to encode "prose matters more in literary
  fiction", but `craft` in `foundation.md` is `internal_consistency` +
  `voice_clarity` + `canon_coverage` — two of the three are bookkeeping,
  so the weight mostly upweighted canon hygiene. Properly encoding
  "prose matters" needs a prose dimension in the base rubric; that is
  out of scope for this plan.
- The seed prompt gained a `WHEN` field. `temporal_grounding` is a scored
  pillar dimension and nothing in the seed asked for period, season, or
  elapsed duration.
- `comps` were five interiority-heavy stylists (Robinson, Ishiguro,
  Ferrante, Whitehead, Cusk), and comps feed the reader/writer panel
  personas as well as the seed — a user who wanted a plain contemporary
  novel got pulled toward Marilynne Robinson. Robinson and Cusk out,
  Patchett, Ng, and Tyler in.
- `## Cast Requirements` said "ghost/wound/lie/want/need chain" where
  every other file in the repo says `wound/want/need/lie`, and dropped
  "physical habits and tells" and "key relationships mapped", which
  `fantasy.md` keeps and which matter at least as much here. Aligned and
  restored, in `fantasy.md`'s numbered-roster shape.
- Two DO-NOT additions: the dead or missing child/sibling as the
  premise's whole engine (distinct from the existing "trauma as a
  substitute for character" — there the wound stands in for character,
  here the wound *is* the plot), and the extramarital affair as sole
  spine.

Create `plugin/autonovel/shared/genres/general.md`:

````markdown
---
{
  "name": "general",
  "label": "General Fiction",
  "role": ["primary"],
  "pillar_label": "Setting & Thematic Architecture",
  "weights": {"pillar": 20, "character": 40, "structure": 20, "craft": 20},
  "beat_system": "save-the-cat",
  "content_register": {},
  "conflicts_with": [],
  "shape": {
    "chapters": [20, 30],
    "words": [75000, 95000],
    "chapter_words": 3000,
    "pov_default": "third limited past"
  },
  "artifacts": []
}
---

## Framing

- genre_noun — "novel"
- pillar_noun — "story world"
- comps — Ann Patchett, Kazuo Ishiguro, Elena Ferrante, Colson Whitehead, Celeste Ng, Anne Tyler
- seed_persona — a novelist with wide range and no house style, who generates premises that are specific, surprising, and structurally sound
- reader_persona — a thoughtful reader who finishes 40 novels a year across every shelf in the store, cares about whether a book earns its length, and has no patience for a premise that never pays out
- writer_persona — a published novelist and workshop teacher who reads as a craftsperson and cares about the gap between what a book attempts and what it achieves

## Pillar Dimensions

- setting_specificity — Do places do narrative work, or are they backdrop? A scene should be impossible to relocate without loss. Check: could two scenes in two locations be swapped with only proper nouns changed? If yes, score 5 max.
- social_texture — Class, work, money, family structure, institutions. Are the characters' material circumstances specific and consequential, or is everyone comfortably unplaced? Test: name what each major character does for money and what happens to them if they stop. If the novel cannot answer that for the protagonist, score 5 max. Decorative sociology — detail that never constrains a choice — counts against, not for.
- thematic_architecture — Is there a genuine question the book is asking, stated nowhere and present everywhere? A theme a character articulates aloud is a message, not a theme. Test: from the documents you were given, can you name the question in one sentence without reusing the documents' own phrasing for it? If you cannot, score 5 max. If the outline or an exemplar passage in voice.md has a character state the theme aloud, score 6 max regardless of how well the rest of the plan explores it.
- temporal_grounding — When is this, and does it matter? Period, season, elapsed duration, and the rate at which this world changes. Test: could this story happen unchanged fifty years earlier or later? If yes, and the novel is not deliberately timeless, score 6 max. Also check that elapsed time is trackable in the documents you were given — the outline should let you say, at any chapter, roughly how long it has been since chapter 1.

## Genre Contract

- The novel's central question is posed in the first quarter and answered — or explicitly refused — by the end.
- No speculative element is introduced that the book has not established as part of its world.

## World Sections

Places, institutions, and money are the pillar here the way a magic
system is the pillar in fantasy. Each section below must produce detail
that CONSTRAINS a choice somewhere in the outline; detail that constrains
nothing is decoration and counts against the score, not for it.

- Setting & Place
- Society & Institutions
- Work, Money, Class
- Time & Period
- Cultural Details
- Internal Consistency Rules

### Setting & Place
The primary setting's physical layout and its distinctive property —
what a stranger would notice first and what a resident stopped noticing
years ago. Neighboring or contrasting places (at least 2-3): where
characters go to escape, to work, to be unobserved. A sensory signature
per location — sound, smell, light, weather — specific enough that a
scene set there could not be relocated with only proper nouns changed.

### Society & Institutions
The bodies with power over the characters: employers, schools, churches,
courts, hospitals, councils, landlords, families acting as institutions.
Who decides, who appeals, who has no standing. At least 3-4 with
interests that collide. For each, what it can take away from the
protagonist and by what procedure.

### Work, Money, Class
What each major character does for money, what they are paid, what it
costs them to live, and what happens to them if the money stops. Who
owns what, who owes whom, who inherited and who did not. The specific
markers by which this world reads class — accent, address, schooling,
teeth, car, the way a debt is asked for.

### Time & Period
When this is: year or era, season, and the span the novel covers from
chapter 1 to the end. What is changing in this world during that span
and at what rate — a closing industry, a rising rent, a season turning,
a child growing. What technology, law, money, and news look like here,
concretely enough that the story could not slide fifty years in either
direction unchanged.

### Cultural Details
Customs, taboos, manners, food, clothing, funerals and weddings, what is
said aloud and what never is. The local rules an outsider would break
without knowing. Things that make daily life feel SPECIFIC to this place
rather than to "a town".

### Internal Consistency Rules
Hard constraints a writer must not violate: distances and travel times,
who can afford what, what an institution is and is not allowed to do,
what is physically possible in this setting. This world has no magic —
which means coincidence, sudden money, and convenient authority are the
things that break it. Write down the ones this book must not use.

## Cast Requirements

1. **The protagonist** — derived from the seed.
   - Full wound/want/need/lie chain
   - Three sliders with justification
   - Arc type (positive/negative/flat)
   - Detailed speech pattern (8 dimensions, with example lines)
   - Physical habits and tells connected to their specific
     circumstances (their work, their class, their wound)
   - At least 2 secrets
   - Key relationships mapped

2. **The person closest to the protagonist's central conflict** — same
   depth as the protagonist. What they know and what they're hiding.

3. **An antagonist** — not a villain. Someone whose legitimate interests
   collide with the protagonist's, with their own full
   wound/want/need/lie chain; they should be understandable, not
   evil-for-evil's-sake.

4. **At least two further characters** the story needs, with the depth
   their page time earns — a peer, someone from the other side of the
   institutional line, an ally with divided loyalties.

## Canon Categories

### Geography
- The Halloran house is four blocks from the river. (world.md)
- The mill sits on the east bank, downstream of the bridge. (world.md)
- Ada's classroom is on the second floor of the old wing. (ch_02)

### Timeline
- Ada is 41 when the novel opens. (characters.md)
- The accident happened eleven years before chapter 1. (world.md)
- Ch 1-4 span a single school term. (outline.md)

### Character Facts
- Ada has not driven since the accident. (ch_02)
- Peter took over his father's route in 2009. (characters.md)
- Ada's sister has not been in the house since the funeral. (characters.md)

### Social & Institutional
- The mill closed in 1998 and was never sold. (world.md)
- The school board meets the first Tuesday of the month. (world.md)
- The county owns the land the trailers sit on. (ch_05)

### Cultural
- In this town, funerals are held on Saturdays. (world.md)
- Nobody locks a door on this street, and everybody notices who does. (world.md)
- The diner closes at two; there is nowhere else to talk. (ch_03)

### Established In-Story (things that happened in chapters)
- Ada told Peter the truth in ch_09. It cannot be untold.
- The house sold in ch_11. She cannot go back.
- Ada missed the hearing in ch_07. The ruling stands.

## Drafting Rules

25. Ground every scene in material specifics — what things cost, who pays, who is owed. Abstraction is where general fiction goes to die.

## Seed Prompt

Persona (adopt while generating):

You are a novelist with wide range and no house style — as at home
in a quiet rural interior as in an institutional satire or a hot,
crowded family novel. You generate premises that are SPECIFIC,
SURPRISING, and STRUCTURALLY SOUND. Every concept names a person in
a situation that is already going wrong — never a mood, a milieu,
or a theme in search of a plot.

Required concept fields (these general-fiction fields and phrasings
replace the neutral scaffold's versions of the same fields):

WORLD: The specific social world the book lives in — a place, a
  trade, an institution, a family, a moment. Not "small-town
  America" but which town, whose kitchen, what the work is. Make it
  SENSORY and make it material: what things cost, who pays.
WHEN: The period (year or era), the season it opens in, and roughly how
  much time the story covers end to end. Name one thing that is
  changing in this world over that span — a closing industry, a rising
  rent, a child growing — so the story could not slide fifty years in
  either direction unchanged.
STAKES: What does the protagonist stand to lose, and what makes the
  loss irreversible? Rarely death — in this genre the stakes are a
  marriage, a house, a licence, a child's regard, a version of
  themselves they can no longer claim. Name the loss AND name the
  thing that closes the door behind it.
TENSION: What's the central conflict? It must be both PERSONAL (one
  character's specific problem) and LARGER (it implicates a family,
  a workplace, a town, an institution). These two must be in
  tension with each other.
THEME: What question does this story explore? Not a message — a
  genuine question with no easy answer.
WHY IT'S NOT GENERIC: One sentence on what makes this different from
  the standard literary premise.

Aim for DIVERSITY across the ten concepts:
  - At least one whose engine is work — a trade, a job, an
    institution — rather than a family
  - At least one comic or warm; literary does not mean bleak
  - At least one outside the contemporary Anglo-American middle class
  - At least one with an unusual narrative structure idea (a braided
    timeline, a documentary frame, a collective narrator)
  - At least one plot-forward enough to hold a reader who came for story
  - Span life stages — not ten protagonists in midlife reckoning
  - Mix of tones: dark, warm, wry, melancholy, tender

DO NOT generate:
  - Plotless mood pieces — a premise that is a situation with no
    engine ("a woman returns to her childhood home and reflects")
  - Trauma as a substitute for character — a backstory wound doing
    the work a want and a lie should be doing
  - The unearned epiphany ending, where the protagonist changes
    because the book is ending rather than because the plot cost
    them something
  - "A family gathers and secrets come out"
  - Writers, MFA programs, or novels about writing novels
  - Terminal illness or a funeral as the whole structural spine
  - A dead or vanished child or sibling as the premise's entire
    engine — the loss may exist, but it cannot be the plot
  - The extramarital affair as the whole spine of the book
````

- [ ] **Step 2: Validate the pack**

Run:
```bash
uv run python plugin/autonovel/shared/scripts/validate_genre_pack.py plugin/autonovel/shared/genres/general.md
```
Expected: `OK   plugin/autonovel/shared/genres/general.md`

- [ ] **Step 3: Run the resolver test that needed it**

Run: `uv run pytest tests/test_resolve_genre.py::test_missing_genre_resolves_to_general -v`
Expected: PASS

- [ ] **Step 4: Commit**

```bash
git add plugin/autonovel/shared/genres/general.md
git commit -m "feat: general genre pack (neutral default)"
```

---

## Task 8: The `fantasy` pack

**Files:**
- Create: `plugin/autonovel/shared/genres/fantasy.md`

This is a **lossless port**: the content moves out of the base files, it does
not get rewritten. Source line ranges are given so nothing is paraphrased
away. Read each source before writing the corresponding pack section.

**Sources to port from:**

| Source | Lines | Goes to |
|---|---|---|
| `shared/rubrics/foundation.md` | 87–110 (the five lore dimensions) | `## Pillar Dimensions` |
| `shared/craft/CRAFT.md` | 175–199 (Sanderson's Three Laws of Magic) | `## Pillar Dimensions` supporting detail |
| `shared/craft/CRAFT.md` | 281–285 (Le Guin's Core Insight) | `## Drafting Rules` |
| `shared/craft/CRAFT.md` | 351–356 (Magic System rubric summary) | `## Pillar Dimensions` |
| `skills/novel-foundation/references/layer-guides.md` | 20–30, 39–78 (world.md craft requirements and sections) | `## World Sections` |
| `skills/novel-foundation/references/layer-guides.md` | 137–171 (cast roster) | `## Cast Requirements` |
| `skills/novel-seed/references/seed-prompts.md` | 5–10, 22–49 (persona, fields, DO-NOT list) | `## Seed Prompt` |
| `skills/novel-draft/references/drafting-rules.md` | 27–29 (rule 6, magic as physical sensation) | `## Drafting Rules` |
| `shared/templates/canon.md` | 19–68 (example entries) | `## Canon Categories` |

- [ ] **Step 1: Write the frontmatter and Framing**

Create `plugin/autonovel/shared/genres/fantasy.md` starting with:

````markdown
---
{
  "name": "fantasy",
  "label": "Fantasy",
  "role": ["primary", "secondary"],
  "pillar_label": "Lore & Worldbuilding",
  "weights": {"pillar": 40, "character": 30, "structure": 20, "craft": 10},
  "beat_system": "save-the-cat",
  "content_register": {},
  "conflicts_with": [],
  "shape": {
    "chapters": [22, 26],
    "words": [80000, 95000],
    "chapter_words": 3200,
    "pov_default": "third limited past"
  },
  "artifacts": []
}
---

## Framing

- genre_noun — "fantasy novel"
- pillar_noun — "magic system"
- comps — Sanderson, Le Guin, Jemisin, Rothfuss, Hobb
- seed_persona — a fantasy novelist with deep knowledge of the genre's best works — Tolkien, Le Guin, Rothfuss, Wolfe, Jemisin, Peake, Susanna Clarke, Andrew Peterson, Sofia Samatar — who never proposes generic medieval Europe plus elves
- reader_persona — an avid fantasy reader who reads 50+ novels a year, cares about pacing, mystery, and worldbuilding payoff, and gets bored by beautiful prose that doesn't go anywhere
- writer_persona — a published fantasy author with five novels and a Hugo nomination, who reads as a craftsperson and notices where the beats fall
````

- [ ] **Step 2: Port the pillar dimensions**

Append the five dimensions, moving the criteria text verbatim from
`foundation.md:87–110`. Each bullet must use an em dash after the key:

````markdown
## Pillar Dimensions

- magic_system — Hard rules with COSTS and LIMITATIONS per Sanderson's Second Law. Could a writer resolve the CLIMACTIC CONFLICT using only rules already established? Are costs plot-driving, not decorative? Are there at least 3 societal implications explored with specificity? Is the system TESTABLE — could you write a courtroom scene, a contract negotiation, and a magical confrontation without inventing new rules? Also check First Law compliance (foreshadowed solutions over total magic solutions), that limitations are at least as prominent as powers, and that no new unforeshadowed powers appear in the final 25%.
- world_history — Timeline of events creating PRESENT-DAY tensions. Each historical event should map to a current faction conflict or character motivation. Decorative history (cool but plot-irrelevant) counts against the score, not for it.
- geography_and_culture — Locations distinct with sensory signatures. Cultures with specific customs that GENERATE CONFLICT. Economy that creates class tension. Check: could two different scenes set in two different locations feel meaningfully different based on what's here?
- lore_interconnection — Does changing one element force changes in at least two others? Test by mentally removing the magic system — does the political structure collapse? Does the class system change? Count the elements that survive removal unchanged: if the political structure, the class system, and the economy all still stand, the lore is modular and detachable, score 4 max; if two of the three still stand, score 6 max.
- iceberg_depth — Implied depth versus stated depth. But CHECK: does the author actually know the answers to the mysteries, or are they handwaving? If a planning doc says "the answer will be revealed" without specifying WHAT the answer is, that's a gap wearing an iceberg costume. Test: pick three mysteries the documents gesture at, and for each ask whether the actual answer is written down somewhere in them. Zero answered caps at 4; three answered while the reader is still meant to be in the dark supports 8+.
````

The last sentence of each of those two bullets is the **only** departure
from the verbatim port, added by the quality-review pass after Task 7's
calibration finding. `general.md` has four dimensions with numeric caps
and `fantasy.md` had none, while both are gated at the same
`> 7.0` pillar bar — so the neutral pack written to unblock non-fantasy
novels was arguably stricter than the fantasy pack that blocked them.
The fix was not to weaken `general`'s caps (they are good, and they are
the pattern the remaining seven packs should copy) but to make
`fantasy`'s two least-scoreable criteria countable: "score low" and
"does the author actually know the answers" each let two judges differ
by 3+ points on the same documents. No other criteria text changed, and
neither addition alters what the dimensions are about — the acceptance
test is still that a fantasy project scores within noise of its
pre-change score.

- [ ] **Step 3: Port the remaining sections**

Append `## Genre Contract`, `## World Sections`, `## Cast Requirements`,
`## Canon Categories`, `## Drafting Rules`, and `## Seed Prompt`, moving the
text from the sources in the table above. Do **not** add a
`## Plot Architecture` section — the investigation-driven architecture
currently in `layer-guides.md:242–271` is mystery content, not fantasy
content, and Task 13 deletes it rather than moving it here.

Key content, in order:

```markdown
## Genre Contract

- The climax resolves using rules established before the final quarter. No new powers appear unforeshadowed.
- Every prominently introduced speculative element serves a narrative purpose later, or is an explained red herring.

## World Sections

- Cosmology & History
- Magic System — Hard Rules
- Magic System — Soft Magic / The Protagonist's Exception
- Magic System — Societal Implications
- Geography
- Factions & Politics
- Bestiary / Flora / Natural World
- Cultural Details
- Internal Consistency Rules
```

For `## Cast Requirements`, move `layer-guides.md:137–171` verbatim,
including the institutional antagonist and the absent-but-plot-critical
character. For `## Canon Categories`, move the seven categories and their
example entries from `templates/canon.md:19–68` — the Vael/Tasren/Kael
examples belong here, not in the neutral template. For `## Drafting Rules`,
start at 25 with the ported rule 6 and Le Guin's insight:

```markdown
## Drafting Rules

25. Magic and its costs manifest as SPECIFIC physical sensation defined in world.md — never vague discomfort. Use the exact established sensations.
26. Style is not ornament — it IS the fantasy. The language does not describe the world, it creates it. If the world sounds like a bus schedule, the register is wrong.
```

For `## Seed Prompt`, move the persona, the required fields (including
`MAGIC/COST`), the diversity requirements, and the full DO-NOT list from
`seed-prompts.md:22–49`.

- [ ] **Step 4: Validate**

Run:
```bash
uv run python plugin/autonovel/shared/scripts/validate_genre_pack.py plugin/autonovel/shared/genres/*.md
```
Expected: `OK` for both `fantasy.md` and `general.md`, plus a `SKIP` line
for `TEMPLATE.md` (the glob sweeps it up; the CLI skips it — see Task 3).

- [ ] **Step 5: Run the full script test suite**

Run: `uv run pytest tests/test_genre_pack.py tests/test_resolve_genre.py -v`
Expected: all pass, including `test_cli_validates_all_shipped_packs` and `test_resolves_shipped_plugin_pack`

- [ ] **Step 6: Commit**

```bash
git add plugin/autonovel/shared/genres/fantasy.md
git commit -m "feat: fantasy genre pack (lossless port of existing content)"
```

---

## Task 9: Neutralize the foundation rubric

**Files:**
- Modify: `plugin/autonovel/shared/rubrics/foundation.md`

- [ ] **Step 1: Add the genre pack to the input list**

Replace lines 8–14:

```markdown
INPUT FILES (read all of them from the project directory you were given):
- voice.md
- world.md
- characters.md
- outline.md
- canon.md
```

with:

```markdown
INPUT FILES (read all of them from the project directory you were given):
- voice.md
- world.md
- characters.md
- outline.md
- canon.md

GENRE PACKS: the dispatching prompt gives you the absolute path of one
primary genre pack and, optionally, a secondary pack and any number of
modifier packs. Read them all. They define the pillar dimensions you score,
the category weights you apply, and the genre contract you check. If no pack
path was given, return exactly
{"error": "no genre pack supplied — the invoking skill must resolve one"}
and nothing else.
```

- [ ] **Step 2: Neutralize the framing line**

Replace line 20 `Evaluate these fantasy novel planning documents.` with:

```markdown
Evaluate these planning documents for a novel in the genre named by the
primary pack's `genre_noun`.
```

- [ ] **Step 3: Neutralize the cross-checks**

In the CROSS-CHECKS block, replace the two genre-specific bullets at
lines 67 and 81:

- `- Are there gaps in the magic system that would block a specific` → `- Are there gaps in the pillar system (as the pack defines it) that would block a specific`
- `   - Check if character abilities match magic system rules` → `   - Check that character capabilities match the rules the pack's pillar dimensions govern`

- [ ] **Step 4: Replace the lore dimension block with a pack hook**

Delete lines 86–110 (the `LORE & WORLDBUILDING:` heading and its five
hardcoded dimensions) and replace with:

```markdown
PILLAR (the genre's own category — the primary pack names it in
`pillar_label` and defines its dimensions under `## Pillar Dimensions`):

Score every dimension the primary pack declares, using that pack's stated
criteria. If a secondary pack is loaded, also score its pillar dimensions;
on a key collision the primary's definition wins. Ignore any modifier pack's
pillar dimensions — modifiers do not contribute scored dimensions.
```

- [ ] **Step 5: Add the genre contract check**

After the `CRAFT:` dimension block (ending at line 153), add:

```markdown
GENRE CONTRACT:
Read every loaded pack's `## Genre Contract` section. These are binary
promises, not scored dimensions. Check each one against the OUTLINE — does
the planned ending satisfy it, does the planned structure make it reachable?
List every promise the plan would breach. A breach caps overall_score at 6.
```

- [ ] **Step 6: Replace the output schema**

Replace the JSON block at lines 155–176 with the nested schema:

```markdown
Respond with JSON:
{
  "pillar": {
    "<each dimension key the pack declares>": {"score": N, "gap": "biggest weakness", "fix": "specific improvement", "note": "..."}
  },
  "character": {
    "character_depth": {"score": N, "gap": "...", "fix": "...", "note": "..."},
    "character_distinctiveness": {"score": N, "gap": "...", "fix": "...", "note": "..."},
    "character_secrets": {"score": N, "gap": "...", "fix": "...", "note": "..."}
  },
  "structure": {
    "outline_completeness": {"score": N, "gap": "...", "fix": "...", "note": "..."},
    "foreshadowing_balance": {"score": N, "gap": "...", "fix": "...", "note": "..."}
  },
  "craft": {
    "internal_consistency": {"score": N, "gap": "...", "fix": "...", "note": "..."},
    "voice_clarity": {"score": N, "gap": "...", "fix": "...", "note": "..."},
    "canon_coverage": {"score": N, "gap": "...", "fix": "...", "note": "..."}
  },
  "genre_contract": {"violations": ["list any promises the plan would breach"], "note": "..."},
  "slop_in_planning_docs": {"found": ["list any AI slop patterns found in exemplar dialogue, voice examples, or character descriptions"], "note": "..."},
  "contradictions_found": ["list any factual contradictions between documents"],
  "overall_score": N,
  "pillar_score": N,
  "weakest_dimension": "...",
  "top_3_improvements": ["ranked list of the 3 highest-leverage improvements"]
}

`pillar_score` is the mean of the pillar category's dimension scores.
`weakest_dimension` is a bare dimension key from any category.
```

- [ ] **Step 7: Replace the hardcoded weighting**

Replace lines 178–180:

```markdown
WEIGHTING: lore/worldbuilding 40%, character 30%, structure 20%, craft 10%.
A novel with thin worldbuilding but a complete outline is WORSE than deep
worldbuilding with an incomplete outline.
```

with:

```markdown
WEIGHTING: use the `weights` object in the primary pack's frontmatter —
pillar, character, structure, and craft, summing to 100. Ignore any
secondary or modifier pack's weights; only the primary's apply.
overall_score is the weighted mean of the four category means.
```

- [ ] **Step 7b: Close the plumbing gaps a judge simulation found**

Steps 1-7 neutralize the rubric correctly, but running it as a clean-room
judge against both shipped packs surfaced six places where the surrounding
machinery is under-specified. None is in the pillar criteria — those got
sharper — but each makes two judges diverge on the same documents.

Apply all six:

1. **Numeric format.** Add next to the WEIGHTING block: dimension scores
   are integers 0-10; `overall_score` and `pillar_score` are decimals to
   two places, never rounded to integers. **This is the one that matters
   most** — a judge who rounds cannot express any value between 7 and 8,
   which silently turns the `> 7.5` gate into `>= 8`.
2. **Cross-check 2's example was still magic-shaped.** "can the
   protagonist's ability do what the climax requires? What established
   rule resolves the climactic conflict?" reads as the wrong question for
   a realist pack whose pillar is Setting & Thematic Architecture. Replace
   with a pack-agnostic form: does the plan establish, before the climax,
   whatever the climax relies on — a rule, a capability, an institution's
   power, a relationship's ground?
3. **Cross-check 4** has the same shape: "character capabilities match the
   rules the pack's pillar dimensions govern" → "what characters can do
   matches whatever constrains them in the pack's pillar dimensions — a
   magic system's rules, an institution's reach, a period's technology, a
   household's money."
4. **`weakest_dimension` tie-break.** A plausible mediocre plan produced a
   genuine five-way tie at score 3. Specify: on a tie, the tied dimension
   in the most heavily weighted category; if still tied, first-listed.
   This field drives which layer the foundation loop revises next.
5. **Operationalize the genre-contract cap.** State that it applies to the
   final weighted mean after computation, that `pillar_score` is never
   capped, and that `genre_contract.note` must say whether the cap bound
   or was inert. Without the `pillar_score` clause, a breaching plan can
   satisfy the pillar gate while `overall_score` is pinned at 6 — the loop
   then spins to its iteration cap with no field explaining why.
6. **Schema placeholders.** `"<each dimension key the pack declares>"` is a
   literal string a judge may emit verbatim. Make it a parenthetical
   instruction, and say the object key is always the literal `pillar` —
   `pillar_label` is for prose only.

Also fix the FINAL CHECK, which is now self-contradictory: it says "revise
down" a score that Step 7 made a computed mean. It must say to revise the
dimension scores and recompute.

- [ ] **Step 8: Verify no fantasy terms remain**

Run:
```bash
grep -niE 'fantasy|magic|sanderson' plugin/autonovel/shared/rubrics/foundation.md
```
Expected: no output

- [ ] **Step 9: Commit**

```bash
git add plugin/autonovel/shared/rubrics/foundation.md
git commit -m "refactor: foundation rubric reads pillar dimensions from genre pack"
```

---

## Task 10: Neutralize the remaining rubrics

**Files:**
- Modify: `plugin/autonovel/shared/rubrics/chapter.md`
- Modify: `plugin/autonovel/shared/rubrics/full-novel.md`
- Modify: `plugin/autonovel/shared/rubrics/adversarial-edit.md`
- Modify: `plugin/autonovel/shared/rubrics/reader-panel.md`
- Modify: `plugin/autonovel/shared/rubrics/manuscript-review.md`

Each of these gets the same genre-pack input block added after its existing
INPUT FILES list. Use this exact wording in all five:

```markdown
GENRE PACKS: the dispatching prompt gives you the absolute path of one
primary genre pack and, optionally, a secondary pack and modifier packs.
Read them. Use each pack's `## Framing` values wherever this rubric refers
to the genre, the pillar, or comparable authors.
```

- [ ] **Step 1: chapter.md**

- Line 36: `Evaluate this fantasy novel chapter against the planning docs.` → `Evaluate this chapter against the planning docs. The primary pack's genre_noun names the genre.`
- Line 39: `9-10: Among the best chapters you've read in published fantasy. Name` → `9-10: Among the best chapters you've read in the pack's genre. Name`
- Lines 113–115: `Does ANY passage sound like generic fantasy prose that could appear in any novel? If yes, score 7 max.` → `Does ANY passage sound like generic genre prose that could appear in any novel of this kind? If yes, score 7 max.`
- Line 147: `magic system rules, timeline, established events, physical descriptions.` → `the pillar system's rules, timeline, established events, physical descriptions.`
- Rename the `lore_integration` dimension to `pillar_integration` at lines 149–151 and in the JSON schema at line 167, and replace its criteria with: `Does the world do WORK in this chapter, or is it set dressing? Judge against what the primary pack's pillar dimensions say matters. A scene that could happen anywhere in the genre with find-and-replace on proper nouns scores 5 max.`

- [ ] **Step 2: full-novel.md**

- Line 24: `Evaluate this complete fantasy novel holistically.` → `Evaluate this complete novel holistically.`
- Line 53: `- world_consistency: Any lore contradictions across chapters?` → `- pillar_consistency: Any contradictions across chapters in the systems the primary pack's pillar dimensions govern?`
- Update the JSON key at line 63 from `world_consistency` to `pillar_consistency`.
- Add a genre-contract dimension after line 55: `- genre_contract: Read every loaded pack's ## Genre Contract. These are binary promises checked against the finished manuscript, not scored dimensions. A breach caps novel_score at 6.`
- Add to the JSON schema: `"genre_contract": {"violations": ["..."], "note": "..."},`

- [ ] **Step 3: adversarial-edit.md**

Line 20: `You are editing a fantasy novel chapter. Your job: identify exactly` → `You are editing a novel chapter. Your job: identify exactly`

- [ ] **Step 4: reader-panel.md**

- Lines 29–38 (Persona: The Genre Reader): replace the fantasy-specific body with `You are the reader the primary pack's `reader_persona` describes. Adopt that persona exactly. You compare everything to the authors in the pack's `comps`. You are generous with what you love and blunt about what bores you.`
- Lines 40–48 (Persona: The Writer): replace the first sentence with `You are the writer the primary pack's `writer_persona` describes.` Keep the rest of the persona (structure, beats, "I forgot I was reading") — it is genre-neutral craft.
- Line 63: `You have just read a complete fantasy novel in summary form. The` → `You have just read a complete novel in summary form. The`
- Leave the Editor and First Reader personas untouched; they are already neutral.

- [ ] **Step 5: manuscript-review.md**

After line 18 (`honest. You don't *have* to find defects.`), add:

```markdown
Before the two reviews, check every loaded pack's `## Genre Contract`
against the manuscript. Report any breach as the first numbered item in the
professor's review, tagged `[severity: major]`.
```

- [ ] **Step 6: Verify**

Run:
```bash
grep -rniE 'fantasy|sanderson|jemisin|rothfuss|hobb|hugo' plugin/autonovel/shared/rubrics/
```
Expected: no output

- [ ] **Step 7: Commit**

```bash
git add plugin/autonovel/shared/rubrics/
git commit -m "refactor: neutralize chapter, full-novel, adversarial, panel, and review rubrics"
```

---

## Task 11: Extract fantasy craft from CRAFT.md

**Files:**
- Modify: `plugin/autonovel/shared/craft/CRAFT.md`

The content being removed was already ported into the fantasy pack in Task 8.
Verify it is there before deleting.

- [ ] **Step 1: Confirm the fantasy pack has the content**

Run:
```bash
grep -c "Second Law\|Le Guin" plugin/autonovel/shared/genres/fantasy.md
```
Expected: at least 2

- [ ] **Step 2: Delete Sanderson's Three Laws**

Delete lines 175–199 (`### Sanderson's Three Laws of Magic` through the
THIRD LAW block). Replace with:

```markdown
### The Genre's Own System Laws

The primary genre pack's pillar dimensions define what rigor the speculative
or central system requires — and how much. Some genres demand hard,
legible rules with stated costs; others are undermined by that legibility.
Do not import one genre's expectations into another.
```

- [ ] **Step 3: Neutralize the worldbuilding pillars**

Line 206: `  - MAGICAL: the speculative element(s)` → `  - SPECULATIVE: the genre's central non-realist element, if it has one`

Lines 212–213: replace the magic-specific interconnection rule with:
```markdown
Interconnection: If the world has a central system, trace its implications
  through society, economy, warfare, religion. A system with zero cultural
  impact is shallow.
```

- [ ] **Step 4: Neutralize the prose section**

Delete lines 281–285 (`### Le Guin's Core Insight` and its body) — this is in
the fantasy pack now. Retitle line 287 from `### What the best fantasy prose does` to `### What the best prose does`. Leave lines 287–304 (the eight
qualities and the Le Guin Exercise) intact; they are genre-neutral craft.

- [ ] **Step 5: Neutralize the rubric summary**

Replace lines 351–356 (`### Magic System` and its five bullets) with:

```markdown
### The Genre Pillar
  - Scored against the primary pack's `## Pillar Dimensions`, not against
    any fixed list here.
```

- [ ] **Step 6: Verify**

Run:
```bash
grep -niE 'fantasy|magic|bestiary' plugin/autonovel/shared/craft/CRAFT.md
```
Expected: no output

Do NOT also grep for `sanderson` here. Three attributions survive by
design — `Promises, Progress, Payoff (Sanderson)`, `MICE Quotient (Orson
Scott Card / Sanderson)`, and `The Three Sliders (Sanderson)` — because
they cite genre-neutral structural frameworks, not fantasy content.
Deleting a correct citation to satisfy a regex would be the wrong trade.
Task 20's leak guard exempts `shared/craft/` from the comp-author check
for exactly this reason, and pins those three strings so the exemption
cannot be used to quietly strip them.

- [ ] **Step 7: Commit**

```bash
git add plugin/autonovel/shared/craft/CRAFT.md
git commit -m "refactor: move fantasy-specific craft out of CRAFT.md"
```

---

## Task 12: Neutralize the templates

**Files:**
- Modify: `plugin/autonovel/shared/templates/world.md`
- Modify: `plugin/autonovel/shared/templates/canon.md`
- Modify: `plugin/autonovel/shared/templates/voice.md`
- Modify: `plugin/autonovel/shared/templates/state.json`

- [ ] **Step 1: Replace world.md wholesale**

```markdown
# World Bible

<!-- Section headings are written at project init from the resolved genre
     pack's `## World Sections`. If this file still shows this comment, the
     foundation loop has not run its world pass yet. -->
```

- [ ] **Step 2: Replace canon.md's fantasy examples**

Keep lines 1–17 (the header and "How to use" block) verbatim. Replace
everything from line 19 to the end with:

```markdown
<!-- Categories and example entries are written at project init from the
     resolved genre pack's `## Canon Categories`. One fact per bullet,
     short, specific, checkable, with its source in parentheses. -->
```

- [ ] **Step 3: Neutralize voice.md**

Line 102: `(a merchant's inventory, a spell's components), earn it. Don't` → `(a merchant's inventory, a recipe's ingredients), earn it. Don't`

- [ ] **Step 4: Add genre fields to state.json**

```json
{
  "phase": "foundation",
  "current_focus": null,
  "genre": null,
  "genre_secondary": null,
  "genre_modifiers": [],
  "iteration": 0,
  "foundation_score": 0.0,
  "pillar_score": 0.0,
  "chapters_drafted": 0,
  "chapters_total": 0,
  "novel_score": 0.0,
  "revision_cycle": 0,
  "review_round": 0,
  "debts": []
}
```

- [ ] **Step 5: Verify**

Run:
```bash
grep -rniE 'magic|bestiary|vael|tasren|kael|vessa|moren|ashenmoor|drennan|spell' plugin/autonovel/shared/templates/
```
Expected: no output

- [ ] **Step 6: Commit**

```bash
git add plugin/autonovel/shared/templates/
git commit -m "refactor: neutralize world, canon, voice templates; add genre fields to state"
```

---

## Task 13: Rewrite layer-guides.md

**Files:**
- Modify: `plugin/autonovel/skills/novel-foundation/references/layer-guides.md`

The heaviest file. Three kinds of change: defer to the pack, delete leaked
mystery content, and remove hardcoded book shape.

- [ ] **Step 1: Add a preamble**

After line 7 (the `---` following the intro), insert:

```markdown
## Genre packs

Before filling any layer, run the resolver from the project directory:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/resolve_genre.py"
```

Read every pack path it reports. The packs define this novel's world
sections, cast requirements, plot architecture, canon categories, book
shape, and any extra artifacts. Where a section below says "from the pack,"
the pack's content governs and this guide only states the standard of depth.

---
```

- [ ] **Step 2: Replace the world.md craft requirements**

Replace lines 18–30 (from `belongs to THIS story, not a generic fantasy setting.` through the CRAFT REQUIREMENTS bullet list) with:

```markdown
belongs to THIS story, not a generic setting for its genre.

CRAFT REQUIREMENTS:
- Whatever central system the pack's pillar dimensions govern must meet the
  rigor those dimensions demand — read them before writing.
- Trace the system's implications through society, economy, law, religion.
- At least 2-3 societal implications explored in depth.
- History must create PRESENT-DAY TENSIONS that drive the plot, not just
  backdrop.
- Geography must be specific and sensory, not generic for the genre.
- Iceberg principle: imply more than you state.
- Interconnection: pulling one thread should move everything.
```

- [ ] **Step 3: Replace the hardcoded world.md sections**

Replace lines 32–79 (`STRUCTURE THE DOCUMENT WITH THESE SECTIONS:` through
the `### Internal Consistency Rules` body) with:

```markdown
STRUCTURE THE DOCUMENT WITH THE SECTIONS LISTED IN THE PACK'S
`## World Sections`, in that order. For each, be specific: named, sensory,
and consequential. Every rule gets a COST or LIMITATION stated alongside it.
Include 2-3 unexplained-but-intriguing facts per section for iceberg depth.
```

Keep lines 80–94 (the IMPORTANT block and word target) except replace the
`~3000-4000 words` target with `Target the word count the pack's shape
implies for a world bible — dense, not padded, roughly 3-4% of the novel's
target length.`

- [ ] **Step 4: Replace the cast roster with a pack hook**

Replace lines 137–171 (`BUILD THE REGISTRY WITH ROLES THE STORY NEEDS.`
through item 7) with:

```markdown
BUILD THE REGISTRY WITH THE ROLES LISTED IN THE PACK'S
`## Cast Requirements`, at the depth each entry specifies. Add any further
characters the seed's plot demands.
```

Leave lines 173–198 (FOR EACH CHARACTER INCLUDE, and the IMPORTANT block)
intact — they are genre-neutral.

- [ ] **Step 5: Remove the hardcoded book shape**

Line 204: `Build a complete chapter outline. Target: 22-26 chapters, ~80,000 words total (~3,000-4,000 words per chapter).` → `Build a complete chapter outline. Use the chapter count, total word count, and per-chapter target from the resolved pack's `shape`.`

- [ ] **Step 6: Make the beat field pack-driven**

Line 223: `- **Save the Cat beat:** which beat this chapter serves (Opening Image, Setup, Catalyst, etc.)` → `- **Beat:** which beat this chapter serves, in the vocabulary of the pack's `beat_system` (for `save-the-cat`: Opening Image, Setup, Catalyst, etc.)`

- [ ] **Step 7: Delete the leaked mystery architecture**

Delete lines 242–263 (`KEY PLOT ARCHITECTURE` and its four act bullets)
entirely. This is mystery content that leaked from the first novel — it is
**not** moved to the fantasy pack. Replace with:

```markdown
KEY PLOT ARCHITECTURE: follow the pack's `## Plot Architecture` if it
declares one. If it does not, use the base act structure from CRAFT.md:
Act I 0-23%, Act II 23-77%, Act III 77-100%, with Save the Cat beats at
their stated percentage marks.
```

In the CONSTRAINTS block that follows, delete line 268–271 (`The
investigation should feel like a mystery plot overlaid on whatever the
protagonist's personal arc is`) — same reason. Keep every other constraint.

- [ ] **Step 8: Add artifacts and genre contract to the fill order**

At the end of the file, after the `canon.md` section, add:

```markdown
---

## Genre artifacts

If the resolved pack declares `artifacts`, create and fill each one
following the pack's `## Artifacts` section. Fill them after canon.md, and
re-check them whenever the layer they draw on changes. They are scored:
the pack's pillar dimensions reference them.

---

## Genre contract

Before exiting foundation, read every loaded pack's `## Genre Contract` and
confirm the OUTLINE satisfies each promise. A plan that cannot keep the
contract is a plan to write the wrong book — fix the outline, not the
contract.
```

- [ ] **Step 9: Verify**

Run:
```bash
grep -niE 'fantasy|magic|sanderson|investigation|22-26' plugin/autonovel/skills/novel-foundation/references/layer-guides.md
```
Expected: no output

- [ ] **Step 10: Commit**

```bash
git add plugin/autonovel/skills/novel-foundation/references/layer-guides.md
git commit -m "refactor: layer-guides defers to genre pack; drop leaked mystery architecture"
```

---

## Task 14: Neutralize seed generation

**Files:**
- Modify: `plugin/autonovel/skills/novel-seed/references/seed-prompts.md`
- Modify: `plugin/autonovel/skills/novel-seed/SKILL.md`

- [ ] **Step 1: Replace seed-prompts.md wholesale**

```markdown
# Seed Generation Prompts

The resolved genre pack supplies the persona, the required concept fields,
the DO-NOT list, and the diversity requirements. This file is the neutral
scaffold around them.

## Persona (adopt while generating)

Adopt the primary pack's `seed_persona`. You generate novel concepts that
are SPECIFIC, SURPRISING, and STRUCTURALLY SOUND. Each concept should make a
reader think 'I've never seen THAT before.'

## Generating fresh concepts

Generate ten seed concepts in the pack's genre. Each should be a complete
premise you could build a novel from.

For EACH concept provide, in this order:

NUMBER. TITLE (a working title, evocative, not generic)
HOOK: One sentence that would make someone pick up the book. Specific and
  surprising, not "In a world where..."
WORLD: What makes this world different? Be concrete and SENSORY.
<the pack's required fields from its `## Seed Prompt`, in the order it lists
 them — e.g. MAGIC/COST for fantasy, THE CRIME for mystery>
TENSION: What's the central conflict? It must be both PERSONAL (one
  character's specific problem) and LARGER (affects more than one life).
  These two must be in tension with each other.
THEME: What question does this story explore? Not a message — a genuine
  question with no easy answer.
WHY IT'S NOT GENERIC: One sentence on what makes this different from
  standard fare in this genre.

Aim for DIVERSITY across the ten concepts, following the pack's diversity
requirements. In every genre: mix tones (dark, warm, weird, melancholy,
whimsical), include at least one that is quieter and more literary than the
genre's default, and at least one with an unusual narrative structure idea.

DO NOT generate anything on the pack's DO-NOT list.

## Riffing on a user idea

The user's seed idea is quoted below.

Generate 5 variations on this concept. Keep what's interesting about the core
idea but push it in different directions. For each variation:

NUMBER. TITLE
HOOK: One sentence.
HOW IT DIFFERS: What did you change from the original seed and why?
WORLD: Concrete, sensory world details.
<the pack's required fields>
TENSION: Personal + larger conflict.
THEME: The question it explores.

Make the variations genuinely different from each other — don't just tweak
surface details. Change the protagonist, the setting, the tone, the
structure, the thematic focus.
```

- [ ] **Step 2: Add genre selection to novel-seed/SKILL.md**

Insert a new step between the current steps 2 and 3:

```markdown
3. **Choose the genre.** List the packs in
   `"${CLAUDE_PLUGIN_ROOT}/shared/genres/"` (excluding TEMPLATE.md) with
   their `label`, and ask the user to pick a primary. Offer an optional
   secondary and any modifiers, explaining that a secondary contributes
   additively (a romance subplot in a fantasy) and a modifier is an
   orthogonal axis (YA, cozy, heat level). If the user declines to choose,
   use `general`. Write `genre`, `genre_secondary`, and `genre_modifiers`
   into state.json, then verify the stack resolves:

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/resolve_genre.py"
   ```

   If it exits non-zero, fix the selection before continuing — a conflicting
   stack (for example `ya` with `erotica`) is rejected here rather than
   producing an incoherent book.
```

- [ ] **Step 3: Render the pack-driven templates at init**

In step 2's template-copy bullet, after the `cp` line, add:

```markdown
   - Write `world.md`'s section headings from the resolved pack's
     `## World Sections`, and `canon.md`'s category headings and one example
     entry each from its `## Canon Categories`. Create any file named in the
     pack's `artifacts` from its `## Artifacts` template.
```

- [ ] **Step 4: Replace the MAGIC/COST validation**

In the current step 4 (Selection), replace `Present the concepts compactly
(TITLE + HOOK + MAGIC/COST, matching the field names in seed-prompts.md)`
with `Present the concepts compactly (TITLE + HOOK + the pack's first
required field that the neutral scaffold does not already define)`.

That qualifier matters. Both shipped packs list `WORLD` first, but the
scaffold defines `WORLD` too — so "first required field" would render
TITLE + HOOK + WORLD, and the user would choose between concepts by their
least distinguishing attribute. The behavior this replaces showed
`MAGIC/COST`, the genre-specific field. That field is second in both packs
(`MAGIC/COST` in fantasy, `STAKES` in general), and it is what makes two
concepts in the same genre actually different from each other.

In the current step 5, replace the four required elements with:

```markdown
5. **Write `seed.txt`** with the full chosen concept. Verify it contains a
   world-differentiator (the WORLD field), a central tension (TENSION), a
   concrete sensory anchor in the WORLD field, and every field the pack's
   `## Seed Prompt` marks required — and strengthen any that are missing
   before saving.
```

- [ ] **Step 5: Verify**

Run:
```bash
grep -rniE 'fantasy|magic|tolkien|elves|dwarves|orcs' plugin/autonovel/skills/novel-seed/
```
Expected: no output

- [ ] **Step 6: Commit**

```bash
git add plugin/autonovel/skills/novel-seed/
git commit -m "refactor: genre selection in novel-seed; neutral seed prompts"
```

---

## Task 15: Neutralize drafting

**Files:**
- Modify: `plugin/autonovel/skills/novel-draft/references/drafting-rules.md`
- Modify: `plugin/autonovel/skills/novel-draft/SKILL.md`

- [ ] **Step 1: Neutralize the writer's stance**

Replace lines 6–15 with:

```markdown
## Writer's stance

You are a literary fiction writer drafting a chapter of a novel in the genre
the resolved pack names. You write in the POV and tense the pack's
`shape.pov_default` specifies unless voice.md Part 2 overrides it — voice.md
wins on any conflict. You follow the voice definition exactly. You hit every
beat in the outline. You never use words from the banned list. You show,
never tell emotions. Your prose is specific, sensory, grounded. Metaphors
come from the character's experience. You vary sentence length. You trust the
reader. You write the FULL chapter — do not truncate, summarize, or skip
ahead.
```

- [ ] **Step 2: Make the word target pack-driven**

Rule 1 (line 19): `1. Write the COMPLETE chapter. Target ~3,200 words. Do not truncate or summarize.` → `1. Write the COMPLETE chapter. Target the pack's `shape.chapter_words`. Do not truncate or summarize.`

Rule 2 (line 21): replace `Third-person limited, past tense, locked to the chapter's designated POV character (from the outline).` with `The POV and tense established in voice.md Part 2, locked to the chapter's designated POV character (from the outline).`

- [ ] **Step 3: Replace rule 6**

Replace lines 27–29 (rule 6, magic and its costs) with:

```markdown
6. The genre's central system, where it appears, manifests as SPECIFIC
   physical or concrete detail defined in world.md — never vague. Use the
   exact established specifics.
```

- [ ] **Step 4: Add the pack rules hook**

At the end of the file, add:

```markdown
## Genre rules (25+)

Read every loaded pack's `## Drafting Rules` and follow them alongside the
24 above. Where a pack supplies a banned-phrase list, treat it with the same
force as voice.md Part 1's Tier 1 list.
```

- [ ] **Step 5: Wire the skill**

In `novel-draft/SKILL.md`, add to the required-reading block (after line 24):

```markdown
   - every genre pack path reported by
     `python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/resolve_genre.py"`
```

And in the judge dispatch at line 47, add the pack paths to the prompt:

```markdown
   "Read the rubric at `<absolute plugin path>/shared/rubrics/chapter.md`
   and the genre pack(s) at `<resolved pack paths, primary first>`, and
   follow the rubric exactly.
```

- [ ] **Step 6: Verify**

Run:
```bash
grep -rniE 'fantasy|magic' plugin/autonovel/skills/novel-draft/
```
Expected: no output

- [ ] **Step 7: Commit**

```bash
git add plugin/autonovel/skills/novel-draft/
git commit -m "refactor: drafting rules read POV, word target, and genre rules from pack"
```

---

## Task 16: Wire novel-foundation

**Files:**
- Modify: `plugin/autonovel/skills/novel-foundation/SKILL.md`

- [ ] **Step 1: Update the gate in the intro**

Line 9: `foundation_score > 7.5 AND lore_score > 7.0` → `foundation_score > 7.5 AND pillar_score > 7.0`

- [ ] **Step 2: Resolve the genre in setup**

Add to the Setup block as a new item after item 1:

```markdown
2. **Resolve the genre.** Run from the project directory:

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/resolve_genre.py"
   ```

   If it exits non-zero, STOP and report — an unresolvable or conflicting
   genre stack must be fixed before any layer work. Keep the reported pack
   paths; every judge dispatch below needs them. If `state.json` has no
   `genre` field at all, STOP and run the migration in `novel/SKILL.md`
   first.
```

Renumber the following items, and add the pack paths to the required
reading list.

- [ ] **Step 3: Add packs to the judge dispatch**

Replace the dispatch prompt at lines 54–60 with:

```markdown
   "Read the rubric at `<absolute plugin path>/shared/rubrics/foundation.md`
   and the genre pack(s) at `<resolved pack paths, primary first, each
   labeled with its role>`, and follow the rubric exactly. The project
   directory is `<absolute project path>`. The input files are: voice.md,
   world.md, characters.md, outline.md, canon.md (all in the project
   directory). Return ONLY the JSON object the rubric specifies."
```

- [ ] **Step 4: Update score handling**

- Line 68–70: `The results.tsv score column takes `overall_score`; put `lore_score` in the description (e.g. `iter N: <dimension> (lore <lore_score>)`).` → `...put `pillar_score` in the description (e.g. `iter N: <dimension> (pillar <pillar_score>)`).`
- Line 71: gate check → `overall_score > 7.5` AND `pillar_score > 7.0`
- Line 82: `update `foundation_score`, `lore_score`, and `iteration`` → `update `foundation_score`, `pillar_score`, and `iteration``

- [ ] **Step 5: Update the cross-layer check**

Line 77: `character abilities match the magic rules` → `character capabilities match the rules the pack's pillar dimensions govern; every genre artifact the pack declares is filled and current`

- [ ] **Step 6: Add the genre-change baseline reset**

In the Keep/discard item, after the resume sentence, add:

```markdown
   If the project's genre changed since the last scored iteration (compare
   `genre`/`genre_secondary`/`genre_modifiers` against the most recent
   `genre-change` marker row in results.tsv), do NOT compare against the old
   best score — the weights differ, so the numbers are not comparable.
   Treat the next scored iteration as the first one.
```

- [ ] **Step 7: Add the genre contract to Exit**

In the Exit block, before the state.json write, add:

```markdown
Do not exit while any loaded pack's `## Genre Contract` is unsatisfiable by
the outline — the judge reports these under `genre_contract.violations`.
Fix the outline first.
```

- [ ] **Step 8: Commit**

```bash
git add plugin/autonovel/skills/novel-foundation/SKILL.md
git commit -m "refactor: novel-foundation resolves genre, gates on pillar_score"
```

---

## Task 17: Wire the remaining skills

**Files:**
- Modify: `plugin/autonovel/skills/novel-revise/SKILL.md`
- Modify: `plugin/autonovel/skills/novel-review/SKILL.md`
- Modify: `plugin/autonovel/skills/novel-export/SKILL.md`
- Modify: `plugin/autonovel/skills/novel/SKILL.md`

- [ ] **Step 1: novel-revise — three judge dispatches**

At lines 46 (adversarial-edit), 124 (reader-panel), and 281 (full-novel), add
the pack paths to each prompt using the same phrasing as Task 16 step 3:
`and the genre pack(s) at <resolved pack paths, primary first>`.

Add a resolver call to the skill's setup so the paths are available.

- [ ] **Step 2: novel-review — one dispatch**

At line 37, add the pack paths to the manuscript-review prompt the same way,
plus a resolver call in setup.

- [ ] **Step 3: novel-export — genre from the pack**

Replace the genre-sourcing clause at lines 37–39 (`genre from seed.txt or the
...`) with:

```markdown
   genre — run `python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/resolve_genre.py"`
   and offer `display_label` as the default `NOVEL-GENRE` (e.g. "Fantasy
   Romance"); let the user edit it, since hybrid genre names are not
   reliably composable from pack labels.
```

- [ ] **Step 4: novel/SKILL.md — report genre and relabel the gate**

In step 2 (Gather state), add:

```markdown
   - the resolved genre: run
     `python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/resolve_genre.py"` and
     report `label_parts` and each pack's role. If it exits non-zero,
     report the error — do not attempt to fix it (this skill is read-only).
```

In step 3 (Report), change `foundation > 7.5 AND lore > 7.0` to
`foundation > 7.5 AND pillar > 7.0`, and add genre to the reported table.

- [ ] **Step 5: Verify**

Run:
```bash
grep -rniE '\blore_score\b|\blore >' plugin/autonovel/
```
Expected: no output

- [ ] **Step 6: Commit**

```bash
git add plugin/autonovel/skills/
git commit -m "refactor: pass genre packs to revise, review, export, and router skills"
```

---

## Task 18: Wire novel-import

**Files:**
- Modify: `plugin/autonovel/skills/novel-import/SKILL.md`
- Modify: `plugin/autonovel/skills/novel-import/references/extraction-guide.md`

- [ ] **Step 1: Add genre inference to SKILL.md**

Insert a new step after the current step 3 (Chapter intake):

```markdown
4. **Infer the genre.** From the manuscript you have now read in full,
   propose a primary pack, an optional secondary, and any modifiers, naming
   the evidence for each (the speculative elements present, the shape of the
   central conflict, the register, the content). Show the user the available
   packs from `"${CLAUDE_PLUGIN_ROOT}/shared/genres/"` and your proposal,
   and ask them to confirm or correct it — same shape as the MYSTERY.md
   confirmation in the final steps. Write the choice into state.json and
   verify with `resolve_genre.py`. In a fully autonomous run, take your own
   inference and say so in the handoff report.
```

Renumber the steps that follow.

- [ ] **Step 2: Make extraction pack-driven**

In `extraction-guide.md`, replace the world.md section's hardcoded section
list (lines 36–40) with:

```markdown
Output must contain the sections listed in the resolved genre pack's
`## World Sections` — but every entry is reconstructed from what the prose
actually shows, not proposed fresh. A section the manuscript gives no
material for is recorded as `[not established in manuscript]` rather than
invented.
```

Replace the canon categories reference (line 222) with `Output follows the
resolved pack's `## Canon Categories`` and neutralize the "magic/speculative
system" phrasing at lines 31 and 43 to "the genre's central system, if the
manuscript has one".

- [ ] **Step 3: Add genre fields to the state rules**

In the `## state.json` section, add:

```markdown
- `genre`, `genre_secondary`, `genre_modifiers`: the confirmed inference
  from step 4. Never leave `genre` null on an import — an imported
  manuscript always has an observable genre, even if the answer is
  `general`.
```

- [ ] **Step 4: Verify**

Run:
```bash
grep -rniE 'fantasy|bestiary' plugin/autonovel/skills/novel-import/
```
Expected: no output

- [ ] **Step 5: Commit**

```bash
git add plugin/autonovel/skills/novel-import/
git commit -m "refactor: novel-import infers and confirms genre"
```

---

## Task 19: Wire the scripts

**Files:**
- Modify: `plugin/autonovel/shared/scripts/gen_brief.py:79`
- Modify: `plugin/autonovel/shared/scripts/slop_score.py`
- Test: `tests/test_gen_brief.py` (append)

- [ ] **Step 1: Write the failing test**

Append to `tests/test_gen_brief.py`:

```python
def test_brief_uses_genre_diction_rule_when_pack_resolves(tmp_path):
    setup_project(tmp_path)
    (tmp_path / "state.json").write_text(json.dumps({"genre": "fantasy"}))
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--eval", "5"],
        capture_output=True, text=True, cwd=tmp_path,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    content = (tmp_path / "briefs/ch05_eval.md").read_text()
    assert "generic fantasy diction" in content


def test_brief_falls_back_to_neutral_diction_rule(tmp_path):
    setup_project(tmp_path)
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--eval", "5"],
        capture_output=True, text=True, cwd=tmp_path,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    content = (tmp_path / "briefs/ch05_eval.md").read_text()
    assert "generic genre diction" in content
```

- [ ] **Step 2: Run to verify failure**

Run: `uv run pytest tests/test_gen_brief.py -k diction -v`
Expected: FAIL — the brief contains the hardcoded fantasy string in both cases

- [ ] **Step 3: Make the rule pack-driven**

In `gen_brief.py`, add near the other path constants:

```python
GENRES_DIR = Path(__file__).resolve().parent.parent / "genres"
STATE_PATH = BASE_DIR / "state.json"
```

And replace line 79 with a lookup:

```python
    rules.append(genre_diction_rule())
```

Add the helper above `extract_voice_rules`:

```python
def genre_diction_rule() -> str:
    """Voice rule naming the genre whose diction the prose must not default to.

    Falls back to a neutral phrasing when no genre is set or the pack is
    missing — gen_brief must never fail because of genre resolution.
    """
    genre = None
    if STATE_PATH.exists():
        try:
            genre = json.loads(STATE_PATH.read_text(encoding="utf-8")).get("genre")
        except (json.JSONDecodeError, OSError):
            genre = None
    noun = "genre"
    if genre:
        for base in (BASE_DIR / "genres", GENRES_DIR):
            pack = base / f"{genre}.md"
            if pack.exists():
                noun = genre
                break
    return (f"Vocabulary from craft/trade/body wells — no generic {noun} "
            "diction")
```

- [ ] **Step 4: Run to verify pass**

Run: `uv run pytest tests/test_gen_brief.py -v`
Expected: all pass

- [ ] **Step 5: Let slop_score.py take a genre banned list**

Add to `slop_score.py` after the `TIER3_FILLER` block:

```python
def load_genre_banned(path=None):
    """Extra banned phrases from a genre pack's '## Drafting Rules' section.

    The pack lists them one per line under a 'BANNED PHRASES:' marker inside
    that section. Returns [] when no pack or no marker is present — a genre
    without its own slop vocabulary is the normal case.
    """
    if path is None:
        return []
    try:
        text = Path(path).read_text(encoding="utf-8")
    except OSError:
        return []
    match = re.search(r"^BANNED PHRASES:\s*$(.*?)(?=^##\s|\Z)",
                      text, re.M | re.S)
    if not match:
        return []
    return [line.strip("- ").strip()
            for line in match.group(1).splitlines() if line.strip()]
```

Then wire it into the CLI. `slop_score.py` currently reads file paths from
`sys.argv[1:]` directly; replace that with argparse so the pack path can be
passed alongside them:

```python
def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="+", help="chapter files to score")
    parser.add_argument("--genre-pack", default=None,
                        help="genre pack whose banned phrases extend Tier 1")
    args = parser.parse_args(argv)

    extra_banned = load_genre_banned(args.genre_pack)
    reports = [slop_score(Path(f).read_text(encoding="utf-8"),
                          extra_banned=extra_banned)
               for f in args.files]
    ...
```

Add `import argparse` and `from pathlib import Path` at the top if absent,
and give `slop_score()` an `extra_banned=()` keyword that its Tier 1 loop
scans in addition to `TIER1_BANNED`:

```python
def slop_score(text, extra_banned=()):
    ...
    for word in list(TIER1_BANNED) + list(extra_banned):
        ...
```

- [ ] **Step 6: Add a test for the genre banned list**

Append to `tests/test_slop_score.py`:

```python
def test_genre_banned_phrases_extend_tier1(tmp_path):
    pack = tmp_path / "testgenre.md"
    pack.write_text(
        "---\n{}\n---\n\n## Drafting Rules\n\nBANNED PHRASES:\n"
        "- quivering member\n- velvet heat\n",
        encoding="utf-8")
    chapter = tmp_path / "ch_01.md"
    chapter.write_text("His quivering member. " * 5, encoding="utf-8")
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(chapter),
         "--genre-pack", str(pack)],
        capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr
    report = json.loads(result.stdout)
    assert report["summary"]["max_penalty"] > 0
```

Run: `uv run pytest tests/test_slop_score.py -v`
Expected: all pass, including the existing tests — the argparse change must
not break the positional-files invocation they use.

- [ ] **Step 7: Commit**

```bash
git add plugin/autonovel/shared/scripts/ tests/test_gen_brief.py
git commit -m "feat: gen_brief and slop_score read genre-specific rules"
```

---

## Task 20: The genre leak guard

**Files:**
- Create: `tests/test_no_genre_leak.py`

The enforceable successor to the De-Bells rule. This is what stops the fix
from eroding.

- [ ] **Step 1: Write the test**

Create `tests/test_no_genre_leak.py`:

```python
"""Guard: no genre-specific content outside plugin/autonovel/shared/genres/.

The successor to the De-Bells rule. The original plan scrubbed content from
the first novel out of the machinery; this keeps the machinery free of any
single genre's assumptions.
"""
import re
from pathlib import Path

import pytest

PLUGIN = Path(__file__).parent.parent / "plugin/autonovel"

SCANNED_DIRS = ["shared/rubrics", "shared/craft", "shared/templates",
                "shared/scripts", "skills"]

# Terms that name one genre's furniture. A hit outside shared/genres/ means
# a genre assumption crept back into the base machinery.
# Genre furniture. A hit anywhere outside shared/genres/ means a genre
# assumption crept back into the base machinery.
LEAK_RE = re.compile(
    r"\b(fantasy|magic|magical|sorcer\w*|wizard|bestiary|elves|dwarves"
    r"|orcs)\b", re.I)

# Author names are a separate check, because they mean different things in
# different places. In a rubric or a skill they are comps — genre content,
# and a leak. In CRAFT.md they are citations on genre-neutral structural
# frameworks ("Promises, Progress, Payoff (Sanderson)", "MICE Quotient
# (Orson Scott Card / Sanderson)", "The Three Sliders (Sanderson)"), which
# must survive. Stripping an attribution to satisfy a regex would be worse
# than the regex being over-broad.
COMPS_RE = re.compile(
    r"\b(sanderson|tolkien|jemisin|rothfuss|hobb|le guin|rowling)\b", re.I)
COMPS_EXEMPT_DIRS = ("shared/craft",)

# ANTI-SLOP.md and voice.md list 'realm' and 'tapestry' as banned slop words,
# which is vocabulary guidance, not genre content. Nothing else is exempt.
ALLOWED = {
    "shared/craft/ANTI-SLOP.md",
    "shared/templates/voice.md",
}


def scanned_files():
    for directory in SCANNED_DIRS:
        for path in sorted((PLUGIN / directory).rglob("*")):
            if not path.is_file():
                continue
            if path.suffix not in {".md", ".py", ".json"}:
                continue
            rel = path.relative_to(PLUGIN).as_posix()
            if rel in ALLOWED:
                continue
            yield rel, path


def _offenders(pattern, skip_dirs=()):
    found = []
    for rel, path in scanned_files():
        if any(rel.startswith(d) for d in skip_dirs):
            continue
        for lineno, line in enumerate(
                path.read_text(encoding="utf-8").splitlines(), start=1):
            match = pattern.search(line)
            if match:
                found.append(
                    f"{rel}:{lineno}: {match.group(0)!r} in {line.strip()!r}")
    return found


def test_no_genre_terms_outside_genre_packs():
    offenders = _offenders(LEAK_RE)
    assert not offenders, (
        "genre-specific content found outside shared/genres/:\n  "
        + "\n  ".join(offenders))


def test_no_comp_authors_outside_genre_packs():
    """Comp authors are genre content in a rubric or skill, citations in CRAFT.md."""
    offenders = _offenders(COMPS_RE, skip_dirs=COMPS_EXEMPT_DIRS)
    assert not offenders, (
        "comparable-author names found outside shared/genres/ — these belong "
        "in a pack's `comps`:\n  " + "\n  ".join(offenders))


def test_craft_citations_survived():
    """The exemption is scoped, not a blanket pass.

    CRAFT.md's structural frameworks carry author attributions that must NOT
    be stripped to satisfy the guard. If these disappear, someone 'fixed' a
    false positive by deleting a correct citation.
    """
    craft = (PLUGIN / "shared/craft/CRAFT.md").read_text(encoding="utf-8")
    for citation in ("Promises, Progress, Payoff (Sanderson)",
                     "MICE Quotient (Orson Scott Card / Sanderson)",
                     "The Three Sliders (Sanderson)"):
        assert citation in craft, f"citation removed from CRAFT.md: {citation}"


def test_guard_actually_scans_something():
    """A regex guard that scans zero files always passes. Prove it doesn't."""
    assert len(list(scanned_files())) > 20
```

- [ ] **Step 2: Run the test**

Run: `uv run pytest tests/test_no_genre_leak.py -v`
Expected: PASS. If it fails, the failure message names every remaining leak with file and line — fix each one; do not add it to `ALLOWED` unless it is genuinely vocabulary guidance rather than genre content.

- [ ] **Step 3: Commit**

```bash
git add tests/test_no_genre_leak.py
git commit -m "test: guard against genre content outside genre packs"
```

---

## Task 21: Migration for existing projects

**Files:**
- Modify: `plugin/autonovel/skills/novel/SKILL.md`

Existing projects have no `genre` field and were scored under fantasy
weights. Taking the `general` default silently would both mislabel them and
break score comparability.

- [ ] **Step 1: Add migration detection**

Add a new step 3 to `novel/SKILL.md`, before the Report step:

```markdown
3. **Migration check.** If `state.json` has no `genre` key, this project
   predates genre packs. Report this and offer the migration — do NOT apply
   it silently, and do NOT default to `general`:

   - Suggest `fantasy`, because that is what the project's existing scores
     in results.tsv were produced under. Explain that picking anything else
     changes the rubric's weights, which resets the score baseline.
   - On the user's confirmation, add `genre`, `genre_secondary: null`, and
     `genre_modifiers: []` to state.json, and rename the `lore_score` key to
     `pillar_score` in place.
   - If the project has scored history in results.tsv AND the chosen genre
     is anything other than `fantasy`, also append a marker row:
     `<ISO timestamp>\t<phase>\t0\t0\tgenre-change\tgenre set to <name>; score baseline reset`
   - This skill is otherwise read-only; the migration is the one exception,
     and only with explicit confirmation.
```

Renumber the steps that follow.

- [ ] **Step 2: Document the same rule for later genre changes**

Add to the end of the migration step:

```markdown
   The same marker row and baseline reset apply any time a project's genre
   changes later, not only at migration. `novel-foundation` reads the most
   recent `genre-change` row to decide whether the previous best score is
   still a valid comparison.
```

- [ ] **Step 3: Commit**

```bash
git add plugin/autonovel/skills/novel/SKILL.md
git commit -m "feat: genre migration for pre-pack projects with baseline reset"
```

---

## Task 22: Full verification

**Files:** none modified — this is the acceptance gate.

- [ ] **Step 1: Run the whole test suite**

Run: `uv run pytest tests/ -v`
Expected: all pass, including the five pre-existing test files

- [ ] **Step 2: Validate every shipped pack**

Run:
```bash
uv run python plugin/autonovel/shared/scripts/validate_genre_pack.py plugin/autonovel/shared/genres/*.md
```
Expected: `OK` for `fantasy.md` and `general.md`, and no line for `TEMPLATE.md` (it is passed by the glob, so confirm it either validates or is excluded — if the glob picks it up and it fails, exclude `TEMPLATE.md` explicitly in the command and note it in the pack authoring guide)

- [ ] **Step 3: Validate the plugin**

Run: `claude plugin validate plugin/autonovel`
Expected: no errors

- [ ] **Step 4: Confirm the leak guard is green**

Run: `uv run pytest tests/test_no_genre_leak.py -v`
Expected: PASS

- [ ] **Step 5: Manual smoke — the bug that motivated this**

The pipeline's real behavior is model-driven and cannot be unit tested. Run
these by hand and record the results in the commit message:

1. Create a scratch project, set `genre: "general"`, and run
   `/autonovel:novel-foundation` on a contemporary premise. Confirm the
   judge returns a `pillar` object with the general pack's four dimensions,
   that `pillar_score` is populated, and that the gate is reachable. **This
   is the acceptance test for the whole plan.**

   **Record the iteration count, not just pass/fail.** `general`'s four
   dimensions carry score caps at 5/5/5-or-6/6. If two of the three 5-caps
   fire at once, the remaining two must average above 9 to clear
   `pillar_score > 7.0` — and this rubric reserves 9+ for work where the
   judge genuinely struggled to find flaws. So the gate is unreachable in
   any single iteration where two 5-caps fire.

   That is not necessarily wrong: the loop targets the weakest dimension
   each pass, so a cap is a "fix this before proceeding" signal rather than
   a wall, and clearing it is exactly the work the loop exists to do. The
   open question is whether 15 iterations is enough. `fantasy` carries no
   comparable caps, so the two packs are not calibrated to the same bar.

   Judge the result on iterations used:
   - Clears in under 8 — the caps are working as intended, no action.
   - Clears in 8-15 — tight but functional; note it and move on.
   - Hits the 15-iteration cap — the caps are a cliff rather than a
     gradient. Do NOT fix this by weakening the criteria; they are the
     best-discriminating scoring text in the repo and the pattern the
     remaining seven packs should copy. Fix it by making the caps scale
     (e.g. "score 5 max" becomes "subtract 2, floor 3"), or by giving
     `fantasy` matching caps so both packs face the same bar and the gate
     itself can be re-tuned against a consistent scale.
2. Take an existing fantasy project, run the migration, and run one
   foundation iteration. Confirm the score lands within ~0.5 of its last
   pre-change score — the lossless-port check.
3. Set `genre_secondary` on a fantasy project and confirm `resolve_genre.py`
   reports both packs and that a foundation judge dispatch includes both
   paths.

- [ ] **Step 6: Commit the smoke results**

```bash
git commit --allow-empty -m "chore: genre parameterization smoke test results

<paste the three results here>"
```

---

## Known gap to close before phases 3-4

`content_register` has no controlled vocabulary and no validation. An
author can write `{"violence": "on-page but not graphic"}` and it passes,
because any string is accepted. Two consequences: the value becomes a
Genre Contract promise the book must keep, with nothing defining what it
means; and `resolve_genre.py`'s `merge()` hard-fails a resolve when two
packs choose differently-worded levels that mean the same thing —
`"closed-door"` versus `"fade to black"` would be treated as a genuine
disagreement.

This is harmless with two shipped packs and no `content_register` values
in use. It becomes a real problem the moment `erotica`, `cozy`, and `ya`
are authored, since those are the packs the field exists for, and they
may be written in parallel. Define the allowed axes and their levels —
probably `heat`, `violence`, `language`, each with an ordered scale — and
validate against them, before authoring those three.

## Follow-on work (not in this plan)

Spec phases 3 and 4 — authoring `science-fiction`, `romance`, `mystery`,
`thriller`, `erotica`, `ya`, and `cozy`. Each is a self-contained pack file
validated by `validate_genre_pack.py` and covered by the existing
`test_cli_validates_all_shipped_packs` test, so they need no further
mechanism work. `romance` and `mystery` should come first: romance has no
world at all, and mystery is the first pack to declare an artifact, so
together they prove the design across its widest span.
