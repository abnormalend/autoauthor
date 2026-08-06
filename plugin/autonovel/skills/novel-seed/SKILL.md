---
name: novel-seed
description: Use when the user wants to start a new novel, generate story seeds or premises, riff on a story idea, or set up a new autonovel project directory.
---

# Novel Seed — Start a New Novel Project

Creates a standalone novel project directory (its own private git repo —
novel content never lives in the plugin or any public repo) and writes the
chosen seed concept. This is the only autonovel skill that runs outside an
existing project.

## Steps

1. **Location.** Ask the user where the project should live unless they
   already said. Default suggestion: `~/novels/<tag>` where `<tag>` is a
   short kebab-case slug. Never nest inside another git repo.

2. **Initialize the project:**
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
   - Install the ignore file: `mv <dir>/gitignore <dir>/.gitignore` —
     eval_logs/, edit_logs/, and briefs/ MUST be gitignored; the
     drafting and revision skills depend on them surviving
     `git reset --hard` discards and staying out of commits.
   - `mkdir chapters eval_logs edit_logs briefs`
   - Create `results.tsv` containing exactly this header line:
     `timestamp	phase	score	words	keep_discard	description`
   - Use the absolute `<dir>` path in every command rather than relying on
     the shell's current directory persisting.

3. **Generate concepts.** Read `references/seed-prompts.md` (in this
   skill's directory). If the user supplied an idea, use the riff prompt
   (5 variations); otherwise the generate prompt (10 concepts). Write the
   concepts yourself, in-session, following every constraint in the prompt
   — the diversity requirements and the DO-NOT list are hard rules.

4. **Selection.** Present the concepts compactly (TITLE + HOOK + MAGIC/COST,
   matching the field names in seed-prompts.md) and ask the user to pick,
   remix, or reroll. If the user asked for a fully autonomous run, pick
   the concept with the strongest interlock between the magic's cost and
   the central tension, and say which you picked and why.

5. **Write `seed.txt`** with the full chosen concept. Verify it contains
   all four required elements — world-differentiator (the WORLD field),
   central tension (TENSION), cost/constraint (MAGIC/COST), and a concrete
   sensory anchor (the WORLD field must contain at least one specific
   sensory detail) — and strengthen any that are missing before saving.

6. **Commit:** `git add -A && git commit -m "seed: <title>"`

7. **Report:** project path, chosen title/hook, and next step:
   `cd <dir>` then `/autonovel:novel-foundation`.
