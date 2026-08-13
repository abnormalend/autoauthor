---
{
  "name": "novel",
  "label": "Novel",
  "band": "extended",
  "words": [40000, 120000],
  "target_words": 85000,
  "gate": {"overall": 7.5, "pillar": 7.0},
  "layers": ["voice", "world", "characters", "mystery", "outline",
             "foreshadowing", "canon"],
  "base_dimensions": {"drop": [], "add": {}}
}
---

## Framing

- form_noun — "novel"
- unit_noun — "chapter"
- reader_persona — a reader who has committed a week of evenings to this
  book and expects the middle to earn them

The word range is the SFWA/Nebula definition, which is what markets and
submission guidelines already assume. The 40,000 floor is the surprising
end of it — commercial fiction rarely sells below 70,000 — but it is
genuinely where "novel" begins, and a genre pack narrows it from there.
The ceiling is where `epic` would begin if it existed; a genre that runs
past it is not in error, it is simply straddling the boundary, and
`ranges_overlap` in form_pack.py exists so that the validator says so
rather than rejecting it.

## Form Contract

Binary promises about the form itself, checked the way a genre contract
is. A breach caps `overall_score` at 6 and never touches `pillar_score`.

- The book is complete in itself. A volume of a series may leave its
  world plot open; it may not leave its own central question unasked or
  its own protagonist mid-arc.
- The middle is load-bearing. A novel is not a short story with a delayed
  ending: the chapters between the midpoint and the black moment must
  change the protagonist's position, not restate it at greater length.

## Drafting Rules

25. Chapter count follows from `shape.chapter_words` and this form's
    target length. A genre's chapter granularity is a genre fact — a
    thriller's 1,900-word chapters against a fantasy's 3,200 — and the
    total is a form fact.

## Base Dimensions

All eight apply unchanged; a novel is the length every one of them was
written for. `base_dimensions.drop` stays empty here and earns its keep in
the shorter forms, where `foreshadowing_balance` scores a ledger the story
has no room to keep.

## Foundation Guidance

All seven layers are built. At this length the planning genuinely earns
itself: a weak plan costs the drafting loop far more than it costs to
plan again, which is why the foundation gate is the highest bar in the
pipeline. That reasoning is novel economics and does not survive a
translation to shorter forms, which is the whole reason `gate` lives on
the form and not in the rubric.

- `voice` — a full voice document with exemplars and anti-exemplars.
- `world` — the pillar layer, scoped by the genre pack's World Sections.
- `characters` — full wound/want/need/lie chains for the principals.
- `mystery` — the questions the book raises and where each is answered.
- `outline` — chapter by chapter, in the genre pack's beat vocabulary.
- `foreshadowing` — a tracked ledger; every plant has a planned payoff.
- `canon` — every hard fact, sourced, granular enough to catch a
  contradiction introduced in chapter 5.
