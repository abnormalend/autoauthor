# Genre Pack Authoring Guide

This file is a guide, not a skeleton — copying it will not produce a
working pack. Create `<name>.md` and paste the block under
[Frontmatter](#frontmatter) below — starting at the `---` line, without
the surrounding backticks — as the very first thing in the file. Then
work down this guide from `## Framing` onward, filling in each `##`
section.

Validate as you go:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/validate_genre_pack.py" <name>.md
```

(`${CLAUDE_PLUGIN_ROOT}` is a variable Claude Code fills in with the
installed plugin's directory. Running the command yourself in a
terminal, substitute the path to `plugin/autonovel` in this repo.)

A pack may live in the plugin (`shared/genres/`) or in a single novel
project (`<project>/genres/`). The project copy wins.

## Roles

`role` is a list, because most packs serve more than one:

- **primary** — owns the pillar dimensions, category weights, plot
  architecture, book shape, and seed prompt.
- **secondary** — contributes additively to a primary. Its weights,
  `pillar_label`, `beat_system`, `shape`, and Plot Architecture are ignored.
- **modifier** — an orthogonal axis (age category, heat level, tone). Only
  its Framing, Genre Contract, Drafting Rules, and `content_register` are
  read. It may not declare `weights`, `pillar_label`, `beat_system`,
  `shape`, or a Pillar Dimensions section.

Romance is `["primary", "secondary"]` — a romance novel, or a romantic
subplot in a fantasy. Erotica is `["primary", "modifier"]`.

A finished pack is switched on from the novel project's `state.json`,
one key per role: `genre` names the primary (defaults to `"general"`
when unset), `genre_secondary` names the single optional secondary, and
`genre_modifiers` is a list of modifier names. A pack must declare the
role of the slot it is used in, and may fill only one slot per project.

## Required

A primary needs `## Framing` and `## Pillar Dimensions`. A modifier needs
neither. Everything else is optional; omit `## Plot Architecture` to inherit
the base Save the Cat structure.

## Calibration

Read this before writing `weights` or `## Pillar Dimensions`.

The foundation loop exits only when BOTH the weighted `overall_score` is
above 7.5 AND the pillar score — the average of *your* pillar
dimensions, on its own — is above 7.0. The pillar bar is an
**independent gate**. `weights` decides how much the pillar contributes
to the overall and nothing else, so lowering `pillar` does not soften
the 7.0 pillar bar; it only removes the pillar's influence on the
overall. A pack that sets `pillar: 15` because "this genre cares less
about worldbuilding" will still refuse to exit the loop on pillar score.

That makes the score caps you write into dimension criteria ("if X,
score 5 max") arithmetic you have to check. Caps are the right tool —
they are what stops a judge from rewarding a real gap — but several low
caps in one section can put the gate out of reach for a book that is
otherwise fine.

Sanity-check before you ship the pack: **if every cap in your section
fired at once, what would the pillar average be, and is it above 7.0?**
Four dimensions capping at 5/5/6/6 average 5.5, so the loop cannot exit
until at least two of those caps stop firing. That is a correct and
useful demand *if* each cap fires only on a genuine defect. A cap an
ordinary competent book trips by accident is mis-set: raise the number
or narrow the trigger — do not delete the cap.

---

## Frontmatter

Paste this into `<name>.md` first, starting at the `---` line. It is JSON
between two `---` lines, not a `##` section — do not add a
`## Frontmatter` heading to your pack.

```
---
{
  "name": "<must match the filename stem>",
  "label": "<human-readable; feeds NOVEL-GENRE at export>",
  "role": ["primary"],
  "pillar_label": "<names the rubric category, e.g. 'Relationship Architecture'>",
  "weights": {"pillar": 40, "character": 30, "structure": 20, "craft": 10},
  "beat_system": "save-the-cat",
  "content_register": {},
  "conflicts_with": [],
  "shape": {
    "chapters": [22, 26],
    "words": [80000, 95000],
    "chapter_words": 3200,
    "pov_default": "third limited past"
  },
  "artifacts": []
}
---
```

`name` must be lowercase letters, digits, and hyphens only, starting
with a letter or digit — `cozy-mystery`, not `Cozy_Mystery` — and must
match the filename stem exactly. Both rules are enforced, so rename the
file and the `name` field together.

`weights` must be integers summing to 100. The four categories it
divides are:

- **pillar** — your own `## Pillar Dimensions`.
- **character** — `character_depth`, `character_distinctiveness`,
  `character_secrets`.
- **structure** — `outline_completeness`, `foreshadowing_balance`.
- **craft** — `internal_consistency`, `voice_clarity`, `canon_coverage`.

Weights set each category's share of `overall_score` and nothing else —
the pillar bar is a separate, independent gate, so lowering `pillar`
makes the pillar no easier to clear (see `## Calibration` above).
Start from 40/30/20/10 and move at most 10-15 points.

`content_register` declares intensity axes and their levels —
`{"heat": "explicit"}`, `{"violence": "off-page"}` — and a declared level
becomes a Genre Contract promise the book must keep. `artifacts` names extra
project files this genre requires; describe each under `## Artifacts`.

## Framing

Terms and personas the rubrics substitute wherever they refer to genre, the
central system, or comparable authors. Use these exact keys.

- genre_noun — "<e.g. 'fantasy novel'>"
- pillar_noun — "<what the prose calls the central system, e.g. 'magic system'>"
- comps — <4-6 authors a genre reader would compare this to>
- seed_persona — <one sentence: who is generating concepts>
- reader_persona — <one sentence: the Genre Reader panel persona>
- writer_persona — <one sentence: the Writer panel persona>

`pillar_noun` is a **bare noun phrase with no leading article** —
`magic system`, not `the magic system`. The rubric prose supplies its own
article around the substitution, so a leading `the` reads as "the the
magic system".

## Pillar Dimensions

Three to six scored dimensions. Each bullet MUST read `- key — criteria`
with an em dash; the validator extracts keys from that shape. Keys must not
collide with the base dimensions (`character_depth`,
`character_distinctiveness`, `character_secrets`, `outline_completeness`,
`foreshadowing_balance`, `internal_consistency`, `voice_clarity`,
`canon_coverage`).

Mind the bullet shape here. The parser reads every **unindented** bullet
in this section whose first word is a bare lowercase identifier —
`- some_key <dash> ...` — as a dimension declaration (or, with the wrong
dash, a malformed one), so a stray prose bullet such as
`- write carefully, judges score 0-10` becomes a dimension key and can
trip the validator. Everything else is safe and welcome: `###`
subsections of supporting prose above the dimension list, bullets
indented by two spaces or more, and bullets whose first word is
capitalized. `fantasy.md` uses all three — two `###` subsections of laws
and measures, full of indented and capitalized prose bullets, sit above
its `### Scored dimensions` list.

Write real rubric criteria, not labels. A judge scores 0-10 against these.
Give each one a concrete test with a number attached, so two judges
reading the same documents land within a point of each other — and read
`## Calibration` above before you set those numbers.

- example_dim — What excellent looks like, what a gap looks like, and one
  concrete test the judge can apply.

## Genre Contract

Binary, checkable promises — not 0-10 scores. A breach caps the score.
`foundation.md` checks these against the outline; `full-novel.md` and
`novel-review` check them against the manuscript.

- <e.g. "The central relationship resolves HEA or HFN.">

## World Sections

Required headings for `world.md`, one per line, in order. Give each one a
`###` body below the list saying what belongs under it — the foundation
agent builds `world.md` from these, and a bare heading tells it nothing.

## Cast Requirements

The roster the foundation loop must build, with the depth each role needs.

## Plot Architecture

Act-by-act shape. Omit this section entirely to inherit the base structure.

## Canon Categories

Categories for `canon.md`. One `###` heading per category, with two or
three example entries as bullets beneath it — each a short, falsifiable
statement followed by its source in parentheses (`world.md`,
`characters.md`, `outline.md`, or `ch_NN`). `novel-seed` renders each
`###` heading here as a `##` section of the project's `canon.md` and the
bullets as its commented-out examples, so the headings must be usable as
section names on their own.

### <Category, e.g. Geography>
- <e.g. "Vael is 12 days' ride north of Tasren. (world.md)">
- <e.g. "The River Kell flows south through Tasren to the sea. (ch_02)">

Most genres want at least Geography, Timeline, Character Facts, Cultural,
and Established In-Story, plus whatever the pillar needs its own category
for (magic system rules, clues and alibis, the relationship's beats).

## Artifacts

One subsection per file named in `artifacts:` — its template, which phase
fills it, and what the rubric checks about it.

## Drafting Rules

Appended to the base 24 in `drafting-rules.md`. Number from 25. May include
a genre-specific banned-phrase list.

## Seed Prompt

What `novel-seed` reads to generate ten concepts. Four parts, in this
order:

1. **The persona block**, introduced by exactly
   `Persona (adopt while generating):` — second person, present tense,
   naming what this genre's concepts must never be.
2. **The required concept fields**, introduced by the sentence
   `Required concept fields (these <genre> fields and phrasings replace
   the neutral scaffold's versions of the same fields):`. That sentence
   is load-bearing — `novel-seed` relies on it to know your fields
   override the neutral scaffold's, so keep the wording and swap only
   `<genre>`. Under it, one block per field: an ALL-CAPS name, a colon,
   and what it must contain. Every pack keeps WORLD, TENSION, THEME, and
   WHY IT'S NOT GENERIC; add or rename the rest for the genre (fantasy
   adds MAGIC/COST, general adds STAKES and WHEN). Every scored pillar
   dimension should have a field feeding it.
3. **The diversity list**, introduced by
   `Aim for DIVERSITY across the ten concepts:` — the axes the ten must
   spread across, so the batch isn't ten variations on one idea.
4. **The DO-NOT list**, introduced by `DO NOT generate:` — this genre's
   exhausted premises, each stated concretely enough to recognize on
   sight.

```
Persona (adopt while generating):

You are <who is generating: the genre's range, what they know>. You
generate novel concepts that are SPECIFIC, SURPRISING, and
STRUCTURALLY SOUND. You never propose <this genre's default cliché>.

Required concept fields (these <genre> fields and phrasings
replace the neutral scaffold's versions of the same fields):

WORLD: <what makes this world specific — make it SENSORY>
<PILLAR FIELD>: <the field this genre's pillar needs — MAGIC/COST,
  STAKES, THE CRIME, whatever your pillar dimensions score>
TENSION: <the central conflict; both PERSONAL and larger, and the
  two in tension with each other>
THEME: <a genuine question with no easy answer — not a message>
WHY IT'S NOT GENERIC: <one sentence>

Aim for DIVERSITY across the ten concepts:
  - <axis: setting, structure, scale, protagonist age, ...>
  - <axis>
  - Mix of tones: <the tones this genre supports>

DO NOT generate:
  - <this genre's most exhausted premise>
  - <the next one>
```
