# Drafting-phase findings — 2026-08-17

Source: a full `/autoauthor:draft` run on **Her Years, Our Years** (`~/novels/redshift`),
a 4-chapter, 4,949-word hard-SF/YA **short story**. Four chapters, four judge
dispatches, zero retries — every chapter cleared the gate on attempt 1.
Finals: 7.33 / 7.44 / 7.00 / 7.33 (mean 7.28). Slop penalty 0.0 on all four.

These are findings about **the skill**, not about that manuscript. Ordered by my
estimate of value. Each carries the evidence that produced it.

Paths below are relative to `plugin/autoauthor/`.

Companion to `2026-08-17-revision-findings.md`. Findings 1 and 3 here are the
drafting-side instance of that document's Finding 1 (novel-scale hard-coding),
and the two should probably be fixed in one pass.

---

## 1. The judge JSON is transcribed by hand, and `score_verdict.py` then validates the transcription

**Severity: high — it puts a lossy human step between the measurement and the
artifact that certifies the measurement.**

`SKILL.md` step 4 says "Return ONLY the JSON object the rubric specifies" and
then, separately, "Save the JSON to `eval_logs/<UTC yyyymmdd_hhmmss>_chNN.json`."
It does not say *who* saves it. In practice the subagent returns ~1,500 words of
JSON in its final message and the orchestrator re-types it into a file with
`Write`.

That is four full re-transcriptions per short story, and it would be twenty-plus
on a novel. Worse, it defeats the purpose of the very next step: `score_verdict.py`
reads the file I typed, so it verifies my copy of the dimension scores against my
copy of `overall_score`. If I fat-finger a dimension during transcription, the
check passes and the record is wrong. The one guard in the loop is validating the
wrong artifact.

It also makes the prescribed "malformed JSON → one strict retry" step nearly
meaningless — malformed output gets silently normalized during transcription
rather than triggering the retry.

**Proposed fix.** Have the judge write its own artifact. Amend the dispatch
prompt in `skills/draft/SKILL.md` step 4:

> "...Write the JSON object to `<absolute path>/eval_logs/<timestamp>_chNN.json`
> and return only that path and the `overall_score` value."

The judge subagent is `general-purpose` and already has `Write`. Then
`score_verdict.py` reads the genuine output, the fence-stripping instruction
becomes the judge's own problem to get right, and the strict-retry branch fires
on real malformation. Same change applies to `skills/revise` wherever it
dispatches scored judges.

---

## 2. `canon_compliance` was the weakest dimension in 3 of 4 chapters, and every failure was a checkable number

**Severity: high — this is the failure mode the loop actually produces, and
nothing mechanical looks for it.**

Aggregate dimension scores across the run:

| dimension | ch1 | ch2 | ch3 | ch4 |
|---|---|---|---|---|
| pillar_integration | 8 | 8 | 8 | 8 |
| voice_adherence | 8 | 8 | 8 | 8 |
| **canon_compliance** | 8 | **6** | **6** | **6** |
| continuity | **6** | 8 | 7 | 7 |

Every violation the judges raised was arithmetic or clock, not craft:

- ch1 — a character reads "the front of" a data block two paragraphs *before* the
  receive window opens.
- ch2 — "Pua had been sixty" (the outline's numbers make her 52); "eight of them
  in eighty years" read at 03:30, before the eighth finishes at 04:02.
- ch3 — "at a desk somewhere out past Neptune" for a ship at 0.98c, which is
  wrong by orders of magnitude *and* contradicts the quoted letter's own "I
  calculated it before I left."
- ch4 — four more: a block year that does not exist, a read-aloud duration
  attached to the wrong object, a character called dead who is alive by the
  story's own physics, and a capability described imprecisely ("a block she
  could not send" for one that can be sent but cannot arrive in time).

Eight defects, all of them derivable from a table that was sitting in
`outline.md` under "The authoritative clock" and "Facts the story must not
contradict." None was a judgement call. `slop_score.py` runs mechanically on
every chapter and catches diction; nothing analogous runs on facts, in a genre
whose own pack says the reader "forgives handwaving but never forgives
inconsistency."

**Proposed fix, cheap version.** Add to `references/drafting-rules.md`, as a
numbered rule rather than prose, a pre-scoring self-check:

> Before running the slop score, list every clock time and every bare number you
> wrote in this chapter, and check each one against the outline's facts/clock
> section. A number you cannot trace to that section is a defect, not a detail.

**Proposed fix, better version.** A `shared/scripts/continuity_check.py` that
regexes `\d{2}:\d{2}` and bare integers out of `ch_NN.md`, greps the same tokens
out of `outline.md`, and prints the chapter's numbers in two columns — *found in
outline* and *not found in outline*. It cannot know which unmatched numbers are
legitimate inventions, and it does not need to; a 10-line "not found" list that a
drafter eyeballs would have caught six of the eight above in seconds. Wire it
into step 3 beside `slop_score.py`.

---

## 3. The gate ships known factual contradictions, with no path to correct one without discarding the chapter

**Severity: high — by design, but the design is wrong for this specific class of
defect.**

The gate is `final > 6.0 → keep`. All four chapters passed on attempt 1 with
`canon_compliance` at 6–8, so the retry loop never engaged, and I committed four
chapters carrying eight known arithmetic errors and logged **18 debts** for a
later phase. "Forward progress over perfection" is the right default and I do not
want it removed. But a canon violation is categorically unlike a weak sentence:

- It is **cheap to fix now** — six of the eight were single-word edits.
- It **compounds**. ch1's early wrong-guess line forced ch2 to write around it,
  and the judge correctly discounted ch2's version of that beat as a repeat.
- It is **least visible to the phase that inherits it**. The revision phase's
  instruments are cutting- and compression-oriented; a wrong number survives a
  cut pass untouched because it reads perfectly well.

There is also no sanctioned middle path. Once judged, my options were keep-as-is
or `git reset --hard` and rewrite from a different approach. Correcting two words
and re-judging is not a listed move, and doing it silently would have decoupled
the committed text from the committed score — so I kept the errors, which is the
behaviour the skill asks for and not the behaviour anyone wants.

**Proposed fix.** Two changes to step 6:

1. Second gate condition: keep requires `final > 6.0` **and** the judge's
   `canon_compliance.violations` array is empty (or `canon_compliance >= 7`).
2. A **surgical-correction branch** that is explicitly not a discard: if the
   chapter fails *only* on canon, apply edits addressing the named violations
   and nothing else, then re-dispatch the judge. Log it as `correct` rather than
   `keep`/`discard`, and count it against the 5-attempt budget so it cannot loop.
   Cost is one Edit and one dispatch, against a debt that otherwise survives into
   revision.

---

## 4. Whole-story voice budgets cannot be enforced by a per-chapter loop

**Severity: high, and it worsens monotonically with length.**

This project's `voice.md` sets budgets scoped to the *whole story*:

- negative definition (`not X, but Y`) — **one instance in the whole story**
- `never once` — **one in the story**
- `the way X did` — **three in the story**
- the two-beat correction — **zero in narration**, reserved to one character

Step 1 loads context "fresh each chapter" and lists this chapter's outline entry
and the previous chapter's last ~1,000 words. Nothing in the prescribed context
carries a *running count* of anything. I tracked these by hand only because a
4-chapter story fits in one session's context; across a 20-chapter novel spanning
sessions it is not trackable at all.

It already failed here. ch2 spent **two** negative definitions against a
whole-story budget of one, and I found out from the judge, not from the loop.

**Proposed fix.** `slop_score.py` already counts figurative constructions
per file and already accepts pack paths. Add a cumulative mode:

```
slop_score.py chapters/ch_*.md --voice-budgets voice_budgets.json
```

reporting `negative_definition: 3/1 OVER` across the set. The patterns are
greppable and the counting machinery exists. Foundation would emit
`voice_budgets.json` alongside `voice_wells.json` (which this project already
has) so the caps are data rather than prose a drafter has to remember. Then step
3 runs it against all chapters drafted so far, not just the current one.

---

## 5. A state/history mismatch silently triggers a full re-draft

**Severity: medium-high — it is a Setup check that does not exist, and it fired
on this very run.**

At Setup, this project presented:

- `state.json`: `phase: "drafting"`, `chapters_drafted: 0`
- `chapters/`: empty
- `git log` HEAD: `374a52b revision complete: 3 cycles (7.71)`, with `cycle 3`,
  `cycle 2` and per-chapter draft commits beneath it

State said nothing had been drafted. History said the book had been drafted *and*
revised through three cycles. Setup checks the phase and the clean tree, and step
4 derives the resume point from `chapters/ch_NN.md` existence alone — so the
empty directory won, and I drafted the entire story from scratch.

Everything the skill told me to check, I checked, and it passed. The skill has no
instruction to reconcile `state.json` against the repository's own history.

**Proposed fix.** Add to Setup, after the phase check:

> Cross-check `chapters_drafted` against both the files in `chapters/` and
> `git log --oneline | grep -cE 'draft: ch|revision complete'`. If history
> records drafting or revision work that the working tree does not reflect, STOP
> and report the discrepancy — do not infer the resume point from the empty
> directory.

Same check belongs in `skills/status`, which is the skill a user runs precisely
to answer "where does this stand."

---

## 6. `canon.md` is required by the loop and created by nobody

**Severity: medium-high — the instruction is unsatisfiable as written at
compressed forms.**

Step 7: "Append the judge's `new_canon_entries` to `canon.md`." Step 4's dispatch
template: "The other input files are voice.md, world.md, characters.md,
**canon.md**, outline.md in the project directory."

At `form: short-story`, `resolve_genre.py` reports `layers: [voice, characters,
outline]`. Foundation therefore never writes `world.md` or `canon.md`, and
neither existed. `forms/short-story.md` anticipates exactly this — "Drafting may
still write a `canon.md` — facts established on the page need recording" — but no
step in `skills/draft/SKILL.md` creates it. I created it by hand at chapter 1
with an invented header, and hand-patched all four judge prompts with a
parenthetical saying world.md and canon.md do not exist, or the judges would have
spent tool calls hunting for missing files.

**Proposed fix.** Two lines:

1. Setup: "If `canon.md` does not exist, create it from
   `shared/templates/canon.md` with the primary pack's `## Canon Categories` as
   its section headings." (The SF pack already ships those headings.)
2. Step 4: build the input-file list from `form.layers` plus `canon.md`, rather
   than naming the novel's five files literally. One sentence:
   "List only the layer files the resolved form actually builds, plus canon.md."

---

## 7. Two drafting rules point at `world.md` and are unsatisfiable at compressed forms

**Severity: medium — same root cause as Finding 6, different blast radius.**

- `references/drafting-rules.md` rule 6: "The genre's central system... manifests
  as SPECIFIC physical or concrete detail **defined in world.md** — never vague.
  Use the exact established specifics."
- `genres/science-fiction.md` drafting rule 26: "The novum's costs and limits
  manifest as specific physical and material consequence **defined in
  `world.md`**... Use the exact established costs."

Both are correct in intent and name a file that does not exist at this form. The
facts they demand were real and available — they were in `outline.md` under
"Facts the story must not contradict," which is where the short-story form pack
says world material lives. A less careful drafter reads "defined in world.md,"
finds no world.md, and concludes the rule is inapplicable. That is the direct
route to the vagueness both rules exist to prevent.

**Proposed fix.** Replace the literal filename with the role in both places:
"defined in the form's fact-bearing layer — `world.md` where the form builds one,
otherwise the outline's facts section." Then grep the other packs; `world.md`
appears in several `## Drafting Rules` blocks and every instance has this bug.

---

## 8. The per-chapter context load starves the drafter of exactly the material that prevents Finding 2

**Severity: medium.**

Step 1 prescribes: voice.md full, world.md full, characters.md full, **this
chapter's outline entry**, the previous chapter's last ~1,000 words, and the next
entry's first ~10 lines.

I ignored the outline slice and loaded `outline.md` whole (42 KB). That was the
right call and I would make it again. The per-scene entries are maybe a third of
that file; the rest is the global apparatus — the authoritative clock table, the
"Facts the story must not contradict" list, the foreshadowing plant/payoff table,
the MICE thread table, the stability-trap audit, the register contract. Those are
precisely the sections that would have prevented the eight canon defects, and a
scene-entry-only load excludes all of them.

The prescribed slice is also poorly matched to the compressed band generally: at
four chapters, the whole outline costs less than the chapter it is used to write.

**Proposed fix.** Amend step 1:

> Load this chapter's outline entry **and every section of `outline.md` that
> precedes the first scene/chapter entry** — the clock, the fact list, the
> register contract, the foreshadowing table. At the compressed band
> (`form.band == "compressed"`), load `outline.md` in full.

---

## 9. The mandated post-draft slop-pass commit fails on a clean tree

**Severity: low — but it is an instruction that errors.**

Cleanup step 1 ends: "Commit `post-draft slop pass`." The pass found nothing —
zero tier-1 hits, zero genre-banned hits, zero fiction AI tells, `max_penalty
0.0`, figurative density 0.00–1.13 against a threshold of 3.5. No edits, clean
tree, and `git commit` exits non-zero with nothing staged.

**Proposed fix.** "If the pass made no edits, report the clean result and skip
the commit." Trivial, but a literal reading currently ends the phase on a failed
command.

---

## 10. `attempts.tsv` handling is undefined for the zero-retry case

**Severity: low.**

Step 6: "During the retry loop, append each attempt's row to the untracked
`eval_logs/attempts.tsv`... At commit time, append ALL of this chapter's attempt
rows from `eval_logs/attempts.tsv` into `results.tsv`."

Both instructions are scoped to the retry loop. With zero retries — which is what
happened four times out of four — it is unclear whether `attempts.tsv` should be
written at all, or whether the single passing row goes straight to `results.tsv`.
I wrote both (`tee -a`), which seems right but is a guess.

**Proposed fix.** One clause: "Write the row to `attempts.tsv` for every attempt
including the first, whether or not it passes."

---

## What worked and should not be "fixed"

- **`resolve_genre.py` → both packs into `slop_score.py`.** The compressed-band
  `figurative_threshold` of 3.5 is well calibrated. Four chapters came in at
  0.00 / 0.75 / 1.13 / 1.13 with zero penalties, and the prose is not austere —
  the threshold is permissive enough to be non-binding on disciplined writing,
  which is the correct place for a guardrail to sit.
- **The genre pack's `## At Compressed Length` section.** Dropping
  `consequence_cascade` and `rule_integrity` and keeping the three that survive
  is right, and `pillar_integration` scored 8 on all four chapters — the one
  dimension that never wobbled. Contrast the revision-findings note that the
  full-novel rubric does *not* receive this; the genre pack's version works.
- **Anti-pattern rule 21 (end each chapter differently).** Four distinct closing
  shapes across four chapters and no judge flagged ending repetition, in a story
  where all four chapters end in the same room. This rule earns its keep.
- **The fresh-judge discipline** ("no drafting context"). The judges caught
  things I was structurally unable to see: a broken pronoun referent at ch4's
  highest-pressure sentence, the Neptune register breach, and an
  outline-mandated plant I had dropped without noticing. Their independence is
  doing real work — do not let them inherit drafter context to save tokens.
- **`score_verdict.py`.** Agreed with the judge 4/4 (7.33 / 7.44 / 7.00 / 7.33).
  It cost nothing. Keep it — but see Finding 1: it should be reading the judge's
  file, not mine.
- **The debts mechanism.** 18 debts logged with file paths, named violations and
  proposed corrections. This is the right shape for handoff; Finding 3 is an
  argument that the *canon* subset should not need it, not that the mechanism is
  wrong.

---

## Suggested priority for the follow-up session

1. **Finding 1** (judge writes its own JSON) — smallest diff in the document, and
   it repairs the integrity of the one automated check in the loop.
2. **Findings 2 + 3** (numeric continuity check, and a canon gate with a surgical
   correction branch) — together these address the run's dominant defect class.
   Do them as one change; the gate is useless without something that finds the
   violations, and the checker is wasted if the gate ignores it.
3. **Finding 4** (cumulative voice budgets) — currently unenforceable at novel
   length, which is the length the pipeline is for.
4. **Findings 6 + 7 + 8** (form-aware file lists, `world.md` references, outline
   load) — one coherent pass over "the skill assumes novel-shaped foundation
   layers." Pairs with revision-findings Finding 1.
5. **Finding 5** (state/history reconciliation at Setup) — small, and it prevents
   an entire wasted phase.
6. **Findings 9 + 10** (clean-tree commit, `attempts.tsv` in the happy path) —
   wording nits, do last.
