---
name: draft
description: Use when a novel project is in the drafting phase, or the user asks to draft chapters, write the first draft, or continue writing the novel's prose.
---

# Novel Draft — Phase 2

Writes chapters in outline order. Keep at score > 6.0 (after slop
penalty), max 5 attempts per chapter. Forward progress over perfection:
a 6.0 ships; revision is Phase 3's job.

## Setup

1. Verify the project (state.json + voice.md in the current directory),
   clean tree (`git status --porcelain` empty — if dirty, STOP and ask),
   and `state.json` phase `drafting`. Anchor the session in the
   verified project directory; use absolute paths whenever there is
   any doubt about the current directory.
2. **Resolve the genre.** Run from the project directory:

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/resolve_genre.py"
   ```

   If it exits non-zero, STOP and report — an unresolvable or conflicting
   genre stack must be fixed before any drafting work. Keep the reported
   pack paths; every judge dispatch below needs them. If `state.json` has no
   `genre` field at all, or its `genre` is null, STOP and run the migration
   in `novel/SKILL.md` first — a null genre resolves silently to `general`,
   so the resolver exiting 0 is NOT evidence that anyone chose a genre.
3. Required reading before the first chapter of the session:
   - `"${CLAUDE_PLUGIN_ROOT}/shared/craft/CRAFT.md"`
   - `"${CLAUDE_PLUGIN_ROOT}/shared/craft/ANTI-SLOP.md"`
   - `"${CLAUDE_PLUGIN_ROOT}/shared/craft/ANTI-PATTERNS.md"`
   - the project's `voice.md` (both parts)
   - `references/drafting-rules.md` (in this skill's directory)
   - every genre pack path reported by
     `python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/resolve_genre.py"`
4. Resume point: next chapter = highest N among existing
   `chapters/ch_NN.md` + 1. First chapter of a fresh project is 1.

## Per-chapter loop (repeat through state.json chapters_total)

1. **Load context — exactly this, fresh each chapter:**
   - voice.md (full), world.md (full), characters.md (full)
   - THIS chapter's outline entry from outline.md (including its
     Plants list)
   - the previous chapter's last ~1000 words (skip for chapter 1)
   - the NEXT chapter's outline entry, first ~10 lines (for
     continuity; skip for the final chapter)
2. **Write `chapters/ch_NN.md`** — the complete chapter. The default word
   target is the resolved pack's `shape.chapter_words`; where this
   chapter's outline entry states its own target, that wins (it is
   per-chapter, and so the more specific of the two). Follow
   every rule in drafting-rules.md. Title line: `# Chapter N: <Title>`.
3. **Mechanical score:**
   `python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/slop_score.py" chapters/ch_NN.md`
   Note the `slop_penalty`. Copy the attempt to an untracked scratch
   file before judging: `cp chapters/ch_NN.md eval_logs/ch_NN_attempt_<k>.md`
   — eval_logs/ is untracked, so attempts survive discards.
4. **Judge.** Dispatch a fresh judge subagent (general-purpose, no
   drafting context) with exactly this prompt shape:
   "Read the rubric at `<absolute plugin path>/shared/rubrics/chapter.md`
   and the genre pack(s) at `<resolved pack paths, primary first, each
   labeled with its role>`, and follow the rubric exactly. The project
   directory is `<absolute project
   path>`. The target chapter is chapter <N>; its file is
   `<absolute path to chapters/ch_NN.md>`. The previous chapter file is
   `<absolute path to ch_(N-1)>` (omit this line for chapter 1). The
   other input files are voice.md, world.md, characters.md, canon.md,
   outline.md in the project directory. Return ONLY the JSON object the
   rubric specifies."
   **Compute the score; do not take the judge's word for it.**

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/score_verdict.py" \
       eval_logs/<the file you just saved>
   ```

   It averages the dimension scores and compares that to the
   `overall_score` the judge reported. **Record the computed number.** A
   judge is qualified to score a dimension and has no particular claim to
   averaging nine of them — a live drafting run returned four chapters
   whose dimensions averaged 7.22, 7.33, 7.22 and 7.00, every one of them
   reported as 7.0. Exit 1 means they disagreed; the message names the
   value to use.

   Save the JSON to `eval_logs/<UTC yyyymmdd_hhmmss>_chNN.json` (NN
   zero-padded — gen_brief.py globs this pattern). Fence-wrapped but
   otherwise valid JSON is VALID — strip the fences. Malformed JSON →
   one strict retry → else record `noscore` and move on. A `noscore`
   attempt counts as a failed attempt: discard and retry, same as a
   below-gate score.
5. **Final score** = judge `overall_score` minus the script's
   `slop_penalty` (floor 0). This mirrors the original pipeline's
   independent mechanical adjustment.
6. **Gate.** Final score > 6.0 → keep: update state.json
   `chapters_drafted`, fold in the attempt rows (fix 2), then
   `git add -A && git commit -m "draft: ch NN (<final score>)"`.
   Otherwise discard with `git reset --hard HEAD` (untracked eval logs
   survive) and retry with a DIFFERENT approach informed by the
   judge's three_weakest_sentences and top_3_revisions — up to 5
   attempts. After 5 failed attempts, keep the best-scoring attempt:
   `cp eval_logs/ch_NN_attempt_<best>.md chapters/ch_NN.md`, then
   commit, and log `keep (best-of-5)`.
   During the retry loop, append each attempt's row to the untracked
   `eval_logs/attempts.tsv` (same columns as results.tsv). At commit
   time (keep or best-of-5), append ALL of this chapter's attempt rows
   from eval_logs/attempts.tsv into results.tsv, then
   `git add -A && git commit` — the full experiment log lands
   atomically with the kept chapter. Row format:
   `<ISO timestamp>\tdrafting\t<final score>\t<chapter word count>\t<keep|discard|noscore>\tch NN attempt <k>`
7. **Canon.** Append the judge's `new_canon_entries` to canon.md,
   each tagged `(ch_NN)`. If writing revealed a lore gap or
   contradiction, log a debt in state.json:
   `{"trigger": "ch_NN: <gap>", "affected": ["<files>"], "status": "pending"}`.

## Post-draft cleanup (after the last chapter)

1. Slop pass over everything:
   `python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/slop_score.py" chapters/ch_*.md`
   Fix every tier-1 hit and any chapter with penalty > 2.0 by surgical
   word/sentence edits only — no rewrites. Commit `post-draft slop pass`.
2. Set state.json `phase: "revision"`. Commit.
3. Pushover notification (pushover skill): title "autoauthor: drafting",
   message with chapters drafted, mean/min final scores, total words,
   next step `/autoauthor:revise`. Then report the same to the
   user.

## Session-length note

Drafting 20+ chapters exceeds one session. After EVERY chapter commit
the project is resumable: a fresh session in the project directory
runs this skill and picks up at the resume point. Prefer stopping
cleanly at a chapter boundary over drafting into a degraded context.
