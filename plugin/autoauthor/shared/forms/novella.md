---
{
  "name": "novella",
  "label": "Novella",
  "band": "intermediate",
  "words": [17500, 40000],
  "target_words": 30000,
  "chapter_words": 2500,
  "gate": {"overall": 7.0, "pillar": 6.5},
  "iteration_cap": 8,
  "layers": ["voice", "world", "characters", "outline", "canon"],
  "base_dimensions": {
    "drop": ["foreshadowing_balance"],
    "add": {"structure": ["single_line"]}
  }
}
---

## Framing

- form_noun — "novella"
- unit_noun — "chapter"
- reader_persona — a reader who will finish this in one long sitting or
  two, and who came for one story told properly rather than for a world to
  live in

The strongest argument for this axis after `short-story`. The novella has
become a real commercial category in the last decade — Tordotcom built an
imprint on it and it is a native ebook length — and it is the length worst
served by a novel pipeline: too long to wing, too short to earn a world
bible and a foreshadowing ledger.

The SFWA range, which is also where the market sits. `novelette`
(7,500–17,500) is deliberately not a form of its own: it is an awards
bucket with nothing acquired or browsed under the name, and it shares this
band regardless — so a work in that range takes whichever neighbouring
form's apparatus it needs.

`intermediate` is the band that falls back. A genre pack that has written
compressed-length criteria and not intermediate gets the compressed ones,
on the reasoning that a pack which has thought about five thousand words
has thought about most of what forty thousand needs, while the reverse is
not true.

## Form Contract

- One line of causation, followed the whole way. A novella may have a
  subplot; it may not have a second plot.
- The ending is the one the opening promised. There is not enough room to
  earn a swerve and then earn the ending as well.
- The world is established only where the story stands on it. A novella
  that opens with a chapter of orientation has spent an eighth of itself
  on furniture.

## Drafting Rules

25. Chapters run shorter than the genre's novel default would suggest —
    take `shape.chapter_words` as an upper bound here, not a target.
26. No chapter exists to move people between places. If a chapter's work
    can be a paragraph in the next one, it is a paragraph.

## Base Dimensions

- single_line — Can you state the book's causal spine in one sentence, and
  does every chapter sit on it? Take each chapter and name what it changes
  about the protagonist's position on that line. A chapter that changes
  nothing on it is a chapter serving a second plot. If two or more do,
  score 6 max. If the spine cannot be stated in one sentence from the
  plan, score 4 max.

## Foundation Guidance

Five layers. `world.md` returns — at thirty thousand words a story can
stand on a world and often must — but scoped to what the story touches,
and `MYSTERY.md` does not, because the questions a novella raises are
answered inside it rather than held across a series.

- `voice` — full, as always.
- `world` — the parts the plot stands on, and nothing built for a sequel.
- `characters` — full chains for the protagonist and the one character
  opposite them; page-time-proportional depth for anyone else.
- `outline` — chapter by chapter in the genre pack's beat vocabulary.
- `canon` — kept, because thirty thousand words is long enough to
  contradict yourself and short enough that the reader will notice.

Dropped, and why: `foreshadowing_balance` scores a tracked ledger. A
novella's plants and payoffs are close enough together to be visible in
the outline, and maintaining a separate ledger over twelve chapters costs
more than it catches. `single_line` replaces it as the structural check
that actually bites at this length.
