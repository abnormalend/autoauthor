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


# --- section_body / parse_pack: further edge cases ---------------------------

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
#
# Tests below are grouped by the frontmatter field or section they exercise,
# not by which task or plan revision introduced them. Packs built from a
# single mutation of VALID_PRIMARY_META/VALID_PRIMARY_BODY assert the exact
# error list (== [...]) — that's what catches a fix in one branch silently
# tripping a second, contradictory message elsewhere. Packs with more than
# one deliberate defect, or whose exact wording depends on set iteration
# order, use any(...) instead.

def validate(tmp_path, name, meta, body=VALID_PRIMARY_BODY, known=None):
    path = write_pack(tmp_path, name, meta, body)
    return genre_pack.validate_pack(genre_pack.parse_pack(path),
                                    known_names=known)


# --- valid packs: anchor cases -------------------------------------------

def test_valid_primary_has_no_errors(tmp_path):
    assert validate(tmp_path, "testgenre", VALID_PRIMARY_META) == []


def test_valid_modifier_has_no_errors(tmp_path):
    meta = {"name": "testmod", "label": "Test Mod", "role": ["modifier"],
            "content_register": {"heat": "explicit"},
            "conflicts_with": []}
    body = "## Framing\n\n- comps — Someone.\n\n## Genre Contract\n\n- Something binary.\n"
    assert validate(tmp_path, "testmod", meta, body=body) == []


# --- name -----------------------------------------------------------------

def test_name_must_match_filename(tmp_path):
    meta = {**VALID_PRIMARY_META, "name": "mismatch"}
    errors = validate(tmp_path, "testgenre", meta)
    assert errors == [
        "frontmatter 'name' is 'mismatch' but the filename stem is 'testgenre'"
    ]


def test_name_non_string_is_reported(tmp_path):
    meta = {**VALID_PRIMARY_META, "name": 123}
    errors = validate(tmp_path, "testgenre", meta)
    assert errors == ["frontmatter 'name' must be a non-empty string"]


def test_name_must_use_resolver_safe_characters(tmp_path):
    # 'Cozy_Mystery' matches its own filename stem, so the stem check
    # passes it — but resolve_genre.py's NAME_RE rejects it at resolve
    # time. Validation must fail at authoring time instead, when the
    # author is still looking at the file.
    meta = {**VALID_PRIMARY_META, "name": "Cozy_Mystery"}
    errors = validate(tmp_path, "Cozy_Mystery", meta)
    assert errors == [
        "frontmatter 'name' is 'Cozy_Mystery'; a pack name must be "
        "lowercase letters, digits, and hyphens only, starting with a "
        "letter or digit (e.g. 'cozy-mystery') — rename the file to match"
    ]


def test_hyphenated_lowercase_name_is_valid(tmp_path):
    meta = {**VALID_PRIMARY_META, "name": "cozy-mystery"}
    assert validate(tmp_path, "cozy-mystery", meta) == []


# --- label ------------------------------------------------------------------

def test_label_missing_is_reported(tmp_path):
    meta = {k: v for k, v in VALID_PRIMARY_META.items() if k != "label"}
    errors = validate(tmp_path, "testgenre", meta)
    assert errors == ["frontmatter 'label' must be a non-empty string"]


def test_label_empty_is_reported(tmp_path):
    meta = {**VALID_PRIMARY_META, "label": ""}
    errors = validate(tmp_path, "testgenre", meta)
    assert errors == ["frontmatter 'label' must be a non-empty string"]


# --- role ---------------------------------------------------------------------

def test_role_must_be_non_empty_list(tmp_path):
    meta = {**VALID_PRIMARY_META, "role": []}
    errors = validate(tmp_path, "testgenre", meta)
    assert errors == ["frontmatter 'role' must be a non-empty list"]


def test_role_must_be_known(tmp_path):
    meta = {**VALID_PRIMARY_META, "role": ["primary", "bogus"]}
    errors = validate(tmp_path, "testgenre", meta)
    valid = ", ".join(sorted(genre_pack.ROLES))
    assert errors == [
        f"frontmatter 'role' has unknown role(s) bogus; valid roles: {valid}"
    ]


def test_role_non_string_element_does_not_crash(tmp_path):
    # A pack author guessing at a richer schema (e.g. {"role": "primary"}
    # nested under a key) must get a message, not a TypeError from the
    # 'r not in ROLES' membership test hashing an unhashable dict.
    meta = {**VALID_PRIMARY_META, "role": ["primary", {"x": 1}]}
    errors = validate(tmp_path, "testgenre", meta)
    valid = ", ".join(sorted(genre_pack.ROLES))
    assert errors == [
        "frontmatter 'role' has unknown role(s) {'x': 1}; "
        f"valid roles: {valid}"
    ]


def test_role_non_string_element_in_modifier_only_check_does_not_crash(tmp_path):
    # Distinct crash site from the one above: modifier_only's set(role)
    # construction, not the unknown-role membership test. A role list of
    # ["modifier", <dict>] must not raise building that set.
    meta = {"name": "testmod", "label": "Test Mod",
            "role": ["modifier", {"x": 1}]}
    errors = validate(tmp_path, "testmod", meta,
                      body="## Framing\n\n- comps — Someone.\n")
    valid = ", ".join(sorted(genre_pack.ROLES))
    assert errors == [
        "frontmatter 'role' has unknown role(s) {'x': 1}; "
        f"valid roles: {valid}"
    ]


# --- weights ------------------------------------------------------------------

def test_weights_required_when_absent(tmp_path):
    meta = {k: v for k, v in VALID_PRIMARY_META.items() if k != "weights"}
    errors = validate(tmp_path, "testgenre", meta)
    assert errors == [
        "frontmatter 'weights' is required for primary and secondary packs"
    ]


def test_weights_wrong_type_is_not_reported_as_missing(tmp_path):
    # A pack with "weights": [40, 30, 20, 10] has weights right there on
    # screen — telling the author it's "required" would be misleading.
    meta = {**VALID_PRIMARY_META, "weights": [40, 30, 20, 10]}
    errors = validate(tmp_path, "testgenre", meta)
    assert errors == [
        "frontmatter 'weights' must be a JSON object mapping "
        "pillar/character/structure/craft to integers"
    ]


def test_weights_missing_key(tmp_path):
    meta = {**VALID_PRIMARY_META,
            "weights": {"pillar": 40, "character": 30, "structure": 30}}
    errors = validate(tmp_path, "testgenre", meta)
    assert errors == ["'weights' missing key(s): craft"]


def test_weights_non_integer_value(tmp_path):
    meta = {**VALID_PRIMARY_META,
            "weights": {"pillar": 40.5, "character": 30, "structure": 20,
                        "craft": 9.5}}
    errors = validate(tmp_path, "testgenre", meta)
    assert errors == [
        "'weights' values must be integers; non-integer key(s): pillar, craft"
    ]


def test_weights_bool_is_not_accepted_as_integer(tmp_path):
    # bool is an int subclass in Python; {"pillar": true} must not slip
    # past the integer check and get summed as 1.
    meta = {**VALID_PRIMARY_META,
            "weights": {"pillar": True, "character": 30, "structure": 20,
                        "craft": 9}}
    errors = validate(tmp_path, "testgenre", meta)
    assert errors == [
        "'weights' values must be integers; non-integer key(s): pillar"
    ]


def test_weights_must_sum_to_100(tmp_path):
    meta = {**VALID_PRIMARY_META,
            "weights": {"pillar": 40, "character": 30, "structure": 20, "craft": 5}}
    errors = validate(tmp_path, "testgenre", meta)
    assert errors == ["'weights' sum to 95, must sum to 100"]


# --- primary structure: pillar_label and the Framing section ------------------

def test_primary_requires_pillar_label(tmp_path):
    meta = {k: v for k, v in VALID_PRIMARY_META.items() if k != "pillar_label"}
    errors = validate(tmp_path, "testgenre", meta)
    assert errors == [
        "frontmatter 'pillar_label' is required for primary packs"
    ]


def test_primary_missing_framing_and_pillar_dimensions_sections(tmp_path):
    errors = validate(tmp_path, "testgenre", VALID_PRIMARY_META,
                      body="## Drafting Rules\n\n25. Something.\n")
    assert errors == [
        "primary pack must have a '## Framing' section",
        "add a '## Pillar Dimensions' section with 3-6 bullets, each "
        "reading '- <key> — <criteria>' with an em dash",
    ]


# --- modifier restrictions ------------------------------------------------

def test_modifier_may_not_declare_weights(tmp_path):
    meta = {"name": "testmod", "label": "Test Mod", "role": ["modifier"],
            "weights": {"pillar": 40, "character": 30, "structure": 20, "craft": 10}}
    errors = validate(tmp_path, "testmod", meta,
                      body="## Framing\n\n- comps — Someone.\n")
    assert errors == ["modifier pack's frontmatter must not declare 'weights'"]


def test_modifier_may_not_have_pillar_dimensions(tmp_path):
    meta = {"name": "testmod", "label": "Test Mod", "role": ["modifier"]}
    errors = validate(tmp_path, "testmod", meta, body=VALID_PRIMARY_BODY)
    assert errors == [
        "modifier pack must not have a '## Pillar Dimensions' section"
    ]


# --- pillar dimensions --------------------------------------------------------

def test_dimensions_missing_section_reported_for_primary(tmp_path):
    body = "## Framing\n\n- genre_noun — \"test novel\"\n"
    errors = validate(tmp_path, "testgenre", VALID_PRIMARY_META, body=body)
    assert errors == [
        "add a '## Pillar Dimensions' section with 3-6 bullets, each "
        "reading '- <key> — <criteria>' with an em dash"
    ]


def test_dimensions_missing_section_reported_for_secondary_too(tmp_path):
    # The section requirement must not be gated on is_primary: a
    # secondary-only pack with no '## Pillar Dimensions' section previously
    # got only "has 0 dimension(s); need 3-6" and was never told to add the
    # section at all.
    meta = {"name": "testsec", "label": "Test Sec", "role": ["secondary"],
            "weights": {"pillar": 40, "character": 30, "structure": 20,
                        "craft": 10},
            "conflicts_with": [], "artifacts": []}
    errors = validate(tmp_path, "testsec", meta,
                      body="## Framing\n\n- x — y.\n")
    assert errors == [
        "add a '## Pillar Dimensions' section with 3-6 bullets, each "
        "reading '- <key> — <criteria>' with an em dash"
    ]


def test_dimension_count_must_be_three_to_six(tmp_path):
    body = VALID_PRIMARY_BODY.replace("- gamma_dim — Third criteria.\n", "")
    errors = validate(tmp_path, "testgenre", VALID_PRIMARY_META, body=body)
    assert errors == [
        "'## Pillar Dimensions' has 2 dimension(s); need 3-6, and each "
        "bullet must read '- <key> — <criteria>' with an em dash"
    ]


def test_malformed_dimension_dash_reports_em_dash_requirement(tmp_path):
    # Editors autocorrect '—' to '-' or '–'. This must produce exactly the
    # em-dash message, not also a "has 2 dimension(s); need 3-6" message
    # that contradicts the 3 bullets visibly on screen (one malformed, two
    # well-formed) — that contradiction was live until malformed bullets
    # were counted toward the range check.
    body = VALID_PRIMARY_BODY.replace("- alpha_dim — First criteria.",
                                      "- alpha_dim - First criteria.")
    errors = validate(tmp_path, "testgenre", VALID_PRIMARY_META, body=body)
    assert errors == [
        "pillar dimension(s) alpha_dim use a hyphen or en dash; an em "
        "dash (—) is required"
    ]


def test_dimensions_may_not_collide_with_reserved(tmp_path):
    body = VALID_PRIMARY_BODY.replace("- alpha_dim — First criteria.",
                                      "- voice_clarity — Colliding.")
    errors = validate(tmp_path, "testgenre", VALID_PRIMARY_META, body=body)
    reserved = ", ".join(sorted(genre_pack.RESERVED_DIMENSIONS))
    assert errors == [
        "pillar dimension(s) voice_clarity collide with reserved base "
        f"dimensions; reserved: {reserved}"
    ]


def test_duplicate_dimension_keys_report_dupes(tmp_path):
    body = VALID_PRIMARY_BODY.replace("- gamma_dim — Third criteria.",
                                      "- alpha_dim — Third criteria.")
    errors = validate(tmp_path, "testgenre", VALID_PRIMARY_META, body=body)
    assert errors == ["duplicate pillar dimension key(s): alpha_dim"]


# --- conflicts_with -------------------------------------------------------

def test_conflicts_with_must_be_list(tmp_path):
    meta = {**VALID_PRIMARY_META, "conflicts_with": "nosuchpack"}
    errors = validate(tmp_path, "testgenre", meta)
    assert errors == ["frontmatter 'conflicts_with' must be a list"]


def test_conflicts_with_must_resolve(tmp_path):
    known = {"testgenre", "general"}
    meta = {**VALID_PRIMARY_META, "conflicts_with": ["nosuchpack"]}
    errors = validate(tmp_path, "testgenre", meta, known=known)
    known_str = ", ".join(sorted(known))
    assert errors == [
        "frontmatter 'conflicts_with' names unknown pack(s) nosuchpack; "
        f"known packs: {known_str}"
    ]


def test_conflicts_with_non_string_element_does_not_crash(tmp_path):
    # An author guessing at a richer schema (a {"pack": ..., "reason": ...}
    # object instead of a bare name string) must get a message, not a
    # TypeError from hashing an unhashable dict against known_names.
    known = {"testgenre", "general"}
    bad = {"pack": "ya", "reason": "unspecified"}
    meta = {**VALID_PRIMARY_META, "conflicts_with": [bad]}
    errors = validate(tmp_path, "testgenre", meta, known=known)
    known_str = ", ".join(sorted(known))
    assert errors == [
        f"frontmatter 'conflicts_with' names unknown pack(s) {bad}; "
        f"known packs: {known_str}"
    ]


# --- shape ----------------------------------------------------------------

def test_shape_must_be_json_object(tmp_path):
    meta = {**VALID_PRIMARY_META, "shape": [22, 26]}
    errors = validate(tmp_path, "testgenre", meta)
    assert errors == ["'shape' must be a JSON object"]


def test_shape_range_must_be_two_integers(tmp_path):
    meta = {**VALID_PRIMARY_META,
            "shape": {**VALID_PRIMARY_META["shape"], "chapters": [22]}}
    errors = validate(tmp_path, "testgenre", meta)
    assert errors == ["shape.chapters must be a two-integer range"]


def test_shape_range_rejects_bool_as_integer(tmp_path):
    meta = {**VALID_PRIMARY_META,
            "shape": {**VALID_PRIMARY_META["shape"], "chapters": [True, 26]}}
    errors = validate(tmp_path, "testgenre", meta)
    assert errors == ["shape.chapters must be a two-integer range"]


def test_shape_chapters_range_must_be_ordered(tmp_path):
    meta = {**VALID_PRIMARY_META,
            "shape": {**VALID_PRIMARY_META["shape"], "chapters": [26, 22]}}
    errors = validate(tmp_path, "testgenre", meta)
    assert errors == ["shape.chapters range [26, 22] is not ordered low..high"]


def test_shape_words_range_must_be_ordered(tmp_path):
    meta = {**VALID_PRIMARY_META,
            "shape": {**VALID_PRIMARY_META["shape"], "words": [95000, 80000]}}
    errors = validate(tmp_path, "testgenre", meta)
    assert errors == [
        "shape.words range [95000, 80000] is not ordered low..high"
    ]


# --- artifacts --------------------------------------------------------------

def test_artifacts_must_be_list(tmp_path):
    meta = {**VALID_PRIMARY_META, "artifacts": "canon.md"}
    errors = validate(tmp_path, "testgenre", meta)
    assert errors == ["frontmatter 'artifacts' must be a list"]


def test_artifact_may_not_collide_with_core_file(tmp_path):
    meta = {**VALID_PRIMARY_META, "artifacts": ["canon.md"]}
    errors = validate(tmp_path, "testgenre", meta)
    assert errors == ["artifact 'canon.md' collides with a core project file"]


def test_artifacts_non_string_element_is_reported(tmp_path):
    # A non-string artifact entry (e.g. an author guessing at a richer
    # schema, {"file": "x"} instead of a bare filename string) must be
    # reported rather than silently skipped — mirroring how 'role' and
    # 'conflicts_with' already report non-string elements — and it must
    # not crash the `artifact in CORE_PROJECT_FILES` membership test. A
    # real collision alongside it must still be caught too.
    meta = {**VALID_PRIMARY_META, "artifacts": [{"file": "x"}, "canon.md"]}
    errors = validate(tmp_path, "testgenre", meta)
    assert errors == [
        "frontmatter 'artifacts' must be a list of strings; non-string "
        "element(s): {'file': 'x'}",
        "artifact 'canon.md' collides with a core project file",
    ]


def test_artifacts_null_is_reported(tmp_path):
    # Guards against a regression to `meta.get("artifacts") or []`, which
    # would silently treat an explicit "artifacts": null as an empty list
    # instead of failing loudly the way conflicts_with does.
    meta = {**VALID_PRIMARY_META, "artifacts": None}
    errors = validate(tmp_path, "testgenre", meta)
    assert errors == ["frontmatter 'artifacts' must be a list"]


# --- validate_genre_pack.py CLI ----------------------------------------------

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
