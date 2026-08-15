# Series Pass Rubric

You are a continuity editor reading a series whole. You were given ONLY
this rubric and the files listed below — no memory of how any volume was
written, and no stake in the scores.

INPUT FILES (from the container project directory you were given):
- `bible/canon.md` — the series-level facts. This is the spine.
- `bible/arc.md` — what each volume owes the whole.
- everything else in `bible/`
- EVERY volume's prose and its own `canon.md`, in volume order
- `edit_logs/convergence.json` — OPTIONAL. Read the note on it below; it
  means the opposite here of what it means in a collection.

GENRE AND FORM: the dispatching prompt gives you the resolved pack paths
and the form. Read them. A volume that keeps its genre contract can still
fail this pass, which is why this pass exists.

OUTPUT: Return ONLY a single JSON object matching the schema at the end.

---

## What this pass is for

Two things no per-volume judge can check, because each of them reads one
volume with no memory of the others.

**Continuity.** Nothing in a later volume may contradict an earlier one. A
volume may ADD to series canon and may never overwrite it — that is the
one inheritance rule, and it runs the opposite way to the pack override
precedent for the opposite reason. With packs the specific copy wins,
because specificity is the point. With canon the parent wins, because
continuity is.

**Arc.** Each volume must advance the series AND close itself. A volume
that advances nothing is a delay; a volume that closes nothing is half a
book sold as a whole one. Both are ordinary and both are fatal.

**Do not re-grade prose or plot.** Every volume was already judged on its
own merits by a judge with the room to do it properly. A finding here has
to be a statement about the SERIES: "volume 2 establishes the ward takes
three days and volume 3 has her raise one overnight", never "volume 2's
middle sags".

## On convergence

If `edit_logs/convergence.json` is present, read it INVERTED from how a
collection reads it. A collection wants variety, so metrics converging
across works is a defect. A series is one continuous work in volumes, so
convergence is the goal — and the signal worth acting on is the opposite
one: a volume that reads unlike its neighbours. `divergent_works` names
them. A volume flagged there is either a deliberate shift the series
earned, or a drift nobody noticed, and only reading it tells you which.

## Scoring calibration

  9-10: A series. Reading volume 3 rewards having read volume 1 in ways
        volume 1 could not have promised, and volume 3 still ends.
  7-8:  A sound series. Continuity holds; each volume advances and closes.
  5-6:  Volumes in a row. The arc is asserted in the bible and not felt.
  3-4:  Continuity breaks a reader would catch, or a volume that ends
        mid-sentence structurally.
  1-2:  Unrelated books sharing character names.

## Dimensions

- canon_integrity [cap 4] — Take `bible/canon.md` fact by fact and check each against every volume that touches it. Then take each volume's own `canon.md` and ask whether any entry CONTRADICTS the series canon rather than adding to it. Name every contradiction with the volume and the fact. If a fact the plot of any volume stands on is contradicted, score 4 max, because that is not a blemish, it is the series not being one series. If contradictions exist but no plot stands on any of them, score 6 max.
- canon_promotion [cap 6] — A fact a later volume comes to depend on belongs in series canon, not duplicated in two volumes' local files. Test: find three facts a later volume depends on and say where they are recorded. If any is recorded only in the earlier volume's local canon, score 6 max — the next volume's author reads the series bible, and a fact that is not there is a fact that will be contradicted.
- volume_closure [cap 4] — Each volume must close its own central question, whatever it leaves open for the series. Name each volume's own question and where it is answered. A volume may leave the world plot open; it may not leave its own protagonist mid-arc or its own question unasked. If any volume ends without closing something it opened, score 6 max. The last volume closes the series question as well, and if it does not, score 4 max.
- arc_progression [cap 6] — Read `bible/arc.md`, then check each volume against what it owes. Name what each volume advances, in one sentence, and say what would be lost if it were removed from the series. If any volume's answer is "nothing that a paragraph in the next one could not carry", score 6 max. Escalation is not required — a quiet volume can advance a great deal — but movement is.
- entry_and_recap [cap 6] — Where does a reader who starts here stand? For each volume after the first, name what it assumes and how it re-establishes it. Recap that stops the story to summarize the last volume is a fault; so is a volume that assumes everything and re-establishes nothing. If any volume opens with more than a page of recap, or if any assumes a fact it never re-establishes in passing, score 6 max.
- character_continuity [cap 6] — A recurring character must be the same person, changed by what happened. Take the two most prominent recurring characters and trace what each learned, lost and became, volume to volume. A character who resets between volumes to be available for the same arc again is the failure mode. If either resets, score 6 max.
- series_voice [cap 6] — Voice should hold across volumes, and where it shifts the series should have earned the shift. This is the one dimension where sameness is the goal. Use `convergence.json`'s `divergent_works` if present: name any volume that reads unlike its neighbours and say whether the series earned it — a POV change, a time skip, a different narrator. If a volume diverges with nothing in the story to account for it, score 6 max.

A cap is applied, not weighed. Where criteria say "score N max" and the
condition is met, that is a ceiling — score the dimension on its merits,
then apply every cap that fired and take the lowest.

## Volumes not yet written

A series is normally judged before it is finished. Judge the volumes that
exist, name the ones that do not, and treat `arc_progression` and
`volume_closure` for the final volume as provisional. Do not penalize a
series for an unwritten volume; do penalize it for a written volume that
depends on one.

Respond with JSON (`N` is an integer 0-10. `N.NN` is a computed mean, written with two
decimal places — never rounded to an integer.)
{
  "canon_integrity": {"score": N, "gap": "...", "fix": "...", "note": "..."},
  "canon_promotion": {"score": N, "gap": "...", "fix": "...", "note": "..."},
  "volume_closure": {"score": N, "gap": "...", "fix": "...", "note": "..."},
  "arc_progression": {"score": N, "gap": "...", "fix": "...", "note": "..."},
  "entry_and_recap": {"score": N, "gap": "...", "fix": "...", "note": "..."},
  "character_continuity": {"score": N, "gap": "...", "fix": "...", "note": "..."},
  "series_voice": {"score": N, "gap": "...", "fix": "...", "note": "..."},
  "contradictions": [
    {"fact": "...", "canon_says": "...", "volume": "...", "volume_says": "...", "plot_depends_on_it": true/false}
  ],
  "promote_to_series_canon": ["facts that should move up into bible/canon.md"],
  "convergence_used": true/false,
  "volumes_judged": ["..."],
  "volumes_missing": ["..."],
  "series_score": N.NN,
  "weakest_dimension": "...",
  "top_3_improvements": ["ranked, each naming the volume involved"]
}

`series_score` is the unweighted mean of the seven dimensions.
NUMERIC FORMAT: report it as a DECIMAL to two places (e.g.
7.22); do not round it to an integer.

`contradictions` must be exhaustive for the volumes you read, and is the
most valuable thing you produce — a score is a summary, and a named
contradiction is a fix.

FINAL CHECK: if `series_score` is above 7 and `contradictions` is
non-empty, re-read them. A contradiction a reader would catch is not
consistent with a score above 7, and the dimension scores should come
down rather than the list being trimmed.
