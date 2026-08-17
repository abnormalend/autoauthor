"""Drafting rules may not name world.md as if every form built one.

At `short-story` the resolver reports layers [voice, characters, outline];
the facts a drafting rule wants live in the outline's facts section. A rule
that says "defined in world.md" reads, to a drafter who finds no world.md,
as a rule that does not apply — which is the direct route to the vagueness
the rule exists to prevent (draft findings 2026-08-17, #7).
"""
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent / "plugin/autoauthor"
PACKS = sorted((ROOT / "shared/genres").glob("*.md"))
RULES = ROOT / "skills/draft/references/drafting-rules.md"


def drafting_rules_section(text):
    m = re.search(r"^## Drafting Rules.*?(?=^## |\Z)", text, re.S | re.M)
    return m.group(0) if m else ""


@pytest.mark.parametrize("path", PACKS, ids=lambda p: p.stem)
def test_pack_drafting_rules_do_not_name_world_md(path):
    section = drafting_rules_section(path.read_text(encoding="utf-8"))
    assert "world.md" not in section, (
        f"{path.name}: a drafting rule names world.md literally; name the "
        "role (the world layer, or the outline's facts section where the "
        "form builds no world.md)")


def test_base_drafting_rules_do_not_name_world_md():
    assert "world.md" not in RULES.read_text(encoding="utf-8")
