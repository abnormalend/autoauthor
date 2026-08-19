---
name: status
description: Use when the user asks where their book stands, wants to resume work, says "continue the novel" or "continue the story", asks what pipeline phase is next, or wants a status report on an autoauthor project.
model: haiku
effort: low
---

# Status — Pipeline Status and Router

Read-only, with exactly one exception: the genre migration in step 3,
which runs only on a project that predates genre packs and only after the
user confirms. This skill never commits, never resets, and never modifies
anything else.

## Steps

1. **Locate the project.** The project is the current working directory
   if it contains `state.json` and `voice.md`. If not, say this isn't a
   novel project and offer: start one with `/autoauthor:seed`, or
   have the user `cd` to (or name) an existing project. `seed.txt` is
   OPTIONAL — projects imported or hand-built without one are valid.

2. **Gather state** (read, don't infer):
   - `state.json` — phase, iteration, scores, revision_cycle,
     review_round, debts
   - last 15 lines of `results.tsv`
   - `git log --oneline -10` and `git status --porcelain`
   - **and reconcile them:** search the full log (`git log --oneline |
     grep -E 'draft: ch|cycle [0-9]+ complete|revision complete'`) for
     the markers; if it shows `draft: ch`, `cycle N complete` or
     `revision complete` commits but `state.json` says
     `chapters_drafted: 0` or `chapters/` is empty, report that as the
     headline — the state file and the repository disagree, and the
     next skill will otherwise redo work that already exists in
     history.
   - chapter count and total words across `chapters/ch_*.md`
   - newest files in `eval_logs/`, `edit_logs/`, `briefs/`
   - the resolved genre: run
     `python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/resolve_genre.py"` and
     report `label_parts` and each pack's role. If it exits non-zero,
     report the error and stop — the only writing this skill does is the
     step 3 migration, and a project that fails to resolve needs a human
     decision, not a repair.

3. **Migration check.** If `state.json` has no `genre` key, or its `genre`
   is null, this project predates genre packs. Report that and offer the
   migration — do NOT apply it silently, and do NOT let it default.

   The resolver exits 0 on such a project (null and missing both resolve
   to `general`), so a clean resolve is not evidence that anyone chose a
   genre. That is exactly why this check reads `state.json` directly.

   - Suggest `fantasy`, because that is what the project's existing scores
     in `results.tsv` were produced under. Say plainly that choosing
     anything else changes the rubric's category weights and its pillar
     dimensions, which makes the new scores incomparable to the old ones.
   - On the user's confirmation, add `genre`, `genre_secondary: null`, and
     `genre_modifiers: []` to `state.json`, and rename any `lore_score`
     key to `pillar_score` in place. Change nothing else. Do not commit —
     tell the user what changed and let them review it.
   - If the project has scored history in `results.tsv` AND the chosen
     genre is anything other than `fantasy`, also append a marker row:
     `<ISO timestamp>\t<phase>\t0\t0\tgenre-change\tgenre set to <name>; score baseline reset`
     `foundation` reads the most recent `genre-change` row to decide
     whether the previous best score is still a valid comparison. Without
     it, the next iteration is measured against a number produced under
     different weights and will look like a regression.

   **Second, independent check — the 0.4.0 rename.** If `state.json` has a
   `novel_score` key, the project predates the autonovel → autoauthor
   rename. This is separate from the genre check above and fires on its
   own: a 0.3.x project has a `genre` already and still carries the old
   key. Rename `novel_score` to `work_score` in place, change nothing
   else, and tell the user. Nothing else in a project directory carries
   the old name — chapter files, `results.tsv`, `canon.md` and the rest
   are all name-agnostic — so this one key is the whole migration.

   The same marker row and baseline reset apply any time a project's genre
   changes later, not only at migration.

4. **Report** in a short table + prose: current phase and iteration; the
   resolved genre (primary, secondary, and modifiers with their roles);
   scores against their gates (foundation > 7.5 AND pillar > 7.0;
   chapters > 6.0; revision plateau Δ < 0.5 across 2 cycles); chapters
   drafted vs planned; pending debts from state.json; and a WARNING if
   the git tree is dirty (uncommitted work from an interrupted run —
   the user should inspect before any phase skill runs).

4b. **If this is a container** (`structure.is_container` is true), the
   report is about the collection, not about a work. Give the running
   order from `structure.works`, each work's own phase and score read
   from its `state.json`, and `collection_score` against its 7.0 gate.
   Then recommend against the EARLIEST unfinished work rather than the
   container: a collection whose third story is undrafted needs that
   story drafted, and the collection pass cannot tell you anything until
   most of them exist. Name the work directory in the recommendation so
   the user knows where to `cd`.

   The container itself has two phases of its own: `export`, and the
   cross-work pass, which is `/autoauthor:collection` for a collection and
   `/autoauthor:series` for a series. They are the same machine pointed
   opposite ways — a collection checks that its works do NOT depend on
   each other, a series checks that they do without contradicting.

   For a SERIES, say so when recommending: the cross-work pass is worth
   running early and often, because a continuity break found while a later
   volume is still an outline costs an afternoon and the same break found
   after it is drafted costs the volume. Do not wait for every volume to
   be done the way a collection does.

5. **Recommend exactly one next action** (for a standalone project, or
   for the work the step above named):
   - phase `foundation` → `/autoauthor:foundation`
   - phase `drafting`  → `/autoauthor:draft`
   - phase `revision`  → `/autoauthor:revise`; but if
     `revision_cycle >= 3` and the last THREE full-novel scores in
     results.tsv (rows whose description starts with `full-eval`)
     show BOTH consecutive deltas < 0.5 (|score(N) − score(N−1)| < 0.5
     AND |score(N−1) − score(N−2)| < 0.5) → `/autoauthor:review`
   - phase `review`    → `/autoauthor:review`
   - phase `export`    → `/autoauthor:export`
   - phase `done`      → congratulate; point at the PDF/ePub outputs.

   If `state.json` has an unrecognized phase value, say so and list the
   valid phases instead of guessing.
