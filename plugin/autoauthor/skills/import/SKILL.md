---
name: import
description: Use when the user wants to import an existing story, manuscript, or draft written elsewhere into the autoauthor pipeline — to revise it, continue it, or salvage its foundation for a re-draft.
---

# Novel Import — Existing Story → Pipeline Project

Reverse-engineers an existing manuscript into a full autoauthor project:
splits chapters, extracts every planning layer from the prose, and
hands off to the gated foundation loop. The manuscript is ground truth
throughout — extraction documents what is on the page.

## Steps

1. **Gather inputs.** Ask for (a) the source — a file, several files,
   or a directory of prose; (b) where the project should live (same
   default and safety rules as seed: suggest `~/novels/<tag>`,
   STOP if the target exists non-empty, verify the parent is not
   inside a git repo); (c) the mode:
   - `revise` — the story is finished; goal is the revision/review
     machinery.
   - `continue` — the story is unfinished; goal is drafting the rest.
   - `salvage` — the ideas are good, the prose isn't; extract the
     foundation, discard the prose, re-draft.
   Read the ENTIRE source before anything else. For sources too large
   for one pass, read in sequential slices, keeping running notes per
   chapter — never extract from an unread portion.

2. **Initialize the project** exactly as seed step 2 does:
   safety checks first (STOP if `<dir>` exists non-empty; verify the
   parent is not inside a git repo), then `mkdir -p <dir> && cd <dir>
   && git init`, copy every file from
   `"${CLAUDE_PLUGIN_ROOT}/shared/templates/"` into it (quoted against
   spaces in the install path), `mv gitignore .gitignore`, `mkdir
   chapters eval_logs edit_logs briefs`, and a printf'd results.tsv
   header:
   `printf 'timestamp\tphase\tscore\twords\tkeep_discard\tdescription\n' > results.tsv`
   Use absolute paths throughout. Do NOT create seed.txt — imported
   projects derive their premise from the manuscript, and every phase
   skill treats seed.txt as optional.

3. **Chapter intake** (revise/continue modes):
   - Pre-split sources (one file per chapter, or clear `#`/"Chapter N"
     headings): write `chapters/ch_NN.md`, zero-padded, sequential,
     title lines normalized to `# Chapter N: <Title>` (untitled
     chapters get a short descriptive title drawn from the chapter).
   - Unstructured sources: detect boundaries by headings first, then
     numeric/"Chapter N" text patterns; if neither exists, propose a
     split at scene breaks and large gaps — show the user the proposed
     boundaries (chapter count, first line of each) and get approval
     BEFORE writing files. Never split silently.
   In salvage mode, instead write the source verbatim to
   `import_source.md` at the project root (tracked) and leave
   `chapters/` empty — the prose is raw material, not canon.

4. **Infer the genre.** From the manuscript you have now read in full,
   propose a primary pack, an optional secondary, and any modifiers, naming
   the evidence for each (the speculative elements present, the shape of the
   central conflict, the register, the content). Show the user the available
   packs from `"${CLAUDE_PLUGIN_ROOT}/shared/genres/"` and your proposal,
   and ask them to confirm or correct it — same shape as the MYSTERY.md
   confirmation in the final steps. Write the choice into state.json —
   never leave `genre` null, which resolves silently to `general` — and
   resolve the stack:

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/resolve_genre.py"
   ```

   If it exits non-zero, STOP and report — an unresolvable or conflicting
   genre stack must be fixed before any extraction work. Keep the reported
   pack paths; step 5's extraction reads the resolved pack's
   `## World Sections` and `## Canon Categories` from them.

   In a fully autonomous run, take your own inference and say so in the
   handoff report.

5. **Extract the layers** following
   `references/extraction-guide.md` (this skill's directory) in this
   order: chapters on disk first (step 3), then voice (Part 2 +
   voice_wells.json, including the fingerprint run when chapters
   exist), then world.md → characters.md → MYSTERY.md → outline.md
   (as-written + observed ledger) → canon.md (salvage mode: SKIP
   outline extraction entirely — leave outline.md as its template;
   the foundation fill pass outlines the re-draft fresh, using the
   extracted layers and import_source.md as raw material). Cite
   chapters as `(ch_NN)` (salvage mode: cite `(source §N)` sections of
   import_source.md).

6. **Write state.json** per the extraction guide's state rules, and
   append one results.tsv row:
   `<ISO timestamp>\tfoundation\t0\t<total manuscript words>\tkeep\timport: <mode>, <N> chapters`

7. **Confirm the mystery.** Show the user the inferred MYSTERY.md and
   ask them to confirm or correct it. Apply corrections. (In a fully
   autonomous run, keep the IMPORTED banner and note that
   confirmation is pending — the foundation judge treats undefined
   mysteries as gaps, which is the correct pressure.)

8. **Commit and hand off.** `git add -A && git commit -m "import:
   <mode>, <N> chapters, <words> words"`. Report: what was extracted
   (per-layer one-liners), unresolved foreshadowing plants found, the
   confirmed/pending mystery, and the next step —
   `/autoauthor:foundation`, which runs the normal gated loop and
   then routes onward automatically (finished manuscripts exit to
   revision; unfinished to drafting).
