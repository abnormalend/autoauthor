"""The structure axis: how many works there are, and how they relate.

Not a pack, and the reason is the line the whole form axis kept insisting
on. Scale changes which dimensions apply, so it is a pack. Structure
changes the state schema and the phase graph, and no pack can do either.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).parent.parent
SCRIPTS = REPO / "plugin/autoauthor/shared/scripts"
sys.path.insert(0, str(SCRIPTS))

import structure  # noqa: E402

RESOLVE_CLI = SCRIPTS / "resolve_genre.py"
CONVERGENCE_CLI = SCRIPTS / "convergence.py"


def make_container(tmp_path, works=("01-first", "02-second"), kind="collection",
                   **state):
    container = tmp_path / kind
    (container / "bible").mkdir(parents=True)
    for name in structure.REQUIRED_BIBLE[kind]:
        (container / "bible" / name).write_text("placeholder\n",
                                                encoding="utf-8")
    for slug in works:
        work = container / structure.WORKS_DIR / slug
        (work / "chapters").mkdir(parents=True)
        (work / "state.json").write_text(json.dumps({"phase": "draft"}),
                                         encoding="utf-8")
    payload = {"structure": kind, "genre": "mystery",
               "form": "short-story", "works": list(works)}
    payload.update(state)
    (container / "state.json").write_text(json.dumps(payload),
                                          encoding="utf-8")
    return container


def resolve(directory):
    return subprocess.run([sys.executable, str(RESOLVE_CLI)], cwd=directory,
                          capture_output=True, text=True)


# --- the default is the thing that already existed -------------------------

def test_a_state_with_no_structure_is_standalone():
    """Every project created before this axis keeps working untouched —
    the same defaulting rule as `genre` and `form`."""
    assert structure.structure_of({}) == "standalone"
    assert structure.structure_of({"structure": None}) == "standalone"
    assert not structure.is_container({})


def test_an_unknown_structure_is_refused():
    with pytest.raises(structure.StructureError, match="unknown structure"):
        structure.structure_of({"structure": "trilogy"})


def test_a_standalone_project_reports_the_structure_block(tmp_path):
    (tmp_path / "state.json").write_text(json.dumps({"genre": "mystery"}),
                                         encoding="utf-8")
    result = resolve(tmp_path)
    assert result.returncode == 0, result.stderr
    block = json.loads(result.stdout)["structure"]
    assert block == {"name": "standalone", "is_container": False,
                     "container": None, "inherited": [],
                     "order_is_editorial": False,
                     "assembles_as_one_book": True}


# --- containers and their children -----------------------------------------

def test_a_container_resolves_and_reports_its_running_order(tmp_path):
    container = make_container(tmp_path)
    result = resolve(container)
    assert result.returncode == 0, result.stderr
    block = json.loads(result.stdout)["structure"]
    assert block["is_container"] is True
    assert block["works"] == ["01-first", "02-second"]


def test_a_child_inherits_genre_and_form_from_its_container(tmp_path):
    """The inheritance runs downward, which inverts the pack precedent
    deliberately: with packs the project copy wins because specificity is
    the point, and here the container wins because coherence is."""
    container = make_container(tmp_path)
    result = resolve(container / structure.WORKS_DIR / "01-first")
    assert result.returncode == 0, result.stderr
    resolved = json.loads(result.stdout)
    assert resolved["packs"][0]["name"] == "mystery"
    assert resolved["form"]["name"] == "short-story"
    assert set(resolved["structure"]["inherited"]) == {"genre", "form"}
    assert resolved["structure"]["container"] == str(container.resolve())


def test_a_child_may_not_set_what_makes_the_works_one_book(tmp_path):
    container = make_container(tmp_path)
    work = container / structure.WORKS_DIR / "01-first"
    work.joinpath("state.json").write_text(
        json.dumps({"phase": "draft", "genre": "fantasy"}), encoding="utf-8")
    result = resolve(container)
    assert result.returncode == 1
    assert "sets genre itself" in result.stderr


def test_a_project_beside_a_container_is_not_adopted_by_it(tmp_path):
    """Proximity is not membership. A project created inside another
    project's tree must not silently inherit its genre."""
    container = make_container(tmp_path)
    stray = container / "notes-project"
    stray.mkdir()
    stray.joinpath("state.json").write_text(json.dumps({"genre": "thriller"}),
                                            encoding="utf-8")
    resolved = json.loads(resolve(stray).stdout)
    assert resolved["packs"][0]["name"] == "thriller"
    assert resolved["structure"]["container"] is None


def test_containers_do_not_nest(tmp_path):
    container = make_container(tmp_path)
    work = container / structure.WORKS_DIR / "01-first"
    work.joinpath("state.json").write_text(
        json.dumps({"phase": "draft", "structure": "collection"}),
        encoding="utf-8")
    result = resolve(container)
    assert result.returncode == 1
    assert "structure of its own" in result.stderr


# --- the running order is a real editorial decision ------------------------

def test_a_work_on_disk_but_not_in_the_order_is_refused(tmp_path):
    """Silently exporting a book with a story missing is the failure this
    prevents. The order is not derived from the filesystem."""
    container = make_container(tmp_path, works=("01-first", "02-second"))
    (container / structure.WORKS_DIR / "03-third" / "chapters").mkdir(
        parents=True)
    (container / structure.WORKS_DIR / "03-third" / "state.json").write_text(
        json.dumps({"phase": "draft"}), encoding="utf-8")
    result = resolve(container)
    assert result.returncode == 1
    assert "03-third exists" in result.stderr


def test_an_order_naming_a_work_that_does_not_exist_is_refused(tmp_path):
    container = make_container(tmp_path)
    state = json.loads((container / "state.json").read_text())
    state["works"].append("03-ghost")
    (container / "state.json").write_text(json.dumps(state), encoding="utf-8")
    result = resolve(container)
    assert result.returncode == 1
    assert "03-ghost" in result.stderr and "does not exist" in result.stderr


def test_a_repeated_work_in_the_order_is_refused(tmp_path):
    container = make_container(tmp_path)
    state = json.loads((container / "state.json").read_text())
    state["works"] = ["01-first", "01-first", "02-second"]
    (container / "state.json").write_text(json.dumps(state), encoding="utf-8")
    result = resolve(container)
    assert result.returncode == 1
    assert "more than once" in result.stderr


def test_the_order_is_the_declared_one_not_the_filesystem_one(tmp_path):
    """Directory names are a naming convention, not an ordering mechanism
    — the opener and closer do specific work and an editor chooses them."""
    container = make_container(tmp_path, works=("02-second", "01-first"))
    block = json.loads(resolve(container).stdout)["structure"]
    assert block["works"] == ["02-second", "01-first"]


def test_a_container_needs_a_bible(tmp_path):
    import shutil

    container = make_container(tmp_path)
    shutil.rmtree(container / "bible")
    result = resolve(container)
    assert result.returncode == 1
    assert "no bible/ directory" in result.stderr


# --- series: the same machine, the opposite checks -------------------------

def test_a_series_is_a_container_too(tmp_path):
    container = make_container(tmp_path, kind="series")
    result = resolve(container)
    assert result.returncode == 0, result.stderr
    block = json.loads(result.stdout)["structure"]
    assert block["name"] == "series"
    assert block["is_container"] is True
    assert block["order_is_editorial"] is False


def test_a_collections_order_is_editorial_and_a_series_is_not(tmp_path):
    """Reordering a collection is a legitimate fix the cross-work pass can
    recommend. Reordering a series is not a fix; it is a different
    series."""
    collection = json.loads(resolve(make_container(tmp_path)).stdout)
    series = json.loads(
        resolve(make_container(tmp_path, kind="series")).stdout)
    assert collection["structure"]["order_is_editorial"] is True
    assert series["structure"]["order_is_editorial"] is False


@pytest.mark.parametrize("missing", ["canon.md", "arc.md"])
def test_a_series_needs_the_documents_its_pass_reads(tmp_path, missing):
    """canon.md is what continuity is checked against and arc.md is what
    progress is checked against. Without them the pass can only report
    that nothing contradicted, which a series of one book also achieves."""
    container = make_container(tmp_path, kind="series")
    (container / "bible" / missing).unlink()
    result = resolve(container)
    assert result.returncode == 1
    assert f"no bible/{missing}" in result.stderr


def test_a_collection_needs_the_file_that_says_what_binds_it(tmp_path):
    """The cross-work pass asks whether the binding is DELIVERED or merely
    declared, and it can ask neither of a file that does not exist."""
    container = make_container(tmp_path)
    (container / "bible" / "binding.md").unlink()
    result = resolve(container)
    assert result.returncode == 1
    assert "no bible/binding.md" in result.stderr
    assert "merely declared" in result.stderr


def test_the_two_containers_require_different_documents():
    """Each requires exactly what its own pass reads, and nothing else.
    A collection has no arc to declare and a series has no slate."""
    assert "arc.md" not in structure.REQUIRED_BIBLE["collection"]
    assert "binding.md" not in structure.REQUIRED_BIBLE["series"]


def test_a_collection_does_not_need_an_arc(tmp_path):
    """The asymmetry is the point: a collection's works do not owe the
    whole a progression, and requiring one would make every collection
    declare an arc it does not have."""
    container = make_container(tmp_path)
    assert not (container / "bible" / "arc.md").exists()
    assert resolve(container).returncode == 0


# --- convergence -----------------------------------------------------------

def draft(work, texts):
    for i, text in enumerate(texts, start=1):
        work.joinpath("chapters", f"ch_{i:02d}.md").write_text(
            text, encoding="utf-8")


PROSE_A = ("She opened the door. The hall was cold and smelled of rain. "
           "Somewhere below, a radio played something old and slow. "
           "She counted the steps down, the way she always had, and stopped "
           "at seven because the eighth one creaked. ") * 12
PROSE_B = ("Marcus drove. Rain. The wipers could not keep up with it and he "
           "did not slow down, because slowing down was how you got caught "
           "thinking. Ahead the road bent left toward the water and he took "
           "it fast, hands loose, radio off, thinking about nothing at all. "
           ) * 12


def test_convergence_needs_a_container(tmp_path):
    (tmp_path / "state.json").write_text(json.dumps({"genre": "mystery"}),
                                         encoding="utf-8")
    result = subprocess.run([sys.executable, str(CONVERGENCE_CLI)],
                            cwd=tmp_path, capture_output=True, text=True)
    assert result.returncode == 2
    assert "a standalone project has one" in result.stderr


def test_convergence_reports_per_work_metrics(tmp_path):
    container = make_container(tmp_path)
    draft(container / structure.WORKS_DIR / "01-first", [PROSE_A])
    draft(container / structure.WORKS_DIR / "02-second", [PROSE_B])
    result = subprocess.run([sys.executable, str(CONVERGENCE_CLI), "--quiet"],
                            cwd=container, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    report = json.loads(
        (container / "edit_logs/convergence.json").read_text())
    assert sorted(report["drafted"]) == ["01-first", "02-second"]
    assert report["undrafted"] == []
    assert report["convergence"]


def test_an_undrafted_work_is_named_not_counted(tmp_path):
    container = make_container(tmp_path, works=("01-first", "02-second"))
    draft(container / structure.WORKS_DIR / "01-first", [PROSE_A])
    subprocess.run([sys.executable, str(CONVERGENCE_CLI), "--quiet"],
                   cwd=container, capture_output=True, text=True)
    report = json.loads(
        (container / "edit_logs/convergence.json").read_text())
    assert report["drafted"] == ["01-first"]
    assert report["undrafted"] == ["02-second"]
    # One work cannot converge with anything.
    assert report["convergence"] == {}


def test_scale_metrics_are_reported_separately_from_style_ones():
    """The correction autoanthology's first real run produced: five of its
    seven converged metrics were downstream of a shared target length, and
    only one was something the rubric knew what to do with. Reporting them
    together sends a judge hunting for prose repetition that is not there.
    """
    import convergence

    per_work = {
        # Identical word_count and sentence_count (scale), different
        # simile_density (style).
        "a": {"word_count": 5000, "sentence_count": 300, "simile_density": 2.0},
        "b": {"word_count": 5010, "sentence_count": 301, "simile_density": 9.0},
    }
    _, style, scale = convergence.convergence_report(per_work)
    assert scale == ["sentence_count", "word_count"]
    assert style == []


def test_a_metric_with_a_zero_mean_is_omitted():
    import convergence

    _, style, scale = convergence.convergence_report(
        {"a": {"em_dashes": 0}, "b": {"em_dashes": 0}})
    assert style == [] and scale == []


def test_the_pooled_scratch_file_does_not_survive(tmp_path):
    """It is written inside the work directory, so a leak would land in
    the user's git repo."""
    container = make_container(tmp_path)
    work = container / structure.WORKS_DIR / "01-first"
    draft(work, [PROSE_A])
    draft(container / structure.WORKS_DIR / "02-second", [PROSE_B])
    subprocess.run([sys.executable, str(CONVERGENCE_CLI), "--quiet"],
                   cwd=container, capture_output=True, text=True)
    assert not list(work.glob(".convergence*"))


# --- the rubric and the skill ----------------------------------------------

def test_the_collection_rubric_scores_seven_dimensions():
    import genre_pack

    rubric = (REPO / "plugin/autoauthor/shared/rubrics/collection-pass.md"
              ).read_text(encoding="utf-8")
    dimensions, malformed, caps, prose_caps = genre_pack.dimension_bullets(
        genre_pack.section_body(rubric, "Dimensions"))
    assert malformed == []
    assert dimensions == ["repetition", "facet_coverage", "range",
                          "binding_delivery", "independence", "running_order",
                          "collection_engagement"]
    assert caps == prose_caps, "a declared cap disagrees with its criteria"


def test_the_collection_skill_exists_and_is_named_for_its_directory():
    skill = REPO / "plugin/autoauthor/skills/collection/SKILL.md"
    assert "name: collection" in skill.read_text(encoding="utf-8")


# --- convergence means the opposite thing in a series ----------------------

def test_the_report_says_which_reading_applies(tmp_path):
    """Both passes read the same file and one of them has to invert it.
    Leaving that to whoever reads the JSON is how it gets forgotten."""
    import convergence

    for kind, verdict in (("collection", "defect"), ("series", "goal")):
        container = make_container(tmp_path / kind, kind=kind)
        draft(container / structure.WORKS_DIR / "01-first", [PROSE_A])
        draft(container / structure.WORKS_DIR / "02-second", [PROSE_B])
        subprocess.run([sys.executable, str(CONVERGENCE_CLI), "--quiet"],
                       cwd=container, capture_output=True, text=True)
        report = json.loads(
            (container / "edit_logs/convergence.json").read_text())
        assert report["structure"] == kind
        assert report["interpretation"]["converged"] == verdict
    assert set(convergence.INTERPRETATION) == {"collection", "series"}


def test_a_divergent_work_is_found_by_a_robust_measure():
    """The trap this walked into first: an ordinary z-score measures the
    outlier against a standard deviation the outlier itself inflates. At
    four works the largest z-score arithmetically possible is 1.5, so a
    2-sigma check could never fire at the sizes a series actually has."""
    import convergence

    per_work = {
        "01": {"simile_density": 2.0},
        "02": {"simile_density": 2.1},
        "03": {"simile_density": 2.05},
        "04": {"simile_density": 30.0},
    }
    assert convergence.divergent_works(per_work) == {"04": ["simile_density"]}

    import statistics
    values = [row["simile_density"] for row in per_work.values()]
    ordinary_z = (abs(30.0 - statistics.mean(values))
                  / statistics.stdev(values))
    assert ordinary_z < 2.0, "the naive check would have found nothing"


def test_ordinary_variation_is_not_divergence():
    import convergence

    assert convergence.divergent_works({
        "01": {"simile_density": 2.0},
        "02": {"simile_density": 2.4},
        "03": {"simile_density": 1.8}}) == {}


def test_two_works_cannot_diverge():
    """With two, each is the other's outlier."""
    import convergence

    assert convergence.divergent_works({"01": {"simile_density": 1.0},
                                        "02": {"simile_density": 90.0}}) == {}


def test_length_is_not_divergence():
    """A volume longer than its neighbours is longer, not differently
    written — the same exclusion the convergence side makes."""
    import convergence

    assert convergence.divergent_works({
        "01": {"word_count": 30000}, "02": {"word_count": 30100},
        "03": {"word_count": 29900}, "04": {"word_count": 90000}}) == {}


# --- the series rubric and skill -------------------------------------------

def test_the_series_rubric_scores_seven_dimensions():
    import genre_pack

    rubric = (REPO / "plugin/autoauthor/shared/rubrics/series-pass.md"
              ).read_text(encoding="utf-8")
    dimensions, malformed, caps, prose_caps = genre_pack.dimension_bullets(
        genre_pack.section_body(rubric, "Dimensions"))
    assert malformed == []
    assert dimensions == ["canon_integrity", "canon_promotion",
                          "volume_closure", "arc_progression",
                          "entry_and_recap", "character_continuity",
                          "series_voice"]
    assert caps == prose_caps, "a declared cap disagrees with its criteria"
    # Continuity is the one thing a series cannot be sound without, so its
    # cap is the severest in either cross-work rubric.
    assert caps["canon_integrity"] == 4


def test_the_two_cross_work_rubrics_check_opposite_things():
    """The clearest statement of what separates the containers. A
    collection requires each work to stand alone; a series requires each
    volume to depend on what came before without contradicting it."""
    rubrics = REPO / "plugin/autoauthor/shared/rubrics"
    collection = (rubrics / "collection-pass.md").read_text(encoding="utf-8")
    series = (rubrics / "series-pass.md").read_text(encoding="utf-8")
    assert "independence" in collection and "independence" not in series
    assert "canon_integrity" in series and "canon_integrity" not in collection
    assert "INVERTED" in series


# --- assembling a container into a book ------------------------------------

ASSEMBLE_CLI = SCRIPTS / "assemble.py"


def chapter(n, title, text="Prose.\n"):
    return f"# Chapter {n}: {title}\n\n{text}"


def test_a_collection_assembles_in_the_declared_order(tmp_path):
    container = make_container(tmp_path, works=("02-second", "01-first"))
    for slug, titles in (("01-first", ["Alpha", "Beta"]),
                         ("02-second", ["Gamma"])):
        work = container / structure.WORKS_DIR / slug
        for i, title in enumerate(titles, start=1):
            (work / "chapters" / f"ch_{i:02d}.md").write_text(
                chapter(i, title), encoding="utf-8")

    result = subprocess.run([sys.executable, str(ASSEMBLE_CLI)],
                            cwd=container, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr + result.stdout

    built = sorted((container / "assembled").glob("ch_*.md"))
    assert [p.name for p in built] == ["ch_01.md", "ch_02.md", "ch_03.md"]
    # 02-second is declared first, so its chapter leads the bound book...
    assert "Gamma" in built[0].read_text()
    # ...and the numbering is gapless across works rather than restarting.
    assert built[1].read_text().startswith("## First\n\n# Chapter 2: Alpha")
    assert "# Chapter 3: Beta" in built[2].read_text()


def test_each_work_opens_with_its_own_title(tmp_path):
    """A reader has to know a new story has started."""
    container = make_container(tmp_path)
    for slug in ("01-first", "02-second"):
        work = container / structure.WORKS_DIR / slug
        (work / "chapters" / "ch_01.md").write_text(chapter(1, "One"),
                                                    encoding="utf-8")
        state = json.loads((work / "state.json").read_text())
        state["title"] = f"The {slug[3:].title()} Story"
        (work / "state.json").write_text(json.dumps(state), encoding="utf-8")

    subprocess.run([sys.executable, str(ASSEMBLE_CLI)], cwd=container,
                   capture_output=True, text=True)
    assembled = (container / "assembled" / "ch_02.md").read_text()
    assert assembled.startswith("## The Second Story\n")


def test_a_work_that_contributed_nothing_is_loud(tmp_path):
    """A bound book silently missing a story is the failure this path
    risks, and it is invisible in the output — the PDF just builds."""
    container = make_container(tmp_path)
    (container / structure.WORKS_DIR / "01-first" / "chapters"
     / "ch_01.md").write_text(chapter(1, "One"), encoding="utf-8")
    result = subprocess.run([sys.executable, str(ASSEMBLE_CLI)],
                            cwd=container, capture_output=True, text=True)
    assert result.returncode == 1
    assert "02-second contributed no chapters" in result.stderr


def test_a_series_refuses_to_assemble(tmp_path):
    """Each volume is a book. Binding them into one is an omnibus, which
    needs its own front matter and its own decisions."""
    container = make_container(tmp_path, kind="series")
    (container / structure.WORKS_DIR / "01-first" / "chapters"
     / "ch_01.md").write_text(chapter(1, "One"), encoding="utf-8")
    result = subprocess.run([sys.executable, str(ASSEMBLE_CLI)],
                            cwd=container, capture_output=True, text=True)
    assert result.returncode == 1
    assert "does not assemble into one book" in result.stderr
    assert not (container / "assembled").exists()


def test_assemble_needs_a_container(tmp_path):
    (tmp_path / "state.json").write_text(json.dumps({"genre": "mystery"}),
                                         encoding="utf-8")
    result = subprocess.run([sys.executable, str(ASSEMBLE_CLI)], cwd=tmp_path,
                            capture_output=True, text=True)
    assert result.returncode == 2
    assert "nothing to assemble" in result.stderr


def test_check_writes_nothing(tmp_path):
    container = make_container(tmp_path)
    for slug in ("01-first", "02-second"):
        (container / structure.WORKS_DIR / slug / "chapters"
         / "ch_01.md").write_text(chapter(1, "One"), encoding="utf-8")
    result = subprocess.run([sys.executable, str(ASSEMBLE_CLI), "--check"],
                            cwd=container, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert not (container / "assembled").exists()
    assert "2 chapters from 2 works" in result.stdout


def test_a_chapter_with_an_unexpected_heading_is_copied_not_guessed_at(tmp_path):
    """Prose is never rewritten to fit the typesetter."""
    container = make_container(tmp_path, works=("01-first",))
    odd = "Just prose, no heading at all.\n"
    (container / structure.WORKS_DIR / "01-first" / "chapters"
     / "ch_01.md").write_text(odd, encoding="utf-8")
    subprocess.run([sys.executable, str(ASSEMBLE_CLI)], cwd=container,
                   capture_output=True, text=True)
    assert odd in (container / "assembled" / "ch_01.md").read_text()


def test_a_stale_assembly_does_not_survive_a_rebuild(tmp_path):
    """A story removed from the running order must not linger in the
    bound book from the last run."""
    container = make_container(tmp_path)
    for slug in ("01-first", "02-second"):
        (container / structure.WORKS_DIR / slug / "chapters"
         / "ch_01.md").write_text(chapter(1, "One"), encoding="utf-8")
    subprocess.run([sys.executable, str(ASSEMBLE_CLI)], cwd=container,
                   capture_output=True, text=True)
    assert len(list((container / "assembled").glob("ch_*.md"))) == 2

    import shutil
    shutil.rmtree(container / structure.WORKS_DIR / "02-second")
    state = json.loads((container / "state.json").read_text())
    state["works"] = ["01-first"]
    (container / "state.json").write_text(json.dumps(state), encoding="utf-8")
    subprocess.run([sys.executable, str(ASSEMBLE_CLI)], cwd=container,
                   capture_output=True, text=True)
    assert len(list((container / "assembled").glob("ch_*.md"))) == 1


# --- a title has a home ----------------------------------------------------
#
# The first export asked for one, which is when it emerged that the title
# had nowhere to live: the story named itself during foundation, wrote the
# name into two markdown headings as decoration, and nothing downstream
# could read it.

def test_the_state_template_has_a_title_field():
    import json as _json
    template = _json.loads(
        (REPO / "plugin/autoauthor/shared/templates/state.json")
        .read_text(encoding="utf-8"))
    assert "title" in template
    assert template["title"] is None, "unset, like genre and form"


def test_export_reads_the_title_and_writes_back_what_it_asks_for():
    """A title asked for and not recorded is a title asked for again, and
    answered differently the second time."""
    export = (REPO / "plugin/autoauthor/skills/export/SKILL.md"
              ).read_text(encoding="utf-8")
    assert "read `state.json`'s `title`" in export
    assert "WRITE THE ANSWER BACK" in export


def test_the_phases_that_can_learn_a_title_record_it():
    skills = REPO / "plugin/autoauthor/skills"
    for name in ("seed", "foundation"):
        text = (skills / name / "SKILL.md").read_text(encoding="utf-8")
        assert "`title`" in text, f"{name} never records the title"


def test_a_work_with_a_title_uses_it_as_its_half_title(tmp_path):
    import assemble

    container = make_container(tmp_path, works=("01-porter",))
    work = container / structure.WORKS_DIR / "01-porter"
    state = json.loads((work / "state.json").read_text())
    state["title"] = "The Warm Key"
    (work / "state.json").write_text(json.dumps(state), encoding="utf-8")
    assert assemble.work_title(work) == "The Warm Key"


def test_a_work_without_one_falls_back_to_its_directory_name(tmp_path):
    """The fallback builds a book with a half-title of "Porter" over a
    story called "The Warm Key", and nothing complains. It exists so the
    bind never fails, not because it is right."""
    import assemble

    container = make_container(tmp_path, works=("01-porter",))
    assert assemble.work_title(
        container / structure.WORKS_DIR / "01-porter") == "Porter"
