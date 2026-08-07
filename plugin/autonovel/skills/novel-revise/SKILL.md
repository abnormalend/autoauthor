---
name: novel-revise
description: Use when a novel project is in the revision phase, or the user asks to revise the draft, tighten chapters, run the reader panel, or apply adversarial edits.
---

# Novel Revise — Phase 3a

Revision cycles: diagnose (cuts + panel) → fix (briefs + rewrites) →
measure (full-novel score). Stop on plateau: full-novel score change
< 0.5 across 2 consecutive cycles, minimum 3 cycles, maximum 6.

## Setup

1. Verify the project (state.json + voice.md present), clean tree
   (dirty → STOP and ask), phase `revision`. Anchor the session in the
   project directory; absolute paths when in doubt.
2. Required reading: `"${CLAUDE_PLUGIN_ROOT}/shared/craft/ANTI-PATTERNS.md"`,
   the project's voice.md, and `references/revision-playbook.md` (this
   skill's directory).
3. Resume: state.json `revision_cycle` is the last COMPLETED cycle;
   this session runs cycle N = revision_cycle + 1.
4. **Malformed judge responses (applies everywhere in this skill):**
   fence-wrapped but otherwise valid JSON is VALID — strip the fences;
   for genuinely malformed output, one strict retry, then skip that
   dispatch and record it in
   `edit_logs/skipped.md` with the cycle, step, and chapter.

## One cycle (N)

**Resume check:** inspect `git log --oneline -20` for this cycle's
step commits (`cycle N: arc summary`, `cycle N: adversarial cuts
(…)`, `cycle N: reader panel`). Skip any Diagnose step whose commit
already exists — NEVER re-run the adversarial-edit + apply-cuts pair
for a cycle that already applied cuts; cutting twice compounds and
can gut chapters.

### Diagnose

1. **arc_summary.md** — regenerate it fresh: first line
   `Novel: <total words> words across <count> chapters.`, then per
   chapter: a 4–6 sentence event summary, the opening and closing
   ~100-word passages, and 1–2 key dialogue exchanges. Commit
   `cycle N: arc summary`.
2. **Adversarial edit** — for EACH chapter, dispatch a fresh judge
   subagent: "Read the rubric at
   `<absolute plugin path>/shared/rubrics/adversarial-edit.md` and
   follow it exactly. The project directory is `<absolute project
   path>`. The target chapter file is `<absolute path to
   chapters/ch_NN.md>`. Return ONLY the JSON the rubric specifies."
   Save each response verbatim to `edit_logs/chNN_cuts.json` (exact
   filename — apply_cuts.py globs it). Dispatch in parallel batches
   of 4–6 (malformed responses: see Setup's shared policy).
3. **Apply mechanical cuts:**
   `python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/apply_cuts.py" all --types OVER-EXPLAIN REDUNDANT --min-fat 15`
   Review its FAIL lines; apply any high-value failed cuts by hand.
   Also handle its SKIP [REWRITE] lines: apply each rewrite by hand
   using the `rewrite` text from the chapter's cuts JSON — those cuts
   need replacement prose, not deletion.
   **If the run reports `Applied: 0` because every chapter fell under
   `--min-fat 15`,** that is expected on a draft that already had a
   post-draft slop pass (judges typically return 7–12% fat there). Do
   not accept the empty result and do not raise the fat numbers: re-run
   the same command with `--min-fat 0`, which keeps the type filter and
   drops only the gate. Say so in the commit message.
   **Then audit for splice damage — REQUIRED, and not optional because
   the word counts look fine.** The script deletes quoted spans
   mid-paragraph, so a cut that removes a trailing or interior sentence
   can leave a paragraph ending on a comma, ending with no terminal
   punctuation at all, or two speeches glued into one line. Neither the
   word-count check nor the slop scorer detects any of this. Diff each
   changed paragraph against the pre-cut tree and flag any that now end
   in `[,;]`, end without terminal punctuation, contain a double space,
   or contain adjacent/empty quote pairs (`" "`, `""`). Repair each by
   hand against the pre-cut text — usually promoting a comma to a
   period or restoring a paragraph break. Re-run the audit until it
   reports zero.
   Then verify no chapter fell below 1800 words
   (`wc -w chapters/ch_*.md`). If one did, restore it with
   `git checkout HEAD -- chapters/ch_NN.md` and exclude it from cuts
   this cycle. Run the slop scorer over the touched chapters as a
   sanity check.
   **Finally, resync arc_summary.md** (see the resync procedure under
   Measure). This step just edited most of the manuscript, and the file
   built in step 1 now quotes sentences that no longer exist in the
   book — the reader panel in step 4 and the full-novel judge in
   Measure both read it. Commit `cycle N: adversarial cuts (<words
   removed> words)`.
4. **Reader panel** — dispatch FOUR judge subagents in parallel, one
   per persona: "Read the rubric at `<absolute plugin
   path>/shared/rubrics/reader-panel.md` and follow it exactly. Your
   assigned persona is <editor|genre_reader|writer|first_reader>. The
   project directory is `<absolute project path>`; the input file is
   arc_summary.md. Return ONLY the JSON the rubric specifies."
   Assemble `edit_logs/reader_panel.json` as:
   `{"readers": {"editor": {...}, "genre_reader": {...}, "writer":
   {...}, "first_reader": {...}}, "consensus": [...],
   "disagreements": [...]}` — consensus = any chapter, character, or
   scene named by 3+ readers for the same question; disagreements use
   the exact shape gen_brief.py consumes: `{"question": "<question
   key>", "chapter": <integer N>, "flagged_by": ["<personas>"],
   "not_flagged": ["<personas>"]}` — `chapter` MUST be a JSON integer,
   not a string, because gen_brief.py matches on int equality. Commit
   `cycle N: reader panel`.

   **What the panel is and isn't evidence of.** All four readers see
   arc_summary.md and never the prose. Their verdicts are therefore
   claims about the *summary*, and the summary is lossy in one
   direction: it compresses dramatized scenes into clauses. So a
   chapter whose strength is texture, restraint, or slow accumulation
   reads to the panel as drag, and a scene the summary renders in six
   words reads as missing. Expect two recurring false positives —
   "missing scene" for a beat that is fully on the page, and "cut
   candidate" for a chapter that is merely quiet. Both can carry 3+
   reader agreement, because all four are misled by the same lossy
   line. Treat a `cut_candidate` verdict as a hypothesis about
   REPETITION, not about length. Verification is mandatory before any
   brief (Fix step 1).
   If `edit_logs/` is gitignored (the default template), the panel and
   cuts JSON are untracked; make the step commit with
   `--allow-empty` so the resume check still finds it.

### Fix (consensus items, priority order per the playbook)

For each consensus item, in playbook priority order (cut candidate →
missing scene → thin character → weak scene → consistency):
1. **Verify the item against the chapter text before briefing
   anything.** Open the chapter (and the outline entry) and confirm the
   defect is on the page. Panel consensus is not evidence that it is —
   the readers saw only arc_summary.md, so an item can carry 3-of-4
   agreement and still be an artifact of one compressed summary line.
   Check the specific claim:
   - *missing scene* → grep the chapter for the beat. If it is already
     dramatized, the summary was lossy, not the chapter. Do not rewrite.
   - *cut candidate* → find what actually repeats. Compare the chapter's
     closing move against its neighbours' closing moves; a real cut
     candidate repeats a beat or a posture, and the fix is to break the
     repetition, which is rarely the same edit as making it shorter.
   - *thin character* → count their actual lines and scenes.
   - any item → check the outline entry, which may already require the
     thing the panel wants added, or forbid it by design.
   If the item does not survive this check, skip it, record it in
   `edit_logs/skipped.md` with what you verified and where, and move to
   the next item. Rewriting a chapter to add a scene it already
   contains costs it its score and gains nothing.
2. Generate a brief:
   `python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/gen_brief.py" --panel <ch>`
   (or `--cuts <ch>`; use `--eval <ch>` once this cycle's chapter
   evals exist). Review the brief; sharpen it by hand if the playbook
   recipe for this item type demands specifics the script missed.
   **Check the brief's TARGET before using it.** A COMPRESS brief sets
   the target at 55% of current length, which on a chapter already near
   the floor asks for a word count the 1800-word guardrail forbids
   (2,400 → 1,320). The guardrail wins; override the number by hand.
3. Rewrite the chapter in-session following the brief plus the
   playbook's Rewrite rules, with the drafting context recipe
   (voice.md, world.md, characters.md in full; the old chapter as raw
   material — keep what works; previous chapter's last ~1000 words;
   next chapter's opening ~1500 chars). Before cutting any element,
   grep the rest of the manuscript for it: a compression brief that
   removes a plant (an object, a card, a named regular) silently breaks
   its payoff chapters later.
4. Score it exactly as novel-draft does: scratch copy to
   `eval_logs/ch_NN_attempt_<k>.md`, slop score, chapter-judge
   dispatch (labeled target/previous paths, per chapter.md's
   contract), final score = judge minus slop penalty. Keep if the
   final score beats the chapter's previous score (from the latest
   eval log; if no valid prior eval exists for the chapter — imported
   project or noscore history — use the drafting gate 6.0 as the
   baseline); else discard (`git reset --hard HEAD`), max 3 attempts
   per chapter per cycle. After 3 failed attempts, leave the chapter
   as-is this cycle and record the item in `edit_logs/skipped.md`.
   Attempt rows go to `eval_logs/attempts.tsv` and fold into
   results.tsv at commit (same columns as novel-draft's rows, but the
   phase column is `revision`). Commit kept rewrites:
   `cycle N: <item type> ch NN (<score>)`.

### Measure

1. **Resync arc_summary.md, then dispatch.** The full-novel judge
   scores the novel from this file alone, so a stale line here is a
   wrong score for the whole cycle.

   **Resync procedure** (used here and at the end of Diagnose step 3;
   run it over EVERY chapter changed since the file was written — cuts
   and by-hand repairs, not just rewritten chapters):
   - Rebuild each changed chapter's opening and closing ~100-word
     passages mechanically from the current chapter text, so they are
     verbatim by construction rather than by transcription.
   - Recompute every per-chapter word count in the `## Chapter NN`
     headers and the header line's total (`wc -w chapters/ch_*.md |
     tail -1`); use that same fresh total in the results.tsv row.
   - Re-verify every remaining quoted line (the key-dialogue
     exchanges): whitespace-normalise both sides and confirm each quote
     still occurs in its chapter. For any that no longer match, locate
     the longest surviving prefix and replace the quote with the
     current paragraph containing it.
   - Repeat until zero quoted passages fail the check. Do not hand a
     summary containing invented or deleted prose to a judge.

   Dispatch the full-novel judge: "Read the rubric at
   `<absolute plugin path>/shared/rubrics/full-novel.md` and follow it
   exactly. The project directory is `<absolute project path>`. The
   input files are voice.md, world.md, characters.md, outline.md,
   arc_summary.md. Return ONLY the JSON the rubric specifies." Save to
   `eval_logs/<UTC yyyymmdd_hhmmss>_full.json`. Log to results.tsv:
   `<ISO timestamp>\trevision\t<novel_score>\t<total words>\tkeep\tfull-eval cycle N`
   (the `full-eval` description prefix is a contract — the router's
   plateau check greps for it).
2. Address the eval's `top_suggestion` if actionable this cycle (the
   playbook's eval-callout patterns have the recipes); at most 2 such
   fixes per cycle, scored and gated like any rewrite.
3. Update state.json: `revision_cycle: N`, `novel_score`. Commit
   `cycle N complete (<score>)`.
4. **Plateau check.** If N >= 3 and the last three `full-eval` scores
   in results.tsv show |score(N) − score(N−1)| < 0.5 AND
   |score(N−1) − score(N−2)| < 0.5 → stop. Also stop at N = 6
   regardless.

## Exit

Set state.json `phase: "review"`. Run
`python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/voice_fingerprint.py"`
for the record. Commit `revision complete: <cycles> cycles
(<final score>)`. Pushover notification (pushover skill): title
"autonovel: revision", message with cycles run, score trajectory, next
step `/autonovel:novel-review`. Report the same to the user.

## Guardrails (from the playbook — non-negotiable)

Never compress a chapter below 1800 words. Expect rewrites to run ~30%
long — brief for shorter than you want. If the full-novel eval names a
NEW weakest chapter twice in a row after fixes, stop chasing it.

Never brief a rewrite off a panel consensus item you have not confirmed
in the chapter text. The four readers share one lossy input, so they
share its errors; agreement measures legibility in summary, not truth.

Never hand arc_summary.md to a judge without re-verifying that every
passage it quotes still occurs in the manuscript. It is the sole input
to the reader panel and the full-novel judge, and any step that edits
chapters invalidates it.

Cut narration, not scenes. A compression that summarizes a dramatized
beat scores worse than the bloat it replaced.

## Optional cycle-1 diagnostic: chapter tournament

If the user asks for deeper diagnosis (or cuts and panel disagree about
the weakest chapters), run head-to-head comparisons: dispatch judge
subagents given two chapter files each, asked only "Read both chapters.
Which is the stronger chapter and why — one paragraph, then a final
line WINNER: <NN>." Seed pairings from adjacent per-chapter scores.
Rankings inform which chapters get briefs first. Skip by default.
