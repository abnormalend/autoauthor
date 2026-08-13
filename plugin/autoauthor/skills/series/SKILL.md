---
name: series
description: Use when volumes of a series are drafted and you need the continuity and arc pass — checking that nothing in a later volume contradicts an earlier one and that each volume both advances the series and closes itself.
---

# Series Pass

The cross-volume phase. Sibling of `/autoauthor:collection` and the same
machine pointed the opposite way: a collection checks that its works do
NOT depend on each other, and a series checks that they do — coherently.

Two things no per-volume judge can check, because each reads one volume
with no memory of the others. **Continuity**: nothing in a later volume
contradicts an earlier one. **Arc**: each volume advances the series and
closes itself.

Unlike the collection pass, this one is worth running EARLY and often. A
continuity break found while volume 3 is still an outline costs an
afternoon; found after it is drafted, it costs the volume.

## Setup

1. Verify the project: the current working directory must contain
   `state.json` with `"structure": "series"`, a `bible/` holding at least
   `voice.md`, `canon.md` and `arc.md`, and `works/`. Clean tree — if
   `git status --porcelain` is non-empty, STOP and ask.
2. **Resolve.** Run from the container directory:

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/resolve_genre.py"
   ```

   Keep the JSON. `structure.works` is the volume order, and
   `structure.order_is_editorial` is false — for a series the order is a
   fact about the story, not a choice. Never reorder volumes as a fix.
3. Read each volume's `state.json` for its phase, and its own `canon.md`.
   Run this with volumes unwritten; say which, and judge what exists.

## Step 1 — The mechanical pass

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/convergence.py"
```

**Read the output inverted from how a collection reads it.** It writes
`edit_logs/convergence.json` with an `interpretation` block that says so,
and the number that matters here is `divergent_works` — the volumes that
read unlike their neighbours. Convergence itself is the goal in a series,
not a defect: this is one continuous work in volumes.

A volume in `divergent_works` is either a shift the series earned — a new
POV, a time skip, a different narrator — or a drift nobody noticed. Only
reading it tells you which, and the judge is asked to say.

## Step 2 — The judge

Dispatch a fresh judge subagent (general-purpose, no drafting context):

  "Read the rubric at `<plugin>/shared/rubrics/series-pass.md` and the
  genre pack(s) at `<resolved pack paths, primary first, each labeled with
  its role>`, and follow the rubric exactly. The form is `<form.name>` at
  `<form.path>`. The series project is `<absolute path>`. The volumes, in
  order, are `<structure.works>`; each volume's prose is in
  `works/<name>/chapters/` and its local canon in `works/<name>/canon.md`.
  Read `bible/canon.md` and `bible/arc.md` first — they are the spine.
  Read `edit_logs/convergence.json` if it exists. Return ONLY the JSON
  object the rubric specifies."

Save the JSON verbatim to `eval_logs/<UTC yyyymmdd_hhmmss>_series.json`.
Fenced but valid JSON is valid — strip the fences. One strict retry on
genuinely malformed output, then stop rather than inventing a score.

## Step 3 — Contradictions first, score second

`contradictions` is the most valuable thing the judge returns, and it is
worth more than the number beside it. Work it before anything else:

1. For each contradiction, decide which side is right. **Default to the
   EARLIER volume** — it is published, or it is closer to being, and a
   reader has already been told. Change the later one.
2. Where the earlier volume is genuinely wrong, fix it there and say so
   loudly; that is a real revision of a real book, not a bookkeeping edit.
3. Apply `promote_to_series_canon`: move facts a later volume depends on
   up into `bible/canon.md`. A fact recorded only in an earlier volume's
   local canon is a fact the next volume will contradict, because the next
   volume's author reads the bible.

Then run the loop: `series_score > 7.0` exits. Otherwise take
`weakest_dimension` and fix it where it lives —

- `canon_integrity`, `canon_promotion` → `bible/canon.md` and the volume
  that strayed.
- `volume_closure`, `arc_progression` → the volume, and sometimes
  `bible/arc.md`, if what the series wanted was never written down.
- `entry_and_recap`, `character_continuity`, `series_voice` → the volume.

Never the running order. Reordering a series is not a fix; it is a
different series.

Commit each kept iteration: `series: <dimension> <old> -> <new>`. Append
to `results.tsv` with `series_score` in the score column.

## Step 4 — Record

Update `state.json`: `series_score`, and `phase` to `export` when the pass
clears and every volume is done. Commit.

## What this pass is not

It does not re-grade prose or plot. Every volume was judged on its own
merits by a judge with the room to do it properly. A finding here has to
be a statement about the SERIES — "volume 2 establishes the ward takes
three days and volume 3 has her raise one overnight", never "volume 2's
middle sags".
