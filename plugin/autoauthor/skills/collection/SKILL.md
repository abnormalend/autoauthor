---
name: collection
description: Use when every work in a collection is drafted and revised, or the user asks to check a collection for repetition and variety, set the running order, or run the cross-work pass before export.
---

# Collection Pass

The only phase that sees every work at once, and the one thing a
collection needs that a standalone work never did. Runs after the works
are drafted and revised, before export.

Every other judge in this pipeline reads exactly one work with no memory
of the others — that clean-room isolation is what makes their verdicts
worth anything, and it is exactly what makes them blind to convergence.
N works written to one voice document by one author will drift toward each
other, and no judge that reads one of them can tell.

## Setup

1. Verify the project: the current working directory must contain
   `state.json` with `"structure": "collection"`, a `bible/` directory,
   and `works/`. `git status --porcelain` must be empty — if dirty, STOP
   and ask before touching anything. Use absolute paths throughout.
2. **Resolve.** Run from the container directory:

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/resolve_genre.py"
   ```

   Keep the JSON. `structure.works` is the declared running order and
   `structure.is_container` must be true; the pack paths, `form`, and
   `base_dimensions` are needed for the dispatch below. If it exits
   non-zero, STOP and report — a container whose running order disagrees
   with what is on disk cannot be assembled, and that is what it will be
   telling you.
3. Read each work's `state.json` and note its phase. You may run this pass
   with works still undrafted; say so up front and treat the result as
   provisional. Two works cannot converge, so below three drafted works
   the repetition and range findings are not worth much.

## Step 1 — The mechanical pass

Run BEFORE dispatching the judge. It measures what an instrument measures
better than a reader does, and the judge takes it as an accelerant rather
than a precondition.

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/convergence.py"
```

This writes `edit_logs/convergence.json`: per-work prose metrics and the
coefficient of variation for each across the collection. High variance is
healthy — the works are doing different things. `converged_metrics` is the
list worth acting on; `converged_scale_metrics` is expected, because the
form set one target length for every work, and a judge sent hunting for
prose repetition on the strength of a converged `word_count` is being sent
after nothing.

Then the slop scanner across the collection, which catches vocabulary
sameness the CV cannot:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/slop_score.py" works/*/chapters/*.md
```

## Step 2 — The judge

Dispatch a fresh judge subagent (general-purpose, no drafting context)
with exactly this prompt shape:

  "Read the rubric at `<plugin>/shared/rubrics/collection-pass.md` and the
  genre pack(s) at `<resolved pack paths, primary first, each labeled with
  its role>`, and follow the rubric exactly. The form is `<form.name>` at
  `<form.path>`. The container project is `<absolute path>`. The works, in
  the declared running order, are `<structure.works>`; each work's prose is
  in `works/<name>/chapters/`. Read everything in `bible/` — `binding.md` first,
  and `edit_logs/convergence.json` if it exists. Return ONLY the JSON
  object the rubric specifies."

Save the returned JSON verbatim to
`eval_logs/<UTC yyyymmdd_hhmmss>_collection.json`. Fence-wrapped but
otherwise valid JSON is VALID — strip the fences rather than spending the
retry on a formatting technicality. If it is genuinely not JSON,
re-dispatch once with a stricter reminder; if still invalid, log the
iteration unscored and stop rather than inventing a score.

## Step 3 — The loop

`collection_score > 7.0` exits. Otherwise:

1. Take `weakest_dimension` and the improvement that names it.
2. Fix it in the RIGHT PLACE, which is rarely this directory:
   - `repetition`, `range` — the fix belongs in a work. Revise the work
     the finding names, then re-run this pass. Do not paper over it in
     `bible/binding.md`.
   - `facet_coverage`, `binding_delivery` — usually `bible/binding.md`
     and the slate, sometimes a work that needs re-briefing.
   - `independence` — the work that borrows. Make it stand alone.
   - `running_order` — this directory: reorder `works` in `state.json`.
     Nothing else changes.
3. Commit each kept iteration: `collection: <dimension> <old> -> <new>`.
4. Append to the CONTAINER's `results.tsv` — not a work's. That file
   carries cross-work rows only; each work keeps its own history in its
   own directory, the same as any project.

A pass that only ever reorders is a pass that is not working. Reordering
is the cheapest fix available and the least likely to be the right one:
if two works open the same way, the order cannot save them.

## Step 4 — Record the order

When the pass clears, write the accepted order into `state.json`'s `works`
array. That array is the running order, and export reads it — the
directory names are not required to sort into it, and `01-`-style prefixes
are a naming convention rather than an ordering mechanism.

Update `state.json`: `phase` to `export`, `collection_score` to the final
value. Commit.

## What this pass is not

It does not re-grade prose. The revision phase already did that, with the
room to do it properly, on a judge that could give one work its full
attention. A finding here has to be a statement about the collection —
"works 3, 5 and 7 all open on a character waking up", never "work 3's
dialogue is flat".
