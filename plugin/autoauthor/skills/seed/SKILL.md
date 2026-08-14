---
name: seed
description: Use when the user wants to start a new novel, generate story seeds or premises, riff on a story idea, or set up a new autoauthor project directory.
---

# Novel Seed — Start a New Novel Project

Creates a standalone novel project directory (its own private git repo —
novel content never lives in the plugin or any public repo) and writes the
chosen seed concept. This is the only autoauthor skill that runs outside an
existing project.

## Steps

1. **Location.** Ask the user where the project should live unless they
   already said. Default suggestion: `~/novels/<tag>` where `<tag>` is a
   short kebab-case slug. Never nest inside another git repo.

2. **Choose the genre.** List the packs in
   `"${CLAUDE_PLUGIN_ROOT}/shared/genres/"` (excluding TEMPLATE.md) with
   their `label`, and ask the user to pick a primary. Offer an optional
   secondary and any modifiers, explaining that a secondary contributes
   additively (a second genre's material layered in, such as a romance
   subplot) and a modifier is an orthogonal axis (YA, cozy, heat level).
   If the user declines to choose, use `general`.

   Settle this BEFORE the project directory exists. The genre is written
   during init below, not after it: the template `state.json` ships
   `"genre": null`, and a null genre resolves silently to `general` — so a
   run interrupted between init and a later genre step would leave a
   project that builds an entire book in a genre nobody chose, with
   nothing ever surfacing the mistake.

2b. **Choose the form.** List the forms in
   `"${CLAUDE_PLUGIN_ROOT}/shared/forms/"` with their `label` and `words`
   range, and ask how long the work is. If the user declines, use `novel`
   — the same defaulting rule and the same caveat as the genre.

   The form decides total length, which planning layers get built, where
   the foundation gate sits, and how the genre's own criteria are read. It
   is not a preference to revisit later: a short story and a novel are
   different works, not the same work at two sizes.

   Not every genre supports every length. A pack needs a length-scoped
   section to be judged below novel length, and one without it is REFUSED
   rather than judged on criteria written for eighty thousand words. Settle
   the form here, alongside the genre, so the pair is checked once at init
   rather than discovered at the first foundation run — the resolver in
   step 3 will say plainly if they cannot go together.

2c. **Choose the structure.** Ask whether this is one work or several:

   - **standalone** — one work. The default, and what to use if the user
     has not said otherwise.
   - **collection** — several complete works bound as one book, checked
     for variety and independence before export.
   - **series** — several books sharing continuity, each advancing a whole
     and closing itself.

   Settle it here for the same reason as genre and form: it decides the
   directory layout, and it cannot be changed later without moving every
   file. If the user describes "a trilogy", "a series of stories", or "a
   collection", ask rather than assuming — those words are used loosely
   and the two containers check opposite things.

   For a CONTAINER, the genre and form chosen above belong to the
   container and are inherited by every work; a work may not override
   them, because they are what make N works one book.

3. **Initialize the project:**
   - Safety checks first: if `<dir>` already exists and is non-empty, STOP
     and ask the user before touching it (a retry may have partial content
     worth keeping — never overwrite silently). Then verify the parent is
     not inside a git repo: `git -C <parent> rev-parse --is-inside-work-tree`
     must FAIL; if it succeeds, pick a different location.
   - `mkdir -p <dir> && cd <dir> && git init`

   **For a container** (`collection` or `series`), the layout differs and
   the rest of this step is replaced by:

   - `mkdir -p bible works`
   - Copy the shared layers into `bible/`: `voice.md`, `world.md`,
     `characters.md`, `canon.md` from
     `${CLAUDE_PLUGIN_ROOT}/shared/templates/`. A SERIES additionally
     needs `bible/arc.md` — write it now, one line per planned volume
     saying what that volume owes the whole, even if it is a guess. The
     resolver refuses a series without it, and for a good reason: without
     an arc the cross-work pass can check that nothing contradicts and
     cannot check that anything progressed.
   - Write `state.json` at the container: the template's keys plus
     `"structure"`, the genre and form from steps 2 and 2b, and
     `"works": []`. That array is the running order, and export reads it.
   - Create the first work: `mkdir -p works/01-<slug>/chapters`, copy the
     per-work templates from `shared/templates/` into it, and add
     `"01-<slug>"` to the container's `works`. Set the work's
     `state.json` phase to `foundation` and leave its genre, form and
     modifiers NULL — it inherits them, and setting them is an error the
     resolver reports.
   - Then run the resolver from the container to confirm it validates,
     and stop. The user runs foundation from inside a work, not here.

   **For a standalone project**, continue:

   - Copy every file from `${CLAUDE_PLUGIN_ROOT}/shared/templates/` into it:
     `cp "${CLAUDE_PLUGIN_ROOT}/shared/templates/"* <dir>/` (quoted against
     spaces in the install path) — this copies voice.md, world.md,
     characters.md, outline.md, canon.md, MYSTERY.md, state.json.
   - **Write the genre and form into `state.json` immediately after the
     copy** — set `genre`, `genre_secondary`, and `genre_modifiers` from
     step 2 and `form` from step 2b, replacing the template's nulls. Then resolve the stack from the
     project directory and KEEP the JSON it prints; the rest of this step
     and step 4 both read it:

     ```bash
     python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/resolve_genre.py"
     ```

     It prints the merged config on stdout: `packs` (each with a `name`,
     `role`, and the absolute `path` of the pack file to read),
     `display_label`, `shape`, `artifacts`, and the rest. If it exits
     non-zero, fix the selection before continuing — a conflicting stack
     (for example `ya` with `erotica`) is rejected here rather than
     producing an incoherent book.
   - Render the pack-driven parts of the copied templates, reading the
     pack files at the `packs[].path` values just printed: write
     `world.md`'s section headings from the resolved pack's
     `## World Sections`, and `canon.md`'s category headings and one example
     entry each from its `## Canon Categories`. Create any file named in the
     resolved `artifacts` list from the pack's `## Artifacts` template.
   - Install the ignore file: `mv <dir>/gitignore <dir>/.gitignore` —
     eval_logs/, edit_logs/, and briefs/ MUST be gitignored; the
     drafting and revision skills depend on them surviving
     `git reset --hard` discards and staying out of commits.
   - `mkdir chapters eval_logs edit_logs briefs`
   - Create `results.tsv` containing exactly this header line (the
     separators are REAL tab characters — use printf, not echo, so
     they can't silently become spaces):
     `printf 'timestamp\tphase\tscore\twords\tkeep_discard\tdescription\n' > results.tsv`
   - Use the absolute `<dir>` path in every command rather than relying on
     the shell's current directory persisting.

4. **Generate concepts.** Read `references/seed-prompts.md` (in this
   skill's directory) and every pack path the resolver reported in step 3
   (the `path` of each entry in `packs`). If the user
   supplied an idea, use the riff prompt (5 variations); otherwise the
   generate prompt (10 concepts). Write the concepts yourself, in-session,
   following every constraint in the prompt — the diversity requirements
   and the DO-NOT list are hard rules.

5. **Selection.** Present the concepts compactly (TITLE + HOOK + the pack's
   first required field that the neutral scaffold does not already define)
   and ask the user to pick, remix, or reroll. If the user asked for a fully
   autonomous run, pick the concept with the strongest interlock between the
   pack's central constraint and the central tension, and say which you
   picked and why.

6. **Write `seed.txt`** with the full chosen concept. Verify it contains a
   world-differentiator (the WORLD field), a central tension (TENSION), a
   concrete sensory anchor in the WORLD field, and every field the pack's
   `## Seed Prompt` marks required — and strengthen any that are missing
   before saving.

7. **Commit:** `git add -A && git commit -m "seed: <title>"`

8. **Report:** project path, chosen title/hook, and next step:
   `cd <dir>` then `/autoauthor:foundation`.
