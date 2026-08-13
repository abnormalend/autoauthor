---
{
  "name": "romantic-suspense",
  "label": "Romantic Suspense",
  "role": ["primary"],
  "pillar_label": "Relationship Under Threat",
  "weights": {"pillar": 40, "character": 28, "structure": 22, "craft": 10},
  "beat_system": "braided-beat",
  "content_register": {},
  "conflicts_with": ["romance", "thriller"],
  "shape": {
    "words": {"extended": [85000, 98000]},
    "chapter_words": 2500,
    "pov_default": "dual third limited past, alternating between the two leads, with optional short antagonist chapters at no more than one in six"
  },
  "artifacts": ["braid_map.md"]
}
---

## Framing

- genre_noun — "romantic suspense novel"
- pillar_noun — "braid of romance and threat"
- comps — Nora Roberts, Karen Rose, Tana French, Lisa Gardner, Laura Griffin, Attica Locke
- seed_persona — a romantic suspense novelist who builds the antagonist's plan and the couple's barrier as one object, and who never proposes a danger the couple's existence does not change or a romance the danger does not accelerate
- reader_persona — a romantic suspense reader who reads forty of these a year, who wants both the reunion and the arrest, and who stops trusting a book the moment she notices the love story and the case are only sharing a table of contents
- writer_persona — a working suspense-and-romance author who reads for whether the two plots are load-bearing for each other, whether the black moment and the threat's peak are the same event, and whether the couple's choice is what ends the danger

## Pillar Dimensions

Romantic suspense is not a romance with a subplot or a thriller with a
love interest. It is one plot with two readings. The danger is what puts
these two people in a room they cannot leave and keeps them honest in it;
the relationship is what gives the antagonist something to aim at. Remove
either and the other stops working.

That is the whole genre, and it is also its defining failure. The
commonest broken romantic suspense runs two competent plots on separate
tracks: the couple could fall in love with the killer deleted, and the
killer could be caught with the couple deleted. Every dimension below is
written to catch some version of that separation, and two of them —
`threat_forces_intimacy` and `romance_raises_stakes` — exist for nothing
else.

Three terms are used precisely below, and should be distinguished before
scoring:

  - **Adhesion** is the mechanism that keeps the leads in contact. In this
    genre it is normally the danger itself: a protective detail, a shared
    target, a witness and her handler, two people who cannot be seen
    separating. Adhesion is machinery, not a trope name.
  - **Leverage** is what the antagonist can do to one lead *through* the
    other. It is the romance's contribution to the suspense, and it must
    be legible before it is used.
  - **The barrier** is what keeps the leads apart for reasons the case's
    resolution does not touch. It is not the danger. A couple whose only
    obstacle is "not while this is going on" has no barrier; it has a
    schedule.

Cap discipline: every score cap below fires at 6, and the section carries
six dimensions, so the 7.0 pillar gate stays reachable with one or two real
defects on the page and closes when three land at once. The most severe
version of the separation failure is handled as a Genre Contract breach
rather than a punishing cap; where a dimension's criteria say so, do not
score the same fault twice.

### The braided beat vocabulary

`beat_system` is `braided-beat`. Its fifteen beats and their percentage
marks are enumerated in `## Plot Architecture` below, together with the
rule governing the point where the relationship curve and the threat
ladder collide. The outline labels chapters with those beat names, and
`outline_completeness` is scored against those marks.

### Scored dimensions

- threat_forces_intimacy [cap 6] — The danger must be the mechanism that produces the intimacy, not the weather it happens in. Excellent looks like an adhesion with real machinery — the leads cannot separate without one of them dying, losing the case, or breaking a promise the book has shown costs something — and like confessions extracted by circumstance: things each lead says because tonight might be the last chance, because the other one has already seen the worst, because the lie is no longer survivable. A gap looks like forced proximity with an unlocked door: a safe house either lead could leave, a protective detail either could refuse, a bodyguard contract with no penalty for walking. Test: take the three scenes in which the relationship moves furthest, and for each name (a) the specific fact of the danger that made the scene possible and (b) the specific thing said or done that would have been withheld in safety. If fewer than two of the three can be answered on both counts, score 6 max. Second test, the romance-side deletion: delete the threat plot from the outline entirely and read the relationship beats. If they still land at the same marks in the same order, the danger is decoration and the intimacy was going to happen anyway; score 6 max. This graded cap is the ordinary version of the fault — if `## Genre Contract`'s separability promise has also been recorded as breached, do not count it twice.
- romance_raises_stakes [cap 6] — The antagonist's position must be sharper because the couple exists. Excellent looks like leverage the plan can state: the antagonist has a move available only because these two matter to each other, the move is telegraphed before it is played, and at least twice a lead makes a materially worse tactical choice for the other's sake — a worse choice the plan can name the better alternative to. A gap looks like a love story the antagonist never notices, or its cheapest counterfeit: the love interest abducted in the final act, which counts only when the leverage was legible earlier and the abducted lead acts rather than waits. Test: state the antagonist's leverage in one sentence, then state what that leverage would be if the two leads had never met. If the two sentences are the same, score 6 max. Second test, the suspense-side deletion: delete the romance and walk the antagonist's moves. If the same sequence still catches them — same evidence, same errors, same endgame — the relationship is not load-bearing; score 6 max. Third test: count the chapters in which a lead's judgement is compromised by the other in a way the plot spends. If fewer than two, score 6 max. As above, do not double-count a recorded contract breach.
- barrier_beyond_the_threat [cap 6] — Something must keep these two apart that surviving the danger does not fix. Excellent looks like a barrier from the leads' ordinary lives with a mechanism behind it: a jurisdiction, a case one of them will have to testify in, a posting on another coast, a child whose custody depends on staying out of the file, a professional rule with a named enforcer. A gap looks like "we can't do this while this is going on" — an obstacle the arrest dissolves — or a distrust that exists only because the danger manufactured it. Test: write the epilogue in which the antagonist is convicted on page one. If nothing remains in the couple's way, the book has a schedule rather than a barrier; score 6 max. Second test: identify what causes the break at the Collision. If it is only danger-induced suspicion — one lead believing the other is the antagonist's agent — and that suspicion is dispelled by a fact rather than by a choice either of them makes, score 6 max.
- antagonist_method_and_retrospect [cap 6] — Capability must be bounded and the plan must be legible backwards. Excellent looks like a documented method — resources, access, how they learn what they learn, what each move costs them, and at least one hard limit that binds in a scene — plus a reveal a rereader can trace: the chapters that carried the antagonist's shape were doing other work at the time. A gap looks like reach by reputation ("he always finds them"), or a reveal built on information first supplied in the reveal chapter. Test: take the three worst things the antagonist does and, for each, name the resource, the access, and the piece of information that made it possible, citing world.md or characters.md. If any one cannot be accounted for, score 6 max. Second test: list the chapters that carry a clue to the antagonist's identity or plan. If there are fewer than three, or if the earliest falls after the midpoint, score 6 max. Third test: state one thing the antagonist cannot do and find the chapter where that limit costs them. If the documents state no limit, or state one that never binds, score 6 max.
- braided_escalation [cap 6] — Both ladders must rise, interleaved, and neither may go flat while the other climbs. Excellent looks like a chapter-by-chapter braid in which each threat rung is answered by a relationship rung within two chapters and each relationship rung raises what the threat can take; and like a Collision where the black moment and the threat's peak are one event under two readings rather than two events filed near each other. A gap looks like a book that alternates in blocks — five chapters of investigation, then four of courtship — or an escalation ladder with a rung going down. Test: build the braid map (see `## Artifacts`) and mark, per chapter, whether the relationship state changed and whether the threat state changed. If four or more consecutive chapters change only one strand, score 6 max. Second test: locate the black moment and the threat's worst move. If they are more than three chapters apart, or if the black moment is caused by a third party's interference while the threat merely continues in parallel, score 6 max. Third test: compare the cost of each act's turn to the one before it, on both strands. If any later turn costs less than an earlier one, score 6 max.
- convergent_resolution [cap 6] — The act that ends the danger and the act that wins the relationship must be the same act, or the first must be caused by the second. Excellent looks like a single decision at the climax that a named lead makes, at a stated cost, which simultaneously neutralizes the threat and answers the barrier — the grand gesture and the takedown as one move. A gap looks like sequential resolution: the antagonist is dealt with, and then, three pages later, the couple talks it out. Test: name the climactic decision, name which lead makes it, name what it costs them, and name how it does both jobs. If the danger ends instead by an arrest a third party makes, by the antagonist's unforced error, or by a rescuer arriving unbidden, score 6 max, and note that the same fault is a contract breach — record it once, there. Second test: for EACH lead, name the belief they hold in chapter 1 that they cannot hold at the end, and the scene in which the other lead and the danger together made it untenable. If you can do this for only one of the two, score 6 max. Third test: measure the gap between the threat's resolution and the couple's. If the reunion needs a chapter of talking after the danger is fully over to happen at all, the two plots resolved separately; score 6 max.

## Genre Contract

These bind the book's central relationship and its central line of threat,
which in this genre are the same object read two ways.

- The central relationship resolves HEA (happily ever after) or HFN (happy for now): both leads alive, together, and choosing each other on the page at the end. Romantic suspense readers treat a central relationship that ends in separation, death, or ambiguity as a broken promise rather than an artistic choice — a book that wants that ending is a crime novel with a love story, and it should not use this pack.
- Both leads are present for the resolution of the relationship, and it does not happen off-page, in summary, or in an epilogue that skips the reconciliation itself.
- Neither plot can be deleted. Remove the threat and the relationship loses beats it cannot reach by other means; remove the relationship and the antagonist loses moves and the protagonists lose the mistakes that shape the plot. If both plots survive the other's deletion intact, this promise is breached.
- The threat is neutralized by a choice a lead makes — something they did, knew, chose, or built earlier — and not by coincidence, by the antagonist's sudden incompetence, or by a rescuer who arrives unbidden. Where an institution closes the case, it closes it on evidence a lead obtained and delivered at a cost the book shows.
- The antagonist's plan is legible in retrospect. At the reveal, a reader can point to earlier chapters that carried it while appearing to do other work. Nothing about the antagonist's identity, method, or motive arrives for the first time in the chapter that explains it.
- The danger survives sensible behaviour. At every point where an ordinary competent person would call the police, leave town, or hand the problem to someone with more power, the plan states specifically why that option is unavailable, already tried, or worse than the danger.
- The endangered lead acts. Whichever of the two the threat lands on hardest makes at least one decision in the final quarter that changes the outcome. A lead who spends the third act as an object to be recovered is a hostage, not a protagonist.
- Every threat the book raises is resolved on the page — paid off, transferred, or explicitly defused.
- Neither lead's consent is treated as an obstacle to be overcome. Fear is not consent and rank is not consent: intimacy under threat must still be chosen by both, and a lead's protective authority — bodyguard, officer, agent, doctor — is never used to overrule the other's refusal.

## Plot Architecture

Two curves run the length of this book. The relationship curve is
Romancing the Beat's four phases; the threat ladder is a thriller
escalation with a visible clock. `beat_system` is `braided-beat`, which is
the two of them woven into a single fifteen-beat vocabulary. The outline
labels chapters with these beat names, at these marks. Marks are
proportional guideposts across a 34-39 chapter novel; adapt exact chapter
numbers to the seed.

The strands are marked **T** (threat), **R** (relationship), and **B**
(braid — a beat that belongs to both and must be written as one event).

- **The Crack** (T, chapter 1, no later than 3%) — something is already wrong on the first page. Not the whole threat: the first crack. Both leads' ordinary lives are established around it and underneath it, never before it.
- **Two Lives** (R, 0-8%) — each lead in their own life, each with a goal that is not the other person, each with an obligation older than the book.
- **Adhesion Under Threat** (B, 8-12%) — the danger is what forces continued contact. The No Way Out and the reason neither can walk away are the same fact, stated as machinery: what would have to break for them to separate, and what separating would cost each of them.
- **The Threat Named** (T, ~15%) — the antagonist's capability is shown rather than reported, and the ordinary remedies are closed off on the page. By here the clock is running and the reader can count it.
- **Inkling of Desire** (R, 15-25%) — the first noticing, rooted in what the danger has already exposed about each of them.
- **First Direct Move** (T, ~25%) — the antagonist acts on these two specifically. Something is lost: a resource, a safe place, a person.
- **Forced Truth** (B, 25-40%) — the danger extracts an admission neither would have volunteered in safety, and that admission becomes usable — by the other lead, and later by the antagonist.
- **Midpoint of Love** (R, ~50%) — the relationship becomes real to both, and what losing it would cost becomes concrete.
- **Midpoint Reframe** (T, ~50%) — the threat is closer, larger, or has been inside the circle all along. These two beats share a chapter or sit adjacent, and one causes the other: the reframe is what makes the love undeniable, or the love is what makes the reframe lethal.
- **Leverage Acquired** (B, 50-62%) — the antagonist learns the couple exists and the relationship becomes the lever. Simultaneously the Inkling of Doubt: the barrier's original terms reassert themselves under the danger's pressure, for reasons the first half planted.
- **Shields Up / The Threat Inside** (B, 62-72%) — the leads pull apart to protect each other or to protect themselves, and that separation is precisely the opening the antagonist has been waiting for. Retreat and vulnerability are one movement.
- **The Collision** (B, 72-80%) — the black moment and the threat's peak, as one event. See the collision rule below.
- **Dark Night, Apart and Hunted** (R+T, 80-88%) — each lead alone, each still in danger, each confronting the belief they actually hold. The clock is at its shortest reading here.
- **The Choosing** (B, 88-97%) — the grand gesture and the neutralization of the threat are the same act. One or both leads pay a real cost, and that payment is what defeats the antagonist. The confrontation happens on ground the antagonist chose, using something a lead established earlier.
- **After** (R, 97-100%) — HEA or HFN on the page, with both leads present, plus the ledger: what the danger took and did not give back, and what the barrier cost to cross.

### The collision rule

At 72-80% the two curves want the same page. Romancing the Beat wants the
break-up; the threat ladder wants All Is Lost. Writing them as two
adjacent events is the single most common structural failure in this
genre, because it lets a reader feel the seam. They must be one event with
two readings. Three shapes are legal:

  1. **Break, then strike.** The leads separate, and the separation is the
     vulnerability the antagonist has been waiting for. The break must be
     caused by the barrier, not by the danger — the danger only cashes it.
  2. **Strike, then break.** The antagonist's worst move forces one lead
     into a choice that betrays the other: a bargain, a handover, a lie
     told to keep them alive. Survival costs the relationship.
  3. **One event, two readings.** A single revelation both peaks the
     danger and detonates the barrier — a lead's prior connection to the
     antagonist, the thing one of them concealed precisely in order to
     protect the other.

Illegal: a black moment caused by a third party's manufactured
interference while the threat merely continues alongside it; a break-up
and a peak more than three chapters apart; a peak that costs the couple
nothing they had earned.

CONSTRAINTS:
- Chapters alternate leads by default and end on a turn — new information,
  a reversal, an arrival, a decision made or foreclosed. Target roughly
  2,500 words — shorter than a romance chapter, longer than a thriller's,
  because each one has to turn twice. A chapter running well past that is
  usually two.
- Antagonist POV chapters are optional and bounded: no more than one in
  six, short, and always producing dramatic irony — the reader must come
  out of one knowing something the couple does not. An antagonist chapter
  that only stages menace is cut. If the book's design depends on the
  antagonist's identity being concealed, do not use antagonist POV at all;
  a coy POV that withholds a name the viewpoint character obviously knows
  is a cheat the reader will charge to the book.
- Every chapter moves at least one strand, and no more than three
  consecutive chapters move only one.
- The clock is visible at least once per act in a form the reader can
  count, and it expires inside the final act, not after it.
- The antagonist has on-page presence — action, not rumour — before the
  midpoint.
- The leads may be wrong; they may not be stupid. Every choice that leads
  them deeper must be the best available choice given what they know,
  which means the plan must state what they know and what they have
  already tried.

## World Sections

This world is two pressure systems clamped together: what the antagonist
can reach, and what the leads' ordinary lives will not let them do about
it or about each other. Every section below must close off a possibility
or force a choice somewhere in the outline. A detail that constrains
nothing is decoration and counts against the score.

- The Threat
- The Antagonist's Machinery
- The Clock
- Adhesion: Why They Cannot Separate
- The Barrier's Machinery
- Authority: Who Could Help, and Why They Won't
- Geography, Escape & Private Space
- The Leads' Resources
- Internal Consistency Rules

### The Threat
What is actually going to happen if nobody stops it, stated plainly and in
full for the author's eyes: who is harmed, how, when, and why. The
antagonist's plan as they understand it, including the parts the leads
will never learn. Write the version of this book in which neither lead
does anything, and say how it ends. Then write the version in which the
two never meet, and say how that one ends — if the two versions are
identical, the couple is not load-bearing and the book has a problem
`romance_raises_stakes` will find.

### The Antagonist's Machinery
Capability as an inventory: money, people, access, authority, technical
skill, information sources, and how they learn what they learn. What each
move costs them in exposure, because an antagonist who spends nothing
cannot be pressured. At least two hard limits, meant. And separately, the
**leverage ledger**: every move available to the antagonist that exists
only because these two leads matter to each other, when the antagonist
learns the relationship exists, and how. That ledger is the spine of this
genre's suspense.

### The Clock
The deadline in concrete form — a hearing, a flight, a transfer, a
shipment, a release date, a body that will be found on Monday. Who set it,
whether it can be moved, what specifically happens when it expires, and
the intermediate markers by which the reader can tell how much is left. If
the book carries a second, personal clock — a posting, a custody date, a
transfer that ends the adhesion — state how the two interact, because in
this genre the personal clock is usually the barrier's enforcement
mechanism.

### Adhesion: Why They Cannot Separate
The mechanism keeping these two in each other's path, stated as machinery
rather than as a trope name. Name the thing that would have to break for
them to lose contact, name what maintaining that contact costs each of
them, and name the penalty for walking away. "She's in protective custody"
is not enough; state what happens if she leaves the house, who notices,
and how long she lasts. An adhesion with no penalty for exit generates no
tension, and it is the failure `threat_forces_intimacy` is written to
catch.

### The Barrier's Machinery
The most important section for this book's afterlife. State what keeps
these two apart for reasons the case's resolution does not touch: a rule,
a posting, a testimony, a family, a professional consequence with a named
enforcer. Then write the conversation that would dissolve it, and state
plainly why neither lead can have that conversation without ceasing to be
who they are. Finally, write the paragraph in which the antagonist is
convicted and the couple still has a problem. If you cannot write that
paragraph, the barrier is a schedule and the romance has no third act.

### Authority: Who Could Help, and Why They Won't
Enumerate every body an ordinary person would turn to — police, employer,
family, press, lawyer, doctor, union, embassy — and for each state
precisely what happens if a lead goes to them. "They wouldn't believe her"
is not an answer; state why, and what specifically she lacks. At least one
must have been tried already, on the page, with a consequence. Where one
of the leads IS the authority — a detective, an agent, a prosecutor —
this section is harder and more necessary: state exactly what their badge
cannot do here, who outranks them, and what going through channels would
cost the other lead.

### Geography, Escape & Private Space
The map as constraint: distances, travel times, coverage, cameras,
checkpoints, the one road, the ferry. Then, in the same document, the
places these two can be unobserved and what it costs to get there —
romantic suspense runs on the overlap between concealment from the
antagonist and privacy from the world, and the best scenes in the genre
sit exactly where the two coincide. Sensory signatures for the two or
three locations the book returns to, specific enough that a scene set in
one could not be relocated by changing proper nouns.

### The Leads' Resources
What each lead actually has: skill, training, money, allies, access,
information, physical condition. Stated as an inventory so the book can
spend it. One of the two carries a demonstrated competence the antagonist
will eventually turn against them; the other carries an exposure the
antagonist can reach. Name which is which, and note that the genre is
better when they are not the same person's strengths twice over. Then the
ledger of what each loses and when.

### Internal Consistency Rules
Hard constraints a writer must not violate: travel times, phone coverage,
who holds which key, how long a wound takes, what a record can show, who
works which shift, who would notice an absence and when. This genre has no
magic, which means what breaks it is coincidence, sudden money, a phone
that dies exactly when isolation is needed, a skill a lead turns out to
have had all along, and a witness who arrives on cue. Write down the ones
this book must not use.

## Cast Requirements

1. **Lead A** — derived from the seed.
   - Full wound/want/need/lie chain
   - Three sliders with justification
   - Arc type (positive/negative/flat)
   - Detailed speech pattern (8 dimensions, with example lines)
   - Physical habits and tells tied to their work, class, and wound
   - At least 2 secrets, at least one of which the antagonist can use
   - A goal that exists independently of the other lead
   - Their **competence**, stated as one specific thing they are good at,
     with the chapter in the first quarter where it is demonstrated on a
     problem they solve and the later chapter where it fails or is turned
     against them

2. **Lead B** — the same depth, with no shortcuts. This genre's most
   common casting failure is a fully realized investigator opposite a
   love interest who is a set of attractive attributes plus a target on
   their back. Lead B needs their own wound/want/need/lie chain, their own
   independent goal, their own competence, and their own arc that closes.
   Name their **exposure** — what the antagonist can reach through them —
   and make sure it is not simply "being loved by Lead A."

3. **The antagonist** — full wound/want/need/lie chain, plus a written
   method: capability, resources, access, information sources, cost per
   move, and at least two hard limits. Their goal must be legible and
   pursued for reasons that make sense from inside their life, and the
   plan must state when and how they learn the two leads matter to each
   other, because that moment is when the leverage ledger opens.

4. **The person or body that benefits from the leads staying apart** —
   not a villain, and specifically not the antagonist. Someone whose
   legitimate interests are served by the barrier holding: a commanding
   officer, a prosecutor protecting a case, a parent, an ex with a claim,
   an institution with a policy. Full chain. If this role and the
   antagonist are the same person, the barrier dies with the threat and
   `barrier_beyond_the_threat` will say so.

5. **One confidant per lead** — the person each talks to, who is allowed
   to say the thing the lead cannot say to themselves. These two must not
   be interchangeable, and they should want different things for their
   respective leads.

6. **The ally who becomes a cost** — someone who helps and is harmed for
   it, or who has to be spent. Full chain. Their loss is the most reliable
   rung on the threat ladder and it only works if they were a person
   first.

7. **The authority who is procedurally correct and useless** — the
   detective, commander, lawyer, or official who follows the rules exactly
   and cannot help. Competent and sympathetic; a stupid institution is a
   cheat, a constrained one is a plot.

## Canon Categories

### Geography & Access
- The lake house is forty minutes from town on one road. (world.md)
- There is no cell coverage past the county line. (world.md)
- The clinic's rear door does not lock from outside. (ch_09)

### Timeline & The Clock
- The grand jury convenes on the 22nd. (world.md)
- Ch 1-8 span five days. (outline.md)
- Sofia's federal transfer date is six weeks out from ch_01. (world.md)

### Relationship Beats
- They first touch deliberately in ch_07, in the car. (outline.md)
- Marcus tells Sofia about the 2019 shooting in ch_15. It cannot be untold.
- The break happens in ch_28, over her testimony, not over the case. (outline.md)

### The Antagonist's Capabilities
- Delaney can pull any plate through a contact at the DMV. (world.md)
- Delaney cannot enter the courthouse; his name is flagged. (world.md, HARD LIMIT)
- Delaney learned Marcus and Sofia were together from the motel clerk in ch_19. (ch_19)

### Leverage & Exposure
- Sofia's sister is the only person Delaney can reach without exposure. (world.md)
- Marcus's badge is suspended from ch_21; he has no lawful authority after that. (ch_21)
- Delaney knows, from ch_19, that Marcus will break protocol for Sofia. (ch_19)

### Character Facts
- Marcus was a paramedic before he was a deputy. He can read an injury. (characters.md)
- Sofia has not spoken to her father since 2017. (characters.md)
- Marcus cannot swim. (characters.md)

### Procedural & Institutional
- A protective detail ends the day the indictment is sealed. (world.md)
- Sofia's testimony is void if she is shown to have a relationship with a member of the detail. (world.md)
- The sheriff's office must log every vehicle checkout. (world.md)

### Established In-Story (things that happened in chapters)
- The safe house was burned in ch_24. It is not available again.
- Sofia signed the statement in ch_26. She cannot unsign it.
- Marcus turned in his weapon in ch_21. He does not get it back.

## Artifacts

### braid_map.md

The one document that makes the genre's defining failure visible. It is a
single markdown table, one row per chapter, and it is what
`braided_escalation` is scored against; `threat_forces_intimacy` and
`romance_raises_stakes` are checked against its two causation columns.

Columns:

| Ch | POV | Braid beat | Relationship state change | Threat state change | Causation | Cost paid |

- **Braid beat** — the `braided-beat` name from `## Plot Architecture`, or
  blank for a chapter between beats.
- **Relationship state change** — what is now known, risked, or foreclosed
  between the leads that was not before. `none` is a legal entry and an
  honest one.
- **Threat state change** — what the antagonist gained, took, or revealed;
  what the leads lost. `none` is legal.
- **Causation** — one of `threat→romance`, `romance→threat`, `both`, or
  `none`, naming which strand caused the other's movement in this chapter.
  A run of `none` is the separation failure showing itself.
- **Cost paid** — what this chapter removed from the leads that they had at
  the start of it. Blank is legal and, repeated, is a flat ladder.

Lifecycle:

- **seed** creates the file with the header row and a note that `none` is
  a legal entry, because a braid map padded with invented movement is
  worse than an honest one.
- **foundation** fills one row per outlined chapter and re-fills whenever
  the outline changes. A judge checks: are there four or more consecutive
  rows with `none` in Causation? Do the beat names appear at the marks
  `## Plot Architecture` states? Is the Collision a single row rather than
  two?
- **draft** updates each row as its chapter is written, replacing planned
  entries with what the prose actually delivered — this is where a
  relationship change that was outlined and then not written on the page
  gets caught.
- **revise/review** re-reads the finished table for flat runs, for a Cost
  column that empties out in Act II, and for any later turn costing less
  than an earlier one.

## Drafting Rules

25. Every chapter moves at least one strand and says which. If a chapter changes neither what the leads know about each other nor what the threat can do, it is a chapter to fold into its neighbour.
26. Intimacy is paid for by danger, and danger is sharpened by intimacy. Before writing a scene in which the leads get closer, name the fact of the situation that made it possible; before writing an antagonist move, ask whether the couple's existence made a better move available.
27. Attraction is shown through specific noticing, never asserted — and under threat, what each lead notices is diagnostic: who checks exits, who checks the other person, who lies well. What does this character see that no one else in the room would see, and what does it cost them to have noticed it?
28. Threat is delivered through capability and consequence, never through atmosphere. Do not tell the reader to be afraid with weather, silence, or an ominous narrator; show what the antagonist can reach, then let them reach it.
29. Interiority carries both plots at once. In every scene the reader must know what the POV lead believes about where they stand with the other AND what they believe the danger can currently do. The gap between those beliefs and the truth is where this genre's tension lives.
30. The leads may be wrong; they may not be stupid. Before writing a choice that leads them deeper, state on the page what they know and what they have already tried — then make the bad choice the best available one. A lead who does something reckless "because she loved him" needs the reader to see why it was also the least bad option.
31. Banned phrases, on top of the base list: "she'd never felt this way before", "electricity/sparks between them", "a heat pooled low in her belly", "her breath hitched", "safe for the first time in her life", "little did she know", "her blood ran cold", "he was a trained killer", "she never saw it coming", "the man in the shadows smiled", "he would burn the world down for her", "she was in danger, and worse, she was falling for him", "I can't protect you if you won't let me". The last three are this genre's specific slop: they announce the braid instead of building it.

## Seed Prompt

Persona (adopt while generating):

You are a romantic suspense novelist who has written across the
genre's range — small-town, procedural, protective-detail, domestic,
cartel, cold-case, corporate. You build the antagonist's plan and the
couple's barrier as a single object, because you know the genre's one
real failure is two competent plots that never touch. You generate
novel concepts that are SPECIFIC, SURPRISING, and STRUCTURALLY SOUND.
For every concept you can say what the danger forces these two to
admit, and what move the antagonist gains the moment he learns they
matter to each other. You never propose a love story the threat could
be deleted from, or a threat the love story could be deleted from.

Required concept fields (these romantic suspense fields and phrasings
replace the neutral scaffold's versions of the same fields):

WORLD: The pressure system this happens inside — the job, the town,
  the institution, the case, the season, the money. Make it SENSORY
  and make it constraining: distances, coverage, who would notice,
  where a person can be unobserved.
THE BRAID: The two-way lock, in two sentences. First: the specific
  fact of the danger that forces these two into contact and makes
  them tell each other something they would have kept. Second: the
  specific move the antagonist gains because they matter to each
  other — the leverage. If either sentence would survive deleting the
  other plot, the concept is not ready.
COUPLE/BARRIER: Who the two leads are, what specifically draws each to
  the other (something no third party in the book would notice), and
  the STRUCTURAL barrier between them — one that is still standing on
  the day the antagonist is convicted. Not "we can't while this is
  going on." A rule, a posting, a testimony, a family, a cost one of
  them genuinely cannot pay.
THREAT/CLOCK: Who or what is coming, stated as capability rather than
  reputation — what they can do, what resource lets them do it, how
  they find people, and at least one hard thing they CANNOT do. Then
  the clock: the concrete deadline, what happens when it expires, and
  who set it.
WHY NOT THE POLICE: The specific reason the ordinary remedies are
  closed — already tried, actively dangerous, or foreclosed by one of
  the leads' own histories. If one of the leads IS the police, say
  what their authority cannot do here and who outranks them.
ARCS: For EACH lead, the belief they hold at the start that they
  cannot hold at the end, and how the other person AND the danger
  together make it untenable. Two arcs, both closing. Neither lead may
  arrive already finished, and neither may spend the third act as
  cargo.
TENSION: What's the central conflict? It must be both PERSONAL (what
  each lead stands to lose in themselves, and in the other) and LARGER
  (an institution, a community, a case, a system). These two must be
  in tension — protecting the person must sometimes be the wrong
  thing to do.
THEME: What question does this story explore? Not a message — a
  genuine question with no easy answer.
WHY IT'S NOT GENERIC: One sentence on what makes this different from
  the standard romantic suspense premise.

Aim for DIVERSITY across the ten concepts:
  - Span the subgenres: small-town, procedural, protective detail,
    domestic, legal, medical, corporate, cold case, wilderness
  - Vary who holds the authority — at least one where neither lead has
    a badge, at least one where both do, at least one where the
    endangered lead outranks the protector
  - Vary the adhesion: custody of a witness, a shared target, a
    contract neither can break, a small town, a job that cannot be
    quit mid-case
  - Vary the antagonist: a person, an institution, a market, someone
    inside the leads' own circle
  - Span heat registers — at least one that clearly wants to be
    closed-door and at least one that clearly wants to be explicit;
    this pack constrains neither
  - Span the violence register from bloodless to brutal; this pack
    constrains neither
  - At least one queer pairing and at least one where neither lead is
    white or Anglo-American
  - Span life stages — at least one couple over fifty, at least one
    with children already in the danger's reach
  - At least one where a lead is guilty of something real
  - Mix of tones: cold, propulsive, tender, grim, wry

DO NOT generate:
  - The parallel-track premise — any concept where the case would
    resolve identically if the couple never met, or the couple would
    resolve identically with the case removed
  - Forced proximity with an unlocked door: a safe house either lead
    could leave, a bodyguard contract either could end, a stakeout
    with no penalty for walking away
  - The love interest kidnapped in act three as the entire leverage,
    with no earlier sign the antagonist noticed the relationship
  - The idiot plot — any premise whose danger evaporates the moment
    someone calls the police, tells a spouse, or leaves town
  - The invincible antagonist with no stated method, whose reach is
    whatever the scene requires
  - The serial killer taunting the profiler he is also seducing
  - The witness protection romance where the marshal's only trait is
    protectiveness
  - Amnesia concealing an elite operative, and the spouse who is
    secretly an assassin
  - Revenge for a murdered first wife who had no life of her own on
    the page
  - Enemies-to-lovers where the enmity is bickering rather than
    genuinely opposed interests, and rivals-in-the-same-agency where
    the rivalry costs nobody anything
  - A third-act breakup manufactured by a jealous ex while the
    threat continues in parallel
  - Coercion written as protectiveness, or a lead's professional
    authority used to override the other's refusal
