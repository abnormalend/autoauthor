# Genre Parameterization — Design

**Date:** 2026-08-12
**Status:** Approved

## Goal

Move every genre-specific assumption out of the autonovel plugin's base files
and into swappable **genre packs**, so the pipeline can write a romance, a
thriller, a literary novel, or an erotic paranormal romance with the same
craft machinery it currently applies only to fantasy.

## Problem

An audit of `plugin/autonovel/` found fantasy hardcoded into 20 files. The
damage is not cosmetic:

- **The foundation gate is unpassable for non-fantasy.** `novel-foundation`
  exits on `foundation_score > 7.5 AND lore_score > 7.0`. The foundation
  rubric scores a mandatory `magic_system` dimension and weights
  lore/worldbuilding at 40%. A contemporary novel scores 0 there and burns
  all 15 iterations against a gate it cannot reach.
- **Every judge is told it is reading fantasy** — `foundation.md`,
  `chapter.md`, `full-novel.md`, `adversarial-edit.md`, and `reader-panel.md`
  all name the genre, and the reader panel's personas compare everything to
  Sanderson, Le Guin, Jemisin, Rothfuss, and Hobb.
- **Templates ship fantasy structure.** `world.md` has `## Magic System` and
  `## Bestiary`; `canon.md`'s worked examples are an invented epic fantasy
  (Vael, Tasren, Kael, "all magic costs blood or memory").
- **Seed generation has no non-fantasy path.** `seed-prompts.md` is a fantasy
  novelist persona producing a required `MAGIC/COST` field, and
  `novel-seed/SKILL.md` validates that field's presence before saving.

This is the same class of leak as the **De-Bells rule** in the original plan —
content from the first novel bleeding into the machinery — one abstraction
level up. Two second-order leaks surfaced during design and are fixed here:
the act-by-act plot architecture in `layer-guides.md` is *mystery* content,
not fantasy content, and the hardcoded book shape (22–26 chapters, ~80,000
words, ~3,200-word chapters, third-limited past) is epic-fantasy convention
presented as universal.

## Decisions (from brainstorming)

| Question | Decision |
|---|---|
| Pack scope | Full parameterization: vocabulary and framing, scored rubric dimensions and weights, required document sections and plot architecture, drafting rules, and seed prompts. |
| Mechanism | **Pack-as-context-document.** Base files become genre-neutral and carry explicit hooks; skills and judges read base + pack together. No render step, no build artifacts. Rejected: token substitution (too weak for structural change) and file-level overlay (duplicates ~85%-neutral rubrics per genre). |
| Hybrids | Primary + secondary + modifiers. Primary owns structure and weights; secondary contributes additively; modifiers carry orthogonal axes and stack safely. |
| Pack location | Plugin ships the canonical set at `shared/genres/`; a project may override with its own `genres/` directory. Project wins. |
| No genre declared | Resolves to a genre-neutral `general` pack, not to fantasy. |
| Roles | `role` is a **set**, not a scalar. Most packs are multi-role: erotica is `[primary, modifier]`, romance and mystery are `[primary, secondary]`. |

## Pack anatomy

A pack is one markdown file: `shared/genres/<name>.md`. YAML frontmatter
holds structured data a validator checks; prose sections hold everything a
model reads.

```yaml
---
name: fantasy
label: Fantasy
role: [primary, secondary]
pillar_label: Lore & Worldbuilding
weights: { pillar: 40, character: 30, structure: 20, craft: 10 }
beat_system: save-the-cat
content_register: {}
conflicts_with: []
shape:
  chapters: [22, 26]
  words: [80000, 95000]
  chapter_words: 3200
  pov_default: third limited past
artifacts: []
---
```

### Frontmatter fields

| Field | Required for | Meaning |
|---|---|---|
| `name` | all | Must match the filename stem. |
| `label` | all | Human-readable; feeds `NOVEL-GENRE` at export. |
| `role` | all | Non-empty subset of `{primary, secondary, modifier}`. |
| `pillar_label` | primary | Names the rubric's genre category ("Relationship Architecture", "Plot Machinery & Procedure"). |
| `weights` | primary | Category weights; integers summing to 100. |
| `beat_system` | primary | Names the beat vocabulary the outline and chapter rubric check against. Default `save-the-cat`. |
| `content_register` | optional | Declared intensity axes with levels, e.g. `{heat: explicit}`, `{violence: off-page}`. |
| `conflicts_with` | optional | Pack names that may not be loaded alongside this one. Enforced at load. |
| `shape` | primary | Chapter count range, word count range, per-chapter target, default POV/tense. |
| `artifacts` | optional | Extra project files this genre requires. |

### Sections

| Section | Purpose |
|---|---|
| `## Framing` | Terms and personas the rubrics substitute: `genre_noun`, `pillar_noun`, `comps`, `seed_persona`, `reader_persona`, `writer_persona`. |
| `## Pillar Dimensions` | The scored dimensions under this genre's pillar category, each with full rubric criteria. 3–6 dimensions. |
| `## Genre Contract` | Binary, checkable promises. Not 0–10 scores. |
| `## World Sections` | Required headings for `world.md`. |
| `## Cast Requirements` | The roster the foundation loop must build. |
| `## Plot Architecture` | Act-by-act shape. Omit to inherit the base Save the Cat structure. |
| `## Canon Categories` | Categories and example entries for `canon.md`. |
| `## Artifacts` | Template and owning phase for each file named in `artifacts:`. |
| `## Drafting Rules` | Appended to the base 24 in `drafting-rules.md`. May include a genre-specific banned-phrase list. |
| `## Seed Prompt` | Required concept fields, DO-NOT list, diversity requirements. |

Only `## Framing` and `## Pillar Dimensions` are required, and only for a
primary. A modifier needs neither. A minimal modifier is about 30 lines —
this matters, because "inject our own genre file" only works if writing one
isn't a project.

### Genre contracts

Some genre promises are pass/fail and no dimension score catches them. A
romance that ends in separation is a different book; a mystery whose solution
the reader could not have reached is a broken one. A breach **caps** the
score, reusing the existing pattern in `foundation.md` ("a single major
contradiction caps this at 6").

Contracts are checked twice, against different objects. `foundation.md`
checks them against the **plan** — does the outline's ending satisfy the
contract, does the clue ledger make the solution reachable — so a breach
surfaces before 80,000 words exist. `full-novel.md` and `novel-review` then
check them against the **manuscript**.

Examples:

- romance — the central relationship resolves HEA or HFN.
- mystery — every clue needed for the solution is on the page before the
  reveal; the reader could solve it.
- erotica — the declared heat level is delivered consistently; all
  participants are adult and established as such; consent is legible on the
  page.
- cozy — violence stays off-page.

## Roles and merge rules

Which parts of a pack are read depends on the role it is loaded in. One rule,
no per-section role tagging:

| Pack content | primary | secondary | modifier |
|---|---|---|---|
| `weights`, `pillar_label`, `beat_system`, `shape` | **owns** | ignored | ignored |
| `content_register`, `conflicts_with` | applies | applies | applies |
| `## Framing` | **owns** | contributes `genre_noun` to the framing text | additive overrides (comps, personas) |
| `## Pillar Dimensions` | applies | additive into the primary's pillar category | ignored |
| `## Genre Contract` | applies | additive | additive |
| `## World Sections`, `## Cast Requirements`, `## Canon Categories`, `## Artifacts` | applies | additive | ignored |
| `## Plot Architecture` | **owns** | ignored | ignored |
| `## Drafting Rules` | applies | additive | additive |
| `## Seed Prompt` | **owns** | additive fields and DO-NOT entries | additive DO-NOT entries only |

"Additive" means set union. On a genuine collision — two packs declaring the
same pillar dimension key — the primary wins and the validator warns.
Modifiers cannot touch weights or dimensions, which is why they stack safely
without reopening the weight-arithmetic problem that ruled out unrestricted
N-pack composition.

*Erotic Paranormal Romance* resolves as primary `fantasy`, secondary
`romance`, modifier `erotica`. The erotica pack's pillar dimensions and
weights are simply not read in that configuration.

## Resolution

`state.json` gains three fields:

```json
{
  "genre": "fantasy",
  "genre_secondary": null,
  "genre_modifiers": []
}
```

Resolution order for each name: the project's own `genres/<name>.md` first,
then `${CLAUDE_PLUGIN_ROOT}/shared/genres/<name>.md`. Project wins, so a
one-off pack for a single novel needs no plugin change.

Rather than restate search-and-merge rules in prose across six skills, a
single script owns it:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/resolve_genre.py"
```

Run from the project directory, it reads `state.json`, resolves and validates
every pack, enforces `conflicts_with`, and prints JSON to stdout:

```json
{
  "packs": [{"name": "fantasy", "role": "primary", "path": "/abs/path.md"}],
  "label": "Fantasy",
  "label_parts": ["Fantasy"],
  "pillar_label": "Lore & Worldbuilding",
  "weights": {"pillar": 40, "character": 30, "structure": 20, "craft": 10},
  "beat_system": "save-the-cat",
  "shape": {"chapters": [22, 26], "words": [80000, 95000],
            "chapter_words": 3200, "pov_default": "third limited past"},
  "content_register": {},
  "artifacts": []
}
```

Every skill calls it once and passes the resolved pack paths to its judge
subagents alongside the rubric path. Judges stay clean-room: packs are static
reference material, exactly like rubrics.

`label` is the primary pack's label; `label_parts` lists every loaded pack's
label in primary → secondary → modifier order. Hybrid genre names are not
auto-generated — "Erotic Paranormal Romance" is not reliably derivable from
three pack names — so `novel-export` offers the joined `label_parts` as the
default `NOVEL-GENRE` string and lets the user edit it.

Missing `genre` resolves to `general`. See Migration for why existing
projects must not take that default silently.

## Rubric output schema

Pillar dimensions vary by genre, so `foundation.md`'s flat JSON becomes
nested by category. Only `pillar` has genre-variable keys:

```json
{
  "pillar": { "<pack-defined dimension>": {"score": N, "gap": "...", "fix": "...", "note": "..."} },
  "character": { "character_depth": {...}, "character_distinctiveness": {...}, "character_secrets": {...} },
  "structure": { "outline_completeness": {...}, "foreshadowing_balance": {...} },
  "craft": { "internal_consistency": {...}, "voice_clarity": {...}, "canon_coverage": {...} },
  "genre_contract": {"violations": [], "note": "..."},
  "slop_in_planning_docs": {"found": [], "note": "..."},
  "contradictions_found": [],
  "overall_score": N,
  "pillar_score": N,
  "weakest_dimension": "...",
  "top_3_improvements": ["...", "...", "..."]
}
```

`overall_score`, `pillar_score`, and `weakest_dimension` are stable keys, so
`gen_brief.py`, `state.json`, and every gate keeps working against fixed
names. `lore_score` is renamed `pillar_score` throughout; the foundation gate
becomes `overall_score > 7.5 AND pillar_score > 7.0` and is now genre-relative.

## Base-file surgery

### New files

| Path | Purpose |
|---|---|
| `shared/genres/<name>.md` | The packs. |
| `shared/genres/TEMPLATE.md` | Annotated skeleton plus authoring guide. |
| `shared/scripts/resolve_genre.py` | Resolution, merge, and conflict enforcement. |
| `shared/scripts/validate_genre_pack.py` | Standalone pack validation. |

### Rubrics

| File | Change |
|---|---|
| `rubrics/foundation.md` | Neutralize all fantasy framing. Pillar dimensions and category weights come from the pack. Nested output schema. `lore_score` → `pillar_score`. Add genre-contract check. |
| `rubrics/chapter.md` | Framing from pack. `lore_integration` → `pillar_integration`, criteria pack-defined. Drop "published fantasy" and "any fantasy city". |
| `rubrics/full-novel.md` | Framing from pack. `world_consistency` → `pillar_consistency`. Add genre-contract verification with score cap on breach. |
| `rubrics/adversarial-edit.md` | One line (`:20`). |
| `rubrics/reader-panel.md` | Genre Reader and Writer personas, comps, and the question preamble all from pack `## Framing`. Editor and First Reader are already neutral. |
| `rubrics/manuscript-review.md` | Add genre-contract verification to the professor review. |

### Craft

| File | Change |
|---|---|
| `craft/CRAFT.md` | Move out to the fantasy pack: §3's "Sanderson's Three Laws of Magic" and the MAGICAL pillar, §6's Le Guin fantasy insight and "what the best fantasy prose does", §8's "Magic System" rubric summary. What remains — plot structure, character craft, foreshadowing, show-don't-tell, prose craft, the stability trap — is genuinely universal and stays. |
| `craft/ANTI-SLOP.md`, `craft/ANTI-PATTERNS.md` | No change. Already neutral. |

### Templates

| File | Change |
|---|---|
| `templates/world.md` | Headings rendered from the pack's `## World Sections` at project init. |
| `templates/canon.md` | Categories from the pack. Strip all Vael/Tasren/Kael/"blood or memory" examples; the pack supplies its own. |
| `templates/voice.md` | `:102` — "a spell's components" → neutral example. |
| `templates/state.json` | Add `genre`, `genre_secondary`, `genre_modifiers`. Rename `lore_score` → `pillar_score`. |

### Skills

| File | Change |
|---|---|
| `novel-foundation/references/layer-guides.md` | The heavy lift. `world.md` sections, cast roster, canon categories, and book shape all defer to the pack. **Remove the investigation/mystery act architecture (`:242–271`) entirely** — it moves to the `mystery` pack, not to `fantasy`. Remove the hardcoded 22–26 chapters / ~80,000 words. |
| `novel-foundation/SKILL.md` | Call `resolve_genre.py` in setup; pass pack paths to the judge; gate on `pillar_score`; fill pack artifacts in the layer order. |
| `novel-seed/references/seed-prompts.md` | Becomes a neutral scaffold. Persona, required concept fields, DO-NOT list, and diversity requirements all come from the pack's `## Seed Prompt`. |
| `novel-seed/SKILL.md` | Add a genre-selection step before concept generation. `MAGIC/COST` becomes the pack's declared required fields. Render `world.md` and `canon.md` headings from the pack; create pack artifacts. |
| `novel-draft/references/drafting-rules.md` | Rule 6 (magic costs as physical sensation) moves to the fantasy pack. The writer's-stance POV/tense line takes `shape.pov_default`. Rules 1's word target takes `shape.chapter_words`. The other 22 rules are neutral and stay. |
| `novel-draft/SKILL.md` | Resolve genre; pass pack paths to the chapter judge. |
| `novel-revise/SKILL.md` | Pass pack paths to the reader-panel, full-novel, and adversarial-edit judges. |
| `novel-review/SKILL.md` | Pass pack paths to the manuscript-review judge. |
| `novel-import/SKILL.md` | Infer genre from the manuscript and confirm with the user, in the same shape as the existing MYSTERY.md confirmation step. |
| `novel-import/references/extraction-guide.md` | World sections and canon categories driven by the resolved pack. |
| `novel-export/SKILL.md` | `NOVEL-GENRE` defaults to the joined `label_parts` instead of asking cold; the user may edit it. |
| `novel/SKILL.md` | Report genre in the status table; relabel the reported gate from `lore > 7.0` to `pillar > 7.0`; detect and offer the migration below. |

### Scripts

| File | Change |
|---|---|
| `scripts/gen_brief.py` | `:79`'s hardcoded "no generic fantasy diction" reads the resolved pack's diction rule. |
| `scripts/slop_score.py` | Accept an optional genre banned-phrase list, sourced from the pack's `## Drafting Rules`. Erotica's purple-euphemism register is the motivating case; the base tiers are unchanged. |
| `scripts/apply_cuts.py`, `scripts/voice_fingerprint.py` | No change. Already neutral. |

## Shipped packs (v1)

| Pack | Role | Pillar |
|---|---|---|
| `general` | primary | Setting & thematic architecture. The neutral default, weighted `{pillar: 15, character: 40, structure: 20, craft: 25}` — the inverse emphasis of fantasy's, and the reason a contemporary novel can now clear the gate |
| `fantasy` | primary, secondary | Lore & worldbuilding — magic system, history, geography, interconnection, iceberg depth |
| `science-fiction` | primary, secondary | The novum and its societal extrapolation |
| `romance` | primary, secondary | Relationship architecture |
| `mystery` | primary, secondary | The puzzle — clues, suspects, fair play. Artifact: clue ledger |
| `thriller` | primary, secondary | Antagonist capability and threat escalation |
| `erotica` | primary, modifier | Erotic architecture — desire, escalation curve, consent and power, embodiment |
| `ya` | modifier | — |
| `cozy` | modifier | — |

The `fantasy` pack is a **lossless port** of today's behavior: a fantasy
project scored before and after the change should land within noise of the
same score. That is the proof the extraction is clean.

Deferred to v2, with no structural work required: `horror`, `historical`
(artifact: real-vs-invented ledger), `literary`, `magical-realism`,
`litrpg` (artifact: progression ledger), `alternate-history`, `western`,
`satire`. `magical-realism` is the design's acceptance test — its pillar
dimension is *sustained productive ambiguity*, the direct opposite of
fantasy's hard-rules-with-costs. If the base rubric can express it without
strain, the architecture is genuinely neutral.

## Validation

`validate_genre_pack.py` checks:

1. Frontmatter parses; `name` matches the filename stem.
2. `role` is a non-empty subset of `{primary, secondary, modifier}`.
3. Primary and secondary declare `weights`: integers summing to 100.
4. Primary declares `pillar_label`, `## Framing`, and `## Pillar Dimensions`.
5. Modifier declares **none** of `weights`, `pillar_label`, `beat_system`,
   `shape`, or `## Pillar Dimensions`.
6. Pillar dimension keys are 3–6 in number, are valid JSON identifiers, and
   do not collide with the reserved base dimension names (`character_depth`,
   `character_distinctiveness`, `character_secrets`, `outline_completeness`,
   `foreshadowing_balance`, `internal_consistency`, `voice_clarity`,
   `canon_coverage`). This is what stops a literary pack from
   double-counting prose against the base `craft` category.
7. Every `conflicts_with` name resolves to a real pack.
8. `shape` ranges are ordered (`low <= high`).
9. Artifact filenames do not collide with core project files.

## Migration

Existing projects have no `genre` field, and taking the `general` default
silently would be wrong twice over: they were written as fantasy, and their
`results.tsv` history was scored under fantasy weights. The keep/discard
logic compares each iteration against the best previous score, so a weight
change mid-project makes those numbers incomparable.

Therefore:

1. `novel/SKILL.md` detects a `state.json` with no `genre` and **stops to
   ask** rather than defaulting. For an existing project it suggests
   `fantasy`, because that is what the project was scored under. New
   projects created by `novel-seed` default to `general` only when the user
   declines to pick.
2. The migration writes `genre`, `genre_secondary`, `genre_modifiers`, and
   renames `lore_score` to `pillar_score` in place.
3. **Any genre change on a project with scored history** — at migration or
   later — appends a marker row to `results.tsv`
   (`keep_discard=genre-change`) and resets the keep/discard baseline. The
   next iteration is treated as the first scored one. This is recorded in
   `novel-foundation/SKILL.md` alongside the existing resume logic.

## Testing

Matching the existing `tests/` pytest setup:

- `test_validate_genre_pack.py` — every validation rule above, plus a valid
  fixture per role and a deliberately broken one per rule.
- `test_resolve_genre.py` — project-over-plugin precedence, primary +
  secondary + modifier merge, `conflicts_with` rejection (`ya` + `erotica`),
  missing-genre default, unknown-pack error.
- `test_no_genre_leak.py` — the enforceable successor to the De-Bells rule.
  A case-insensitive grep for `fantasy|magic|sanderson|tolkien|elves|bestiary`
  across `shared/rubrics/`, `shared/craft/`, `shared/templates/`, and
  `skills/` must return zero hits outside `shared/genres/`. This is what
  keeps the fix from eroding.
- Every shipped pack validates in CI.

Manual smoke tests, since the pipeline's real behavior is model-driven:

- A romance seed reaches and clears the foundation gate — the bug that
  motivated this work.
- A fantasy project scores within noise of its pre-change score.
- `fantasy` + `romance` + `erotica` resolves and produces a coherent merged
  brief.

## Implementation phasing

The surgery touches 24 files, but it is one coherent change and should land
as one plan, staged so the pipeline is never broken between stages:

1. **Mechanism.** `resolve_genre.py`, `validate_genre_pack.py`,
   `TEMPLATE.md`, and their tests. Nothing else reads them yet.
2. **Lossless fantasy extraction.** Author `general` and `fantasy`; perform
   the base-file surgery; migrate `state.json` and the gate. Acceptance: a
   fantasy project scores within noise of its pre-change score, and
   `test_no_genre_leak.py` passes.
3. **Proof of range.** Author `romance` and `mystery` — the two packs that
   most stress the design (no world; a required artifact). Acceptance: a
   romance seed reaches and clears the foundation gate.
4. **Remaining v1 packs.** `science-fiction`, `thriller`, `erotica`, `ya`,
   `cozy`. Acceptance: `fantasy` + `romance` + `erotica` resolves and
   produces a coherent merged brief.

Stage 2 is the risky one and carries the acceptance test that matters; stages
3 and 4 are additive and can slip without blocking anything.

## Out of scope

These break the pipeline below the genre layer, and no pack can rescue them:

- **Verse novels** — the ~3,200-word prose chapter is meaningless.
- **Screenplays and graphic novel scripts** — a different unit of composition.
- **Non-fiction and memoir** — no outline-to-prose model.
- **Short story collections** — already served by the separate `autoanthology`
  plugin.

Also unchanged: the art, audiobook, cover, and landing-page scripts at the
repo root, which were out of scope for the original plugin conversion and
remain so.
