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

3. **Initialize the project:**
   - Safety checks first: if `<dir>` already exists and is non-empty, STOP
     and ask the user before touching it (a retry may have partial content
     worth keeping — never overwrite silently). Then verify the parent is
     not inside a git repo: `git -C <parent> rev-parse --is-inside-work-tree`
     must FAIL; if it succeeds, pick a different location.
   - `mkdir -p <dir> && cd <dir> && git init`
   - Copy every file from `${CLAUDE_PLUGIN_ROOT}/shared/templates/` into it:
     `cp "${CLAUDE_PLUGIN_ROOT}/shared/templates/"* <dir>/` (quoted against
     spaces in the install path) — this copies voice.md, world.md,
     characters.md, outline.md, canon.md, MYSTERY.md, state.json.
   - **Write the genre into `state.json` immediately after the copy** —
     set `genre`, `genre_secondary`, and `genre_modifiers` from step 2,
     replacing the template's nulls. Then resolve the stack from the
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
