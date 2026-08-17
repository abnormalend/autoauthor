# Foundation Layer Guides

One section per planning document. Follow the matching section when
filling or revising that layer. Every requirement below is a hard
requirement, not a suggestion — the foundation rubric scores against
exactly these expectations.

---

## Genre packs

Before filling any layer, run the resolver from the project directory:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/resolve_genre.py"
```

Read every pack path it reports. The packs define this novel's world
sections, cast requirements, plot architecture, canon categories, book
shape, and any extra artifacts. Where a section below says "from the pack,"
the pack's content governs and this guide only states the standard of depth.

---

## world.md

Build a complete world bible. This is the definitive reference for
everything that EXISTS in this world. A writer should be able to
resolve any worldbuilding question from this document alone.

Ground every choice in the seed concept and the discovered voice
(voice.md Part 2, filled first) — this document must feel like it
belongs to THIS story, not a generic setting for its genre.

CRAFT REQUIREMENTS:
- Whatever central system the pack's pillar dimensions govern must meet the
  rigor those dimensions demand — read them before writing.
- Trace the system's implications through society, economy, law, religion.
- At least 2-3 societal implications explored in depth.
- History must create PRESENT-DAY TENSIONS that drive the plot, not just
  backdrop.
- Geography must be specific and sensory, not generic for the genre.
- Iceberg principle: imply more than you state.
- Interconnection: pulling one thread should move everything.

STRUCTURE THE DOCUMENT WITH THE SECTIONS LISTED IN THE PACK'S
`## World Sections`, in that order. For each, be specific: named, sensory,
and consequential. Every rule gets a COST or LIMITATION stated alongside it.
Include 2-3 unexplained-but-intriguing facts per section for iceberg depth.

IMPORTANT:
- Be SPECIFIC. Not "the city has districts" but name them, describe
  them, give them sensory signatures.
- Every rule should have a COST or LIMITATION stated alongside it.
- Include 2-3 facts per section that are unexplained, hinting at
  deeper systems (iceberg depth).
- Facts should INTERCONNECT: the world's central system should shape
  the politics, the geography should shape the culture, the history
  should explain current faction conflicts.
- Write in clean, direct prose. No AI slop. No "rich tapestry." No
  "delving."
- The world should feel grounded and LIVED-IN, not imagined. Think:
  what does breakfast smell like? What do children play? How do old
  people complain?
- Target the word count the pack's shape implies for a world bible —
  dense, not padded, roughly 3-4% of the novel's target length.

---

## characters.md

Build a complete character registry. This is the definitive reference
for WHO exists in this story, what drives them, how they speak, and
what secrets they carry. Draw on the discovered voice (voice.md
Part 2) and world.md, both filled first — characters must sound like
they belong to this world and their circumstances must be consistent
with its rules.

CHARACTER CRAFT REQUIREMENTS (from CRAFT.md):

### The Three Sliders (Sanderson)
Every character has three independent dials (0-10):
  PROACTIVITY — Do they drive the plot or react to it?
  LIKABILITY  — Does the reader empathize with them?
  COMPETENCE  — Are they good at what they do?
Rule: compelling = HIGH on at least TWO, or HIGH on one with clear
growth.

### Wound / Want / Need / Lie Framework
A causal chain:
  GHOST (backstory event) -> WOUND (ongoing damage) -> LIE (false
  belief to cope) -> WANT (external goal driven by Lie) -> NEED
  (internal truth, opposes Lie)
Rules: Want and Need must be IN TENSION. Lie statable in one sentence.
Truth is its direct opposite. Every link in the chain must be
CAUSALLY LINKED, not just thematically associated — the rubric checks
that the lie logically follows from the wound and the want is the
wrong solution to the lie.

### Dialogue Distinctiveness (8 dimensions)
1. Vocabulary level  2. Sentence length  3. Contractions/formality
4. Verbal tics  5. Question vs statement ratio  6. Interruption
patterns  7. Metaphor domain  8. Directness vs indirectness
Test: Remove dialogue tags. Can you tell who's speaking? Metaphor
domains must not overlap between characters. Speech patterns must
reflect background (a teenager should not sound like an elderly
merchant).

BUILD THE REGISTRY WITH THE ROLES LISTED IN THE PACK'S
`## Cast Requirements`, at the depth each entry specifies. Add any further
characters the seed's plot demands.

FOR EACH CHARACTER INCLUDE:
- Name, age, role
- Ghost/Wound/Want/Need/Lie chain (for major characters)
- Three sliders (proactivity/likability/competence) with numbers and
  justification
- Arc type and arc trajectory
- Speech pattern (all 8 dimensions, with example lines)
- Physical appearance (specific, not generic)
- Physical habits and unconscious tells
- Secrets (what the reader doesn't learn immediately)
- Key relationships (mapped to other characters)
- Thematic role (what question does this character embody?)

IMPORTANT:
- Characters must INTERCONNECT. Their wants should conflict with each
  other.
- Every secret should be something that would CHANGE the story if
  revealed — vague secrets score lower than specific, checkable ones.
- Speech patterns must be distinct enough to pass the no-tags test.
- Give the protagonist habits that come from their specific
  circumstances (their gift's cost, their trade, their wound).
- Any physical tell (shaking hands, a limp, a tic) should connect to
  something specific in the backstory, not be decorative.
- The antagonist should be as fully realized as the protagonist — a
  worthy opposition.
- Target ~3000-4000 words. Dense character work, not padding.

---

## outline.md part 1

Build a complete chapter outline. Use the chapter count, total word
count, and per-chapter target from the resolved pack's `shape`. Draw on
world.md, characters.md, the discovered voice (voice.md Part 2), and the
central mystery (MYSTERY.md) — all filled first — as available
inputs; the outline is the layer that turns them into a sequence of
scenes.

BUILD THE OUTLINE WITH:

### Act Structure
Map out the acts and state the percentage marks for the key beats. If the
pack declares a `## Plot Architecture`, use ITS act structure and marks —
do not overlay a three-act shape on a pack that chose another. Only when
the pack declares none, use the default: Act I (0-23%), Act II Part 1
(23-50%), Act II Part 2 (50-77%), Act III (77-100%).

### Chapter-by-Chapter Outline

For EACH chapter, provide:
- **POV:** which character, and narrative mode (third limited, first,
  etc. — must match voice.md Part 2)
- **Location:** where the chapter is set
- **Beat:** which beat this chapter serves, in the vocabulary of the
  pack's `beat_system` (for `save-the-cat`: Opening Image, Setup,
  Catalyst, etc.)
- **% mark:** where this falls in the novel
- **Emotional arc:** starting emotion -> ending emotion
- **Try-fail cycle:** Yes-but / No-and / No-but / Yes-and
- **Beats:** 3-5 specific scene beats that must happen
- **Plants:** foreshadowing elements planted in this chapter
- **Payoffs:** foreshadowing elements that pay off here
- **Character movement:** what changes for the POV character (or
  others) by chapter's end
- **The lie:** how the protagonist's lie (from their wound/want/
  need/lie chain) is reinforced or challenged in this chapter
- **~Word count target:** for pacing

### MICE Threads
Identify the MICE threads at work (Milieu / Inquiry / Character /
Event) and note which chapters open and close each one. Nest them —
plan them to close in the reverse order they opened.

KEY PLOT ARCHITECTURE: follow the pack's `## Plot Architecture` if it
declares one — this is the same rule the Act Structure section above
states, and it governs both. If the pack declares none, use the base act
structure from CRAFT.md: Act I 0-23%, Act II 23-77%, Act III 77-100%, with
the beats of the pack's `beat_system` at their stated percentage marks
(Save the Cat when the pack declares no `beat_system`).

CONSTRAINTS:
- The climax must be mechanically resolvable using established world
  rules — a reader should be able to see, in hindsight, that the
  pieces were already on the board.
- Any text the story quotes verbatim — a letter, a prophecy, a
  contract, a transmission, a will, a song — must exist IN FULL in the
  plan, at the length the world's own rules permit. A plan that
  describes such an object instead of containing it has left the scene
  it appears in unplanned, and no judge can check whether the object
  does what the outline claims. On one run the single most useful
  planning move was writing the central letter out at exactly the
  byte budget the plan allowed; two evals then caught it contradicting
  its own frame, which is only possible because the text existed.
- The document opens with a `## Facts the story must not contradict`
  section: the clock, the fact table, every number a chapter may need
  to state. This is what `continuity_check.py` reads during drafting.
- The Stability Trap: bad things must stay bad. Not everything
  resolves cleanly.
- Any character established as "absent but plot-critical" must appear
  in person at some point, not only in memory or secondhand report.
- At least 3 chapters should be "quiet" — character-focused, low-
  action, emotionally rich.
- Vary the try-fail types: 60%+ should be "yes-but" or "no-and."
- The foreshadowing ledger (part 2) must have plant-to-payoff
  distances of at least 3 chapters.

---

## outline.md part 2 (foreshadowing ledger)

Continue the outline started in part 1 through its final chapter, then
add:

### Foreshadowing Ledger

A table tracking every planted thread:

| # | Thread | Planted (Ch) | Reinforced (Ch) | Payoff (Ch) | Type |
|---|--------|--------------|------------------|-------------|------|

Include at LEAST 15 threads. Types: object, dialogue, action,
symbolic, structural.

RULES:
- Every plant needs a planned payoff chapter — the ledger must
  BALANCE. A thread with a "Planted" entry and no "Payoff" entry is a
  gap, not a mystery; the rubric scores an empty or unbalanced ledger
  at 0 regardless of implicit threads elsewhere in the documents.
- Plant-to-payoff distance must be at least 3 chapters.
- The protagonist's lie (from characters.md) must be fully confronted
  — reinforced, challenged, and finally shattered or consciously
  kept — by the climax; the ledger must show where.
- The climax should resolve using an option the reader can reconstruct
  from earlier established rules, not a new one invented for the
  finale.
- Any irreversible cost from the central choice should NOT be
  undone by the ledger's payoffs (Stability Trap: don't let the
  ledger quietly walk back the story's losses).
- Final Image should mirror the Opening Image but show transformation.
- Confirm at least one quiet chapter appears in the back half.

---

## voice discovery

During foundation, the agent must DISCOVER the voice for this novel:

1. Read the world concept and initial ideas
2. Write 5 trial passages in different registers (mythic, spare,
   warm, cold, whimsical, etc.)
3. Evaluate which register best serves THIS story's world and tone
4. Select the best, refine it, write exemplar and anti-exemplar
   passages
5. Fill in voice.md Part 2 with the discovered voice

The voice should feel like it BELONGS in the world (Le Guin's insight:
the language creates the world, it does not merely describe it). Where a
loaded pack states its own voice or register expectations, honor them —
the pack governs, this guide only sets the standard of rigor.

After filling voice.md Part 2, also write `voice_wells.json` in the
project root:

```json
{"<well_name>": ["word", "..."], "...": ["..."]}
```

2-4 vocabulary wells (domains the POV character thinks in), 30-60
words each. The mechanical voice-fingerprint script reads this file.

---

## MYSTERY.md

Define the central secret of the novel — the thing the reader
discovers late, that recontextualizes everything before it. The
author must know the FULL answer before drafting begins; a document
that says "the answer will be revealed" without specifying WHAT the
answer is is a gap wearing an iceberg costume, and the foundation
rubric penalizes it as such.

A good mystery has:
- A question that can be asked in one sentence
- An answer that recontextualizes the entire story
- No right answer (moral ambiguity)
- A physical manifestation in the world (not just information)
- A choice the protagonist must make that has real cost

This file is author's-eyes-only — it should NOT be loaded into the
drafting agent's context. The mystery emerges from the world and
characters in the prose; it is not stated explicitly until the reveal.

---

## canon.md

Extract EVERY hard fact from the other layers into a structured canon
database. A "hard fact" is anything a writer must not contradict:
names, ages, dates, physical descriptions, the rules of whatever central
system the world runs on, geography, relationships, established events.

SOURCE DOCUMENTS: seed.txt, world.md, characters.md (and outline.md
once it exists — re-run this extraction whenever any layer changes).

NEVER cite MYSTERY.md as a canon source — the foundation judge cannot
see that file, so citations to it read as unverifiable and get scored
as consistency gaps. Any fact whose only home is MYSTERY.md must ALSO
exist in veiled form in world.md or characters.md (state what is
observably true without revealing why); cite that visible source. The
full secret stays in MYSTERY.md, author-eyes-only.

FORMAT THE OUTPUT AS canon.md WITH THE CATEGORIES LISTED IN THE PACK'S
`## Canon Categories`, using its example entries as the model for
granularity and sourcing. Every category the pack lists gets a heading,
even if thin on the first pass.

RULES:
- One fact per bullet point. Short. Specific. Checkable.
- Include the source (world.md, characters.md, outline.md) in
  parentheses after each fact.
- Aim for 80-120 entries on the first pass; grow the canon toward
  400+ entries before exiting foundation (facts accumulate every
  iteration).
- If two documents give slightly different details, note the
  discrepancy instead of silently picking one — that's a contradiction
  for the next iteration to resolve.
- DO NOT invent facts. Only record what's explicitly stated.

---

## Genre artifacts

If the resolved pack declares `artifacts`, create and fill each one
following the pack's `## Artifacts` section. Fill them after canon.md, and
re-check them whenever the layer they draw on changes. They are scored:
the pack's pillar dimensions reference them.

---

## Genre contract

Before exiting foundation, read every loaded pack's `## Genre Contract` and
confirm the OUTLINE satisfies each promise. A plan that cannot keep the
contract is a plan to write the wrong book — fix the outline, not the
contract.
