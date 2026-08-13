"""Guards on the plugin's manifests and skill layout.

These exist because every defect they catch is silent. Nothing here throws
at runtime — a version that disagrees with itself installs fine, and a skill
whose frontmatter name does not match its directory is invocable under a
name no document mentions. Both shipped during the 0.4.0 rename and were
caught by hand.

The version check deliberately covers only the three PLUGIN version strings.
`pyproject.toml` carries its own version for the dev tooling that runs these
tests; it is not the shipped artifact and must not be roped in here, or a
future release will be blocked by a number nobody publishes.
"""
import json
import re
from pathlib import Path

REPO = Path(__file__).parent.parent
MARKETPLACE = REPO / ".claude-plugin/marketplace.json"
PLUGIN_DIR = REPO / "plugin/autoauthor"
PLUGIN_JSON = PLUGIN_DIR / ".claude-plugin/plugin.json"
SKILLS = PLUGIN_DIR / "skills"

SEMVER = re.compile(r"^\d+\.\d+\.\d+$")


def market():
    return json.loads(MARKETPLACE.read_text(encoding="utf-8"))


def plugin():
    return json.loads(PLUGIN_JSON.read_text(encoding="utf-8"))


def entry():
    """The marketplace's entry for this plugin."""
    plugins = market()["plugins"]
    matches = [p for p in plugins if p["name"] == plugin()["name"]]
    assert len(matches) == 1, (
        f"expected exactly one marketplace entry named {plugin()['name']!r}, "
        f"found {len(matches)}")
    return matches[0]


def skill_dirs():
    return sorted(d for d in SKILLS.iterdir() if d.is_dir())


def frontmatter(skill_md):
    """The YAML-ish frontmatter block as a dict of the scalar keys."""
    text = skill_md.read_text(encoding="utf-8")
    assert text.startswith("---\n"), f"{skill_md} has no frontmatter block"
    body = text.split("---\n", 2)[1]
    out = {}
    for line in body.splitlines():
        if ":" in line and not line.startswith((" ", "\t", "-")):
            k, _, v = line.partition(":")
            out[k.strip()] = v.strip()
    return out


# --- versions -------------------------------------------------------------

def test_the_three_plugin_versions_agree():
    """Bumping a release means editing three strings by hand.

    Missing one ships a plugin whose manifest disagrees with the marketplace
    that serves it, and the update button greys out for reasons nobody can
    see.
    """
    versions = {
        "plugin.json": plugin()["version"],
        "marketplace.json (marketplace)": market()["version"],
        "marketplace.json (plugin entry)": entry()["version"],
    }
    assert len(set(versions.values())) == 1, (
        "plugin version strings disagree:\n  "
        + "\n  ".join(f"{k}: {v}" for k, v in versions.items()))


def test_versions_are_semver():
    assert SEMVER.match(plugin()["version"]), plugin()["version"]


# --- identity -------------------------------------------------------------

def test_plugin_name_matches_its_directory():
    assert plugin()["name"] == PLUGIN_DIR.name


def test_marketplace_source_points_at_the_plugin():
    src = (REPO / entry()["source"]).resolve()
    assert src == PLUGIN_DIR.resolve(), f"source {entry()['source']} -> {src}"
    assert (src / ".claude-plugin/plugin.json").exists()


def test_no_stale_plugin_directory_survives_a_rename():
    """A rename that copies instead of moving leaves two plugin trees.

    The stale one keeps validating and keeps being found by globs, so it
    fails silently rather than loudly.
    """
    trees = [d for d in (REPO / "plugin").iterdir()
             if d.is_dir() and (d / ".claude-plugin/plugin.json").exists()]
    assert trees == [PLUGIN_DIR], f"expected one plugin tree, found {trees}"


# --- skills ---------------------------------------------------------------

def test_every_skill_directory_has_a_skill_md():
    missing = [d.name for d in skill_dirs() if not (d / "SKILL.md").exists()]
    assert not missing, f"skill directories without SKILL.md: {missing}"


def test_skill_frontmatter_name_matches_its_directory():
    """The 0.4.0 rename shipped `name: novel` inside `skills/status/`.

    Every path and every invocation had been updated; only the frontmatter
    field was missed, so the skill would have been invocable as
    `/autoauthor:novel` while every document said `status`. Nothing errors.
    """
    wrong = []
    for d in skill_dirs():
        declared = frontmatter(d / "SKILL.md").get("name")
        if declared != d.name:
            wrong.append(f"{d.name}/SKILL.md declares name: {declared!r}")
    assert not wrong, (
        "skill frontmatter disagrees with its directory:\n  "
        + "\n  ".join(wrong))


def test_every_skill_has_a_nonempty_description():
    """The description is what decides whether a skill ever triggers."""
    bad = [d.name for d in skill_dirs()
           if not frontmatter(d / "SKILL.md").get("description")]
    assert not bad, f"skills with no description: {bad}"


def test_skill_names_carry_no_redundant_prefix():
    """0.4.0 dropped `novel-`; the plugin namespace already says it.

    Also guards the broader point: a skill named for one form is wrong once
    the form axis ships short stories and collections.
    """
    prefixed = [d.name for d in skill_dirs() if d.name.startswith("novel")]
    assert not prefixed, f"skills still carrying a form prefix: {prefixed}"


def test_the_expected_skills_are_all_present():
    """Pins the roster so a lost directory is loud rather than quiet."""
    assert {d.name for d in skill_dirs()} == {
        "status", "seed", "import", "foundation",
        "draft", "revise", "review", "export"}
