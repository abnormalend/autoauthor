# Extraction Guide — Reverse-Engineering Layers from Prose

One section per artifact novel-import produces. Follow the matching
section when extracting or writing that artifact. These mirror the
structures in `novel-foundation/references/layer-guides.md`, but the
direction of work is reversed: layer-guides.md is for INVENTING a
layer from a seed concept; this guide is for RECOVERING a layer from
prose that already exists. Where a requirement below cross-references
layer-guides.md, that document still governs the target document's
required sections and depth — this guide only states what changes
about *how* you fill them.

## Global rule

The manuscript is ground truth. Every extracted document DESCRIBES
what the prose establishes — it does not invent, upgrade, or
"improve" what is on the page. Where the prose is silent on a
question the layer document needs answered (a rule's exact cost, a
character's exact age, a place's exact distance from another), mark
the gap explicitly with `[inferred]` and state the inference's basis,
rather than inventing a fact and presenting it as text-established.
Never write anything that contradicts a scene as written. If two
passages in the manuscript conflict with each other, record the
conflict rather than silently resolving it in either document — that
is revision fuel, not your call to make.

---

## world.md

Read for it: every scene touching the speculative/magic system, every
named location, every faction or institution mentioned, every custom
or cultural detail shown or referenced.

Output must contain the same sections as layer-guides.md's `world.md`
section (Cosmology & History, Magic System — Hard Rules / Soft Rules —
Protagonist's Exception, Societal Implications, Geography, Factions &
Politics, Bestiary/Flora, Cultural Details, Internal Consistency
Rules) — but every entry is reconstructed from what the prose actually
shows, not proposed fresh.

Extraction-specific rules:
- Every rule, cost, and limitation of the magic/speculative system
  gets a `(ch_NN)` citation to the chapter(s) that demonstrate it. A
  rule the text asserts but never shows in action is still citable to
  where it's asserted — note it as "(stated, not dramatized)".
- Geography, factions, and culture are written up exactly as the prose
  depicts them — same specificity standard as layer-guides.md (named,
  sensory, not generic), but sourced from scenes, not imagined.
- Where the manuscript implies connective tissue it never states
  outright (why a rule exists, how two factions' history connects),
  write it under a clearly marked `[inferred]` list at the end of the
  relevant subsection rather than folding it silently into the
  reconstructed-fact prose above it.
- Do not backfill iceberg depth the prose doesn't have. If the
  manuscript only gestures at a detail once, report it as gestured-at,
  not as an established fact with invented specifics.

---

## characters.md

Read for it: every scene featuring each character — dialogue, action,
interiority, what other characters say about them, how their
circumstances change chapter to chapter.

Output must contain the same per-character structure as
layer-guides.md's `characters.md` section (name/age/role, wound/want/
need/lie chain, three sliders with justification, arc type and
trajectory, speech pattern across the 8 dimensions with example
lines, physical appearance and tells, secrets, relationships,
thematic role) for every character the manuscript actually gives
enough material to reconstruct.

Extraction-specific rules:
- The wound/want/need/lie chain is INFERRED from arc evidence, not
  invented from scratch — build the causal chain (ghost → wound → lie
  → want → need) from what the character does and what the text shows
  changing in them, and cite the chapters that show each link (e.g.
  "WOUND inferred from ch_03, ch_07").
- The three sliders (proactivity/likability/competence) are read off
  the character's actual behavior on the page, with the justification
  citing specific scenes.
- Speech patterns are extracted from real dialogue, not synthesized:
  quote 2–3 actual lines per character (verbatim, with `(ch_NN)`) as
  the worked examples for the 8 dimensions, instead of writing fresh
  example lines.
- Secrets the text reveals late (a twist, a withheld fact) go into
  the registry with a `reveal: ch_NN` note — record them as secrets
  even after their reveal chapter, since revision work needs to know
  when the reader learns them.
- Where the manuscript doesn't give enough material to reconstruct a
  full chain or all 8 speech dimensions for a minor character, fill
  what the text supports and mark the rest `[inferred]` or
  `[insufficient material — flag for foundation loop]` rather than
  padding with invention.

---

## outline.md

Applies to revise and continue modes only. **Salvage mode skips this
section entirely** — leave outline.md as its unmodified template; the
manuscript's plot shape is exactly what's being discarded, so there is
nothing to extract. The foundation loop's outline pass builds the
re-draft's outline fresh from the extracted world/characters/MYSTERY
layers and `import_source.md`, the same as a from-scratch project.

Read for it: the full manuscript, chapter by chapter, plus any
author notes about intended future chapters (continue mode only).

Output has two parts, both extraction-specific in structure (this
replaces, not just re-sources, layer-guides.md's outline.md part 1):

### AS-WRITTEN outline
For every chapter that exists on disk: POV character and narrative
mode, the beats that actually occur (not a idealized version — what
happens on the page), the emotional arc as shown, and the chapter's
actual word count. Do not force chapters into Save the Cat beat names
they don't fit — note the beat only where it's a reasonable read of
what the chapter is doing.

### Foreshadowing ledger (OBSERVED)
Same table shape as layer-guides.md's foreshadowing ledger (# / Thread
/ Planted Ch / Reinforced Ch / Payoff Ch / Type), but built from what
is actually planted and paid off in the prose, not planned in advance.
Any plant with no payoff chapter in the existing text gets
`UNRESOLVED` in the Payoff column instead of a chapter number — these
are revision fuel, not failures to hide. Do not invent a payoff to
balance the ledger.

For **continue-mode** imports: after the as-written section and
observed ledger, add planned entries for the chapters that don't yet
exist ONLY if the user has described their intent for the rest of the
story. If they haven't, mark the remaining outline `TO BE OUTLINED`
and note explicitly that the foundation loop's outline pass will fill
it — do not guess at an ending the author hasn't described.

---

## voice.md Part 2 + voice_wells.json

Read for it: representative passages across the manuscript — opening
pages, a mid-book scene, action, dialogue-heavy scene, quiet/interior
scene — enough to see the voice's range, not just its average.

Output fills the same Part 2 subsections as the template (Tone,
Sentence Rhythm, Vocabulary Register, POV and Tense, Dialogue
Conventions, Exemplar Passages, Anti-Exemplars), but every claim is
derived from the prose itself:
- Tone, sentence rhythm, and vocabulary register are described as
  observed in the manuscript's actual register and metaphor domains —
  not aspirational.
- POV and tense are read directly off the prose (don't assume; check
  for drift chapter to chapter and note it if present).
- **Exemplar Passages:** 3–5 passages QUOTED VERBATIM from the
  manuscript, each with a `(ch_NN)` citation — these are what the
  drafting/revision loop calibrates against, so they must be real text
  the voice already achieved, not written fresh.
- **Anti-Exemplars:** 2–3 patterns actually observed in the weaker
  passages of the manuscript (repetition, a recurring crutch phrase,
  a register that drifts off-voice) — quote them if the prose has clear examples; if the
  prose is clean and no real anti-exemplar exists, it's fine to
  construct one that represents the nearest temptation the voice
  should resist (mark it `(constructed, not from manuscript)`).

`voice_wells.json` (2–4 wells, 30–60 words each) is built from the
manuscript's actual recurring vocabulary domains — the words the POV
character's thinking and imagery keep returning to — pulled from real
usage counts across the text, not guessed at from the premise.

After the chapter files exist on disk (step 3 of SKILL.md), run:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/voice_fingerprint.py"
```

Record its summary stats (novel-average metrics, any outlier
chapters it flags) in a `### Discovery Notes` subsection added at the
end of voice.md Part 2 — this gives the foundation and revision loops
a documented baseline to calibrate future chapters and edits against.

---

## MYSTERY.md

Read for it: the whole manuscript, with particular attention to what
information is withheld from the reader, what reveal (if any) recasts
earlier scenes, and what the ending resolves or refuses to resolve.

Output follows layer-guides.md's MYSTERY.md requirements (a
one-sentence question, an answer that recontextualizes the story, no
clean right answer, a physical manifestation in the world, a real-cost
choice) as far as the manuscript supports them — inferred from the
central secret/reveal structure the prose actually has.

The file's first line must be:

```
> IMPORTED — INFERRED FROM MANUSCRIPT. Author: verify before relying on this.
```

before any other content. This is not optional and is not removed
even after the author confirms the inference (step 6 of SKILL.md) —
if the author edits the file to correct it, they may remove the
banner themselves as part of that edit, but the import step must
never write a MYSTERY.md without it.

Like the invented version, this file stays author's-eyes-only and is
never loaded into drafting context.

---

## canon.md

Read for it: everything already read for the other layers — this is
the fact index across all of them plus any facts scenes establish
that don't rise to their own section elsewhere (an exact date, a
character's age stated once, a travel time mentioned in passing).

Output follows layer-guides.md's canon.md categories (Geography,
Timeline, Magic System Rules, Character Facts, Political/Factional,
Cultural, Established In-Story) with the same one-fact-per-bullet,
short-and-checkable format.

Extraction-specific rules:
- Every entry gets a `(ch_NN)` citation — extraction has no
  "world.md" or "characters.md" source category the way invention
  does, because those documents are themselves extracted from the
  chapters; cite the chapter(s) the fact actually comes from. If a
  fact only appears in the extracted world.md/characters.md prose and
  isn't independently statable from a chapter (e.g. a synthesized
  slider justification), cite the document instead: `(world.md)` /
  `(characters.md)`.
- Never cite MYSTERY.md, same rule as layer-guides.md: a fact whose
  only home is MYSTERY.md must also appear in veiled form in world.md
  or characters.md, cited there. The full secret stays in MYSTERY.md,
  author-eyes-only.
- Do not invent facts to round out categories. A manuscript that
  doesn't establish a character's exact age leaves that entry out (or
  notes `age: [inferred from context, not stated]` if the text gives
  enough to bound it, e.g. "old enough to remember the war").

---

## state.json

Write the state file with the same shape as
`shared/templates/state.json`. Extraction-specific values:

- `phase`: always `"foundation"` — every import mode runs the normal
  gated foundation loop before drafting or revision resumes.
- `chapters_drafted`: the number of chapter files actually written to
  `chapters/` in step 3 (0 for salvage mode, since salvage writes
  `import_source.md` instead of chapter files).
- `chapters_total`:
  - **revise mode:** equal to `chapters_drafted` — the manuscript is
    complete, so the total is whatever exists.
  - **continue mode:** the user's stated planned total chapter count;
    ask if they haven't said. If they don't know yet, use
    `chapters_drafted` as a placeholder and note in the report that
    the foundation loop's outline pass will set the real total.
  - **salvage mode:** `0` at import time — outline.md is not
    extracted (left as its template; see the outline.md section
    above), so there is no chapter count to derive one from yet. The
    foundation loop's outline pass builds the outline from scratch and
    sets the real `chapters_total` at its Exit. Note this explicitly
    in the handoff report so `0` isn't mistaken for a finished value.
- Leave `iteration`, `foundation_score`, `lore_score`, `novel_score`,
  `revision_cycle`, `review_round`, and `debts` at their template
  defaults (0 / 0.0 / `[]`) — the foundation loop sets these as it
  runs.
