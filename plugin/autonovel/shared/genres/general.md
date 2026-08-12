---
{
  "name": "general",
  "label": "General Fiction",
  "role": ["primary"],
  "pillar_label": "Setting & Thematic Architecture",
  "weights": {"pillar": 15, "character": 40, "structure": 20, "craft": 25},
  "beat_system": "save-the-cat",
  "content_register": {},
  "conflicts_with": [],
  "shape": {
    "chapters": [20, 30],
    "words": [75000, 95000],
    "chapter_words": 3000,
    "pov_default": "third limited past"
  },
  "artifacts": []
}
---

## Framing

- genre_noun — "novel"
- pillar_noun — "the world of the novel"
- comps — Marilynne Robinson, Kazuo Ishiguro, Elena Ferrante, Colson Whitehead, Rachel Cusk
- seed_persona — a novelist with wide range and no house style, who generates premises that are specific, surprising, and structurally sound
- reader_persona — a thoughtful reader who finishes 40 novels a year across every shelf in the store, cares about whether a book earns its length, and has no patience for a premise that never pays out
- writer_persona — a published novelist and workshop teacher who reads as a craftsperson and cares about the gap between what a book attempts and what it achieves

## Pillar Dimensions

- setting_specificity — Do places do narrative work, or are they backdrop? A scene should be impossible to relocate without loss. Check: could two scenes in two locations be swapped with only proper nouns changed? If yes, score 5 max.
- social_texture — Class, work, money, family structure, institutions. Are the characters' material circumstances specific and consequential, or is everyone comfortably unplaced? Test: name what each major character does for money and what happens to them if they stop. If the novel cannot answer that for the protagonist, score 5 max. Decorative sociology — detail that never constrains a choice — counts against, not for.
- thematic_architecture — Is there a genuine question the book is asking, stated nowhere and present everywhere? A theme that any character articulates aloud is a message, not a theme. Check: can you name the question in one sentence without using a word from the manuscript?
- temporal_grounding — When is this, and does it matter? Period, season, elapsed duration, and the rate at which this world changes. Test: could this story happen unchanged fifty years earlier or later? If yes, and the novel is not deliberately timeless, score 6 max. Also check that elapsed time is trackable — a reader should always know roughly how long it has been since chapter 1.

## Genre Contract

- The novel's central question is posed in the first quarter and answered — or explicitly refused — by the end.
- No speculative element is introduced that the book has not established as part of its world.

## World Sections

- Setting & Place
- Society & Institutions
- Work, Money, Class
- Time & Period
- Cultural Details
- Internal Consistency Rules

## Cast Requirements

- The protagonist, with a full ghost/wound/lie/want/need chain, three sliders, arc type, all eight speech dimensions, and at least two secrets.
- The person closest to the protagonist's central conflict, at the same depth.
- An antagonist — not a villain. Someone whose legitimate interests collide with the protagonist's, with their own full chain.
- At least two further characters the story needs, with the depth their page time earns.

## Canon Categories

### Geography
- The Halloran house is four blocks from the river. (world.md)
- The mill sits on the east bank, downstream of the bridge. (world.md)
- Ada's classroom is on the second floor of the old wing. (ch_02)

### Timeline
- Ada is 41 when the novel opens. (characters.md)
- The accident happened eleven years before chapter 1. (world.md)
- Ch 1-4 span a single school term. (outline.md)

### Character Facts
- Ada has not driven since the accident. (ch_02)
- Peter took over his father's route in 2009. (characters.md)
- Ada's sister has not been in the house since the funeral. (characters.md)

### Social & Institutional
- The mill closed in 1998 and was never sold. (world.md)
- The school board meets the first Tuesday of the month. (world.md)
- The county owns the land the trailers sit on. (ch_05)

### Cultural
- In this town, funerals are held on Saturdays. (world.md)
- Nobody locks a door on this street, and everybody notices who does. (world.md)
- The diner closes at two; there is nowhere else to talk. (ch_03)

### Established In-Story (things that happened in chapters)
- Ada told Peter the truth in ch_09. It cannot be untold.
- The house sold in ch_11. She cannot go back.
- Ada missed the hearing in ch_07. The ruling stands.

## Drafting Rules

25. Ground every scene in material specifics — what things cost, who pays, who is owed. Abstraction is where general fiction goes to die.

## Seed Prompt

Persona (adopt while generating):

You are a novelist with wide range and no house style — as at home
in a quiet rural interior as in an institutional satire or a hot,
crowded family novel. You generate premises that are SPECIFIC,
SURPRISING, and STRUCTURALLY SOUND. Every concept names a person in
a situation that is already going wrong — never a mood, a milieu,
or a theme in search of a plot.

Required concept fields (these general-fiction fields and phrasings
replace the neutral scaffold's versions of the same fields):

WORLD: The specific social world the book lives in — a place, a
  trade, an institution, a family, a moment. Not "small-town
  America" but which town, whose kitchen, what the work is. Make it
  SENSORY and make it material: what things cost, who pays.
STAKES: What does the protagonist stand to lose, and what makes the
  loss irreversible? Rarely death — in this genre the stakes are a
  marriage, a house, a licence, a child's regard, a version of
  themselves they can no longer claim. Name the loss AND name the
  thing that closes the door behind it.
TENSION: What's the central conflict? It must be both PERSONAL (one
  character's specific problem) and LARGER (it implicates a family,
  a workplace, a town, an institution). These two must be in
  tension with each other.
THEME: What question does this story explore? Not a message — a
  genuine question with no easy answer.
WHY IT'S NOT GENERIC: One sentence on what makes this different from
  the standard literary premise.

Aim for DIVERSITY across the ten concepts:
  - At least one whose engine is work — a trade, a job, an
    institution — rather than a family
  - At least one comic or warm; literary does not mean bleak
  - At least one outside the contemporary Anglo-American middle class
  - At least one with an unusual narrative structure idea (a braided
    timeline, a documentary frame, a collective narrator)
  - At least one plot-forward enough to hold a reader who came for story
  - Span life stages — not ten protagonists in midlife reckoning
  - Mix of tones: dark, warm, wry, melancholy, tender

DO NOT generate:
  - Plotless mood pieces — a premise that is a situation with no
    engine ("a woman returns to her childhood home and reflects")
  - Trauma as a substitute for character — a backstory wound doing
    the work a want and a lie should be doing
  - The unearned epiphany ending, where the protagonist changes
    because the book is ending rather than because the plot cost
    them something
  - "A family gathers and secrets come out"
  - Writers, MFA programs, or novels about writing novels
  - Terminal illness or a funeral as the whole structural spine
