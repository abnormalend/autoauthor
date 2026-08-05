# Autonovel → Claude Code Skills Conversion — Design

**Date:** 2026-08-05
**Status:** Approved

## Goal

Convert the autonovel pipeline (fork of NousResearch/autonovel) into a set of
Claude Code skills packaged as a self-contained plugin. Claude Code becomes the
runtime: the 18 Python scripts that wrap the Anthropic API are replaced by
skill instructions, while the genuinely mechanical scripts are preserved as
executables shipped inside the plugin.

## Decisions (from brainstorming)

| Question | Decision |
|---|---|
| Scope | Core writing pipeline only: seed → foundation → draft → revise → review → typeset/ePub export. Art (fal.ai), audiobook (ElevenLabs), cover, and landing-page scripts stay in the repo untouched and out of scope. |
| Final home | A plugin in Brent's existing marketplace repo (separate project). This fork is the development source; `plugin/autonovel/` is built here and copied to the marketplace when ready. |
| Novel storage | One directory per novel with its own private git repo (e.g. `~/novels/<tag>/`). Replaces branch-per-novel — this fork is public and can't host novel content. |
| Evaluation | Clean-room subagent judges + the mechanical regex slop scorer as a real script. Each judge subagent receives only the rubric and the text under judgment, no drafting context — preserving the independence the original separate-judge-model design was after. |
| Interaction model | Phase-gated: one skill per phase, each runs autonomously to its exit criteria then stops and reports. Human kicks off the next phase, possibly in a fresh session. |
| Architecture | Skill-per-phase plus a thin `novel` router skill that reads `state.json` and reports status / next step. |

## Plugin layout

```
autonovel/  (this fork — development source)
└── plugin/autonovel/
    ├── .claude-plugin/plugin.json
    ├── skills/
    │   ├── novel/            SKILL.md   ← router: status + what to run next
    │   ├── novel-seed/       SKILL.md   ← project init + seed generation
    │   ├── novel-foundation/ SKILL.md   ← Phase 1 loop
    │   ├── novel-draft/      SKILL.md   ← Phase 2 sequential drafting
    │   ├── novel-revise/     SKILL.md   ← Phase 3a revision cycles
    │   ├── novel-review/     SKILL.md   ← Phase 3b dual-persona review loop
    │   └── novel-export/     SKILL.md   ← Phase 4 LaTeX/ePub export
    └── shared/                          ← referenced by skills via relative paths
        ├── craft/       CRAFT.md, ANTI-SLOP.md, ANTI-PATTERNS.md
        ├── rubrics/     foundation.md, chapter.md, full-novel.md,
        │                adversarial-edit.md, reader-panel.md, opus-review.md
        ├── templates/   voice.md, world.md, characters.md, outline.md,
        │                canon.md, MYSTERY.md, state.json
        ├── scripts/     slop_score.py, apply_cuts.py, gen_brief.py,
        │                voice_fingerprint.py
        └── typeset/     build_tex.py, novel.tex, epub_metadata.yaml,
                         epub_style.css, epub front/back matter
```

Everything the skills need ships inside the plugin. No runtime dependency on
the autonovel repo. Craft docs are moved (not copied) into `shared/craft/` —
the plugin copy is the single source of truth.

## Script disposition

**Replaced by skill instructions (deleted; git history preserves them):**
`seed.py`, `gen_world.py`, `gen_characters.py`, `gen_outline.py`,
`gen_outline_part2.py`, `gen_canon.py`, `draft_chapter.py`, `run_drafts.py`,
`gen_revision.py`, `adversarial_edit.py`, `compare_chapters.py`,
`reader_panel.py`, `review.py`, `build_arc_summary.py`, `build_outline.py`,
`evaluate.py` (LLM-judge portion), `run_pipeline.py`, `main.py`.
Their prompts are ported into skill instructions and `shared/rubrics/`.

**Preserved as mechanical scripts in `shared/scripts/`:**
- `slop_score.py` — extracted from `evaluate.py` (~lines 45–240): regex bans,
  fiction clichés, show-don't-tell violations, sentence-uniformity checks.
  Gets a CLI (`slop_score.py <file>...`) with the same score-adjustment
  semantics evaluate.py applied.
- `apply_cuts.py` — batch adversarial-cut applicator (quote-matching removal).
- `gen_brief.py` — mechanical revision-brief assembler from panel/eval/cuts
  JSON logs (no API calls today; kept as-is with path adjustments).
- `voice_fingerprint.py` — mechanical voice/text analysis.
- `typeset/build_tex.py` + LaTeX/ePub assets — unchanged.

**Out of scope, left untouched at repo root:** `gen_art.py`,
`gen_art_directions.py`, `gen_audiobook.py`, `gen_audiobook_script.py`,
`gen_cover_composite.py`, `gen_cover_print.py`, `audiobook_voices.json`,
`landing/`.

**Porting requirement — de-Bells the prompts:** the original scripts leak
story-specific content from the first novel (e.g. `gen_world.py` hardcodes
"Cass's Gift" and "Cantamura" section headers). Ported instructions must be
fully generic, deriving all story specifics from `seed.txt`.

## Shared invariants (stated in every phase skill)

1. **Score-gated git mechanics, unchanged from the original:** iterate →
   evaluate → `git commit` if the score improved, `git reset --hard HEAD~1`
   if worse. Every keep/discard logged to `results.tsv`. `state.json` tracks
   phase, iteration, scores, and propagation debts. All of this happens in
   the novel's own repo.
2. **Clean-room subagent judging:** evaluation spawns a fresh subagent (Agent
   tool) given only the relevant `shared/rubrics/*.md` file and the text
   under judgment. Judges return structured scores the skill parses. The
   mechanical `slop_score.py` runs alongside and adjusts scores
   independently, mirroring evaluate.py's behavior.
3. **Required reading:** each skill's first instruction is to read the novel
   project's `voice.md` (Part 1 guardrails), plus `shared/craft/CRAFT.md` and
   `ANTI-SLOP.md` before writing or judging anything.
4. **Phase completion notification:** each phase skill ends by sending a
   Pushover notification (via the installed pushover skill) with the outcome:
   score reached, chapters completed, or where/why it stopped.
5. **The Stability Trap and craft rules** from `program.md` (fight stability,
   specificity over abstraction, earned metaphors, forward progress over
   perfection) are ported into the relevant skills' instructions.

## Per-skill behavior

### `novel` (router)
Invoked from inside a novel project directory. Reads `state.json`,
`results.tsv`, and recent git log; reports current phase, iteration, latest
scores, pending debts; names the skill to run next. If invoked outside a
novel project, explains how to start one with `novel-seed`. Never mutates
anything.

### `novel-seed`
Asks where the novel should live (default `~/novels/<tag>/`). Creates the
directory, `git init`, copies `shared/templates/` in, generates 10 candidate
seed concepts (each with world-differentiator, central tension,
cost/constraint, sensory hook), presents them for selection (or auto-picks
when told to), writes `seed.txt` and initial `state.json`
(`phase: foundation`), makes the initial commit.

### `novel-foundation` (Phase 1)
Loop until `foundation_score > 7.5 AND lore_score > 7.0`:
world.md → characters.md (wound/want/need/lie, sliders, distinct speech) →
outline.md part 1 (Save the Cat beats, try-fail cycles) → foreshadowing
ledger → voice discovery (5 trial passages in different registers; select;
write exemplars and anti-exemplars into voice.md Part 2) → MYSTERY.md →
canon.md cross-referencing. Every added fact also logged to canon.md.
Foundation-judge subagent scores against `rubrics/foundation.md` (lore
interconnection weighted 40%). Keep/discard per invariant 1; target the
weakest dimension each iteration. Cross-layer consistency checks every
iteration (per program.md).

### `novel-draft` (Phase 2)
For each chapter in outline order, max 5 attempts, keep at score > 6.0.
Context recipe per chapter (from program.md): voice.md + world.md +
characters.md in full, this chapter's outline entry, previous chapter's last
~1000 words, next chapter's outline entry. After each draft: chapter-judge
subagent (`rubrics/chapter.md`) + `slop_score.py`; extract new canon entries
into canon.md; log a debt in `state.json` when writing reveals a lore gap.
Post-draft: mechanical slop pass across all chapters, fix recurring patterns,
set phase to `revision`. Forward progress over perfection — 6.0 ships.

### `novel-revise` (Phase 3a)
Cycles of: adversarial-edit subagent per chapter (`rubrics/adversarial-edit.md`
→ classified cuts JSON in `edit_logs/`) → `apply_cuts.py` for OVER-EXPLAIN +
REDUNDANT cuts → 4 reader-panel persona subagents (editor, genre reader,
writer, first reader; `rubrics/reader-panel.md`) → consensus items (3/4+)
become priorities → `gen_brief.py` assembles briefs → rewrite target chapters
in-session per brief → re-evaluate affected chapters (keep/discard).
Full-novel judge (`rubrics/full-novel.md`) closes each cycle. The Elo
tournament from `compare_chapters.py` is folded in as an optional cycle-1
diagnostic (head-to-head chapter comparisons by judge subagents) rather than
a required step. Stop on plateau:
Δ < 0.5 across 2 consecutive cycles (min 3, max 6 cycles). Guardrails from
PIPELINE.md ported: compression sweet spot 2200–3000 words, don't chase the
rotating weakest chapter past 2 rotations, watch for expansion bloat.

### `novel-review` (Phase 3b)
Loop (max 4 rounds): send full manuscript to one fresh subagent on the
strongest available model with the dual-persona prompt (literary critic, then
professor of fiction; `rubrics/opus-review.md`). Parse items by severity
(major/moderate/minor) and qualification (hedged vs. unqualified). Stopping
conditions verbatim from the original: no major unqualified items, OR >50% of
items qualified/hedged, OR ≤2 items total. Address top items via briefs +
in-session rewrites + `apply_cuts.py`; commit; repeat.

### `novel-export` (Phase 4)
Normalize chapter titles, run `shared/typeset/build_tex.py`, compile with
`tectonic` (check availability; tell the user how to install if missing),
build the ePub from the epub assets. Set title/author/epigraph in the
template. Output `novel.pdf` and `.epub` into the novel project.

## Error handling

- Judge subagent returns malformed/unparseable output → re-spawn once with a
  stricter format reminder; if still bad, record the iteration as
  no-score and continue rather than crash the loop.
- Attempt limits preserved (5 per chapter, 4 review rounds, 6 revision
  cycles) so no loop runs unbounded.
- A phase skill never marks its phase complete in `state.json` unless the
  exit gate is actually met; if it stops early (limits, user interrupt), it
  records where and why so `/novel` can resume accurately.
- Dirty git state in the novel repo at skill start → stop and ask the user
  rather than committing or resetting over unknown changes.

## Testing / validation

- **Scripts standalone:** `slop_score.py` run against a sample chapter with
  known planted slop; `apply_cuts.py` against a fixture cuts JSON;
  `gen_brief.py` against fixture eval/panel logs.
- **Local install:** add this repo's `plugin/` as a local marketplace and
  install the plugin, verifying all 7 skills list and trigger.
- **Smoke run:** `novel-seed` → a bounded `novel-foundation` run (2–3
  iterations) in a throwaway project to validate the loop mechanics, judge
  parsing, and keep/discard git behavior end to end.
- Skill authoring follows the superpowers `writing-skills` conventions
  (verified during implementation).

## Delivery

1. Build and validate `plugin/autonovel/` in this fork.
2. Remove the replaced API-wrapper scripts and moved docs from repo root;
   update README to describe the skills-based workflow.
3. Brent copies `plugin/autonovel/` into the marketplace repo (out of scope
   for this project).
