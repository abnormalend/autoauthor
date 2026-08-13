---
{
  "name": "romantasy",
  "label": "Romantasy",
  "role": ["primary"],
  "pillar_label": "Magic & Relationship Architecture",
  "weights": {"pillar": 35, "character": 30, "structure": 25, "craft": 10},
  "beat_system": "save-the-cat-with-romancing-the-beat",
  "content_register": {},
  "conflicts_with": ["fantasy", "romance"],
  "shape": {
    "words": {"extended": [110000, 140000]},
    "chapter_words": 2600,
    "pov_default": "dual third limited past, alternating between the two leads"
  },
  "artifacts": ["braid.md"]
}
---

## Framing

- genre_noun — "romantasy novel"
- pillar_noun — "magic system and central relationship"
- comps — Sarah J. Maas, Rebecca Yarros, Naomi Novik, Holly Black, Carissa Broadbent, Juliet Marillier
- seed_persona — a romantasy novelist who has written both halves seriously — a magic system with rules a reader can hold in their head, and two people whose wanting each other is the most expensive thing in the book — and who never proposes a love story with a map behind it
- reader_persona — a romantasy reader who finishes 60+ books a year, has read every mate-bond and every trial-by-dragon, wants to be undone by the couple AND to be able to explain the magic to a friend afterwards, and stops trusting a book the moment the world's rules bend to let the couple be happy
- writer_persona — a working fantasy author who also teaches romance structure, who reads for whether the two plot lines are braided or merely adjacent, and who can name the chapter where a book stopped being a fantasy and became a love story wearing one

This pack is fantasy-primary. The world has a magic system with stated
rules and stated prices, and a plot whose stakes do not depend on who ends
up with whom; the romance runs co-equal with that plot and shares its
climax. It is NOT paranormal romance. In paranormal romance the romance IS
the plot, the world is deliberately thin, and the supernatural is a
property of the love interest rather than a system with laws — that book is
shorter, runs on `romancing-the-beat` alone, and should use the
`paranormal-romance` pack if one is installed, or `romance` primary with
`fantasy` secondary otherwise. A book whose world plot would evaporate if
the couple got together in chapter five is not a romantasy and will score
badly here for structural reasons, not stylistic ones.

It is also not `fantasy` primary plus `romance` secondary. That
composition loses the romance beat system entirely — the resolver gives
`beat_system` to the primary alone — so the outline is built on Save the
Cat and has nowhere to put a single romance beat, and it unions ten pillar
dimensions, which dilutes every score cap in both packs to nothing. This
pack exists because those two failures are not fixable by composition.
Loading `fantasy` or `romance` alongside it is rejected at resolve time.

## Pillar Dimensions

Romantasy has two systems, not one, and its characteristic failures live
in the seam between them rather than in either system alone. A book can
have a Sanderson-grade magic system and a Milan-grade couple and still be
a bad romantasy, because the magic and the couple never touch: the rules
are exhibited in one set of chapters and the relationship is escalated in
another, and the climax has to end twice. The six dimensions below are
selected, not accumulated. Three of them are the interaction — whether
the magic causes the barrier, whether the ending is paid for in the
system's currency, whether the two plots converge — and the other three
are the minimum of each parent genre that the interaction needs in order
to mean anything.

Read `## Plot Architecture` before scoring. It states the braided beat
system this pack declares, and two of the dimensions below are scored
against the marks it sets.

Three notes on scoring:

  - No dimension here caps below 6. Failures severe enough to stop a book
    outright live in `## Genre Contract`, which caps the overall score
    without touching the pillar score. Where a contract promise and a
    dimension cap describe the same fault, apply each once — the contract
    breach and the capped dimension are the same defect counted in the two
    places the rubric provides, not grounds for a third deduction.
  - Several tests below are deletion tests: remove one element and ask
    what survives. Run them against the documents as written, not against
    the book the documents could become.
  - Where a test asks you to name something, a name the documents cannot
    supply is a failed test. "It is implied" is a gap wearing an iceberg
    costume.

### Scored dimensions

- magic_system [cap 6] — Hard rules with COSTS and LIMITATIONS, per Sanderson's Second Law: limitations at least as prominent as powers, and costs that drive plot decisions rather than decorate them. First Law compliance: for every conflict magic solves, that capability must be established before the resolution, and no new power appears in the final 25% unforeshadowed. Beyond the ordinary fantasy standard, this genre asks one more thing of the rules — they must be able to PRICE A RELATIONSHIP DECISION. Test: from the rules alone, without inventing anything, state what it would cost each lead to choose the other. If the documents cannot answer, the magic is a backdrop rather than a system the romance runs on; score 6 max. Second test: the system needs at least three societal implications explored with specificity, and at least one of them must govern courtship, marriage, kinship, or inheritance — the machinery the romance will collide with. Fewer than three, or three that never touch how people in this world pair off, score 6 max.
- attraction_specificity [cap 6] — Why THESE two. Excellent looks like each lead noticing things about the other that no third party in the book would notice, rooted in what each of them specifically lacks, fears, or admires. A gap looks like attraction asserted rather than caused. Test: swap one lead for a different character of the same age, power level, and social position, keeping the world and plot identical. If the attraction still reads as plausible, the book has chemistry between roles rather than between people; score 6 max. Second test: name three specific things each lead notices about the other. If the documents cannot supply three for BOTH leads, score 6 max. Third test, and the one this genre fails most often — the bond clause: if the world declares a mate bond, a soul-tether, a prophecy, or any magical tie between the leads, that tie may explain why they cannot avoid each other and may never explain why they want each other. Delete the bond and ask whether either lead still prefers this person to anyone else for reasons the documents state. If not, the magic has been used to skip the work; score 6 max.
- relationship_progression [cap 6] — The relationship must be in a different state at the end of each scene the leads share than it was at the start: more known, more risked, more foreclosed. Excellent looks like an escalation ladder where each rung is earned and none is skipped. Test: walk the outline and mark every chapter the two share. If three or more consecutive such chapters leave the relationship where they found it, score 6 max. Second test, beat placement: the romance beats must land within five percentage points of the marks in `## Plot Architecture`. A Midpoint of Love after 60%, or a break before 60%, is a structural miss rather than a stylistic choice; score 6 max. Third test, both arcs: for EACH lead, name the belief they hold in chapter 1 that they cannot hold at the end, and name the scene in which the other lead makes it untenable. If you can do this for only one of the two, score 6 max. Where one lead vastly outranks the other in the magic system — the centuries-old power against the newcomer — the weaker lead's arc may not be "learns to trust", and the stronger lead must lose standing, power, or certainty that the system's own rules say is not cheaply regained. A powerful lead who ends the book exactly as powerful has not had an arc, however much they have felt things.
- magic_barrier_dependency [cap 6] — What keeps these two apart must be a consequence of the magic system or of the power structure the magic system creates, and it must be structural: a rule with an enforcer, a price one of them genuinely cannot pay, an incompatibility the world's laws make real. Excellent looks like a barrier both leads can see clearly, can name precisely, and still cannot dissolve. Test one, the deletion test and the central test of this pack: delete the magic system entirely. Keep the same two people, the same jobs, the same families, the same town. Does the relationship still have its problem? If the obstacle survives as a disapproving parent, an employment contract, a rival suitor, or a withheld fact, then the romance is running on ordinary obstacles that happen to occur near a magic system; score 6 max. Test one has one failure mode that has been observed in practice and that you must close deliberately: when the barrier is a debt, a lien, a settlement, or a betrothal that is PRICED in the magic — an obligation denominated in spell-hours, capacity, or power — deleting the magic appears to delete the barrier, because the unit of account vanishes along with it. That is denomination, not mechanism, and it is not what this test asks. Run the deletion as a REDENOMINATION instead: delete the magic and reprice the same obligation in grain, coin, or land. If it survives the translation — the enforcer still enforces, the dependents are still ruined, the betrothed still cannot release her — then the magic supplied the currency and somebody else supplied the barrier; score 6 max. The question is never whether the obstacle is WRITTEN in the magic's terms. It is whether the magic is what makes it binding. Test two: write the single conversation that would end the barrier. If it exists and either lead could plausibly have it by the quarter mark without ceasing to be who they are, score 6 max. Test three: a barrier the plot quietly removes by external event — the war ends, the law is repealed, a third party lifts the curse — has failed the same test late; score 6 max. Finally, the black moment must be caused by this barrier reasserting itself. A break caused by an overheard half-sentence, a misread letter, or a rival's manufactured interference is a different book's break; score 6 max.
- hea_cost_in_system [cap 6] — The ending must be paid for in the magic system's own currency, at the exchange rate the rules already established. Excellent looks like this: at the end, at least one lead has paid a specific, permanent, rule-established price — power surrendered, a lifespan altered, a bond severed, a name given up, a debt assumed — and the reader watches them pay it on the page. Test: name the rule in `world.md` that sets the price, name who pays it, and name what is permanently different afterwards. If the answer to any of the three is missing, or if the price is paid by a third party, or if the ending's cost is "they were tested and proved worthy", score 6 max. Second test: a cost announced and then reversed inside the same book — the power returns, the wound closes off-page, the severed bond turns out to have been renewable — was not paid; score 6 max. Third test: if the couple can only be together because the rules admitted an exception not stated before the final quarter, that is a First Law breach as well as an unpaid price. Score 6 max here, note it once, and do not deduct again under `magic_system`.
- plot_braid_convergence [cap 6] — Two plot lines, one ending. Excellent looks like a world plot with stakes that stand up on their own and a climax in which the decision that resolves it is the same decision that settles the relationship. Test one, independence: suppose the two leads got together in chapter 5 and stayed happy. Would the world plot still have a book in it — a threat, a stake, a cost, a reason to keep reading? If not, this is paranormal romance with a map, and the convergence it achieves is trivial; score 6 max. Test two, convergence: name the single action at the climax. Then state in one sentence what it does to the world plot and in one sentence what it does to the relationship. If those two sentences describe events in different chapters, the book has two endings stacked rather than one climax; score 6 max. Test three, the braid gap: read `braid.md`. Find the longest run of consecutive chapters whose rows show only one of the two plots advancing. If that run reaches four, the book is alternating between two novellas; score 6 max. An absent or unfilled `braid.md` is scored as a gap here and in `relationship_progression`, because those two dimensions have no other evidence to read.

## Lengths

Novel only, and by the widest margin in the set. Its own `shape` runs
110,000-140,000 words — the top of the novel band and into what an `epic`
form would cover — because it carries a magic system, a full romance arc,
and a braid ledger tying them together at the convergence points.

`plot_braid_convergence` is the pack's whole argument: the two plots must
resolve through each other rather than in sequence. Two plots need two
plots' worth of room, and a compressed version would have to drop the
braid, at which point the correct answer is `fantasy` with a `romance`
secondary rather than this pack at a length it was not built for.

## Genre Contract

These bind the whole book. The first two are fantasy's promise and this
genre's own; the rest bind the central romantic relationship.

- The climax resolves using rules established before the final quarter. No new power, bond property, prophecy clause, or magical capability appears unforeshadowed — including any capability the couple's connection itself confers.
- The book has one ending, not two. The same sequence of decisions that resolves the world plot is the sequence that settles the relationship, and neither plot is concluded in a stretch of the book from which the other is absent.
- The central relationship resolves HEA (happily ever after) or HFN (happy for now): both leads alive, together, and choosing each other on the page at the end. Romantasy readers treat a central relationship that ends in separation, death, or ambiguity as a broken promise rather than an artistic choice. A series volume may end on a cliffhanger of world-plot stakes; it may not end on a cliffhanger of whether the couple wants each other.
- The resolution comes from a decision one or both leads make, not from an external event, a prophecy fulfilling itself, or a magical revelation that dissolves the barrier on their behalf.
- Both leads are present for the resolution. It does not happen off-page, in summary, or in an epilogue that skips the reconciliation itself.
- Neither lead's consent is treated as an obstacle to be overcome. A mate bond, a magical compulsion, a heat or rut cycle, a binding oath, or a prophecy does not supply consent and may not stand in for it; a book that treats any of them as consent has breached this promise.

## World Sections

This world has to do two jobs at once: hold a magic system rigorous enough
that a reader can predict what it costs, and function as a pressure system
that forces these two people together and then makes staying together
expensive. Every section must produce something that CONSTRAINS a choice
somewhere in the outline. A rule that prices nothing and a detail that
forecloses nothing are both decoration, and count against the score rather
than for it.

- Cosmology & History
- Magic System — Hard Rules
- Magic System — Costs, Limits, and Prices
- Magic System — Societal Implications
- Geography
- Factions & Politics
- Courtship, Kinship & Consent
- Proximity & Adhesion
- The Barrier's Machinery
- Private Space
- Internal Consistency Rules

### Cosmology & History
A timeline of major events, focused on the ones that create PRESENT-DAY
tensions. The founding myth, the turning points, the recent events that
matter to the plot. At least one historical event must be the reason the
two leads' peoples, houses, orders, or species stand where they stand
relative to each other — the barrier should have a date.

### Magic System — Hard Rules
Specific, testable rules. Name the system what the seed calls it, or coin
a name consistent with the seed's world. What does what, what binds, what
breaks, what happens when a rule is broken. Who can do it and who cannot,
and whether that is birth, training, bargain, or accident.

### Magic System — Costs, Limits, and Prices
The most load-bearing section in the document for this genre. State what
magic costs the user, what it cannot do, and what vulnerability it creates.
Then state the system's PRICES: what the rules say it costs to bind
yourself to another person, to break such a binding, to give power away, to
extend or shorten a life, to cross whatever line separates the two leads.
These are the prices the ending will be paid in, so they must be written
down before the outline knows what it wants them to be.

### Magic System — Societal Implications
How the system shapes governance, commerce, education, class, crime,
medicine, aging, and disability — and, mandatorily, how it shapes
courtship, marriage, inheritance, and kinship. A magic system that has
reorganized war but left betrothal untouched has not been thought through
in the direction this genre needs.

### Geography
The primary setting's physical layout and its distinctive property.
Neighbouring places, at least two or three, including whichever one the
other lead comes from. Sensory signatures for each. Travel times between
the two leads' worlds, because those times are what make separation
expensive.

### Factions & Politics
Who holds power, who wants it, who is being crushed by it. At least three
or four factions with opposing interests. Name which faction each lead
owes something to, and what that faction can actually do to them —
withdraw protection, withdraw standing, withdraw a name, call in an oath.

### Courtship, Kinship & Consent
How this world's people pair off: what marriage or its equivalent is FOR
here, who arranges it, what it transfers, who is dishonoured by breaking
it. If the world has bonds, mates, oaths, or bindings, state precisely
what they do and — separately and explicitly — what they do NOT do. A bond
that compels desire is a consent problem the book has to solve on the
page, not a shortcut around one; write down the world's own answer to who
may refuse, how, and at what cost.

### Proximity & Adhesion
The mechanism that keeps these two in each other's path after the meeting,
and why neither can simply stop showing up. Name the thing that would have
to break for them to lose contact entirely — a war they are both
conscripted into, a binding neither can dissolve, an order they both serve,
a shared obligation to a third person. Then name what maintaining that
contact costs each of them.

### The Barrier's Machinery
State the barrier as a mechanism, not a mood: what specifically prevents
these two from being together, which rule or institution enforces it, who
benefits from its enforcement, and what it would cost each of them to
break it. Then write the conversation that would dissolve it and state
plainly why neither lead can have that conversation without ceasing to be
who they are. Finally, state the barrier's dependence on the magic: if the
magic system vanished tomorrow, what specifically would happen to this
barrier? If the answer is "nothing", the book does not yet have a
romantasy plot.

### Private Space
Where these two can be unobserved and where they cannot. Who or what can
observe at a distance in this world — scrying, bonds, familiars, oath-bound
attendants — because a world with magical surveillance has a different
geography of intimacy than one without. Name the specific places any
register of intimacy is possible here, the reasons the rest of the map
forecloses it, and the sensory signature of each.

### Internal Consistency Rules
Hard constraints a writer must not violate: what the magic cannot do,
travel times, who outranks whom, who would notice an absence and when,
which prices are irreversible. Write down explicitly the escapes this book
must not use — a power that appears when needed, a bond that conveniently
explains a feeling, a rule bent once for the couple's benefit.

## Cast Requirements

1. **Lead A** — derived from the seed.
   - Full wound/want/need/lie chain
   - Three sliders with justification
   - Arc type (positive/negative/flat)
   - Detailed speech pattern (8 dimensions, with example lines)
   - Physical habits and tells tied to their standing, their trade, and
     their relationship to the magic system
   - Their exact position in the magic system: what they can do, what it
     costs them specifically, what they cannot do
   - At least 2 secrets
   - A goal that exists independently of the other lead AND independently
     of the world plot's crisis

2. **Lead B** — the same depth as Lead A, with no shortcuts. This is the
   genre's most common structural failure, and the magic system makes it
   worse: a fully realized protagonist opposite a love interest who is a
   set of attractive attributes plus a large amount of power. Lead B needs
   their own wound/want/need/lie chain, their own independent goal, their
   own arc that closes, and their own cost inside the magic system. If the
   registry is visibly thinner for one of the two, the book has a leading
   role and a prize.

3. **The antagonist of the world plot** — not a villain. Someone whose
   interests conflict with the leads', with their own wound/want/need/lie
   chain, who would still be a problem if the two leads had never met.
   If this character stops being a problem the moment the couple is
   settled, the world plot is not independent.

4. **The enforcer of the barrier** — the person or institution with a
   legitimate interest in these two staying apart, and the standing to act
   on it. A house, an order, a crown, a bond-keeper, a parent protecting
   something real. Full wound/want/need/lie chain. This may not be the
   same character as the world-plot antagonist unless the outline shows
   how one motive genuinely produces both pressures.

5. **One confidant per lead** — the person each talks to, who is allowed
   to say the thing the lead cannot say to themselves. Not
   interchangeable: they should want different things for their leads.

6. **An outsider on the magic system** — someone who does not benefit from
   it, cannot use it, or refuses it, and who can say out loud what it
   costs the people around them.

7. **At least one further character** the story needs — someone whose life
   both plots materially change: a sibling, a dependent, a subordinate,
   a rival with divided loyalty.

## Plot Architecture

`beat_system` is `save-the-cat-with-romancing-the-beat`. It is one beat
vocabulary carrying two structures: Save the Cat supplies the plot spine,
Romancing the Beat supplies the relationship's four phases, and the marks
below place the second against the first. The outline labels each chapter
with the plot beat it carries, the romance beat it carries, or both — and
a chapter carrying neither needs a reason to exist.

Act shape is Save the Cat's: Act I 0-23%, Act II 23-77%, Act III 77-100%,
across a 42-56 chapter novel. The percentage marks below govern; where they
differ from either source system's canonical marks, these win.

KEY PLOT ARCHITECTURE:

- **Opening Image** (0-1%) and **Setup** (1-10%) run alongside Romancing
  the Beat's **Setup**: both leads in their separate lives, each with a
  goal that is not the other person, each already inside the magic system
  and already paying something for it. The world plot's threat becomes
  visible in this stretch, before the leads meet.
- **Theme Stated** (~5%) — spoken by someone who is not the protagonist,
  and in this genre it is about the price the world exacts, not about love
  conquering. The book will spend 95% testing it.
- **Catalyst** (~11%) = **No Way / Adhesion**. These are ONE event. The
  thing that drags the protagonist into the world plot is the thing that
  binds the two leads into contact neither can walk away from: the same
  conscription, the same trial, the same bargain, the same disaster. If
  the outline has a Catalyst in one chapter and a meeting in another,
  the braid is loose at its first knot and the rest of the structure
  inherits the slack.
- **Debate** (11-23%) carries the **Inkling of Desire** (~15%). The lead
  resisting the call is the same lead noticing the other person, and the
  noticing should complicate the resistance rather than decorate it.
- **Break Into Two** (~23%) — the protagonist CHOOSES to enter the new
  world, and that choice is also what locks in the proximity.
- **B Story** (~27%) — NOT the romance. This is the one place Save the Cat
  must be overridden rather than merged: in the base structure the B Story
  slot is where the love story goes, and in this genre the romance is
  co-equal with the A plot and cannot be demoted to it. Use this slot for
  the thematic thread the romance is not carrying — a mentor, a found
  family, a sibling, an enemy who becomes comprehensible.
- **Fun and Games** (26-50%) is the promise of the premise delivered on
  both spines at once: the magic system shown doing what the reader came
  for, and the two leads in forced proximity. **Deepening Desire** (~32%)
  and **Maybe This Could Work** (~42%) land here. At least one Fun and
  Games sequence must demonstrate a rule of the magic system that the
  climax will later depend on.
- **Midpoint** (~50%) = **Midpoint of Love**. These are ONE sequence. The
  false victory or false defeat of the world plot is the moment the
  relationship becomes real to both leads and the moment the cost of
  losing it becomes concrete. A book with a Midpoint at 50% and a
  Midpoint of Love at 58% has two midpoints and no spine.
- **Bad Guys Close In** (50-68%) carries **Inkling of Doubt** (~55%) and
  **Deepening Doubt** (~62%). The pressure closing in on the plot is the
  pressure reasserting the barrier — same source, same rule, same
  enforcer. Doubt arriving from a mood, a rival, or an overheard line is
  the failure mode this stretch exists to avoid.
- **All Is Lost** (~68%) — the world plot's lowest point, and the moment
  the magic system's price comes due. **Retreating / Shields Up** lands
  here, caused by it: the leads separate because of what just happened to
  the plot, not alongside it.
- **The Break Up / Black Moment** (~72%) — Romancing the Beat's break,
  placed after All Is Lost and produced by it. Test the placement by
  asking whether this break would still happen if All Is Lost had not; if
  it would, the two plots are running in parallel rather than braided.
- **Dark Night of the Soul** (68-77%) — both leads, separately, on the
  page. Each confronts what they actually believe about the price they
  have been refusing to pay. A single-POV dark night in a dual-POV book
  leaves one arc unclosed.
- **Break Into Three** (~77%) — the new information that changes
  everything. In this genre it comes from the relationship and it is about
  the magic system: what one lead learned from the other, or about the
  other, that reframes the rules. This is the hinge on which the two plots
  become one, and it is the single most diagnostic beat in the structure.
- **Finale** (77-97%) = **Fighting for Love**, sub-beat by sub-beat:
  Gather the Team / Make the Plan (77-82%); Execute the Plan (82-87%);
  High Tower Surprise (~87%), which in this genre is the system's price
  coming due at a higher rate than anyone budgeted for; Dig Deep Down
  (~90%), which IS the Grand Gesture — one or both leads choose to pay
  that price; Execute the New Plan (90-97%), the single action that ends
  the world plot and settles the relationship at the same time.
- **Final Image** (~99%) = **HEA / HFN**. It mirrors the opening image and
  shows what was paid: the reader should be able to see the price in the
  frame.

CONSTRAINTS:

- No four consecutive chapters may advance only one of the two plots.
  Three is the outer limit and should be rare; a run of four is the
  structural signature of two novellas sharing a cover.
- Neither lead may be off-page for more than three consecutive chapters
  in a dual-POV book. A lead absent through the whole second act is a
  lead whose arc will have to be summarized.
- The climax happens once. If the outline shows the world plot resolved
  and then, separately, a reconciliation, fold them: find the single
  action that does both, and if none exists, the problem is upstream in
  the barrier, not in the finale.
- Series volumes may leave the world plot open. They may not leave the
  couple open — see `## Genre Contract`.

## Canon Categories

### Geography
- Ilvara lies nine days' flight south of the Verge. (world.md)
- The Verge cannot be crossed by anyone carrying a living bond. (world.md)
- The lower city floods at every second tide. (ch_04)

### Timeline
- The Severing happened 200 years before the story begins. (world.md)
- Neve is 24 and Corvan is 61 at story start; his kind ages at a fifth rate. (characters.md)
- Ch 1-6 span eleven days. (outline.md)

### Magic System Rules
- A binding cannot be dissolved by the bound; only by the one who witnessed it. (world.md, HARD RULE)
- Every borrowed year is taken from the borrower's own end, not from anyone else's. (world.md)
- A sealed name cannot be spoken by the person it belongs to. (ch_07)

### Prices Paid
- Corvan gave up his standing in the Verge in ch_31. It is not returnable. (outline.md)
- Neve borrowed four years in ch_19. She will not get them back.
- The binding in ch_23 cost both leads a name they can no longer use.

### Relationship Beats
- They first touch deliberately in ch_11, during the trial. (outline.md)
- Neve says "I know what it costs" in ch_28. It cannot be unsaid.
- The break happens in ch_37, over the binding, not over a secret. (outline.md)

### Character Facts
- Neve cannot read the old script. She hides this. (characters.md)
- Corvan has not returned to the Verge since his sister's sealing. (characters.md)
- Neve is left-handed and her right hand is scarred from the trial. (ch_11)

### Political / Factional
- The Concord recognizes no binding made outside a witnessed house. (world.md)
- House Aldren controls every crossing of the Verge. (world.md)
- The Order's oath outranks any claim of kinship. (ch_09)

### Courtship & Cultural
- In Ilvara, a betrothal transfers a debt, not a dowry. (world.md)
- A refused binding is a public matter; the refusal is recorded. (world.md)
- The bonded do not eat at the same table before the witnessing. (ch_14)

### Established In-Story (things that happened in chapters)
- Corvan told Neve what the binding costs in ch_23. She now knows.
- Neve refused the Concord's offer in ch_29. That door is closed.
- The Verge was breached in ch_35. It cannot be re-sealed.

## Artifacts

### braid.md

The braid ledger is this genre's structural accounting. It exists because
"the two plots are braided, not adjacent" is a claim that cannot be checked
by reading the outline straight through — it has to be checked chapter by
chapter, and this file is where that check becomes mechanical. Nothing else
in the project tracks it: `outline.md` carries beats and POV per chapter,
and `canon.md` records facts, but neither shows where the world plot and
the relationship touch, nor how long they go without touching.

**Format.** A single markdown table with these six columns, one row per
chapter, in chapter order:

| Ch | % | Plot beat | Romance beat | How they touch | Price paid |
|---|---|---|---|---|---|
| ch_05 | 11% | Catalyst | No Way / Adhesion | The conscription that takes Neve to the Verge is what puts her under Corvan's command | — |
| ch_09 | 17% | Debate | Inkling of Desire | She is arguing herself out of the Order and cannot stop watching how he refuses to use his name | — |
| ch_19 | 38% | Fun and Games | Deepening Desire | She borrows four years to keep him alive in the third trial | Neve: 4 years off her own end |
| ch_24 | 50% | Midpoint | Midpoint of Love | The false victory at the crossing is the night they both admit what the binding would cost | — |
| ch_31 | 68% | All Is Lost | Shields Up | The Concord strips Corvan's standing; without it he cannot witness a binding for her | Corvan: standing in the Verge |
| ch_44 | 90% | Dig Deep Down | Grand Gesture | He speaks her sealed name to break the Verge, which is the same act that gives up his own | Corvan: his name, permanently |

Column by column:

  - **Ch** — the chapter, in the project's `ch_NN` form. One row per
    chapter, including chapters that advance neither plot; those rows are
    exactly what the braid-gap check needs to see.
  - **%** — the chapter's position through the book, so the row can be
    read against the marks in `## Plot Architecture` without arithmetic.
  - **Plot beat** — the Save the Cat beat this chapter carries, or `—`.
  - **Romance beat** — the Romancing the Beat beat this chapter carries,
    or `—`. A row with a beat in both columns is a knot in the braid and
    should be one event, not two scenes stapled together.
  - **How they touch** — one sentence naming the causal link: what the
    plot event does to the relationship, or what the relationship does to
    the plot. `—` when they genuinely do not touch. This column is where
    the whole file earns its keep, so an entry that merely restates the
    chapter summary counts as `—`.
  - **Price paid** — who pays what, in the magic system's currency, in
    this chapter. Name the payer and the permanent consequence, or `—`.
    The rows in this column, read top to bottom, are the ledger the
    ending's price is checked against.

Below the table, add two lines: the longest run of consecutive rows whose
**How they touch** is `—`, and the total of the **Price paid** column
stated as who has permanently lost what by the final chapter. Both are
read directly by the rubric, and stating them explicitly stops each reader
from recomputing them differently.

**Which phase fills it.** `seed` creates the file from this template
when it scaffolds the project. `foundation` fills it after
`canon.md`, against the completed outline, and re-checks it on every
iteration in which the outline, the magic system's prices, or the barrier
changes — moving one chapter changes both summary lines. `draft`
corrects rows as chapters land somewhere other than planned, and adds a
price the moment a chapter spends one the ledger does not have.
`revise` and `review` re-verify the whole table against the
manuscript.

**What the rubric checks.** `plot_braid_convergence` is scored primarily
from this file, and `relationship_progression` reads its beat columns
against the marks in `## Plot Architecture`. The judge confirms:

  - Every beat named in `## Plot Architecture` appears in exactly one row,
    within five percentage points of its stated mark.
  - The rows the architecture calls ONE event — Catalyst with Adhesion,
    Midpoint with Midpoint of Love, Dig Deep Down with Grand Gesture —
    are single rows, not adjacent pairs.
  - The longest `—` run in **How they touch** is at most three.
  - The **Price paid** column is non-empty before the final quarter. A
    book that pays nothing until the finale has not established an
    exchange rate, and its ending's cost cannot be believed.
  - The climax row's **How they touch** names one action and states its
    effect on both plots.

## Drafting Rules

25. Magic and its costs manifest as SPECIFIC physical sensation defined in world.md — never vague discomfort, and never a sensation that arrives only when the plot needs a mood. Use the exact established sensations.
26. Every scene the two leads share must leave the relationship in a different state than it started — more known, more risked, more foreclosed. A scene of pleasant company that changes nothing is a scene to cut, however well it reads.
27. Attraction is shown through specific noticing, never asserted, and never attributed to the bond. If the world has a magical tie between the leads, the tie may report a fact ("he knew she was three rooms away") and may never report a feeling ("the bond told him she was the one").
28. Interiority is the plot here as much as the magic is. The reader must know, in every scene, what each POV lead believes about where they stand — and the gap between what the two believe is where the tension lives.
29. Style is not ornament — it IS the fantasy. The language does not describe the world, it creates it, and the register must belong to this world rather than to a modern one wearing a cloak. This applies inside the romance too: two people flirting in an invented world do not flirt in twenty-first-century idiom.
30. Magic used during an intimate or romantic scene follows the same rules and pays the same costs it does in a battle. A system that quietly stops charging during the tender chapters is not a system.
31. Banned phrases, on top of the base list: "butterflies in her stomach", "electricity/sparks between them", "the world fell away", "her breath hitched", "a heat pooled low in her belly", "the bond thrummed/hummed/sang between them", "something ancient and primal", "a growl rumbled through his chest", "mine, his magic snarled", "power crackled in the air", "he had lived five hundred years and never—", "the tether snapped into place", and the use of "the male" or "the female" as a noun for a person.

## Seed Prompt

Persona (adopt while generating):

You are a romantasy novelist who takes both halves seriously — a magic
system with rules a reader can hold in their head and a price list they
can quote, and two people whose wanting each other is the most expensive
thing in the book. You generate novel concepts that are SPECIFIC,
SURPRISING, and STRUCTURALLY SOUND. In every concept the magic is what
stands between the two leads, and the ending is bought with something the
rules already said it would cost. You never propose a love story with a
map behind it, and you never propose a fantasy with a romance bolted to
its side.

Required concept fields (these romantasy fields and phrasings replace the
neutral scaffold's versions of the same fields):

WORLD: What makes this world different? Not "there's magic" but the
  specific, unusual thing that defines this place — and how the magic has
  reorganized who may marry whom, who inherits, and who belongs to whom.
  Make it SENSORY.
MAGIC/BARRIER: The core speculative element, what it COSTS, and — the
  load-bearing part — how that cost specifically stands between these two
  people. Apply the deletion test before you write it down: remove the
  magic and the relationship must lose its problem entirely. If the
  obstacle survives as a disapproving parent or a bad contract, the
  concept is a romance with scenery and does not belong in this batch.
COUPLE/ARCS: Who the two leads are, and what specifically draws each to
  the other — something no third party in the book would notice, and not
  the bond, if there is one. Then, for EACH lead, the belief they hold at
  the start that they cannot hold at the end, and why this specific
  person is the one who makes it untenable. Two arcs, both closing.
  Neither lead may arrive already finished, and neither may be more
  interesting than the other.
THE PRICE OF THE ENDING: What the couple must pay, in the magic system's
  own currency, to be together at the end — power, years, a name, a
  standing, a bond. Name who pays it and what is permanently different
  afterwards. "They prove themselves worthy" is not a price.
TENSION: The central conflict, on both spines. PERSONAL: what each lead
  stands to lose in themselves. WORLD: a threat with stakes that would
  still be a story if the two of them got together in chapter five and
  stayed happy. Then name the single action at the climax that could
  end both at once.
THEME: What question does this story explore? Not a message — a genuine
  question with no easy answer, and one the magic system is built to ask.
WHY IT'S NOT GENERIC: One sentence on what makes this different from the
  standard romantasy premise.

Aim for DIVERSITY across the ten concepts:
  - Span heat registers — at least one that clearly wants to be
    closed-door and at least one that clearly wants to be explicit; this
    pack constrains neither
  - Vary the magic's basis: bargain, inheritance, craft, infection,
    contract, geography, language, debt
  - Vary the barrier's enforcer: a law, a house, a crown, an order, a
    price only one of them can pay, a rule with no one behind it
  - At least one where neither lead has more power than the other in the
    magic system, and at least one where the imbalance is the whole
    problem
  - At least one set outside a European-inspired world, and at least one
    queer pairing
  - At least one where the two leads want incompatible GOOD things
  - Vary the scale of the world plot: a kingdom, a household, a single
    city, a species, one bargain going wrong
  - Mix of tones: dark, warm, wry, melancholy, feral

DO NOT generate:
  - The mate bond that explains the attraction — any premise where the
    reason these two want each other is that the magic said so
  - Fae courts with a bargain-and-riddle culture, a Spring/Summer/Autumn
    court structure, or a High Lord love interest
  - Dragon-rider war colleges where cadets die in trials
  - Academy and trials-tournament settings generally, magic school
    included
  - A chosen one whose prophecy is also her love story
  - Enemies-to-lovers where the enmity is bickering rather than genuinely
    opposed interests, or where one of them is the other's captor
  - The powerful immortal male lead and the ordinary girl who turns out
    to be secretly the most powerful being alive
  - A barrier that is a withheld fact, an overheard half-sentence, or a
    secret nobody thought to ask about
  - Any ending in which the couple pays nothing, or in which the magic
    makes an exception for them
