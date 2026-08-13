"""Guard: no genre-specific content outside plugin/autoauthor/shared/genres/.

The successor to the De-Bells rule. The original plan scrubbed content from
the project's first novel out of the machinery; this keeps the machinery free
of any single genre's assumptions.

Two separate checks, because the same word means different things in
different places:

- Genre furniture (magic, bestiary, elves) is a leak anywhere outside a pack.
- Author names are a leak in a rubric or a skill, where they would be comps —
  but in CRAFT.md they are citations on genre-neutral structural frameworks,
  and stripping a correct attribution to satisfy a regex would be the wrong
  trade. That exemption is scoped to shared/craft/ and pinned by
  test_craft_citations_survived, so it cannot be used to quietly delete them.
"""
import re
from pathlib import Path

PLUGIN = Path(__file__).parent.parent / "plugin/autoauthor"

SCANNED_DIRS = ["shared/rubrics", "shared/craft", "shared/templates",
                "shared/scripts", "skills"]

# Genre furniture. A hit outside shared/genres/ means a genre assumption
# crept back into the base machinery.
LEAK_RE = re.compile(
    r"\b(fantasy|magic|magical|sorcer\w*|wizard|bestiary|elves|dwarves"
    r"|orcs)\b", re.I)

# Comparable authors. These belong in a pack's `comps`, never in a base file.
COMPS_RE = re.compile(
    r"\b(sanderson|tolkien|jemisin|rothfuss|hobb|le guin|rowling)\b", re.I)

# An author name is a COMP when it tells a persona whose books to measure
# against — that is genre content and belongs in a pack. It is a CITATION
# when it attributes a craft framework, and those are genre-neutral and must
# survive. Only these two files teach craft frameworks, so the exemption is
# per-file rather than per-directory: every rubric, every SKILL.md, every
# template stays strict, because a comp appearing in one of those is a leak.
COMPS_EXEMPT_FILES = {
    "shared/craft/CRAFT.md",
    "skills/foundation/references/layer-guides.md",
}

# ANTI-SLOP.md and voice.md list 'realm' and 'tapestry' as banned slop words,
# which is vocabulary guidance, not genre content. Nothing else is exempt.
ALLOWED = {
    "shared/craft/ANTI-SLOP.md",
    "shared/templates/voice.md",
}

# The router's migration step names `fantasy` because that is a historical
# fact about projects created before genre packs existed: their results.tsv
# scores were produced under the fantasy rubric, and telling a user to pick
# anything else without saying so would hide that their old and new scores
# are incomparable. Same category as PIPELINE.md recording the original
# program's `lore_score` — a record of what was, not an assumption about
# what should be. Scoped to the migration and pinned by
# test_router_names_fantasy_only_in_the_migration.
LEAK_EXEMPT_FILES = {"skills/status/SKILL.md"}

# Attributions on genre-neutral craft frameworks. These must survive the
# comps exemption above — see the module docstring.
PINNED_CITATIONS = (
    "Promises, Progress, Payoff (Sanderson)",
    "MICE Quotient (Orson Scott Card / Sanderson)",
    "The Three Sliders (Sanderson)",
)


def scanned_files():
    for directory in SCANNED_DIRS:
        for path in sorted((PLUGIN / directory).rglob("*")):
            if not path.is_file():
                continue
            if path.suffix not in {".md", ".py", ".json"}:
                continue
            rel = path.relative_to(PLUGIN).as_posix()
            if rel in ALLOWED:
                continue
            yield rel, path


def _offenders(pattern, skip_files=()):
    found = []
    for rel, path in scanned_files():
        if rel in skip_files:
            continue
        for lineno, line in enumerate(
                path.read_text(encoding="utf-8").splitlines(), start=1):
            match = pattern.search(line)
            if match:
                found.append(
                    f"{rel}:{lineno}: {match.group(0)!r} in {line.strip()!r}")
    return found


def test_no_genre_terms_outside_genre_packs():
    offenders = _offenders(LEAK_RE, skip_files=LEAK_EXEMPT_FILES)
    assert not offenders, (
        "genre-specific content found outside shared/genres/ — move it into "
        "a genre pack:\n  " + "\n  ".join(offenders))


def test_router_names_fantasy_only_in_the_migration():
    """The router's exemption is scoped to its migration step.

    Every genre term in that file must sit inside the migration, which
    exists to tell a legacy user which rubric produced their old scores.
    A hit anywhere else means genre logic crept into the router itself.
    """
    path = PLUGIN / "skills/status/SKILL.md"
    lines = path.read_text(encoding="utf-8").splitlines()

    starts = [i for i, l in enumerate(lines) if l.startswith("3. **Migration check.")]
    ends = [i for i, l in enumerate(lines) if l.startswith("4. **Report**")]
    assert starts and ends, "the router's migration step has moved or been renamed"
    lo, hi = starts[0], ends[0]

    stray = [f"{i + 1}: {lines[i].strip()!r}"
             for i in range(len(lines))
             if LEAK_RE.search(lines[i]) and not lo <= i < hi]
    assert not stray, (
        "genre terms in skills/status/SKILL.md outside the migration step:\n  "
        + "\n  ".join(stray))


def test_no_comp_authors_outside_genre_packs():
    offenders = _offenders(COMPS_RE, skip_files=COMPS_EXEMPT_FILES)
    assert not offenders, (
        "comparable-author names found outside shared/genres/ — these belong "
        "in a pack's `comps`:\n  " + "\n  ".join(offenders))


def test_craft_citations_survived():
    """The comps exemption is scoped, not a blanket pass.

    If these disappear, someone 'fixed' a false positive by deleting a
    correct citation rather than by narrowing the regex.
    """
    craft = (PLUGIN / "shared/craft/CRAFT.md").read_text(encoding="utf-8")
    for citation in PINNED_CITATIONS:
        assert citation in craft, f"citation removed from CRAFT.md: {citation}"


def test_comps_exemption_covers_only_craft_reference_files():
    """The exemption must not silently widen.

    Adding a rubric or a SKILL.md here would let real comps through, which
    is the leak this guard exists to catch.
    """
    assert COMPS_EXEMPT_FILES == {
        "shared/craft/CRAFT.md",
        "skills/foundation/references/layer-guides.md",
    }
    for rel in COMPS_EXEMPT_FILES:
        assert (PLUGIN / rel).exists(), f"exempt file no longer exists: {rel}"


def test_packs_are_not_scanned():
    """The packs are where genre content is SUPPOSED to live.

    If shared/genres/ ever lands in SCANNED_DIRS, every pack fails the guard
    and the natural 'fix' is to gut the packs.
    """
    scanned = {rel for rel, _ in scanned_files()}
    assert not any(rel.startswith("shared/genres") for rel in scanned)


def test_guard_actually_scans_something():
    """A regex guard that scans zero files always passes. Prove it doesn't."""
    assert len(list(scanned_files())) > 20


def test_guard_would_catch_a_real_leak(tmp_path):
    """Prove the pattern fires, so a green result means 'clean', not 'broken'."""
    assert LEAK_RE.search("The magic system needs hard rules")
    assert LEAK_RE.search("## Bestiary")
    assert COMPS_RE.search("You compare everything to Sanderson and Hobb.")
    # ...and does not fire on ordinary prose that merely sounds adjacent.
    assert not LEAK_RE.search("The institution's reach constrains her.")
    assert not COMPS_RE.search("The editor has seen 200 novels.")
