# Shakedown Findings (2026-08-17) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix the skill-level defects surfaced by the 2026-08-17 foundation / draft / revise runs on a short-story project, grouped into six independently shippable parts.

**Architecture:** Most of the plugin is markdown a model reads at runtime, so most tasks are prose edits to `skills/*/SKILL.md`, `shared/rubrics/*.md`, and reference guides — each edit shows the exact old and new text. Three small Python scripts are added under `shared/scripts/` (`splice_audit.py`, `continuity_check.py`, and a `--protect-file` flag on `apply_cuts.py`), plus one form-frontmatter field (`iteration_cap`) and one `gen_brief.py` flag; those get tests. Parts A–F are independent; ship them in order but any one can be dropped without breaking the others.

**Tech Stack:** Python 3.11+, pytest via `uv run pytest tests/ -q` (461 tests, ~7 s), no new dependencies.

**Spec:** the three findings documents. Task 0 moves them under `docs/superpowers/specs/`.

**Repo conventions to honour throughout** (from `CLAUDE.md`):
- Prose under `shared/genres`, `shared/forms`, `shared/rubrics`, `shared/craft`, `shared/templates` is required reading; `test_required_reading_is_clean.py` bans Tier-1 phrases there. Read `ANTI-SLOP.md` before writing any prose.
- Dimension keys are a compatibility surface — no renames anywhere in this plan.
- No cap values change, so `gate_solver.py` results are unaffected; CI still runs it.
- Commit with `git commit -F -` and a heredoc, never `-m` with backticks.
- Version lives in `plugin/autoauthor/.claude-plugin/plugin.json` and twice in `.claude-plugin/marketplace.json`; the final task bumps all three.

All paths below are relative to the repo root unless they start with `skills/`, `shared/`, which are relative to `plugin/autoauthor/`.

---

## Task 0: File the findings as the spec

**Files:**
- Move: `2026-08-17-foundation-findings.md`, `2026-08-17-draft-findings.md`, `2026-08-17-revision-findings.md` → `docs/superpowers/specs/`

- [ ] **Step 1: Move and commit**

```bash
git mv 2026-08-17-foundation-findings.md docs/superpowers/specs/2026-08-17-foundation-findings.md 2>/dev/null || mv 2026-08-17-foundation-findings.md docs/superpowers/specs/
mv 2026-08-17-draft-findings.md 2026-08-17-revision-findings.md docs/superpowers/specs/
git add docs/superpowers/specs/2026-08-17-*-findings.md docs/superpowers/plans/2026-08-17-shakedown-findings.md
git commit -F - <<'EOF'
docs: file the 2026-08-17 shakedown findings and the plan that acts on them

Three findings documents from a full foundation → draft → revise run on a
short-story project, plus the implementation plan. The findings are the
spec; the plan groups them into six independent parts.
EOF
```

---

# Part A — Baseline and keep/discard rules (prose only)

Covers: revision findings 5, 6; foundation findings 1 (weak form), 2, 8.

## Task A1: Revise — baseline at the start of Fix, valid only within its cycle

**Files:**
- Modify: `skills/revise/SKILL.md:232-272` (Fix step 4)
- Modify: `skills/revise/SKILL.md:377-378` (Guardrails)

- [ ] **Step 1: Replace the same-cycle baseline block**

In `skills/revise/SKILL.md`, replace the paragraph starting `So: use the recorded score as a first pass, but **the moment a` through `Re-baseline before concluding either way.` (lines 256–272) with:

```markdown
   So: **baseline before you rewrite, not after a rewrite fails.** At
   the start of Fix, dispatch the chapter judge once for EVERY chapter
   you intend to touch this cycle, in parallel, against the current
   committed text (same labeled paths as a scoring dispatch; write each
   to `eval_logs/chNN_baseline_cycleN.json`). These run concurrently
   with drafting the first brief, so they cost wall-clock nothing. Two
   things you get only by doing it first: an honest gate from the first
   attempt (a chapter carrying 7.33 from drafting baselined at 7.00 in
   revision — the rewrite's real gain was +0.78, not +0.45), and a
   fresh read of the committed text that names defects the debt list
   missed (one run's baselines found a continuity contradiction and an
   archive keyed by different calendars in two chapters, none of it on
   any list). A baseline dispatch is not an attempt: it does not count
   against the 3 per chapter per cycle. Log each as a row in
   attempts.tsv with `baseline` in the keep_discard column.

   **A baseline is valid only within the cycle it was measured.** This
   is not just a drafting-vs-revision effect. Measured on one project:
   a chapter's committed text scored 7.89 by the cycle-1 revision judge
   and 7.22 by the cycle-2 revision judge, unchanged in between. A
   cycle-2 rewrite scored 7.78 and "failed" the 7.89 gate by 0.11;
   against the true same-cycle baseline it beat it by 0.56 and was one
   command from being discarded. Never gate against a number from a
   prior cycle. If you skipped the start-of-Fix baseline for a chapter
   and a rewrite then fails, re-baseline it before discarding — one
   dispatch settles whether you are discarding a regression or a
   phantom.

   Two consequences worth internalising:
   - Same-judge variance on identical text runs about ±0.5, so a
     single measurement is noisy. Do not spend a second and third
     attempt chasing a 0.5 gap before you have re-baselined; the gap
     may not exist.
   - A rewrite that TIES a true same-cycle baseline is not an
     improvement and should still be discarded — but a rewrite that
     ties the *recorded* number may in fact be beating the true one.
     Re-baseline before concluding either way.
```

- [ ] **Step 2: Fix the guardrail**

Replace lines 377–378:

```markdown
Never discard a rewrite against a score you did not measure this cycle.
Drafting-phase numbers run high; re-baseline the committed text first.
```

with:

```markdown
Never discard a rewrite against a score you did not measure THIS cycle.
Drafting-phase numbers run high and prior-cycle numbers drift by more
than half a point on identical text; baseline every chapter you will
touch at the start of Fix, and re-baseline before any discard that
would otherwise rest on an older number.
```

- [ ] **Step 3: Update the "attempt rows" sentence in step 4**

In the same step 4, the line `Attempt rows go to \`eval_logs/attempts.tsv\` and fold into results.tsv at commit (same columns as draft's rows, but the phase column is \`revision\`).` — append: ` Baseline rows carry \`baseline\` in the keep_discard column and fold in with the rest; they are the record of what each cycle's judge thought of the text it started from.`

- [ ] **Step 4: Run tests and commit**

```bash
uv run pytest tests/ -q
git add plugin/autoauthor/skills/revise/SKILL.md
git commit -F - <<'EOF'
fix: baseline every touched chapter at the start of Fix, and only trust a same-cycle number

The skill said to re-baseline reactively, after a rewrite failed, and
told the operator to log baselines "so later cycles can reuse it". A
live run measured 0.67 drift between cycle-1 and cycle-2 revision
judges on identical text; a rewrite that beat its true baseline by
0.56 was one command from discard because it was gated against the
prior cycle's number. Baselining first also surfaced three defects no
debt list carried.
EOF
```

## Task A2: Foundation — a fired cap forces another iteration

**Files:**
- Modify: `skills/foundation/SKILL.md:103-109` (Gate check)

- [ ] **Step 1: Replace step 2**

Replace:

```markdown
2. **Gate check.** `overall_score > form.gate.overall` AND `pillar_score >
   form.gate.pillar` → exit the loop. Both numbers come from the resolver's
   `form` block, never from memory; for the `novel` form they are 7.5 and
   7.0. They are the form's because they are length economics — the bar is
   this high on the reasoning that a weak plan costs the drafting loop far
   more than it costs to plan again, and that reasoning does not survive a
   translation to five thousand words.
```

with:

```markdown
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
```

- [ ] **Step 2: Commit**

```bash
uv run pytest tests/ -q
git add plugin/autoauthor/skills/foundation/SKILL.md
git commit -F - <<'EOF'
fix: a fired cap in foundation forces another iteration even when the gate is cleared

The gate is a floor on a weighted mean; a live run cleared it on the
first scored iteration with internal_consistency capped at 4 and five
contradictions listed, one of them the clock the climax depends on.
Following the skill literally would have exited there.
EOF
```

## Task A3: Foundation — tie band and "was the targeted fault fixed?" before discard

**Files:**
- Modify: `skills/foundation/SKILL.md:126-145` (Keep/discard)

- [ ] **Step 1: Replace the keep/discard rule**

Replace the text from `4. **Keep/discard.** Score improved over the best previous score (or` through `eval record is kept even for discarded iterations). Either way` with:

```markdown
4. **Keep/discard.** Compare `overall_score` against the best previous
   score (or treat the first scored iteration as the best). Three cases:

   - **Improved by more than 0.15** → `git add -A && git commit -m
     "foundation iter <N>: <weakest_dimension> (<score>)"`.
   - **Within ±0.15 of the best** → a TIE, which is inside single-judge
     noise (per-dimension variance on unchanged text was measured at
     two full points on one run). Keep the state with the higher
     `pillar_score`; if those tie too, keep the state whose eval lists
     fewer contradictions in fact tables, outline beats, quoted text, or
     character facts. Commit if keeping the new state.
   - **Regressed by more than 0.15** → before discarding, read the two
     evals side by side. If the dimension you targeted improved and the
     contradictions the new eval lists are NEW ones (surface faults you
     introduced while rewriting), the revision worked and you dropped a
     wrench on the way out: keep it, and target the new faults next
     iteration. Discard only when the targeted dimension did not
     improve. One run's iteration 3 fixed the transmission-cadence
     fault two judges had called MAJOR and regressed 0.12 because it
     introduced four one-line surface errors; discarding would have
     restored the major fault to recover 0.12.

   After every KEPT iteration, update `foundation_score`, `pillar_score`,
   and `iteration: <N>` in state.json to the new best values (this is
   what makes the run resumable — the router reads `iteration`). A
   resuming session takes "best previous score" from state.json,
   cross-checking the last `keep` row in results.tsv.
   If the project's genre changed since the last scored iteration (compare
   `genre`/`genre_secondary`/`genre_modifiers` against the most recent
   `genre-change` marker row in results.tsv), do NOT compare against the old
   best score — the weights differ, so the numbers are not comparable.
   Treat the next scored iteration as the first one.
   Discard means `git reset --hard HEAD` (resets tracked files,
   staged and unstaged, back to the last kept iteration; untracked
   files like the new eval log survive, which is what we want — the
   eval record is kept even for discarded iterations). Either way
```

(The `append to results.tsv:` line and its row format that follow stay as they are.)

- [ ] **Step 2: Add "fix strings are hypotheses" to step 3**

After the sentence ending `canon.md captures all new facts.` in step 3, add:

```markdown
   The eval's per-dimension `fix` strings and `top_3_improvements` are
   hypotheses from an agent that has seen one set of documents and no
   other constraint. Take the diagnosis; design the fix yourself, and
   check it against the outline's fact table before writing it. One
   run's `novum_specificity.fix` proposed a specific window that
   contradicted the ten-hour window the same eval was complaining about
   two dimensions earlier — applying it verbatim would have preserved
   the fault it diagnosed.
```

- [ ] **Step 3: Commit**

```bash
uv run pytest tests/ -q
git add plugin/autoauthor/skills/foundation/SKILL.md
git commit -F - <<'EOF'
fix: foundation keep/discard reads why a score moved before discarding

Score-only keep/discard with no epsilon discarded a structurally
better plan twice in six iterations on one run: a 0.12 regression that
had fixed a MAJOR fault and introduced four one-line surface errors,
and a 0.01 delta on a state whose pillar rose 0.33. Adds a ±0.15 tie
band and a "did the targeted dimension improve" check, and marks the
judge's fix strings as hypotheses.
EOF
```

---

# Part B — Judge integrity and form-aware dispatch

Covers: draft findings 1, 5, 6, 7, 8, 9, 10; foundation finding 4.

## Task B1: The judge writes its own eval JSON (draft, foundation, revise)

**Files:**
- Modify: `skills/draft/SKILL.md:72-104`
- Modify: `skills/foundation/SKILL.md:77-99`
- Modify: `skills/revise/SKILL.md:232-237` and `:297-304`

- [ ] **Step 1: Draft step 4**

Replace the dispatch prompt in `skills/draft/SKILL.md` step 4 (`"Read the rubric at ... Return ONLY the JSON object the rubric specifies."`) with:

```markdown
   "Read the rubric at `<absolute plugin path>/shared/rubrics/chapter.md`
   and the genre pack(s) at `<resolved pack paths, primary first, each
   labeled with its role>`, and follow the rubric exactly. The project
   directory is `<absolute project
   path>`. The target chapter is chapter <N>; its file is
   `<absolute path to chapters/ch_NN.md>`. The previous chapter file is
   `<absolute path to ch_(N-1)>` (omit this line for chapter 1). The
   other input files are `<the layer files the resolved form builds,
   named — see Setup step 5>` and canon.md in the project directory.
   Write the JSON object the rubric specifies — bare JSON, no fences —
   to `<absolute project path>/eval_logs/<UTC yyyymmdd_hhmmss>_chNN.json`
   (compute the timestamp yourself before dispatching and put the exact
   path in the prompt), and return only that path and the
   `overall_score` value."

   The judge writes the file; you do not transcribe it. A run that
   re-typed four ~1,500-word verdicts by hand put a lossy step between
   the measurement and the artifact `score_verdict.py` certifies — the
   check was validating the orchestrator's copy, not the judge's. If
   the file is missing or is not valid JSON, that is a malformed
   response: one strict retry, then `noscore`.
```

Then replace the later `Save the JSON to \`eval_logs/<UTC yyyymmdd_hhmmss>_chNN.json\` (NN zero-padded — gen_brief.py globs this pattern). Fence-wrapped but otherwise valid JSON is VALID — strip the fences. Malformed JSON → one strict retry → else record \`noscore\` and move on.` with:

```markdown
   The filename is `<UTC yyyymmdd_hhmmss>_chNN.json` with NN zero-padded
   — gen_brief.py globs this pattern. If the judge fenced the JSON
   anyway, strip the fences in place; that is a formatting technicality,
   not a malformed response. Malformed or missing → one strict retry →
   else record `noscore` and move on.
```

- [ ] **Step 2: Foundation step 1**

In `skills/foundation/SKILL.md` step 1, replace `Return ONLY the JSON object the rubric specifies."` with `Write the JSON object the rubric specifies — bare JSON, no fences — to \`<absolute project path>/eval_logs/<UTC yyyymmdd_hhmmss>_foundation.json\` (compute the timestamp before dispatching and put the exact path in the prompt), and return only that path and the \`overall_score\` and \`pillar_score\` values."`

Replace `Save the returned JSON verbatim to \`eval_logs/<UTC yyyymmdd_hhmmss>_foundation.json\`. Fence-wrapped but otherwise valid JSON is VALID — strip the fences, don't waste the retry on a formatting technicality. If the response genuinely is not valid JSON, re-dispatch once` with `The judge writes the file; do not transcribe it (`score_verdict.py` must certify the judge's artifact, not your copy of it). If it fenced the JSON anyway, strip the fences in place — a formatting technicality, not a malformed response. If the file is missing or genuinely not valid JSON, re-dispatch once`.

- [ ] **Step 3: Revise Fix step 4 and Measure**

In `skills/revise/SKILL.md` Fix step 4, after `final score = judge minus slop penalty.` add: `The judge writes its own verdict file (\`eval_logs/<UTC yyyymmdd_hhmmss>_chNN.json\`, exact path in the prompt) and returns the path and score, exactly as draft does.`

In Measure step 1, replace `Return ONLY the JSON the rubric specifies." Save to \`eval_logs/<UTC yyyymmdd_hhmmss>_full.json\`.` with `Write the JSON the rubric specifies — bare JSON, no fences — to \`<absolute project path>/eval_logs/<UTC yyyymmdd_hhmmss>_full.json\` (exact path in the prompt) and return only that path and \`work_score\`."`

- [ ] **Step 4: Commit**

```bash
uv run pytest tests/ -q
git add plugin/autoauthor/skills/draft/SKILL.md plugin/autoauthor/skills/foundation/SKILL.md plugin/autoauthor/skills/revise/SKILL.md
git commit -F - <<'EOF'
fix: judges write their own eval JSON; the orchestrator no longer transcribes it

score_verdict.py was verifying the orchestrator's re-typed copy of the
verdict, so a transcription slip passed the check. Every scored
dispatch now names an absolute output path and the judge writes it.
EOF
```

## Task B2: Foundation dispatch names `voice_wells.json`; rubric forbids inferring absence

**Files:**
- Modify: `skills/foundation/SKILL.md:85-87`
- Modify: `shared/rubrics/foundation.md:8-14`

- [ ] **Step 1: Dispatch**

In step 1, replace `The input files are: \`<the documents form.layers calls for, named>\`.` with `The input files are: \`<the documents form.layers calls for, named>\`, and — whenever the \`voice\` layer is among them — \`voice_wells.json\` (the vocabulary wells the voice layer is required to emit).`

- [ ] **Step 2: Rubric**

In `shared/rubrics/foundation.md`, after the paragraph ending `its absence penalizes the work for being correctly what it is.` add:

```markdown
The converse also holds: a file you were not named is a file you have
not seen, not a file that does not exist. "I was not shown X" and "X
does not exist" are different findings, and only the first is one you
can make. A judge once deducted from voice_clarity for a "dangling
promise" to a `voice_wells.json` that was sitting, committed, in the
project directory; it had not been named, so it was not read, and its
absence was inferred from silence. If a document you were given refers
to a file you were not, note the reference and score what you were
given.
```

- [ ] **Step 3: Commit**

```bash
uv run pytest tests/ -q
git add plugin/autoauthor/skills/foundation/SKILL.md plugin/autoauthor/shared/rubrics/foundation.md
git commit -F - <<'EOF'
fix: name voice_wells.json in the foundation dispatch, and stop judges inferring absence from silence

The voice layer is required to emit voice_wells.json and nothing named
it to the judge, which then deducted for a file it decided did not
exist. It did.
EOF
```

## Task B3: Draft Setup creates `canon.md`, builds the file list from the form, reconciles state against history

**Files:**
- Modify: `skills/draft/SKILL.md:12-40` (Setup), `:44-50` (step 1), `:124-127` (step 7)
- Modify: `skills/status/SKILL.md:20-26`

- [ ] **Step 1: Add Setup steps 5–7 to draft**

After Setup step 4 (`Resume point: ...`) in `skills/draft/SKILL.md`, add:

```markdown
5. **Build the input-file list from the form.** The resolver's
   `form.layers` names which planning documents exist. Map them through
   `LAYER_FILES` in `form_pack.py` (`voice` → voice.md, `world` →
   world.md, `characters` → characters.md, `mystery` → MYSTERY.md,
   `outline`/`foreshadowing` → outline.md, `canon` → canon.md). That
   list, plus canon.md, is what every judge dispatch below names as
   "the other input files" and what step 1 loads. Do not name the
   novel's five files by habit: at `short-story` there is no world.md,
   and a judge told to read one spends its tool calls hunting for it.
6. **Ensure `canon.md` exists.** Compressed forms do not build a canon
   layer in foundation, but drafting establishes facts on the page that
   the chapter judge checks later chapters against. If `canon.md` is
   missing, create it now from
   `"${CLAUDE_PLUGIN_ROOT}/shared/templates/canon.md"` with the primary
   pack's `## Canon Categories` as its section headings, and commit
   `draft: canon.md scaffold`.
7. **Reconcile state against history.** Compare `state.json`'s
   `chapters_drafted` with the files in `chapters/` AND with
   `git log --oneline | grep -cE '^[0-9a-f]+ (draft: ch|revision complete|cycle [0-9]+ complete)'`.
   If history records drafting or revision work the working tree does
   not reflect (a `revision complete` commit above an empty
   `chapters/`, say), STOP and report the discrepancy — do not infer
   the resume point from the empty directory. One session drafted an
   entire story from scratch on top of a repository whose HEAD was
   `revision complete: 3 cycles`; every check the skill named passed.
```

- [ ] **Step 2: Step 1 context load**

Replace step 1's first bullet `- voice.md (full), world.md (full), characters.md (full)` with `- every layer file the form builds (Setup step 5), in full, except outline.md — voice.md and characters.md always; world.md and MYSTERY.md where the form built them`.

Replace `- THIS chapter's outline entry from outline.md (including its Plants list)` with:

```markdown
   - from outline.md: THIS chapter's entry (including its Plants list)
     AND every section that precedes the first chapter entry — the
     structure, the fact table, the clock, the register contract, the
     foreshadowing table. Those sections are what prevent the arithmetic
     and clock errors that were the dominant defect class on one run
     (eight of them across four chapters, every one derivable from the
     outline's fact table). At `form.band == "compressed"` load
     outline.md whole; at that length it costs less than the chapter it
     is used to write.
```

- [ ] **Step 3: Step 7 canon**

Replace `7. **Canon.** Append the judge's \`new_canon_entries\` to canon.md,` with `7. **Canon.** Append the judge's \`new_canon_entries\` to canon.md (created in Setup step 6 if the form did not build one),`.

- [ ] **Step 4: Status skill**

In `skills/status/SKILL.md` step 2, after the bullet `- \`git log --oneline -10\` and \`git status --porcelain\`` add:

```markdown
   - **and reconcile them:** if `git log` shows `draft: ch`, `cycle N
     complete` or `revision complete` commits but `state.json` says
     `chapters_drafted: 0` or `chapters/` is empty, report that as the
     headline — the state file and the repository disagree, and the
     next skill will otherwise redo work that already exists in
     history.
```

- [ ] **Step 5: Commit**

```bash
uv run pytest tests/ -q
git add plugin/autoauthor/skills/draft/SKILL.md plugin/autoauthor/skills/status/SKILL.md
git commit -F - <<'EOF'
fix: draft builds its file list from the form, scaffolds canon.md, and reconciles state against git history

Draft named the novel's five layer files literally, appended canon
to a file nobody created at compressed forms, and derived the resume
point from chapters/ alone — which redrafted a story whose HEAD said
"revision complete".
EOF
```

## Task B4: `world.md` references become role references in drafting rules and packs

**Files:**
- Modify: `skills/draft/references/drafting-rules.md:30-32`
- Modify: `shared/genres/erotica.md`, `fantasy.md`, `paranormal-romance.md`, `romantasy.md`, `science-fiction.md` (one line each in `## Drafting Rules`)
- Test: `tests/test_no_genre_leak.py` — no change; but add a guard `tests/test_drafting_rules_name_roles.py`

- [ ] **Step 1: Write the failing test**

```python
"""Drafting rules may not name world.md as if every form built one.

At `short-story` the resolver reports layers [voice, characters, outline];
the facts a drafting rule wants live in the outline's facts section. A rule
that says "defined in world.md" reads, to a drafter who finds no world.md,
as a rule that does not apply — which is the direct route to the vagueness
the rule exists to prevent (draft findings 2026-08-17, #7).
"""
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent / "plugin/autoauthor"
PACKS = sorted((ROOT / "shared/genres").glob("*.md"))
RULES = ROOT / "skills/draft/references/drafting-rules.md"


def drafting_rules_section(text):
    m = re.search(r"^## Drafting Rules.*?(?=^## |\Z)", text, re.S | re.M)
    return m.group(0) if m else ""


@pytest.mark.parametrize("path", PACKS, ids=lambda p: p.stem)
def test_pack_drafting_rules_do_not_name_world_md(path):
    section = drafting_rules_section(path.read_text(encoding="utf-8"))
    assert "world.md" not in section, (
        f"{path.name}: a drafting rule names world.md literally; name the "
        "role (the world layer, or the outline's facts section where the "
        "form builds no world.md)")


def test_base_drafting_rules_do_not_name_world_md():
    assert "world.md" not in RULES.read_text(encoding="utf-8")
```

- [ ] **Step 2: Run it to see it fail**

Run: `uv run pytest tests/test_drafting_rules_name_roles.py -q`
Expected: 6 failures (5 packs + base rules).

- [ ] **Step 3: Edit the six lines**

`skills/draft/references/drafting-rules.md` rule 6 — replace:

```
6. The genre's central system, where it appears, manifests as SPECIFIC
   physical or concrete detail defined in world.md — never vague. Use the
   exact established specifics.
```
with:
```
6. The genre's central system, where it appears, manifests as SPECIFIC
   physical or concrete detail defined in the fact-bearing layer — the
   world bible where the form builds one, otherwise the outline's facts
   section — never vague. Use the exact established specifics; a rule
   you cannot find written down is one you have not been given.
```

`shared/genres/erotica.md` rule 26: replace `` in the register `world.md` established under "The Vocabulary of This World" `` with `in the register the world layer established under "The Vocabulary of This World"`; and `Decide the register once, in the world bible, and hold it` stays (it names the layer by role already).

`shared/genres/fantasy.md` rule 25: replace `defined in world.md — never vague discomfort.` with `defined in the world layer (the outline's facts section where the form builds no world bible) — never vague discomfort.`

`shared/genres/romantasy.md` rule 25: same replacement as fantasy.

`shared/genres/paranormal-romance.md` rule 25: replace `established in world.md — the same cold` with `established in the world layer (or the outline's facts section, where the form builds no world bible) — the same cold`.

`shared/genres/science-fiction.md` rule 26: replace `` defined in `world.md` — a named sensation `` with `defined in the world layer (the outline's facts section where the form builds no world bible) — a named sensation`.

- [ ] **Step 4: Run tests**

Run: `uv run pytest tests/test_drafting_rules_name_roles.py tests/test_no_genre_leak.py tests/test_required_reading_is_clean.py -q`
Expected: all pass. Then `uv run pytest tests/ -q` and `for f in plugin/autoauthor/shared/genres/*.md; do python3 plugin/autoauthor/shared/scripts/validate_genre_pack.py "$f" >/dev/null || echo "FAIL $f"; done` — no output.

- [ ] **Step 5: Commit**

```bash
git add tests/test_drafting_rules_name_roles.py plugin/autoauthor/skills/draft/references/drafting-rules.md plugin/autoauthor/shared/genres/{erotica,fantasy,paranormal-romance,romantasy,science-fiction}.md
git commit -F - <<'EOF'
fix: drafting rules name the fact-bearing layer by role, not as world.md

Six rules said "defined in world.md". At short-story no world.md
exists and the facts sit in the outline; a drafter reading the literal
filename concludes the rule does not apply. A test now keeps the
Drafting Rules blocks free of the literal.
EOF
```

## Task B5: Two wording nits — clean-tree slop-pass commit, `attempts.tsv` on the first attempt

**Files:**
- Modify: `skills/draft/SKILL.md:117-123` and `:148`

- [ ] **Step 1: attempts.tsv**

Replace `During the retry loop, append each attempt's row to the untracked \`eval_logs/attempts.tsv\` (same columns as results.tsv).` with `Append EVERY attempt's row to the untracked \`eval_logs/attempts.tsv\` (same columns as results.tsv) — including the first, whether or not it passes; a chapter that clears on attempt 1 has one row there and one in results.tsv.`

- [ ] **Step 2: Clean-tree commit**

Replace `   Commit \`post-draft slop pass\`.` with `   Commit \`post-draft slop pass\`. If the pass made no edits (zero hits, clean tree), report the clean result and skip the commit — \`git commit\` with nothing staged exits non-zero, and a literal reading ended one run's phase on a failed command.`

- [ ] **Step 3: Commit**

```bash
uv run pytest tests/ -q
git add plugin/autoauthor/skills/draft/SKILL.md
git commit -F - <<'EOF'
docs: draft writes attempts.tsv on every attempt and skips the slop-pass commit on a clean tree

Both were undefined for the happy path, which is what four of four
chapters hit on one run.
EOF
```

---

# Part C — Facts checker, canon gate, and the plan carrying quoted text

Covers: draft findings 2, 3; foundation findings 10, 11.

## Task C1: `continuity_check.py`

**Files:**
- Create: `shared/scripts/continuity_check.py`
- Test: `tests/test_continuity_check.py`

- [ ] **Step 1: Write the failing tests**

```python
"""Numbers a chapter states that no fact-bearing document states.

Eight canon defects across four drafted chapters on one run were every one
of them a clock time or a bare number derivable from the outline's fact
table (draft findings 2026-08-17, #2). Nothing mechanical looked for them.
This does not know which unmatched numbers are legitimate inventions and
does not need to: a short "not found" list a drafter eyeballs is the point.
"""
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).parent.parent / "plugin/autoauthor/shared/scripts"
sys.path.insert(0, str(SCRIPTS))

import continuity_check  # noqa: E402

CLI = SCRIPTS / "continuity_check.py"

OUTLINE = """# Outline

## Facts the story must not contradict
- The receive window opens at 04:02 and closes at 14:02.
- Pua is fifty-two at the start; Mele left in 2091.
- Eight blocks have arrived in eighty years.
"""

CHAPTER = """# Chapter 2: The Window

At 03:30 she read the front of the block. Pua had been sixty then.
Eight of them in eighty years, she thought, twenty-six characters each.
The window opened at 04:02.
"""


def test_extracts_clock_times_and_integers_and_number_words():
    found = continuity_check.numbers_in(CHAPTER)
    keys = {n.key for n in found}
    assert "03:30" in keys
    assert "04:02" in keys
    assert 60 in keys      # "sixty"
    assert 26 in keys      # "twenty-six"
    assert 80 in keys      # "eighty"


def test_reports_unmatched_numbers_and_matched_ones_separately(tmp_path):
    (tmp_path / "outline.md").write_text(OUTLINE)
    (tmp_path / "chapters").mkdir()
    (tmp_path / "chapters/ch_02.md").write_text(CHAPTER)
    result = subprocess.run(
        [sys.executable, str(CLI), "chapters/ch_02.md"],
        capture_output=True, text=True, cwd=tmp_path)
    assert result.returncode == 1, result.stdout + result.stderr
    out = result.stdout
    assert "NOT FOUND" in out
    assert "03:30" in out.split("NOT FOUND", 1)[1]
    assert "sixty" in out.split("NOT FOUND", 1)[1]
    assert "04:02" in out.split("NOT FOUND", 1)[0]   # matched


def test_clean_chapter_exits_zero(tmp_path):
    (tmp_path / "outline.md").write_text(OUTLINE)
    (tmp_path / "chapters").mkdir()
    (tmp_path / "chapters/ch_01.md").write_text(
        "# Chapter 1\n\nThe window opened at 04:02. Eight blocks in eighty years.\n")
    result = subprocess.run(
        [sys.executable, str(CLI), "chapters/ch_01.md"],
        capture_output=True, text=True, cwd=tmp_path)
    assert result.returncode == 0, result.stdout + result.stderr


def test_small_number_words_are_ignored_by_default():
    found = continuity_check.numbers_in("One of the two doors. Three keys.")
    assert {n.key for n in found} == {3}


def test_reads_every_fact_bearing_file_that_exists(tmp_path):
    (tmp_path / "outline.md").write_text("# Outline\n")
    (tmp_path / "canon.md").write_text("- The ship left in 2091. (ch_01)\n")
    (tmp_path / "chapters").mkdir()
    (tmp_path / "chapters/ch_03.md").write_text("# Ch 3\n\nShe left in 2091.\n")
    result = subprocess.run(
        [sys.executable, str(CLI), "chapters/ch_03.md"],
        capture_output=True, text=True, cwd=tmp_path)
    assert result.returncode == 0, result.stdout + result.stderr
```

- [ ] **Step 2: Run to see them fail**

Run: `uv run pytest tests/test_continuity_check.py -q`
Expected: ImportError / failures.

- [ ] **Step 3: Write the script**

```python
#!/usr/bin/env python3
"""List every number a chapter states and whether a fact-bearing document
states it too.

Usage (from the project directory):
  python continuity_check.py chapters/ch_04.md
  python continuity_check.py chapters/ch_*.md
  python continuity_check.py chapters/ch_04.md --facts outline.md canon.md

Why this exists. On one drafting run the weakest dimension in three of four
chapters was canon_compliance, and every violation the judges raised was a
clock time or a bare number — a character read a block before the window
opened, an age off by eight years, a distance wrong by orders of magnitude.
All eight were derivable from the outline's fact table. slop_score.py runs
mechanically on every chapter and catches diction; nothing ran on facts.

What it does. Extracts from the chapter every clock time (`04:02`), every
digit-run (`2091`, `1,200`, `0.98`), and every number word or hyphenated
number word phrase (`sixty`, `twenty-six`, `eighty`), then looks for the
same value in the fact-bearing documents that exist — by default
outline.md, canon.md, world.md, characters.md, whichever are present. It
prints two lists: FOUND and NOT FOUND, and exits 1 if NOT FOUND is
non-empty.

What it does not do. It cannot tell a legitimate invention ("she counted
eleven steps") from a contradiction, and it does not try. It hands the
drafter a short list to eyeball before the judge is dispatched. Number
words below MIN_WORD_VALUE are skipped because "one" and "two" are
articles in disguise; digit forms are never skipped.
"""
import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

DEFAULT_FACT_FILES = ("outline.md", "canon.md", "world.md", "characters.md")
MIN_WORD_VALUE = 3

UNITS = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11,
    "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
    "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19,
}
TENS = {
    "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60,
    "seventy": 70, "eighty": 80, "ninety": 90,
}
SCALES = {"hundred": 100, "thousand": 1000, "million": 1_000_000}
NUMBER_WORDS = set(UNITS) | set(TENS) | set(SCALES)

CLOCK_RE = re.compile(r"\b(\d{1,2}:\d{2})\b")
DIGITS_RE = re.compile(r"(?<![\d:])(\d+(?:[.,]\d+)*)(?![\d:])")
WORDS_RE = re.compile(
    r"\b((?:" + "|".join(sorted(NUMBER_WORDS, key=len, reverse=True)) +
    r")(?:[-\s](?:" + "|".join(sorted(NUMBER_WORDS, key=len, reverse=True)) +
    r"))*)\b", re.IGNORECASE)


@dataclass(frozen=True)
class Number:
    key: object      # "04:02" for clocks, int/float for values
    text: str        # as written in the chapter
    line: int


def words_to_int(phrase):
    """'twenty-six' -> 26, 'two hundred' -> 200. Returns None if unparsable."""
    total, current = 0, 0
    for w in re.split(r"[-\s]+", phrase.lower()):
        if w in UNITS:
            current += UNITS[w]
        elif w in TENS:
            current += TENS[w]
        elif w in SCALES:
            current = max(current, 1) * SCALES[w]
            if SCALES[w] >= 1000:
                total += current
                current = 0
        else:
            return None
    return total + current


def _digit_key(text):
    cleaned = text.replace(",", "")
    try:
        return float(cleaned) if "." in cleaned else int(cleaned)
    except ValueError:
        return None


def numbers_in(text, min_word_value=MIN_WORD_VALUE):
    """Every number the text states, deduplicated by (key, text)."""
    found = {}
    for lineno, line in enumerate(text.splitlines(), 1):
        if line.lstrip().startswith("#"):
            continue  # "# Chapter 4" is not a fact the chapter states
        for m in CLOCK_RE.finditer(line):
            found.setdefault((m.group(1), m.group(1)), Number(m.group(1), m.group(1), lineno))
        stripped = CLOCK_RE.sub(" ", line)
        for m in DIGITS_RE.finditer(stripped):
            key = _digit_key(m.group(1))
            if key is not None:
                found.setdefault((key, m.group(1)), Number(key, m.group(1), lineno))
        for m in WORDS_RE.finditer(stripped):
            value = words_to_int(m.group(1))
            if value is None or value < min_word_value:
                continue
            found.setdefault((value, m.group(1)), Number(value, m.group(1), lineno))
    return list(found.values())


def fact_keys(paths, min_word_value=MIN_WORD_VALUE):
    keys = set()
    for p in paths:
        if p.exists():
            keys.update(n.key for n in numbers_in(p.read_text(encoding="utf-8"), 0))
    return keys


def check(chapter_path, fact_paths):
    text = chapter_path.read_text(encoding="utf-8")
    facts = fact_keys(fact_paths)
    numbers = sorted(numbers_in(text), key=lambda n: (n.line, n.text))
    found = [n for n in numbers if n.key in facts]
    missing = [n for n in numbers if n.key not in facts]
    return found, missing


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("chapters", nargs="+", help="chapter files to check")
    parser.add_argument("--facts", nargs="+", metavar="FILE",
                        help="fact-bearing files (default: whichever of "
                             f"{', '.join(DEFAULT_FACT_FILES)} exist in CWD)")
    args = parser.parse_args(argv)

    fact_paths = ([Path(f) for f in args.facts] if args.facts
                  else [Path(f) for f in DEFAULT_FACT_FILES])
    present = [p for p in fact_paths if p.exists()]
    if not present:
        print("ERROR: no fact-bearing files found "
              f"(looked for {', '.join(str(p) for p in fact_paths)})", file=sys.stderr)
        return 2

    any_missing = False
    for ch in args.chapters:
        found, missing = check(Path(ch), present)
        print(f"=== {ch} — facts from {', '.join(p.name for p in present)} ===")
        print(f"FOUND ({len(found)}):")
        for n in found:
            print(f"  L{n.line:<4} {n.text}")
        print(f"NOT FOUND ({len(missing)}) — check each against the fact table:")
        for n in missing:
            print(f"  L{n.line:<4} {n.text}")
        print()
        any_missing = any_missing or bool(missing)
    return 1 if any_missing else 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run tests**

Run: `uv run pytest tests/test_continuity_check.py -q`
Expected: 5 passed. If `test_extracts_clock_times_and_integers_and_number_words` fails on `26`, check `WORDS_RE` handles the hyphen — the alternation must be sorted longest-first (it is) and `[-\s]` must join tokens.

- [ ] **Step 5: Add the script to the CLAUDE.md orientation table**

In `CLAUDE.md`'s Orientation table, after the `slop_score.py` row add:
`| \`continuity_check.py\` | numbers a chapter states that no fact-bearing document states |`

- [ ] **Step 6: Commit**

```bash
git add plugin/autoauthor/shared/scripts/continuity_check.py tests/test_continuity_check.py CLAUDE.md
git commit -F - <<'EOF'
feat: continuity_check.py lists a chapter's numbers that no fact-bearing document states

Every canon violation on one drafting run was a clock time or a bare
number derivable from the outline's fact table; slop_score.py ran on
every chapter and nothing ran on facts. This prints FOUND / NOT FOUND
and exits 1 on the latter; it does not judge, it hands the drafter a
short list.
EOF
```

## Task C2: Wire the checker and a canon gate with a surgical-correction branch into draft

**Files:**
- Modify: `skills/draft/SKILL.md:56-71` (step 3), `:108-123` (step 6)
- Modify: `skills/draft/references/drafting-rules.md` (new section after Core rules)

- [ ] **Step 1: Step 3 — run it beside slop_score**

After the slop_score code block and its explanatory paragraph in step 3, before `Note the \`slop_penalty\`.`, add:

```markdown
   Then, in the same breath:

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/continuity_check.py" chapters/ch_NN.md
   ```

   It lists every clock time and number the chapter states and whether
   any fact-bearing document (outline, canon, world, characters —
   whichever exist) states it too. Read the NOT FOUND list against the
   outline's fact table before dispatching the judge. Most entries will
   be harmless inventions; the ones that are not are the cheapest
   defects you will ever fix — six of eight canon violations on one run
   were single-word edits, and every one of them survived into a later
   phase because nothing looked. Fix what is wrong, re-run both scripts,
   then judge.
```

- [ ] **Step 2: Step 6 — the gate and the correction branch**

Replace `6. **Gate.** Final score > 6.0 → keep: update state.json` with:

```markdown
6. **Gate.** Keep requires BOTH: final score > 6.0 AND the judge's
   `canon_compliance.violations` list is empty (or `canon_compliance`
   scored 7 or higher). A canon violation is unlike a weak sentence: it
   is cheap now, it compounds (a wrong line in ch1 forced ch2 to write
   around it on one run, and the judge discounted ch2's version as a
   repeat), and it is invisible to revision, whose instruments cut and
   compress and read a wrong number as perfectly good prose.

   **If the chapter fails ONLY on canon** — score clears, violations
   listed — do not discard. Take the surgical-correction branch: apply
   edits that address the named violations and nothing else, re-run
   step 3, re-dispatch the judge, and log the attempt row as `correct`
   rather than `keep`/`discard`. A correction counts against the
   5-attempt budget so it cannot loop. Cost is one edit pass and one
   dispatch, against a debt that otherwise waits for a phase that will
   not see it.

   Score clears and canon clean → keep: update state.json
```

And in the row-format line at the end of step 6, change `<keep|discard|noscore>` to `<keep|discard|correct|noscore>`.

- [ ] **Step 3: Drafting rules — the pre-scoring self-check**

In `skills/draft/references/drafting-rules.md`, after the Core rules block (after rule 13) and before `## Anti-pattern rules (14–24)`, add:

```markdown
## Pre-scoring self-check

Before running the slop score, list every clock time and every bare
number you wrote in this chapter — ages, counts, dates, distances,
durations — and check each against the outline's facts and clock
sections. A number you cannot trace to that section is a defect until
you have decided otherwise, not a detail. `continuity_check.py` prints
the list; the deciding is yours. If you do not need the number, do not
write one.
```

- [ ] **Step 4: Commit** (`tests/test_results_tsv.py` does not enumerate keep_discard values — verified — so `correct` needs no test change)

```bash
uv run pytest tests/ -q
git add plugin/autoauthor/skills/draft/SKILL.md plugin/autoauthor/skills/draft/references/drafting-rules.md
git commit -F - <<'EOF'
fix: draft gates on canon violations and adds a surgical-correction branch that is not a discard

Four chapters shipped eight known arithmetic errors because the gate
was score-only and the only moves after judging were keep or reset.
Correction is one edit and one dispatch, counted against the attempt
budget.
EOF
```

## Task C3: Foundation — verify seed arithmetic; the plan contains what the story quotes

**Files:**
- Modify: `skills/foundation/SKILL.md:35-44` (Setup step 3)
- Modify: `skills/foundation/references/layer-guides.md:191-206` (outline part 1 CONSTRAINTS)
- Modify: `shared/templates/outline.md:14-15`

- [ ] **Step 1: Setup step 3**

After the bullet `- the project's \`seed.txt\` if present; otherwise derive the premise ... never require seed.txt).` add a new numbered step:

```markdown
3b. **Check the seed's arithmetic before building anything.** If the
   seed states quantities the premise depends on — dates, ages,
   distances, rates, budgets, intervals — verify them against each
   other now, and write the resolved set into outline.md's `## Facts
   the story must not contradict` section as the single source. A
   seed's numbers are an input, not an authority: one seed conflated a
   per-year allowance with an annual window in a way that could not
   both be true, and it took two scored iterations to surface because
   nothing asked Setup to check. Foundation inherits a seed's errors
   and multiplies them across three documents.
```

- [ ] **Step 2: layer-guides outline constraints**

In `## outline.md part 1`, in the CONSTRAINTS list, after `- The climax must be mechanically resolvable ... already on the board.` add:

```markdown
- Any text the story quotes verbatim — a letter, a prophecy, a
  contract, a transmission, a will, a song — must exist IN FULL in the
  plan, at the length the world's own rules permit. A plan that
  describes such an object instead of containing it has left the scene
  it appears in unplanned, and no judge can check whether the object
  does what the outline claims. On one run the single most useful
  planning move was writing the central letter out at exactly the
  byte budget the plan allowed; two evals then caught it contradicting
  its own frame, which is only possible because the text existed.
- The document opens with a `## Facts the story must not contradict`
  section: the clock, the fact table, every number a chapter may need
  to state. This is what `continuity_check.py` reads during drafting.
```

- [ ] **Step 3: Template**

In `shared/templates/outline.md`, after the `## Themes` block, add:

```markdown
## Facts the story must not contradict
<!-- The authoritative clock and the fact table: dates, ages, distances,
     counts, rates, durations — every number a chapter may state, in one
     place, reconciled with each other. Drafting's continuity check reads
     this section; a number that lives only in prose elsewhere is one it
     cannot find. Keep it a list, not an argument. -->
```

- [ ] **Step 4: Commit**

```bash
uv run pytest tests/ -q
git add plugin/autoauthor/skills/foundation/SKILL.md plugin/autoauthor/skills/foundation/references/layer-guides.md plugin/autoauthor/shared/templates/outline.md
git commit -F - <<'EOF'
feat: the outline carries a facts section, foundation checks the seed's arithmetic into it, and quoted objects exist in full

Gives continuity_check.py a section to read, and closes two foundation
findings: seed numbers were inherited unchecked, and nothing required a
letter the climax reads aloud to exist anywhere but as a description.
EOF
```

---

# Part D — Revision cutting: protection, splice audit, gating

Covers: revision findings 2, 3, 4, 9.

## Task D1: `apply_cuts.py --protect-file`

**Files:**
- Modify: `shared/scripts/apply_cuts.py`
- Test: `tests/test_apply_cuts.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_apply_cuts.py`:

```python
def test_protect_file_skips_cuts_that_touch_a_protected_line(tmp_path):
    """A protected substring anywhere in a cut's quote — or a quote that is a
    fragment of a protected line — is skipped and reported, not applied.
    Whitespace is normalised on both sides."""
    setup_project(tmp_path)
    (tmp_path / "edit_logs/protected.md").write_text(
        "# protected\n"
        "\n"
        "every person in the room   already knew\n"   # ws-normalised match
    )
    result = run_in(tmp_path, "3", "--protect-file", "edit_logs/protected.md")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "PROTECT" in result.stdout
    text = (tmp_path / "chapters/ch_03.md").read_text()
    assert "He realized then" in text  # the OVER-EXPLAIN cut was NOT applied


def test_protect_file_lines_starting_with_hash_or_blank_are_ignored(tmp_path):
    setup_project(tmp_path)
    (tmp_path / "edit_logs/protected.md").write_text("# nothing here\n\n")
    result = run_in(tmp_path, "3", "--protect-file", "edit_logs/protected.md")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "He realized then" not in (tmp_path / "chapters/ch_03.md").read_text()
```

- [ ] **Step 2: Run to see it fail**

Run: `uv run pytest tests/test_apply_cuts.py -q`
Expected: 2 failures (`unrecognized arguments: --protect-file`).

- [ ] **Step 3: Implement**

In `shared/scripts/apply_cuts.py`:

Update the module docstring usage block to add:
```
  python apply_cuts.py all --protect-file edit_logs/protected.md
                                                           # never cut a line listed there
```

After `MIN_QUOTE_LEN = 25` add:

```python
_WS = re.compile(r"\s+")


def _norm(s: str) -> str:
    return _WS.sub(" ", s).strip()


def load_protected(path: Path | None) -> list[str]:
    """Newline-delimited substrings that must never be cut.

    Blank lines and lines starting with '#' are ignored, so the skill can
    keep the file as readable markdown with a heading per source (chapter
    judges' three_strongest_sentences, the outline's plant/harvest quotes).
    Whitespace-normalised, because the file is hand-maintained.
    """
    if path is None:
        return []
    lines = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        lines.append(_norm(line))
    return lines


def protected_by(quote: str, protected: list[str]) -> str | None:
    """The protected line a quote collides with, or None.

    Collides in either direction: the quote contains a protected line
    (the cut would remove it), or a protected line contains the quote (the
    cut would remove part of it). Both destroy the line.
    """
    q = _norm(quote)
    if not q:
        return None
    for p in protected:
        if p in q or q in p:
            return p
    return None
```

Change `process_chapter`'s signature and body:

```python
def process_chapter(
    chapter_num: int,
    type_filter: set[str] | None,
    min_fat: int,
    dry_run: bool,
    protected: list[str] | None = None,
) -> dict:
    """Process cuts for one chapter. Returns stats dict."""
    stats = {"applied": 0, "failed": 0, "skipped": 0, "protected": 0,
             "words_removed": 0, "error": None}
```

and inside the `for cut in cuts:` loop, immediately after the type filter block and BEFORE the REWRITE skip (a protected line must be reported even when the cut is a REWRITE the skill would otherwise apply by hand):

```python
        hit = protected_by(quote, protected or [])
        if hit:
            stats["protected"] += 1
            print(f"  PROTECT [{cut_type}] touches protected line: {hit[:60]}")
            continue
```

In `main()`, add the argument:

```python
    parser.add_argument(
        "--protect-file",
        type=Path,
        metavar="PATH",
        help="Newline-delimited substrings that must never be cut; a cut "
             "whose quote contains one (or is contained by one) is skipped "
             "and reported as PROTECT.",
    )
```

after parsing: `protected = load_protected(args.protect_file)`; pass `protected` into `process_chapter(ch_num, type_filter, args.min_fat, args.dry_run, protected)`; add `"protected": 0` to `totals`; and change the summary line to:

```python
    print(f"Applied: {totals['applied']}  |  Failed: {totals['failed']}  |  "
          f"Skipped: {totals['skipped']}  |  Protected: {totals['protected']}")
```

- [ ] **Step 4: Run tests**

Run: `uv run pytest tests/test_apply_cuts.py -q`
Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add plugin/autoauthor/shared/scripts/apply_cuts.py tests/test_apply_cuts.py
git commit -F - <<'EOF'
feat: apply_cuts.py --protect-file skips any cut that touches a protected line

The mechanical pass ran before any protection existed; in one cycle it
cut the sentence that states the append-only archive the climax turns
on, which a prior judge had listed among the chapter's three strongest.
The restore came from reading the diff, not from any check.
EOF
```

## Task D2: `splice_audit.py`

**Files:**
- Create: `shared/scripts/splice_audit.py`
- Test: `tests/test_splice_audit.py`

- [ ] **Step 1: Write the failing tests**

```python
"""Splice damage after mechanical cuts.

Six mechanical cuts in one cycle produced five defects; two were outside
the checklist the skill named, and one (trailing whitespace) survived a
whole cycle. Re-implemented three times in one session with different
checks each time — hence a script (revision findings 2026-08-17, #4).
"""
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).parent.parent / "plugin/autoauthor/shared/scripts"
sys.path.insert(0, str(SCRIPTS))

import splice_audit  # noqa: E402

CLI = SCRIPTS / "splice_audit.py"

BEFORE = """# Chapter 4

"Okay," Pua said, and put the phone down, and did not look at anyone. She called the room.

There was nobody in the room for it, not really, and her mother had gone back to work.

Kalei went past it with the cooler. Her mother worked here.

Somebody said "ho" very quietly.
"""

AFTER = """# Chapter 4

"Okay," Pua said, and put the phone down,  She called the room.

There was nobody in the room for it, , and her mother had gone back to work. 

Kalei went past it with the cooler. Her mother worked here.

 Somebody said "ho" very quietly.
"""


def test_finds_each_defect_class_only_in_changed_paragraphs():
    findings = splice_audit.audit(BEFORE, AFTER)
    kinds = {f.kind for f in findings}
    assert "glued-sentence" in kinds        # ", She"
    assert "double-space" in kinds
    assert "doubled-comma" in kinds
    assert "trailing-whitespace" in kinds
    assert "leading-whitespace" in kinds
    # unchanged paragraph is not audited
    assert not any("cooler" in f.text for f in findings)


def test_proper_noun_after_comma_is_not_a_glued_sentence():
    before = "She left, Kalei said, and that was that.\n"
    after = "She left, Kalei said.\n"
    kinds = {f.kind for f in splice_audit.audit(before, after)}
    assert "glued-sentence" not in kinds   # 'Kalei' follows a comma in BEFORE


def test_terminal_punctuation_and_dangling_comma():
    before = "He waited for the answer, and it came.\n"
    after = "He waited for the answer,\n"
    kinds = {f.kind for f in splice_audit.audit(before, after)}
    assert "ends-on-comma" in kinds
    after2 = "He waited for the answer\n"
    kinds2 = {f.kind for f in splice_audit.audit(before, after2)}
    assert "no-terminal-punctuation" in kinds2


def test_cli_exits_one_on_findings_and_zero_when_clean(tmp_path):
    (tmp_path / "before").mkdir()
    (tmp_path / "chapters").mkdir()
    (tmp_path / "before/ch_04.md").write_text(BEFORE)
    (tmp_path / "chapters/ch_04.md").write_text(AFTER)
    r = subprocess.run([sys.executable, str(CLI), "chapters/ch_04.md",
                        "--before-dir", "before"],
                       capture_output=True, text=True, cwd=tmp_path)
    assert r.returncode == 1, r.stdout + r.stderr
    assert "glued-sentence" in r.stdout
    (tmp_path / "chapters/ch_04.md").write_text(BEFORE)
    r = subprocess.run([sys.executable, str(CLI), "chapters/ch_04.md",
                        "--before-dir", "before"],
                       capture_output=True, text=True, cwd=tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr


def test_cli_defaults_to_git_head_for_the_before_text(tmp_path):
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    (tmp_path / "chapters").mkdir()
    (tmp_path / "chapters/ch_04.md").write_text(BEFORE)
    subprocess.run(["git", "add", "-A"], cwd=tmp_path, check=True)
    subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t",
                    "commit", "-qm", "before"], cwd=tmp_path, check=True)
    (tmp_path / "chapters/ch_04.md").write_text(AFTER)
    r = subprocess.run([sys.executable, str(CLI), "chapters/ch_04.md"],
                       capture_output=True, text=True, cwd=tmp_path)
    assert r.returncode == 1, r.stdout + r.stderr
    assert "doubled-comma" in r.stdout
```

- [ ] **Step 2: Run to see them fail**

Run: `uv run pytest tests/test_splice_audit.py -q`
Expected: ImportError.

- [ ] **Step 3: Write the script**

```python
#!/usr/bin/env python3
"""Audit chapters for splice damage after a mechanical cut pass.

Usage (from the project directory):
  python splice_audit.py chapters/ch_*.md                    # compare against git HEAD
  python splice_audit.py chapters/ch_04.md --before-dir /tmp/precut
  python splice_audit.py chapters/ch_*.md --ref cycle-3-start  # any git ref

apply_cuts.py deletes quoted spans mid-paragraph. A cut that removes a
trailing or interior sentence can leave a paragraph ending on a comma,
ending with no terminal punctuation, two speeches glued into one line, a
doubled comma, or stray whitespace at either end. Neither the word count
nor the slop scorer sees any of it. This audits ONLY paragraphs that
changed between the before-text and the current text — unchanged prose is
not this pass's damage and would drown the signal — and exits 1 if it
found anything.

The checks, each named in the output so a repair can be logged by kind:
  ends-on-comma            paragraph ends in , or ;
  no-terminal-punctuation  paragraph ends without . ! ? … a closing quote,
                           a closing bracket, or an em-dash
  double-space             two spaces inside a paragraph
  doubled-comma            ", ," with any whitespace between
  empty-quotes             "" or " " — an emptied speech
  space-before-punct       whitespace before , . ; : ! ?
  doubled-word             "the the", case-insensitive
  glued-sentence           [,;] then space then a capitalised word that did
                           NOT follow a comma or semicolon anywhere in the
                           before-text — proper nouns after commas are
                           learned from the before-text, so "left, Kalei
                           said" passes and "down,  She called" does not
  leading-whitespace       paragraph starts with a space
  trailing-whitespace      paragraph ends with a space (this one survived
                           a whole cycle by eye)

Expect one or two false positives from intentional oddities; check them,
then leave them.
"""
import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

TERMINAL = '.!?…"”’\')*_—–'


@dataclass(frozen=True)
class Finding:
    kind: str
    para: int
    text: str


def paragraphs(text):
    """Non-empty, non-heading paragraphs with their index in the raw split."""
    out = []
    for i, p in enumerate(text.split("\n\n")):
        raw = p.rstrip("\n")
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        out.append((i, raw))
    return out


def _capitalised_after_comma(text):
    """Words that legitimately follow , or ; in the before-text — proper
    nouns, 'I', dialogue tags with names — so they are not glued sentences."""
    return {m.group(1) for m in re.finditer(r"[,;]\s+([A-Z][\w'’-]*)", text)}


def audit_paragraph(idx, raw, allow):
    findings = []
    stripped = raw.strip()
    add = lambda kind: findings.append(Finding(kind, idx, stripped[:80]))  # noqa: E731

    if raw != raw.lstrip(" \t"):
        add("leading-whitespace")
    if raw != raw.rstrip(" \t"):
        add("trailing-whitespace")
    if stripped.endswith((",", ";")):
        add("ends-on-comma")
    elif stripped and stripped[-1] not in TERMINAL:
        add("no-terminal-punctuation")
    if "  " in stripped:
        add("double-space")
    if re.search(r",\s*,", stripped):
        add("doubled-comma")
    if re.search(r'"\s*"', stripped) or re.search(r"“\s*”", stripped):
        add("empty-quotes")
    if re.search(r"\s[,.;:!?]", stripped):
        add("space-before-punct")
    if re.search(r"\b(\w+)\s+\1\b", stripped, re.IGNORECASE):
        add("doubled-word")
    for m in re.finditer(r"[,;]\s+([A-Z][\w'’-]*)", stripped):
        if m.group(1) not in allow and m.group(1) != "I":
            add("glued-sentence")
            break
    return findings


def audit(before, after):
    """Findings in paragraphs of `after` that do not appear verbatim in `before`."""
    before_paras = {raw.strip() for _, raw in paragraphs(before)}
    allow = _capitalised_after_comma(before)
    findings = []
    for idx, raw in paragraphs(after):
        if raw.strip() in before_paras and raw == raw.strip():
            continue
        findings.extend(audit_paragraph(idx, raw, allow))
    return findings


def before_text(path, before_dir, ref):
    if before_dir is not None:
        p = Path(before_dir) / Path(path).name
        return p.read_text(encoding="utf-8") if p.exists() else ""
    r = subprocess.run(["git", "show", f"{ref}:{path}"],
                       capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("chapters", nargs="+")
    parser.add_argument("--before-dir", metavar="DIR",
                        help="directory holding the pre-cut copies (same filenames)")
    parser.add_argument("--ref", default="HEAD",
                        help="git ref to read the pre-cut text from (default HEAD)")
    args = parser.parse_args(argv)

    total = 0
    for ch in args.chapters:
        after = Path(ch).read_text(encoding="utf-8")
        before = before_text(ch, args.before_dir, args.ref)
        findings = audit(before, after)
        total += len(findings)
        print(f"=== {ch}: {len(findings)} finding(s) ===")
        for f in findings:
            print(f"  [{f.kind}] para {f.para}: {f.text}")
    print(f"\n{total} finding(s) total")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run tests**

Run: `uv run pytest tests/test_splice_audit.py -q`
Expected: 5 passed. If `test_finds_each_defect_class_only_in_changed_paragraphs` fails on `trailing-whitespace`, check the `AFTER` fixture line `...gone back to work. ` still carries its trailing space (editors strip it — the test file must preserve it; if yours strips on save, build the string with `"work. " + "\n"`).

- [ ] **Step 5: Orientation table + commit**

Add to `CLAUDE.md`'s table: `| \`splice_audit.py\` | paragraph-level damage a mechanical cut leaves behind |`

```bash
git add plugin/autoauthor/shared/scripts/splice_audit.py tests/test_splice_audit.py CLAUDE.md
git commit -F - <<'EOF'
feat: splice_audit.py — the post-cut damage checklist as a script, with the four checks the prose list missed

Glued sentence, doubled comma, leading and trailing whitespace were
outside the skill's list; the last survived a full cycle. The audit
was re-implemented three times in one session with different checks
each time.
EOF
```

## Task D3: Wire protection, the audit, and cuts gating into the revise skill

**Files:**
- Modify: `skills/revise/SKILL.md:56-134` (Diagnose steps 2–3), `:171-244` (Fix), `:340-341` (Measure step 3)

- [ ] **Step 1: Build `protected.md` before the mechanical pass**

Insert a new Diagnose step between step 1 (arc_summary) and step 2 (adversarial edit), renumbering the rest 3→4, 4→5 (and update the "Fix step 1"/"step 4" cross-references in the same file: `the reader panel in step 4` → `step 5`; `Fix step 1` stays):

```markdown
2. **Build `edit_logs/protected.md`** (create on cycle 1, append every
   cycle after). It is a newline-delimited list of lines no cutting
   pass may touch, and it comes from two sources that already exist:
   - every entry in `three_strongest_sentences` from every chapter
     verdict in `eval_logs/` (drafting and prior revision cycles);
   - every line quoted in outline.md's plant/harvest table and every
     `Plants:`/`Payoffs:` entry that quotes prose.
   Group them under `#` headings by source; the scripts ignore
   headings and blank lines. Cutting judges see one chapter and have
   no memory: across three cycles on one project five lines were
   protected by hand and two of them were attacked in consecutive
   cycles, including the sentence both cycle-1 judges had named the
   chapter's strongest. Commit `cycle N: protected lines`.
```

- [ ] **Step 2: Pass it to `apply_cuts.py` and use `splice_audit.py`**

In the (now) step 4 "Apply mechanical cuts", change the command to:

```
`python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/apply_cuts.py" all --types OVER-EXPLAIN REDUNDANT --min-fat 15 --protect-file edit_logs/protected.md`
```

After `Two filters, both required:` and its two bullets, add a third bullet:

```markdown
   - **Skip any the script reported as `PROTECT`.** It reports them
     even for REWRITE cuts, because the by-hand pass would otherwise
     be the first place protection applied — and on one run it was,
     one step too late.
```

Replace the paragraph from `**Then audit for splice damage — REQUIRED, and not optional because the word counts look fine.**` through `check them, then leave them.` (two paragraphs) with:

```markdown
   **Then audit for splice damage — REQUIRED, and not optional because
   the word counts look fine.** The script deletes quoted spans
   mid-paragraph, and neither the word-count check nor the slop scorer
   detects what that leaves. Run:

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/splice_audit.py" chapters/ch_*.md
   ```

   It diffs each changed paragraph against the tree at HEAD (pass
   `--ref <sha>` for the commit that started this cycle if you have
   made intermediate commits) and names each finding by kind:
   ends-on-comma, no-terminal-punctuation, double-space, doubled-comma,
   empty-quotes, space-before-punct, doubled-word, glued-sentence,
   leading-whitespace, trailing-whitespace. Six mechanical cuts in one
   cycle produced five of these, and two kinds were outside the
   checklist this step used to carry.

   Repair each by hand against the pre-cut text: usually promoting a
   comma to a period, restoring a paragraph break, or merging two
   speeches that lost the beat between them. Re-run until it reports
   zero. Expect one or two false positives from intentional oddities
   (an emoticon on a hand-lettered sign) — check them, then leave them.
```

Keep the following paragraph (`Audit against the tree as it stood at the START of this cycle...`) as is.

- [ ] **Step 3: Gate the cuts pass after cycle 1**

At the top of the (now) step 3 "Adversarial edit", before `for EACH chapter, dispatch`, insert:

```markdown
   **Which chapters.** In cycle 1, every chapter. In later cycles, only
   chapters whose score fell last cycle, or whose last reported
   `overall_fat_percentage` was 12% or higher. Judges asked for 10–20
   cuts return 10–20 cuts whatever the fat; on a manuscript at 9–13%
   fat one run's cycle-2 pass removed 269 words, needed four
   protections and one restore, left five splice defects, and moved
   the full-novel score 7.86 → 7.86 with `overall_engagement` down a
   point. Record any chapter you skip, and why, in `edit_logs/skipped.md`.
```

Then in "Apply mechanical cuts", replace the sentence beginning `**If the run reports \`Applied: 0\` because every chapter fell under \`--min-fat 15\`,**` through `Say so in the commit message.` with:

```markdown
   **If the run reports `Applied: 0` because every chapter fell under
   `--min-fat 15`,** re-run with `--min-fat 0`, which keeps the type
   filter and drops only the gate, and say so in the commit message.
   This is the usual case, not the exception: a draft that had a
   post-draft slop pass typically comes back at 7–13% fat, and on one
   run the 15% gate excluded three of four chapters on the first pass.
```

- [ ] **Step 4: Protection in Fix, and prior-cycle skips**

In Fix step 1, before the `- *missing scene*` bullet, insert:

```markdown
   - *any item already in `edit_logs/skipped.md` from a prior cycle* →
     skip it again unless the panel supplies evidence the earlier
     verification did not have. "Cut chapter 2" carried 4/4 in three
     consecutive cycles on one run and was verified-and-skipped the
     same way each time.
```

In Fix step 3 (Rewrite), after `silently breaks its payoff chapters later.` add: `Check the old chapter's lines against \`edit_logs/protected.md\` too: a rewrite may reword a protected line, but it may not lose it.`

- [ ] **Step 5: Resync granularity**

In Measure step 1's resync procedure, after the bullet ending `replace the quote with the current paragraph containing it.` add:

```markdown
   - For any beat a prior cycle's panel consensus asked for and you
     then wrote, the summary must carry it at the granularity that was
     asked for — a scene the panel wanted gets its dialogue, not a
     clause. A 16-line exchange rendered as one clause was named
     "missing" by 3 of 4 readers in each of the next two cycles.
```

- [ ] **Step 6: Commit**

```bash
uv run pytest tests/ -q
git add plugin/autoauthor/skills/revise/SKILL.md
git commit -F - <<'EOF'
fix: revise builds a protected-lines file before cutting, audits splices by script, and gates the cuts pass after cycle 1

Wires --protect-file and splice_audit.py into Diagnose, carries
prior-cycle skips into Fix, and makes the resync keep a
panel-requested scene at scene granularity so it stops being reported
missing.
EOF
```

---

# Part E — Novel-scale literals become ratios of the resolved shape

Covers: revision finding 1; foundation findings 5, 9.

## Task E1: `gen_brief.py` clamps COMPRESS/TIGHTEN targets to a form-derived floor

**Files:**
- Modify: `shared/scripts/gen_brief.py:346-357`, `:821-835`
- Test: `tests/test_gen_brief.py`

- [ ] **Step 1: Write the failing test**

Append to `tests/test_gen_brief.py` (use the same project-setup helpers the file already has; the panel fixture must name the chapter as a `cut_candidate` so the brief type is COMPRESS):

```python
def test_compress_target_clamps_to_half_the_unit_length(tmp_path, monkeypatch):
    """55% of a 1,100-word scene is 605; the floor for a 1,200-word unit is
    600, so the target is 605. For a 900-word scene 55% is 495 and the
    floor wins: 600. Without --chapter-words the floor is the novel's 1800."""
    import json
    monkeypatch.chdir(tmp_path)
    (tmp_path / "chapters").mkdir()
    (tmp_path / "edit_logs").mkdir()
    (tmp_path / "voice.md").write_text("# Voice\n")
    (tmp_path / "chapters/ch_02.md").write_text(
        "# Chapter 2: Short\n\n" + ("word " * 900).strip() + "\n")
    (tmp_path / "edit_logs/reader_panel.json").write_text(json.dumps({
        "readers": {"editor": {"cut_candidate": "Chapter 2"}},
        "consensus": ["cut_candidate: chapter 2"],
        "disagreements": []}))
    r = subprocess.run([sys.executable, str(SCRIPT), "--panel", "2",
                        "--chapter-words", "1200", "--dry-run"],
                       capture_output=True, text=True, cwd=tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "~600 words" in r.stdout          # 495 clamped up to the 600 floor
    assert "floor 600" in r.stdout


def test_compress_target_floor_defaults_to_the_novel_1800(tmp_path, monkeypatch):
    import json
    monkeypatch.chdir(tmp_path)
    (tmp_path / "chapters").mkdir()
    (tmp_path / "edit_logs").mkdir()
    (tmp_path / "voice.md").write_text("# Voice\n")
    (tmp_path / "chapters/ch_02.md").write_text(
        "# Chapter 2: Short\n\n" + ("word " * 2400).strip() + "\n")
    (tmp_path / "edit_logs/reader_panel.json").write_text(json.dumps({
        "readers": {"editor": {"cut_candidate": "Chapter 2"}},
        "consensus": [], "disagreements": []}))
    r = subprocess.run([sys.executable, str(SCRIPT), "--panel", "2", "--dry-run"],
                       capture_output=True, text=True, cwd=tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "~1800 words" in r.stdout         # 1320 clamped up to 1800
```

`SCRIPT` is the module-level path constant already used by the file's other tests (check the top of `tests/test_gen_brief.py`; if it is named differently, use that name). `--dry-run` prints the brief to stdout; `panel_mentions_for_chapter` matches `cut_candidate` text with `\bChapter\s*2\b`, which the fixture satisfies. Only `build_panel_brief` computes a compression target (`gen_brief.py:348,354`), so no other builder needs the clamp.

- [ ] **Step 2: Run to see it fail**

Run: `uv run pytest tests/test_gen_brief.py -q -k clamps`
Expected: FAIL (`unrecognized arguments: --chapter-words`).

- [ ] **Step 3: Implement**

In `gen_brief.py`, near the other module constants add:

```python
# The novel's unit length; the floor below is 50% of it (1800), which is
# where the revision playbook's guardrail came from. A form with a shorter
# unit passes its own via --chapter-words and the floor scales with it.
DEFAULT_CHAPTER_WORDS = 3600
FLOOR_RATIO = 0.5
CHAPTER_WORDS = DEFAULT_CHAPTER_WORDS


def chapter_floor() -> int:
    return int(CHAPTER_WORDS * FLOOR_RATIO)
```

Replace the target block in `build_panel_brief`:

```python
    # Determine word count target
    if brief_type == "COMPRESS":
        target_wc = int(wc * 0.55)
        target_note = f"~{target_wc} words (compress from current {wc})"
    elif brief_type == "DRAMATIZE":
        target_wc = wc  # restructure, not expand
        target_note = f"~{target_wc} words (restructure, roughly same length)"
    elif brief_type == "TIGHTEN":
        target_wc = int(wc * 0.85)
        target_note = f"~{target_wc} words (tighten from current {wc})"
    else:
        target_note = f"~{wc} words (current length, unless changes dictate otherwise)"
```

with:

```python
    # Determine word count target. COMPRESS and TIGHTEN clamp to the floor
    # (half the resolved unit length): 55% of a chapter already near the
    # floor asked for 1,320 words on a 2,400-word chapter, and the skill
    # had to override it by hand.
    floor = chapter_floor()
    if brief_type == "COMPRESS":
        target_wc = max(int(wc * 0.55), floor)
        target_note = f"~{target_wc} words (compress from current {wc}; floor {floor})"
    elif brief_type == "DRAMATIZE":
        target_wc = wc  # restructure, not expand
        target_note = f"~{target_wc} words (restructure, roughly same length)"
    elif brief_type == "TIGHTEN":
        target_wc = max(int(wc * 0.85), floor)
        target_note = f"~{target_wc} words (tighten from current {wc}; floor {floor})"
    else:
        target_note = f"~{wc} words (current length, unless changes dictate otherwise)"
```

In `main()`, add:

```python
    parser.add_argument("--chapter-words", type=int, metavar="N",
                        help="the resolved shape.chapter_words; the compression "
                             "floor is half of it (default 3600 → 1800)")
```

and after `args = parser.parse_args()`:

```python
    global CHAPTER_WORDS
    if args.chapter_words:
        CHAPTER_WORDS = args.chapter_words
```

- [ ] **Step 4: Run tests and commit**

Run: `uv run pytest tests/test_gen_brief.py -q` — all pass.

```bash
git add plugin/autoauthor/shared/scripts/gen_brief.py tests/test_gen_brief.py
git commit -F - <<'EOF'
feat: gen_brief.py clamps compression targets to half the resolved unit length

The COMPRESS target was 55% of current with no floor; the skill told
the operator to override it by hand against a literal 1800. The floor
is now 0.5 × --chapter-words, defaulting to the novel's 3600.
EOF
```

## Task E2: Revise skill and playbook derive the floor from `shape.chapter_words`

**Files:**
- Modify: `skills/revise/SKILL.md:17-28` (Setup 2), `:124-128`, `:194-202`, `:356-360`
- Modify: `skills/revise/references/revision-playbook.md:29-35`, `:143-145`

- [ ] **Step 1: Setup computes and prints the numbers**

In Setup step 2, after `Keep the reported pack paths; every judge dispatch below needs them.` add:

```markdown
   Keep `shape.chapter_words` too, and compute — and STATE in your
   first message, so it is in the transcript — this project's length
   guardrails from it:

   ```
   unit floor  = 0.5 × shape.chapter_words   (novel 3600 → 1800; short story 1200 → 600)
   sweet spot  = 0.6–0.85 × shape.chapter_words
   ```

   Every "1800" and "2200–3000" in the playbook is the novel case of
   these ratios. On a short-story project every scene was already
   below 1800 before revision began; read literally, the guardrail
   forbade all cutting.
```

- [ ] **Step 2: Replace the literals in the skill**

Line 124: `Then verify no chapter fell below 1800 words` → `Then verify no chapter fell below the unit floor (Setup step 2)`.

Lines 199–202: replace `A COMPRESS brief sets the target at 55% of current length, which on a chapter already near the floor asks for a word count the 1800-word guardrail forbids (2,400 → 1,320). The guardrail wins; override the number by hand.` with `Pass \`--chapter-words <shape.chapter_words>\` so the script clamps COMPRESS and TIGHTEN targets to the unit floor; without it the floor is the novel's 1800. If the brief's TARGET is at the floor, the chapter has no compression left in it and the item wants a different fix.`

Line 358: `Never compress a chapter below 1800 words.` → `Never compress a unit below the floor computed in Setup (0.5 × shape.chapter_words; 1800 for a novel).`

- [ ] **Step 3: Playbook**

Replace lines 29–35:

```
Target: cut 40-60% of the chapter's words.
Keep: the 2-3 essential beats the panel identified.
WARNING: don't over-compress. Below ~1800 words is too thin for any chapter.
Sweet spot: 2200-3000 words for a compressed chapter.
WARNING: the script's COMPRESS target (55% of current) will ask for a
count under the 1800 floor on any chapter below ~3,300 words. Override
it by hand; the guardrail wins.
```

with:

```
Target: cut 40-60% of the unit's words.
Keep: the 2-3 essential beats the panel identified.
WARNING: don't over-compress. Below the unit floor — half the resolved
`shape.chapter_words`, 1800 for a novel — is too thin for any unit.
Sweet spot: 0.6–0.85 × `shape.chapter_words` (2200–3000 for a novel).
gen_brief.py clamps its COMPRESS target to the floor when given
`--chapter-words`; a brief whose TARGET sits at the floor is telling you
the chapter has no compression left, and the item wants a different fix.
```

Replace lines 143–145:

```
- **Over-compressing.** Cutting a chapter below 1800 words tends to
  make it the new weakest chapter. Sweet spot for a compressed chapter
  is 2200-3000 words.
```

with:

```
- **Over-compressing.** Cutting a unit below the floor (0.5 ×
  `shape.chapter_words`; 1800 for a novel) tends to make it the new
  weakest chapter. Sweet spot is 0.6–0.85 × the unit length
  (2200–3000 for a novel).
```

- [ ] **Step 4: Commit**

```bash
uv run pytest tests/ -q
git add plugin/autoauthor/skills/revise/SKILL.md plugin/autoauthor/skills/revise/references/revision-playbook.md
git commit -F - <<'EOF'
fix: revision guardrails are ratios of shape.chapter_words, not the novel's literals

1800 was 50% of the SF pack's chapter_words. At short-story every unit
was under 1800 before revision started and the guardrail forbade all
cutting. Setup now computes and prints the floor and sweet spot.
EOF
```

## Task E3: `layer-guides.md` absolutes become ratios

**Files:**
- Modify: `skills/foundation/references/layer-guides.md:138`, `:199-202`, `:221`, `:321`
- Modify: `skills/foundation/references/layer-guides.md:1-7` (preamble)

- [ ] **Step 1: Preamble**

Replace the opening paragraph:

```
One section per planning document. Follow the matching section when
filling or revising that layer. Every requirement below is a hard
requirement, not a suggestion — the foundation rubric scores against
exactly these expectations.
```

with:

```
One section per planning document. Follow the matching section when
filling or revising that layer. Every requirement below is a hard
requirement, not a suggestion — the foundation rubric scores against
exactly these expectations.

Two things govern how to read the numbers here. First, the form pack's
`## Foundation Guidance` says which layers exist at this length and what
each means; a layer the form does not name is not a gap. Second, every
count and length below is written for a novel and scales by the resolved
`shape` — where a line says "per N chapters" or "per N words", compute it
from `shape.chapters` and `shape.target_words` and use that number. A
5,000-word story does not owe fifteen tracked threads or three quiet
chapters; it owes the ratio.

These documents address the drafting agent, not the evaluator. Do not
write arguments about why a choice satisfies a rubric, a contract, or
this guide into a planning document. If a choice needs defending, the
defence belongs in the commit message. On one run a judge found "a
substantial fraction" of two documents was parenthetical self-defence
addressed to it — and the one genuine hole in the climax survived four
iterations because the surrounding prose was busy defending choices that
were already fine.
```

- [ ] **Step 2: The four literals**

Line 138: `- Target ~3000-4000 words. Dense character work, not padding.` → `- Target roughly 4% of \`shape.target_words\` (3000–4000 for a novel). Dense character work, not padding.`

Lines 199–200 (both places it appears — in `## outline.md part 1` CONSTRAINTS and, if repeated, in the earlier bullets): `- Any character established as "absent but plot-critical" must appear in person at some point, not only in memory or secondhand report.` → `- Any character established as "absent but plot-critical" must appear in person at some point, not only in memory or secondhand report — unless the impossibility of their appearing IS the story's subject, in which case the outline states that once, plainly, and moves on.`

Lines 201–202: `- At least 3 chapters should be "quiet" — character-focused, low-action, emotionally rich.` → `- About one unit in four should be "quiet" — character-focused, low-action, emotionally rich (at least 3 for a novel; a four-scene story owes one).`

Line 221: `Include at LEAST 15 threads. Types: object, dialogue, action, symbolic, structural.` → `Include at least one tracked thread per 5,000 words of \`shape.target_words\` (15 for an 80,000-word novel; a short story owes one or two, and the form may drop the ledger entirely). Types: object, dialogue, action, symbolic, structural.`

Line 321: `- Aim for 80-120 entries on the first pass; grow the canon toward 400+ entries before exiting foundation` → `- Aim for one entry per 800 words of \`shape.target_words\` on the first pass (80–120 for a novel); grow the canon toward five times that before exiting foundation`

- [ ] **Step 3: Anti-exemplars from rejected voice trials**

In `## voice discovery`, replace step 4 `4. Select the best, refine it, write exemplar and anti-exemplar passages` with `4. Select the best, refine it, write exemplar passages — and keep the four rejected trials AS the anti-exemplars, each with one line on why it lost. Two judges on one run independently called that section the strongest element in any of the planning documents; a discarded trial is a boundary the drafter can see.`

- [ ] **Step 4: Commit**

```bash
uv run pytest tests/ -q
git add plugin/autoauthor/skills/foundation/references/layer-guides.md
git commit -F - <<'EOF'
fix: layer-guides literals scale with the resolved shape, and the guide says who it addresses

Fifteen threads, three quiet chapters, 3000-word character docs and
400 canon entries were novel absolutes still live at 5,000 words.
Also tells the author the plan addresses the drafter, not the judge —
a judge caught rubric-facing prose and the hole it was hiding.
EOF
```

## Task E4: `iteration_cap` in form frontmatter

**Files:**
- Modify: `shared/scripts/form_pack.py:103-160`, `resolve_genre.py:476-485`
- Modify: `shared/forms/novel.md`, `novella.md`, `short-story.md` (frontmatter)
- Modify: `skills/foundation/SKILL.md:146-148`
- Test: `tests/test_form_pack.py`

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_form_pack.py`:

```python
def test_iteration_cap_is_optional_and_defaults_to_fifteen(tmp_path):
    assert validate(tmp_path, "testform", VALID_FORM_META) == []
    assert resolve(tmp_path, {"genre": "mystery"})["form"]["iteration_cap"] == 15


@pytest.mark.parametrize("cap", [0, -1, 2.5, "8", True])
def test_iteration_cap_must_be_a_positive_integer(tmp_path, cap):
    meta = dict(VALID_FORM_META, iteration_cap=cap)
    errors = validate(tmp_path, "testform", meta)
    assert any("iteration_cap" in e for e in errors), errors


def test_shipped_forms_declare_shorter_caps_at_shorter_lengths():
    caps = {p.stem: form_pack.parse_form(p)["meta"].get("iteration_cap")
            for p in FORMS.glob("*.md")}
    assert caps["novel"] == 15
    assert caps["novella"] == 8
    assert caps["short-story"] == 4
```

And update `test_the_form_block_carries_what_the_skills_need` so the expected key set includes `"iteration_cap"`.

- [ ] **Step 2: Run to see them fail**

Run: `uv run pytest tests/test_form_pack.py -q`
Expected: 4 new failures plus the updated key-set test.

- [ ] **Step 3: Implement**

`form_pack.py`, in `validate_form` after the `chapter_words` check:

```python
    cap = meta.get("iteration_cap")
    if cap is not None and not (isinstance(cap, int)
                                and not isinstance(cap, bool) and cap > 0):
        errors.append("'iteration_cap' must be a positive integer; it is "
                      "how many foundation iterations this length can "
                      "earn before the plan cannot be much righter than "
                      "the work")
```

Add near the top of `form_pack.py` (with the other module constants): `DEFAULT_ITERATION_CAP = 15`.

`resolve_genre.py`, in the `"form": {...}` block after `"gate": form["meta"]["gate"],` add:
`"iteration_cap": form["meta"].get("iteration_cap", form_pack.DEFAULT_ITERATION_CAP),`

Also add to `resolve_genre.py`'s module docstring `form` description a line: `iteration_cap — how many foundation iterations before the loop stops regardless (form's own, default 15)`.

Frontmatter: add `"iteration_cap": 15` to `shared/forms/novel.md`, `"iteration_cap": 8` to `novella.md`, `"iteration_cap": 4` to `short-story.md`, each on the line after `"gate": {...},`.

`skills/foundation/SKILL.md` step 5: replace `5. **Iteration cap.** After 15 iterations without passing the gate, STOP.` with `5. **Iteration cap.** After \`form.iteration_cap\` iterations (from the resolver's \`form\` block — 15 for a novel, 8 for a novella, 4 for a short story) without passing the gate, STOP.` and after `(accept and move on / keep iterating / revise the seed).` add: `The cap is the form's for the same reason the gate is: six evals at 119k tokens each to plan 5,000 words was the cost on one run, and the last two moved the mean 0.10.`

Also the skill's opening paragraph `Typical runs take 5–15 iterations.` → `Typical runs take 5–15 iterations at novel length; the form's \`iteration_cap\` bounds it.`

- [ ] **Step 4: Run tests, validate forms, commit**

```bash
uv run pytest tests/ -q
for f in plugin/autoauthor/shared/forms/*.md; do python3 plugin/autoauthor/shared/scripts/validate_form_pack.py "$f" || echo "FAIL $f"; done
git add plugin/autoauthor/shared/scripts/form_pack.py plugin/autoauthor/shared/scripts/resolve_genre.py plugin/autoauthor/shared/forms/*.md plugin/autoauthor/skills/foundation/SKILL.md tests/test_form_pack.py
git commit -F - <<'EOF'
feat: forms declare iteration_cap; foundation stops at the form's number, not a universal 15

The short-story form lowered the gate on the reasoning that the plan
cannot be much righter than the story; that reasoning also lowers the
ceiling and nothing carried it there.
EOF
```

## Task E5: `full-novel.md` honours the band's pillar dimensions

**Files:**
- Modify: `shared/rubrics/full-novel.md:19-29`
- Modify: `skills/revise/SKILL.md` Measure dispatch (the prompt in Task B1 step 3)

(Verified while planning: `full-novel.md` contains no mention of `band` or the packs' length-scoped sections; `chapter.md` gets there only because the genre pack's `## At Compressed Length` names the dimensions and the chapter judge reads the pack.)

- [ ] **Step 1: Add the band instruction**

After the GENRE PACKS paragraph in `shared/rubrics/full-novel.md`, add:

```markdown
BAND: the dispatching prompt names the work's form and band. Where the
primary pack carries a section for that band (`## At Compressed Length`,
`## At Intermediate Length`), the pillar dimensions it names — and only
those — are the ones you score; the ones it drops are absent by the
form's decision, not the plan's. Every full-novel judge on one
short-story run volunteered that it was scoring a 4,600-word work
against a novel's instrument; the pack already said which instruments
apply, and this rubric did not tell you to read it.
```

- [ ] **Step 2: Dispatch names the form and band**

In `skills/revise/SKILL.md` Measure step 1's dispatch, after `and follow the rubric exactly.` add ` The form is \`<form.name>\` and its band is \`<form.band>\`.`

- [ ] **Step 3: Commit**

```bash
uv run pytest tests/ -q
git add plugin/autoauthor/shared/rubrics/full-novel.md plugin/autoauthor/skills/revise/SKILL.md
git commit -F - <<'EOF'
fix: the full-novel judge scores the band's pillar dimensions, as the chapter judge already does
EOF
```

---

# Part F — Rubric prose

Covers: foundation findings 6, 7; revision finding 8.

## Task F1: `internal_consistency` counts contradictions a writer must not violate

**Files:**
- Modify: `shared/rubrics/base-dimensions.md:65-68`

- [ ] **Step 1: Replace the dimension text** (key and cap value unchanged)

Replace:

```
- internal_consistency [cap 4] — Actively hunt for contradictions.
  Cross-ref dates, ages, character counts, named locations. Flag any case
  where documents disagree. A single major contradiction caps this at 6.
  Three or more caps at 4.
```

with:

```
- internal_consistency [cap 4] — Actively hunt for contradictions.
  Cross-ref dates, ages, character counts, named locations, and every
  number in the outline's facts section against every other document.
  Count only contradictions in text a writer must not violate: fact
  tables, outline beats, quoted in-story text, and character facts. A
  disagreement confined to authorial commentary is a note under this
  dimension, not a contradiction. A MAJOR contradiction is one the plot
  depends on — a clock the climax runs on stated three ways, an interval
  that cannot both be what two chapters need. One major caps this at 6;
  three or more major cap it at 4. Two judges on one run handled the
  same class of set oppositely because the rule gave no severity axis:
  one capped at 4 on four one-line typography and wording faults, the
  other scored 8 by declining to count comparable ones. List every
  contradiction you found, major or not, so the author can fix all of
  them; cap on the major ones.
```

- [ ] **Step 2: Run the guards and the solver**

```bash
uv run pytest tests/test_required_reading_is_clean.py tests/test_gate_solver.py tests/test_rubric_contract.py -q
python3 plugin/autoauthor/shared/scripts/gate_solver.py 2>&1 | tail -5
```

Expected: pass; solver output unchanged (cap value did not move).

- [ ] **Step 3: Commit**

```bash
git add plugin/autoauthor/shared/rubrics/base-dimensions.md
git commit -F - <<'EOF'
fix: internal_consistency caps on major contradictions in binding text, not on a count of any disagreement

The count bound with no severity axis; a typography mismatch in
commentary weighed the same as the clock the second half runs on, and
two judges resolved the strain in opposite directions.
EOF
```

## Task F2: Foundation rubric discounts rubric-facing prose

**Files:**
- Modify: `shared/rubrics/foundation.md:69-85` (CROSS-CHECKS)

- [ ] **Step 1: Add a cross-check**

After cross-check 2 (`Check for missing NEGATIVE SPACE`) and its sub-bullets, before cross-check 3, insert:

```markdown
2b. Discount prose addressed to you rather than to a writer. A plan that
   argues a gap does not exist has not closed it — check the material
   the argument stands in front of, and note the argument under
   `slop_in_planning_docs`. Parentheticals of the shape "(the contract
   requires it)", "which <dimension> would rightly punish", "stated so
   it reads as a choice" are the tell. On one run a substantial
   fraction of two documents was this, and the one hole a drafter would
   actually stop at survived four iterations because it was never
   argued about.
```

(If the existing list is not numbered `3.` after `2.`, insert as the next item and renumber nothing else.)

- [ ] **Step 2: Commit**

```bash
uv run pytest tests/ -q
git add plugin/autoauthor/shared/rubrics/foundation.md
git commit -F - <<'EOF'
fix: the foundation judge discounts prose addressed to it and checks the material behind it
EOF
```

## Task F3: `## Author-facing only` in the templates, honoured by three rubrics

**Files:**
- Modify: `shared/templates/outline.md`, `shared/templates/characters.md`
- Modify: `shared/rubrics/full-novel.md`, `shared/rubrics/reader-panel.md`, `shared/rubrics/chapter.md`
- Modify: `skills/foundation/references/layer-guides.md` (outline part 1 CONSTRAINTS)

- [ ] **Step 1: Templates**

In `shared/templates/outline.md`, immediately after the `## Facts the story must not contradict` block from Task C3, add:

```markdown
## Author-facing only (never on the page)
<!-- Rules, mechanisms, and withholdings that govern the story but are
     deliberately never stated in it: a physical constraint the reader
     can only infer, a character's unnamed job whose namelessness is the
     payoff. One line each, no argument. Judges treat items here as
     withheld by design, not as unpaid debts. -->
```

In `shared/templates/characters.md`, at the end, add:

```markdown
## Author-facing only (never on the page)
<!-- Anything about a character the story deliberately never states.
     One line each. -->
```

- [ ] **Step 2: layer-guides**

In `## outline.md part 1` CONSTRAINTS (after the two bullets Task C3 added), add:

```markdown
- Anything the story deliberately never states — a rule the reader can
  only infer, a withheld name whose withholding is the payoff — goes
  under `## Author-facing only (never on the page)`, one line each,
  without argument. This is the one place the plan may speak to a judge
  rather than a drafter, and it is a list, not a defence. Three rewrite
  attempts on one run tried to put a codec rule into prose because a
  judge read its absence as a debt; each introduced a new arithmetic
  error, and the rule was correct physics and unwritable prose.
```

- [ ] **Step 3: Rubrics**

`shared/rubrics/full-novel.md`, after the OUTLINE + FORESHADOWING LEDGER read instruction, add:

```markdown
If outline.md or characters.md carries a `## Author-facing only (never
on the page)` section, its items are withheld by design. Do not score
their absence from the manuscript as an unpaid debt, a missing beat, or
a hole; score whether the story works WITHOUT them stated, which is the
test the author chose. Judge only what appears there as a bare list —
an argument in that section is rubric-facing prose and gets no such
protection.
```

`shared/rubrics/reader-panel.md`, in the INPUT FILES block after `arc_summary.md`, add: `- outline.md's \`## Author-facing only (never on the page)\` section, if present — items there are withheld by design; do not name them as missing.` (Read the block's exact format first and match it.)

`shared/rubrics/chapter.md`, after `CHAPTER OUTLINE ENTRY: Extract the target chapter's entry from outline.md.` add: `Also read outline.md's \`## Author-facing only (never on the page)\` section if present: an item there is withheld by design and is not a canon violation or a missing beat when the chapter does not state it.`

- [ ] **Step 4: Run guards and commit**

```bash
uv run pytest tests/ -q
git add plugin/autoauthor/shared/templates/outline.md plugin/autoauthor/shared/templates/characters.md plugin/autoauthor/shared/rubrics/full-novel.md plugin/autoauthor/shared/rubrics/reader-panel.md plugin/autoauthor/shared/rubrics/chapter.md plugin/autoauthor/skills/foundation/references/layer-guides.md
git commit -F - <<'EOF'
feat: an author-facing-only section the judges treat as withheld by design

Three rewrite attempts and a score regression on one run came from a
judge reading a deliberately unstated rule as an unpaid debt. The
section is a list, not an argument, and only the list is protected.
EOF
```

---

# Task Z: Release

**Files:**
- Modify: `plugin/autoauthor/.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` (twice)
- Modify: `CHANGELOG.md` if present (check `ls`)

- [ ] **Step 1: Full verification**

```bash
uv run pytest tests/ -q
for f in plugin/autoauthor/shared/genres/*.md; do python3 plugin/autoauthor/shared/scripts/validate_genre_pack.py "$f" >/dev/null || echo "FAIL $f"; done
for f in plugin/autoauthor/shared/forms/*.md; do python3 plugin/autoauthor/shared/scripts/validate_form_pack.py "$f" >/dev/null || echo "FAIL $f"; done
python3 plugin/autoauthor/shared/scripts/gate_solver.py | tail -3
```

Expected: all tests pass (461 + the new ones), no FAIL lines, solver reports every pack clears its gate.

- [ ] **Step 2: Bump 0.17.1 → 0.18.0 in all three places**

```bash
sed -i '' 's/"version": "0.17.1"/"version": "0.18.0"/' plugin/autoauthor/.claude-plugin/plugin.json .claude-plugin/marketplace.json
grep -n '"version"' plugin/autoauthor/.claude-plugin/plugin.json .claude-plugin/marketplace.json
```

Expected: three lines, all `0.18.0`.

- [ ] **Step 3: Commit**

```bash
git add plugin/autoauthor/.claude-plugin/plugin.json .claude-plugin/marketplace.json
git commit -F - <<'EOF'
release: 0.18.0 — the 2026-08-17 shakedown findings

Baseline and keep/discard rules that trust only same-cycle numbers;
judges write their own verdicts; form-aware file lists and a canon.md
scaffold in draft; continuity_check.py and a canon gate with a
surgical-correction branch; protected lines and splice_audit.py in
revise; guardrails and guide literals as ratios of the resolved shape;
iteration_cap on forms; author-facing-only sections the judges honour.
EOF
```

---

## Self-review against the three findings documents

| Finding | Task |
|---|---|
| revision 1 (novel-scale guardrails) | E1, E2, E5 |
| revision 2 (apply_cuts before protection) | D1, D3 |
| revision 3 (no cross-cycle memory) | D3 |
| revision 4 (splice checklist) | D2, D3 |
| revision 5 (baseline before rewriting) | A1 |
| revision 6 (baseline per-cycle) | A1 |
| revision 7 (panel false positives) | D3 steps 4–5 |
| revision 8 (author-facing only) | F3 |
| revision 9 (gate the cuts pass) | D3 step 3 |
| foundation 1 (cap vs gate) | A2 (weak form, deliberately) |
| foundation 2 (keep/discard) | A3 |
| foundation 3 (judge noise) | A3 tie band; C1 as the mechanical alternative; triple-judge median **not done** (cost) |
| foundation 4 (voice_wells.json) | B2 |
| foundation 5 (layer-guides literals) | E3 (ratios, not a suppression list) |
| foundation 6 (rubric-facing prose) | E3 preamble, F2 |
| foundation 7 (internal_consistency severity) | F1 |
| foundation 8 (fix strings) | A3 step 2 |
| foundation 9 (iteration cap) | E4 |
| foundation 10 (seed arithmetic) | C3 |
| foundation 11 (verbatim objects) | C3 |
| foundation 12 small things | `words` column and `iteration` overload **not done** (cosmetic; noted) |
| draft 1 (judge writes JSON) | B1 |
| draft 2 (continuity check) | C1, C2 |
| draft 3 (canon gate) | C2 |
| draft 4 (voice budgets) | **not done** — needs foundation to emit machine-readable patterns; deferred to its own plan |
| draft 5 (state/history) | B3 |
| draft 6 (canon.md) | B3 |
| draft 7 (world.md refs) | B4 |
| draft 8 (outline load) | B3 |
| draft 9, 10 (nits) | B5 |

Deliberately not done, and why: triple-judge median (trebles the cost the same document complains about); form-pack `layer_guide.suppress` (heavy machinery aimed at prose; ratios do the job); voice budgets in `slop_score.py` (worth doing, but it needs a `voice_budgets.json` contract from foundation and its own tests — separate plan); `results.tsv` `words` column in foundation and the `iteration` field overload (cosmetic).
