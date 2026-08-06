---
name: novel
description: Use when the user asks where their novel stands, wants to resume novel work, says "continue the novel", asks what pipeline phase is next, or wants a status report on an autonovel project.
---

# Novel — Pipeline Status and Router

Read-only. This skill NEVER modifies project files, commits, or resets.

## Steps

1. **Locate the project.** The project is the current working directory
   if it contains `state.json` and `voice.md`. If not, say this isn't a
   novel project and offer: start one with `/autonovel:novel-seed`, or
   have the user `cd` to (or name) an existing project. `seed.txt` is
   OPTIONAL — projects imported or hand-built without one are valid.

2. **Gather state** (read, don't infer):
   - `state.json` — phase, iteration, scores, revision_cycle,
     review_round, debts
   - last 15 lines of `results.tsv`
   - `git log --oneline -10` and `git status --porcelain`
   - chapter count and total words across `chapters/ch_*.md`
   - newest files in `eval_logs/`, `edit_logs/`, `briefs/`

3. **Report** in a short table + prose: current phase and iteration;
   scores against their gates (foundation > 7.5 AND lore > 7.0;
   chapters > 6.0; revision plateau Δ < 0.5 across 2 cycles); chapters
   drafted vs planned; pending debts from state.json; and a WARNING if
   the git tree is dirty (uncommitted work from an interrupted run —
   the user should inspect before any phase skill runs).

4. **Recommend exactly one next action:**
   - phase `foundation` → `/autonovel:novel-foundation`
   - phase `drafting`  → `/autonovel:novel-draft`
   - phase `revision`  → `/autonovel:novel-revise`; but if
     `revision_cycle >= 3` and the last two full-novel scores in
     results.tsv (rows whose description starts with `full-eval`)
     differ by < 0.5 → `/autonovel:novel-review`
   - phase `review`    → `/autonovel:novel-review`
   - phase `export`    → `/autonovel:novel-export`
   - phase `done`      → congratulate; point at the PDF/ePub outputs.

   If `state.json` has an unrecognized phase value, say so and list the
   valid phases instead of guessing.
