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
    assert out["label"] == "Local Fantasy"
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
    assert out["label"] == "Testprimary"
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
