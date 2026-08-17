# Foundation-phase findings — 2026-08-17

Source: a full `/autoauthor:foundation` run on **Her Years, Our Years**
(`~/novels/redshift`), a 4-scene, 5,000-word hard-SF/YA **short story** built
from a detailed `seed.txt`. Six scored iterations, six judge dispatches. Score
trace: 7.45 → 7.68 → 7.56 (discard) → 8.04 → 8.03 (discard) → **8.14**, against
a form gate of 6.5 / 6.0.

These are findings about **the skills**, not about that story. Ordered by my
estimate of value. Each carries the evidence that produced it so a follow-up
session can judge whether the fix is worth making.

Paths are relative to `plugin/autoauthor/`.

**Caveat on n.** One run, one form, one genre stack, one seed. The judge-noise
findings (3, 7) are the ones I'd most want a second run to confirm; the
dispatch-contract and scale findings (4, 5, 11) are structural and don't need
replication.

---

## 1. The gate can be cleared while a capped dimension is actively broken

**Severity: high — following the skill literally would have shipped a plan that
stops a drafter mid-scene.**

`skills/foundation/SKILL.md` orders the loop: (1) evaluate, (2) gate check →
**exit**, (3) target the weakest dimension. Iteration 1 returned
`overall 7.45 / pillar 7.00` against a gate of `6.5 / 6.0`. Both cleared on the
first scored iteration, so step 2 fires and the phase exits.

At that moment the eval also reported:

- `internal_consistency: 4` — **the cap had fired** (3+ contradictions)
- `contradictions_found`: five, including *"The interval Kalei has alone… stated
  three times… Load-bearing: it is the pressure the whole second half runs on"*
  and a ten-hour telemetry block inside a ten-hour window
- `register_plausibility: 6` — cap fired, on a hand-wave the judge called *"a
  rule invented to escape the corner the plot is in"*

A plan can therefore satisfy the exit condition while two of seven dimensions
sit on caps and the outline contradicts itself about the clock the climax
depends on. The gate is a floor on the *weighted mean*; caps are the mechanism
the packs use to refuse a book something, and the mean lets a fired cap through
whenever the other categories are strong. Here character (8.0) and structure
(8.0) paid for craft (7.0) without either problem being fixed.

I continued past the gate on judgement and the score rose 0.69 over five more
iterations, with `internal_consistency` going 4 → 8 as the real contradictions
cleared. That improvement was available only by ignoring step 2.

**Proposed fix.** Add a second, non-negotiable exit condition to step 2:

```
Gate check. Exit only when ALL of:
  - overall_score > form.gate.overall
  - pillar_score  > form.gate.pillar
  - no scored dimension is sitting on a fired cap
  - contradictions_found is empty
```

The last two cost nothing when the plan is clean and are exactly the conditions
that mean "a writer will stop here." If that is judged too strict, the weaker
version still fixes the observed failure: *a fired cap forces at least one more
iteration, regardless of the mean.*

---

## 2. Keep/discard is score-only, and discards structurally better plans

**Severity: high. This bit twice in six iterations and I deviated from the skill
both times.**

Step 4 says: improved → commit; *"Score regressed → discard with
`git reset --hard HEAD`."* No epsilon, and no reading of *why* it regressed.

**Iteration 3 (7.68 → 7.56).** The revision fixed the transmission-cadence
fault — which two independent judges had separately called MAJOR and which the
iteration-2 eval named as the sole reason two dimensions were capped. It
regressed because, while rewriting, I introduced four *new* surface errors (a
stale "seven blocks" line, two wrong distances, a letter-typography split).
`register_plausibility` went 6 → 8 and `internal_consistency` went 6 → 4 in the
same pass. Discarding would have restored the major fault to recover 0.12.

**Iteration 5 (8.04 → 8.03).** A 0.01 delta — indistinguishable from noise —
while `pillar_score` rose 7.67 → 8.00 and two genuine cross-document
contradictions were fixed (`voice.md` and `characters.md` disagreeing about two
characters' signature cadences, in the file the drafter consults most).

I kept both trees and committed neither, so git history contains only improving
states and `results.tsv` records the true sequence. That works, but it is a
judgement the skill delegates silently and a less careful session would either
revert real progress or quietly stop logging.

**Proposed fix.** Two changes to step 4:

```
Score improved by more than 0.15 → commit.
Score within ±0.15 of best → TIE. Keep the state with fewer
  contradictions_found; if equal, keep the higher pillar_score.
Score regressed by more than 0.15 → before discarding, check whether the
  eval's contradictions_found are the SAME faults as last iteration or NEW
  ones. If the targeted fault is gone and new surface faults replaced it,
  the revision worked: keep it, and target the new faults next iteration.
  Discard only when the targeted dimension did not improve.
```

The distinction that matters is *"the fix was wrong"* versus *"the fix was right
and I dropped a wrench on the way out."* The current rule cannot tell them apart
and defaults to throwing away the fix.

---

## 3. Per-dimension judge noise is ±2, which swamps the deltas the loop steers on

**Severity: high — this undermines the loop's control signal.**

Two clean data points, both from documents where I can account for every edit.

**`outline_completeness`: 9 → 7 on an unchanged feature.** Iteration 4 scored it
**9** and its gap paragraph never mentioned the 04:47–10:05 span. Iteration 5
scored the same span **7**, calling it *"A five-hour hole… 26% of the story's
runtime with essentially no dramatized content assigned to it — a drafter
reaching 04:47 must stop and invent the interior of five hours."* The gap was
present and identical in both documents. Nothing I changed between them touched
it.

**`premise_dependence`: 8 → 7 with no premise-relevant edit.** Between
iterations 5 and 6 I changed: a stale harvest cross-reference, Mele's arrival
age, the codec's framing, and added one beat closing the dead zone above. None
of it touches the transposition test. The dimension moved a point anyway, and
took `pillar_score` from 8.00 to 7.67 with it.

Consequence: at iteration 5→6 the two headline numbers moved in **opposite
directions** on the same document family — `overall` 8.03 → 8.14 while `pillar`
8.00 → 7.67. The loop gates on both. A run that trusted single-run deltas would
oscillate.

**What the judges were reliable at.** Every one of the six independently
recomputed the physics, and all six got it right — γ, the Doppler factor, the
D·τ arrival law, the D⁴ link penalty, the byte budgets, every character age at
every date. Iteration 6's note lists roughly a dozen verifications and closes
*"Every one landed."* The judges are trustworthy on checkable claims and noisy
on holistic ones, which is a useful split.

**Proposed fix, cheapest first.**

1. Adopt the ±0.15 tie band from finding 2 so sub-noise deltas stop driving
   keep/discard.
2. Move the mechanical checks out of the judge. A `check_facts.py` that reads a
   declared fact table from the outline and re-derives the arithmetic would be
   deterministic, free, and would have caught every contradiction this run
   surfaced across four iterations — the judges found them one or two at a time
   because each ran once.
3. If budget allows at novel scale, dispatch the foundation judge **three times
   in parallel and take the median** per dimension. At compressed band that
   trebles an already disproportionate cost (finding 9), so it should be
   form-scoped rather than universal.

---

## 4. The eval dispatch never names `voice_wells.json`, so a required artifact is unscored

**Severity: medium-high, and the fix is one line.**

`references/layer-guides.md:261` requires it: *"After filling voice.md Part 2,
also write `voice_wells.json` in the project root."* `shared/scripts/
voice_fingerprint.py:30` reads it and errors rather than falling back.
`genre_pack.py:72` knows about it.

The eval dispatch in `SKILL.md` says: *"The input files are: `<the documents
form.layers calls for, named>`."* `form.layers` for `short-story` is
`["voice", "characters", "outline"]`, which resolves to three `.md` files.
`voice_wells.json` is never named, so it is never read and never scored.

Observed consequence: the iteration-4 judge wrote *"It cites `voice_wells.json`
as the record of the four wells, and **no such file exists in the project**…
a dangling promise in a document that trades on precision"* — and deducted from
`voice_clarity`. The file existed (2,301 bytes, committed with the initial
layers). The rubric correctly tells judges not to go looking for files they
weren't named, so the judge inferred absence from silence and was wrong.

**Proposed fix.** In the dispatch template, append the artifact to the file list
whenever the `voice` layer is present:

```
The input files are: <documents form.layers calls for>, and
`voice_wells.json` (the vocabulary wells the voice layer is required to emit).
```

**Related, worth a separate look:** the rubric should probably forbid asserting
the absence of a file it was not given. *"I was not shown X"* and *"X does not
exist"* are different findings and only one of them is scoreable.

---

## 5. `layer-guides.md` is novel-scaled and the form pack cannot suppress its literals

**Severity: medium-high. Same class as the revision phase's 1800-word floor.**

The form pack's `## Foundation Guidance` does good work: it names which layers
to build and what each *means* at 5,000 words. What it cannot do is switch off
specific requirements written into the guide as absolutes. Still live and still
novel-scaled when the form is `short-story`:

| `layer-guides.md` | Problem at 4 scenes / 5,000 words |
|---|---|
| `:221` "Include at LEAST 15 threads" | Ledger is dropped from scoring, but the prose requirement remains |
| `:201` "At least 3 chapters should be 'quiet'" | 3 of 4 scenes quiet in a story whose climax is a 700-word crisis |
| `:199` absent-but-plot-critical characters "must appear in person" | **Structurally impossible here — and the impossibility is the story's subject** |
| `:138` characters.md "Target ~3000-4000 words" | 60–80% of the story's own length |
| `:321` canon "80-120 entries… toward 400+" | Layer not built at this form at all |

The guide does say *"read the form pack's `## Foundation Guidance` first"* and
that *"a layer the form does not name is not a gap."* That covers whole layers.
It does not cover a requirement *inside* a layer the form does build — the
15-thread ledger and the 3 quiet chapters both live in `outline.md`, which the
form does call for.

What I actually did about it was write defensive prose *into the plan* — an
explicit "one deliberate inversion of the novel-scale guidance, stated so it
reads as a choice" paragraph justifying why Mele cannot appear in person. It
worked (no judge scored it as a gap) but it is 120 words of the plan spent
arguing with a guide rather than briefing a drafter, and it feeds finding 6.

**Proposed fix.** Give form packs a suppression list, parallel to the
`base_dimensions.drop` mechanism they already have:

```json
"layer_guide": {
  "suppress": [
    "foreshadowing.min_threads",
    "outline.min_quiet_chapters",
    "outline.absent_character_must_appear",
    "characters.word_target",
    "canon.entry_target"
  ]
}
```

…with the guide's absolutes tagged so they can be addressed by name. Cheaper
interim version: convert each literal in `layer-guides.md` into a ratio of the
resolved `shape` the way finding 1 of the revision doc proposes for the chapter
floor — "one quiet unit per four", "one tracked thread per 300 words" — so they
scale instead of needing suppression.

---

## 6. The rubric's justification requirement produces rubric-facing prose, and a judge caught it

**Severity: medium-high. This is an emergent gaming pressure, not a bug in any
one file.**

`shared/rubrics/foundation.md` instructs: *"MANDATORY: For EVERY dimension… you
must identify (a) the single biggest GAP… If you cannot find a gap, explain why
you believe one doesn't exist."* Combined with genre-contract and stability-trap
checks the plan is expected to pass, the rational move for the authoring agent
is to write the *defence* into the planning documents. I did this heavily and
without noticing until it was named back to me.

The iteration-3 judge flagged it unprompted, under `slop_in_planning_docs`:

> *"Rubric-facing self-defence rather than material: a substantial fraction of
> both characters.md and outline.md consists of parenthetical arguments
> addressed to an evaluator rather than to a drafter — '(YA contract: the
> teenager causes the ending)', 'the form contract requires it', 'which
> single_effect would rightly punish'… **it inflates apparent completeness:
> several apparent gaps are closed by an argument that a gap does not exist
> rather than by supplying the missing material, and the forgery-mechanics hole
> survived precisely because it was never argued about.**"*

That last clause is the real damage and it verified: the forgery mechanics were
the one place a drafter was genuinely blocked, and they survived four iterations
*because* the surrounding prose was busy defending choices that were already
fine. The judge scored 8s on documents with a hole in the climax.

**Proposed fix.** Two lines, in two files.

In `layer-guides.md`, at the top: *"These documents address the drafting agent,
not the evaluator. Do not include arguments about why a choice satisfies a
rubric, a contract, or this guide. If a choice needs defending, the defence
belongs in the commit message."*

In `rubrics/foundation.md`, under CROSS-CHECKS: *"Discount prose addressed to
you rather than to a writer. A plan that argues a gap does not exist has not
closed it; check the material instead, and note the argument under
`slop_in_planning_docs`."*

---

## 7. `internal_consistency`'s cap treats surface and structural faults identically

**Severity: medium.**

`base-dimensions.md` sets it as: *"A single major contradiction caps this at 6.
Three or more caps at 4."* Nothing grades severity, so the count is what binds.

At iteration 3 the cap fired at 4 on this set: a letter rendered ALL CAPS in one
file and mixed case in another; a "seven blocks" line that should have said
three; "two light-decades" where the geometry says thirty-nine; and Mele's
position given as the destination distance. Two were in load-bearing text and
two were in authorial commentary. All four were single-line edits. Meanwhile the
iteration-1 clock contradiction — *stated three times, and the pressure the
entire second half runs on* — counted exactly the same as the typography.

The judges felt the strain and said so. Iteration 3: *"Two of the four are in
load-bearing text… two are in authorial commentary. The cap is applied, not
weighed."* Iteration 6, on a comparable set: *"No single contradiction rises to
major… the other two are wording"* — and scored 8 by declining to count them the
same way. Same rule, opposite handling, because the rule gives no severity axis.

**Proposed fix.** Grade the count in `base-dimensions.md`:

```
- internal_consistency [cap 4] — … Count only contradictions in text a
  writer must not violate: the fact tables, the outline's beats, quoted
  in-story text, and character facts. A disagreement confined to authorial
  commentary is a note, not a contradiction. One major (a contradiction the
  plot depends on) caps at 6; three or more major caps at 4.
```

That also removes the incentive to under-report, which iteration 6 arguably
acted on.

---

## 8. Judge-supplied `fix` strings are sometimes wrong, and the skill implies applying them

**Severity: medium.**

Step 3 says target the weakest dimension; the eval supplies `fix` per dimension
and `top_3_improvements`. Nothing says these are hypotheses.

Iteration 1's `novum_specificity.fix` read: *"State the window's opening time,
its duration… (e.g. window 02:41–06:50; telemetry occupies the first ~80 minutes
of an unusually short block because the null aft-string stream compresses to
nothing…)"*. The same judge's `register_plausibility` gap had just correctly
demolished the aft-string explanation as *"a rule invented to escape the corner
the plot is in"* — and the suggested 02:41–06:50 window contradicts the
ten-hour window it was also complaining about. Applying that fix verbatim would
have preserved the fault it diagnosed.

The judge is scoring one document with no drafting context, which is what makes
its *diagnosis* worth having and its *prescription* unreliable — it cannot see
what else the fix breaks.

**Proposed fix.** One sentence in step 3: *"The eval's `fix` strings are
hypotheses from an agent that has seen one document and no other constraint.
Take the diagnosis; design the fix yourself, and check it against the facts
table before writing it."*

---

## 9. Cost is disproportionate at compressed band, and the form lowers the gate but not the budget

**Severity: medium.**

Six evals: **717k subagent tokens, 46.5 minutes of eval wall time** (avg 119k
tokens / 7.8 min each), plus the authoring passes, to plan **5,000 words**.

The form pack argues the opposite case in its own voice, and I think it is
right:

> *"a weak plan costs the drafting loop far more than it costs to plan again —
> true across eighty thousand words, false across five, where the drafting loop
> is cheap enough to absorb the error and the plan cannot be much righter than
> the story."*

So `short-story.md` lowers `gate` from 7.5/7.0 to 6.5/6.0 — and leaves the
iteration cap at the universal 15. The reasoning that justifies the lower gate
justifies a lower ceiling too, and nothing carries it there.

Worth noting against myself: the run *did* keep improving (7.45 → 8.14), so the
iterations bought something. But the top three findings at exit were all
polish-grade, and iterations 5 and 6 together moved the mean 0.10.

**Proposed fix.** Add `iteration_cap` to the form frontmatter — `short-story: 4`,
`novella: 8`, `novel: 15` — and have step 5 read it rather than hard-coding 15.
Combined with finding 1's cap-based exit condition, that produces the right
shape: *iterate until nothing is capped and nothing contradicts, then stop
early at short lengths rather than grinding the mean.*

---

## 10. Seed arithmetic is inherited unchecked, and foundation amplifies it

**Severity: medium.**

`seed.txt` here was unusually rigorous — I verified γ, D, D², D⁴, the arrival
dates, the wavelength shift, the character budget and every age against it
before writing a line, and all of it held. It still contained one genuine
internal ambiguity: "300 characters each, per year" and "one transmission window
per year" cannot both be true alongside letters indexed by ship-year arriving at
D·τ, because consecutive ship-years land ~9.95 Earth-years apart. The seed
conflates a per-ship-year allowance with an annual Earth window.

That took **two iterations to surface** (the iteration-2 judge caught it and
called it MAJOR) and the fix rippled through all three documents plus the
clock, the queue sizes and two characters' dialogue. Resolving it improved the
story — annual windows with decadal deliveries is a harder institution than the
seed's version — but it was expensive to find that late, and Setup had already
read the seed in full without anything asking it to check the numbers.

**Proposed fix.** Add to Setup step 3, after the required reading: *"If the seed
states quantities the story's premise depends on, verify them against each other
before building any layer, and write the resolved set into the outline's fact
table as the single source. A seed's arithmetic is an input, not an authority —
foundation inherits its errors and multiplies them across three documents."*

---

## 11. Nothing requires the plan to contain text the story quotes verbatim

**Severity: medium. Cheapest high-value change in this document.**

The single most useful thing I did in this phase was write the story's central
object — a 1,200-character letter, the exact artifact the climax delivers aloud
— out in full inside `characters.md`, at exactly the length the plan's own byte
budget allows. No guide asked for it. I did it because *"she reads a warm, thin
letter"* is a gap where the climax should be.

It paid repeatedly and in ways I did not anticipate:

- Every judge could measure the letter's insufficiency instead of taking the
  plan's word for it. Iteration 6 called the decision to quote it uncut *"the
  strongest single structural choice in the file — it makes the condition
  measurable by the reader instead of asserted."*
- It made a whole class of contradiction findable. Two separate evals caught the
  letter contradicting itself or its own frame size, which is only possible
  because the text existed to be checked.
- It forced the arithmetic honest: the letter is 1,200 characters because the
  allowance is four banked years at 300, and I had to make those agree to the
  character.

**Proposed fix.** In `layer-guides.md`, under `outline.md part 1` constraints:

> *Any text the story quotes verbatim — a letter, a prophecy, a contract, a
> transmission, a will, a song — must exist in full in the plan, at the length
> the world's own rules permit. A plan that describes such an object instead of
> containing it has left the scene it appears in unplanned, and no judge can
> check whether the object does what the outline claims it does.*

---

## 12. Small things

**`results.tsv`'s `words` column is dead in foundation.** The append template
hard-codes it: `<score>\t0\t<keep|discard|noscore>`. Six rows of `0`. Either
drop it for this phase or put something in it — the plan's total planned word
count would actually be useful for spotting a plan drifting off `target_words`.

**`iteration` is overloaded.** Step 4 uses it as the resume cursor
(*"this is what makes the run resumable — the router reads `iteration`"*), and
Exit sets it to `0`. Both are right for their purpose but the field means two
things. A separate `foundation_iterations_used` would preserve the run's history,
which is otherwise only in `results.tsv`.

**`score_verdict.py` agreed with the judge 6 times out of 6.** The warned
failure mode (*"a live cycle returned dimensions averaging 7.43 alongside
`work_score: 7`"*) did not reproduce once. Keep the check — it's ~1 second and
the failure is silent — but the instruction's alarm may be overcalibrated for
this rubric, whose JSON asks for two-decimal means explicitly.

**The `genre-change` marker contract is intact.** I went looking for a dangling
reference and did not find one: `skills/status/SKILL.md:53` writes the row that
`skills/foundation/SKILL.md:136` reads. Noting it so a future session doesn't
re-audit it.

---

## What worked, and should not be touched

- **`[cap N]` as "applied, not weighed."** The rubric's paragraph defending this
  against "every other test passes strongly" is the most load-carrying prose in
  the whole rubric set, and it held every time. Iteration 2's judge scored
  `register_plausibility` 6 while writing *"Score on merits absent this would be
  9"* — exactly the refusal the mechanism exists to make. Finding 7 asks for
  severity grading *inside* one cap, not for softening the mechanism.

- **Form-selectable base dimensions.** `base_dimensions.scored` passed verbatim
  through the dispatch worked exactly as designed. No judge restored
  `foreshadowing_balance` or `canon_coverage`, and none penalized the absence of
  `world.md` or `canon.md`. The rubric's instruction — *"an absence here is a
  decision the form made"* — is doing real work.

- **`## At Compressed Length` in the genre pack.** Three pillar dimensions
  instead of five, with the two novel-scale instruments named and dropped. Every
  judge scored the right three without prompting.

- **The five-register voice trial.** The guide asks for five trial passages and a
  selection; what made it valuable was keeping the four rejected registers *as
  the anti-exemplars*. Two judges independently called the anti-exemplar section
  the strongest element in any of the three documents. Worth promoting from an
  emergent move to an instruction: `layer-guides.md`'s voice-discovery section
  should say the rejected trials become the anti-exemplars, each with the reason
  it lost.

- **The clean-room judge.** Six dispatches with no drafting context produced six
  genuinely independent reads, caught faults I had looked straight through four
  times, and never once flattered the work. The noise in finding 3 is a reason to
  aggregate them, not to give them context.
