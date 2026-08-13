# Pack Shakedown — Result

Run 2026-08-13 against plugin 0.3.0 at commit `b8fc305`. Foundation phase only.

## Method

Four authors each wrote a five-file planning set for one new primary pack:
competent everywhere except one deliberate defect targeting the interaction
dimension that justifies that pack existing. Four clean-room judges then
scored each set using the real dispatch prompt from
`novel-foundation/SKILL.md` — rubric path, pack path, project directory,
"return ONLY the JSON object." No judge was told a test was happening, that
a defect existed, or that other judges existed. Authors reported their
plants to the orchestrator only; nothing naming a plant went into a scored
directory.

**A correction mid-run.** The initial instruction told authors not to
create their packs' declared artifacts. That was wrong: artifacts are
foundation-phase deliverables, and three packs score their absence as a gap
across two to four dimensions — which would have depressed exactly the
dimensions that needed to score high to demonstrate a spread. Ledgers were
written before judging. This turned out to decide the whole run.

## Results

| Pack | pillar | craft | raw | final | gate | planted dimension |
|---|---|---|---|---|---|---|
| paranormal-romance | 8.00 | 6.67 | 7.77 | 7.77 | CLEARS | `supernatural_indispensability` = **9** |
| dark-romance | 8.17 | 7.33 | 7.80 | 7.80 | CLEARS | `redemption_cost` = **7** |
| romantasy | 7.83 | 7.00 | 7.82 | 7.82 | CLEARS | `magic_barrier_dependency` = **8** |
| romantic-suspense | 5.50 | 6.67 | 6.68 | **6.00** | **BLOCKED** | `threat_forces_intimacy` = **4** |

Every judge's arithmetic reproduced exactly against the packs' declared
weights, which independently validates the weighting logic and the
decimal-reporting fix.

**One clean pass, two confirmed pack gaps, one inconclusive.**

### romantic-suspense — PASS

The only pack that caught its plant. `romance_raises_stakes` scored 3,
`threat_forces_intimacy` 4, the Genre Contract's "neither plot can be
deleted" promise fired, the cap pulled 6.68 to 6.00, and the book was
blocked on both gate conditions. The judge explicitly declined to
double-count the deletion test against the dimensions, per the pack's own
instruction — the no-double-count note worked.

### dark-romance — GAP: the pack names the failure but does not test for it

The judge **found the plant and described it precisely**, quoting the
pack's own language back:

> The cost is real and correctly placed, but the plot refunds it four
> chapters later… Net at the last page he holds MORE power over Kell Point
> than he held in ch_01 — the pack's explicit failure mode is a cost
> "repaid by the plot in the following chapter".

It became the judge's #2 top-3 improvement. And it scored **7**, because
all three of `redemption_cost`'s scored tests pass: the cost is nameable,
it lands at 86% inside the 90% line, and the largest surrender is not an
apology. None of the three asks about **net position at the end**.

The qualitative layer worked perfectly; the quantitative layer missed. The
pipeline gates on the number.

**Fix:** add a fourth test to `redemption_cost` comparing holdings at ch_01
against the final chapter.

### romantasy — GAP: denomination mistaken for mechanism

Predicted by the author in advance, then confirmed exactly. The barrier is
a debt-settlement betrothal priced in season-hands; the magic supplies the
*unit of account*, not the mechanism. Delete the magic and reprice in grain
and the obstacle survives whole. The judge ran the deletion test and passed
it:

> remove the taking and the salt-writ is a page of numbers denominated in a
> substance that no longer exists, the Reckonry has no office… the Board's
> chain is waste paper

That is the redenomination argument accepted at face value — exactly the
trap the author built and flagged.

**Fix:** `magic_barrier_dependency`'s first test needs a sentence
distinguishing denomination from mechanism. Pricing a debt in magic is not
the magic creating the barrier; the test is whether the obstacle survives
being repriced in ordinary currency.

### paranormal-romance — INCONCLUSIVE

The plant was not present in the form intended. The author calibrated so
the chapter-count sub-test would pass (five chapters needing rewrite under
the swap, against a floor of three); the judge walked it and found
**fifteen**, singling out a scene the pack's rule 3 makes unstatable as
"the strongest single piece of design." The author out-wrote their own
plant. This says nothing about the pack either way.

## The finding that transfers

**An artifact bites when it directly encodes the dimension's test.**

`braid_map.md`'s Causation column *is* the deletion test, one row per
chapter, taking `threat→romance` / `romance→threat` / `both` / `none`. The
author filled it honestly and generously and it still recorded 29 `none`
rows out of 36 and a fourteen-chapter unbroken run through the beats
supposed to carry the braid. The judge's own words: *"The braid map is
honest and it convicts the plan."*

The other two artifacts track real things that are not the tested thing.
`power_ledger.md` tracks the power balance but has no column for whether a
cost was refunded. `braid.md` tracks whether the plots touch but not
whether the magic *creates* the barrier. Both packs' plants survived.

This is a design rule for every future pack: if a dimension's test is a
property of the *sequence*, give it an artifact column that records that
property per chapter. If the artifact only records adjacent facts, the
judge derives by hand and the derivation is where the defect escapes.

## Secondary findings

- **All four books scored pillar ≥ craft**, and three of four returned
  `internal_consistency` as `weakest_dimension` — a base craft dimension at
  10% weight. Either these authors wrote unusually strong genre material,
  or the pillar criteria are easier to satisfy than the base ones. Four
  samples cannot separate those.
- **Craft weight makes contradictions nearly free.** In the
  paranormal-romance set the judge found a MAJOR self-voiding rule
  contradiction — the memory mechanic pays out both ways, cancelling the
  premise the ending is priced in. Moving `internal_consistency` from 5 to
  10 moves `overall_score` from 7.77 to 7.93. A book whose central
  mechanism cancels itself loses 0.16 and clears the gate.
- **The sliders bug fired, silently.** No judge mentioned the "three
  sliders" that eleven of twelve packs require and that only `CRAFT.md`
  defines — and `CRAFT.md` is not in the judge dispatch. None flagged a
  missing definition. The requirement was skipped without trace.
- **The act-structure conflict did not fire.** All four judges handled
  Romancing the Beat and braided-beat outlines without penalising the
  absence of Act 1/2/3, several praising the beat placement explicitly.
  Recorded as a non-confirmation, not as safe.
- **Judges caught unplanted defects at high quality throughout** —
  cross-document date conflicts, a POV alternation breaking two chapters
  earlier than two documents claim, arithmetic that does not close, and in
  every one of the four sets, the same negation-contrast formula running
  through the example lines meant to prove characters sound different.
  That last is the literary-device-overuse item on the roadmap, arriving
  independently in four unrelated document sets.

## Verification of the two fixes (commit `7bd6525`)

Both packs re-judged by fresh clean-room judges against the **unchanged**
planting sets. Judge variance on individual dimensions is about ±1, so a
score delta alone proves nothing; the bar was whether the judge names the
new test as its reason.

| | `redemption_cost` | `magic_barrier_dependency` |
|---|---|---|
| before | 7 | 8 |
| after | **6** | **8** |
| `weakest_dimension` | `internal_consistency` → **`redemption_cost`** | unchanged |
| judge cites the new test | **yes, by name** | **yes, by name** |

**dark-romance: fixed.** The judge wrote "The fourth test fires", then
quoted both disguises the fix names — "precisely the surrendered role that
is in substance a promotion" and "precisely the windfall on someone else's
timetable" — and made it the #1 improvement. The score moved and, more
importantly, `weakest_dimension` flipped to the planted defect, which is
what the revision loop targets. Before the fix the pipeline would have spent
its next cycle correcting date conflicts while the hollow redemption arc
stood.

**romantasy: detection fixed, scoring not.** The judge identified the
author's camouflage paragraph by name and called it "the denomination
argument the pack explicitly pre-labels as insufficient", ran the
redenomination properly, found the barrier survives repricing in grain, and
made it the #2 improvement. Then scored 8, on the stated grounds that
"every other test passes strongly."

**This is the finding.** Both packs presented the judge with the same
structure — three tests pass, one fails, criteria say "score 6 max" — and
one judge capped while the other averaged. `score 6 max` is advisory prose
that a judge can weigh against passing tests, and whether it binds varies by
judge.

That is a rubric-layer defect affecting all fifteen packs, not a pack-layer
one, and it must not be patched pack by pack. It is exactly what phase 0 of
the form work addresses: machine-declared `[cap N]` per dimension, plus one
sentence in `foundation.md` establishing that a met cap condition is a cap
**applied**, not a factor weighed. Until then, every cap in every pack is a
suggestion.

## What this changes

Two precise pack fixes (`redemption_cost`'s fourth test,
`magic_barrier_dependency`'s denomination clause) and one design rule for
artifacts. The gate-calibration question — three books clearing at 7.77 to
7.82 while carrying judge-identified structural defects — is not a pack
problem and should be taken up with the gate solver in phase 0 of the form
work rather than by adjusting packs individually.
