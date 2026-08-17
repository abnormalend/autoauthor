---
name: foundation
description: Use when a novel project is in the foundation phase, or the user asks to build or improve the novel's world bible, characters, outline, voice, mystery, or canon before drafting begins.
---

# Novel Foundation — Phase 1

Builds the planning layers the work's form calls for and iterates until
both scores clear that form's gate — `foundation_score > 7.5 AND
pillar_score > 7.0` for a novel. No prose chapters are written in this
phase. Typical runs take 5–15 iterations.

## Setup

1. Verify the project: the current working directory must contain
   `state.json` and `voice.md`; `git status --porcelain` must be empty
   (if dirty, STOP and ask the user before touching anything). Confirm
   `state.json` phase is `foundation` — if it's later, ask before
   re-running foundation. Use absolute paths everywhere.
2. **Resolve the genre and form.** Run from the project directory:

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/resolve_genre.py"
   ```

   If it exits non-zero, STOP and report — an unresolvable or conflicting
   genre stack must be fixed before any layer work. Keep the reported pack
   paths; every judge dispatch below needs them. Keep the `form` block
   too: `form.layers` is which layers to build, `form.gate` is what the
   loop exits on, and `form.band` is which length-scoped section of a
   genre pack applies. If `state.json` has no
   `genre` field at all, or its `genre` is null, STOP and run the migration
   in `novel/SKILL.md` first — a null genre resolves silently to `general`,
   so the resolver exiting 0 is NOT evidence that anyone chose a genre.
3. Required reading, in full, before writing anything:
   - `"${CLAUDE_PLUGIN_ROOT}/shared/craft/CRAFT.md"`
   - `"${CLAUDE_PLUGIN_ROOT}/shared/craft/ANTI-SLOP.md"`
   - the project's `voice.md` Part 1 (guardrails)
   - `references/layer-guides.md` (in this skill's directory)
   - every genre pack path reported by
     `python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/resolve_genre.py"`
   - the project's `seed.txt` if present; otherwise derive the premise
     from whatever layer docs already exist (imported or hand-built
     projects are valid — never require seed.txt).
4. If `chapters/` already contains prose (imported project), the
   manuscript is ground truth: layer revisions during iteration must
   document and deepen what the prose establishes — never contradict
   it. Cite chapters as `(ch_NN)` in canon entries you add.

## Filling empty layers

Fill ONLY the layers `form.layers` names, in this order, skipping any the
form does not call for: voice discovery (from seed.txt — trial passages
against the seed's world concept; voice.md Part 2 + voice_wells.json) →
world.md → characters.md → MYSTERY.md → outline.md part 1 →
foreshadowing ledger (outline.md part 2) → canon.md. Follow the matching
section of layer-guides.md for each, and read the form pack's
`## Foundation Guidance` first — layer-guides.md is written at novel
scale, and the form says what each layer means at this length. A layer
the form does not name is not a gap: building it anyway spends the work's
budget on apparatus its length cannot earn. Every hard fact added to any
layer gets a canon.md entry at the same time, where the form calls for
canon. Commit once: `foundation: initial layers`.

If some layers already contain real content (an interrupted run, or
an imported project), do not refill them — fill only the still-
template layers, in the same order, then proceed to the iteration
loop.

Exception: an outline.md containing a `TO BE OUTLINED` marker counts
as unfilled for the outline pass — fill ONLY the marked
remaining-chapters portion (keep the as-written entries for existing
chapters untouched).

## Iteration loop

1. **Evaluate.** Dispatch a fresh judge subagent (general-purpose,
   no drafting context) with exactly this prompt shape:
   "Read the rubric at `<absolute plugin path>/shared/rubrics/foundation.md`
   and the genre pack(s) at `<resolved pack paths, primary first, each
   labeled with its role>`, and follow the rubric exactly. The form is
   `<form.name>` at `<form.path>` and its band is `<form.band>`. The base
   dimensions file is `<base_dimensions.path>`; score exactly these keys,
   by category: `<base_dimensions.scored as reported, verbatim>`. The
   project directory is `<absolute project path>`. The input files are:
   `<the documents form.layers calls for, named>`. Return ONLY the JSON
   object the rubric specifies."

   Every angle-bracketed value comes from the resolver output kept in
   Setup step 2. Pass `base_dimensions.scored` through verbatim — do not
   summarize it, and do not substitute the eight you remember, which is
   the whole failure this parameterization exists to prevent.
   Save the returned JSON verbatim to
   `eval_logs/<UTC yyyymmdd_hhmmss>_foundation.json`.
   Fence-wrapped but otherwise valid JSON is VALID — strip the fences,
   don't waste the retry on a formatting technicality. If the response
   genuinely is not valid JSON, re-dispatch once with a stricter
   reminder; if still invalid, log the iteration as unscored in
   results.tsv (`keep_discard=noscore`) and continue.
   The results.tsv score column takes `overall_score`; put
   `pillar_score` in the description (e.g. `iter N: <dimension> (pillar
   <pillar_score>)`).
2. **Gate check.** `overall_score > form.gate.overall` AND `pillar_score >
   form.gate.pillar` → exit the loop. Both numbers come from the resolver's
   `form` block, never from memory; for the `novel` form they are 7.5 and
   7.0. They are the form's because they are length economics — the bar is
   this high on the reasoning that a weak plan costs the drafting loop far
   more than it costs to plan again, and that reasoning does not survive a
   translation to five thousand words.

   **A fired cap overrides a cleared gate.** The gate is a floor on a
   weighted mean, and a mean lets a capped dimension through whenever
   the other categories are strong. One run cleared 6.5/6.0 on its first
   scored iteration at 7.45/7.00 while `internal_consistency` sat on its
   cap at 4 with five listed contradictions — including the clock the
   whole second half runs on, stated three different ways — and
   `register_plausibility` sat on its cap at 6. Exiting there ships a
   plan that stops a drafter mid-scene. So: if any scored dimension's
   note says its cap fired, or the eval's contradictions list names a
   contradiction in a fact table, an outline beat, quoted in-story
   text, or a character fact, do NOT exit — run at least one more
   iteration targeting that dimension, then re-check. Caps are how the
   packs refuse a book something; the gate does not overrule them.
3. **Target the weakest dimension.** The eval names `weakest_dimension`
   and `top_3_improvements`. Revise THAT layer's document. While
   revising, run the cross-layer consistency checks: the outline
   references only lore that exists in world.md; character capabilities
   match the rules the pack's pillar dimensions govern; every genre
   artifact the pack declares is filled and current; the foreshadowing
   ledger balances (every plant has a payoff); canon.md captures all new
   facts.
3b. **Record the title if the work has acquired one.** A story usually
   names itself while its outline is being built, and that name tends to
   end up only in a document heading. Write it to `state.json`'s `title`
   the moment it exists. Export reads it from there; a title living in a
   markdown heading is lost the first time the document is regenerated,
   and a title nobody recorded gets asked for at export and answered
   differently than the one the plan used.

4. **Keep/discard.** Score improved over the best previous score (or
   first scored iteration) → `git add -A && git commit -m "foundation
   iter <N>: <weakest_dimension> (<score>)"`. After every KEPT
   iteration, update `foundation_score`, `pillar_score`, and `iteration:
   <N>` in state.json to the new best values (this is what makes the
   run resumable — the router reads `iteration`). A
   resuming session takes "best previous score" from state.json,
   cross-checking the last `keep` row in results.tsv.
   If the project's genre changed since the last scored iteration (compare
   `genre`/`genre_secondary`/`genre_modifiers` against the most recent
   `genre-change` marker row in results.tsv), do NOT compare against the old
   best score — the weights differ, so the numbers are not comparable.
   Treat the next scored iteration as the first one.
   Score regressed
   → discard with `git reset --hard HEAD` (resets tracked files,
   staged and unstaged, back to the last kept iteration; untracked
   files like the new eval log survive, which is what we want — the
   eval record is kept even for discarded iterations). Either way
   append to results.tsv:
   `<ISO timestamp>\tfoundation\t<score>\t0\t<keep|discard|noscore>\t<one line>`.
5. **Iteration cap.** After 15 iterations without passing the gate,
   STOP. Report the best score, the stubborn dimension, and options
   (accept and move on / keep iterating / revise the seed).

   **Compute the score; do not take the judge's word for it.**

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/score_verdict.py" \
       eval_logs/<the file you just saved> \
       --weights '<the primary pack's weights object>'
   ```

   It averages the dimension scores and compares that to the aggregate
   the judge reported. **Record the computed number.** A judge is
   qualified to score a dimension and has no particular claim to
   averaging seven of them: a live cycle returned dimensions averaging
   7.43 alongside `work_score: 7`, against a phase that stops when that
   number moves by less than 0.5. Exit 1 means they disagreed; the
   message names the value to use.


## Fight the Stability Trap (hard rules, from the original program)

Characters must end truly different from how they began. Let bad things
stay bad. Allow irreversible decisions and irreversible loss. Withhold
information from the reader — maintain mystery. Create genuine moral
ambiguity: the "right" choice should be unclear. If a choice has no
real cost, it is not a real choice. Resist rounding sharp edges into
something safer.

## Exit

Do not exit while outline.md still contains a `TO BE OUTLINED`
marker — the outline pass must complete first, regardless of scores.

Do not exit while any loaded pack's `## Genre Contract` is unsatisfiable by
the outline — the judge reports these under `genre_contract.violations`.
Fix the outline first.

Set state.json: `chapters_total: <chapter count from outline.md>`,
`iteration: 0`, and record the final scores. Set `phase`: if every
outlined chapter already exists in `chapters/` (imported finished
manuscript), set `"revision"`; otherwise set `"drafting"`. Commit
`foundation complete: <overall>/<pillar>`. Send a Pushover notification
(pushover skill): title "autoauthor: foundation", message with final
scores, iterations used, and next step `/autoauthor:draft` (or
`/autoauthor:revise` when exiting to revision). Then report the
same to the user.
