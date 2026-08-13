---
{
  "name": "thriller",
  "label": "Thriller",
  "role": ["primary", "secondary"],
  "pillar_label": "Threat & Escalation",
  "weights": {"pillar": 40, "character": 25, "structure": 25, "craft": 10},
  "beat_system": "save-the-cat",
  "content_register": {},
  "conflicts_with": [],
  "shape": {
    "chapters": [40, 55],
    "words": [85000, 100000],
    "chapter_words": 1900,
    "pov_default": "third limited past, alternating between the protagonist and the antagonist"
  },
  "artifacts": []
}
---

## Framing

- genre_noun — "thriller"
- pillar_noun — "threat"
- comps — Thomas Harris, John le Carré, Patricia Highsmith, Gillian Flynn, Don Winslow, Attica Locke
- seed_persona — a thriller novelist who has written across the range from domestic suspense to espionage to the brutal end of crime, who builds the antagonist's plan first and the protagonist's disadvantage second, and who never proposes a danger that one phone call would end
- reader_persona — a thriller reader who finishes a book in two sittings, who reads for the next turn rather than the sentence, and who stops trusting a book the moment a character does something stupid so the plot can continue
- writer_persona — a working suspense novelist and editor who reads for whether the pressure actually rises, whether the antagonist has a method or only a reputation, and whether the protagonist's defeats cost them anything they had

## Pillar Dimensions

A thriller lives or dies on pressure. Not on violence, not on pace as a
prose texture, but on a reader's belief that something bad is coming, that
it is coming faster than the protagonist can move, and that it will land on
someone they can name. Everything below tests that belief.

Three things are worth distinguishing before scoring.

  - **Danger** is what the antagonist can actually do — capability,
    resources, reach, and method. It is a set of facts about the world.
  - **Pressure** is what the structure does with that danger: the clock,
    the narrowing of options, the rising cost of each attempt. Danger
    without pressure is a monster in a cage.
  - **Threat display** is neither: a book telling the reader to be afraid
    through weather, ominous narration, and reputation. It is the cheapest
    thing in the genre and it should score nothing. If you find yourself
    scoring a dimension well on the strength of atmosphere alone, the score
    is wrong.

### Scored dimensions

- antagonist_capability — The antagonist's power must be established, specific, and bounded. Excellent looks like a documented method: what they can do, how they do it, what it costs them, what resources and access they hold, how they learn what they learn, and — critically — what they cannot do. A gap looks like capability by reputation: "he always finds them", "she has people everywhere", an opponent whose reach is whatever the current chapter requires. Test: take the three worst things the antagonist does in the outline and, for each, name the resource, the access, and the piece of information that made it possible, citing world.md or characters.md. If any one of the three cannot be accounted for, score 6 max. Second test: state one specific thing the antagonist cannot do, and find the scene where that limit costs them. If the documents state no limit, or state one that never binds, score 6 max — an unbounded antagonist generates dread but not suspense, because nothing the protagonist does can matter.
- clock_pressure — There must be a deadline the reader can see and count down. Excellent looks like a clock that is concrete (a date, a flight, a surgery, a trial, a shipment, a body that will be found on Monday), stated early, referenced as it runs, and enforced when it expires. A gap looks like urgency asserted in adverbs — everyone hurrying, nobody late for anything — or a deadline that quietly slips when the plot needs more room. Test: name the deadline, name the chapter it is established in, and list every chapter that references its remaining time. If the clock is established after the first quarter, or is referenced in fewer than a third of the chapters, score 6 max. Second test: check what happens when it runs out. If the outline lets it pass without a consequence the plan states, or resets it by an event outside the protagonist's control, score 6 max.
- escalation_ladder — Each turn must cost more than the last. Excellent looks like a ladder you can list: at every stage the protagonist has fewer options, less help, less to fall back on, and the antagonist has moved closer or taken something. A gap looks like repetition at a fixed intensity — three chase sequences, three near-misses, three threatening messages — motion that resets to the same state. Test: walk the outline and, for each act, write down what the protagonist has lost that they had at the start of it: an ally, a resource, a safe place, a piece of standing, an option. If any quarter of the book takes nothing away, score 6 max. Second test: compare the cost of the midpoint reversal with the cost of the Act I catalyst, and the All Is Lost with the midpoint. If any later turn costs the protagonist less than an earlier one, the ladder has a rung going down; score 6 max.
- protagonist_competence — Setbacks only mean something if the reader has seen the protagonist be good at something. Excellent looks like a specific, demonstrated skill — shown in use, early, on a problem they solve — that the antagonist then defeats or turns against them. A gap looks like a protagonist defined by what is done to them: reactive throughout, surviving by luck, or conversely a protagonist who never fails because their competence has no stated edge. Test: name the protagonist's competence in one phrase, find the chapter in the first quarter where it is demonstrated on a problem they actually solve, and find the later chapter where it fails or is used against them. If any of the three is missing, score 6 max. Second test: count the chapters in which the protagonist acts on a plan of their own rather than responding to the antagonist's move. If that is under a third of the book, score 6 max — a protagonist who only reacts is a passenger, and their defeats read as weather.
- personal_stakes — The threat must land on someone the reader can name, and stay landed. Excellent looks like a danger whose worst outcome is specific and intimate — this child, this job, this sister, this reputation, this one person finding out — and which stays that way even when the scale grows. A gap looks like stakes that inflate into abstraction: a city, a network, a country, thousands of unnamed people, an outcome no scene can show. Test: state the worst thing that happens if the protagonist fails, in one sentence, naming the people it happens to. If that sentence contains no named character, score 6 max. Second test: check the final act. If the book abstracts upward at the climax — the personal jeopardy replaced by a larger one the reader has no relationship with — score 6 max. Note that suffering is not stakes: pain inflicted on a character the plan has not made the reader care about raises the volume, not the tension, and does not earn points here.

## Genre Contract

These bind the book's central line of threat. When this pack is loaded as a
secondary, they bind the suspense thread rather than the whole plot.

- The danger survives sensible behaviour. At every point where an ordinary competent person would call the police, leave town, tell a spouse, or hand the problem to someone with more power, the plan states specifically why that option is unavailable, already tried, or worse than the danger.
- The antagonist's every move against the protagonist is accountable. For each one the plan can say who did it, with what resource, and how they knew where to be. Nothing happens because the antagonist is uncanny.
- The protagonist survives the climax through something they did, knew, chose, or built earlier. Not through coincidence, a rescuer arriving unbidden, or the antagonist becoming suddenly incompetent.
- Every threat the book raises is resolved on the page — paid off, transferred, or explicitly defused. A danger that is simply dropped is a promise broken.
- Nothing is threatened that the book will not follow through on somewhere. A book that repeatedly raises harm it never delivers in any form has trained its reader not to believe it.

## Plot Architecture

A thriller's shape is not a three-act novel run faster. The disturbance
arrives before the reader has finished being introduced to anyone, the
chapters are short and end on turns, and the second act is a descent rather
than an investigation. `beat_system` remains `save-the-cat`, and the
outline should label chapters with its beats — but placed at the marks
below, with the Catalyst pulled far forward of the usual 10%.

KEY PLOT ARCHITECTURE (adapt exact chapter numbers to the seed; these are
proportional guideposts across a 40-55 chapter novel):

- **The disturbance** (chapter 1, and no later than 5%): something is
  wrong on the first page. Not the full threat — the first crack. The
  protagonist's ordinary world is established around it and underneath
  it, never before it.
- **Act I** (0-20%): the protagonist's competence is demonstrated on a
  problem they solve, the person or thing they cannot afford to lose is
  established, and the Catalyst commits them. By the end of Act I the
  clock is running, the protagonist knows they are in trouble, and the
  ordinary remedies have been closed off on the page.
- **Act II Part 1** (20-50%): the protagonist acts on their own plan and
  it half-works. The antagonist's capability is revealed in pieces, each
  larger than the reader assumed. Midpoint: a reversal that reframes the
  threat — it is closer, or larger, or has been inside the protagonist's
  circle the whole time — and the protagonist shifts from evading to
  pursuing, or the reverse.
- **Act II Part 2** (50-75%): the antagonist takes things. An ally, a
  safe place, a resource, a piece of standing. The protagonist's options
  narrow chapter by chapter and every remaining one costs more. All Is
  Lost (around 75%): the protagonist loses the thing the book has been
  protecting, or learns they have been helping the antagonist.
- **Act III** (75-100%): the confrontation happens on the antagonist's
  ground, or on ground the antagonist chose, using something the
  protagonist established earlier. The clock expires inside this act, not
  after it. The resolution shows the cost — what was not recovered.

CONSTRAINTS:
- Most chapters end on a turn: new information, a reversal, an arrival,
  a decision made or foreclosed. A chapter that ends on a character
  going to bed with nothing changed is a chapter to fold into its
  neighbour.
- No two consecutive chapters at the same intensity. The genre's
  pacing comes from variance — a quiet chapter is what makes the next
  one land, and three loud chapters in a row read as one.
- The clock must be visible at least once per act, in a specific form
  the reader can count.
- The antagonist gets on-page presence before the halfway mark. An
  opponent who is only rumour for half a book cannot escalate, because
  the reader has nothing to measure the escalation against.
- The protagonist may be wrong, but must not be stupid. Every choice
  that leads them deeper must be the best available choice given what
  they know — which means the plan must state what they know.

## World Sections

The world of a thriller is a system of pressure and foreclosure: what the
antagonist can reach, where the protagonist can go, who could help and why
they will not, and how long there is. Every section below must close off a
possibility somewhere in the outline. A detail that rules nothing out is
decoration and counts against the score, not for it.

- The Threat
- The Antagonist's Machinery
- The Clock
- Geography, Escape & Concealment
- Authority: Who Could Help, and Why They Won't
- The Protagonist's Resources
- Internal Consistency Rules

### The Threat
What is actually going to happen if nobody stops it — stated plainly, in
full, for the author's eyes. Who is harmed, how, when, and why. The
antagonist's plan as they understand it, including the parts the
protagonist will never learn. Write the version of this book in which the
protagonist does nothing, and say how it ends. Everything else in this
document is measured against that.

### The Antagonist's Machinery
Capability as an inventory, not an aura. Money, people, weapons, access,
authority, technical skill, information sources. How they learn what they
learn — surveillance, an informant, a database, a habit of the
protagonist's they have studied. What each move costs them in exposure or
resources, because an antagonist who spends nothing cannot be pressured.
And the limits: what is out of reach, where they are blind, whom they
cannot touch. State at least two hard limits, and mean them.

### The Clock
The deadline, in concrete form: a date, a flight, a hearing, a shipment, a
surgery, a tide, a body that will be found. Who set it and whether it can
be moved. What specifically happens when it expires. Then the intermediate
markers — the points at which the protagonist can tell how much time is
left — because a clock the reader cannot read exerts no pressure. If the
book has a second, personal clock (an illness, a pregnancy, a parole date,
a custody hearing), state how the two interact.

### Geography, Escape & Concealment
The map as a set of constraints: distances, travel times, borders,
checkpoints, cameras, the road that floods, the only ferry. Where a person
can be unobserved here and what it costs to get there. Where the
protagonist can run and what running forfeits. Sensory signatures for the
two or three locations the book returns to, specific enough that a scene
set in one could not be relocated to another by changing proper nouns.

### Authority: Who Could Help, and Why They Won't
The single most important section for this genre's credibility. Enumerate
every body an ordinary person would turn to — police, employer, family,
press, lawyer, doctor, embassy, union — and for each state precisely what
happens if the protagonist goes to them. "They wouldn't believe her" is not
an answer; state why, and what specifically she lacks. At least one of them
must have been tried already, on the page, with a consequence. If you
cannot fill this section, the book has an idiot plot and the Genre Contract
will catch it.

### The Protagonist's Resources
What the protagonist actually has: skill, training, money, allies, access,
information, and physical condition. Stated as an inventory so that the
book can spend it. Then the ledger of what they lose and when — this is
what `escalation_ladder` is checked against. Include what they are bad at
and what they will not do, because those are the walls the antagonist will
push them toward.

### Internal Consistency Rules
Hard constraints a writer must not violate: travel times, phone coverage,
who holds which key, how long a wound takes, what a record can show, how
long a person can go without sleep, what money is left. This genre has no
magic, which means the things that break it are coincidence, a phone that
dies exactly when isolation is needed, a skill the protagonist turns out to
have had all along, and a witness who arrives on cue. Write down the ones
this book must not use.

## Cast Requirements

1. **The protagonist** — derived from the seed.
   - Full wound/want/need/lie chain
   - Three sliders with justification
   - Arc type (positive/negative/flat)
   - Detailed speech pattern (8 dimensions, with example lines)
   - Physical habits and tells tied to their work and their wound
   - At least 2 secrets, at least one of which the antagonist can use
   - **Their competence**, stated as one specific thing they are good
     at, with the chapter in the first quarter where it is demonstrated
     and the later chapter where it fails them. It is scored under
     `protagonist_competence`, so it must be concrete enough to show.
   - **Their disadvantage**: what they lack that the antagonist has.

2. **The antagonist** — full wound/want/need/lie chain, plus a written
   method: capability, resources, access, information sources, cost per
   move, and at least two hard limits. Their goal must be legible and
   pursued for reasons that make sense from inside their life. An
   antagonist whose motive is that they are evil cannot be anticipated,
   and a reader who cannot anticipate cannot dread.

3. **The person the threat lands on** — whoever makes this personal: a
   child, a sibling, a patient, a partner, a witness the protagonist
   promised to protect. They need enough life on the page that the
   reader would miss them. A stake the reader has not met is an
   abstraction.

4. **The ally who becomes a cost** — someone who helps and is harmed for
   it, or who has to be spent. Full chain. Their loss is the most
   reliable rung on the escalation ladder, and it only works if they
   were a person first.

5. **The authority who is procedurally correct and useless** — the
   detective, manager, lawyer, or official who follows the rules exactly
   and cannot help. They must be competent and sympathetic; a stupid
   institution is a cheat, a constrained one is a plot.

6. **The insider** — someone inside the protagonist's circle whose
   loyalty is divided, compromised, or bought. What they gain and what
   they tell themselves about it. If the seed does not want a betrayal,
   this role becomes the person who knows more than they are saying for
   a reason that is not the threat.

## Canon Categories

### Geography & Access
- The cabin is fifty minutes from the nearest town, on one road. (world.md)
- There is no cell coverage past the ridge. (world.md)
- The service door to the loading bay does not lock from outside. (ch_07)

### Timeline & The Clock
- The extradition hearing is on the 14th. (world.md)
- Ch 1-9 span three days. (outline.md)
- Maren has been awake for thirty-one hours by ch_22. (ch_22)

### The Antagonist's Capabilities
- Voss can pull any plate through a contact at the county office. (world.md)
- Voss cannot cross into the reservation without being seen. (world.md, HARD LIMIT)
- Voss learned about the storage unit from the bank clerk in ch_10. (ch_10)

### Resources & Constraints
- Maren has $2,300 and no working card. (ch_04)
- Maren's car has a broken fuel gauge. (characters.md)
- The gun has five rounds and no more are available. (ch_15)

### Character Facts
- Maren was an EMT for nine years. She can read an injury. (characters.md)
- Devin cannot drive. (characters.md)
- Maren's sister does not know about the restraining order. (characters.md)

### Procedural & Institutional
- The restraining order is unenforceable across the state line. (world.md)
- The hospital must report a gunshot wound within one hour. (world.md)
- Maren cannot go to the police; her statement in 2019 is on record and contradicts her. (world.md)

### Established In-Story (things that happened in chapters)
- Maren burned the phone in ch_11. That number is gone.
- Devin saw Voss's face in ch_14. He cannot un-see it.
- The safe house was compromised in ch_28. It is not available again.

## Drafting Rules

25. End chapters on a turn — new information, a reversal, an arrival, a decision made or foreclosed. Target roughly 1,900 words per chapter; a chapter running well past that is usually two chapters with the cut in the middle of it.
26. Vary intensity deliberately. After a chapter of action or revelation, the next one earns its keep by being quieter and by costing the protagonist something anyway. Three loud chapters in a row read to a reader as one long chapter.
27. Threat is delivered through capability and consequence, never through atmosphere. Do not tell the reader to be afraid with weather, silence, or an ominous narrator; show what the antagonist can reach, and then let them reach it.
28. The protagonist may be wrong; they may not be stupid. Before writing a choice that leads them deeper, state on the page what they know and what they have already tried — then make the bad choice the best available one.
29. Every escalation takes something. If a chapter raises the pressure without removing an option, an ally, a resource, or a piece of standing, the pressure has not actually risen.
30. Banned phrases, on top of the base list: "little did she know", "it was already too late", "her blood ran cold", "time seemed to slow", "everything went black", "he was a ghost", "trained killer", "you have no idea who you're dealing with", "a chill ran down his spine", "he had a bad feeling about this", "she never saw it coming", "the man in the shadows smiled". Narratorial menace that promises danger without delivering a fact is this genre's slop — it fakes tension while giving the reader nothing to fear with.

## Seed Prompt

Persona (adopt while generating):

You are a thriller novelist who has written across the genre's range —
domestic suspense, espionage, legal, medical, crime, survival. You
build the antagonist's plan first and the protagonist's disadvantage
second, and you know that suspense comes from the reader
understanding the danger better than the character does. You generate
novel concepts that are SPECIFIC, SURPRISING, and STRUCTURALLY SOUND.
Every concept you propose has a threat that survives sensible
behaviour: you can say exactly why the protagonist cannot simply call
the police and go home. You never propose a danger that one honest
phone call would end.

Required concept fields (these thriller fields and phrasings replace
the neutral scaffold's versions of the same fields):

WORLD: The specific pressure system this happens inside — the job,
  the town, the institution, the border, the season, the money. Make
  it SENSORY, and make it constraining: distances, coverage,
  checkpoints, who would notice, where a person can be unobserved.
THREAT/CLOCK: Who or what is coming, stated as a capability rather
  than a reputation — what they can do, what resource lets them do
  it, how they find people, and at least one hard thing they CANNOT
  do. Then the clock: the concrete deadline, what happens when it
  expires, and who set it. If you cannot name the limit and the
  deadline, the concept is not ready.
WHY NOT THE POLICE: The specific reason the ordinary remedies are
  closed — already tried, actively dangerous, or foreclosed by
  something in the protagonist's own history. "Nobody would believe
  her" is not an answer; say why, and say what she lacks.
THE PROTAGONIST'S EDGE: The one thing this person is genuinely good
  at, how the story will demonstrate it early, and how the antagonist
  will turn it against them. Also what they lack that the antagonist
  has.
TENSION: What's the central conflict? It must be both PERSONAL (a
  named person the protagonist cannot afford to lose) and LARGER (an
  institution, a community, a system that is implicated). These two
  must be in tension with each other — the personal must sometimes be
  the wrong thing to protect.
THEME: What question does this story explore? Not a message — a
  genuine question with no easy answer.
WHY IT'S NOT GENERIC: One sentence on what makes this different from
  the standard thriller premise.

Aim for DIVERSITY across the ten concepts:
  - Span the subgenres: domestic, espionage, legal, medical, survival,
    corporate, political, crime
  - Span the register from bloodless to brutal; this pack constrains
    neither, so at least one should be tense without a body and at
    least one genuinely violent
  - Vary the antagonist: a person, an institution, a market, a
    process, someone the protagonist loves
  - Vary the protagonist's power — at least one with real
    professional authority and at least one with none at all
  - Vary the clock: a hard external deadline, a slow biological one, a
    countdown the protagonist sets themselves
  - Vary scale and geography: one confined to a single building, one
    across a border; at least one outside the Anglo-American default
  - At least one where the protagonist is guilty of something real
  - At least one where the right thing to do and the safe thing to do
    are the same, and the protagonist still cannot do it
  - Mix of tones: cold, propulsive, paranoid, grim, darkly funny

DO NOT generate:
  - The idiot plot — any premise whose danger evaporates the moment
    someone calls the police, tells a spouse, or leaves town, and
    whose only defense is that nobody does
  - The invincible antagonist: an opponent with no stated method,
    whose reach is whatever the current scene requires, who "always
    finds them"
  - Torture as stakes — extended suffering inflicted on a character
    in place of an escalating plan, or a captivity sequence standing
    in for a second act
  - A conspiracy that "goes all the way to the top" and is never
    specified past that phrase
  - The amnesiac who turns out to be an elite operative
  - The serial killer taunting the profiler with clues, and the
    killer with an elaborate thematic signature
  - Revenge for a murdered wife or child, where the dead person had no
    life of their own on the page
  - The ticking bomb under a landmark, and the plot to release a
    pathogen at a stadium
  - The spouse who is secretly an assassin, spy, or someone else
    entirely
  - The unreliable narrator whose unreliability is alcohol and whose
    testimony nobody believes for that reason alone
  - A protagonist saved at the climax by an authority figure who
    finally shows up
