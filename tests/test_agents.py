"""The plugin's agent definitions and the model contract the skills rely on.

Every scored dispatch goes to `autoauthor:judge`, which pins one model, so a
project's score history was produced by one instrument; the cheaper tiers
(`editor`, `reader`) are the dispatches whose output is verified or gated
downstream. A skill that fell back to `general-purpose` would silently
inherit the session model and break the comparability the pin exists for.
"""
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent / "plugin/autoauthor"
AGENTS = sorted((ROOT / "agents").glob("*.md"))
SKILLS = sorted((ROOT / "skills").glob("*/SKILL.md"))
RUBRICS = ROOT / "shared/rubrics"

MODEL_RE = re.compile(r"^(opus|sonnet|haiku|inherit|claude-[a-z0-9.-]+)$")


def frontmatter(path):
    text = path.read_text(encoding="utf-8")
    assert text.startswith("---\n"), f"{path.name}: no frontmatter"
    head = text[4:].split("\n---\n", 1)[0]
    return dict(line.split(":", 1) for line in head.splitlines() if ":" in line), text


def test_the_three_agents_exist():
    assert {p.stem for p in AGENTS} == {"judge", "editor", "reader"}


@pytest.mark.parametrize("path", AGENTS, ids=lambda p: p.stem)
def test_agent_frontmatter_pins_a_model_and_a_tool_set(path):
    meta, _ = frontmatter(path)
    assert meta.get("name", "").strip() == path.stem
    assert meta.get("description", "").strip()
    assert MODEL_RE.match(meta.get("model", "").strip()), meta.get("model")
    assert meta.get("tools", "").strip()


def test_only_the_judge_may_write():
    for path in AGENTS:
        meta, _ = frontmatter(path)
        tools = {t.strip() for t in meta["tools"].split(",")}
        if path.stem == "judge":
            assert "Write" in tools, "judges write their own verdict files"
        else:
            assert "Write" not in tools, f"{path.stem} has no verdict file to write"


@pytest.mark.parametrize("path", SKILLS, ids=lambda p: p.parent.name)
def test_every_skill_pins_its_own_model(path):
    meta, _ = frontmatter(path)
    assert MODEL_RE.match(meta.get("model", "").strip()), (
        f"{path.parent.name}: SKILL.md frontmatter needs a `model:`")


@pytest.mark.parametrize("path", SKILLS, ids=lambda p: p.parent.name)
def test_no_skill_dispatches_a_general_purpose_judge(path):
    text = path.read_text(encoding="utf-8")
    assert "general-purpose" not in text, (
        f"{path.parent.name}: dispatch names general-purpose; use "
        "autoauthor:judge / autoauthor:editor / autoauthor:reader")


def test_scored_dispatches_name_a_plugin_agent():
    for name in ("draft", "foundation", "revise", "review", "collection", "series"):
        text = (ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
        assert "autoauthor:judge" in text, f"{name}: no autoauthor:judge dispatch"
    revise = (ROOT / "skills/revise/SKILL.md").read_text(encoding="utf-8")
    assert "autoauthor:editor" in revise and "autoauthor:reader" in revise


def test_every_scoring_rubric_records_the_judge_model():
    for path in sorted(RUBRICS.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        if re.search(r'"\w+_score": N\.NN', text):
            assert '"judge_model"' in text, f"{path.name}: schema lacks judge_model"
