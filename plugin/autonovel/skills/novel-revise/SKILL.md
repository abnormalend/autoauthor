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
   Then verify no chapter fell below 1800 words
   (`wc -w chapters/ch_*.md`). If one did, restore it with
   `git checkout HEAD -- chapters/ch_NN.md` and exclude it from cuts
   this cycle. Run the slop scorer over the touched chapters as a
   sanity check. Commit `cycle N: adversarial cuts (<words removed>
   words)`.
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

### Fix (consensus items, priority order per the playbook)

For each consensus item, in playbook priority order (cut candidate →
missing scene → thin character → weak scene → consistency):
1. Generate a brief:
   `python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/gen_brief.py" --panel <ch>`
   (or `--cuts <ch>`; use `--eval <ch>` once this cycle's chapter
   evals exist). Review the brief; sharpen it by hand if the playbook
   recipe for this item type demands specifics the script missed.
2. Rewrite the chapter in-session following the brief plus the
   playbook's Rewrite rules, with the drafting context recipe
   (voice.md, world.md, characters.md in full; the old chapter as raw
   material — keep what works; previous chapter's last ~1000 words;
   next chapter's opening ~1500 chars).
3. Score it exactly as novel-draft does: scratch copy to
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

1. Refresh arc_summary.md entries for rewritten chapters AND
   recompute the header line's total word count (`wc -w
   chapters/ch_*.md | tail -1`); use that same fresh total in the
   results.tsv row. Dispatch the full-novel judge: "Read the rubric at
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

## Optional cycle-1 diagnostic: chapter tournament

If the user asks for deeper diagnosis (or cuts and panel disagree about
the weakest chapters), run head-to-head comparisons: dispatch judge
subagents given two chapter files each, asked only "Read both chapters.
Which is the stronger chapter and why — one paragraph, then a final
line WINNER: <NN>." Seed pairings from adjacent per-chapter scores.
Rankings inform which chapters get briefs first. Skip by default.
