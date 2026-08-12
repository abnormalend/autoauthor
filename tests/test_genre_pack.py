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


# --- validate_pack ------------------------------------------------------------

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


# --- Additional coverage: branches the plan's test block leaves untested ------

def test_malformed_dimension_dash_reports_em_dash_requirement(tmp_path):
    # Editors autocorrect '—' to '-' or '–'; the validator must call this out
    # by name rather than just reporting "need 3-6" while dimensions are
    # visibly present on screen.
    body = VALID_PRIMARY_BODY.replace("- alpha_dim — First criteria.",
                                      "- alpha_dim - First criteria.")
    errors = validate(tmp_path, "testgenre", VALID_PRIMARY_META, body=body)
    assert any("alpha_dim" in e and "em dash" in e for e in errors)


def test_duplicate_dimension_keys_report_dupes(tmp_path):
    body = VALID_PRIMARY_BODY.replace("- gamma_dim — Third criteria.",
                                      "- alpha_dim — Third criteria.")
    errors = validate(tmp_path, "testgenre", VALID_PRIMARY_META, body=body)
    assert any("duplicate pillar dimension" in e and "alpha_dim" in e
               for e in errors)


def test_primary_without_weights_is_reported(tmp_path):
    meta = {k: v for k, v in VALID_PRIMARY_META.items() if k != "weights"}
    errors = validate(tmp_path, "testgenre", meta)
    assert any("'weights' is required" in e for e in errors)


def test_weights_missing_key(tmp_path):
    meta = {**VALID_PRIMARY_META,
            "weights": {"pillar": 40, "character": 30, "structure": 30}}
    errors = validate(tmp_path, "testgenre", meta)
    assert any("missing key" in e and "craft" in e for e in errors)


def test_weights_non_integer_value(tmp_path):
    meta = {**VALID_PRIMARY_META,
            "weights": {"pillar": 40.5, "character": 30, "structure": 20,
                        "craft": 9.5}}
    errors = validate(tmp_path, "testgenre", meta)
    assert any("must be integers" in e and "pillar" in e and "craft" in e
               for e in errors)


def test_shape_must_be_json_object(tmp_path):
    meta = {**VALID_PRIMARY_META, "shape": [22, 26]}
    errors = validate(tmp_path, "testgenre", meta)
    assert any("'shape' must be a JSON object" in e for e in errors)


def test_shape_range_must_be_two_integers(tmp_path):
    meta = {**VALID_PRIMARY_META,
            "shape": {**VALID_PRIMARY_META["shape"], "chapters": [22]}}
    errors = validate(tmp_path, "testgenre", meta)
    assert any("shape.chapters" in e and "two-integer range" in e
               for e in errors)


def test_shape_words_range_must_be_ordered(tmp_path):
    meta = {**VALID_PRIMARY_META,
            "shape": {**VALID_PRIMARY_META["shape"], "words": [95000, 80000]}}
    errors = validate(tmp_path, "testgenre", meta)
    assert any("shape.words" in e and "not ordered" in e for e in errors)


def test_conflicts_with_must_be_list(tmp_path):
    meta = {**VALID_PRIMARY_META, "conflicts_with": "nosuchpack"}
    errors = validate(tmp_path, "testgenre", meta)
    assert any("'conflicts_with' must be a list" in e for e in errors)


def test_artifacts_must_be_list(tmp_path):
    meta = {**VALID_PRIMARY_META, "artifacts": "canon.md"}
    errors = validate(tmp_path, "testgenre", meta)
    assert any("'artifacts' must be a list" in e for e in errors)


def test_label_missing_is_reported(tmp_path):
    meta = {k: v for k, v in VALID_PRIMARY_META.items() if k != "label"}
    errors = validate(tmp_path, "testgenre", meta)
    assert any("'label' must be a non-empty string" in e for e in errors)


def test_label_empty_is_reported(tmp_path):
    meta = {**VALID_PRIMARY_META, "label": ""}
    errors = validate(tmp_path, "testgenre", meta)
    assert any("'label' must be a non-empty string" in e for e in errors)


def test_name_non_string_is_reported(tmp_path):
    meta = {**VALID_PRIMARY_META, "name": 123}
    errors = validate(tmp_path, "testgenre", meta)
    assert any("'name' must be a non-empty string" in e for e in errors)
