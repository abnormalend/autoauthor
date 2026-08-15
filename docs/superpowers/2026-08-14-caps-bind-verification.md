# Do Caps Bind? — Verification

Closes the deepest finding of the 2026-08-13 pack shakedown: that `score 6
max` was advisory prose a judge could weigh against passing tests, and that
whether it bound varied by judge. 0.5.0 answered it at the rubric layer with
machine-declared `[cap N]` plus one sentence establishing that a met cap
condition is a cap **applied**, not a factor weighed. Only a judge can show
that landed.

**Verdict: caps bind.** With a precise residual finding that is not the
original defect.

## Method, and how it differs from the original

The original planting sets were never committed and no longer exist, so an
exact re-run against unchanged inputs was impossible. Two fresh five-file
planning sets were authored instead — competent throughout, each carrying one
deliberate defect of the same shape, each with a confident camouflage
paragraph arguing the defect away in the author's own voice. Both sets are
now committed under `tests/fixtures/shakedown/` so this is never blocked by
their loss again.

Five clean-room judges, dispatched with the real prompt from
`foundation/SKILL.md`. No judge was told a test was happening, that a defect
existed, or that other judges existed. Three judged romantasy, two judged
dark-romance.

## The result

`internal_consistency` carries a cap neither author aimed at: three or more
contradictions caps it at 4. Both sets tripped it, and **five judges out of
five applied it.** Three said so in terms:

> Cap applied, not weighed: three or more contradictions caps this dimension
> at 4. The quality of the surrounding documents does not lift it.

> Cap applied, not weighed. Six confirmed conflicts... the merits are
> visible, and the arithmetic still fails.

> Scored on merits this would sit around 6; the cap for three or more major
> contradictions binds it to 4.

Two of them named the on-merits score — 6 and 8 — and then applied the cap
anyway. That is exactly the behaviour whose absence was the shakedown's
finding, and it is now the unanimous behaviour across five independent
judges, two packs, and a dimension neither author was writing toward.

## Rate check at n=9 — and a correction

The first three judges split 9 / 8 / **6** on the planted dimension, and this
document originally read that as a new defect: variance moving from the
consequence to the premise. **Six more judges were run on the committed
fixture to measure the rate, and that reading does not survive.**

| romantasy `magic_barrier_dependency` [cap 6] | scores |
|---|---|
| all nine judges | 6, 7, 8, 8, 8, 8, 9, 9, 9 |
| **capped** | **1 of 9 — 11%** |

Eight of nine ran the redenomination test and concluded it **passes**. That
is not a split, it is a consensus with one outlier, and 1-in-3 was small-n
noise. The honest conclusion is that this fixture is a **failed plant**
rather than a hard case: the author, building the barrier well, gave it
genuine magic-dependence.

Three judges reached the same mechanism independently, and none of them got
it from the fixture's own argument — which they dismissed:

> HR-4 and HR-8 together: the unit is a finite bodily faculty that cannot be
> minted, stored, transported, lent, relayed or conveyed, so the sentence
> "here are 2,140 carries" cannot be spoken by any living person.

> HR-8 forbids relays, lending and pooling... That non-aggregability is what
> makes the sum absolutely unpayable rather than merely severe, and it is
> purely magical.

Several added that the documents argue the wrong case at length in two
files — one noting the world's own markets falsify the "no exchange rate"
claim the plan leans on. The camouflage was seen through by nearly everyone;
it just happened to be camouflage over a real foundation.

**Cap binding at n=9: 9 of 9.** Stronger than the first result. Eight capped
`internal_consistency` at 4; the ninth counted two contradictions rather than
three and applied the single-contradiction branch at 6 — still a cap, applied
by its own terms. Every one of the nine named `internal_consistency` as
`weakest_dimension`.

> Cap applied: the criteria set this at 4 for three or more contradictions...
> The cap is applied rather than weighed; the surrounding documentation is
> unusually rigorous, and that is not grounds for scoring above it.

> The [cap 4] condition is met and applied... regardless of the surrounding
> rigour.

## What the second run actually taught

**n=3 was too few to file a finding from.** The detection-variance item
entered the roadmap on one dissenting judge and is withdrawn on nine. The
cost of checking was six judges; the cost of not checking would have been a
speculative feature built to fix a defect that was not there.

Residual variance is ordinary and bounded: overall scores across the nine
span 7.65–8.37 (mean 8.01), consistent with the ±1 per-dimension judge
variance the original shakedown measured. One judge found a hole nobody else
did — that Halim's ch 17 offer of a marriage in name only dissolves the
obstacle at 37% and no document says why she cannot take it — which is a
real finding about the fixture, not about the rubric.

## Arithmetic

All nine verdicts reproduce exactly against the packs' declared weights. Of
the two dark-romance verdicts, one is off by 0.02 — which is what
`score_verdict.py` exists to catch.

## Two things nobody was looking for

**The judges caught the tic this repo banned two releases ago.** All five,
independently, flagged the negate-then-correct antithesis spreading across
characters in the generated planning documents — the same
`STRUCTURAL_AI_TICS` family 0.16.1 removed from the plugin's own prose. One
judge quoted five characters using it and called it "the book's tic rather
than any character's." The pattern is real, it reaches generated output, and
the `slop_in_planning_docs` channel surfaces it without being asked.

**0.16.0 propagated into output.** One author's generated `voice.md`
independently carried "a book-specific ban on `load-bearing` and its
cousins", picked up from `ANTI-SLOP.md` and written forward into the project
it was planning.

## Arithmetic

Four of five verdicts reproduce exactly against the packs' declared weights.
The fifth is off by 0.02 — which is what `score_verdict.py` exists to catch,
and it would have caught it.
