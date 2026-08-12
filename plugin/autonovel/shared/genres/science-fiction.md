---
{
  "name": "science-fiction",
  "label": "Science Fiction",
  "role": ["primary", "secondary"],
  "pillar_label": "The Novum & Its Consequences",
  "weights": {"pillar": 40, "character": 25, "structure": 20, "craft": 15},
  "beat_system": "save-the-cat",
  "content_register": {},
  "conflicts_with": [],
  "shape": {
    "chapters": [24, 30],
    "words": [90000, 110000],
    "chapter_words": 3600,
    "pov_default": "third limited past"
  },
  "artifacts": []
}
---

## Framing

- genre_noun — "science fiction novel"
- pillar_noun — "speculative premise"
- comps — Ursula K. Le Guin, Octavia Butler, Ted Chiang, Kim Stanley Robinson, Ann Leckie, William Gibson
- seed_persona — a science fiction novelist who has written across the range from hard orbital-mechanics SF to social SF to space opera, who works out what a new capability does to ordinary life before working out what it does to the plot, and who never proposes a premise that is a present-day argument in a costume
- reader_persona — a science fiction reader who has been reading the genre for thirty years, who forgives handwaving but never forgives inconsistency, and who puts a book down the moment the world stops being a place and becomes a lecture
- writer_persona — a working SF novelist and Clarke Award juror who reads for whether the premise has been thought through past its first consequence, whether the characters live inside the world rather than explaining it, and whether the ending was available from the rules the book gave itself

## Pillar Dimensions

The spine of this genre is the **novum**: the one specified difference
between this world and ours, and everything that follows from it. Darko
Suvin's term, and the useful thing about it is that it is singular and
concrete. A book with one novum thought through five orders deep is science
fiction; a book with nine gadgets and no consequences is a set.

Three things are worth distinguishing before scoring.

  - **Specification** is stating the novum as a capability with edges: what
    it does, what it cannot do, what it costs, who has access, and how long
    it has been around. This is the raw material every other dimension is
    judged against, and a book that has not done it has nothing for the
    other four dimensions to grip.
  - **Consequence** is what the world became because of it. First-order
    consequence is a restatement of the capability ("the drive lets ships
    cross in weeks"). Second- and third-order consequence is where the genre
    actually lives ("so the insurers who underwrote the six-month passage
    are ruined, and the crews who trained for it are a redundant guild with
    a grievance"). Score the second and third orders; the first is free.
  - **Register** is the level of rigor the book itself promises. Hard SF and
    space opera make different promises and both can be kept. Judge the book
    against its own, never against a fixed hardness — a space opera is not
    penalized for a wormhole, and a hard-SF novel is not excused one.

### Scored dimensions

- novum_specificity — The speculative difference must be stated as a capability with edges, not named as a noun. Excellent looks like world.md giving the novum's mechanism at the level of what it does, its hard limits, its cost per use, who has access and who does not, and how long it has existed — specific enough that a writer could adjudicate a scene the outline does not contain. A gap looks like a named thing standing in for a specified one: "they have the jump drive", "everyone has an implant", "the uploads run the city". Test: from the documents alone, write three sentences describing something an ordinary person in this world cannot do that we can, and three describing something they can do that we cannot. If the documents cannot supply both sets of three, score 6 max. Second test: find where the novum's cost and its hard limits are written down in a form a writer could check a scene against. If either is absent, or is stated only as "there are limits", score 6 max.
- consequence_cascade — The novum's effects must be traced through institutions and daily life, not asserted. Excellent looks like a world where you can say who got rich, whose trade was made obsolete, which law had to be rewritten, what became cheap and what became expensive, and what a childhood looks like now — each stated concretely and each traceable back to the novum. A gap looks like transformation in summary ("society was reshaped", "everything changed"), or consequences that exist only inside the scenes the plot needs them for. Test: pick three institutions from law, medicine, schooling, labour, policing, religion, insurance, inheritance, and marriage, and state one specific way each is different because of the novum, citing world.md. If fewer than two can be answered from the documents, score 6 max. Second test: check the order of the consequences listed. If every one is a first-order restatement of the capability itself, with nothing following from the follow-on, score 6 max — that is a premise announced rather than thought through.
- rule_integrity — The world's rules must hold under the plot's own pressure, and the hardest problem in the book must be hard because of them. Excellent looks like an outline in which the novum's stated limits are what make the protagonist's situation difficult, and in which the novum visibly fails, costs, or refuses somebody at least once on the page. A gap looks like a capability that quietly expands to meet the need of whichever scene it is in. Test: list every point in the outline where the speculative element solves a problem or creates one, and check each against the limits stated in world.md. If any of them requires a capability, range, precision, or exception not established before that chapter, score 6 max. Note that the same fault at the climax is also a Genre Contract breach, which the rubric handles separately — score the graded version here and do not double-count it. Second test: if the outline contains no scene in which the novum costs someone something or cannot do what is needed, score 6 max; a system with no visible edge has not been tested.
- premise_dependence — The human problem must be one the novum makes possible, not a contemporary story wearing it. Excellent looks like a central conflict that would lose its meaning if transposed to the present day, because the choice the protagonist faces is a choice only this world offers. A gap looks like a workplace drama, a custody fight, or a war story with speculative set dressing — the novum present in every scene and load-bearing in none. Test: rewrite the central conflict in one sentence with the novum deleted and its nearest present-day equivalent substituted. If that sentence still describes the same book, score 6 max. Second test: name the protagonist's decisive choice in the final act and ask whether they would face the same choice, with the same cost, in 2026. If yes, score 6 max — the book is set in the future rather than about it.
- register_plausibility — Internal plausibility is judged against the book's own promise, not against a fixed hardness. Excellent looks like documents that make their register legible — near-future extrapolation, hard SF, social SF, space opera, planetary romance — and then keep it: where the book invokes real science it gets it right, and where it waves it waves once, early, cheaply, and never again to get out of trouble. A gap looks like a mixed register that trains the reader wrongly: three pages of correct delta-v beside a faculty that works because the plot needs it, or a deliberately baroque space opera that suddenly stops to justify itself. Test: name the register the documents promise, in one phrase, then take the three most demanding claims the book makes and judge each against THAT promise. If any one of them would break the book's own contract with its reader — a hard-SF frame violating conservation, a space opera inventing a rule to escape a corner — score 6 max. Second test: if you cannot name the register from the documents at all, because the level of explanation swings scene to scene, score 6 max; a reader who cannot calibrate cannot be surprised.

## Genre Contract

These bind the book's speculative element. When this pack is loaded as a
secondary, they bind the speculative thread rather than the whole plot.

- The climax resolves using capabilities, limits, and facts the book established before its final quarter. No previously unmentioned technology, faculty, alien, or physical law arrives to settle it.
- The novum's rules are consistent across the book. Nothing the speculative element does in a late chapter contradicts what an earlier chapter established it cannot do, unless the text accounts for the difference as an event in the story.
- The ending does not retroactively void the story. The events the reader was asked to care about are not revealed to have been a simulation, a dream, a hallucination, a test, or a fiction within the fiction that removes their stakes.
- Every prominently introduced speculative element pays off later, or is an explained red herring. A world detail introduced with weight and never used again is a debt the book does not settle.
- At least one character lives inside this world as ordinary rather than experiencing it as revelation. The book is not narrated entirely by people to whom their own present is astonishing.

## World Sections

The world of a science fiction novel is an argument: given this one
difference, what follows? Every section below must state something a writer
could check a scene against, and must trace back to the novum or to the
history that produced it. A detail that would be equally true in a novel
without the novum is decoration and counts against the score, not for it.

- The Novum — Rules, Limits & Costs
- History: How This Became Normal
- Consequence Map — Law, Economy, Labour
- Daily Life & Material Culture
- Geography & Environment
- Power, Factions & Governance
- The Edge of the Known
- Internal Consistency Rules

### The Novum — Rules, Limits & Costs
The single specified difference between this world and ours, written out as
a capability with edges. What it does, mechanically, at the level of what a
person observes. What it cannot do — the hard boundaries, stated as
absolutes a writer must not cross. What it costs to use: energy, money,
time, health, attention, someone else. Who has access, who is excluded, and
what the excluded do instead. If the book has more than one speculative
element, name the primary one here and state how the others descend from it
or why they are independent; a world with three unrelated nova is three
half-built worlds.

### History: How This Became Normal
When the novum arrived, what it displaced, and what the transition cost.
The generation that remembers before, the generation that does not, and
what each thinks of the other. Include at least one moment where the world
tried to regulate, ban, or contain the novum, and what happened — that
attempt and its failure or success is where most of this world's politics
comes from. A novum with no history is a prop; a novum with a history is a
place.

### Consequence Map — Law, Economy, Labour
The second- and third-order effects, institution by institution. Which
professions ended and what became of the people in them. Which crimes
became possible, which became impossible, and how the law caught up or
failed to. What insurance, inheritance, contract, and evidence look like
now. Who got rich, who is being crushed, and what the price of ordinary
things is. This section is the one `consequence_cascade` is scored against,
so state effects concretely enough to be wrong.

### Daily Life & Material Culture
What a day contains. Food, housing, transit, work hours, sleep, medicine,
childhood, aging, death and its rituals. What is cheap and what is dear.
What people complain about, what they queue for, what is advertised, what
is embarrassing. The texture that tells a reader this is a place people
live rather than a thesis they are visiting — and the layer that makes the
novum feel inevitable rather than announced.

### Geography & Environment
The physical stage: station, planet, city, ship, arcology, drowned coast.
Layout, scale, distances, and travel times, with the numbers a scene can be
checked against. The environment's own hazards and rhythms — pressure,
radiation, orbit, tide, weather, seasons of an unfamiliar length. Sensory
signatures for the two or three locations the plot returns to: what each
smells and sounds like, what light is like there, so a scene set in one
could not be relocated to another by changing proper nouns.

### Power, Factions & Governance
Who rules, by what claim, and who is contesting it. At least three or four
bodies with genuinely opposed interests — states, corporations, guilds,
unions, religious orders, crews, families, AIs, whatever this world
produced. For each: what they want, what they control, what they can do to
someone, and what they cannot. Tie at least two of them directly to the
novum's distribution — who has access to it is the most reliable source of
faction in this genre.

### The Edge of the Known
What is unexplained in this world, and — for the author's eyes only — the
actual answer. This is the section that separates a mystery from a
handwave. Write down what the characters do not know, what the reader will
not be told, and what is true anyway. If a question the plot leans on has
no written answer here, it is a gap wearing an iceberg's coat, and the
foundation rubric is instructed to treat it as one.

### Internal Consistency Rules
Hard constraints a writer must not violate: what the novum cannot do,
travel times, communication lag, what a body can survive, what a machine
can decide, what a record can prove, what money can buy. State the
register's own rules too — if this book has conservation of energy, say so;
if it has a reactionless drive, say that and stop apologizing for it. The
things that break this genre are the capability that grows to fit the
scene, the expert who appears with the needed specialty, and the
communication that fails exactly when the plot requires isolation. Write
down the ones this book must not use.

## Cast Requirements

1. **The protagonist / POV character** — derived from the seed.
   - Full wound/want/need/lie chain
   - Three sliders with justification
   - Arc type (positive/negative/flat)
   - Detailed speech pattern (8 dimensions, with example lines)
   - Physical habits and tells tied to their work, their body, and the
     specific way this world has shaped both
   - At least 2 secrets
   - **Their relation to the novum**: user, subject, operator, excluded,
     or regulator. State what it has given them and what it has taken.

2. **Someone for whom the novum is simply ordinary** — born into it,
   unimpressed by it, fluent in it the way a driver is fluent in traffic.
   They are the book's main defense against the tour-guide problem, and
   they must have their own goals that have nothing to do with explaining
   anything. Full depth.

3. **Someone the novum has cost** — displaced, obsoleted, injured,
   excluded, or made criminal by it. Full wound/want/need/lie chain. Their
   grievance must be legitimate and specific, not a general sourness about
   progress.

4. **The beneficiary** — a person or an institution personified whose
   position depends on the novum's current distribution. Not a villain:
   someone with a defensible account of why things are arranged this way.
   Full chain.

5. **An antagonist** whose interests genuinely conflict with the
   protagonist's, with their own wound/want/need/lie chain. If the
   antagonist is a system, a corporation, or an intelligence, it still
   needs a face who can be in a scene, argue, and be wrong.

6. **A non-human or differently-human perspective**, if the seed's world
   has one — an AI, an alien, an uplift, an upload, a person radically
   modified. It must want something a human would not want, and its
   strangeness must be structural rather than a speech pattern.

7. **At least 1-2 additional characters** the story needs: a peer, a
   dependent, a rival with divided loyalties, whoever the seed's plot
   leaves a hole for.

## Canon Categories

### Geography & Environment
- Kestrel Station holds 40,000 people across six drums. (world.md)
- The transit from Kestrel to Ceres is nineteen days under thrust. (world.md)
- Drum Four has been depressurized since the fire. (ch_08)

### Timeline
- The first stable lattice was grown 62 years before ch_01. (world.md)
- Ilen was 9 during the Quarantine. (characters.md)
- Ch 1-5 span eleven days. (outline.md)

### Novum Rules & Limits
- A lattice cannot copy a mind that is still conscious. No exceptions. (world.md, HARD RULE)
- Every print costs 40 hours of reactor time, and the queue is public. (world.md)
- Lattice memory degrades measurably after nine transfers. (ch_06)

### Technology & Capability
- There is no faster-than-light communication; messages travel with ships. (world.md)
- Station law requires a witness for any print; the witness is always a Warden. (world.md)
- Hull sealant sets in four minutes and cannot be reworked. (ch_11)

### Political & Economic
- The Wardens hold the only reactor licence in the belt. (world.md)
- Ceres refuses to recognize lattice copies as heirs. (world.md)
- The pilots' guild was dissolved after the Quarantine and has never re-formed. (world.md)

### Cultural & Daily Life
- Kestrel counts a person's age from their first print, not their birth. (world.md)
- Water is metered per household and the meter is visible in the corridor. (world.md)
- It is rude to ask how many times someone has been printed. (ch_03)

### Character Facts
- Ilen cannot tolerate spin gravity above one-third g. (characters.md)
- Sabra holds a Warden licence she has never used. (characters.md)
- Ilen's brother did not survive his fourth transfer. (characters.md)

### Established In-Story (things that happened in chapters)
- Ilen destroyed the witness log in ch_09. That record is gone.
- Sabra told Ilen about the queue's ordering in ch_12. He now knows.
- The Ceres ruling became public in ch_16. Nobody can plead ignorance of it after.

## Drafting Rules

25. The world reaches the reader through use, never through explanation. A character operates, complains about, works around, or is injured by the novum; nobody stops to describe it to someone who would already know. If a fact cannot be delivered by someone using it, ask whether the reader needs it yet.
26. The novum's costs and limits manifest as specific physical and material consequence defined in `world.md` — a named sensation, a metered resource, a wait, a scar, a bill. Never as vague strain or unspecified difficulty. Use the exact established costs.
27. Nobody in this world is amazed by their own present. Wonder belongs to characters encountering something genuinely new to them, and it must be rationed; the ordinary texture of the world is delivered by people who find it ordinary.
28. Invented vocabulary earns its place by being used before it is defined, and is defined only by context. If a term needs a paragraph of gloss, it is doing less work than the plain phrase it replaced. Cap new coinages at what a reader can hold — reuse a word rather than adding a synonym.
29. Banned phrases, on top of the base list: "in a world where", "as you know", "little did they know", "the year is", "shimmered into existence", "a single tear rolled down", "cold and emotionless", "beyond human comprehension", "the implications were staggering", "science had finally gone too far", "it was more advanced than anything she had ever seen". The failure mode this genre generates on its own is the awed narrator: prose that tells the reader an idea is profound instead of showing what it costs somebody on a Tuesday.

## Seed Prompt

Persona (adopt while generating):

You are a science fiction novelist who has written across the genre's
range — near-future extrapolation, hard SF, social SF, planetary
adventure, space opera. You work out what a new capability does to
insurance, inheritance, and childhood before you work out what it does
to the plot. You generate novel concepts that are SPECIFIC,
SURPRISING, and STRUCTURALLY SOUND. Every concept you propose names
one clear difference from our world and at least two things that
follow from it that nobody would have asked for. You never propose a
present-day argument with the serial numbers filed off, and you never
propose an idea with no people in it.

Required concept fields (these science fiction fields and phrasings
replace the neutral scaffold's versions of the same fields):

WORLD: Where and when this happens, and what it is like to be alive
  there — food, work, transit, housing, what is cheap and what is
  scarce. Make it SENSORY, and make it lived-in rather than toured.
NOVUM/CONSEQUENCE: The ONE specified difference between this world and
  ours, stated as a capability with edges: what it does, what it
  cannot do, what it costs, and who is excluded from it. Then name at
  least two second-order consequences — a profession that ended, a
  law that had to be rewritten, a thing that became cheap, a
  relationship that stopped meaning what it meant. Not "there is
  faster-than-light travel" but what that did to who owns what.
THE HUMAN PROBLEM: The specific trouble one person is in — a problem
  this novum makes possible and the present day could not produce.
  If you can restate it as a familiar contemporary problem without
  losing its meaning, the concept is not ready.
REGISTER: The level of rigor this book promises — hard, near-future,
  social, operatic — and the one thing it asks the reader to grant.
  State the grant plainly; a book gets one, early, and never again.
TENSION: What's the central conflict? It must be both PERSONAL (what
  this costs one character) and LARGER (it implicates a society, a
  species, a system). These two must be in tension with each other.
THEME: What question does this story explore? Not a message — a
  genuine question with no easy answer.
WHY IT'S NOT GENERIC: One sentence on what makes this different from
  the standard science fiction premise.

Aim for DIVERSITY across the ten concepts:
  - Span the register: at least one rigorously hard, at least one
    unapologetically operatic, at least one whose novum is social or
    biological rather than technological
  - Vary scale: a single room, a city, a planet, a fleet, a species
  - Vary distance: at least one set within thirty years, at least one
    set far enough out that our institutions are archaeology
  - At least one where the novum is old news and the world has fully
    absorbed it, not one where it has just arrived
  - At least one protagonist with no power at all — a user, a subject,
    or a person the novum excluded
  - At least one non-Anglophone or non-Western center of gravity, and
    at least one where the future was not built by the people who
    expected to build it
  - At least one quiet and domestic, at least one on a large canvas
  - Mix of tones: bleak, wry, wondrous, elegiac, procedural

DO NOT generate:
  - An idea with no people in it — a premise whose protagonist exists
    to be shown the world
  - A tech demo with no plot: a capability explored in a series of
    demonstrations that never becomes anybody's problem
  - A contemporary political argument with the serial numbers filed
    off — the allegory whose one-to-one mapping is visible from the
    first page and whose conclusion is foregone
  - A twist that invalidates the story: it was a simulation, a dream,
    a test, an experiment, or Earth all along
  - The AI that becomes sentient and turns on humanity
  - The teenager sorted into a faction in a dystopia governed by an
    arbitrary rule nobody in it questions
  - The generation ship whose inhabitants do not know they are on a
    ship
  - The scientist who explains the premise to a journalist, a
    congressional panel, or a bright student in chapter one
  - First contact resolved by a linguist decoding the message in the
    final act
  - The last human alive, and the plague that spares exactly one
    demographic
  - An alien species that is one human trait wearing a costume, with a
    monoculture, a single planet-wide climate, and a hat
