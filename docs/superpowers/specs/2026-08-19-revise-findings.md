# autoauthor:revise (0.18.0) — findings from cycle 1 on `redshift`

Issues and bugs only. Importance: 1 (cosmetic) – 5 (silently wrong result).

## 1. `gen_brief.py --panel` misses zero-padded chapter references — importance 4
arc_summary.md headers are `## Chapter 01`, so panel readers write "Chapter 03". The
mention regex `\b(?:Chapter|Ch\.?)\s*{ch}\b` does not match "Chapter 03" (the `0` sits
between). The editor persona's verdicts were dropped from the brief until I normalised
"Chapter 0N" → "Chapter N" in reader_panel.json by hand. Fix: accept `0*{ch}` in the
regex (and/or tell the arc_summary step to use unpadded numbers).

## 2. Panel brief TARGET is a mechanical 45% COMPRESS whenever cut_candidate matches — importance 3
`--panel 3 --chapter-words 1200` produced `TARGET ~969 words (compress from 1762)`. The
playbook itself says a cut-candidate verdict is a hypothesis about repetition, not
length, and the floor clamp only protects against going below 600. A user following
the brief literally would summarise an eventful chapter; the panel's actual finding
(lookup device repeated; clock-stamped pacing) needed a restructure at ~the same
length, which scored +0.22. Suggest the brief print the compress target only when
`--cuts` fat% supports it, or label it "upper bound, not a goal".

## 3. One cycle per session vs "minimum 3 cycles" is ambiguous — importance 3
Setup step 4 says "this session runs cycle N = revision_cycle + 1"; the header says
stop on plateau, minimum 3, maximum 6. It is unclear whether the skill should loop
cycles in-session until plateau or return after one cycle for a router to re-invoke.
I returned after one. State which is intended.

## 4. Tie-discard gate is too strict for surgical patches — importance 3
Nine integer dimensions give 0.11 granularity and the skill itself states ±0.5
judge variance. Two ch1 attempts that fixed a chronology defect named by BOTH the
adversarial and the baseline judge tied the baseline exactly (7.44, 7.44) and were
discarded; a full-eval top_suggestion clause deletion in ch4 tied 7.89 and was
discarded. Three judge dispatches spent to not-keep fixes the judges asked for.
Suggest: for patches under ~50 words that address a judge-named defect, a tie keeps,
or the gate uses the dimension the fix targeted rather than the mean.

## 5. `protected.md` sourcing pulls sentences from superseded drafting attempts — importance 2
"every entry in three_strongest_sentences from every chapter verdict in eval_logs/"
includes verdicts for attempts that were discarded/superseded (e.g. ch01 attempt 1's
"in a kitchen, behind a chair", which the kept text changed to "in a cold room").
Harmless to apply_cuts.py (no match) but pollutes the file; say "verdicts of kept
attempts" or have the step verify each line exists in the manuscript (I did this by
hand and found one miss).

## 6. Parallel attempts on adjacent chapters: the judge reads the previous chapter from disk — importance 2
The chapter judge reads `chapters/ch_NN-1.md` as it stands on disk. When ch3 and ch4
attempts run concurrently, ch4's judge scores continuity against an uncommitted ch3
attempt that may be discarded. The skill encourages parallel baselines but does not
warn about parallel *attempts* on neighbours. One sentence would do.

## 7. `full-eval` prefix rule forces the label before you know if you'll re-measure — importance 2
Measure step 1 says log the row immediately, then step 2 may trigger a fix and a
re-measure, and "only the FINAL measurement may carry the full-eval prefix". In
practice you log first and relabel later (I had to sed the row). Suggest: log the
full-eval row at the end of Measure, once.

## 8. reader_panel.json consensus shape for `thinnest_character` is undocumented — importance 1
Consensus items are described as "any chapter, character, or scene"; the disagreements
shape requires an integer `chapter`. A character-level consensus (Hoku) has no chapter;
I used `"chapter": null, "character": "Hoku"`. Document the expected shape.

## 9. Judge dispatch failure mode not covered — importance 1
Setup's shared policy covers malformed responses only. One baseline judge died on an
API connection error mid-run (no file written). Re-dispatch worked; say so explicitly
("a dispatch that returns no file is retried once, then logged to skipped.md").

## Not bugs, noted
- `apply_cuts.py` with `--types OVER-EXPLAIN REDUNDANT` only surfaces SKIP [REWRITE]
  lines of those types; FAT/TELL/GENERIC rewrites never appear. Consistent with the
  filter but the "250+ items" warning in the skill implies more will surface than does.
- Pre-splice-audit: three defects from three script cuts on one chapter (double-space ×2,
  glued sentence, trailing whitespace) — the REQUIRED audit earned its place.

---

# Cycle 2 additions (same project, same day)

## 10. Baseline step invites writing patches while judges are still reading the file — importance 5
Fix step 4 says baselines "run concurrently with drafting the first brief, so they cost
wall-clock nothing", and the next paragraph tells you to rewrite in-session. Nothing says
"do not write to `chapters/` until every baseline verdict file exists". Judge subagents
read `chapters/ch_NN.md` one to three minutes into their run, not at dispatch. I wrote
four patches ~2.5 min after dispatching four baselines; the ch03 and ch04 "baselines"
quoted the patched text (found by grepping the verdicts for patch-unique strings), ch02
was unprovable either way, and all three had to be re-baselined on a restored tree
(three extra dispatches, a `git checkout HEAD -- chapters/`, and reclassifying two
verdicts as attempt readings). Without the grep it would have gated two rewrites against
scores of themselves. Fix: an explicit sentence — "draft patches in scratch/attempt
files; copy nothing into chapters/ until the baseline verdict files exist" — and,
ideally, have the dispatch prompt tell the judge to read the chapter first. Same hazard
exists for the previous-chapter read (finding 6).

## 11. Chapter selection for later-cycle cuts keys on a pre-cut fat number — importance 3
"In later cycles, only chapters whose score fell last cycle, or whose last reported
overall_fat_percentage was 12% or higher." The last reported fat is measured BEFORE that
cycle's cuts were applied, so a chapter that was at 13% and then cut gets re-dispatched
next cycle on a stale number by construction (ch02 here: 13% → cut → re-dispatched →
judge now says 9%, returns 11 cuts, 25 words applied). Harmless at this scale but the
criterion can never see the effect of the cut it is trying to avoid repeating. Fix: key
on the fat the *post-cut* judge reports, or on score movement only.

## 12. `apply_cuts.py` SKIP message says "needs replacement text" when the JSON has it — importance 1
For REWRITE cuts the script prints `SKIP [REWRITE] needs replacement text, apply by hand:`
even though the cut's `rewrite` field is populated. The behaviour (never auto-apply
rewrites) is right; the message reads as if the judge failed to supply a rewrite.
Print the rewrite text, or say "REWRITE cuts are applied by hand".

## 13. `gen_brief.py --panel N` pulls other chapters' missing_scene into chapter N's brief — importance 2
ch03's panel brief carried "Add missing beat: Panel identifies a scene gap near this
chapter" quoting the writer persona's ch2 encoder-competence ask (flagged for chapter 2
in disagreements). "Near this chapter" is doing a lot of work; a COMPRESS brief that also
says "add a beat" is self-contradicting. Restrict to items whose `chapter == N`.

## 14. protected.md has no re-verification step after a kept rewrite rewords a line — importance 3
Step 2 says append every cycle, and the Fix rules allow a rewrite to reword a protected
line. Nothing tells you to check, next cycle, that every protected line still occurs in
the manuscript and to re-quote the reworded ones. Two lines from cycle 1 ("There was no
reason on earth to open the phrase table…", "She closed neither.") protected nothing in
cycle 2 until I diffed by hand. One line of instruction (or a `--verify` in apply_cuts
that reports protected lines not found) fixes it. Related to finding 5.

## 15. Tie-discard gate, again (reinforces finding 4) — importance 3
This cycle 4 of 8 judged attempts tied their baseline exactly (ch02 7.67, ch03 7.89 ×2,
plus a prior ch04 tie); two of those were judge-requested edits where the targeted
dimension rose a point and an unrelated one fell. The mean-of-nine gate treats a 1-point
swap as no change. Not re-arguing the fix here; noting the rate.

## 16. "Regenerate arc_summary.md fresh" each cycle is the wrong instruction once a resync exists — importance 2
Diagnose step 1 says regenerate fresh; Measure defines a mechanical resync that is
verbatim-by-construction. When nothing changed since the last resync (start of cycle 2),
regeneration can only add drift. Suggest: "verify with the resync procedure; regenerate
only if the file is missing or fails verification".

## 17. `continuity_check.py` false positives on numbers the fact table states in another form — importance 1
ch02 NOT FOUND: `01:12` (fact table has 01:12 only inside a prose line? it has
"00:40–02:40"/"01:31") and `ninety-eight` (table has "β = 0.98"). Both pre-existing and
benign; the skill's "read NOT FOUND against the fact table" handles it, but a
number-word→digit normaliser would remove the noise.

---

# Cycle 3 additions (same project, same day)

## 18. canon.md "Established In-Story" entries turn eval-requested cuts into canon violations — importance 3
Revision commits update canon.md with per-cycle entries like "Kalei registers, during the
second reading, that her mother stood behind this chair at fourteen (ch_04)". When the next
cycle's full-eval top_suggestion asks for exactly that sentence to be cut, the chapter judge
(told to check canon.md) reports the cut as a "canon drift" violation and can dock
canon_compliance — i.e. the gate penalises the edit the eval asked for. The skill never says
to update canon.md for kept rewrites (prior sessions did it ad hoc), and the judge prompt
does not say in-story entries describe the *previous* state. Fix: either (a) tell the Fix
step to amend canon.md in the same commit as a kept rewrite and tell the judge that
Established-In-Story entries are descriptive of the committed text, not constraints on it,
or (b) keep revision-cycle entries out of canon.md entirely (the chapter is the record).

## 19. "No chapter qualifies for cuts" path has no commit instruction — importance 2
Diagnose step 3's later-cycle filter can select zero chapters (it did here: no score fell,
all fat 6–9%). The resume check greps for `cycle N: adversarial cuts (…)`, but the step
only says "record any chapter you skip in skipped.md". Say explicitly: make the step commit
(`--allow-empty`, "0 words — no chapter qualified") and skip apply_cuts/splice audit, so the
resume check and the word-count trail stay intact.

## 20. "Whose score fell last cycle" is ambiguous under same-cycle baselining — importance 2
With the baseline-first rule a chapter's trajectory within a cycle is kept(N-1) → baseline(N)
→ kept(N). ch03 here went 7.89 → 7.78 → 7.89. Did its score "fall last cycle"? I read it as
no (compare kept to kept) but the text could equally mean baseline vs prior kept, which would
re-dispatch almost every chapter every cycle (baselines reliably come in under the prior
kept score — the skill's own drafting-vs-revision note). State which two numbers to compare.

## 21. Agent completion notifications are not a reliable wake signal; verdict files are — importance 2
In this session no Agent-tool completion notification arrived for any of the 11 judge/panel
dispatches (idle notifications landed ~40 min later, after the cycle was finished), and
`TaskOutput` on the returned agent id reported "No task found". The only reason the cycle
could proceed was that every judge writes its verdict to a named path, so I polled for the
files (`until ls <path>; do sleep 10; done`) and, for the reader panel (which returns JSON
inline rather than writing a file), read the subagents' transcripts by hand. Suggest: have
the reader-panel dispatch write `edit_logs/panel_raw/<persona>.json` like every other judge,
and tell the orchestrator to wait on files, not on the tool's return.

## 22. gen_brief.py --panel attributes non-chapter items to whichever chapter is briefed — importance 2
Extends finding 13. `--panel 4` emitted "Deepen character: Panel flags thin characterization
in this chapter" from a thinnest_character verdict (Ikaika) that names no chapter; `--panel 3`
emitted "Dramatize: break it. Let her get as far as the sum paragraph, have the roster hit at
01:31…" — the genre_reader's ch2 worst_scene fix — as chapter 3's instruction. Both briefs
therefore recommend edits the panel aimed elsewhere. Filter WHAT TO CHANGE to verdicts whose
chapter mention resolves to N; print character-level items under a separate heading.

## 23. Exit step's voice_fingerprint "for the record" writes only to an untracked path — importance 1
`voice_fingerprint.py` saves to `edit_logs/voice_fingerprint.json`, which the default
template gitignores; the `revision complete` commit records nothing. Either print the table
into the commit message / results.tsv, or write to a tracked location.

## Not bugs, noted (cycle 3)
- The panel's 4/4 "cut chapter 2" recurred for the third cycle and was correctly caught by
  the floor clamp (`--panel 2 --chapter-words 1200` → TARGET 629). The guidance works; it
  just costs a gen_brief run per cycle to re-prove.
- Both ch02 judges called the top_suggestion's "She was whoever" cut "arguably right" and
  still scored it tie/below — finding 4/15 (tie gate) again: 2 of 4 attempts this cycle tied
  or lost on edits a judge had asked for.
