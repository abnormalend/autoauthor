# Form Parameterization, and autonovel → autoauthor — Design

Status: draft, not yet planned or implemented.
Predecessor: `2026-08-12-genre-parameterization-design.md`, whose pack
system this extends rather than replaces.

## Goal

Make the pipeline able to produce works other than a 80,000-word novel —
a 5,000-word short story, a novella, a serial, a collection — without
forking the repo per output. Then fold `autoanthology` back in and rename
the product to match what it does.

## Problem

Three separate problems that look like one.

**1. Length is not expressible.** `shape.words` can say `[4000, 6000]`
today, and it will not work. A 5,000-word story run through
`novel-foundation` builds five planning layers — a world bible, a
chapter-by-chapter outline with MICE threads, a foreshadowing ledger,
`MYSTERY.md`, `canon.md` — and gates them at `overall > 7.5`. The
planning outweighs the story several times over. The gate is deliberately
the highest bar in the pipeline because a weak plan costs more later;
that reasoning is novel economics. At 5,000 words a weak plan costs an
afternoon.

**2. The base dimensions are novel-scale and hardcoded.**
`outline_completeness` and `foreshadowing_balance` assume chapter-by-chapter
architecture. `character_depth` wants a causally linked wound/want/need/lie
chain. `canon_coverage` assumes a canon file. A short story plants and pays
within a page and often gives one character at one moment. These live in
`rubrics/foundation.md` exactly as the fantasy lore dimensions did before
the genre work — the same hardcoding, one level down.

**3. The genre packs are novel-scale too.** Fantasy wants "at least 3
societal implications explored with specificity". Romance wants the full
four-phase Romancing the Beat curve across 26–32 chapters. Romantasy wants
a 22-row braid ledger. Applying these to a 5,000-word story reproduces
exactly the defect that justified `paranormal-romance`: **wrong-scale
criteria penalize a work for being correctly what it is.**

`autoanthology` already discovered the shape of the fix without naming it.
Its fantasy pack says: *"At short length the concept must be graspable in a
paragraph: a 5,000-word story cannot spend 800 words orienting the reader in
a world."* That is a length-scoped reading of a genre criterion, hand-written
into a forked file. This spec formalizes it.

## The thing that must not be conflated

"Form" as a word covers two different axes, and collapsing them repeats the
mistake of trying to make anthology a modifier.

**Scale** — how long one complete work is. Flash through epic. Changes which
base dimensions apply, how genre criteria are read, the foundation layer set,
and the gate. Same phase graph: seed → foundation → draft → revise → review →
export. **This is a pack.**

**Structure** — how many complete works there are and how they relate.
Standalone, collection, series, serial. Changes the state schema and the
phase graph itself. `autoanthology`'s state carries `stories: []` where
autonovel carries scalar `chapters_drafted`/`chapters_total`, and it has a
`collection-pass.md` rubric with no counterpart here. No pack can change a
state schema or add a phase. **This is a pipeline selector, not a pack.**

The test, mirroring the genre work's: *does it change which dimensions
apply (scale → pack) or does it change the phase graph (structure →
pipeline)?*

## Decisions

- `form` is a fourth pack type, resolved alongside genre/secondary/modifiers.
- `structure` is a `state.json` field that selects the phase graph. Not a pack.
- Genre packs stay length-agnostic by default and gain optional length-band
  sections. Absence degrades gracefully to today's behavior.
- Form owns total length; genre keeps chapter granularity. This resolves an
  existing conflict and fixes a bug (below).
- Rename to `autoauthor` in the same release, because the installed base is
  effectively zero and two migrations is worse than one.
- `autoanthology` is absorbed as `structure: collection`, not kept as a fork.

## The forms

Bands are the unit genre packs write against, so that 15 packs do not each
need six length-scoped sections.

| Form | Words | Band | Ship? | Anchor |
|---|---|---|---|---|
| *drabble / micro* | 100–1,000 | — | no | — |
| `flash` | < 1,000 | compressed | defer | *Sticks* |
| **`short-story`** | 1,000–7,500 | compressed | **v1** | *The Lottery* (~3,800) |
| `novelette` | 7,500–17,500 | intermediate | no | *The Bloody Chamber* |
| **`novella`** | 17,500–40,000 | intermediate | **v1** | *Binti*, *A Christmas Carol* |
| **`novel`** | 40,000–120,000 | extended | **v1** | most of the market |
| `epic` | 120,000+ | extended | defer | *The Way of Kings* (~387k) |

Boundaries follow the SFWA/Nebula categories, which Hugo also uses — what
markets and submission guidelines already assume. The 40,000 novel floor is
the surprising one; it is genuinely where "novel" starts for awards purposes
even though commercial fiction rarely sells below 70,000.

**Ship three: `short-story`, `novella`, `novel`.** These are the lengths with
real markets and genuinely different apparatus. The other three fail the
same test the genre work used for hybrids — *name something that
distinguishes this from its neighbour, or do not give it a file.*

- **`novelette` is an awards category, not a market category.** Nothing is
  acquired, sold, or browsed as a novelette; the bucket exists so the Hugos
  have something between short story and novella. It collapses into
  `short-story` or `novella` depending on which apparatus it needs, and it
  shares the `intermediate` band with `novella` regardless. Not a form.
- **`flash` sits below the useful floor of a five-phase pipeline.** A
  900-word story costs more to run through seed → foundation → draft →
  revise → review → export than to write. Deferred, not rejected: if the
  compressed band proves out, a two-phase flash path might be worth it.
- **`epic` is the likeliest of the three to survive the test.** Multi-POV
  and subplot braiding are real structural facts a 90,000-word novel does
  not have, and they are nameable as dimensions. Deferred until someone
  writes them down; until then it is `novel` with a wider `words` range.

`novella` is the strongest argument for this whole axis after `short-story`.
It has become a real commercial category in the last decade — Tordotcom built
an imprint on it, and it is a native ebook length — and it is the length most
poorly served by a novel pipeline: too long to wing, too short to earn a
world bible and a foreshadowing ledger.

`extended` is the implicit default: a genre pack that declares no band
sections behaves exactly as it does today. The minimum authoring cost per
pack is therefore **one** new section covering compressed length, with
intermediate optional and inheriting from whichever neighbour is present.

### Forms deliberately excluded

- **Screenplay, teleplay, graphic novel script** — different output medium,
  different craft rubric, different notion of voice. `voice.md` and
  `CRAFT.md` assume prose. Out of scope; would be a sibling product.
- **Poetry collection** — same reason, more so.
- **Interactive/branching** — changes the outline from a sequence to a graph.
  Out of scope.
- **Nonfiction, memoir** — the whole rubric assumes invented material and
  the genre contract assumes genre promises. Out of scope.

## Form pack anatomy

Same file format as a genre pack — JSON frontmatter, `##` prose sections,
parsed by the existing `genre_pack.py`. Lives in `shared/forms/`.

```
---
{
  "name": "short-story",
  "label": "Short Story",
  "band": "compressed",
  "words": [1000, 7500],
  "target_words": 5000,
  "gate": {"overall": 6.5, "pillar": 6.0},
  "layers": ["premise", "characters", "voice"],
  "base_dimensions": {
    "drop": ["foreshadowing_balance", "canon_coverage"],
    "add": ["compression", "single_effect"]
  },
  "weights": {"pillar": 30, "character": 30, "structure": 15, "craft": 25}
}
---
```

### Fields

- `band` — `compressed` | `intermediate` | `extended`. Selects which
  genre-pack section is read.
- `words` / `target_words` — total length. **Form owns this, not genre.**
- `gate` — overrides the 7.5/7.0 foundation bar. A compressed form should
  gate lower, because there is less plan to be right about and the drafting
  loop is cheap enough to absorb error.
- `layers` — which foundation layers get built. `short-story` needs no
  `world.md`, no `MYSTERY.md`, no foreshadowing ledger.
- `base_dimensions.drop` / `.add` — the base dimensions are no longer a
  fixed list. Same treatment the pillar dimensions got.
- `weights` — optional override. A compressed form weights craft up and
  structure down; there is less structure and every sentence is load-bearing.
  Must still sum to 100; validated like a genre pack's.

### Sections

- `## Framing` — `form_noun` ("short story"), personas scoped to the form.
  A short-story reader is not a novel reader.
- `## Form Contract` — promises about the form itself, checked like a genre
  contract. For `short-story`: the story has one central effect; it does not
  end on the first beat of a novel it is not going to write.
- `## Drafting Rules` — numbered from 25 like every other pack.
- `## Foundation Guidance` — what each declared layer means at this length.

## Genre pack interaction

The hard part, and the part most likely to be got wrong.

A genre pack gains optional sections:

```
## At Compressed Length

`magic_system` — one rule, stated and paid. Do not score societal
implications; a 5,000-word story that explains three is a worse story.
Judge whether the single rule constrains the one decision the story turns on.

`world_history` — not scored at this band.
```

Resolution rules:

1. If the form's `band` is `extended`, or the pack declares no band section,
   the pack's `## Pillar Dimensions` criteria apply unchanged. **Today's
   behavior is the default and needs no edits to ship.**
2. If a band section exists, its per-dimension text **replaces** the criteria
   for the dimensions it names and leaves the rest alone.
3. A dimension the band section marks "not scored at this band" is dropped
   from the pillar entirely — and therefore from `pillar_score`'s divisor.
4. `intermediate` falls back to `compressed` if absent, then to the default.

Rule 3 has a consequence the plan must handle: **dropping dimensions changes
N, and every pack's cap arithmetic is calibrated against its own N.** Fantasy
at compressed length might score 2 of 5 dimensions, where the sum needed is
7(2)+1 = 15 and a single 6-cap leaves the other needing a 9. The form pack's
`gate.pillar` override is the release valve, but band sections must restate
caps for the reduced set. `validate_pack` must compute the arithmetic per
band and reject a design that is unreachable — this is checkable statically
and should not be left to authoring discipline.

## Shape ownership

Currently genre packs own all of `shape`. That conflicts with form owning
length, and the conflict is worth resolving rather than papering over.

**After:** form owns `words` and `target_words`. Genre keeps `chapter_words`
and `pov_default` — a thriller's 1,900-word chapters against a fantasy's
3,200 is a genuine genre fact, not a length fact. `chapters` is **derived**
(`target_words / chapter_words`), not declared.

This fixes a bug found during the genre-pack work: several packs' declared
`chapters × chapter_words` ranges only partially intersect their declared
`words` range. `mystery` spans 70,400–83,200 against a declared
80,000–95,000, so most of its chapter range cannot reach its own word floor.
Deriving `chapters` makes the inconsistency unrepresentable.

Migration: each genre pack's existing `shape.words` becomes the `novel`
form's default and is deleted from the pack.

## The structure axis

A `state.json` field, not a pack. Selects which skills run.

| Value | Unit | Phase graph delta |
|---|---|---|
| `standalone` | one work | today's pipeline; the default |
| `collection` | N works + a collection pass | per-story subdirectories; adds a cross-story variety phase before export |
| `series` | N works, shared continuity | adds a series bible above per-volume foundation; per-volume arcs plus a series arc |
| `serial` | one work, incremental release | no global revision plateau; per-episode publish; open-ended outline |

`collection` is `autoanthology`'s job and absorbs it. Its story list, its
`collection-pass.md` rubric, and its running-order logic port over largely
intact — they are genuinely its own contribution and are not duplicated here.

`series` is worth including now rather than later because this session
surfaced the need three times: `paranormal-romance` had to encode
interconnected-standalone convention as a contract promise because `shape`
could not express series position; `romantasy`'s contract carves out
"a series volume may leave the world plot open, never the couple"; and
`fantasy` has no way to say a trilogy's middle volume should not resolve.

`serial` is specified but should ship last; it is the only value that breaks
the score-plateau model the whole pipeline rests on.

## autonovel → autoauthor

Once the product does flash through epic, standalone through collection,
"autonovel" is wrong on the tin, and every skill named `novel-*` misdescribes
itself.

### Rename inventory

- `plugin.json` name; `marketplace.json` name, id, and plugin entry
- 8 skills: `novel` → `status`, `novel-seed` → `seed`, `novel-foundation` →
  `foundation`, and so on. The `novel-` prefix was always redundant under a
  plugin namespace — `/autoauthor:draft` reads better than
  `/autoauthor:novel-draft`.
- Every cross-reference between skills (7 judge-dispatch sites, the router's
  phase table, `${CLAUDE_PLUGIN_ROOT}` paths in references)
- `state.json`: `novel_score` → `work_score`; add `form`, `structure`
- README, PIPELINE.md, both spec/plan directories
- The GitHub repo (optional — redirects handle it)
- `installed_plugins.json` key, which means users reinstall rather than update

### Sequencing

Bundle the rename into the same release as the form axis. The installed base
is one user with no in-flight projects, so the migration cost is near zero
today and grows monotonically. Two migrations is strictly worse than one.

The router's existing migration step is the model: detect a pre-rename
project, explain that its scores came from the novel-only rubric, migrate on
confirmation.

## Validation

Extends `validate_genre_pack.py` and `genre_pack.py`:

- Form packs validate against a form schema: `band` in the closed set,
  `words` ordered and non-empty, `gate` values in 0–10, `layers` naming known
  layers, `base_dimensions.drop` naming dimensions that exist,
  `base_dimensions.add` not colliding with a reserved key.
- **Band arithmetic**: for each genre pack × each band, compute the surviving
  dimension count and the k=1/k=2 cap arithmetic, and reject any combination
  that requires a 9. This is the single highest-value new check — it is the
  defect class that has bitten twice already (`fantasy`'s two 4-caps, and the
  `pillar_score` dilution three subagents found independently).
- A genre pack's band section may only name dimensions it actually declares.
- `resolve_genre.py` → `resolve_packs.py`, returning `form` alongside the
  existing keys, and reporting the resolved band.

## Testing

- Form pack parse/validate, mirroring `test_genre_pack.py`.
- Resolution: form + genre + secondary + modifiers, and the precedence rules
  above, including band fallback (`intermediate` → `compressed` → default).
- **Band arithmetic across the full matrix** — every shipped genre pack ×
  every band, asserting reachability. Cheap, static, and the guard against
  the recurring defect.
- Derived `chapters` never contradicts declared `words`.
- A regression pin that a genre pack with no band sections resolves to
  byte-identical criteria at `extended`, so the default path cannot drift.
- Rename: a migration test on a pre-rename `state.json`.

## Implementation phasing

1. **Form pack type**, `shared/forms/`, parser, validator, resolver. No
   behavior change: ship only `novel` with today's values and prove nothing
   moves.
2. **Base dimension parameterization** — lift the base dimensions out of
   `rubrics/foundation.md` the way the pillar dimensions were lifted. This is
   the largest single piece and the one with the most silent-wrong risk.
3. **`short-story` and `novella` forms** — the full v1 set alongside `novel`
   from phase 1 — plus compressed-band sections on the genre packs and
   intermediate-band sections where compressed is too severe. Band
   arithmetic tests land here.
4. **Rename to autoauthor**, with migration.
5. **`structure: collection`**, absorbing autoanthology.
6. **`structure: series`**.
7. **`structure: serial`**, last, or dropped.

Phases 1–2 are behavior-preserving and should be verifiable by an A/B
against the current rubric, the way the fantasy port was.

## Out of scope

- Screenplay, poetry, interactive, nonfiction forms.
- Any change to the export pipeline beyond what `collection` needs.
- Retiring the `autoanthology` repo — it stays until `collection` ships and
  is verified end to end.
- Per-form typesetting; a short story and a novel can share LaTeX for now.

## Open questions

1. Should `gate` be a form override, or computed from the surviving
   dimension count? The latter is more principled and harder to reason
   about, and it changes the shape of phases 1 and 2 — worth settling before
   planning.
2. Does `series` need a form-level or structure-level home for the series
   bible? It is a planning layer above foundation, which no current phase
   owns.

**Settled** (were open in the first draft):

- *Does `flash` earn a form?* No — below the useful floor of a five-phase
  pipeline. Deferred, with a two-phase path as the only way it comes back.
- *Do `epic` and `novel` differ enough?* Not yet demonstrated. `epic` stays
  merged into `novel` until multi-POV and subplot braiding are written as
  actual dimensions rather than asserted as a difference.
- *Does `novelette` belong?* No — an awards bucket with no market behind it,
  sharing a band with `novella` anyway.
