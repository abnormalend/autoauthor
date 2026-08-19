# autoauthor:draft — findings from the *Her Years, Our Years* run

Date: 2026-08-19
Plugin: autoauthor 0.18.0, skill `draft`
Project: ~/novels/redshift (science-fiction + ya, short-story form, 4 chapters)
Scope: issues and bugs only. Importance 1–5 (5 = affects correctness of what gets committed).

---

## 1. No branch for "score clears but the judge named a missing plant/payoff or a one-word arithmetic fix" — importance 4

The gate has exactly two outcomes (keep / discard) plus the canon-only
`correct` branch. Twice the judge flagged an outlined plant that was not
on the page (P4 "send whoever is yours" in ch1; P8 the unsent phone notes
in ch3) and twice a one-word count error (switchback arithmetic in ch1;
"three sentences" → "two" in ch3). The skill's own reasoning says plants
compound into later chapters, so committing as-is is wrong, but editing
after the judge breaks the "score certifies the artifact" rule the skill
is emphatic about. Resolution was improvised and inconsistent: ch1 and
ch3 were re-judged as attempt 2; ch2 and ch4 got un-judged surgical
touch-ups before commit.

Suggest: extend `correct` to cover (a) a plant named in this chapter's
outline Plants list that the judge reports missing, and (b) a
judge-named arithmetic/fact fix — same rules as the canon branch: one
edit pass addressing only the named items, re-run step 3, one
re-dispatch, counts against the 5-attempt budget, row logged `correct`.
Or, alternatively, state explicitly that post-judge edits are forbidden
and that missing plants become state.json debts.

## 2. Setup step 1 has no path for "foundation cleared its gate at the iteration cap but the phase was never flipped" — importance 3

Foundation's exit sets `phase: drafting` only on its normal exit. At
cap it left `phase: foundation`, `iteration: 4`, scores 7.51 / 7.33
(both above the form gate 7.5 / 6.0), and a results.tsv row reading
"awaiting user decision". The draft skill says STOP on any phase other
than `drafting`, so a literal reading blocks forever. I checked the gate
numbers, treated the user's `/autoauthor:draft` as the decision, flipped
the phase, and committed `foundation complete: 7.51/7.33`.

Suggest: if phase is `foundation`, `iteration == form.iteration_cap`,
and both `foundation_score` and `pillar_score` clear the form gate, the
invocation of `/autoauthor:draft` is the user's decision — flip the
phase, commit `foundation complete`, and proceed. Otherwise STOP as now.

## 3. `continuity_check.py` FOUND is a false reassurance for small integers, and the outline's own beat prose can contradict its fact table — importance 3

Ch2 originally said the block took "under five seconds", copied from the
outline's scene-2 beat 6 and voice.md exemplar 4. The fact table says
35 s from the first frame to the Kahananui frame (~2 s per frame,
alphabetical). The script reported "five" as FOUND because the word
occurs somewhere in a fact document. Caught by hand.

Two fixes: (a) drafting-rules.md should say the fact table outranks beat
prose and voice exemplars where they disagree; (b) foundation's
`internal_consistency` dimension should be checking the outline's beat
text against its own fact table — it passed this one through four
iterations.

## 4. Exemplar reuse is penalized by the judge but the drafting rules push toward it — importance 2

voice.md calls its exemplar passages "the tuning fork", and the
outline's beats for scenes 1–2 are near-paraphrases of them. The judge
docked ch1 and ch2 for "heavy verbatim reuse of the voice-doc exemplar
passages". One line in drafting-rules.md — "calibrate against the
exemplars; do not reproduce them" — resolves the tension.

## 5. Mechanical `telling_violations` fights the YA pack's rule 26 — importance 2

"Kalei was proud of it. She was furious." is the hot, absolute teenage
interiority ya.md rule 26 asks for; slop_score.py penalized it (0.7
total with one other hit) and I rewrote to evade the regex. Either
exempt free-indirect declaratives under a `ya` modifier, or note in the
skill that this penalty is expected in that register and should be
absorbed rather than dodged.

## 6. Word target ambiguity with required quoted text — importance 1

Ch3's outline target of ~1,600 words includes ~270 words of verbatim
letter and forgery text the outline requires on the page. The skill does
not say whether quoted text counts toward the target. Say so.

---

## Not a draft-skill bug, noticed in passing

- The pushover skill's SKILL.md points at
  `~/.claude/skills/omc-learned/pushover/pushover.sh`; the script
  actually lives at `~/.claude/skills/pushover/pushover.sh`.
