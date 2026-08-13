---
{
  "name": "mystery",
  "label": "Mystery",
  "role": ["primary", "secondary"],
  "pillar_label": "The Puzzle",
  "weights": {"pillar": 40, "character": 25, "structure": 25, "craft": 10},
  "beat_system": "save-the-cat",
  "content_register": {},
  "conflicts_with": [],
  "shape": {
    "words": {"extended": [80000, 95000]},
    "chapter_words": 3200,
    "pov_default": "single-POV third limited past"
  },
  "artifacts": ["clue_ledger.md"]
}
---

## Framing

- genre_noun — "mystery novel"
- pillar_noun — "puzzle"
- comps — Agatha Christie, Dorothy L. Sayers, Tana French, Louise Penny, Kate Atkinson, Anthony Horowitz
- seed_persona — a crime novelist who has written across the range from village cozy to procedural to hardboiled, who builds the solution first and the concealment second, and who never proposes a puzzle that only works because the narration looked away
- reader_persona — a mystery reader who solves about a third of the books they read and is delighted when they don't, who keeps a mental list of every clue, and who will forgive almost anything except being cheated
- writer_persona — a working crime novelist and CWA judge who reads for the placement of the clue that cracks it, for whether the suspects are people or a lineup, and for whether the detective reasons or is simply told

## Pillar Dimensions

The spine of this genre is fair play: the reader must be able to solve it,
in principle, from what is on the page before the reveal. That is a
structural property of the plan, not a matter of taste, and everything
below tests it. Read `clue_ledger.md` (this pack's artifact — see
`## Artifacts`) alongside the outline; the ledger is the primary evidence
for the dimensions that follow, and a missing or unfilled ledger is a real
gap in the plan, not a missing formality.

Two things are worth distinguishing before scoring. **Concealment** is what
the book does to stop the reader seeing what is in front of them: burying a
clue in a busy scene, giving it a plausible wrong meaning, letting the
detective dismiss it. That is the craft of the genre and it should score
well. **Withholding** is not showing the reader something the POV character
saw. That is cheating, and no amount of elegance redeems it.

### Scored dimensions

- clue_completeness [cap 6] — Every fact the solution depends on must appear on the page, in a scene the POV character witnesses, before the reveal. Excellent looks like a ledger in which the last necessary clue lands with real chapters to spare, and in which each clue is planted in a scene that has its own reason to exist. A gap looks like a solution resting on a document, a conversation, or a forensic result that the reader first learns of in the reveal itself. Test: list every fact the culprit's identification requires, then find each one's planting chapter in the ledger and confirm it precedes the reveal. If any required fact has no earlier planting, score 6 max — and note that this is also a Genre Contract breach, which the rubric handles separately. If clues exist but three or more of them are planted only in the final quarter, the book is fair on paper and unsolvable in practice; score 6 max.
- suspect_viability [cap 6] — Excellent looks like at least three suspects besides the culprit for whom you could write the accusation scene: each has a means, a motive, and an opportunity established on the page, and each has a secret of their own that explains their evasiveness without being the crime. A gap looks like a lineup — characters who are suspects because the narration calls them suspects. Test: for each named suspect, state their means, motive, opportunity, and the innocent secret that makes them behave guiltily. If fewer than three suspects yield all four, score 6 max. A suspect who is exonerated by a fact the reader was never given is not a suspect; count them as absent.
- misdirection_honesty [cap 6] — Red herrings must mislead by interpretation, never by omission. Excellent looks like a clue that is entirely true, shown in full, and means something other than what the detective and the reader conclude — and whose real, innocent meaning is written down in the ledger. A gap looks like a herring built from a fact the POV character knew and the narration skipped, or one whose innocent explanation the plan has not actually decided on. Test: take each row the ledger marks as a red herring and check that its "Actually means" column contains a specific true explanation rather than "nothing" or "misleading". If any herring lacks one, score 6 max. If the plan's misdirection depends anywhere on the narration declining to report what the POV character observed, score 6 max regardless of how well the rest is built.
- detection_logic [cap 6] — The route from clues to solution must be reproducible. Excellent looks like a detective with a stated method who is shown using it, and a chain in which each inference names the clue it rests on. A gap looks like intuition doing the load-bearing work — a hunch, a feeling that something was wrong, a leap the text asserts rather than shows. Test: reconstruct the chain from the outline in numbered steps, each citing a ledger row. If you cannot get from the evidence to the culprit without a step that has no clue behind it, score 6 max. If the solution reaches the reader through a confession, an eleventh-hour witness, or the culprit explaining themselves unprompted rather than through the detective's reasoning, score 6 max.
- solvability_curve [cap 6] — A mystery should become solvable at a specific point and then stay unsolved for a while — enough runway that the attentive reader gets to be right and the ordinary reader gets to be surprised. Excellent looks like a ledger whose "Solvable by" values converge two to four chapters before the reveal. A gap looks like the last necessary clue arriving in the reveal chapter (nobody could have solved it) or every clue being present by the third chapter with nothing to do afterwards (everyone solved it, and the middle is filler). Test: take the maximum "Solvable by" value across all rows the solution depends on and compare it to the reveal chapter. If the gap is under one chapter or over a third of the book, score 6 max. Also check the middle: if the outline's second act plants no clue the solution needs, the investigation is treading water; score 6 max.

## At Compressed Length

Three dimensions, not five. A short mystery cannot field a viable suspect
pool — three suspects with means, motive and opportunity is most of a
novel's cast — and a solvability curve measured in chapters has no
chapters to measure. What survives is the fair-play core, which is
exactly what does not scale down: a clue withheld is a broken promise at
any length.

- clue_completeness [cap 6] — Every fact the solution rests on is on the page before it. Unchanged, and the least negotiable thing in this pack. If any required fact has no earlier planting, score 6 max — and note that this is also a Genre Contract breach, which the rubric handles separately.
- misdirection_honesty [cap 6] — One herring, honestly built: it must have an innocent explanation the reader can reach. At this length a single herring is the right number and two is usually one too many. If the misdirection anywhere depends on the narration declining to report what the POV character observed, score 6 max regardless of how well the rest is built.
- detection_logic [cap 6] — The chain from evidence to culprit, with no step missing. If you cannot get there without a step that has no clue behind it, score 6 max. A confession or an unprompted explanation is worse here than in a novel: it is not a shortcut past a hundred pages, it is the story.
- suspect_viability — not scored at this band.
- solvability_curve — not scored at this band.

## Genre Contract

These bind the book's central mystery. When this pack is loaded as a
secondary, they bind the mystery thread rather than the whole plot.

- The reader could have solved it. Every fact the solution depends on appears on the page, in a scene the POV character witnesses, before the reveal.
- The solution follows from those facts by reasoning the text shows. It is not delivered by a confession, a coincidence, or evidence introduced in the reveal itself.
- The culprit appears before the final quarter, is someone the reader has met and can name, and has a means, a motive, and an opportunity established before the reveal.
- Narration never withholds what the POV character observed. Every red herring misleads by what it appears to mean, and has a true, innocent explanation recorded in `clue_ledger.md`.
- No twin, secret sibling, undisclosed identity, or previously unmentioned person is the answer.

## World Sections

The world of a mystery is the machinery of concealment and discovery: who
could have been where, what could have been known, who is allowed to ask,
and what the answer costs. Every section below must produce a constraint
that closes off a possibility somewhere in the outline. A detail that rules
nothing out is decoration and counts against the score, not for it.

- The Crime & Its Scene
- Investigative Authority & Procedure
- Geography & Access
- The Community Under Suspicion
- Evidence & What It Can Prove
- Timeline of the Crime
- Internal Consistency Rules

### The Crime & Its Scene
What was actually done, by whom, how, when, and why — written out plainly
for the author's eyes, in full, before anything else in this document. The
physical scene in detail: layout, entry and exit, what was disturbed, what
was left, what was taken. What the crime looked like to the first person to
find it, and how that first impression differs from the truth. If this
section is vague, every other section is guesswork.

### Investigative Authority & Procedure
Who is permitted to investigate here, and by what right. What the detective
can compel, what they must ask for, and what they can be refused. Who
outranks them, who can shut them down, and what it costs them to be shut
down. If the detective is an amateur, state precisely why they have access
that an amateur would not, and what they lose the moment the professionals
notice. The reader must never wonder why the police are not simply handling
this.

### Geography & Access
The map as a set of constraints: distances, travel times, sightlines, locks,
keys, shifts, who can see whose door from where. This is the section
alibis are built and broken against, so it must be specific enough to be
checked. Sensory signatures for the two or three locations the
investigation returns to, so a scene set in one could not be relocated to
another with only proper nouns changed.

### The Community Under Suspicion
The social body the crime happened inside: a village, a department, a firm,
a family, a school. What everyone here already knows about each other, what
is never said aloud, and who is owed what. Every suspect needs a secret of
their own that is not the crime — this section is where those secrets and
their costs live, because they are the engine of every honest red herring
the book will use.

### Evidence & What It Can Prove
What forensic, documentary, and testimonial evidence exists in this setting
and period, what it can establish, how long it takes, and who controls it.
State the limits explicitly: no DNA in 1931, no phone records without a
warrant, no autopsy for eleven days. These limits are what make the puzzle
solvable by reasoning rather than by laboratory, and a book that forgets
them resolves itself off-page.

### Timeline of the Crime
The true sequence, to the hour: where every suspect actually was, what they
actually did, and what they will say instead. Include the culprit's
complete movements before, during, and after. This is written for the
author, never shown whole to the reader — but every alibi the book offers
must be checkable against it, and every contradiction the detective finds
must be a real contradiction here.

### Internal Consistency Rules
Hard constraints a writer must not violate: travel times, who held which
key, what a body can and cannot do, what a record can and cannot show, who
was demonstrably elsewhere. This world has no magic, which means the things
that break it are coincidence, a witness who appears exactly when needed,
and a piece of evidence that arrives because the plot has run out of road.
Write down the ones this book must not use.

## Cast Requirements

1. **The detective** — derived from the seed. Amateur or professional.
   - Full wound/want/need/lie chain
   - Three sliders with justification
   - Arc type (positive/negative/flat)
   - Detailed speech pattern (8 dimensions, with example lines)
   - Physical habits and tells tied to their work and their wound
   - **Their method**, stated explicitly: what kind of thing they
     notice, what they do with it, and what it blinds them to. The
     method is scored under `detection_logic`, so it must be concrete
     enough to be shown in use.
   - At least 2 secrets
   - Their standing: what they may compel, what they may only ask for

2. **The victim** — full depth despite being absent or dead. Who they
   were to each suspect, what they were doing in the days before, and
   what they had that someone wanted. A victim who exists only to be
   found gives the book no motives to work with.

3. **The culprit** — full wound/want/need/lie chain, plus means, motive,
   and opportunity, plus their complete movements as recorded in the
   world bible's timeline. Their motive must be legible in hindsight
   and invisible in prospect. Note explicitly what they do in every
   scene they appear in before the reveal, and what innocent reading
   each of those actions supports.

4. **At least three further viable suspects** — each with means, motive,
   and opportunity on the page, and each with their own secret that is
   not the crime and that explains their evasiveness. Depth
   proportional to page time, but none of the three may be a placeholder.

5. **The ally who is wrong** — a witness, partner, or confidant whose
   sincere and well-supported reading of the evidence is mistaken. They
   are how the book misdirects without lying.

6. **An institutional figure** with the power to end the investigation —
   a superintendent, an editor, a family lawyer, a school head. They
   believe they are protecting something legitimate.

## Plot Architecture

KEY PLOT ARCHITECTURE (adapt the exact chapter numbers to the seed,
these are proportional guideposts across a 22-26 chapter novel):

- **Act I** (roughly the first quarter): establish the protagonist's
  world, their wound, their competence — whatever they are good at that
  the investigation will require — their institution, their family.
  Plant the central mystery early. Catalyst: something forces the
  protagonist to investigate.
- **Act II Part 1** (roughly 23-50%): investigation. The protagonist
  digs into the inciting secret, encounters the antagonist, allies
  with supporting characters, sharpens their method. Midpoint: the
  protagonist learns a partial truth that changes their approach
  (false victory or false defeat).
- **Act II Part 2** (roughly 50-77%): pressure mounts. The antagonist
  moves against the protagonist's circle. Hidden truths begin to
  surface. The protagonist's lie is increasingly unsustainable. All
  Is Lost: the protagonist confronts the person closest to the secret
  and learns the full truth.
- **Act III** (roughly 77-100%): the protagonist understands the real
  question and must choose how to answer it. The climax must be
  resolvable using facts already established on the page — no new
  evidence introduced at the last minute. The resolution shows the
  aftermath of the protagonist's choice.

CONSTRAINTS:
- The climax must be resolvable using clues already on the page — a
  reader should be able to see, in hindsight, that the pieces were
  already on the board.
- The investigation should feel like a mystery plot overlaid on
  whatever the protagonist's personal arc is (coming-of-age, redemption,
  etc.).

## Canon Categories

### Geography & Access
- The boathouse is eleven minutes' walk from the lodge. (world.md)
- Only the housekeeper and Mr. Everett hold keys to the study. (world.md)
- The lane floods above the ford after heavy rain. (ch_07)

### Timeline
- Iris Everett died between 9:40 and 11:15 on the night of the 14th. (world.md)
- Marlowe arrives at the lodge on the morning of the 15th. (outline.md)
- Ch 1-6 span four days. (outline.md)

### Clues & Evidence
- The study window was latched from the inside. (ch_03, TRUE)
- The torn receipt names a chemist in Hadleigh. (ch_05, TRUE)
- Prentice's coat was wet at 10pm. (ch_04, RED HERRING — he was at the weir, not the boathouse)

### Alibis & Whereabouts
- Prentice claims he was in the billiard room until eleven. (ch_04)
- The housekeeper was demonstrably in the kitchen from 9 to 11. (ch_06, CONFIRMED)
- Nobody can account for Dr. Sayle between 9:30 and 10:15. (ch_08)

### Character Facts
- Marlowe cannot swim. (characters.md)
- Prentice is in debt to his brother-in-law. (characters.md)
- Iris Everett had changed her will six weeks earlier. (world.md)

### Procedural & Institutional
- The county police will not reopen a closed inquest without new evidence. (world.md)
- There is no telephone at the lodge; messages go through the post office. (world.md)
- Marlowe has no power to compel testimony and everyone knows it. (world.md)

### Established In-Story (things that happened in chapters)
- Marlowe read the will in ch_09. He now knows about the change.
- The boathouse burned in ch_15. That evidence is gone.
- Prentice admitted the debt in ch_12. He cannot deny it later.

## Artifacts

### clue_ledger.md

The clue ledger is the book's fair-play accounting. It exists because
"every clue is on the page before the reveal" is a claim that cannot be
checked by reading the outline straight through — it has to be checked
clue by clue, and this file is where that check becomes possible. Nothing
else in the project tracks it: `canon.md` records facts, and the
foreshadowing ledger in `outline.md` tracks plants and payoffs generally,
but neither distinguishes a true clue from an honest red herring or
records the chapter by which the puzzle becomes solvable.

**Format.** A single markdown table with these six columns, one row per
clue, in the order the clues are planted:

| Clue | Planted | Appears to mean | Actually means | True / Herring | Solvable by |
|---|---|---|---|---|---|
| The study window is latched from the inside | ch_03 | Nobody entered from the garden | The killer left through the house and had a key | TRUE | ch_18 |
| Prentice's coat is wet at 10pm | ch_04 | He was at the boathouse | He was at the weir, poaching | HERRING | — |
| A torn chemist's receipt in the grate | ch_05 | Iris was ill and hiding it | Someone else bought the chloral in her name | TRUE | ch_18 |
| Dr. Sayle's missing forty-five minutes | ch_08 | He is the killer | He was with a patient he will not name | HERRING | — |

Column by column:

- **Clue** — the observable fact as the reader receives it, in one line.
  Write what is on the page, not what it proves: "the coat is wet," not
  "Prentice lies about the weir."
- **Planted** — the chapter in which the reader first sees it, in the
  project's `ch_NN` form. A clue mentioned twice is one row, planted at
  the first sighting.
- **Appears to mean** — the reading the text invites at that moment: what
  the detective concludes, or what an attentive reader would conclude.
  This column is the misdirection, stated deliberately rather than left
  to chance.
- **Actually means** — the true significance. Every row must have one,
  red herrings included: a herring's true meaning is its innocent
  explanation, and a herring with no innocent explanation is a
  withheld fact wearing a clue's clothes. "Nothing" is never a valid
  entry here.
- **True / Herring** — `TRUE` if the solution depends on this clue,
  `HERRING` if it does not. This is the column that makes the fair-play
  check mechanical: the set of `TRUE` rows must be sufficient, on its
  own, to identify the culprit.
- **Solvable by** — for a `TRUE` clue, the chapter by which a careful
  reader holding this clue and every earlier one could reach the
  solution. For most rows this is the same chapter for all of them — the
  point at which the last necessary piece is in hand. Use `—` for
  herrings.

Below the table, add one line stating the reveal chapter and the
maximum `Solvable by` value across the `TRUE` rows. That pair is what
`solvability_curve` is scored against, and stating it explicitly stops
the number from being recomputed differently by each reader.

**Which phase fills it.** `seed` creates the file from this
template when it scaffolds the project. `foundation` fills it,
after `canon.md` and against the completed outline, and re-checks it on
every iteration in which the outline or the world bible's crime timeline
changes — a clue moved to a different chapter changes the whole
solvability curve. `draft` adds a row whenever a chapter plants a
clue the ledger does not have, and corrects the `Planted` column when a
chapter lands a clue somewhere other than planned. `revise` and
`review` re-verify the whole table against the manuscript.

**What the rubric checks.** The judge reads this file alongside
`outline.md` and confirms:

  - Every `TRUE` row's `Planted` chapter precedes the reveal chapter.
  - The `TRUE` rows are together sufficient to identify the culprit —
    reconstruct the reasoning chain from them alone and see whether it
    closes.
  - Every row has a non-empty, specific `Actually means`, herrings
    included.
  - No `TRUE` row's `Planted` chapter falls after its `Solvable by`
    chapter.
  - The maximum `Solvable by` sits comfortably before the reveal —
    between one chapter and roughly a third of the book ahead of it.
  - The second act plants at least some `TRUE` rows; an act that plants
    only herrings is an investigation that is not progressing.

An absent or unfilled ledger is scored as a gap in
`clue_completeness`, `misdirection_honesty`, and `solvability_curve`
alike, because those three dimensions have no other evidence to read.

## Drafting Rules

25. Every clue reaches the reader through the POV character's senses, in scene, at the moment they encounter it. If the POV character sees it, the reader sees it — concealment is a matter of what a thing appears to mean, never of what the narration reports.
26. The detective may not conclude anything the reader has not been given the material for. When a deduction lands, the clues it rests on must already be on the page and findable.
27. Record every clue you plant in `clue_ledger.md` as you draft it, including the ones you improvise. A clue that exists only in the manuscript and not in the ledger will not be checked, and will not pay off.
28. Banned phrases, on top of the base list: "little did she know", "if only he had known then", "it would be days before he understood", "something wasn't right", "a chill ran down her spine", "the game is afoot", "and then it hit her". Narratorial foreshadowing that promises significance without delivering a fact is the slop of this genre — it fakes the feeling of a clue while giving the reader nothing to hold.

## Seed Prompt

Persona (adopt while generating):

You are a crime novelist who has written across the genre's range —
village cozy, police procedural, historical, hardboiled. You build the
solution first and the concealment second, and you know the difference
between hiding a thing in plain sight and not showing it at all. You
generate novel concepts that are SPECIFIC, SURPRISING, and
STRUCTURALLY SOUND. Every concept you propose is one you could
actually plant fairly: you know who did it, how, and which observable
fact gives them away. You never propose a puzzle that works only
because the narration looked away.

Required concept fields (these mystery fields and phrasings replace
the neutral scaffold's versions of the same fields):

WORLD: The closed social body the crime happens inside — a village, a
  department, a firm, a household, a ship, a school — and the specific
  rules of access, authority, and secrecy that govern it. Make it
  SENSORY, and make it constraining: who can go where, who can ask
  what, who would be noticed.
THE CRIME: What was done, to whom, and — for your eyes, not the
  reader's — by whom and why. Name the single observable fact that
  gives the culprit away, and say what innocent thing that fact will
  appear to mean when the reader first meets it. If you cannot name
  that fact, the concept is not ready.
THE SUSPECTS: Three or four people besides the culprit who each have a
  means, a motive, an opportunity, AND a secret of their own that is
  not the crime. Name each secret — that is what makes them behave
  guiltily without being guilty.
THE DETECTION: Who investigates, by what right, and by what method —
  what kind of thing they notice and what that same method blinds them
  to. Name what they can compel and what they can only ask for.
TENSION: What's the central conflict? It must be both PERSONAL (what
  solving this costs the investigator) and LARGER (it implicates a
  family, an institution, a community). These two must be in tension
  with each other.
THEME: What question does this story explore? Not a message — a
  genuine question with no easy answer.
WHY IT'S NOT GENERIC: One sentence on what makes this different from
  the standard mystery premise.

Aim for DIVERSITY across the ten concepts:
  - Span the register from cozy to hardboiled; this pack constrains
    neither, so at least one should be bloodless and at least one
    genuinely brutal
  - Mix amateur and professional investigators, and at least one with
    no standing at all
  - At least one closed circle and at least one open, city-scale case
  - At least one crime that is not a murder, and one where the
    question is not whodunit but howdunit or whydunit
  - Vary period and place; at least one historical and at least one
    outside the Anglo-American default
  - At least one where the detective is wrong about something that
    matters to them personally
  - Vary scale: a stolen object, a disappearance, a fraud, a death
  - Mix of tones: wry, bleak, warm, unsettling, comic

DO NOT generate:
  - A solution turning on a twin, a secret sibling, a disguise, or a
    person the reader has not met
  - The psychic hunch as the mechanism — a detective who "just knew"
  - The serial killer taunting the profiler, and the killer who leaves
    literary or biblical puzzles at the scene
  - A narrator who withholds their own guilt from a reader they
    otherwise show everything to
  - Amnesia as the puzzle
  - A dead young woman whose only function is to be found, and whose
    interiority the book never supplies
  - A confession as the resolution mechanism
  - The last-chapter drawing-room reveal in which the detective
    produces evidence the reader never saw
  - A cold case solved by a forensic technique introduced in the
    final act
