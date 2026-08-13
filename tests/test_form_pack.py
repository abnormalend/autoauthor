"""Form packs: the scale axis.

Phase 1 of the form work ships exactly one form, `novel`, carrying the
values the pipeline already used. So the most important test here is the
boring one — that nothing moved.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).parent.parent
SCRIPTS = REPO / "plugin/autoauthor/shared/scripts"
FORMS = REPO / "plugin/autoauthor/shared/forms"
sys.path.insert(0, str(SCRIPTS))

import form_pack  # noqa: E402
import genre_pack  # noqa: E402

VALIDATE_CLI = SCRIPTS / "validate_form_pack.py"
RESOLVE_CLI = SCRIPTS / "resolve_genre.py"

VALID_FORM_META = {
    "name": "testform",
    "label": "Test Form",
    "band": "extended",
    "words": [40000, 120000],
    "target_words": 85000,
    "gate": {"overall": 7.5, "pillar": 7.0},
    "layers": ["voice", "outline"],
    "base_dimensions": {"drop": [], "add": {}},
}

VALID_FORM_BODY = """
## Framing

- form_noun — "test work"

## Form Contract

- The work is complete in itself.
"""


def write_form(tmp_path, name, meta, body=VALID_FORM_BODY):
    path = tmp_path / f"{name}.md"
    path.write_text("---\n" + json.dumps(meta, indent=2) + "\n---\n" + body,
                    encoding="utf-8")
    return path


def validate(tmp_path, name, meta, body=VALID_FORM_BODY):
    return form_pack.validate_form(
        form_pack.parse_form(write_form(tmp_path, name, meta, body)))


# --- the shipped form ------------------------------------------------------

def test_the_novel_form_is_valid():
    form = form_pack.parse_form(FORMS / "novel.md")
    assert form_pack.validate_form(form) == []


def test_the_novel_form_carries_the_values_the_pipeline_already_used():
    """Phase 1's whole acceptance criterion. If any of these move, the
    form axis has changed behaviour while claiming not to."""
    meta = form_pack.parse_form(FORMS / "novel.md")["meta"]
    assert meta["gate"] == {"overall": 7.5, "pillar": 7.0}
    assert meta["band"] == "extended"
    assert meta["layers"] == ["voice", "world", "characters", "mystery",
                              "outline", "foreshadowing", "canon"]
    assert meta["base_dimensions"] == {"drop": [], "add": {}}


def test_every_layer_a_form_can_ask_for_is_defined_somewhere():
    """KNOWN_LAYERS is mirrored from layer-guides.md, which is prose. If a
    layer is renamed there and not here, a form can name a layer nothing
    knows how to build."""
    guides = (REPO / "plugin/autoauthor/skills/foundation/references"
              / "layer-guides.md").read_text(encoding="utf-8")
    for layer, heading in form_pack.KNOWN_LAYERS.items():
        assert f"## {heading}" in guides, (
            f"layer {layer!r} claims to be defined by '## {heading}' in "
            "layer-guides.md, which has no such section")


def test_cli_validates_every_shipped_form():
    forms = sorted(FORMS.glob("*.md"))
    assert forms, "no form packs found"
    result = subprocess.run(
        [sys.executable, str(VALIDATE_CLI), *[str(f) for f in forms]],
        capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr


# --- schema ---------------------------------------------------------------

def test_band_must_be_one_of_the_three(tmp_path):
    meta = {**VALID_FORM_META, "band": "medium"}
    errors = validate(tmp_path, "testform", meta)
    assert any("'band' is 'medium'" in e for e in errors)


def test_target_words_must_sit_inside_the_form_own_range(tmp_path):
    meta = {**VALID_FORM_META, "target_words": 200000}
    errors = validate(tmp_path, "testform", meta)
    assert any("outside this form's own 'words' range" in e for e in errors)


def test_words_range_must_be_ordered(tmp_path):
    meta = {**VALID_FORM_META, "words": [120000, 40000], "target_words": 80000}
    errors = validate(tmp_path, "testform", meta)
    assert any("not ordered low..high" in e for e in errors)


@pytest.mark.parametrize("gate", [
    {"overall": 7.5},
    {"overall": 7.5, "pillar": 11},
    {"overall": 7.5, "pillar": "high"},
    "7.5",
])
def test_a_broken_gate_is_rejected(tmp_path, gate):
    errors = validate(tmp_path, "testform", {**VALID_FORM_META, "gate": gate})
    assert errors


def test_layers_must_be_known(tmp_path):
    meta = {**VALID_FORM_META, "layers": ["voice", "storyboard"]}
    errors = validate(tmp_path, "testform", meta)
    assert any("unknown layer(s) storyboard" in e for e in errors)


def test_dropped_base_dimensions_must_actually_be_base_dimensions(tmp_path):
    meta = {**VALID_FORM_META,
            "base_dimensions": {"drop": ["magic_system"], "add": {}}}
    errors = validate(tmp_path, "testform", meta)
    assert any("not base dimensions" in e for e in errors)
    # ...and a real one is fine. This is the field's entire purpose: a
    # short story keeps no foreshadowing ledger, so scoring one penalizes
    # the story for being correctly what it is.
    meta = {**VALID_FORM_META,
            "base_dimensions": {"drop": ["foreshadowing_balance"], "add": {}}}
    assert validate(tmp_path, "testform", meta) == []


def test_an_added_base_dimension_may_not_shadow_an_existing_one(tmp_path):
    meta = {**VALID_FORM_META,
            "base_dimensions": {"drop": [], "add": {"craft": ["voice_clarity"]}}}
    errors = validate(tmp_path, "testform", meta)
    assert any("already exist as base dimensions" in e for e in errors)


def test_a_form_may_not_declare_pillar_dimensions(tmp_path):
    """A form changes how a genre's dimensions are READ. It does not have
    dimensions of its own — that is the line between the two axes."""
    body = VALID_FORM_BODY + "\n## Pillar Dimensions\n\n- alpha_dim — no.\n"
    errors = validate(tmp_path, "testform", VALID_FORM_META, body)
    assert any("must not declare pillar dimensions" in e for e in errors)


def test_a_form_may_not_declare_a_role(tmp_path):
    meta = {**VALID_FORM_META, "role": ["primary"]}
    errors = validate(tmp_path, "testform", meta)
    assert any("must not declare 'role'" in e for e in errors)


def test_a_form_needs_framing_and_a_contract(tmp_path):
    errors = validate(tmp_path, "testform", VALID_FORM_META, "## Framing\n")
    assert any("'## Form Contract'" in e for e in errors)


# --- form and genre have to agree -----------------------------------------

def test_overlap_not_containment():
    """A genre that runs past the form's ceiling is straddling a boundary,
    not contradicting the form. Containment would reject a real pack."""
    assert form_pack.ranges_overlap([110000, 140000], [40000, 120000])
    assert form_pack.ranges_overlap([40000, 120000], [110000, 140000])
    assert not form_pack.ranges_overlap([1000, 7500], [40000, 120000])


def test_a_genre_whose_length_cannot_fit_the_form_is_refused(tmp_path):
    """The check that makes the form axis mean something: no length
    satisfies both, so the pair is unusable and says so."""
    form = {**VALID_FORM_META, "name": "shortform",
            "words": [1000, 7500], "target_words": 5000}
    (tmp_path / "forms").mkdir()
    write_form(tmp_path / "forms", "shortform", form)
    (tmp_path / "state.json").write_text(
        json.dumps({"genre": "fantasy", "form": "shortform"}), encoding="utf-8")

    result = subprocess.run([sys.executable, str(RESOLVE_CLI)],
                            cwd=tmp_path, capture_output=True, text=True)
    assert result.returncode == 1
    assert "no length that satisfies both" in result.stderr


def test_a_form_may_not_gate_above_what_the_genre_can_reach(tmp_path):
    """Neither pack can catch this alone — the ceiling is the genre's and
    the gate is the form's, so it is only visible once both are loaded."""
    form = {**VALID_FORM_META, "name": "steepform",
            "gate": {"overall": 7.5, "pillar": 9.0}}
    (tmp_path / "forms").mkdir()
    write_form(tmp_path / "forms", "steepform", form)
    (tmp_path / "state.json").write_text(
        json.dumps({"genre": "fantasy", "form": "steepform"}), encoding="utf-8")

    result = subprocess.run([sys.executable, str(RESOLVE_CLI)],
                            cwd=tmp_path, capture_output=True, text=True)
    assert result.returncode == 1
    assert "tops out at 7.1" in result.stderr


# --- resolution ------------------------------------------------------------

def resolve(tmp_path, state):
    (tmp_path / "state.json").write_text(json.dumps(state), encoding="utf-8")
    result = subprocess.run([sys.executable, str(RESOLVE_CLI)], cwd=tmp_path,
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def test_a_project_with_no_form_resolves_to_novel(tmp_path):
    """Same defaulting rule as `genre`, and it is what keeps every project
    created before this axis existed working untouched."""
    assert resolve(tmp_path, {"genre": "fantasy"})["form"]["name"] == "novel"


def test_the_form_block_carries_what_the_skills_need(tmp_path):
    form = resolve(tmp_path, {"genre": "mystery"})["form"]
    assert set(form) == {"name", "label", "band", "words", "target_words",
                         "gate", "layers", "path"}
    assert form["band"] == "extended"


def test_the_genre_still_owns_shape(tmp_path):
    """Form owns how long the whole work is; genre owns chapter
    granularity. Phase 1 does not migrate `shape.words` off the packs —
    that lands with the compressed forms, where it starts to matter."""
    resolved = resolve(tmp_path, {"genre": "thriller"})
    assert resolved["shape"]["chapter_words"] == 1900
    assert resolved["shape"]["words"] == [85000, 100000]


def test_a_project_form_wins_over_the_shipped_one(tmp_path):
    """Same precedent as genre packs: the project copy wins, because
    specificity is the point."""
    (tmp_path / "forms").mkdir()
    write_form(tmp_path / "forms", "novel",
               {**VALID_FORM_META, "name": "novel", "label": "House Novel"})
    resolved = resolve(tmp_path, {"genre": "fantasy", "form": "novel"})
    assert resolved["form"]["label"] == "House Novel"


def test_an_unknown_form_is_refused_with_the_known_ones(tmp_path):
    (tmp_path / "state.json").write_text(
        json.dumps({"genre": "fantasy", "form": "haiku"}), encoding="utf-8")
    result = subprocess.run([sys.executable, str(RESOLVE_CLI)], cwd=tmp_path,
                            capture_output=True, text=True)
    assert result.returncode == 1
    assert "unknown form 'haiku'" in result.stderr
    assert "novel" in result.stderr


def test_a_form_name_cannot_escape_the_forms_directory(tmp_path):
    (tmp_path / "state.json").write_text(
        json.dumps({"genre": "fantasy", "form": "../genres/fantasy"}),
        encoding="utf-8")
    result = subprocess.run([sys.executable, str(RESOLVE_CLI)], cwd=tmp_path,
                            capture_output=True, text=True)
    assert result.returncode == 1
    assert "invalid form name" in result.stderr


def test_every_shipped_genre_overlaps_the_novel_form(tmp_path):
    """Every pack in the set is usable at novel length today. When the
    compressed forms land, this is the test that will fail for the packs
    that need a band section."""
    novel = form_pack.parse_form(FORMS / "novel.md")["meta"]
    genres = REPO / "plugin/autoauthor/shared/genres"
    checked = 0
    for path in sorted(genres.glob("*.md")):
        if path.stem == "TEMPLATE":
            continue
        shape = genre_pack.parse_pack(path)["meta"].get("shape") or {}
        if not shape.get("words"):
            continue
        checked += 1
        assert form_pack.ranges_overlap(shape["words"], novel["words"]), (
            f"{path.stem} runs {shape['words']} and cannot be a novel")
    assert checked >= 10
