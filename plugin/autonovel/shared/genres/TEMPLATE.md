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
  Its `## Genre Contract` is NOT ignored — every loaded pack's contract is
  checked. So if your pack declares `["primary", "secondary"]`, each promise
  must be true in both slots. "The relationship is the main plot" is false in
  a romantasy; scope it ("where this pack is the primary...") or write the
  promise so it holds either way.
- **modifier** — an orthogonal axis (age category, heat level, tone). Only
  its Framing, Genre Contract, Drafting Rules, and `content_register` are
  read. It may not declare `weights`, `pillar_label`, `beat_system`,
  `shape`, or a Pillar Dimensions section. Its `## Framing` should supply
  only `comps` and the three personas — `genre_noun` and `pillar_noun`
  belong to the primary, since a YA fantasy is still a fantasy novel with
  whatever central system fantasy has. Its `## Genre Contract` is checked
  like every other pack's, so scope each promise to what the modifier
  actually governs, the same way a secondary must.
  A modifier's `artifacts` are **dropped** by the resolver: artifacts are
  per-book deliverables the genre owns, and an orthogonal axis should not
  spawn project files. A dual-role pack therefore gets its artifact as a
  primary and not as a modifier — scope any rule that references it.

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

Check the **partial-fire** case, not the all-fire one. Asking "if every cap
fired, is the average still above 7.0?" is the obvious test and it is the
wrong one — a pack can pass it and still be unreachable, because real books
trip one or two caps, not all of them.

Scores are integers and the gate is strict, so with N dimensions the pillar
sum must be **at least 7N + 1**. With k caps firing at value C, the
remaining N − k dimensions must average `(7N + 1 − kC) / (N − k)`. Compute
that for k = 1 and k = 2 and read the answer against this rubric's own
calibration, which reserves 9+ for work where the judge "genuinely
struggled to find flaws":

| Pack shape | 1 cap fires | 2 caps fire |
|---|---|---|
| 4 dimensions, caps at 5 | rest average 8.00 | rest average **9.50** — needs a 10 and a 9 |
| 5 dimensions, caps at 6 | rest average 7.50 | rest average 8.00 |

**Reject any design where two caps firing requires a 9.** One cap should
leave the gate clearly reachable; two should be hard but possible; three
should block, because three real defects ought to.

**Dimension count is the lever, not cap severity.** This is the least
obvious thing on this page. Going from four dimensions to five is what
makes 6-caps safe — at four dimensions, two 6-caps still force `9, 8` from
the remainder. If your arithmetic comes out unreachable, adding a fifth
dimension usually fixes it more cleanly than softening a cap, because it
keeps every criterion honest.

For a failure so severe that any book committing it should be blocked
outright, do not reach for a punishing cap. Put it in `## Genre Contract`
instead: a contract breach caps `overall_score` at 6 and never touches
`pillar_score`, so it stops the loop without making the pillar gate
arithmetically unreachable. Then let the graded version of the same fault
keep an ordinary cap, and say in the criteria that the two are not to be
double-counted.

A cap an ordinary competent book trips by accident is mis-set: raise the
number or narrow the trigger — do not delete the cap.

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

**A modifier uses a shorter block.** Pasting the one above into a modifier
produces four validator errors, because a modifier may not declare
`pillar_label`, `weights`, `beat_system`, or `shape`. Use this instead:

```
---
{
  "name": "<must match the filename stem>",
  "label": "<human-readable>",
  "role": ["modifier"],
  "content_register": {},
  "conflicts_with": [],
  "artifacts": []
}
---
```

`name` must be lowercase letters, digits, and hyphens only, starting
with a letter or digit — `cozy-mystery`, not `Cozy_Mystery` — and must
match the filename stem exactly. Both rules are enforced, so rename the
file and the `name` field together.

`shape` is required on a primary and must carry all four keys — the
outline step reads `chapters` and `words`, and the drafting step reads
`chapter_words`, so a primary without them leaves those instructions
pointing at nothing. A modifier needs no `shape` at all.

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

`artifacts` names extra project files this genre requires; describe each
under `## Artifacts`.

### content_register

Declares how intense this genre's content is, on three axes with fixed
vocabularies. Anything else is rejected at authoring time.

| Axis | Levels, least to most intense |
|---|---|
| `heat` | `none` · `closed-door` · `warm` · `steamy` · `explicit` |
| `violence` | `none` · `off-page` · `moderate` · `graphic` |
| `language` | `none` · `mild` · `strong` · `unrestricted` |

Declare only the axes your genre actually constrains. A pack that says
nothing about violence should omit `violence` rather than set it to `none` —
omitting leaves it open, while `none` promises the book contains none.

**`{}` is the right answer for most genre packs, not a placeholder.**
Romance spans closed-door to explicit and mystery spans cozy to hardboiled;
neither genre constrains any axis, so both ship `{}` and leave all three
open for a modifier to set. Declaring a level here forces it on every book
in the genre. If you are reaching for one, ask whether you are describing
the genre or describing one book in it.

**A level is always a ceiling. It is also a floor only when your
`## Genre Contract` says so.**

That distinction matters and is easy to get wrong. `erotica` declares
`heat: explicit` *and* contracts that "the declared heat level is
delivered" — so for that pack the level is a target in both directions, and
a book that fades to black has breached. `cozy` declares
`violence: off-page` with no matching contract clause, so it bounds the
book without promising violence occurs at all: a cozy mystery has a body,
a cozy fantasy may have none, and both satisfy it.

Without that split, a tone or age modifier is pushed to omit exactly the
axes it exists to bound, because `violence: off-page` read as a delivery
promise would falsely assert that violence happens. If your pack means the
level as a target rather than a bound, say so in `## Genre Contract` —
otherwise it bounds only.

**When packs disagree, the most restrictive level wins.** A `ya` modifier
declaring `heat: warm` over a romance primary declaring `heat: steamy`
resolves to `warm`, and `resolve_genre.py` reports which pack it came from
in `content_register_sources`. This is the normal case, not an error — it is
why modifiers exist. Restrictive is the safe direction: under-delivering on
heat disappoints a reader, while over-delivering can break an age-category
promise.

That resolution is only possible because the vocabulary is closed. If one
pack wrote `closed-door` and another `fade to black`, the two would be
unorderable and read as a genuine disagreement, and every stack combining
them would fail to resolve. Use the words in the table even when a better
one exists for your genre — say what you mean about nuance in
`## Genre Contract`, where prose belongs.

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

The shape most likely to catch you out is a **definitional list** — terms
of art you want to define before scoring against them. Written the natural
way, `- fair play — every clue is on the page`, each entry is
indistinguishable from a dimension declaration and every term becomes a
phantom key. Either indent those bullets two spaces, or write them as
bold-prefixed prose the way `mystery.md` and `romance.md` do.

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

`beat_system` and this section do different jobs and can both be declared.
`beat_system` names the **beat vocabulary** the outline labels chapters with
and the chapter rubric scores against. This section sets the **act shape and
percentage marks**. Declaring one does not replace the other: mystery ships
`beat_system: save-the-cat` alongside its own act structure, and the outline
uses Save the Cat beat names at the act marks stated here.

**Percentage marks stated in this section win** over the beat system's own
canonical marks. A thriller declaring `save-the-cat` alongside a Plot
Architecture that pulls the Catalyst to 5% gets a Catalyst at 5%, not at
Save the Cat's usual ~11% — the beat *names* still come from `beat_system`,
but where they fall comes from here. That is the point of declaring both.

**If you declare a `beat_system` other than `save-the-cat`, you must state
its beats somewhere in the pack.** The recommended home is a `###`
subsection above your scored dimensions inside `## Pillar Dimensions`, which
is what `romance.md` does for Romancing the Beat — it ships no
`## Plot Architecture` at all. Use this section for act shape and marks; use
that subsection to enumerate an unfamiliar beat vocabulary.
Nothing else in the pipeline knows them — `layer-guides.md` tells the
outliner to place "the beats of the pack's `beat_system` at their stated
percentage marks", and if your pack does not state them, there is nothing to
place. Name each beat and its percentage mark, the way Save the Cat is
enumerated in `CRAFT.md`.

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

One subsection per file named in `artifacts:`. An artifact has a lifecycle
across four phases, not one, and your subsection should say what happens in
each:

- **seed** creates the file from the template you give here
- **foundation** fills it, and re-checks it whenever a layer it draws on changes
- **draft** and **revise/review** update it as the manuscript moves

Give the template itself (a markdown table's columns, or the headings),
state which pillar dimension scores it, and say what a judge checks. An
artifact nothing scores is a file the pipeline will quietly stop maintaining.

## Drafting Rules

Appended to the base 24 in `drafting-rules.md`. Number from 25 — the
numbering is per-pack, not a global sequence, so a stack of three packs
will produce three rules numbered 25. The drafter reads every loaded
pack's section, so the collision is expected and harmless. May include
a genre-specific banned-phrase list.

## Seed Prompt

**Field order is load-bearing.** `novel-seed` presents each generated concept
as TITLE + HOOK + *the first required field the neutral scaffold does not
already define*. The scaffold defines WORLD, TENSION, THEME, and WHY IT'S NOT
GENERIC — so whatever you list immediately after WORLD becomes the single
field a user compares ten concepts by. Put your genre's discriminating field
there: `MAGIC/COST` for fantasy, `STAKES` for general fiction, `THE CRIME`
for mystery. A field like WHEN or SETTING in that slot makes the user choose
between ten premises on their least distinguishing attribute.

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
