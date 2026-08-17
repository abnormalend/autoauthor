# Revision-phase findings — 2026-08-17

Source: a full `/autoauthor:revise` run on **Her Years, Our Years** (`~/novels/redshift`),
a 4-chapter, ~4,800-word hard-SF/YA **short story**. Three cycles, ~35 judge
dispatches. Final: 7.86 → 7.86 → 7.71 (plateau), chapters 7.67 / 7.78 / 7.78 / 8.00.

These are findings about **the skills**, not about that manuscript. Ordered by
my estimate of value. Each has the evidence that produced it, so a follow-up
session can judge whether the fix is worth it.

Paths below are relative to `plugin/autoauthor/`.

---

## 1. Guardrails are hard-coded to novel scale and break on other forms

**Severity: high — this is the one that produced a wrong instruction, not just a
suboptimal one.**

`skills/revise/SKILL.md` and `skills/revise/references/revision-playbook.md`
state as non-negotiable:

- "Never compress a chapter below 1800 words"
- "Sweet spot: 2200-3000 words for a compressed chapter"
- "Target: cut 40-60% of the chapter's words"
- "WARNING: the script's COMPRESS target (55% of current) will ask for a count
  under the 1800 floor on any chapter below ~3,300 words."

This project's form is `short-story`; `resolve_genre.py` reports
`shape.chapter_words: 1200`. **Every chapter was already below the stated floor
before revision started.** Read literally, the guardrail forbids all cutting and
the sweet spot is unreachable. I scaled it by hand (announced a ~1,000-word
floor) and flagged the deviation, but that is a judgement the skill should not
be delegating silently.

Note the floor is *ratio-derived* in the novel case: 1800 is 50% of the SF
pack's `chapter_words: 3600`. That ratio applied here gives 600, which is far
more permissive than the 1,000 I chose — so even the principled scaling is
ambiguous, and I had to pick.

**Proposed fix.** Derive the floor from the resolved shape rather than stating a
literal. In `SKILL.md` Setup, after `resolve_genre.py`, compute and state:

```
chapter floor = 0.5 × shape.chapter_words   (novel: 1800, short-story: 600)
sweet spot    = 0.6–0.85 × shape.chapter_words
```

Then have Setup *print* the resolved numbers so they appear in the transcript.
Same change in the playbook's Dangers section and in `gen_brief.py`'s COMPRESS
target, which should clamp to the derived floor rather than to 1800.

**Related:** the rubrics are also novel-shaped. Every full-novel judge this run
volunteered some version of "this is a 4,610-word novelette being scored against
the full-novel rubric" — one explicitly added a structural note that the
compressed band should drop `consequence_cascade` and `rule_integrity`. The
genre pack already knows this (`## At Compressed Length`); `full-novel.md`
apparently does not receive it.

---

## 2. `apply_cuts.py` runs before any protection mechanism exists

**Severity: high — caused actual damage that I caught only in manual review.**

The Diagnose flow is: dispatch cutting judges → run `apply_cuts.py` → hand-apply
the REWRITE skips. Protection of load-bearing lines is possible only at the
*third* step, because that's the first one a human/model is in the loop for.

In cycle 2 the mechanical pass cut `"Nothing had ever come off that list. There
was no button."` — a line a cycle-1 chapter judge had listed among ch_04's
`three_strongest_sentences`, and the sentence that states the append-only
archive the entire climax turns on. My protection list existed but only guarded
the REWRITE triage. I restored it by reading the diff, not by any check.

**Proposed fix.** Add `--protect-file <path>` to `shared/scripts/apply_cuts.py`:
a newline-delimited list of substrings; any cut whose quote contains one is
skipped and reported as `PROTECT [reason]`. Then have `SKILL.md` build
`edit_logs/protected.md` *before* the mechanical pass (see finding 3 for what
goes in it).

---

## 3. No cross-cycle memory: cutting judges re-attack the same protected lines

**Severity: high — recurring, and the cost compounds each cycle.**

Cutting judges see one chapter and have no memory of prior cycles. Across three
cycles I protected **five** lines, and two were attacked in consecutive cycles:

| Line | Attacked | Why protected |
|---|---|---|
| `and we're just the ones who show up, so—` | cycle 1, cycle 2 | `outline.md:620` Sc1 plant → Sc4 harvest |
| `Kalei went past it with the cooler. Her mother worked here.` | cycle 2 | cycle-1 judge: chapter's *strongest sentence*; outline mandates the beat |
| `The letter did not have a hole in it...` | cycle 2, cycle 3 | `three_strongest` per **both** cycle-1 ch_03 judges |
| `Kalei had spent six hours deciding it at a keyboard...` | cycle 2 | `three_strongest` per **both** cycle-1 ch_04 judges |
| `Everybody knew it and nobody said it in front of Pua.` | cycle 3 | `three_strongest` per cycle-2 ch_04 judge |

A related near-miss: in cycle 1 the ch_01 cutting judge removed `because the
summit was a sacred place`. The chapter judge then flagged the beat as missing —
`outline.md` mandates exactly one such line. Nothing in the pipeline connects
those two judges; I caught it because I read both.

**Proposed fix.** Have `SKILL.md` maintain `edit_logs/protected.md`, appended to
at the end of each cycle from two sources that are already being produced:

1. every `three_strongest_sentences` entry from that cycle's chapter judges
2. every quoted line in the outline's plant/harvest table

Feed it to `apply_cuts.py --protect-file` and to the REWRITE triage. Cheap,
mechanical, and it removes the single most error-prone manual step in the cycle.

---

## 4. Splice-damage checklist is incomplete

**Severity: medium-high — the audit is mandatory and its stated checks miss
real defects.**

`SKILL.md` lists: ends in `[,;]`; no terminal punctuation; double space;
adjacent/empty quote pairs; whitespace before punctuation; doubled word.

Six mechanical cuts in cycle 2 produced **five** defects. Two of the five were
outside that list:

- **Glued sentence** — `"Okay," Pua said, and put the phone down,  She called the room.`
  (comma + double space + capital). The double-space check caught this one only
  by luck; a single-space version would have passed everything.
- **Doubled comma** — `nobody in the room for it, , and her mother`
- **Trailing whitespace at paragraph end** — `...and gone back to work. ` — passed
  every listed check (it ends in `.` followed by `\s*$`). I found it by eye in
  cycle 1 and it survived into cycle 2.
- **Leading whitespace at paragraph start** — ` Somebody said "ho" very quietly.`

**Proposed fix.** Extend the checklist with: `,\s*,`; `[,;]\s+[A-Z]` (glued
sentence, with a proper-noun allowlist); trailing `\s+$`; leading `^\s+`. Better:
ship it as `shared/scripts/splice_audit.py` taking a pre-cut tree, so it isn't
re-implemented per run. I wrote one three times this session with slightly
different checks each time.

---

## 5. Re-baseline **before** rewriting, not after a failed gate

**Severity: high — this was the single highest-value deviation I made.**

`SKILL.md` says to re-baseline reactively: "the moment a rewrite fails the gate,
re-score the CURRENT committed text." I instead dispatched baselines for all four
chapters *at the start of Fix*, concurrently with drafting. Two payoffs:

1. **Honest gates from the start.** ch_04's recorded score was 7.33 but its true
   revision-phase baseline was 7.00 — the real gain was +0.78, not +0.45.
2. **The baseline judges found defects the debt list had missed** — three of
   them, including a continuity contradiction (`"I'd have to wake up your
   mother"` four paragraphs after she speaks on the crew loop) and an archive
   keyed by ship-year in one chapter and Earth-year in another.

Reactive baselining gets neither, because by then you've already written against
a wrong number.

**Proposed fix.** Change Fix step 4 to recommend dispatching baselines for all
chapters you intend to touch, in parallel, at the start of Fix. Keep the reactive
rule as the fallback.

---

## 6. Baseline staleness is per-**cycle**, not just per-phase

**Severity: high — the skill's stated cause is too narrow, and I nearly
discarded good work because of it.**

`SKILL.md` frames staleness as a *phase* effect: drafting judges are more
generous than revision judges. True, but incomplete. I measured a **0.67 drift
between cycle 1 and cycle 2 revision judges on identical text**:

- ch_03 committed text, scored cycle 1: **7.89**
- same text, unchanged, re-scored cycle 2: **7.22**

In cycle 2 a rewrite scored 7.78 and "failed" the 7.89 gate by 0.11. Against the
true same-cycle baseline it **beat it by +0.56**. I was one command from
discarding it. The re-baseline judge then independently recommended exactly the
change I was about to throw away.

**Proposed fix.** Restate the rule as: *a baseline is valid only within the cycle
it was measured.* Any gate using a number from a prior cycle must be re-measured
first. Combined with finding 5, this is just "baseline at the start of every
cycle's Fix."

Also worth stating explicitly (currently only implied by the `baseline` value in
the `keep_discard` column): **a baseline dispatch does not consume one of the 3
attempts.** I had to reason that out mid-run while attempt-budget-constrained.

---

## 7. The panel's lossy-input false positives are predictable and un-suppressed

**Severity: medium — wasted verification effort every cycle, and the same items
recur.**

The skill correctly warns the panel reads only `arc_summary.md` and names two
recurring false positives. In practice I hit them repeatedly, and one was new:

- *"Kalei and Pua alone"* named as a missing scene by 4/4 in cycle 1 — legitimate
  then. I **built** it. It was named again by 3/4 in cycle 2 and 3/4 in cycle 3,
  because the summary compresses 16 lines of dialogue into one clause.
- *"The three forged sentences are never shown"* (cycle 2, writer) — they are
  quoted **in full** at `ch_03.md:81`, in the same italic treatment as the real
  letter. The summary renders them as "writes three of her own."
- *"Cut chapter 2"* — 4/4 in all three cycles, verified-and-skipped twice, with
  the same verification each time.

**Proposed fix, two options (not exclusive):**

- **(a)** Have the resync procedure require that any beat named in a prior
  cycle's consensus be represented in the summary *at the granularity that was
  asked for* — i.e. if the panel asked for a scene and you wrote one, the summary
  gets the dialogue, not a clause. Cheap, and it directly kills the recurrence.
- **(b)** Feed prior-cycle `edit_logs/skipped.md` into the panel dispatch prompt,
  or at minimum into Fix step 1, so an item already verified-and-skipped is
  auto-skipped unless the reader supplies new evidence. Currently every cycle
  re-litigates from zero.

---

## 8. Foundation docs need an explicit "author-facing only" marker

**Severity: medium-high — cost three failed rewrite attempts and a score
regression.**

The cycle-2 full-novel judge faulted the book for not delivering
`outline.md:143` — "300 bytes is not a letter, and the codec will not emit a
partial frame" — noting correctly that without it a reader can ask why the
sender couldn't transmit 75 characters a year.

Three attempts to put that rule in prose each introduced a **new arithmetic
error** into a story whose whole contract is that numbers check:

| Attempt | Score | Failure |
|---|---|---|
| 4 | 7.56 | stated as a character budget; the forgery then violates it by ~100 chars |
| 5 | 7.44 | welded the 40-year letter gap to the 10-year transmission cadence; `canon_compliance` 8 → **6** |
| 6 | 7.78 | rule dropped, resistance beat kept; `canon_compliance` 8 → **9**, zero violations |

The rule sits at the intersection of frame size, allowance banking, and the
Doppler cadence. Every compact in-voice statement of it collapsed two of the
three. It is *correct* physics and *unwritable* prose.

The same shape appears with deliberate withholdings. `characters.md:318` says of
Ikaika's unnamed job: *"That is the entire payoff"* and *"which he does not do in
this story."* The full-novel judge faulted the book for not naming it. Naming it
would dismantle the character.

**Proposed fix.** Add to the outline/characters templates an explicit section —
`## Author-facing only (never on the page)` — and instruct `full-novel.md`,
`reader-panel.md` and `chapter.md` to treat items listed there as
deliberately withheld rather than as unpaid debts. This converts a recurring
class of expensive false positives into a one-line lookup.

---

## 9. Cutting passes have negative expected value on a low-fat manuscript

**Severity: medium — mostly a cost/waste issue, but cycle 2 shows it can hurt.**

Fat estimates by cycle: **c1** 10–16%, **c2** 9–16%, **c3** 9–13%. The judges
keep returning cuts because they are asked to return 10–20 regardless.

Cycle 2's cuts pass: −269 words, 4 protections, 1 restore, 5 splice defects, and
the cycle score went **7.86 → 7.86** with `overall_engagement` dropping 8 → 7. By
cycle 3 I skipped the ch_01/ch_02 cutting dispatches entirely (logged) because I
had pre-committed to rejecting most of their output.

**Proposed fix.** Gate the cuts pass in `SKILL.md`: skip a chapter's adversarial
edit if *both* (a) its last reported fat < ~12% and (b) the previous cycle's cuts
did not improve its chapter score. Or simply: run the full cuts pass in cycle 1,
and in later cycles only on chapters whose score fell.

Also worth noting for the router: `--min-fat 15` gated out 3 of 4 chapters on the
very first run. The skill *anticipates* this and says re-run with `--min-fat 0` —
which worked — but if the default is wrong for every post-slop-pass draft, the
default is wrong.

---

## What worked and should not be "fixed"

Recording these so a follow-up session doesn't refactor them away:

- **`score_verdict.py`** — judge and computed aggregate agreed on all three
  full-novel evals (7.86 / 7.86 / 7.71). The check cost nothing and the one time
  it matters it will matter a lot.
- **The interim-measurement rule** (only the final measurement in a cycle carries
  the `full-eval cycle N` prefix) — used exactly once, in cycle 2, when a
  measurement came back down and I repaired the cause. Worked as designed; the
  plateau check saw cycle 2 once.
- **The dialogue-paragraph filter on REWRITE cuts** — earned its keep on the
  first run by blocking a cut to `"we're just the ones who show up, so—"`, an
  outline plant. The skill's justification for it is measured and correct.
- **"Reject any rewrite longer than its quote"** — zero hits across three cycles.
  Harmless, keep it, but it isn't where the risk is.
- **The plateau rule** — fired correctly and stopped a run that was oscillating
  within judge variance. `pacing_curve` read 7 / 7 / 8 / 7 across four
  measurements; the playbook's "pacing 7 may be a structural ceiling" is
  accurate and saved a fourth cycle.

---

## Suggested priority for the follow-up session

1. **Findings 5 + 6** (baseline timing and per-cycle validity) — highest value,
   smallest diff, and the one that silently destroys good work today.
2. **Findings 2 + 3** (protection list, wired into `apply_cuts.py`) — removes the
   most error-prone manual step.
3. **Finding 1** (form-scaled guardrails) — correctness bug for any non-novel form.
4. **Finding 4** (splice checks → shared script).
5. **Findings 7 + 8** (lossy-summary and author-facing-only suppression) — biggest
   reduction in wasted dispatches.
6. **Finding 9** (gate the cuts pass) — cost saving, do last.
