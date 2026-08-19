# Changelog

Versions are the plugin's, declared in `plugin/autoauthor/.claude-plugin/plugin.json`
and mirrored in `.claude-plugin/marketplace.json`. Updating the marketplace
is not the same as updating the plugin — see [README](README.md#install).

Dated entries with no version number changed nothing under
`plugin/autoauthor/`, so there is nothing to install. They are here because
the reason a thing was *not* changed is worth the same record as a change.

---

## 0.19.0 — 2026-08-19

Models are chosen per step instead of inherited from whatever the session
happens to be on.

**Three plugin agents** under `plugin/autoauthor/agents/`: `judge` (Opus;
Read, Glob, Grep, Write) for every scored rubric — foundation, chapter,
full-novel, manuscript-review, collection, series; `editor` (Sonnet) for
adversarial cuts and the chapter tournament; `reader` (Sonnet) for the four
panel personas. The cheaper two carry only work the pipeline already
verifies or gates: cuts pass through `--protect-file`, the dialogue filter
and `splice_audit.py`; panel verdicts are checked against the prose in Fix
step 1. Every dispatch in the skills names one of the three; none says
`general-purpose` any more, and `test_agents.py` keeps it that way.

**Every skill pins its orchestrator model** in `SKILL.md` frontmatter:
`foundation` and `draft` on `claude-fable-5` (the plan that gates the run
and the prose that ships), `seed`, `revise`, `review`, `import`,
`collection`, `series` on `opus`, `export` on `sonnet`, `status` on `haiku`
with `effort: low`. If the named model is not available to the session the
session keeps its own — the frontmatter is a preference, not a hard failure.

**The judge model is recorded.** Every scored dispatch tells the judge to
write `judge_model` into its JSON (the rubric schemas carry the field), and
the draft, foundation and full-eval rows in `results.tsv` end in
`judge=<model>`. A score history that spans a model change now says so; the
pin is what makes the history comparable, and the field is what lets you
see when it was not.

The `review` skill's "request the strongest model if the Agent tool exposes
a choice" is gone — the agent definition is the choice. 520 → 547 tests.

---

## 2026-08-19 — the README's attribution was wrong, and is corrected

Nothing under `plugin/autoauthor/` changed. The 0.12.0 entry below said
"no upstream content remains here" and the README's *Origin and licensing*
section repeated it in bold. `git blame -C -C -C` against the root commit
says otherwise: `gen_brief.py` (525 of 918 lines), `CRAFT.md` (260 of 359),
`ANTI-SLOP.md` (237 of 378), `apply_cuts.py` (199 of 380), `slop_score.py`
(172 of 469, descended from upstream's `evaluate.py`), the typeset kit, the
`voice.md` template, `voice_fingerprint.py` and `ANTI-PATTERNS.md` are all
still substantially upstream's text, moved into `plugin/` on 2026-08-05 and
revised in place. What 0.4.1 and 0.12.0 removed was the standalone tooling
and the specification document, not the working files.

The README now carries the table and says the debt is literal as well as
architectural. The 0.12.0 entry is left as written; this entry is the
correction. The licence position is unchanged — upstream has none, so none
is granted — and it now names the files it bears on.

---

## 2026-08-19 — marketplace renamed `autoauthor-dev` → `autoauthor`

Nothing under `plugin/autoauthor/` changed, so there is nothing to install.
The marketplace's `name` in `.claude-plugin/marketplace.json` drops the
`-dev` suffix it carried from the prototype; the install command is now
`/plugin install autoauthor@autoauthor`. The name is the key an installed
plugin is recorded under, so a machine that added the marketplace as
`autoauthor-dev` should `/plugin marketplace remove autoauthor-dev`, re-add
`abnormalend/autoauthor`, and reinstall.

---

## 0.18.0 — 2026-08-17

The findings from one full foundation → draft → revise run on a
short-story project, filed under `docs/superpowers/specs/2026-08-17-*` and
acted on by the plan beside them. Six parts, each shippable alone.

**Baselines and keep/discard.** Revise baselines every chapter it will
touch at the start of Fix, in parallel, and trusts only a same-cycle number
— identical text drifted 0.67 between two revision cycles' judges, and a
rewrite that beat its true baseline by 0.56 was one command from discard.
Foundation gets a ±0.15 tie band, checks whether the targeted fault cleared
before discarding a regression, treats a fired cap as overriding a cleared
gate, and reads the judge's `fix` strings as hypotheses.

**Judges write their own verdicts.** Every scored dispatch names an
absolute output path; the judge writes it and returns the path and score.
`score_verdict.py` was certifying the orchestrator's transcription. The
rubrics' OUTPUT lines and file lists agree, and a judge may no longer infer
that a file it was not shown does not exist.

**Form-aware drafting.** Draft builds its input-file list from
`form.layers`, scaffolds `canon.md` at compressed forms, loads the outline's
preamble (fact table, clock) with every chapter, and reconciles `state.json`
against `git log` before inferring a resume point. Six drafting rules that
named `world.md` name the fact-bearing layer by role; a test keeps them so.

**A facts checker and a canon gate.** `continuity_check.py` lists every
clock time and number a chapter states and whether any fact-bearing document
states it too. Draft runs it beside the slop score, keeps only chapters
whose `canon_compliance.violations` is empty (or ≥ 7), and gains a
surgical-correction branch that is not a discard. The outline template
carries `## Facts the story must not contradict`; foundation checks the
seed's arithmetic into it and requires any text the story quotes verbatim
to exist in full in the plan.

**Cutting protection.** `apply_cuts.py --protect-file`; `splice_audit.py`
with the four checks the prose list missed; revise builds
`edit_logs/protected.md` from prior judges' strongest sentences and the
ledger's carrying sentences before any mechanical pass, archives the prior
cycle's cuts JSON before re-dispatching, gates the cuts pass by chapter
after cycle 1, and carries prior-cycle skips into Fix.

**Ratios, not novel literals.** The 1800-word floor is 0.5 ×
`shape.chapter_words`; `gen_brief.py --chapter-words` clamps to it;
layer-guides' thread, quiet-unit, character-doc and canon counts scale with
the resolved shape; forms declare `iteration_cap` (novel 15, novella 8,
short story 4); the full-novel judge honours the band section.

**Rubric prose.** `internal_consistency` caps on major contradictions in
binding text; the foundation judge discounts prose addressed to it; an
`## Author-facing only (never on the page)` section in the outline and
character templates that every judge treats as withheld by design.

Not done, and why: triple-judge median (trebles a cost the same findings
complain about); a suppression list for the layer guide (ratios do it);
cumulative voice budgets in `slop_score.py` (needs a `voice_budgets.json`
contract from foundation — its own plan). 461 → 520 tests.

---

## 0.17.1 — 2026-08-15

A chapter that opens on dialogue got a backtick for a drop cap.

`make_drop_cap` took the first character of the first paragraph and wrapped
it in a `lettrine`. After `md_to_latex`, a paragraph opening with speech
starts with a LaTeX open quote, so the first character is a grave accent —
and the second one was swallowed into the lettrine's second argument:

```
narration  ->  \lettrine[...]{W}{ren} was awake before the bell.
dialogue   ->  \lettrine[...]{`}{`Pick} them up,'' she said,
```

Two lines tall, at the head of the chapter, in the PDF. `time-squatting`
ch_03 opens on dialogue, so this was reachable by a book already on disk.

The fix strips the quote before choosing the letter and sets it back through
lettrine's own `ante` option, which is what that option is for — the mark
hangs ahead of the capital instead of becoming it.

```
dialogue   ->  \lettrine[..., ante=``]{P}{ick} them up,'' she said,
```

**Where it had been.** Written on 2026-08-05 with its test, left uncommitted
in a git worktree under `.claude/worktrees/`, and found ten days later while
auditing the repo for stray directories. The worktree predates the rename —
it still had `plugin/autonovel/` and the `gen_*.py` tools 0.4.1 removed — so
nothing about it looked like current work, and `git status` on master never
mentioned it.

**Why a live run did not catch it.** `export` *has* been run against a real
book: `small-hours/01-porter` produced a PDF and an ePub on 2026-08-14. It
emitted four lettrines and every one was correct —

```
{T}{here}   {T}{he}   {T}{hey}   {H}{e}
```

— because all four chapters open on narration. The surface was exercised;
this branch of it was not. That is the more useful lesson than "untested
code": a stage can be driven end to end by a real book and still leave a
common path cold, and the only thing that would have caught this is a
chapter that happens to start with someone speaking.

---

## Caps bind — 2026-08-15

**Caps bind. Fourteen clean-room judges, and no plugin change.**

The deepest finding of the 0.3.1 shakedown was that `score 6 max` was
advisory prose a judge could weigh against passing tests, and that whether it
bound varied by judge. 0.5.0 answered it at the rubric layer with declared
`[cap N]` plus one sentence establishing that a met cap condition is a cap
**applied**, not a factor weighed. Only a judge could show that landed.

`internal_consistency`'s cap fired in **every run** — nine of nine on
romantasy, both on dark-romance, three of three on the repaired fixture — and
the judges wrote the refusal out themselves:

> Cap applied, not weighed: three or more contradictions caps this dimension
> at 4. The quality of the surrounding documents does not lift it.

Several named the on-merits score — 6, 8, "would otherwise have scored high"
— and applied the cap anyway.

**A finding filed on three judges was withdrawn on nine.** The first three
split 9/8/6 on the planted dimension, which read as a new defect: variance
moving from whether a cap binds to whether its condition is met. Six more
judges put the capping rate at 1 in 9, with eight independently concluding
the redenomination test passes. n=3 was too few to file from, and six judges
cost less than the feature that finding would have justified.

The two planting sets are now committed under `tests/fixtures/shakedown/`.
Their loss is what blocked this item for a day and cost two sets' worth of
regeneration.

**One real hole, closed.** A single judge found that Halim's ch 17 offer of a
marriage in name only dissolved the fixture's barrier at 37%. It now carries
an alienation clause the world already implied — the pledged security is a
*line*, so issue entered outside the merged estate voids for cause, and
nobody in the book can waive what is pledged forward. Three fresh judges
raised nothing.

**Added `test_fixture_ledgers.py`.** A ledger row may not cite a chapter that
does not carry the plant. Fixing that class rather than the three instances
judges found turned up a fourth that all fourteen had missed. Mutation-tested
both ways.

A judge also flagged the fixture for using `load-bearing`, naming it as a
phrase the plugin bans — 0.16.0 arriving through the judge channel rather
than the required-reading one, since the romantasy author never read
`ANTI-SLOP.md` and the dark-romance author did.

Full result in
[`docs/superpowers/2026-08-14-caps-bind-verification.md`](docs/superpowers/2026-08-14-caps-bind-verification.md).

Nothing under `plugin/autoauthor/` changed, so the shipped content is
byte-identical to 0.17.0 and no version moved.

---

## 0.17.0 — 2026-08-14

Literary device overuse, mechanical half and judged half.

Identified from a 0.2.0 draft that ran one figurative construction every 83
words. Individually most were good; collectively they were the narrator's
tic, and nothing stood out because everything was reaching.

**`figurative_density` in `slop_score.py`**, per 1000 words of *narration*.
Dialogue is excluded before counting — a distinctive speaker's similes
characterise the speaker and should differ from the narration's, and scoring
them would penalise a book for having a vivid character in it.

**Calibrated, not guessed.** 36 chapters across four projects: median 2.9,
and the chapter this feature was specced from is the corpus maximum at 7.3.
Four chapters trip the threshold, all from the project the fault was found
in, and the motivating chapter takes the largest penalty of the four.

**The threshold varies by form**, read from the band via `--form-pack`, and a
genre pack can override it with a `FIGURATIVE DENSITY:` line — the same
forgiving shape as `BANNED PHRASES:` — because literary fiction carries
figures a thriller cannot. `draft` and `collection` now pass both packs on
every invocation; without them the scan silently used the general lists and
the novel-length threshold.

**Two parts of the spec did not survive the data.**

*The repeated-construction penalty is not shipped.* The roadmap expected
monoculture to score worse than the same count spread across varied figures.
Measured, it inverts: the motivating chapter repeats its commonest
construction 53% of the time against a corpus median of 83% — it is *more*
varied than typical. Penalising repetition would have hit the wrong
chapters. Volume is what distinguishes it, so volume is what is scored. The
breakdown is still reported, just not scored.

*A five-figure floor was added*, and the existing clean fixture is what
found it: one figure in an 89-word passage computes to 11.6 per 1000 and
means nothing. A tic requires repetition — you cannot have a monoculture of
one. The fixture failing was the test suite doing its job on a feature added
years after it was written.

**The judged half** carries what a regex cannot. `ANTI-SLOP.md` gains a
figurative monoculture section built on the operative test — **delete the
figure; if the sentence loses nothing, it was ornament** — and
`prose_quality` in the chapter rubric now judges the collective rather than
the individual figure, capping at 6 when more than a third are detachable.

Neither half is "use fewer similes". The same draft earned its figures where
they carried the book's argument. A figure tied to the subject earns its
place; a figure generated to make a sentence interesting does not.

Known limit, stated in the code: this measures the simile family. Metaphor
cannot be regexed, and a hand count of 31 on the motivating chapter is 16
here — a proxy for roughly half the true load. Only the `extended` threshold
is corpus-grounded; no short-form chapters exist to measure yet.

---

## 0.16.1 — 2026-08-14

Audited the rest of the required reading for the same defect, using the
plugin's own lists against the plugin's own prose.

**One more real hit**, and a pointed one. `shared/rubrics/chapter.md` asked
whether the dialogue sounded machine-made using *"not just the right thing,
but a REAL thing"* — the construction `ANTI-PATTERNS.md` §10 names as the AI
dialogue formula, and `ANTI-SLOP.md` calls the single most overused pattern
in LLM output. The check now asks whether every line lands exactly where the
scene needs it, which is the same question without the tell.

**Everything else was a false positive**, which is worth recording. 34 hits,
33 of them fine: `leverage` 19 times, always the noun the coercive-romance
packs need (*"the antagonist's leverage"*, *"Leverage Acquired"*) — the ban
is on the verb; `Catalyst` 14 times, the Save the Cat beat name sitting
beside Opening Image and Adhesion; `tapestry` inside a quoted ban;
`profound` inside a sentence describing the awed-narrator failure.

**Added `test_required_reading_is_clean.py`** — 68 checks. Deliberately
narrow: only the multi-word Tier 1 phrases and the structural formulas, the
two lists that came back with no false positives. Pinning the full tier
lists would fail on `Catalyst` and `leverage`, and a guard that cries wolf
gets muted. The three files that quote the bans are exempt per-file, not
per-directory, so every pack and rubric beside them stays strict.

---

## 0.16.0 — 2026-08-14

`load-bearing` is a tell, and the plugin was teaching it.

Most of the Tier 1 list is corpus-derived — words measured as
overrepresented across every model. This one is not. It is a Claude tell,
noticed in use, and it earns Tier 1 anyway: a phrase that identifies the
model that wrote it is precisely what the anti-slop reference exists to
catch.

**Banned in all three places a ban has to exist.** `ANTI-SLOP.md` Tier 1,
the `voice.md` guardrail table every project gets its own copy of, and
`slop_score.py`, which is the only one of the three that can fail a
chapter rather than advise it.

**Added `TIER1_PHRASES` to the scorer.** Tier 1 matched exact tokens, so it
could never see a phrase — `bears the load` was unreachable by
construction. The new list is regex, scored in the same bucket at the same
weight, because a phrase is not a lesser offence than a word, only a harder
match.

The hyphen is required. `load bearing` unhyphenated is not reliably the
metaphor — *the load bearing down on her* is a sentence a person writes,
and a scorer that penalises it trains the drafter away from real prose to
catch a tell that isn't there. The pattern tolerates a line break on the
hyphen instead, which is exactly where a hard wrap prefers to land.

**Swept the plugin's own prose — 22 sites.** `foundation/SKILL.md` requires
reading `ANTI-SLOP.md` *and* every genre pack, so the packs were putting the
banned phrase in front of the drafter 22 times in the same context as the
instruction to kill it on sight. That is priming, not inconsistency, and it
is why a ban nobody in the required reading follows does not hold.

Two occurrences deliberately survive. `darkness_load_bearing` is a scoring
dimension key in `dark-romance`, and renaming it would make every existing
dark-romance project's scores incomparable with its own history — the cost
of a clean identifier is not worth a broken record. Two source comments in
`base_dimensions.py` and `genre_pack.py` are also left: no drafting agent
reads them, and the phrase is literal there.

---

## 0.15.0 — 2026-08-14

A title has somewhere to live.

Export asked for one, which is the last thing anybody expected it to be
confused about — and the reason turned out to be that it had nothing to
read. The story named itself during foundation, wrote that name into the
headers of `outline.md` and `canon.md` as decoration, and `state.json` had
no field for it. Export was documented to source the title from "outline.md's
first heading (confirm with the user)": prose, parsed, every time.

**Added: `title` in `state.json`**, beside `genre`, `form` and `structure`
— the facts about the work that are not the work.

- `seed` records the title it already names in its own commit message.
- `foundation` records it the moment the work acquires one, which is
  usually while the outline is being built.
- `export` reads it and asks only when it is null — and **writes back what
  it is told**, because a title asked for and not recorded is a title
  asked for again and answered differently.

**The failure this was heading for** is quieter than a prompt.
`assemble.py` reads a work's title for its half-title in a bound
collection, falling back to the directory name. A collection whose works
never recorded their titles would have bound "The Warm Key" under a
half-title reading **Porter** — silently, in a PDF that builds without
complaint. The fallback stays, because the bind should never fail; it is
now documented as a fallback rather than the path.

---

## 0.14.2 — 2026-08-14

Records why the critic rates out of five, so nobody standardizes it away.

Six rubrics score 0-10 and `manuscript-review.md` rates out of five, which
makes the odd one out look like an oversight. It is not. The critic writes
a newspaper book review, and stars are what those use — the persona is the
instrument, and it catches what the dimension rubrics do not precisely
because it is writing a review rather than filling in a form. Rating out
of ten would make it a rubric wearing a critic's hat.

Nothing is lost by keeping it: half-star increments give eleven values,
which is the granularity of 0-10 integers exactly, so the doubling at the
recording boundary is lossless in both directions. And the stars are not
the gate — the phase stops on item counts.

The rubric now says all of that where a tidying edit would happen, and a
test pins it as the only non-10 scale.

---

## 0.14.1 — 2026-08-14

The first story reached `export`. Foundation, drafting, two revision
cycles and three review rounds, end to end, in a work inside a container.
One defect, found by reading `results.tsv` rather than by anything
failing.

**`results.tsv` had two scales in one column.** Every phase writes a 0-10
score there. The review phase wrote the critic's star rating, out of five.
The run reads:

    foundation 8.25 → drafting 7.0 → revision 7.43 → review 4.0 → 4.5

which looks like a book falling apart in review. It is the opposite: 4.5
stars is 9.0, the best number in the sequence. Review now doubles the
rating for the column and keeps the raw figure in the description, where
it carries its own units. `tests/test_results_tsv.py` parses the row
format every skill documents and fails any phase writing a rating on a
different scale.

The reader this was hurting is `status`, which reports "scores against
their gates" straight out of that file.

---

## 0.14.0 — 2026-08-14

Stop asking the judge to do arithmetic.

Two releases went into getting a judge to report a mean correctly — first
by adding the instruction, then by moving it into the JSON schema where a
judge copies tokens rather than reads paragraphs. The second worked. But
the aggregate every rubric asks for **is the mean of the dimensions**,
which is arithmetic, and a judge is qualified to score a dimension without
having any particular claim to averaging seven of them.

**Added: `score_verdict.py`**

Takes an eval JSON, averages the dimension scores, and compares that to
the aggregate the judge reported. Handles both verdict shapes — flat, and
foundation's categories, where it takes the weighted mean of the category
means and renormalizes if a form has emptied one. Exit 1 on a
disagreement, naming the value to record.

`foundation`, `draft` and `revise` now run it after saving a verdict and
record the computed number.

Run against the live project's history it reproduces the whole story: all
five foundation verdicts agree exactly, and the one full-novel cycle that
predates the schema fix disagrees by 0.43 — dimensions averaging 7.43
against a reported 7, in a phase that stops when that number moves less
than 0.5.

**Confirmed from the run**

The schema fix works: revision cycle 2 reported `work_score: 7.43`,
matching its dimensions exactly. And the two cycles are the clearest
plateau this project has produced — identical means, with
`arc_completion` and `pillar_consistency` up a point each while
`foreshadowing_resolution` and `voice_consistency` went down a point each.
Real work, no movement. Which is what `revise` already tells its operator
to look for: *read the dimension scores, not just the total.*

---

## 0.13.2 — 2026-08-14

0.13.1 fixed the wrong half of the problem, and the next run proved it.

The full-novel judge ran AFTER that release, read a `full-novel.md` that
closed with a paragraph demanding a two-decimal `work_score`, and returned
`"work_score": 7` for dimensions averaging 7.43. The instruction was
present, in the file, and ignored.

`foundation.md` had been getting decimals all along, and the difference is
placement: its rule sits mid-file among other instructions rather than as
the last thing after the JSON schema. But the reliable fix is not better
placement — it is putting the type where the value is written. Every
schema now reads `"work_score": N.NN` rather than `"work_score": N`, with
a legend saying `N` is an integer and `N.NN` is a computed mean. A judge
filling a template copies the template's token; a paragraph after the
template is read and then not applied.

The test now requires the schema token, not just the paragraph.

**Why 0.43 matters.** Revision stops on a change of less than 0.5 across
two cycles. The gap between the reported 7 and the actual 7.43 is
comparable to the threshold itself — so the stop condition was being
evaluated against a number that had already discarded most of the signal
it needed.

---

## 0.13.1 — 2026-08-14

The first story drafted: four scenes, 4,769 words against a 5,000 target,
every scene clearing the 6.0 bar on its first attempt. One defect found by
reading the eval logs, and it is the more serious kind — silent, and it
degrades a gate.

**Fixed: a computed score reported as an integer**

Four chapters whose dimension scores genuinely differed — 7.22, 7.33, 7.22
and 7.00 by their own arithmetic — all reported `overall_score: 7.0`. Only
`foundation.md` carried the two-decimal instruction; 0.2.0 added it there
and nowhere else, and it reads in that changelog as a formatting nicety.
It is not.

`chapter.md` and `full-novel.md` now carry it, and the second is where
this actually bites. **Revision stops when the full-novel score changes by
less than 0.5 across two cycles** — a test that cannot function on
integers, because an integer cannot express a change smaller than 1. On
rounded scores that rule degenerates into "stop when two cycles round the
same way", which ends revision early on a book that was still improving
and late on one that was not. The same rubric already notes that
same-judge variance runs about ±0.5, so the noise and the rounding
quantum were the same size.

`tests/test_rubric_contract.py` now fails any rubric that emits an
aggregate `*_score` without saying how to format it. Per-dimension scores
stay integers; only the means are decimals.

**Documented rather than fixed**

The drafter wrote a `canon.md` for a form whose layers are voice,
characters and outline. That is correct behaviour and the form now says
so: `layers` is what FOUNDATION builds. Facts established on the page have
to be recorded somewhere, and in a collection the shared bible is fed from
below — which is not the same as planning a canon in advance, and at five
thousand words the second is waste while the first is not.

---

## 0.13.0 — 2026-08-14

The first work in the first collection cleared foundation — 8.25 overall
against a 6.5 gate, 8.00 pillar against 6.0, in five iterations with two
discarded for regression. Everything below was learned from watching it.

**Verified in the wild, by five independent clean-room judges**

- **Judges score the dimensions they are handed, and only those.** All
  five scored exactly the eight the resolver reported — three pillar
  dimensions from `mystery`'s compressed band, two character, two
  structure, three craft — and not one reached for `canon_coverage`,
  `character_secrets`, `foreshadowing_balance`, `suspect_viability` or
  `solvability_curve`. That instruction landed in 0.7.0 and had never met
  a judge.
- **A form's ADDED base dimensions are real.** `single_effect` and
  `compression` were scored alongside the inherited ones. Nothing had ever
  produced one before.
- **The cap binds.** One iteration hit five contradictions and
  `internal_consistency` came back at 4 — its declared cap — with the
  judge writing: *"Cap applied, not weighed. On merits this would score
  around 6-7 ... but the criterion caps at 4 for three or more
  contradictions and the count is five."* That is the 0.5.0 sentence,
  quoted back by a judge that never saw the shakedown which found the
  defect. The loop then correctly discarded the iteration.
- **`clue_ledger.md` was produced and used.** The first genre artifact any
  run has ever created, and its criteria bit: two of the recorded debts
  are ledger-versus-prose disagreements the ledger won.

**Fixed**

- **A work owns its own `results.tsv` and `eval_logs/`.** The run put both
  at the container and tagged rows `[01-porter]`, which is coherent and is
  not what the rest of the architecture does — a work is an ordinary
  project, and a user who `cd`s into one and runs `/autoauthor:status`
  should find its history where every project keeps it. `seed` now
  scaffolds a work the same as a standalone project, and the container's
  `results.tsv` carries cross-work rows only, so the collection record is
  not fifteen foundation iterations deep in rows it did not write.

---

## 0.12.2 — 2026-08-14

Found by the first real container run, which is what a first real run is
for.

- **`seed` scaffolds only the layer files the form calls for.** A short
  story was given an empty `world.md`, an empty `canon.md` and an empty
  `MYSTERY.md` — three documents its form deliberately does not build, in
  a project whose `canon_coverage` dimension had been dropped for exactly
  that reason. `form_pack.LAYER_FILES` maps each layer to the file it
  produces, and `seed` copies that list and nothing else. `outline` and
  `foreshadowing` map to the same file, because the ledger is part two of
  the outline rather than a document of its own.

  Harmless in the sense that nothing reads those files, and not harmless
  in the sense that the foundation rubric now tells its judge not to go
  looking for a document it was not named — an empty five-line template
  sitting in the project is a thing to be marked down.

---

## 0.12.1 — 2026-08-14

Pre-flight fixes found by walking the container path before running it,
rather than by running it.

- **`bible/binding.md` is now required for a collection, and `seed`
  writes it.** The collection pass reads it — `binding_delivery` asks
  whether what unifies the works is delivered or merely declared — and
  nothing created it. A first real run would have reached the cross-work
  pass and found the file missing.
- The container gets `results.tsv`, `eval_logs/`, `edit_logs/` and a
  `.gitignore` at scaffold time. The cross-work pass writes to all four.
- Each container now requires exactly the document its own pass reads and
  nothing else: a collection has no arc to declare, a series has no slate.

---

## 0.12.0 — 2026-08-13

Containers become reachable. 0.10.0 and 0.11.0 built machinery that could
resolve, validate and judge a collection or a series, and neither could be
CREATED or SHIPPED — `seed` built a standalone project only and `export`
assembled one work. That gap is closed.

**Added**

- `assemble.py`. A container has no `chapters/` of its own, only
  `works/<name>/chapters/`, and export builds a book out of `chapters/`.
  This writes the one export expects: every work's chapters in the
  container's declared running order, renumbered gaplessly, each work
  opening with its own half-title. It exits **non-zero if any work
  contributed nothing**, because a bound book silently missing a story is
  the failure this path risks and it is invisible in the output — the PDF
  just builds.
- `seed` asks for the structure alongside genre and form, and scaffolds a
  container when one is chosen: `bible/`, `works/01-<slug>/`, and a
  container `state.json` whose `works` array is the running order. It
  settles the question before the directory exists for the same reason as
  the other two — the layout cannot be changed later without moving every
  file. It also asks rather than assuming when the user says "trilogy" or
  "collection", because those words are used loosely and the two
  containers check opposite things.
- `export` branches on `structure.assembles_as_one_book`. **A collection
  binds as one book; a series does not.** Each volume of a series is a
  book and exports on its own — binding them into one is an omnibus, which
  is a legitimate thing to want, is not this, and would need its own front
  matter and its own decisions.

**Removed**

- `PIPELINE.md`, upstream's own technical specification. It was the last
  file in this repository that someone else wrote, and it had stopped
  describing this program several releases earlier — it documents a Python
  script pipeline with a `lore_score`, against a plugin that now has genre
  packs, form packs, a structure axis and a computed gate.

  With it gone, **no upstream content remains here at all**, which is the
  cleanest possible position while upstream's repository still carries no
  licence. The attribution stays in the README, where it belongs: the
  scoring loop, the clean-room judge pattern and the phase structure all
  descend from that work, and the debt is architectural and real.

---

## 0.11.0 — 2026-08-13

Phase 6. `structure: series` — the same machine as a collection, pointed
the opposite way.

Both are a container, a shared bible, N child works, and one cross-work
phase. The cross-work check is the entire difference. A collection wants
**variety and independence**: no trick twice, every work standing alone. A
series wants **continuity and arc**: nothing contradicting what came
before, and each volume both advancing the whole and closing itself.

**Added**

- `structure: "series"`, reusing the container machinery unchanged. A
  series additionally requires `bible/canon.md` — what continuity is
  checked against — and `bible/arc.md` — what each volume owes the whole.
  A collection needs neither, and requiring an arc of one would make every
  collection declare a progression it does not have.
- `rubrics/series-pass.md` and the `series` skill. Seven dimensions:
  canon integrity, canon promotion, volume closure, arc progression, entry
  and recap, character continuity, series voice. `canon_integrity` carries
  the severest cap in either cross-work rubric — a contradicted
  load-bearing fact caps it at 4, because that is not a blemish, it is the
  series not being one series.
- `structure.order_is_editorial`. A collection's running order is a
  choice the cross-work pass may recommend changing; a series' order is a
  fact about the story, and reordering it is not a fix but a different
  series.
- The one inheritance rule, now stated where it is enforced: a volume may
  ADD to series canon and may never contradict it. Facts a later volume
  depends on get promoted up into the bible, because the next volume's
  author reads the bible and a fact that is not there is a fact that will
  be contradicted.

**Changed — convergence now says which way to read it**

`convergence.py` reports the same numbers for both structures and states
the interpretation, rather than leaving it to whoever opens the JSON. In a
collection a low coefficient of variation is the defect; in a series it is
the goal, and the signal worth acting on is the inverse — the volume that
reads unlike its neighbours. `divergent_works` computes those.

That outlier detection uses a **modified** z-score, on the median and the
median absolute deviation. The first version used an ordinary z-score and
could never have fired: an outlier inflates the standard deviation it is
being measured against, so with four works the largest z-score
arithmetically possible is 1.5, against a threshold of 2. The test that
pins this asserts the naive check would have found nothing.

---

## 0.10.0 — 2026-08-13

Phase 5, and the first of the structure axis. The pipeline can hold a
collection: N complete works, a shared bible, a running order, and the one
pass that sees all of them at once.

**The distinction this rests on.** Scale is a pack, because it changes
which dimensions apply. Structure is not, because it changes the state
schema and the phase graph — a collection has a work list, a directory per
work, and a cross-work phase before export, and none of that is
expressible as criteria. `structure` is a `state.json` field.

**Added**

- `structure: "collection"`. A container project holds `bible/` and
  `works/<name>/`, each child an ordinary project with its own state,
  phase and layers. Absent or null means `standalone`, so every existing
  project keeps working untouched.
- `structure.py`. Container discovery, child enumeration, and inheritance.
  A child takes `genre`, `genre_secondary`, `genre_modifiers` and `form`
  from its container and may not set them itself — those are what make N
  works one book. **The inheritance runs downward, inverting the pack
  precedent deliberately:** with packs the project copy wins because
  specificity is the point, and here the container wins because coherence
  is.
- `convergence.py`. The measurement no other judge in this pipeline can
  make. Every judge reads exactly one work with no memory of the others —
  that isolation is what makes their verdicts worth anything, and it is
  exactly what blinds them to N works written to one voice document
  drifting toward each other. This computes the coefficient of variation
  for each prose metric across the collection; high variance is healthy.
- `rubrics/collection-pass.md` and the `collection` skill. Seven
  dimensions — repetition, facet coverage, range, binding delivery,
  independence, running order, collection engagement — gated at 7.0. The
  pass does not re-grade prose: the revision phase already did that with
  the room to do it properly, and a finding here has to be a statement
  about the collection.

**Ported from `autoanthology`, with its corrections**

The cross-work pass is that fork's real contribution, and it arrives with
the lesson its first real run produced. Convergence metrics split into
STYLE and SCALE: `word_count` and everything downstream of it converge
because the works share a target length, which is now guaranteed rather
than likely since every work in a collection inherits one form. Reporting
those as convergence sends a judge hunting for prose repetition that is
not there — five of that run's seven flagged metrics were this, and only
one was something the rubric knew what to do with.

**The running order is declared, not derived**

`works` in the container's state.json IS the running order, and a
disagreement with what is on disk is refused rather than reconciled. A
work present but unlisted, a listed work that does not exist, or a
repeat — each stops the resolve. Directory prefixes like `01-` are a
naming convention; the opener and the closer do specific work and an
editor chooses them.

`autoanthology` is not retired yet. That waits until a collection has run
end to end.

---

## 0.9.0 — 2026-08-13

Length coverage for the rest of the pack set. Every genre pack now either
supports a shorter form or says in writing why it does not.

**Added**

| Pack | short story | novella |
|---|---|---|
| `general`, `fantasy`, `science-fiction`, `mystery`, `thriller`, `erotica` | yes | yes, via the compressed section |
| `romance` | yes | yes, its own intermediate section |
| `paranormal-romance` | no | yes |
| `dark-romance`, `romantasy`, `romantic-suspense` | no | no |

- Compressed sections for `thriller`, `romance` and `erotica` — three
  dimensions each, chosen by what the length can actually demonstrate. A
  short thriller is a clock and a person, so the antagonist's capability
  and the escalation ladder go. A short romance is two people and one
  barrier, so progression across chapters and both leads transforming go.
  Short erotica has one encounter, so variation across encounters and
  consequence past the last one go.
- An **intermediate section for `romance`** that drops nothing and rewrites
  three criteria. A band section is not only a way to remove dimensions:
  the novella is where category romance actually lives and it has room for
  the full curve, read at its own scale.
- An **intermediate-only section for `paranormal-romance`**. It needs a
  condition established, a bond tested and a reveal paid; five thousand
  words cannot hold all three without one becoming an assertion, and thirty
  thousand can. First pack to support a middle length and not a short one.

**Recorded, not fixed**

`dark-romance`, `romantasy` and `romantic-suspense` stay novel-only, and
each now carries a `## Lengths` section saying why — in the pack, where
the next person notices the gap, rather than only in the roadmap. All
three measure something over a book's duration: chapters that would need
rewriting, a power balance moving three times, four consecutive chapters
changing one strand of a braid. A compressed version would be scoring
something else under the same name. Each names the better alternative at
that length, which in every case is a different pack rather than this one
compressed. A test requires the explanation to exist and to be more than a
sentence.

---

## 0.8.0 — 2026-08-13

Phase 3, and the first phase that changes what the pipeline produces. It
writes short stories and novellas now, not only novels.

**Added**

- **`short-story`** (1,000–7,500 words) and **`novella`** (17,500–40,000),
  the SFWA boundaries, which is what markets and submission guidelines
  already assume. Each drops the base dimensions its length cannot earn and
  adds ones that bite at that length — `single_effect` and `compression`
  for the short story, `single_line` for the novella — and each gates
  lower, at 6.5/6.0 and 7.0/6.5. That is not a lower standard: the
  foundation bar is the highest in the pipeline because a weak plan costs
  the drafting loop more than it costs to plan again, and that reasoning is
  novel economics.
- **Length bands on genre packs.** A pack may declare `## At Compressed
  Length` or `## At Intermediate Length`, rewriting the criteria for the
  dimensions it names and taking others out with "not scored at this band".
  `general`, `fantasy`, `science-fiction` and `mystery` ship with
  compressed sections; the rest are novel-only for now and say so.
- **Band arithmetic.** Dropping a dimension shrinks the divisor
  `pillar_score` is a mean over, so a band is a different design with a
  different ceiling — five dimensions capped at 6 support a 7.1 gate, and
  the two that might survive a compressed band support 5.9, under the short
  story's own 6.0. The validator checks each band, the resolver checks the
  genre's band ceiling against the form's gate, and a test walks the full
  genre × form matrix. `gate_solver.py` now prints a row per band.

**Changed — this is the migration phase 1 deferred**

- `shape.words` is **keyed by band**: `{"extended": [80000, 95000]}`. Length
  is the form's to own, but a genre still has a length within a form — one
  pack runs 110,000–140,000 where another runs 65,000 — and collapsing them
  onto one form default would lose a real genre fact. A band a pack says
  nothing about takes the form's range.
- `shape.chapters` is **gone**, derived from the effective target over
  `chapter_words`, and declaring one is now an error. Several packs' chapter
  ranges only partially intersected their own word ranges — `mystery`
  spanned 70,400–83,200 against a declared 80,000–95,000, so most of its
  chapter range could not reach its own word floor. Deriving the count makes
  that unrepresentable rather than merely fixed.
- A form may override `chapter_words`. The genre owns chapter size at novel
  length, but a five-thousand-word story's unit is a scene, and dividing it
  by a 3,200-word chapter yields one chapter and a remainder.
- `seed` asks for the form alongside the genre, and settles both before the
  project directory exists — for the same reason the genre is settled there.
- `foundation` builds only the layers the form names and reads the form's
  `## Foundation Guidance` before layer-guides.md, which is written at novel
  scale.

**Refused, not degraded**

A genre pack with no length-scoped section cannot be used below novel
length. Falling back to its ordinary criteria would score a
five-thousand-word story on whether its world has "at least 3 societal
implications explored with specificity" — the exact defect this axis
exists to prevent, and one that would look like a bad story rather than a
bad pairing. The resolver names the pack, the band, and the two ways out.

---

## 0.7.0 — 2026-08-13

Phase 2 of the form work, and the largest of them: the base dimensions
stop being a fixed list written into the foundation rubric. No scoring
changes for a novel — the `novel` form drops nothing — but one long-standing
defect is fixed on the way out, and it affected a third of the pack set.

**Added**

- `shared/rubrics/base-dimensions.md`. The eight dimensions every work is
  scored on outside its genre, lifted out of `foundation.md` exactly as the
  pillar dimensions were lifted out before them, in the same
  `- key [cap N] — criteria` bullet form. Two caps that were already caps
  in prose are now declared: `internal_consistency` at 4, and
  `outline_completeness` at 4, which had been phrased inversely as
  "score 5+ only if".
- `base_dimensions.py`, which turns a form's `drop`/`add` into the list the
  judge is handed, and `foundation.md` now scores exactly that list. A
  short form drops what its length cannot earn — `foreshadowing_balance`
  scores a tracked ledger, `canon_coverage` assumes a canon file — and
  scoring those anyway penalizes a work for being correctly what it is.
- The resolver reports `base_dimensions.scored` by category and
  `base_dimensions.dropped`, so a dimension missing from a verdict is
  explicable rather than looking like a judge that forgot one.

**Fixed**

- **`outline_completeness` demanded act structure five packs do not use.**
  It scored "5+ only if act structure exists" while the sentence above it
  said to score against the beat system the pack actually names. `romance`,
  `paranormal-romance`, `dark-romance`, `romantasy` and `romantic-suspense`
  run on Romancing the Beat's four Parts or a braided threat/relationship
  ladder, so a literal judge capped a correctly built romance outline at 4
  for using the structure its own pack prescribes. The criteria now name
  the alternatives, and `templates/outline.md` no longer presents acts as
  the only architecture.

**Changed**

- `base_dimensions.add` on a form pack is keyed by category rather than
  being a flat list. A dimension in no category carries no weight and
  cannot reach `overall_score`. Criteria for an added dimension live in
  that form's own `## Base Dimensions` section — frontmatter says which
  category, prose says what it means, exactly as a genre pack works.
- Two more cross-pack checks in the resolver, both invisible to either
  validator alone: a form that empties a category the primary still
  weights, and a form whose added dimension collides with a name the genre
  already uses as a pillar dimension.
- `genre_pack.RESERVED_DIMENSIONS` is now a mirror of the new file rather
  than of the rubric, pinned by a test that fails if the two disagree.

---

## 0.6.0 — 2026-08-13

Phase 1 of the form work: the form pack type exists. Only `novel` ships,
carrying the values the pipeline already used, so **nothing moves** — that
is the phase's whole acceptance criterion and there is a test asserting
each of those values individually.

**Added**

- `shared/forms/`, a fourth pack type resolved alongside
  genre/secondary/modifiers. Same file format, parsed by the same code. A
  form declares the scale of one complete work: its `band`, its `words`
  range and `target_words`, the `gate` the foundation loop exits on, which
  `layers` get built, and which base dimensions the length drops or adds.
- `form_pack.py` and `validate_form_pack.py`, siblings of the genre pair
  and deliberately not folded into them — the two schemas share almost
  nothing, and a command that guessed which kind of pack it was reading
  would report a genre pack's missing `band` as an error.
- `state.json` gains `form`. Absent or null resolves to `novel`, under the
  same defaulting rule as `genre`, so no existing project needs migration.
- The resolver returns a `form` block, and `foundation` now reads its gate
  from there rather than from two numbers written into its own prose.

**Two checks that only exist once both packs are loaded**

Neither pack can catch either of these alone, which is why they live in
the resolver:

- A genre whose word range cannot fit inside the form's. The relation is
  **overlap, not containment** — a genre that runs past the form's ceiling
  is straddling a boundary rather than contradicting it, and containment
  would have rejected `romantasy`, which legitimately runs 110,000–140,000
  against a novel band topping out at 120,000. Overlap still catches the
  real error: a novel-scale genre under a short-story form.
- A form that gates the pillar above what the genre's caps can reach. The
  ceiling is the genre's and the gate is the form's, so this is invisible
  until they meet. It is the 0.5.0 solver doing work at resolve time.

**Deliberately deferred**

- The spec's migration of `shape.words` off the genre packs. Each pack's
  range is genuinely different — a cozy is not a romantasy — and
  collapsing fifteen of them into one form default would move behaviour in
  a phase whose contract is that nothing does. It lands with the
  compressed forms, where band-scoped overrides make it expressible.
- Deriving `chapters` from `target_words / chapter_words`, for the same
  reason.
- Renaming `resolve_genre.py` to `resolve_packs.py`. Cosmetic, touches
  nine skill files, and buys nothing this phase needs.

---

## 0.5.0 — 2026-08-13

Phase 0 of the form work. Score caps stop being prose and become data the
machine checks, which makes two things possible that were not: computing a
pack's gate instead of guessing it, and telling a judge that a cap binds.

Scoring behaviour changes for **general fiction** projects (a fifth pillar
dimension, and three caps raised from 5 to 6) and, in principle, for every
genre — a judge that previously weighed a met cap against a dimension's
other tests must now apply it. No schema or state changes; existing
projects need no migration.

**Added**

- `[cap N]` on a pillar dimension bullet: `- lore_interconnection [cap 6] —
  ...`. The value is the lowest tier the dimension's criteria can force.
  Fifty-five dimensions across eleven packs now declare one.
- `shared/scripts/gate_solver.py`. Given a dimension count and its caps it
  computes what the uncapped dimensions must average when the *k* lowest
  caps co-fire, and the highest gate the design can support. TEMPLATE has
  stated that policy in prose since the genre work and asked authors to
  check it by hand; this inverts it.
- The validator now rejects a primary pack whose own caps put the
  pipeline's 7.0 pillar gate out of reach — no book can be finished under
  such a pack however good it is. It also fails a `[cap N]` that disagrees
  with what the criteria say in words, since the judge reads one and the
  arithmetic reads the other.
- CI prints the gate ceiling for every shipped pack.

**Fixed**

- **`general` shipped unreachable.** Four dimensions with three caps at 5:
  two caps firing demanded 9.50 from the remaining two, and its highest
  legal gate was 6.4 against a pipeline gating at 7.0. Found by the solver
  on its first run, which is the argument for having built it. Fixed by
  TEMPLATE's own remedy — dimension count is the lever — with a fifth
  dimension, `cultural_particularity`, scoring the one World Section the
  pack demanded and never graded. The three 5-caps become 6s, which the
  arithmetic then forces and which also brings the pack in line with every
  other one in the set, where 6 is the severest ordinary cap.
- **Caps were advisory.** The 0.3.1 shakedown proved two judges meeting
  the same structure — three tests pass, one fails, criteria say "score 6
  max" — where one capped and one scored 8 because "every other test
  passes strongly". `rubrics/foundation.md` now states that a met cap is
  applied and not weighed, and says why: the criteria already decided what
  the other tests are worth by capping in spite of them. Fixed once at the
  rubric layer rather than pack by pack.

---

## CI — 2026-08-13

No version. `.github/workflows/ci.yml` runs the suite and the pack validator
CLI on every push and pull request.

The consistency checks live in `tests/test_plugin_manifest.py` rather than in
YAML, so they run locally too — version agreement across the three plugin
strings, and skill frontmatter matching its directory, which is the defect
0.4.0 shipped and a human caught. Both mutation-tested.

---

## 0.4.1 — 2026-08-13

No change to the plugin. This removes the last upstream-derived code from
the repository around it.

**Removed**

- `gen_art.py`, `gen_art_directions.py`, `gen_cover_composite.py`,
  `gen_cover_print.py` — the standalone image tools.
- `gen_audiobook.py`, `gen_audiobook_script.py`, `audiobook_voices.json`,
  `landing/` — removed just before this, for the same reason.
- `.env.example`, and both runtime dependencies (`httpx`, `python-dotenv`),
  which existed only for those tools.

None of them was ever called by the pipeline, covered by a test, or shipped
in the plugin. Each hardcoded the first book's title, byline or cast as a
**default** rather than as an example — an upstream defect
([#7](https://github.com/NousResearch/autonovel/issues/7),
[#9](https://github.com/NousResearch/autonovel/issues/9)) that had survived
into this tree because the genre-leak scrub was scoped to the plugin and
these sat outside it. They also carried upstream
[#5](https://github.com/NousResearch/autonovel/issues/5), fixed `max_tokens`
that breaks against a thinking model.

**Consequences**

- Everything that ships is now original to this project, which is the
  cleanest position for eventually going public while upstream's licensing
  is unresolved. The remaining debt is architectural — `PIPELINE.md` is
  upstream's own document, kept deliberately as the record of what this
  descends from.
- The repo has **no runtime dependencies**. The plugin's scripts were
  already stdlib-only by design, since they run inside Claude Code on
  whatever Python is present and a third-party import would fail silently
  on someone else's machine. `pyproject.toml` now says so.
- No API keys are needed for anything in this repository.

**Added**

- The De-Bells rule is finally executable. `tests/test_no_genre_leak.py` has
  described itself as that rule's successor since it was written while
  checking only for genre furniture — the content it was named after was
  never guarded. It now scans the whole repo rather than the plugin-scoped
  directories, because the leak's last hiding place was exactly the tooling
  those directories do not cover.

---

## 0.4.0 — 2026-08-13

**Renamed from autonovel to autoauthor.** Breaking: you must **reinstall**,
not update, because the marketplace id changed.

```bash
/plugin marketplace add abnormalend/autoauthor
```
```bash
/plugin install autoauthor@autoauthor-dev
```

The old plugin can be removed once the new one resolves. Existing novel
projects keep working — see Migration below.

**Why now.** The product is growing past novels: short stories, novellas,
collections and series are all specced. "autonovel" was already wrong on the
tin, and every skill named `novel-*` misdescribed itself. The rename was
scheduled as phase 4 of the form work and moved ahead of phases 0–3 because
everything those phases create — structured caps across fifteen packs, the
form pack type, band sections on every genre pack — would otherwise have
been born under the old name and needed rewriting afterward.

**Changed**

- Plugin `autonovel` → `autoauthor`; marketplace `autonovel-dev` →
  `autoauthor-dev`; plugin directory `plugin/autonovel/` →
  `plugin/autoauthor/`.
- All eight skills drop the redundant `novel-` prefix, and the router is
  named for what it does:

  | before | after |
  |---|---|
  | `/autonovel:novel` | `/autoauthor:status` |
  | `/autonovel:novel-seed` | `/autoauthor:seed` |
  | `/autonovel:novel-import` | `/autoauthor:import` |
  | `/autonovel:novel-foundation` | `/autoauthor:foundation` |
  | `/autonovel:novel-draft` | `/autoauthor:draft` |
  | `/autonovel:novel-revise` | `/autoauthor:revise` |
  | `/autonovel:novel-review` | `/autoauthor:review` |
  | `/autonovel:novel-export` | `/autoauthor:export` |

- `state.json`: `novel_score` → `work_score`.

**Migration.** One key. Run `/autoauthor:status` inside any existing
project — it detects a `novel_score` key, renames it to `work_score`, and
tells you what changed without committing. This check is independent of the
0.2.0 genre migration and fires on its own, since a 0.3.x project already
has a `genre` and still carries the old key. Nothing else in a project
directory carries the old name: chapters, `results.tsv`, `canon.md`,
`outline.md` and the rest are all name-agnostic.

**Not changed.** The dated design record under `docs/superpowers/` was
deliberately left under the old names, for the same reason `PIPELINE.md`
still records `lore_score` — a design document edited to match later
decisions stops being evidence of what was decided. See
[docs/superpowers/README.md](docs/superpowers/README.md) for a translation
table.

**Attribution.** The README now credits the upstream project this began
from — autonovel by emozilla / Jeffrey Quesnelle at Nous Research — and
records the licensing position. Note that "autonovel" continues to refer to
*their* project throughout; this rename does not reach it.

---

## Pack shakedown — 2026-08-13

No version, and the most useful thing done to the packs. Four authors each
wrote a five-file planning set for one new primary pack — competent
everywhere except one deliberate defect targeting the dimension that
justifies that pack existing. Four clean-room judges then scored each set
with the real dispatch prompt. No judge was told a test was happening, that a
defect existed, or that other judges existed.

**One clean pass, two confirmed pack gaps, one inconclusive.** `dark-romance`
named its failure and did not test for it; `romantasy` accepted a
denomination argument as a mechanism. Both were fixed and re-judged, and both
judges cited the new test by name.

**And the finding that transferred.** Both packs handed their judge the same
structure — three tests pass, one fails, criteria say "score 6 max" — and one
judge capped while the other averaged. That was a rubric-layer defect
affecting all fifteen packs rather than a pack-layer one, and it became phase
0 of the form work. See 0.5.0, and the Unreleased entry above for the
fourteen-judge verification that it is now closed.

A correction mid-run decided the whole thing: authors were initially told not
to create their packs' declared artifacts, which was wrong, because three
packs score their absence across two to four dimensions — exactly the
dimensions that needed to score high to demonstrate a spread.

Full result in
[`docs/superpowers/2026-08-13-pack-shakedown-result.md`](docs/superpowers/2026-08-13-pack-shakedown-result.md).

---

## 0.3.1 — 2026-08-13

Two pack-criteria fixes, both confirmed by a planted-defect run against the
new packs and then verified by re-judging. Scoring behaviour changes for
dark romance and romantasy projects; no schema or state changes, so existing
projects need no migration.

**Fixed**

- `dark-romance` / `redemption_cost` now totals the ledger in **both**
  directions. Its three previous tests asked what the darker lead lost and
  never whether losses exceed gains, so a book could retire one arrangement
  and then be handed immunity, a replacement contract and a promotion while
  answering every stated test truthfully. The new fourth test caps at 6 when
  net position at the end is equal to or better than at the start, and names
  the two disguises the run exposed: a windfall arriving on someone else's
  timetable, and a surrendered role that is in substance a promotion.
- `romantasy` / `magic_barrier_dependency`'s deletion test now runs as a
  **redenomination**. Deleting the magic from a barrier *priced* in magic
  destroys its unit of account and makes any such barrier look
  magic-dependent — so a debt-settlement betrothal passed a test designed to
  catch exactly that. The test now reprices the obligation in grain, coin or
  land and asks whether the enforcer still enforces. The distinction is
  stated plainly: the question is not whether the obstacle is written in the
  magic's terms, it is whether the magic is what makes it binding.

Neither pack changed dimension count or cap values, so calibration holds at
7.40 / 7.75 / 8.33 for one, two and three caps firing.

**Known, unfixed:** dimension caps are advisory. Two judges met the same
structure — three tests pass, one fails, criteria say "score 6 max" — and
one capped while the other averaged. Every cap in every pack is currently a
suggestion. This is a rubric-layer defect and is deliberately not being
patched pack by pack; see [ROADMAP](ROADMAP.md).

---

## 0.3.0 — 2026-08-13

Six new genre packs, taking the shipped set from nine to fifteen, plus five
fixes to packs the new ones surfaced. Requires a plugin update, not just a
marketplace refresh.

**Added**

- Four primary packs — `paranormal-romance`, `romantasy`,
  `romantic-suspense`, `dark-romance` — admitted only where composing
  existing packs is *wrong* rather than merely thin. A secondary pack
  contributes its dimensions and contract but never its `beat_system`,
  `shape` or `weights`, so `fantasy` + `romance` outlines on Save the Cat
  and never places a romance beat; and unioning two packs' dimensions
  dilutes the pillar gate until caps stop biting.
- Two modifiers — `historical` and `inspirational` — because period and
  faith are orthogonal axes. `inspirational` sets `violence: moderate`
  rather than cozy's `off-page`, so inspirational suspense stays writable.
- Three new per-book artifacts: `braid.md`, `braid_map.md`,
  `power_ledger.md`.

Erotic paranormal romance needs no pack of its own — it is
`paranormal-romance` plus the `erotica` modifier, which is what the modifier
role exists for.

**Fixed**

- `pillar_score` no longer dilutes when a secondary loads. The gate now
  averages the **primary's** dimensions alone; the secondary's still reach
  `overall_score` through the pillar weight. Every pack's authored cap
  arithmetic was wrong whenever a secondary was loaded.
- `fantasy` was out of calibration by TEMPLATE's own rejection rule — two
  4-caps meant two firing required a 9. The severest case moved to the Genre
  Contract, where a breach caps `overall_score` at 6 without touching
  `pillar_score`.
- `cozy` capped its own exemplars: Louise Penny and M.C. Beaton sat in its
  comps while its contract made professional standing a breach.
- `romance`'s pillar preamble was unscoped for its secondary role, telling
  judges to score a fantasy novel as though its main plot were subordinate
  to its romance.
- `display_label` no longer renders "Paranormal Romance Romance" on export
  title pages.
- `ya`'s register promise now yields explicitly to a lower clamp, so YA
  inspirational is writable.

---

## 0.2.0 — 2026-08-12

Genre parameterization. The pipeline stopped assuming every book is a
fantasy novel.

**Added**

- The genre pack system: single markdown files with JSON frontmatter
  declaring `role`, `weights`, `pillar_label`, `beat_system`, `shape`,
  `content_register`, `conflicts_with` and `artifacts`, plus prose sections
  a judge reads directly. Nine packs shipped — `general`, `fantasy`,
  `science-fiction`, `mystery`, `thriller`, `romance`, `erotica`, and `ya`
  and `cozy` as modifiers.
- Three roles: `primary` owns the pillar dimensions and book shape,
  `secondary` layers a second genre's concerns additively, `modifier` is an
  orthogonal axis. Packs may declare more than one.
- Genre contracts — binary promises checked at planning time and against the
  finished manuscript. A breach caps `overall_score` at 6 and never touches
  `pillar_score`.
- `content_register`, clamped per axis to the most restrictive level any
  loaded pack declares, with the source reported so an unexpected clamp is
  explicable.
- `resolve_genre.py`, `validate_genre_pack.py`, `genre_pack.py`, a pack
  authoring guide, and a leak guard test keeping genre content out of the
  base machinery.
- Project-level pack override: a pack in a novel's own `genres/` directory
  wins over the plugin's.

**Changed**

- `lore_score` → `pillar_score` throughout; the foundation rubric's output
  schema became nested under `pillar` / `character` / `structure` / `craft`.
- `overall_score` and `pillar_score` are now reported as two-decimal means.
  Integer-only scores could not express any value between 7 and 8 — exactly
  the band the gate sits in.
- Genre selection moved into `seed` step 2, before the project
  directory exists, closing a window where an interrupted run could build an
  entire book as general fiction silently.
- The marketplace manifest moved to the repo root, which is where
  git-sourced marketplaces look for it.

**Migration:** projects created before 0.2.0 have no `genre` field. Running
`/autoauthor:status` inside one detects this, explains that existing scores
came from the fantasy rubric, and migrates on confirmation.

---

## 0.1.0 — 2026-08-05

Initial release. The original Python pipeline rebuilt as a Claude Code
plugin.

**Added**

- Eight skills: `novel` (status and routing), `seed`,
  `import`, `foundation`, `draft`, `revise`,
  `review`, `export`.
- Score-gated phases — each runs a modify → evaluate → keep-or-discard loop
  against a rubric rather than finishing a checklist, and a phase that
  cannot clear its bar keeps working.
- Clean-room LLM judges: each receives only a rubric and the text, with no
  drafting context and no memory of how the text was produced.
- A mechanical slop scanner with no LLM in the loop — banned vocabulary, AI
  fiction clichés, telling-not-showing, sentence-length uniformity, em-dash
  density.
- A four-persona reader panel in the revision phase.
- Per-project git repositories, committed at every kept iteration, so a
  regression costs nothing to discard.
- LaTeX PDF and ePub export.
