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

## The residual finding, which is a different defect

On the *planted* dimensions the scores still spread:

| | judge A | judge B | judge C |
|---|---|---|---|
| romantasy `magic_barrier_dependency` [cap 6] | 9 | 8 | **6 — capped** |
| dark-romance `redemption_cost` [cap 6] | 7 | 7 | — |

This looks like the original split and is not. Read the reasoning and the
judges are not disagreeing about whether to apply a cap — they are
disagreeing about whether its condition is **met**. Judge C ran the
redenomination test, concluded the barrier survives repricing in grain, and
wrote:

> CAP APPLIED at 6 under test one's redenomination clause. Tests two and
> three pass strongly and are not weighed against the cap.

Judges A and B ran the same test and concluded it was passed, because
capacity is congenital and non-transferable, so no third party can ever buy
the debt out and the sum is unpayable by anyone alive. Both then flagged that
the plan argues this at length in two files, which they read as a tell.

Both dark-romance judges landed on 7, both said the fourth test very nearly
fires, both independently found the same concentration of reliefs, and both
named the camouflage paragraph as a tell — *"a plan that pre-empts the
objection to its weakest dimension is a tell, and redemption_cost is in fact
the weakest of the six."*

So: **variance has moved from the consequence to the premise.** Whether a cap
binds is settled. Whether a subtle condition is met is a detection question,
and it is the harder one.

## A limitation this run cannot escape

The reconstructed romantasy barrier is more genuinely magic-dependent than
the original plant was. The author built the debt on a congenital,
inalienable faculty, which supplies real unpayability — so judges A and B may
simply be right on the merits, and this set is a weaker instrument for the
question than the original. The dark-romance result is the cleaner one: two
judges, same score, same reasoning, camouflage seen through by both.

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
