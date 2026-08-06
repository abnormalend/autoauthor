---
name: novel-draft
description: Use when a novel project is in the drafting phase, or the user asks to draft chapters, write the first draft, or continue writing the novel's prose.
---

# Novel Draft — Phase 2

Writes chapters in outline order. Keep at score > 6.0 (after slop
penalty), max 5 attempts per chapter. Forward progress over perfection:
a 6.0 ships; revision is Phase 3's job.

## Setup

1. Verify the project (state.json + voice.md in the current directory),
   clean tree (`git status --porcelain` empty — if dirty, STOP and ask),
   and `state.json` phase `drafting`. Use absolute paths everywhere.
2. Required reading before the first chapter of the session:
   - `"${CLAUDE_PLUGIN_ROOT}/shared/craft/CRAFT.md"`
   - `"${CLAUDE_PLUGIN_ROOT}/shared/craft/ANTI-SLOP.md"`
   - `"${CLAUDE_PLUGIN_ROOT}/shared/craft/ANTI-PATTERNS.md"`
   - the project's `voice.md` (both parts)
   - `references/drafting-rules.md` (in this skill's directory)
3. Resume point: next chapter = highest N among existing
   `chapters/ch_NN.md` + 1. First chapter of a fresh project is 1.

## Per-chapter loop (repeat through state.json chapters_total)

1. **Load context — exactly this, fresh each chapter:**
   - voice.md (full), world.md (full), characters.md (full)
   - THIS chapter's outline entry from outline.md (including its
     Plants list)
   - the previous chapter's last ~1000 words (skip for chapter 1)
   - the NEXT chapter's outline entry, first ~10 lines (for
     continuity; skip for the final chapter)
2. **Write `chapters/ch_NN.md`** — the complete chapter, target
   ~3,200 words (or the outline entry's stated target), following
   every rule in drafting-rules.md. Title line: `# Chapter N: <Title>`.
3. **Mechanical score:**
   `python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/slop_score.py" chapters/ch_NN.md`
   Note the `slop_penalty`.
4. **Judge.** Dispatch a fresh judge subagent (general-purpose, no
   drafting context) with exactly this prompt shape:
   "Read the rubric at `<absolute plugin path>/shared/rubrics/chapter.md`
   and follow it exactly. The project directory is `<absolute project
   path>`. The target chapter is chapter <N>; its file is
   `<absolute path to chapters/ch_NN.md>`. The previous chapter file is
   `<absolute path to ch_(N-1)>` (omit this line for chapter 1). The
   other input files are voice.md, world.md, characters.md, canon.md,
   outline.md in the project directory. Return ONLY the JSON object the
   rubric specifies."
   Save the JSON to `eval_logs/<UTC yyyymmdd_hhmmss>_chNN.json` (NN
   zero-padded — gen_brief.py globs this pattern). Malformed JSON →
   one strict retry → else record `noscore` and move on.
5. **Final score** = judge `overall_score` minus the script's
   `slop_penalty` (floor 0). This mirrors the original pipeline's
   independent mechanical adjustment.
6. **Gate.** Final score > 6.0 → keep: `git add -A && git commit -m
   "draft: ch NN (<final score>)"`; update state.json
   `chapters_drafted`. Otherwise discard with `git reset --hard HEAD`
   (untracked eval logs survive) and retry with a DIFFERENT approach
   informed by the judge's three_weakest_sentences and
   top_3_revisions — up to 5 attempts. After 5 failed attempts, keep
   the best-scoring attempt anyway (rewrite it from the saved eval
   logs if needed), commit it, and log `keep (best-of-5)`.
   Every attempt appends to results.tsv:
   `<ISO timestamp>\tdrafting\t<final score>\t<chapter word count>\t<keep|discard|noscore>\tch NN attempt <k>`
7. **Canon.** Append the judge's `new_canon_entries` to canon.md,
   each tagged `[ch NN]`. If writing revealed a lore gap or
   contradiction, log a debt in state.json:
   `{"trigger": "ch_NN: <gap>", "affected": ["<files>"], "status": "pending"}`.

## Post-draft cleanup (after the last chapter)

1. Slop pass over everything:
   `python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/slop_score.py" chapters/ch_*.md`
   Fix every tier-1 hit and any chapter with penalty > 2.0 by surgical
   word/sentence edits only — no rewrites. Commit `post-draft slop pass`.
2. Set state.json `phase: "revision"`. Commit.
3. Pushover notification (pushover skill): title "autonovel: drafting",
   message with chapters drafted, mean/min final scores, total words,
   next step `/autonovel:novel-revise`. Then report the same to the
   user.

## Session-length note

Drafting 20+ chapters exceeds one session. After EVERY chapter commit
the project is resumable: a fresh session in the project directory
runs this skill and picks up at the resume point. Prefer stopping
cleanly at a chapter boundary over drafting into a degraded context.
