# autoauthor:foundation — skill findings

Date: 2026-08-19
Project: ~/novels/redshift (*Her Years, Our Years*, short story, SF + YA)
Plugin: autoauthor 0.18.0
Run: 4 scored iterations (cap), scores 7.69 / 7.69 / 8.23 / 7.51; gate 6.5/6.0 cleared every pass; cap fired.

Issues and bugs only. Importance: HIGH / MEDIUM / LOW.

## 1. HIGH — Forced-iteration rule on any named contradiction makes the gate unreachable at short-story cap
Iteration loop step 2 forces another iteration whenever `contradictions_found` names anything in binding text, regardless of severity. Every judge listed new *minor* items ("seven-thirty" vs "19:50"; a question mark on one line) while the score sat 7.7–8.2 against a 6.5 gate. With `iteration_cap: 4` and normal judge variance the loop could never exit cleanly; the cap was guaranteed to fire.
Suggest: force only on MAJOR-flagged contradictions or fired caps; minor ones go on the next iteration's fix list but do not block exit.

## 2. HIGH — Keep/discard regression rule has no case for a pre-existing fault surfaced late
Iter 4 dropped 0.72 because the judge found a MAJOR contradiction (allowance priced as a fixed 1,200-character field *and* as a byte-priced codebook) that also existed in the kept state. The rule says "discard only when the targeted dimension did not improve"; it did not (8→6), so the letter of the rule says discard — which would restore the four faults just fixed and keep the major one. Had to deviate and document it.
Suggest: add "if the new contradictions also exist in the kept state, the regression is discovery, not damage — keep and target."

## 3. MEDIUM — Observed judge variance dwarfs the ±0.15 tie band
Iter 3→4 changed a handful of lines and moved −0.72; iter 1→2 changed a lot and moved 0.00. Keep/discard decisions at 0.15 granularity on a single judge are mostly noise.
Suggest: two judges (or a second judge on any regression > 0.5) before keep/discard, or a wider tie band per form.

## 4. MEDIUM — layer-guides.md and forms/short-story.md disagree on the ledger
The form drops `foreshadowing_balance` ("a story that plants and pays within four pages does not keep one"); layer-guides says a short story "owes one or two" tracked threads with a plant-in-scene-1 / pay-in-scene-4 rule. Harmless in practice, but a contradiction in the guidance itself.

## 5. LOW — layer-guides' character section applies pack Cast Requirements unconditionally
"Build the registry with the roles listed in the pack's Cast Requirements" — the SF pack demands seven roles including an antagonist with a face; the form says only the characters who appear. The form wins implicitly, but the guide should say so. Effort spent pre-empting a cast-requirement objection was then flagged by a judge as prose addressed to the evaluator.

## 6. LOW — At cap, the skill does not say what state.json should hold
It says report options, but not whether `chapters_total` gets set or whether `foundation_score` should be last-kept (7.51) or best (8.23). Set chapters_total and last-kept; one line would settle it.

## Not bugs
- `resolve_genre.py` and `score_verdict.py` behaved exactly as documented.
- Setup step 3b (seed arithmetic check) earned its place: it caught the per-ship-year vs per-Earth-year window ambiguity and the "six hours" that was really four.
