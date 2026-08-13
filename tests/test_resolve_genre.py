import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).parent.parent.resolve()
SCRIPT = REPO / "plugin/autoauthor/shared/scripts/resolve_genre.py"
PLUGIN_GENRES = REPO / "plugin/autoauthor/shared/genres"


def run(project, *args):
    return subprocess.run([sys.executable, str(SCRIPT), *args],
                          capture_output=True, text=True, cwd=project)


def write_state(project, **fields):
    state = {"phase": "foundation", "iteration": 0, "foundation_score": 0.0,
             "pillar_score": 0.0, "chapters_drafted": 0, "chapters_total": 0,
             "work_score": 0.0, "revision_cycle": 0, "review_round": 0,
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
        "shape": {"words": {"extended": [80000, 95000]},
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


SECONDARY_META = {
    "name": "testsecond", "label": "Test Second",
    "role": ["primary", "secondary"], "pillar_label": "Second Pillar",
    "weights": {"pillar": 20, "character": 40, "structure": 25, "craft": 15},
    # Declares "primary", so it must carry a usable `shape` even though these
    # tests only ever load it in the secondary slot.
    "shape": {"words": {"extended": [70000, 85000]},
              "chapter_words": 3000, "pov_default": "first person present"},
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


def test_display_label_drops_a_label_that_says_nothing_new(tmp_path):
    """A hybrid pack's label legitimately contains its parent's.

    'paranormal-romance' primary with a 'romance' secondary must not render
    "Paranormal Romance Romance" on the export title page.
    """
    write_state(tmp_path, genre="testhybrid", genre_secondary="testsecond")
    write_project_pack(tmp_path, "testhybrid",
                       primary_meta("testhybrid", label="Test Second Hybrid"),
                       PRIMARY_BODY)
    write_project_pack(tmp_path, "testsecond", SECONDARY_META, PRIMARY_BODY)
    out = json.loads(run(tmp_path).stdout)
    assert out["label_parts"] == ["Test Second Hybrid"]
    assert out["display_label"] == "Test Second Hybrid"
    # primary_label is the pack's own label and is never deduped.
    assert out["primary_label"] == "Test Second Hybrid"


def test_display_label_keeps_a_label_that_only_shares_some_words(tmp_path):
    """The drop is all-or-nothing: a partial overlap must survive.

    Guards against a future 'simplification' to substring or any-word
    matching, which would silently eat 'Dark Romance' after 'Romance'.
    """
    write_state(tmp_path, genre="testprimary", genre_secondary="testsecond")
    write_project_pack(tmp_path, "testprimary",
                       primary_meta("testprimary", label="Test Overlap"),
                       PRIMARY_BODY)
    write_project_pack(tmp_path, "testsecond", SECONDARY_META, PRIMARY_BODY)
    out = json.loads(run(tmp_path).stdout)
    assert out["display_label"] == "Test Overlap Test Second"


def test_display_label_is_always_the_join_of_label_parts(tmp_path):
    """The documented invariant between the two keys, pinned.

    Six skills parse this output; if dedupe is applied to one and not the
    other they disagree about what the book is called.
    """
    setup_stack(tmp_path)
    out = json.loads(run(tmp_path).stdout)
    assert out["display_label"] == " ".join(out["label_parts"])


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


def _register_stack(tmp_path, **levels_by_pack):
    """Primary plus one modifier per named pack, each with its own levels."""
    write_state(tmp_path, genre="testprimary",
                genre_modifiers=list(levels_by_pack))
    write_project_pack(tmp_path, "testprimary", primary_meta("testprimary"),
                       PRIMARY_BODY)
    for name, register in levels_by_pack.items():
        write_project_pack(
            tmp_path, name,
            {"name": name, "label": name.title(), "role": ["modifier"],
             "content_register": register, "conflicts_with": []},
            MODIFIER_BODY)


def test_content_register_clamps_to_the_most_restrictive_level(tmp_path):
    # Two packs setting the same axis differently is the NORMAL case — a ya
    # modifier over a romance primary — not an authoring error. Because the
    # scales are ordered, it resolves to the more restrictive level rather
    # than to whichever pack loaded last.
    _register_stack(tmp_path,
                    steamy={"heat": "explicit"},
                    cozy={"heat": "closed-door"})
    result = run(tmp_path)
    assert result.returncode == 0, result.stdout + result.stderr
    out = json.loads(result.stdout)
    assert out["content_register"]["heat"] == "closed-door"
    assert out["content_register_sources"]["heat"] == "cozy"


def test_clamping_is_order_independent(tmp_path):
    """The restrictive level wins regardless of which pack loads first."""
    _register_stack(tmp_path,
                    cozy={"heat": "closed-door"},
                    steamy={"heat": "explicit"})
    out = json.loads(run(tmp_path).stdout)
    assert out["content_register"]["heat"] == "closed-door"


def test_agreeing_packs_merge_without_a_source_surprise(tmp_path):
    _register_stack(tmp_path,
                    alpha={"heat": "warm"},
                    beta={"heat": "warm"})
    out = json.loads(run(tmp_path).stdout)
    assert out["content_register"]["heat"] == "warm"
    assert out["content_register_sources"]["heat"] == "alpha"


def test_different_axes_merge_independently(tmp_path):
    _register_stack(tmp_path,
                    alpha={"heat": "steamy"},
                    beta={"violence": "off-page"})
    out = json.loads(run(tmp_path).stdout)
    assert out["content_register"] == {"heat": "steamy",
                                       "violence": "off-page"}
    assert out["content_register_sources"] == {"heat": "alpha",
                                               "violence": "beta"}


def test_unknown_axis_is_rejected_at_resolve(tmp_path):
    _register_stack(tmp_path, alpha={"gore": "lots"})
    result = run(tmp_path)
    assert result.returncode == 1
    assert "unknown content_register axis 'gore'" in result.stderr


def test_unknown_level_is_rejected_at_resolve(tmp_path):
    """This is the 'fade to black' case the closed vocabulary exists for."""
    _register_stack(tmp_path, alpha={"heat": "fade to black"})
    result = run(tmp_path)
    assert result.returncode == 1
    assert "content_register.heat is 'fade to black'" in result.stderr
    assert "closed-door" in result.stderr  # the message names the real levels


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
