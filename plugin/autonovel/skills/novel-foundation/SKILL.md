---
name: novel-foundation
description: Use when a novel project is in the foundation phase, or the user asks to build or improve the novel's world bible, characters, outline, voice, mystery, or canon before drafting begins.
---

# Novel Foundation — Phase 1

Builds the five planning layers and iterates until
`foundation_score > 7.5 AND lore_score > 7.0`. No prose chapters are
written in this phase. Typical runs take 5–15 iterations.

## Setup

1. Verify the project: the current working directory must contain
   `state.json` and `voice.md`; `git status --porcelain` must be empty
   (if dirty, STOP and ask the user before touching anything). Confirm
   `state.json` phase is `foundation` — if it's later, ask before
   re-running foundation. Use absolute paths everywhere.
2. Required reading, in full, before writing anything:
   - `"${CLAUDE_PLUGIN_ROOT}/shared/craft/CRAFT.md"`
   - `"${CLAUDE_PLUGIN_ROOT}/shared/craft/ANTI-SLOP.md"`
   - the project's `voice.md` Part 1 (guardrails)
   - `references/layer-guides.md` (in this skill's directory)
   - the project's `seed.txt` if present; otherwise derive the premise
     from whatever layer docs already exist (imported or hand-built
     projects are valid — never require seed.txt).

## Filling empty layers

Fill the layers IN THIS ORDER, following the matching section of
layer-guides.md for each: voice discovery (from seed.txt — trial
passages against the seed's world concept; voice.md Part 2 +
voice_wells.json) → world.md → characters.md → MYSTERY.md →
outline.md part 1 → foreshadowing ledger (outline.md part 2) →
canon.md. Every hard fact added to any layer gets a canon.md entry at
the same time. Commit once: `foundation: initial layers`.

If some layers already contain real content (an interrupted run, or
an imported project), do not refill them — fill only the still-
template layers, in the same order, then proceed to the iteration
loop.

## Iteration loop

1. **Evaluate.** Dispatch a fresh judge subagent (general-purpose,
   no drafting context) with exactly this prompt shape:
   "Read the rubric at `<absolute plugin path>/shared/rubrics/foundation.md`
   and follow it exactly. The project directory is `<absolute project
   path>`. The input files are: voice.md, world.md, characters.md,
   outline.md, canon.md (all in the project directory). Return ONLY the
   JSON object the rubric specifies."
   Save the returned JSON verbatim to
   `eval_logs/<UTC yyyymmdd_hhmmss>_foundation.json`.
   Fence-wrapped but otherwise valid JSON is VALID — strip the fences,
   don't waste the retry on a formatting technicality. If the response
   genuinely is not valid JSON, re-dispatch once with a stricter
   reminder; if still invalid, log the iteration as unscored in
   results.tsv (`keep_discard=noscore`) and continue.
   The results.tsv score column takes `overall_score`; put
   `lore_score` in the description (e.g. `iter N: <dimension> (lore
   <lore_score>)`).
2. **Gate check.** `overall_score > 7.5` AND `lore_score > 7.0` → exit
   the loop.
3. **Target the weakest dimension.** The eval names `weakest_dimension`
   and `top_3_improvements`. Revise THAT layer's document. While
   revising, run the cross-layer consistency checks: the outline
   references only lore that exists in world.md; character abilities
   match the magic rules; the foreshadowing ledger balances (every
   plant has a payoff); canon.md captures all new facts.
4. **Keep/discard.** Score improved over the best previous score (or
   first scored iteration) → `git add -A && git commit -m "foundation
   iter <N>: <weakest_dimension> (<score>)"`. After every KEPT
   iteration, update `foundation_score`, `lore_score`, and `iteration:
   <N>` in state.json to the new best values (this is what makes the
   run resumable — the router reads `iteration`). A
   resuming session takes "best previous score" from state.json,
   cross-checking the last `keep` row in results.tsv. Score regressed
   → discard with `git reset --hard HEAD` (resets tracked files,
   staged and unstaged, back to the last kept iteration; untracked
   files like the new eval log survive, which is what we want — the
   eval record is kept even for discarded iterations). Either way
   append to results.tsv:
   `<ISO timestamp>\tfoundation\t<score>\t0\t<keep|discard|noscore>\t<one line>`.
5. **Iteration cap.** After 15 iterations without passing the gate,
   STOP. Report the best score, the stubborn dimension, and options
   (accept and move on / keep iterating / revise the seed).

## Fight the Stability Trap (hard rules, from the original program)

Characters must end truly different from how they began. Let bad things
stay bad. Allow irreversible decisions and irreversible loss. Withhold
information from the reader — maintain mystery. Create genuine moral
ambiguity: the "right" choice should be unclear. If a choice has no
real cost, it is not a real choice. Resist rounding sharp edges into
something safer.

## Exit

Set state.json: `phase: "drafting"`, `chapters_total: <chapter count
from outline.md>`, `iteration: 0`, and record the final scores. Commit
`foundation complete: <overall>/<lore>`. Send a Pushover notification
(pushover skill): title "autonovel: foundation", message with final
scores, iterations used, and next step `/autonovel:novel-draft`. Then
report the same to the user.
