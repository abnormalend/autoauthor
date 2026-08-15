"""The plugin must not teach the drafter the phrases it bans.

`foundation/SKILL.md` and `draft/SKILL.md` require reading ANTI-SLOP.md AND
every genre pack, form and craft doc. A banned construction anywhere in that
set arrives in the drafter's context window alongside the instruction to kill
it on sight -- which is priming, not merely an inconsistency. 0.16.0 found
`load-bearing` in 22 such places and `not just X, but Y` in the chapter
rubric, the latter while asking whether the dialogue sounded machine-made.

Deliberately narrow. An audit of the full tier lists against this same corpus
returned 34 hits of which 33 were false positives -- `leverage` as a noun
("the antagonist's leverage"), `Catalyst` as a Save the Cat beat name,
`tapestry` inside a quoted ban. A guard that cries wolf gets muted, so this
pins only the two checks that came back clean: the multi-word Tier 1 phrases
and the structural formulas. Both are constructions no term of art needs.
"""
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent / "plugin/autoauthor"
sys.path.insert(0, str(ROOT / "shared/scripts"))
import slop_score  # noqa: E402

# What the drafting and foundation skills name as required reading, plus the
# rubrics, which reach a judge in the same posture.
REQUIRED_READING = ("shared/craft", "shared/genres", "shared/forms",
                    "shared/rubrics", "shared/templates")

# These three files LIST the banned constructions. Quoting a ban is the
# opposite of committing one, and the exemption is per-file rather than
# per-directory so that every pack, form and rubric beside them stays strict.
QUOTES_THE_BANS = {
    "shared/craft/ANTI-SLOP.md",
    "shared/craft/ANTI-PATTERNS.md",
    "shared/templates/voice.md",
}


def required_reading_files():
    for directory in REQUIRED_READING:
        for path in sorted((ROOT / directory).rglob("*.md")):
            rel = str(path.relative_to(ROOT))
            if rel not in QUOTES_THE_BANS:
                yield pytest.param(path, id=rel)


@pytest.mark.parametrize("path", required_reading_files())
def test_no_tier1_phrases_in_required_reading(path):
    """`load-bearing` and its cousins, in the drafter's own context."""
    flat = re.sub(r"\s+", " ", path.read_text(encoding="utf-8").lower())
    for pattern in slop_score.TIER1_PHRASES:
        found = re.findall(pattern, flat)
        assert not found, (
            f"{path.name} uses a Tier 1 phrase ({found[0]!r}) the drafter "
            f"reads this file alongside a ban on. Rewrite it.")


@pytest.mark.parametrize("path", required_reading_files())
def test_no_structural_formulas_in_required_reading(path):
    """"Not just X, but Y" and friends -- the rhetorical templates."""
    flat = re.sub(r"\s+", " ", path.read_text(encoding="utf-8"))
    for pattern in slop_score.STRUCTURAL_AI_TICS:
        match = re.search(pattern, flat)
        assert not match, (
            f"{path.name} uses a structural AI formula ({match.group()!r}). "
            f"ANTI-PATTERNS.md calls this one out by name.")
