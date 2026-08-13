"""The base dimensions, lifted out of the foundation rubric.

They were a fixed list written into `rubrics/foundation.md` for the same
reason the pillar dimensions once were: nobody had needed them to vary.
A form needs them to.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).parent.parent
SCRIPTS = REPO / "plugin/autoauthor/shared/scripts"
RUBRICS = REPO / "plugin/autoauthor/shared/rubrics"
sys.path.insert(0, str(SCRIPTS))

import base_dimensions  # noqa: E402
import genre_pack  # noqa: E402

RESOLVE_CLI = SCRIPTS / "resolve_genre.py"


@pytest.fixture(scope="module")
def parsed():
    return base_dimensions.parse_base_dimensions()


# --- the shipped file ------------------------------------------------------

def test_the_shipped_file_parses_and_validates(parsed):
    assert base_dimensions.validate_base_dimensions(parsed) == []


def test_the_eight_survived_the_move(parsed):
    """The lift must not have quietly lost one. These are exactly the
    dimensions foundation.md scored before base-dimensions.md existed."""
    assert parsed["character"]["dimensions"] == [
        "character_depth", "character_distinctiveness", "character_secrets"]
    assert parsed["structure"]["dimensions"] == [
        "outline_completeness", "foreshadowing_balance"]
    assert parsed["craft"]["dimensions"] == [
        "internal_consistency", "voice_clarity", "canon_coverage"]


def test_reserved_dimensions_matches_the_file(parsed):
    """genre_pack.RESERVED_DIMENSIONS is a mirror. This is the only thing
    keeping it honest — and a stale mirror would let a genre pack declare
    a pillar dimension that collides with a base one, which is exactly the
    double-counting the reservation exists to prevent."""
    assert base_dimensions.all_keys(parsed) == genre_pack.RESERVED_DIMENSIONS


def test_the_caps_that_came_across_are_declared(parsed):
    """Both were already caps in prose — one stated plainly, one phrased
    inversely as 'score 5+ only if'. Declaring them is what makes them
    visible to tooling and binding on a judge."""
    assert parsed["craft"]["caps"]["internal_consistency"] == 4
    assert parsed["structure"]["caps"]["outline_completeness"] == 4


def test_outline_completeness_no_longer_demands_act_structure(parsed):
    """Five shipped packs run on something other than acts. The old
    criteria capped a correctly built romance outline at 4 for using the
    structure its own pack prescribes."""
    section = genre_pack.section_body(
        (RUBRICS / "base-dimensions.md").read_text(encoding="utf-8"),
        "Structure")
    assert "Romancing the Beat" in section
    assert "Score 5+ only if act structure exists" not in section


def test_the_foundation_rubric_no_longer_carries_the_list():
    """If the criteria are in two places they will disagree, and the copy
    the judge reads first wins silently."""
    rubric = (RUBRICS / "foundation.md").read_text(encoding="utf-8")
    assert "base_dimensions.scored" in rubric
    for key in ("character_depth", "canon_coverage", "foreshadowing_balance"):
        assert f"- {key}:" not in rubric, (
            f"{key} still has criteria in foundation.md as well as in "
            "base-dimensions.md")


# --- structure of the file itself ------------------------------------------

def write_base(tmp_path, body):
    path = tmp_path / "base-dimensions.md"
    path.write_text(body, encoding="utf-8")
    return path


GOOD_BODY = """# Base Dimensions

## Character

- alpha_dim — Something.

## Structure

- beta_dim — Something else.

## Craft

- gamma_dim [cap 6] — If absent, score 6 max.
"""


def test_a_missing_category_is_an_error(tmp_path):
    body = GOOD_BODY.replace("## Craft", "## Polish")
    with pytest.raises(genre_pack.PackError, match="no '## Craft' section"):
        base_dimensions.parse_base_dimensions(write_base(tmp_path, body))


def test_an_empty_category_is_an_error(tmp_path):
    """Silently empty would drop a third of the rubric with nothing
    failing, which is this project's signature failure mode."""
    body = GOOD_BODY.replace("- beta_dim — Something else.", "")
    with pytest.raises(genre_pack.PackError, match="declares no dimensions"):
        base_dimensions.parse_base_dimensions(write_base(tmp_path, body))


def test_a_wrong_dash_is_an_error_not_a_silent_omission(tmp_path):
    body = GOOD_BODY.replace("- alpha_dim —", "- alpha_dim -")
    with pytest.raises(genre_pack.PackError, match="em dash"):
        base_dimensions.parse_base_dimensions(write_base(tmp_path, body))


def test_a_key_in_two_categories_is_an_error(tmp_path):
    body = GOOD_BODY.replace("- beta_dim — Something else.",
                             "- alpha_dim — Something else.")
    parsed = base_dimensions.parse_base_dimensions(write_base(tmp_path, body))
    errors = base_dimensions.validate_base_dimensions(parsed)
    assert any("appear in more than one category" in e for e in errors)


def test_a_cap_that_disagrees_with_the_criteria_is_an_error(tmp_path):
    body = GOOD_BODY.replace("score 6 max", "score 4 max")
    parsed = base_dimensions.parse_base_dimensions(write_base(tmp_path, body))
    errors = base_dimensions.validate_base_dimensions(parsed)
    assert any("can force it to 4" in e for e in errors)


# --- what a form does with them --------------------------------------------

def test_a_form_that_drops_nothing_gets_everything(parsed):
    scored, dropped = base_dimensions.resolve_for_form(
        parsed, {"base_dimensions": {"drop": [], "add": {}}})
    assert dropped == []
    assert scored["craft"] == parsed["craft"]["dimensions"]


def test_a_form_drops_what_its_length_cannot_earn(parsed):
    scored, dropped = base_dimensions.resolve_for_form(parsed, {
        "base_dimensions": {"drop": ["foreshadowing_balance",
                                     "canon_coverage"], "add": {}}})
    assert dropped == ["canon_coverage", "foreshadowing_balance"]
    assert scored["structure"] == ["outline_completeness"]
    assert "canon_coverage" not in scored["craft"]


def test_an_added_dimension_lands_in_its_declared_category(parsed):
    scored, _ = base_dimensions.resolve_for_form(parsed, {
        "base_dimensions": {"drop": [], "add": {"structure": ["compression"]}}})
    assert scored["structure"][-1] == "compression"
    assert "compression" not in scored["craft"]


def test_a_form_with_no_base_dimensions_block_changes_nothing(parsed):
    scored, dropped = base_dimensions.resolve_for_form(parsed, {})
    assert dropped == []
    assert scored == {c: parsed[c]["dimensions"]
                      for c in base_dimensions.CATEGORIES}


def test_emptying_a_category_is_detectable(parsed):
    scored, _ = base_dimensions.resolve_for_form(parsed, {
        "base_dimensions": {"drop": ["outline_completeness",
                                     "foreshadowing_balance"], "add": {}}})
    assert base_dimensions.empty_categories(scored) == ["structure"]


# --- resolution ------------------------------------------------------------

def resolve(tmp_path, state):
    (tmp_path / "state.json").write_text(json.dumps(state), encoding="utf-8")
    result = subprocess.run([sys.executable, str(RESOLVE_CLI)], cwd=tmp_path,
                            capture_output=True, text=True)
    return result


def test_the_resolver_reports_the_scored_set(tmp_path):
    result = resolve(tmp_path, {"genre": "fantasy"})
    assert result.returncode == 0, result.stderr
    base = json.loads(result.stdout)["base_dimensions"]
    assert base["dropped"] == []
    assert base["scored"]["character"] == [
        "character_depth", "character_distinctiveness", "character_secrets"]
    assert Path(base["path"]).name == "base-dimensions.md"


def _form(tmp_path, criteria_for=None, **overrides):
    """Write a project-local form. By default it writes a criteria bullet
    for every key it adds, since a form missing those is its own separate
    error; pass criteria_for=[] to exercise that one deliberately."""
    meta = {"name": "testform", "label": "Test", "band": "compressed",
            "words": [1000, 200000], "target_words": 5000,
            "gate": {"overall": 7.0, "pillar": 6.5},
            "layers": ["voice", "outline"],
            "base_dimensions": {"drop": [], "add": {}}}
    meta.update(overrides)
    keys = (base_dimensions.added_keys(meta) if criteria_for is None
            else criteria_for)
    (tmp_path / "forms").mkdir(exist_ok=True)
    body = ('\n## Framing\n\n- form_noun — "test"\n\n## Form Contract\n\n'
            "- It is complete.\n\n## Base Dimensions\n\n"
            + "".join(f"- {k} — Criteria for {k}.\n" for k in keys))
    (tmp_path / "forms" / "testform.md").write_text(
        "---\n" + json.dumps(meta) + "\n---\n" + body, encoding="utf-8")
    return meta


def test_a_form_that_empties_a_weighted_category_is_refused(tmp_path):
    """The primary's weights still give that category a share of
    overall_score, and the mean of no dimensions is undefined."""
    _form(tmp_path, base_dimensions={
        "drop": ["outline_completeness", "foreshadowing_balance"], "add": {}})
    result = resolve(tmp_path, {"genre": "fantasy", "form": "testform"})
    assert result.returncode == 1
    assert "drops every dimension in structure" in result.stderr


def test_an_added_dimension_may_not_collide_with_a_pillar_dimension(tmp_path):
    """Invisible to either validator alone: the key is in the form and the
    collision is in the genre."""
    _form(tmp_path, base_dimensions={"drop": [], "add": {"craft": ["magic_system"]}})
    result = resolve(tmp_path, {"genre": "fantasy", "form": "testform"})
    assert result.returncode == 1
    assert "already declares as pillar dimensions" in result.stderr
    # ...and the same form is fine beside a genre that has no such
    # dimension, which is what makes this a cross-pack check rather than a
    # blanket ban.
    result = resolve(tmp_path, {"genre": "mystery", "form": "testform"})
    assert result.returncode == 0, result.stderr


def test_a_form_dropping_dimensions_shows_up_in_the_resolver(tmp_path):
    _form(tmp_path, base_dimensions={
        "drop": ["foreshadowing_balance", "canon_coverage"], "add": {}})
    result = resolve(tmp_path, {"genre": "mystery", "form": "testform"})
    assert result.returncode == 0, result.stderr
    base = json.loads(result.stdout)["base_dimensions"]
    assert base["dropped"] == ["canon_coverage", "foreshadowing_balance"]
    assert base["scored"]["structure"] == ["outline_completeness"]


def test_an_added_dimension_needs_criteria_a_judge_can_read(tmp_path):
    """A key with no bullet is a dimension nobody can score."""
    _form(tmp_path, criteria_for=[],
          base_dimensions={"drop": [], "add": {"craft": ["texture"]}})
    result = resolve(tmp_path, {"genre": "mystery", "form": "testform"})
    assert result.returncode == 1
    assert "with no criteria" in result.stderr
