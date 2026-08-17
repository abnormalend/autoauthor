---
name: draft
description: Use when a novel project is in the drafting phase, or the user asks to draft chapters, write the first draft, or continue writing the novel's prose.
---

# Novel Draft — Phase 2

Writes chapters in outline order. Keep at score > 6.0 (after slop
penalty) and canon clean, max 5 attempts per chapter. Forward progress over perfection:
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
   `chapters/ch_NN.md` + 1. First chapter of a fresh project is 1 —
   subject to the reconciliation in step 7, which overrides it.
5. **Build the input-file list from the form.** The resolver's
   `form.layers` names which planning documents exist. Map them through
   `LAYER_FILES` in `form_pack.py` (`voice` → voice.md, `world` →
   world.md, `characters` → characters.md, `mystery` → MYSTERY.md,
   `outline`/`foreshadowing` → outline.md, `canon` → canon.md). That
   list, plus canon.md, is what every judge dispatch below names as
   "the other input files" and what the per-chapter loop's step 1
   loads. Do not name the novel's five files by habit: at `short-story`
   there is no world.md, and a judge told to read one spends its tool
   calls hunting for it.
6. **Ensure `canon.md` exists.** Compressed forms do not build a canon
   layer in foundation, but drafting establishes facts on the page that
   the chapter judge checks later chapters against. If `canon.md` is
   missing, create it now from
   `"${CLAUDE_PLUGIN_ROOT}/shared/templates/canon.md"` with the primary
   pack's `## Canon Categories` as its section headings, and commit
   `draft: canon.md scaffold`.
7. **Reconcile state against history.** Compare `state.json`'s
   `chapters_drafted` with the files in `chapters/` AND with
   `git log --oneline | grep -cE '^[0-9a-f]+ (draft: ch|revision complete|cycle [0-9]+ complete)'`.
   If history records drafting or revision work the working tree does
   not reflect (a `revision complete` commit above an empty
   `chapters/`, say), STOP and report the discrepancy — do not infer
   the resume point from the empty directory. One session drafted an
   entire story from scratch on top of a repository whose HEAD was
   `revision complete: 3 cycles`; every check the skill named passed.

## Per-chapter loop (repeat through state.json chapters_total)

1. **Load context — exactly this, fresh each chapter:**
   - every layer file the form builds (Setup step 5), in full, except
     outline.md — voice.md and characters.md always; world.md and
     MYSTERY.md where the form built them; canon.md is read for the
     facts already established, not in full — grep it for the names
     and objects this chapter touches
   - from outline.md: THIS chapter's entry (including its Plants list)
     AND every section that precedes the first chapter entry — the
     structure, the fact table, the clock, the register contract, the
     foreshadowing table. Those sections are what prevent the arithmetic
     and clock errors that were the dominant defect class on one run
     (eight of them across four chapters, every one derivable from the
     outline's fact table). At `form.band == "compressed"` load
     outline.md whole; at that length it costs less than the chapter it
     is used to write.
   - the previous chapter's last ~1000 words (skip for chapter 1)
   - the NEXT chapter's outline entry, first ~10 lines (for
     continuity; skip for the final chapter)
2. **Write `chapters/ch_NN.md`** — the complete chapter. The default word
   target is the resolved pack's `shape.chapter_words`; where this
   chapter's outline entry states its own target, that wins (it is
   per-chapter, and so the more specific of the two). Follow
   every rule in drafting-rules.md. Title line: `# Chapter N: <Title>`.
3. **Mechanical score:**

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/slop_score.py" \
       chapters/ch_NN.md \
       --genre-pack <primary pack path> --form-pack <form.path>
   ```

   Both paths come from the resolver output kept in Setup. Pass them every
   time: the genre pack carries this genre's own banned diction, and the
   form's band sets the figurative density threshold — a compressed form
   cannot afford the ornament budget a novel can. Without them the scan
   falls back to the general lists and the novel-length threshold, silently.

   Then, in the same breath:

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/continuity_check.py" chapters/ch_NN.md
   ```

   It lists every clock time and number the chapter states and whether
   any fact-bearing document (outline, canon, world, characters —
   whichever exist) states it too. Read the NOT FOUND list against the
   outline's fact table before dispatching the judge. FOUND means the
   value occurs somewhere in a fact document, not that it is the right
   value here — the NOT FOUND list is where to look first, not the only
   place. Most entries will
   be harmless inventions; the ones that are not are the cheapest
   defects you will ever fix — six of eight canon violations on one run
   were single-word edits, and every one of them survived into a later
   phase because nothing looked. Fix what is wrong, re-run both scripts,
   then judge.

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
   other input files are `<the layer files the resolved form builds,
   named — see Setup step 5>` and canon.md in the project directory.
   Write the JSON object the rubric specifies — bare JSON, no fences —
   to `<absolute project path>/eval_logs/<UTC yyyymmdd_hhmmss>_chNN.json`
   and return only that path and the `overall_score` value."

   Compute the UTC timestamp yourself before dispatching; the path in
   the prompt is literal, and it is the path you will hand to
   score_verdict.py. The judge writes the file; you do not transcribe
   it. A run that re-typed four ~1,500-word verdicts by hand put a
   lossy step between the measurement and the artifact
   `score_verdict.py` certifies — the check was validating the
   orchestrator's copy, not the judge's. If the file is missing or is
   not valid JSON, that is a malformed response: one strict retry, then
   `noscore`. Rename an unparseable judge file to `<name>.bad` before
   retrying — gen_brief.py reads the newest eval file with a bare
   json.loads and a garbage file there breaks a later brief.
   **Compute the score; do not take the judge's word for it.**

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/score_verdict.py" \
       eval_logs/<the path the judge returned>
   ```

   It averages the dimension scores and compares that to the
   `overall_score` the judge reported. **Record the computed number.** A
   judge is qualified to score a dimension and has no particular claim to
   averaging nine of them — a live drafting run returned four chapters
   whose dimensions averaged 7.22, 7.33, 7.22 and 7.00, every one of them
   reported as 7.0. Exit 1 means they disagreed; the message names the
   value to use.

   The filename is `<UTC yyyymmdd_hhmmss>_chNN.json` with NN zero-padded
   — gen_brief.py globs this pattern. If the judge fenced the JSON
   anyway, strip the fences in place; that is a formatting technicality,
   not a malformed response. A `noscore` attempt counts as a failed
   attempt: discard and retry, same as a below-gate score.
5. **Final score** = judge `overall_score` minus the script's
   `slop_penalty` (floor 0). This mirrors the original pipeline's
   independent mechanical adjustment.
6. **Gate.** Keep requires BOTH: final score > 6.0 AND the judge's
   `canon_compliance.violations` list is empty (or `canon_compliance`
   scored 7 or higher) — if kept with violations listed, log each as a
   debt (step 7). A canon violation is unlike a weak sentence: it
   is cheap now, it compounds (a wrong line in ch1 forced ch2 to write
   around it on one run, and the judge discounted ch2's version as a
   repeat), and it is invisible to revision, whose instruments cut and
   compress and read a wrong number as perfectly good prose.

   **If the chapter fails ONLY on canon** — score clears, violations
   listed — do not discard. Take the surgical-correction branch: apply
   edits that address the named violations and nothing else, re-run
   step 3, re-dispatch the judge, and log the attempt row as `correct`
   rather than `keep`/`discard`. A correction counts against the
   5-attempt budget so it cannot loop. Cost is one edit pass and one
   dispatch, against a debt that otherwise waits for a phase that will
   not see it.

   Score clears and canon clean → keep: update state.json
   `chapters_drafted`, fold in the attempt rows (fix 2), then
   `git add -A && git commit -m "draft: ch NN (<final score>)"`.
   Otherwise discard with `git reset --hard HEAD` (untracked eval logs
   survive) and retry with a DIFFERENT approach informed by the
   judge's three_weakest_sentences and top_3_revisions — up to 5
   attempts. After 5 failed attempts, keep the best-scoring canon-clean
   attempt; if none is clean, keep the best score and log each listed
   violation as a state.json debt (step 7 format) — the `correct`
   branch is unavailable once the budget is spent. Then
   `cp eval_logs/ch_NN_attempt_<best>.md chapters/ch_NN.md`,
   commit, and log `keep (best-of-5)`.
   Append EVERY attempt's row to the untracked `eval_logs/attempts.tsv`
   (same columns as results.tsv) — including the first, whether or not
   it passes; a chapter that clears on attempt 1 has one row there and
   one in results.tsv. At commit
   time (keep or best-of-5), append ALL of this chapter's attempt rows
   from eval_logs/attempts.tsv into results.tsv, then
   `git add -A && git commit` — the full experiment log lands
   atomically with the kept chapter. Row format:
   `<ISO timestamp>\tdrafting\t<final score>\t<chapter word count>\t<keep|discard|correct|noscore>\tch NN attempt <k>`
7. **Canon.** Append the judge's `new_canon_entries` to canon.md
   (created in Setup step 6 if the form did not build one), each
   tagged `(ch_NN)`. If writing revealed a lore gap or contradiction,
   log a debt in state.json:
   `{"trigger": "ch_NN: <gap>", "affected": ["<files>"], "status": "pending"}`.

## Post-draft cleanup (after the last chapter)

1. Slop pass over everything:

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/slop_score.py" \
       chapters/ch_*.md \
       --genre-pack <primary pack path> --form-pack <form.path>
   ```

   Fix every tier-1 hit and any chapter with penalty > 2.0 by surgical
   word/sentence edits only — no rewrites.

   A chapter over its `figurative_threshold` is fixed by DELETION, not by
   rewriting figures into different figures. Take the ones that fail the
   detachability test in ANTI-SLOP.md — delete the figure, and if the
   sentence loses nothing it was ornament — and cut those first. The count
   is the fault; swapping one simile for another leaves it where it was.

   Commit `post-draft slop pass`. If the pass made no edits (zero hits,
   clean tree), report the clean result and skip the commit — `git
   commit` with nothing staged exits non-zero, and a literal reading
   ended one run's phase on a failed command.
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
