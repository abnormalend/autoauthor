"""Length bands: genre criteria read at the scale the work actually is.

A genre pack's criteria were written for a novel. Applied to five thousand
words they reproduce exactly the defect that justified splitting hybrids
out in the first place — wrong-scale criteria penalize a work for being
correctly what it is.

The check the form spec calls the single highest-value addition lives here:
dropping a dimension at a band shrinks the divisor `pillar_score` is a mean
over, so a band is a different design with a different ceiling, and it has
to be checked as one.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).parent.parent
SCRIPTS = REPO / "plugin/autoauthor/shared/scripts"
GENRES = REPO / "plugin/autoauthor/shared/genres"
FORMS = REPO / "plugin/autoauthor/shared/forms"
sys.path.insert(0, str(SCRIPTS))

import form_pack  # noqa: E402
import gate_solver  # noqa: E402
import genre_pack  # noqa: E402

RESOLVE_CLI = SCRIPTS / "resolve_genre.py"

from test_genre_pack import VALID_PRIMARY_META, write_pack  # noqa: E402

BANDED_BODY = """
## Framing

- genre_noun — "test novel"

## Pillar Dimensions

- alpha_dim [cap 6] — First. If absent, score 6 max.
- beta_dim [cap 6] — Second. If absent, score 6 max.
- gamma_dim [cap 6] — Third. If absent, score 6 max.
- delta_dim [cap 6] — Fourth. If absent, score 6 max.
- epsilon_dim [cap 6] — Fifth. If absent, score 6 max.

## At Compressed Length

- alpha_dim [cap 6] — One rule, not three. If absent, score 6 max.
- beta_dim [cap 6] — Tightened. If absent, score 6 max.
- gamma_dim [cap 6] — Tightened. If absent, score 6 max.
- delta_dim — not scored at this band.
- epsilon_dim — not scored at this band.
"""


def parse(tmp_path, body=BANDED_BODY, meta=None):
    return genre_pack.parse_pack(
        write_pack(tmp_path, "testgenre", meta or VALID_PRIMARY_META, body))


# --- reading a band --------------------------------------------------------

def test_extended_uses_the_packs_own_criteria(tmp_path):
    """A pack with no band section is not length-unaware at novel length —
    its criteria ARE its extended criteria. That default is what let
    fifteen packs stay untouched while this axis was built."""
    pack = parse(tmp_path)
    dimensions, caps, replaced, dropped, source = genre_pack.band_criteria(
        pack, "extended")
    assert len(dimensions) == 5
    assert source is None and replaced == [] and dropped == []
    assert caps == pack["caps"]


def test_compressed_drops_and_rescopes(tmp_path):
    dimensions, caps, replaced, dropped, source = genre_pack.band_criteria(
        parse(tmp_path), "compressed")
    assert dimensions == ["alpha_dim", "beta_dim", "gamma_dim"]
    assert dropped == ["delta_dim", "epsilon_dim"]
    assert replaced == ["alpha_dim", "beta_dim", "gamma_dim"]
    assert source == "compressed"
    assert set(caps) == set(dimensions)


def test_intermediate_falls_back_to_compressed(tmp_path):
    """A pack that has thought about five thousand words has thought about
    most of what forty thousand needs. The reverse is not true, which is
    why the fallback runs in one direction only."""
    _, _, _, dropped, source = genre_pack.band_criteria(
        parse(tmp_path), "intermediate")
    assert source == "compressed"
    assert dropped == ["delta_dim", "epsilon_dim"]


def test_an_intermediate_section_wins_over_compressed(tmp_path):
    body = BANDED_BODY + """
## At Intermediate Length

- alpha_dim [cap 6] — Room for two rules. If absent, score 6 max.
- delta_dim [cap 6] — Back in scope here. If absent, score 6 max.
- epsilon_dim — not scored at this band.
"""
    dimensions, _, replaced, dropped, source = genre_pack.band_criteria(
        parse(tmp_path, body), "intermediate")
    assert source == "intermediate"
    assert dropped == ["epsilon_dim"]
    assert "delta_dim" in dimensions
    assert replaced == ["alpha_dim", "delta_dim"]


def test_a_dimension_the_band_says_nothing_about_keeps_its_default(tmp_path):
    body = BANDED_BODY.replace(
        "- beta_dim [cap 6] — Tightened. If absent, score 6 max.\n", "")
    dimensions, caps, replaced, _, _ = genre_pack.band_criteria(
        parse(tmp_path, body), "compressed")
    assert "beta_dim" in dimensions
    assert "beta_dim" not in replaced
    assert caps["beta_dim"] == 6


# --- band arithmetic -------------------------------------------------------

def validate(tmp_path, body, meta=None):
    return genre_pack.validate_pack(parse(tmp_path, body, meta))


def test_a_band_may_only_rescope_dimensions_the_pack_declares(tmp_path):
    body = BANDED_BODY.replace("- delta_dim — not scored at this band.",
                               "- omega_dim — not scored at this band.")
    errors = validate(tmp_path, body)
    assert any("does not declare" in e for e in errors)


def test_an_empty_band_section_is_an_error_not_a_no_op(tmp_path):
    """Silently ignoring it leaves the pack looking length-aware while
    scoring a short work against criteria written for a long one."""
    body = BANDED_BODY.split("## At Compressed Length")[0] + (
        "## At Compressed Length\n\nShorter, obviously.\n")
    errors = validate(tmp_path, body)
    assert any("names no dimension" in e for e in errors)


def test_a_band_that_drops_everything_is_an_error(tmp_path):
    body = BANDED_BODY.split("## At Compressed Length")[0] + (
        "## At Compressed Length\n\n"
        + "".join(f"- {d}_dim — not scored at this band.\n"
                  for d in ("alpha", "beta", "gamma", "delta", "epsilon")))
    errors = validate(tmp_path, body)
    assert any("drops every dimension" in e for e in errors)


def test_a_band_cap_must_agree_with_the_band_criteria(tmp_path):
    body = BANDED_BODY.replace(
        "- alpha_dim [cap 6] — One rule, not three. If absent, score 6 max.",
        "- alpha_dim [cap 6] — One rule, not three. If absent, score 4 max.")
    errors = validate(tmp_path, body)
    assert any("can force it to 4" in e and "At Compressed Length" in e
               for e in errors)


TIGHT_BAND = (
    "## At Compressed Length\n\n"
    "- alpha_dim [cap 6] — Tight. If absent, score 6 max.\n"
    "- beta_dim [cap 6] — Tight. If absent, score 6 max.\n"
    "- gamma_dim — not scored at this band.\n"
    "- delta_dim — not scored at this band.\n"
    "- epsilon_dim — not scored at this band.\n")


def test_dropping_to_two_capped_dimensions_puts_the_short_gate_out_of_reach():
    """Two dimensions both capped at 6: with two caps firing there is no
    third dimension to make up the difference, so the design tops out at
    5.9 — under `short-story`'s 6.0 pillar gate.

    This is the arithmetic the band check exists for. Dropping a dimension
    shrinks the divisor the caps were calibrated against, so a band is a
    different design with a different ceiling.
    """
    assert gate_solver.max_gate(5, [6, 6]) == pytest.approx(7.1)
    assert gate_solver.max_gate(2, [6, 6]) == pytest.approx(5.9)


def test_a_band_that_cannot_reach_its_forms_gate_is_refused(tmp_path):
    """Neither pack can see this alone: the ceiling is the genre's, at a
    band, and the gate is the form's."""
    (tmp_path / "genres").mkdir()
    write_pack(tmp_path / "genres", "testgenre", VALID_PRIMARY_META,
               BANDED_BODY.split("## At Compressed Length")[0] + TIGHT_BAND)
    result = resolve(tmp_path, "testgenre", "short-story")
    assert result.returncode == 1
    assert "tops out at 5.9" in result.stderr
    assert "2 dimension(s) at compressed length" in result.stderr


def test_a_modifier_may_not_declare_a_band_section(tmp_path):
    meta = {k: v for k, v in VALID_PRIMARY_META.items()
            if k not in ("shape", "pillar_label", "weights")}
    meta["role"] = ["modifier"]
    body = ('\n## Framing\n\n- genre_noun — "x"\n\n'
            "## At Compressed Length\n\n- alpha_dim — Tighter.\n")
    errors = genre_pack.validate_pack(parse(tmp_path, body, meta))
    assert any("modifier pack must not have" in e for e in errors)


# --- the shipped matrix ----------------------------------------------------

def shipped(directory):
    return sorted(p for p in directory.glob("*.md") if p.stem != "TEMPLATE")


def resolve(tmp_path, genre, form):
    (tmp_path / "state.json").write_text(
        json.dumps({"genre": genre, "form": form}), encoding="utf-8")
    return subprocess.run([sys.executable, str(RESOLVE_CLI)], cwd=tmp_path,
                          capture_output=True, text=True)


@pytest.mark.parametrize("genre", [p.stem for p in shipped(GENRES)])
@pytest.mark.parametrize("form", [p.stem for p in shipped(FORMS)])
def test_every_genre_by_every_form_either_resolves_or_says_why(
        tmp_path, genre, form):
    """The full matrix. Every pair must be usable or refused for a stated
    reason — never silently misjudged, which is what applying novel
    criteria to a short story would be.

    A modifier-only pack cannot be a primary at all; that refusal is about
    roles rather than length and is checked elsewhere.
    """
    result = resolve(tmp_path, genre, form)
    if result.returncode != 0:
        assert ("has no '## At" in result.stderr
                or "does not declare role 'primary'" in result.stderr), (
            f"{genre} x {form} failed for an unexplained reason:\n"
            f"{result.stderr}")
        return

    resolved = json.loads(result.stdout)
    pillar, shape = resolved["pillar"], resolved["shape"]
    gate = resolved["form"]["gate"]["pillar"]

    ceiling = gate_solver.max_gate(len(pillar["dimensions"]),
                                   sorted(pillar["caps"].values()))
    assert ceiling is not None and ceiling >= gate, (
        f"{genre} at {form} length: {len(pillar['dimensions'])} dimensions "
        f"top out at {ceiling}, below the {gate} gate")
    assert 3 <= len(pillar["dimensions"]) <= 6
    assert shape["chapters"] >= 1
    lo, hi = shape["words"]
    assert lo <= shape["target_words"] <= hi or shape["words_source"] == "genre"


def test_a_short_form_is_refused_for_a_pack_with_no_compressed_section(tmp_path):
    """Refused rather than degraded. Degrading gracefully here means
    scoring a five-thousand-word story on whether its world has three
    societal implications, which is the exact defect the axis exists to
    prevent."""
    result = resolve(tmp_path, "romantasy", "short-story")
    assert result.returncode == 1
    assert "has no '## At Compressed Length' section" in result.stderr
    assert "penalize a shorter work" in result.stderr


def test_at_least_four_packs_support_the_compressed_forms():
    supported = [p.stem for p in shipped(GENRES)
                 if genre_pack.section_body(
                     genre_pack.parse_pack(p)["body"],
                     "At Compressed Length") is not None]
    assert len(supported) >= 4, supported


# --- shape reconciliation --------------------------------------------------

def test_chapters_are_derived_and_no_pack_declares_them():
    for path in shipped(GENRES):
        shape = genre_pack.parse_pack(path)["meta"].get("shape") or {}
        assert "chapters" not in shape, f"{path.stem} declares a chapter count"


def test_a_genre_narrows_the_length_within_the_form(tmp_path):
    """The reason `shape.words` did not simply move onto the form: one pack
    runs half again as long as another at the same form, and collapsing
    them onto one default would lose a real genre fact."""
    long_book = json.loads(resolve(tmp_path, "romantasy", "novel").stdout)
    short_book = json.loads(resolve(tmp_path, "erotica", "novel").stdout)
    assert long_book["shape"]["target_words"] > short_book["shape"]["target_words"]
    assert long_book["shape"]["words_source"] == "genre"


def test_the_form_supplies_the_length_where_the_genre_is_silent(tmp_path):
    """No pack declares a compressed range, so every one of them takes the
    form's — which is the graceful half of this design."""
    resolved = json.loads(resolve(tmp_path, "fantasy", "short-story").stdout)
    assert resolved["shape"]["words_source"] == "form"
    assert resolved["shape"]["target_words"] == 5000


def test_a_compressed_form_overrides_chapter_granularity(tmp_path):
    """The genre owns chapter size at novel length. At five thousand words
    the unit is a scene, and dividing by a novel's chapter size yields one
    chapter and a remainder."""
    short = json.loads(resolve(tmp_path, "fantasy", "short-story").stdout)
    novel = json.loads(resolve(tmp_path, "fantasy", "novel").stdout)
    assert short["shape"]["chapter_words_source"] == "form"
    assert novel["shape"]["chapter_words_source"] == "genre"
    assert short["shape"]["chapters"] >= 3


def test_effective_shape_rounds_the_target_to_a_round_number():
    shape = form_pack.effective_shape(
        {"words": [40000, 120000], "target_words": 85000},
        {"words": {"extended": [80000, 95000]}, "chapter_words": 3200},
        "extended")
    assert shape["target_words"] == 88000
    assert shape["chapters"] == 28
