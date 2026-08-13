---
{
  "name": "dark-romance",
  "label": "Dark Romance",
  "role": ["primary"],
  "pillar_label": "Power & Redemption Architecture",
  "weights": {"pillar": 40, "character": 30, "structure": 20, "craft": 10},
  "beat_system": "romancing-the-beat",
  "content_register": {},
  "conflicts_with": ["romance", "ya", "cozy"],
  "shape": {
    "chapters": [34, 40],
    "words": [75000, 88000],
    "chapter_words": 2200,
    "pov_default": "dual first person present, alternating between the two leads"
  },
  "artifacts": ["power_ledger.md"]
}
---

This pack **replaces** `romance`; it does not extend it. That is what
`conflicts_with: ["romance"]` is for, and it is the load-bearing decision
here.

Every loaded pack's `## Genre Contract` is checked against the same book, so
loading both packs would check two contradictory promises at once. Romance
promises that "neither lead's consent is treated as an obstacle to be
overcome" and that "coercion, deception into intimacy, and persistence past
refusal are not courtship in this genre." That is the correct default for
romance and it is exactly what this genre is built out of. A dark romance
composed with `romance` loaded therefore breaches on page one and stays
capped at an `overall_score` of 6 forever, however well it is written — the
book is not failing, the wrong contract is being applied to it.

So the promises below are a replacement set, not a subtraction. Dark romance
is not romance with a rule removed; in the places that matter it is stricter.
The genre puts more explicit, on-page verbal consent into its negotiated
scenes than mainstream contemporary romance does, because it knows precisely
what it is depicting and cannot afford to be vague about it. It still owes
the reader a happily-ever-after. What it may not do is buy that ending with
the less-powerful lead's surrender.

## Framing

- genre_noun — "dark romance novel"
- pillar_noun — "power relationship"
- comps — Penelope Douglas, C.J. Roberts, Pepper Winters, Rina Kent, Katee Robert, Ana Huang
- seed_persona — a dark romance novelist who has written across the subgenre's range — captivity, mafia, revenge, dark academia, stalker — who knows the difference between a hero whose cruelty holds the plot up and a hero with a scowl and a car, and who never proposes a premise where the darkness could be deleted without the book noticing
- reader_persona — a dark romance reader who buys forty of these a year, who is here for the fantasy and refuses to be apologized to for it, and who closes a book the moment the resolution turns out to be that the heroine simply stopped minding
- writer_persona — an editor of the subgenre who reads for whether the power imbalance is dramatized or merely announced, for whether the darker lead pays anything the reader can name before the ending, and for whether the book knows what it is putting on the page

## Pillar Dimensions

In this genre the power relationship is the plot. Not a flavour applied to a
romance — the spine. Everything below is scored on the assumption that if
you removed the imbalance and the harm that maintains it, there would be no
book left, and that whatever external plot exists — the syndicate, the debt,
the inheritance, the school — is there to make the imbalance real rather
than the other way round.

Three distinctions decide most of the scoring, because most of this genre's
failures are one of them collapsing.

**Dark is not the same as mean.** A darker lead who is rude, withholding,
arrogant, or unavailable is a romance hero. A darker lead in this genre does
something to the other lead that the other lead did not agree to and cannot
undo, and the plot is built on top of that act. If the cruelty can be lifted
out and the chapters still connect, the book is a romance wearing a coat.

**A power imbalance is a mechanism, not an adjective.** "He owns her" is a
claim about the world that has to cash out in specifics: who can end this,
by what means, at what cost to whom, and who else would have to be dealt
with. An imbalance stated once in Act I and never re-examined is set
dressing, and the reader cannot feel a shift in a thing that was never
measured.

**Redemption is paid, not felt.** The darker lead wanting her more is not
change; it is the same appetite at higher volume. Change in this genre is
visible as subtraction — power given up, an alliance broken, standing lost,
a thing he built handed to someone else — and the reader has to watch it go.

Read `power_ledger.md` (this pack's artifact — see `## Artifacts`) alongside
the outline. It is the primary evidence for `power_shift_tracking`,
`captive_agency`, `redemption_cost`, and `aftermath_consequence`, all four of
which are claims about the relationship *between* scenes and none of which
can be checked by reading any single scene. A missing or unfilled ledger is a
real gap in the plan, not a missing formality.

A note on terms. This section says "the darker lead" for the one who holds
the power and does the harm, and "the constrained lead" for the one it is
done to. Neither is tied to a gender, and a book may swap which lead is which
partway through — that swap, where it happens, is the strongest possible
entry in the ledger.

### Romancing the Beat, in the dark register

`beat_system` is `romancing-the-beat`, not Save the Cat, and because this
pack conflicts with `romance` the beats are stated here in full rather than
inherited. The four phases and their approximate percentage marks are the
structure the outline is judged against; the annotations are what this genre
does differently inside them.

  1. **Setup** (0-10%) — Introduce both leads in their separate lives, each
     with a goal that is not the other person. Then the No Way / Adhesion.
     In this register the adhesion is not coincidence or a shared lease: one
     lead imposes it, and the other cannot leave. Establish in this phase
     what specifically prevents leaving — the door, the debt, the
     jurisdiction, the hostage, the name on the paperwork — because the rest
     of the book is a negotiation with that fact.
  2. **Falling in Love** (10-50%) — Inkling of Desire, Deepening Desire,
     Maybe This Could Work, and the Midpoint of Love. The dark variant runs
     these against resistance rather than against shyness: what deepens is
     not only wanting but the constrained lead's understanding of the
     machinery, and the first real move of the balance should land inside
     this phase. The Midpoint is the point at which each of them has
     something to lose that is not the other's compliance.
  3. **Retreating from Love** (50-75%) — Inkling of Doubt, Deepening Doubt,
     Retreating, Shields Up. The doubt here is usually correct. The
     constrained lead is right to distrust, and the retreat must be caused by
     the darker lead doing the thing he has always done rather than by a
     misunderstanding about whether he did it.
  4. **Fighting for Love** (75-100%) — the Break Up / Black Moment, the Dark
     Night of the Soul, the Grand Gesture, and the resolution: HEA or HFN.
     The Grand Gesture in this genre is a relinquishment. He gives up the
     hold, and the constrained lead is then free to leave and chooses
     otherwise — the choice is only worth anything if leaving was genuinely
     available first.

An outline in which the hold is broken by a third party, or in which the
constrained lead is never actually free to go before she stays, has not
written this phase. An outline whose black moment is the discovery of a fact
the reader already had has written a delay.

### Scored dimensions

- darkness_load_bearing — The darker lead's cruelty must hold the plot up, not decorate it. Excellent looks like a book in which a specific act of his — the taking, the debt called in, the threat made good on, the thing done to a third party — is the hinge that several later chapters swing on, and in which the constrained lead's every option is shaped by it. A gap looks like darkness as aesthetic: tattoos, a reputation, a scowl, a warning delivered by a third party, violence done only to people who deserved it and never in the direction of the other lead. Test: rewrite him as merely rude — same money, same job, same history, but nothing he does to her is coercive or cruel — and walk the outline. If fewer than four chapters need rewriting, or if the black moment survives intact, score 6 max. Second test: name the single act of his the plot could not proceed without, and name the chapter. If that act is a mood, a rumour, or something he did before the book began, score 6 max.
- power_shift_tracking — The imbalance must be specific, material, and in motion. Excellent looks like a plan where at any point the reader can say who could end this, by what means, and at what cost to whom, and where that answer changes at least three times across the book with every change caused by an act on the page. A gap looks like an imbalance asserted in Act I and never re-measured, or a single reversal in the last chapter with nothing between. Test: read the ledger's "Which way the balance moves" column top to bottom. If it moves fewer than three times, or if any three consecutive rows leave it unmoved, score 6 max. Second test: at the 50% mark, state exactly what the constrained lead could do about her position and what it would cost her. If the documents cannot answer without inventing, the imbalance has not been written; score 6 max.
- captive_agency — The constrained lead acts, and her actions change outcomes. Excellent looks like at least three decisions of hers that alter the plot's direction — a refusal that is not overridden, a bargain she names the terms of, a deception, an escape that half works, information or a capability the darker lead does not know she has — and at least one that costs her something she wanted. A gap looks like a lead whose entire repertoire is enduring, and whose one escape attempt exists in order to be foiled. Test: list every plot event she causes. If there are fewer than three, or if every one is reversed by the darker lead inside the same act, score 6 max. Second test: if the only thing she chooses in the whole book is to stay, score 6 max. Note that adaptation is not agency — becoming comfortable in the constraint is a change of state, not an action, and does not count toward the three.
- redemption_cost — The darker lead pays, on the page, before the ending, in the world's own currency. Excellent looks like a subtraction the reader watches happen and can name afterwards: power surrendered, an alliance broken, standing lost, protection withdrawn from himself, the thing he spent the book building handed to someone else — irreversible, and not repaid by the plot in the following chapter. A gap looks like a cost announced in dialogue, paid off-page, or refunded immediately; or a redemption that consists of wanting her more than before. Test: name the cost, name the chapter, and name what he no longer has at the end that he had at the start. If any of the three cannot be answered from the outline, score 6 max. Second test: check the mark — if the cost lands after the 90% mark, the book has bought its ending on credit; score 6 max. Third test: if the largest thing he gives up is an apology or a confession, score 6 max. Fourth test, and the one a plausible book is most likely to walk through: total the ledger in BOTH directions. The first test asks what he lost, and a book can answer it truthfully while still handing him more than it took. So list what he holds in the final chapter — power, standing, money, protection, alliances, position — against what he held in the first, and subtract. A book may retire one arrangement at 86% and then, in the chapters after, deliver immunity, a replacement contract, and a promotion, so that the reader who asks what he actually paid finds the answer is nothing. If his net position at the end is equal to or better than at the start, the cost was refunded however vividly it was paid; score 6 max regardless of the first three tests passing. Watch particularly for a windfall the plot delivers on someone else's timetable, and for a surrendered role that is in substance a promotion.
- aftermath_consequence — What happens to these people lands on them, and does not reset between chapters. Excellent looks like named, persisting change: what she cannot do now that she could in chapter 1, what he flinches at, what the body remembers, what the relationship can no longer contain, who else was altered — plus at least one chapter whose whole business is aftermath rather than escalation. A gap looks like a book that reboots between scenes, where a coercive or violent chapter is followed by one in which neither party's behaviour reflects it. Test: take the three most severe events in the outline and, for each, name one behaviour in a later chapter that makes sense only because that event happened. If any of the three has no answer, score 6 max. Second test: count the chapters given to aftermath rather than to escalation. If there are none, score 6 max.
- narrative_stance — The text knows what it is depicting. This genre is allowed to make the darkness pleasurable; it is not allowed to be ignorant of it. Excellent looks like harm that registers somewhere in the text every time it occurs — in the interiority of the person it happens to, in a consequence a later chapter pays, in another character who names it plainly, or in the darker lead's own awareness — while the book still lets the reader want what it is offering. A gap runs in two directions: the book that serves coercion as the erotic payoff with nothing anywhere registering it as harm, and the book that apologizes in the narration every few pages, which is disclaiming rather than stance. Test: for the three most coercive scenes in the outline, name where the harm registers — the line of interiority, the later consequence, the character who says it. If any of the three has no answer, score 6 max. Second test: if the book's awareness arrives only as narration instructing the reader how to feel, rather than as an interior line or a consequence, score 6 max. Note that a complete absence of any such awareness across the whole book is a Genre Contract breach, which the rubric handles separately; do not double-count it here.

## Genre Contract

These bind the central relationship and the book built around it. They
replace `romance`'s contract rather than supplementing it, which is why the
two packs conflict.

- The central relationship resolves HEA (happily ever after) or HFN (happy for now): both leads alive, together, and choosing each other on the page at the end, with both present for the resolution rather than reconciled off-page or in summary. Dark romance delivers this ending; a book that wants separation, death, or ambiguity is a dark love story and should not use this pack.
- What earns that ending is the darker lead's own change, demonstrated by a cost he pays on the page before the resolution and does not get back. A book whose resolution is that the constrained lead stops objecting — that she adapts to the constraint rather than the constraint being dismantled — has breached this, however tender its final chapter.
- The hold between them is ended by a decision one or both leads make, not by an external event that removes it for them. The rival is not what frees her; the arrest, the inheritance, and the death of the man who set the terms are not resolutions.
- The darkness is depicted as darkness. The narrative may let the reader enjoy the fantasy; it may not be ignorant of what it is showing. Coercion presented as the erotic payoff with nothing anywhere in the text registering it as harm — no cost, no fear, no consequence, no interiority from the person it happens to, no character who names it — is a breach. This is the line between provocative and predatory, and it is a promise about the book's awareness, not a requirement that the book condemn itself.
- Where an encounter is a negotiated fantasy — consensual non-consent, primal play, captivity kink between people who have agreed to it — the negotiation is legible in the text. Before, during, or after, but on the page: terms set, a limit named, a word or signal that ends it, or an afterward in which both parties confirm what was agreed. A book that depends on the reader assuming a negotiation happened off the page has breached this.
- Neither lead is a minor, and each is established as an adult on the page before the first intimate or violent scene between them. This is not satisfied by the absence of a stated age.

## World Sections

The world of a dark romance is a control system. Every section below must
produce something that CONSTRAINS a choice somewhere in the outline — a door
that locks from one side, a person whose safety is the leverage, a
jurisdiction that will not help, a rule the darker lead is himself subject
to. A detail that constrains nothing is decoration and counts against the
score. Keep this document short and load-bearing; a long world bible here is
usually a sign the power relationship is underbuilt.

- The Power Structure
- Leverage & Exits
- Violence: Rules, Reach & Aftermath
- Private Space & Access
- Who Would Find Out, and What It Costs
- Internal Consistency Rules

### The Power Structure
Who holds power over whom, and what makes it real in this world rather than
asserted. Money, ownership, a debt, a name, a weapon, an institution, a
jurisdiction, a family that enforces, a document with a signature on it.
State the source of the darker lead's power and — this is the part packs
usually skip — state what he is himself subject to. A darker lead who
answers to nobody has no cost available to pay later, which is why the
redemption in those books always has to be an apology.

### Leverage & Exits
What is actually stopping the constrained lead from leaving, stated as a
mechanism and not a mood. Name every exit that exists — a road, a phone, a
sibling with a car, a lawyer, a passport, a police force — and for each one,
what specifically forecloses it and what it would cost to try. Then name the
leverage: the person, the money, the information, or the future that is held
against her. If she can leave at no cost and does not, the book has a
different problem than it thinks.

### Violence: Rules, Reach & Aftermath
What violence exists in this world, who is permitted to do it, to whom, and
what happens afterwards. Write the rules the darker lead operates under and
the ones he breaks. Then write what violence costs here in physical terms —
how long an injury takes, what a hospital would ask, who cleans up, what a
body's absence sets in motion. This section is what stops harm from being
weightless, and it is the evidence `aftermath_consequence` reads.

### Private Space & Access
Where these two can be unobserved, where they cannot, and who controls the
difference. This genre runs on access asymmetry: he has the keys, the
cameras, the schedule, the staff. Name the specific rooms this book happens
in with a sensory signature for each, name who else can enter and when, and
name the one place the constrained lead has that is hers — because the
existence or absence of that place is a fact about the book, and either
answer needs to be deliberate.

### Who Would Find Out, and What It Costs
Who has standing to notice, what they could do about it, and why they do not.
Family, employers, police, a rival organization, a school, a neighbour, a
group chat. Name at least two people whose knowledge carries a concrete
consequence rather than a bad feeling, and name why each is currently
neutralized — bought, afraid, complicit, deceived, or far away. A world in
which nobody would care is a world with no exposure stakes, and exposure is
half this genre's tension.

### Internal Consistency Rules
Hard constraints a writer must not violate: who is where and when, who has a
key, how far the darker lead's reach actually extends, how long an injury
takes to heal, how long a drive is, who would be missed and by whom, what
money can and cannot buy here. This genre has no magic; what breaks it is a
reach that expands whenever the plot needs it, a phone with no signal exactly
once, an organization that is omniscient in Act II and blind in Act III, and
a body that recovers between chapters. Write down the ones this book must not
use.

## Cast Requirements

1. **The darker lead** — full depth.
   - Full wound/want/need/lie chain
   - What the cruelty is FOR: the thing it gets him, protects him from, or
     proves. Cruelty without a function is a costume, and this is the
     evidence `darkness_load_bearing` reads.
   - What he is subject to — the person, body, or rule that can cost him
     something. Without this there is nothing available for
     `redemption_cost` to spend.
   - Three sliders with justification
   - Arc type (positive/negative/flat)
   - Detailed speech pattern (8 dimensions, with example lines), including
     how he speaks when he is not performing control
   - Physical habits and tells tied to his work, his history, and his wound
   - At least 2 secrets
   - A goal that exists independently of the other lead

2. **The constrained lead** — the same depth, with no shortcuts, and one
   thing more: a capability, a piece of knowledge, or a relationship the
   darker lead does not know about. The genre's signature structural failure
   is a fully realized captor opposite a captive who is a reaction. She needs
   her own wound/want/need/lie chain, her own goal from before the book, her
   own arc that closes, and a repertoire of actions — this is the registry
   evidence `captive_agency` is scored against.

3. **The person or body that makes the power real** — the family, the
   organization, the institution, the creditor, the school. Not a villain
   standing behind the hero: a structure with its own legitimate interests
   that would continue without him. Full wound/want/need/lie chain if it has
   a face.

4. **The leverage** — whoever or whatever is held against the constrained
   lead: a sibling, a child, a parent's care, a debt, a visa, a reputation.
   If this is a person, they need their own life and their own opinion about
   being used this way.

5. **One person who can name what is happening** — a friend, a doctor, a
   priest, a rival, someone inside the organization with a conscience. Not
   the book's moral spokesperson; someone whose plain description of the
   situation the leads have to react to. A book with nobody in this role
   makes `narrative_stance` much harder to satisfy.

6. **One confidant per lead**, not interchangeable, wanting different things
   for their respective leads.

## Canon Categories

### Geography & Access
- The house has one road in and the gate is coded. (world.md)
- Ilse's room is on the third floor; the third-floor windows do not open. (world.md)
- The clinic is forty minutes away, and someone would have to drive. (ch_09)

### Timeline
- Ilse is taken in ch_03, in the second week of November. (outline.md)
- Ch_01-16 span nine weeks. (outline.md)
- Andrei's brother died fourteen months before ch_01. (characters.md)

### Power & Leverage
- Andrei holds the note on Ilse's father's debt. (world.md)
- Ilse's sister's tuition is paid quarterly, by Andrei, since ch_05. (world.md)
- Andrei answers to Grigor, who can withdraw protection at any time. (world.md)

### Agreements & Limits
- In ch_11 they set terms; the word that ends it is "November". (ch_11)
- Ilse said she will not be locked in again, and has not been. (ch_14)
- Andrei promised not to touch her sister's file. He has read it. (ch_17)

### Harm & Aftermath
- Ilse's wrist was broken in ch_06 and set badly; it aches in cold. (ch_06)
- Andrei killed Petr in ch_12, in front of her. She cannot un-see it. (ch_12)
- Ilse has not slept a full night since ch_06. (ch_08)

### Character Facts
- Ilse is twenty-six and a veterinary nurse. (characters.md)
- Andrei is thirty-four and cannot read Cyrillic script. (characters.md)
- Ilse can drive a manual; nobody in the house knows this. (characters.md)

### Established In-Story (things that happened in chapters)
- Ilse got out as far as the gate in ch_10 and came back on her own. (ch_10)
- Andrei gave Grigor's ledger to the prosecutor in ch_31. That is irreversible.
- Ilse told him about her mother in ch_20. He now knows.

## Artifacts

### power_ledger.md

The power ledger is this genre's accounting for the claims that cannot be
checked by reading any single scene: that the imbalance is being dramatized
rather than asserted, that it moves, that the constrained lead acts, that the
darker lead pays, and that what happens sticks. Every one of those is a
statement about the sequence. A captivity scene can be excellent on its own
and the book can still be a static tableau with an apology at the end, and
nothing else in the project would catch it — `canon.md` records facts, the
foreshadowing ledger tracks plants and payoffs, and neither records which way
the balance moved.

**Format.** A single markdown table with these seven columns, one row per
chapter in which the power relationship is in play, in chapter order:

| # | Chapter | Who holds the power, and what makes it real | What the darker lead does with it | What the other lead does about it | Which way the balance moves | What cannot be taken back |
|---|---|---|---|---|---|---|
| 1 | ch_03 | Andrei — the debt, the gate code, the drive | takes her from the flat; states the terms | agrees, to keep her sister out of it | to him, hard | she is in the house; her father knows and did nothing |
| 2 | ch_06 | Andrei — physical, and the house staff | has her locked in after she reaches the kitchen door | fights, and her wrist breaks | to him, and it costs him the staff's silence | the injury; the staff saw |
| 3 | ch_10 | Andrei — but the gate was open | leaves the gate open to see what she does | walks out, gets as far as the road, returns on terms she names | to her, first real move | he now knows she chose it; he cannot use the gate as a threat again |
| 4 | ch_11 | contested | agrees to terms aloud for the first time | sets the word that ends it | level, briefly | there is an agreement, so there is something to breach |
| 5 | ch_17 | Andrei — information | reads her sister's file after promising not to | finds out; stops speaking to him | to him in fact, to her in standing | the promise is broken and cannot be un-broken |

Column by column:

- **#** — sequence number, so a reordering in revision is visible.
- **Chapter** — in the project's `ch_NN` form.
- **Who holds the power, and what makes it real** — not a name alone. The
  mechanism: the debt, the gate, the staff, the file, the strength, the
  jurisdiction. If this column ever reads as a bare assertion, that is the
  finding.
- **What the darker lead does with it** — the concrete act this chapter,
  not his mood. `Nothing` is a legitimate entry and a meaningful one when it
  follows a row where he would have acted.
- **What the other lead does about it** — the action, not the feeling.
  `Endures` is a valid entry and three of them in a row is a finding; this
  column is the evidence `captive_agency` reads.
- **Which way the balance moves** — to him, to her, level, or unmoved, plus
  the cause. This column is the evidence `power_shift_tracking` reads, and
  the direction must be caused by something in the two columns to its left.
- **What cannot be taken back** — what is permanently true afterwards:
  knowledge, injury, a broken promise, a witness, a foreclosed threat. This
  column is the evidence `aftermath_consequence` and `redemption_cost` read.

Below the table, add three lines: the chapter at which the balance first
moves toward the constrained lead, as a percentage of the book; the chapter
of the darker lead's largest cost, as a percentage; and whether any three
consecutive rows leave the balance unmoved. Stating those explicitly stops
each reader recomputing them differently.

**Which phase fills it.** `novel-seed` creates the file from this template
when it scaffolds the project. `novel-foundation` fills it against the
completed outline, after `characters.md` exists — the power column cannot be
written before the darker lead's sources of power and the constrained lead's
capabilities are on record — and re-checks it whenever the outline or either
lead's chain changes. `novel-draft` adds a row whenever a chapter moves the
balance in a way the ledger does not have, and corrects the last two columns
when a chapter lands differently from the plan. `novel-revise` and
`novel-review` re-verify the whole table against the manuscript, and are the
passes most likely to find that the balance stopped moving after the midpoint.

**What the rubric checks.** The judge reads this file alongside `outline.md`
and confirms:

  - The balance moves at least three times, and no three consecutive rows
    leave it unmoved.
  - The constrained lead's column contains at least three entries that are
    actions rather than endurance, and at least one of them changes what a
    later row can contain.
  - At least one row records a cost to the darker lead in the world's own
    currency, before the 90% mark.
  - Every row's `What cannot be taken back` is specific and non-empty, and
    at least three of them are referred back to in a later chapter.
  - The final row could not have been the first — something in it depends on
    an earlier row.
  - Everyone named in the table appears in `characters.md`.

An absent or unfilled ledger is scored as a gap in `power_shift_tracking`,
`captive_agency`, `redemption_cost`, and `aftermath_consequence` alike,
because those four have no other cross-scene evidence to read.

## Drafting Rules

25. Write the harm at its real weight. This genre's contract is that the darkness is depicted as darkness, and that is a drafting instruction before it is a promise: when something is done to a character, the prose registers what it costs — in her body, in her attention, in what she does in the next chapter. The reader may enjoy the scene. The book may not be unaware of it.
26. Never narrate the reader's verdict. Do not write "what he did was unforgivable" or "she should have hated him for it". Awareness belongs in an interior line, a consequence, or a character who says it out loud, never in narration telling the reader how to feel. A book that disclaims in the narration has replaced stance with anxiety.
27. Every chapter in which the two are together must move the balance, and you must be able to say which way before you draft it. Record it in `power_ledger.md` as you write. If the answer is "nowhere" for a third consecutive chapter, the book has stopped being about anything.
28. The constrained lead acts in every act of the book. Refusal, bargaining, deception, sabotage, escape, an alliance made behind his back, a term named and held to — something. Enduring is a state, not an action, and a chapter in which her only verb is enduring needs a second verb before it is finished.
29. Where a scene is a negotiated fantasy, put the negotiation on the page. Terms, a limit, a word that ends it, or an afterward in which both of them say what it was. This is the scene that makes every other scene in the book readable as desire rather than as damage, and it is not optional because it is unsexy — write it so that it is not.
30. Establish both leads as adults early, concretely, and once. An age, a profession, a lease, a divorce, a degree finished years ago. Do it in the first two chapters and do not do it again.
31. Interiority does not stop when the violence starts. The POV character keeps thinking, calculating, misreading, and wanting throughout — a scene where the interior line goes quiet and the choreography takes over is where this genre's prose most reliably goes dead, and it is also where the stance disappears.
32. Redemption is written as subtraction. When the darker lead changes, show the reader the thing leaving his hands. A speech about who he used to be is not a cost, and no amount of tenderness in the final act substitutes for one page of him losing something.

BANNED PHRASES:
he was a monster but he was her monster
the beast inside him
his inner demons
he was darkness and she was light
she was the light to his darkness
the darkness in him called to the darkness in her
she brought out the light in him
she was the only one who could save him
love him back to life
she tamed the monster
his beautiful obsession
she was his salvation
danger radiated off him
a predator's smile
his eyes went black
he was the devil in a suit
sinfully handsome
dark and dangerous
every instinct told her to run
she should have been afraid but she wasn't
she knew she should hate him
broken but not beaten
he growled possessively
you belong to me and only me
he'd never wanted anyone the way he wanted her
she was ruin and he was ruined
his to break

## Seed Prompt

Persona (adopt while generating):

You are a dark romance novelist who has written across the subgenre's
full range — captivity, mafia and organized crime, revenge, dark
academia, stalker, arranged marriage under duress — contemporary and
historical, queer and straight. You generate novel concepts that are
SPECIFIC, SURPRISING, and STRUCTURALLY SOUND. Every concept names a
power arrangement that is a mechanism rather than a mood, one concrete
thing the darker lead does that the plot could not proceed without, and
a price he pays before the ending that the reader watches leave his
hands. You never propose a hero whose darkness is a wardrobe, and you
never propose a book whose resolution is that she stopped minding.

Required concept fields (these dark romance fields and phrasings replace
the neutral scaffold's versions of the same fields):

WORLD: The control system this book runs on — the house, the
  organization, the debt, the institution, the jurisdiction, the
  season. Not a backdrop: the specific arrangement that makes leaving
  expensive and being found out worse. Make it SENSORY and make it
  material — who holds the key, who is paid by whom, how far the reach
  actually extends, and where it stops.
POWER/LEVERAGE: Who holds what over whom, and what makes it real in
  this world. Name the ONE concrete act the darker lead performs with
  it — not a reputation, not a threat delivered by a third party, an
  act on the page — and say which later chapters depend on it. Name
  what is held against the other lead. Name what the darker lead is
  himself subject to, and name the moment the balance first moves the
  other way.
AGENCY: What the constrained lead actually DOES — three specific
  actions that change the plot's direction: a refusal that stands, a
  bargain whose terms she sets, a deception, an escape that half
  works, a capability he does not know she has. Say what each costs
  her. Adapting to the constraint does not count.
COST & AFTERMATH: What the darker lead loses on the page before the
  ending — power, an alliance, standing, protection, the thing he
  built — who watches it go, and why it cannot be recovered. Then name
  one thing that is permanently different in each of them afterwards,
  and one moment where the book registers the harm as harm without
  stopping to lecture.
TENSION: What's the central conflict? It must be both PERSONAL (what
  each lead stands to lose in themselves) and LARGER (it implicates a
  family, an organization, a community, someone dependent on them).
  These two must be in tension with each other.
THEME: What question does this story explore? Not a message — a
  genuine question with no easy answer.
WHY IT'S NOT GENERIC: One sentence on what makes this different from
  the standard dark romance premise.

Aim for DIVERSITY across the ten concepts:
  - Span the subgenres: captivity, organized crime, revenge, dark
    academia, arranged marriage, stalker, historical
  - Vary WHICH lead holds the power, and include at least one where it
    genuinely changes hands partway through
  - At least one queer pairing and at least one where neither lead is
    white or Anglo-American
  - Span life stages — not ten twenty-somethings; at least one pairing
    over forty, at least one where a child or a dependent is in the
    house
  - Vary the register of the darkness: physical, financial,
    institutional, informational, social. At least one where no one is
    ever hit
  - Vary the currency of the cost he pays — money, standing, an
    alliance, a body, a name, a person he was loyal to
  - At least one where the negotiated fantasy is explicit on the page
    and central, and at least one where the darkness is entirely
    non-negotiated and the book knows it
  - Span heat registers; this pack constrains none of them
  - Mix of tones: brutal, cold, feverish, tender-in-the-wrong-places,
    darkly funny

DO NOT generate:
  - Darkness as wardrobe — the tattooed billionaire, the scowl, the
    car, a hero who is dangerous to everyone except her
  - Any premise where deleting the cruelty leaves the plot standing
  - Redemption by love alone — a hero who changes because he wants her
    more, and pays nothing anyone can name
  - A resolution in which the constrained lead simply stops objecting,
    adapts, or is revealed to have wanted it all along
  - The third-act retcon: he was secretly protecting her the whole
    time and none of it was real
  - Captivity that is comfortable and costs nothing — the gilded suite,
    the wardrobe, the chef, an unlocked door nobody walks through
  - A lead whose only verb is enduring, and whose one escape attempt
    exists to be foiled
  - Sexual violence as backstory decoration — an assault in a
    character's past that motivates a plot and never touches how she
    behaves
  - Any premise requiring a participant who is not an adult, or whose
    age the concept leaves unstated
  - The mafia whose money and violence dissolve every obstacle, and the
    organization that is omniscient when convenient
  - A dead or dying love interest, an ambiguous ending, or a separation
    played as maturity; this pack promises HEA or HFN
