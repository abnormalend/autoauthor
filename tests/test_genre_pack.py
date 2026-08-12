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
