# Second Shakedown Findings (2026-08-19) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Act on the four findings documents from the 0.18.0 run on `redshift` (`docs/superpowers/specs/2026-08-19-{foundation,draft,revise,review}-findings.md`), plus one correction to 0.19.0 (the `editor`/`reader` agents must write their own artifacts).

**Architecture:** Five independent parts. A and B are prose edits to skills/rubrics/agents; C is the gate rules (prose); D is code in `gen_brief.py` and `apply_cuts.py` with tests; E is one-line clarifications. Each task quotes an anchor phrase from the current file — locate edits by anchor, never by line number.

**Tech Stack:** Python 3.11+, `uv run pytest tests/ -q` (547 tests, ~8 s). No new dependencies.

**Repo conventions:** see `CLAUDE.md`/`AGENTS.md` — commit with `git commit -F -` heredoc (never `-m` with backticks); Tier-1 phrases banned in `shared/**` (`test_required_reading_is_clean.py`); no dimension key renames; no cap value changes; version bump in three places at the end. Paths below starting `skills/`, `shared/`, `agents/` are relative to `plugin/autoauthor/`.

---

# Part A — The review judge learns the form; title; stop rule

Covers: review findings 1, 2, 3, 4, 5.

## Task A1: Review dispatch and rubric carry form, shape and title

**Files:** `skills/review/SKILL.md`, `shared/rubrics/manuscript-review.md`

- [ ] **Step 1** — In `skills/review/SKILL.md` step 2's quoted dispatch, after `and follow the rubric exactly.` insert: ` The work's title is \`<state.json title>\`. Its form is \`<form.label>\` (\`<form.name>\`, band \`<form.band>\`): the resolver's \`shape.words\` for this band is \`<low>–<high>\` and \`shape.target_words\` is \`<N>\`; the manuscript is \`<total words>\` words. Judge it as a work of that form and length, not as a novel.` Then, after the closing quote and the "The judge agent pins the model" sentence, add a new paragraph:

```markdown
   Every value in angle brackets comes from `state.json` and the resolver
   output kept in Setup. On one short-story run the judge was told
   nothing about the form, read the genre pack's novel-band shape, and
   returned as its ONLY major item "a novelette presented as a novel …
   against a declared shape of 90–110k" — for a 5,071-word story whose
   form targets 5,000. Its second item was conditioned on the first. A
   review whose headline defect is a pipeline artifact can drive a round
   of fixes toward expanding a finished story.
```

- [ ] **Step 2** — In `shared/rubrics/manuscript-review.md`: replace `You are reviewing a complete novel manuscript.` with `You are reviewing a complete manuscript of the form the dispatching prompt declares — a novel, a novella, or a short story.`; replace `(the full novel, chapters concatenated in order)` with `(the full work, chapters or scenes concatenated in order)`; replace `Read the novel in manuscript.md (the input file above).` with `Read the work in manuscript.md (the input file above). The dispatching prompt gives its title, form, the form's word range and target, and the delivered word count: judge length, pacing and scope against THAT form. A short story is not a failed novel, and a tic that would wear across ninety thousand words may be a signature across five thousand.` Grep the rest of the rubric for `the novel` / `this novel` and change those that address the work to `the work` where the sentence would otherwise assert novel length; leave "novel" where it names the genre-pack framing. Run `uv run pytest tests/test_rubric_contract.py tests/test_results_tsv.py tests/test_required_reading_is_clean.py -q`.

- [ ] **Step 3** — Commit:

```
fix: the manuscript-review judge is told the form, shape and title it is reviewing

Told nothing, it read the genre pack's novel band and returned "a
novelette presented as a novel" as a short story's only major item.
```

## Task A2: Review's brief flag, stop rule, exit grammar

**Files:** `skills/review/SKILL.md`

- [ ] **Step 1** — Step 5: `gen_brief.py" --eval <ch>\`` → `gen_brief.py" --eval <ch> --chapter-words <shape.chapter_words>\`` (the flag clamps the compression floor to the form; without it the floor is the novel's 1800).

- [ ] **Step 2** — Step 4 stopping conditions: replace the bullet `- zero major unqualified items` with `- zero major unqualified items AND at most 2 moderate unqualified items — a round-1 review that names several cheap, concrete, unqualified moderate fixes and no major one should still run Fix once; on one run the only major was a pipeline artifact and four one-to-three-line moderate fixes were never attempted`.

- [ ] **Step 3** — Exit commit: `"review complete: <R> rounds, <stars> stars"` → `"review complete: <R> round(s), <stars> stars"`.

- [ ] **Step 4** — Commit: `docs: review passes --chapter-words, runs Fix once when cheap moderate items remain, and pluralises its exit`.

---

# Part B — Agents write their artifacts; baseline race; dispatch failure

Covers: revise findings 6, 9, 10, 21; corrects 0.19.0's read-only `editor`/`reader`.

## Task B1: `editor` and `reader` write their own files

**Files:** `agents/editor.md`, `agents/reader.md`, `tests/test_agents.py`, `skills/revise/SKILL.md`

- [ ] **Step 1** — Test first. In `tests/test_agents.py` replace `test_only_the_judge_may_write` with:

```python
def test_every_agent_writes_its_own_artifact():
    """Judges write verdicts, the editor writes chNN_cuts.json, readers write
    panel_raw/<persona>.json. The orchestrator transcribing any of them is
    the lossy step 0.18.0 removed for judges; 0.19.0 left the other two
    inline and a run with no tool-completion signal had nothing to wait on."""
    for path in AGENTS:
        meta, _ = frontmatter(path)
        tools = {t.strip() for t in meta["tools"].split(",")}
        assert "Write" in tools, f"{path.stem} must be able to write its artifact"
```

Run `uv run pytest tests/test_agents.py -q` → the new test fails for editor and reader.

- [ ] **Step 2** — `agents/editor.md`: `tools: Read, Glob, Grep` → `tools: Read, Glob, Grep, Write`; description: replace `returns quote-anchored cuts against the adversarial-edit rubric, or a one-paragraph head-to-head verdict` with `writes quote-anchored cuts against the adversarial-edit rubric to the path the prompt names, or returns a one-paragraph head-to-head verdict`; body: replace `Return only what the dispatching prompt asks for — the JSON the\nrubric specifies, or the one-paragraph comparison and its WINNER line — and\nnothing else.` with `Write the JSON the rubric specifies — bare JSON, no fences — to the exact path the dispatching prompt names and return only that path; for a head-to-head comparison (no path given) return the one paragraph and its WINNER line and nothing else.`

  `agents/reader.md`: same tools change; body: replace `Return only the JSON the rubric\nspecifies.` with `Write the JSON the rubric specifies — bare JSON, no fences — to the exact path the dispatching prompt names, and return only that path.`

- [ ] **Step 3** — `skills/revise/SKILL.md` Diagnose step 3 editor dispatch: replace `Return ONLY the JSON the rubric specifies."\n   Save each response verbatim to \`edit_logs/chNN_cuts.json\` (exact\n   filename — apply_cuts.py globs it).` with `Write the JSON the rubric specifies — bare JSON, no fences — to \`<absolute project path>/edit_logs/chNN_cuts.json\` (exact filename, NN zero-padded — apply_cuts.py globs it) and return only that path."\n   The editor writes the file; you do not transcribe it.`

  Step 5 reader dispatch: replace `Return ONLY the JSON the rubric specifies."\n   Assemble \`edit_logs/reader_panel.json\` as:` with `Write the JSON the rubric specifies — bare JSON, no fences — to \`<absolute project path>/edit_logs/panel_raw/<persona>.json\` and return only that path."\n   **Wait on the four files, not on the tool's return.** Poll \`edit_logs/panel_raw/\` until all four exist (\`until ls …; do sleep 10; done\`); on one run no Agent-tool completion arrived for any of eleven dispatches in a cycle, and the verdict files were the only wake signal. Then assemble \`edit_logs/reader_panel.json\` from the four files as:`

  Same "wait on the file" sentence for judges: in Fix step 4, after `The judge writes its own verdict file` sentence, add ` Wait on the file's existence, not on the tool's completion notice.`

- [ ] **Step 4** — Run `uv run pytest tests/ -q`; commit:

```
fix: the editor and reader agents write their own files, and the skill waits on files rather than tool returns

0.19.0 made them read-only and the orchestrator transcribed cuts JSON
and panel JSON by hand — the lossy step 0.18.0 removed for judges. A
cycle with no tool-completion signal had nothing to wait on except the
files judges wrote.
```

## Task B2: The baseline race and parallel attempts on neighbours

**Files:** `skills/revise/SKILL.md`

- [ ] **Step 1** — Fix step 4, replace `These run concurrently\n   with drafting the first brief, so they cost wall-clock nothing.` with:

```markdown
   These run concurrently with reading briefs and planning the first
   rewrite, so they cost wall-clock nothing — **but nothing is written
   to `chapters/` until every baseline verdict file exists.** Judges
   read `chapters/ch_NN.md` one to three minutes into their run, not at
   dispatch: on one cycle four patches written 2.5 minutes after
   dispatching four baselines produced two "baselines" that quoted the
   patched text, and would have gated two rewrites against scores of
   themselves. Draft in `eval_logs/ch_NN_attempt_<k>.md`; copy into
   `chapters/` only when the baselines are on disk and you are scoring.
   The same hazard holds for the previous-chapter read: do not run
   attempts on adjacent chapters concurrently — ch_04's judge scores
   continuity against whatever ch_03 is on disk, committed or not.
```

- [ ] **Step 2** — Setup step 5 (malformed responses): append ` A dispatch that returns no file at all (an API error mid-run) is retried once with the same prompt, then recorded in \`edit_logs/skipped.md\` like a malformed one.`

- [ ] **Step 3** — Commit: `fix: revise writes nothing to chapters/ until baselines exist, serialises adjacent-chapter attempts, and retries a no-file dispatch once`.

---

# Part C — Gate rules, third time

Covers: foundation findings 1, 2, 3, 6; revise 4/15; draft 1, 2.

## Task C1: Foundation — force only on MAJOR; discovery is not damage; second judge on a big regression; exit at cap

**Files:** `skills/foundation/SKILL.md`

- [ ] **Step 1** — Step 2 cap paragraph: in the sentence beginning `So: if any scored dimension's note says its cap fired, or the eval's \`contradictions_found\` list names a contradiction in a fact table,` replace `names a contradiction in a fact table, an outline beat, quoted in-story text, a character fact, or an author-facing rule, do NOT exit` with `names a contradiction marked MAJOR (one the plot depends on — the rubric asks for that marking), do NOT exit`. After `then re-check.` add: ` A minor contradiction — a clock written two ways, a stray question mark — goes on the next iteration's fix list but does not block exit: on one short-story run every judge listed new minor items while the score sat 7.7–8.2 against a 6.5 gate, and with \`iteration_cap: 4\` the loop could never exit cleanly.` Make the same MAJOR-only change in `## Exit`'s "Do not exit while … `contradictions_found` names a contradiction in a fact table, an outline beat, quoted in-story text, a character fact, or an author-facing rule" → `names a contradiction marked MAJOR`.

- [ ] **Step 2** — Step 4, `**Regressed by more than 0.15**` bullet: after `Discard only when the targeted dimension did not\n     improve.` add: ` One more case: if the contradictions the new eval lists ALSO exist in the kept state — the judge found a fault that was already there — the regression is discovery, not damage. Keep, and target it next iteration; discarding would restore the faults you just fixed and keep the one you just found (one run's iteration 4 dropped 0.72 on exactly this and the rule's letter said discard). And before discarding any regression larger than 0.5, dispatch a second judge on the same tree: single-judge variance has moved a score 0.72 on a handful of changed lines and 0.00 on a rewrite, and one extra dispatch is cheaper than throwing away an iteration.`

- [ ] **Step 3** — Step 5 iteration cap: after `STOP. Report the best score, the stubborn dimension or the cap that keeps firing, and options (accept and move on / keep iterating / revise the seed).` add: ` If at the cap both scores clear the gate and no MAJOR contradiction or fired cap remains, that is a normal exit, not a stop — go to Exit. If you do stop: leave \`foundation_score\` and \`pillar_score\` at the last KEPT state's values (not the best ever seen), set \`chapters_total\` from the outline so a user who accepts can draft without a second pass here, and write the results.tsv row with \`awaiting user decision\` in the description.`

- [ ] **Step 4** — Commit:

```
fix: foundation forces iterations on MAJOR contradictions only, keeps a regression that is discovery, and exits cleanly at the cap

Any-contradiction forcing made the short-story cap unreachable by
construction; a 0.72 regression that found a pre-existing major fault
read as "discard" under the rule's letter.
```

## Task C2: Draft — `correct` covers missing plants and judge-named fact fixes; Setup accepts a cap-cleared foundation

**Files:** `skills/draft/SKILL.md`

- [ ] **Step 1** — Step 6: replace `**If the chapter fails ONLY on canon** — final score clears 6.0,` … through the end of that paragraph's `against a debt that otherwise waits for a phase that will\n   not see it.` with:

```markdown
   **The surgical-correction branch.** If the final score clears 6.0
   and the judge names any of: (a) `canon_compliance` below 7 with a
   non-empty `violations` list; (b) a plant from this chapter's outline
   `Plants:` list that is not on the page; (c) a one-word or one-number
   fact fix (a count, an age, a clock time) — do not discard and do not
   commit as-is. Apply edits addressing only the named items, re-run
   step 3, re-dispatch the judge, and log the attempt row as `correct`.
   A correction counts against the 5-attempt budget so it cannot loop.
   A canon violation or a missing plant is unlike a weak sentence: it is
   cheap now, it compounds (a wrong line in ch1 forced ch2 to write
   around it; a plant missing from ch1 has no payoff in ch6), and it is
   invisible to revision, whose instruments cut and compress. Post-judge
   edits outside this branch are forbidden — they decouple the committed
   text from the committed score; one run improvised both re-judging and
   un-judged touch-ups for the same class of defect, which is the
   inconsistency this branch exists to remove.
```

  Then in the keep sentence that follows (`Score clears and canon clean → keep:`) change to `Score clears, and no branch-(a)/(b)/(c) item is named → keep:`.

- [ ] **Step 2** — Setup step 1: after `and \`state.json\` phase \`drafting\`.` add: ` One exception: phase \`foundation\` with \`iteration\` equal to \`form.iteration_cap\` and both \`foundation_score\` and \`pillar_score\` above the form gate means foundation stopped at its cap with the gate cleared and left the decision to the user — invoking this skill is that decision. Set \`phase: drafting\` and \`chapters_total\` if unset, commit \`foundation complete: <overall>/<pillar> (at cap)\`, and proceed. Any other non-\`drafting\` phase: STOP and ask.`

- [ ] **Step 3** — Commit: `fix: draft's correct branch covers missing plants and one-word fact fixes, and Setup accepts a foundation that stopped at its cap with the gate cleared`.

## Task C3: Revise — a tie keeps when the targeted dimension rose

**Files:** `skills/revise/SKILL.md`

- [ ] **Step 1** — Fix step 4 "Two consequences" bullets: replace the bullet beginning `- A rewrite that TIES a true same-cycle baseline is not an\n     improvement and should still be discarded` (through `Re-baseline before concluding either way.`) with:

```markdown
   - A rewrite within ±0.15 of a true same-cycle baseline is a TIE, and
     nine integer dimensions give 0.11 granularity, so ties are common.
     A tie KEEPS when the dimension the brief targeted rose and no other
     dimension fell by more than one point — that is a judge-requested
     edit landing and the mean not moving, not "no change". A tie where
     the targeted dimension did not rise is discarded. One cycle
     discarded four of eight judged attempts on exact ties, most of
     them edits a judge had asked for, where the targeted dimension rose
     a point and an unrelated one fell; three dispatches were spent to
     not-keep fixes the judges asked for. A rewrite that ties the
     *recorded* (prior-cycle) number may be beating the true one —
     re-baseline before concluding either way.
```

  And in the keep sentence above it (`Keep if the final score beats the chapter's baseline (see below)`) → `Keep if the final score beats the chapter's baseline, or ties it with the targeted dimension up (see below)`.

- [ ] **Step 2** — Commit: `fix: a revise rewrite that ties its baseline keeps when the dimension it targeted rose`.

---

# Part D — Code: gen_brief.py and apply_cuts.py

Covers: revise findings 1, 2, 12, 13, 22, 5/14; review 2 (done in A2).

## Task D1: `gen_brief.py` — zero-padded chapters, primary-chapter attribution, character notes, COMPRESS as upper bound

**Files:** `shared/scripts/gen_brief.py`, `tests/test_gen_brief.py`

- [ ] **Step 1** — Tests first. Append to `tests/test_gen_brief.py` (reuse the file's `SCRIPT` constant and its panel fixture pattern; all via `--dry-run` and `monkeypatch.chdir(tmp_path)`):

```python
def _panel_project(tmp_path, readers, wc=1500):
    import json
    (tmp_path / "chapters").mkdir()
    (tmp_path / "edit_logs").mkdir()
    (tmp_path / "voice.md").write_text("# Voice\n")
    for n in (2, 3, 4):
        (tmp_path / f"chapters/ch_0{n}.md").write_text(
            f"# Chapter {n}: T\n\n" + ("word " * wc).strip() + "\n")
    (tmp_path / "edit_logs/reader_panel.json").write_text(json.dumps(
        {"readers": readers, "consensus": [], "disagreements": []}))


def _brief(tmp_path, ch):
    r = subprocess.run([sys.executable, str(SCRIPT), "--panel", str(ch),
                        "--chapter-words", "1200", "--dry-run"],
                       capture_output=True, text=True, cwd=tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr
    return r.stdout


def test_zero_padded_chapter_mentions_match(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _panel_project(tmp_path, {"editor": {"cut_candidate": "Chapter 03 repeats the lookup device."}})
    assert "COMPRESS" in _brief(tmp_path, 3)


def test_an_item_is_attributed_to_the_first_chapter_it_names(tmp_path, monkeypatch):
    """'Chapter 2's roster scene is weak; chapter 3 then has to carry it' is a
    chapter-2 item. It must not appear in chapter 3's brief."""
    monkeypatch.chdir(tmp_path)
    _panel_project(tmp_path, {"genre_reader": {
        "worst_scene": "Chapter 2's roster scene is weak; chapter 3 then has to carry it. Fix: break it."}})
    assert "Dramatize" in _brief(tmp_path, 2)
    assert "Dramatize" not in _brief(tmp_path, 3)


def test_character_level_items_go_under_their_own_heading_not_into_changes(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _panel_project(tmp_path, {"writer": {"thinnest_character": "Ikaika is thinnest; I never learn what he wants."}})
    out = _brief(tmp_path, 4)
    assert "Deepen character" not in out
    assert "CHARACTER NOTES" in out and "Ikaika" in out


def test_compress_target_is_labelled_an_upper_bound(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _panel_project(tmp_path, {"editor": {"cut_candidate": "Chapter 2 could go."}}, wc=1762)
    out = _brief(tmp_path, 2)
    assert "upper bound" in out
    assert "repetition" in out.lower()
```

Run → failures.

- [ ] **Step 2** — Implement in `gen_brief.py`:
  - `ch_re`: `rf"\b(?:Chapter|Ch\.?)\s*0*{ch}\b"`.
  - Add `ANY_CH_RE = re.compile(r"\b(?:Chapter|Ch\.?)\s*0*(\d+)\b", re.I)` and a helper `primary_chapter(text) -> int | None` returning the first chapter number mentioned. In `panel_mentions_for_chapter`, attribute an answer to `ch` only if `primary_chapter(text) == ch` (not merely if `ch` is mentioned anywhere). Docstring: an answer that names several chapters belongs to the first one it names; "near this chapter" was attributing chapter 2's worst scene to chapter 3's brief.
  - Add `character_items` to the returned dict: every `thinnest_character` answer whose `primary_chapter` is None (names no chapter), as `[reader] text`. In `build_panel_brief`, drop the `**Deepen character**` change entry entirely; instead, if `info["character_items"]` is non-empty, emit a section `## CHARACTER NOTES (whole-book, not this chapter's instruction)` after WHAT TO CHANGE listing them. If a `thinnest_character` answer DOES name a chapter as its primary, it still counts as a mention for that chapter, but goes under CHARACTER NOTES too, not under changes.
  - `missing_scene`: change the change-entry text `Panel identifies a scene gap near this chapter.` → `Panel identifies a scene gap in this chapter.` (attribution is now by primary chapter, so "near" is no longer doing work).
  - COMPRESS target note: after the clamped note, append ` — an UPPER BOUND, not a goal: a cut_candidate verdict is a hypothesis about repetition, not length (revision-playbook); find what repeats and break it, and let the length follow.` Do this inside `build_panel_brief` only (cuts briefs have measured fat behind their target).

- [ ] **Step 3** — Run `uv run pytest tests/test_gen_brief.py -q` → pass; then the full suite. Commit:

```
fix: gen_brief attributes a panel answer to the first chapter it names, matches zero-padded chapters, and labels COMPRESS an upper bound

"Chapter 03" never matched chapter 3, so one persona's verdicts were
silently dropped; an answer naming chapters 2 and 3 was briefed to
both; chapter-less thinnest_character answers became "Deepen character
in this chapter".
```

## Task D2: `apply_cuts.py` — `--verify-protected`, SKIP message

**Files:** `shared/scripts/apply_cuts.py`, `tests/test_apply_cuts.py`, `skills/revise/SKILL.md`

- [ ] **Step 1** — Tests first. Append to `tests/test_apply_cuts.py`:

```python
def test_verify_protected_reports_lines_no_longer_in_any_chapter(tmp_path):
    setup_project(tmp_path)
    (tmp_path / "edit_logs/protected.md").write_text(
        "# ch03\nThe council chamber smelled of tallow and wet wool.\n"
        "This sentence was reworded out of existence.\n")
    result = run_in(tmp_path, "--verify-protected", "edit_logs/protected.md")
    assert result.returncode == 1, result.stdout + result.stderr
    assert "NOT FOUND" in result.stdout
    assert "reworded out of existence" in result.stdout
    assert "tallow and wet wool" not in result.stdout.split("NOT FOUND", 1)[1]


def test_verify_protected_exits_zero_when_every_line_is_present(tmp_path):
    setup_project(tmp_path)
    (tmp_path / "edit_logs/protected.md").write_text(
        "The council chamber smelled of tallow and wet wool.\n")
    result = run_in(tmp_path, "--verify-protected", "edit_logs/protected.md")
    assert result.returncode == 0, result.stdout + result.stderr


def test_rewrite_skip_message_prints_the_rewrite(tmp_path):
    import json
    setup_project(tmp_path)
    cuts = json.loads((tmp_path / "edit_logs/ch03_cuts.json").read_text())
    cuts["cuts"][0]["action"] = "REWRITE"
    cuts["cuts"][0]["rewrite"] = "He realized the meeting had been arranged."
    (tmp_path / "edit_logs/ch03_cuts.json").write_text(json.dumps(cuts))
    result = run_in(tmp_path, "3")
    assert "REWRITE cuts are applied by hand" in result.stdout
    assert "He realized the meeting had been arranged." in result.stdout
```

- [ ] **Step 2** — Implement: `--verify-protected PATH` as a mode that makes the positional `chapter` argument optional (`nargs="?"`); it loads the protected lines, whitespace/quote-normalises every `chapters/ch_*.md`, and prints `FOUND` / `NOT FOUND` lists; exit 1 if any NOT FOUND. Docstring: a kept rewrite may reword a protected line, and a line sourced from a superseded drafting attempt may never have been in the manuscript; either way it protects nothing, and the skill re-quotes it at the start of each cycle. SKIP message → `SKIP [REWRITE] REWRITE cuts are applied by hand — rewrite: {rewrite[:80]!r}  (quote: {quote[:40]!r})`.

- [ ] **Step 3** — `skills/revise/SKILL.md` Diagnose step 2 (protected.md): replace `- every entry in \`three_strongest_sentences\` from every chapter\n     verdict in \`eval_logs/\` (drafting and prior revision cycles);` with `- every entry in \`three_strongest_sentences\` from the verdicts of KEPT attempts in \`eval_logs/\` (drafting and prior revision cycles) — a superseded attempt's strongest sentence may never have been in the manuscript;` and after `Commit \`cycle N: protected lines\`` … add a new sentence before it: ` Then run \`python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/apply_cuts.py" --verify-protected edit_logs/protected.md\` and re-quote every NOT FOUND line from the current manuscript (a kept rewrite may have reworded it; two cycle-1 lines protected nothing in cycle 2 on one run until a hand diff found them).`

- [ ] **Step 4** — Run tests; commit: `feat: apply_cuts --verify-protected reports protected lines the manuscript no longer contains; the REWRITE skip says what it means`.

---

# Part E — One-line clarifications

Covers: foundation 4, 5; revise 3, 7, 8, 11, 16, 18, 19, 20, 23; draft 3, 4, 5, 6.

## Task E1: Revise clarifications

**Files:** `skills/revise/SKILL.md`, `shared/rubrics/chapter.md`

- [ ] Setup step 4: after `this session runs cycle N = revision_cycle + 1.` add ` Run cycles in-session until the plateau rule or the maximum stops you; each cycle's \`cycle N complete\` commit is a resume point, so a session that ends mid-run loses at most the cycle in progress.`
- [ ] Diagnose step 1: replace `**arc_summary.md** — regenerate it fresh:` with `**arc_summary.md** — on cycle 1, or if the file is missing, build it fresh; on later cycles run the Measure resync procedure over it instead and regenerate only if a quoted passage fails verification (regenerating a file that was resynced verbatim-by-construction can only add drift). Fresh build:`
- [ ] Diagnose step 3 "Which chapters": replace `only chapters whose score\n   fell last cycle, or whose last reported\n   \`overall_fat_percentage\` was 12% or higher.` with `only chapters whose KEPT score fell last cycle — compare the chapter's kept score at the end of cycle N−1 with its kept score at the end of cycle N−2; a baseline is not a kept score, and baselines reliably come in under the prior kept number. Do not key on the last reported fat percentage: it was measured BEFORE that cycle's cuts, so it re-dispatches by construction the chapter it just cut.` And after `Record any chapter you skip, and why, in \`edit_logs/skipped.md\`.` add ` If no chapter qualifies, still make the step commit — \`cycle N: adversarial cuts (0 words — no chapter qualified)\`, \`--allow-empty\` — and skip apply_cuts and the splice audit; the resume check greps for that commit.`
- [ ] Step 5 reader panel, consensus shape: after `\`chapter\` MUST be a JSON integer,\n   not a string, because gen_brief.py matches on int equality.` add ` A character-level item (a \`thinnest_character\` consensus) has no chapter: write \`{"question": "thinnest_character", "chapter": null, "character": "<name>", …}\`; gen_brief prints these under CHARACTER NOTES rather than as a chapter instruction.`
- [ ] Fix step 3 (rewrite): after the protected.md sentence add: ` If a kept rewrite removes or changes a fact that canon.md records under an in-story entry sourced to this chapter, amend that entry in the same commit — the chapter is the record and canon describes it; a stale entry turns the next judge's reading of an eval-requested cut into a "canon drift" violation.`
- [ ] Measure step 1: replace `Log to results.tsv:` … through the end of the `**If you measure more than once in a cycle**` paragraph with a single rule: the results.tsv `full-eval cycle N` row is written ONCE, at the end of Measure, after any step-2 fix-and-re-measure; an intermediate measurement is logged at the time with a plain description and no `full-eval` prefix. (Keep the row format line and the `judge=<model>` suffix; keep the sentence that the prefix is a contract the plateau check greps for.)
- [ ] Exit: after `for the record.` add ` It writes to \`edit_logs/\`, which is gitignored; paste its summary table into the \`revision complete\` commit message so the record is tracked.`
- [ ] `shared/rubrics/chapter.md`, the `CANON (established hard facts -- violations are bugs):` block: add ` An entry sourced to the target chapter itself (\`(ch_NN)\` where NN is the chapter you are judging) describes that chapter's committed text; if the chapter no longer states it, report it under \`new_canon_entries\` as an amendment ("supersedes: …"), not under \`violations\` — unless another chapter's entry depends on it, in which case it is a violation of that other entry.` Then in the canon_compliance dimension line (`- canon_compliance: Check ALL facts against canon. List violations.`) append ` (an entry the target chapter itself established and has now changed is an amendment, see CANON above).`
- [ ] Commit: `docs: revise — cycles loop in-session, arc_summary is resynced not regenerated, cut selection keys on kept scores, zero-chapter cuts still commit, one full-eval row per cycle, canon entries amended with the rewrite that changes them`.

## Task E2: Foundation guide and draft rule clarifications

**Files:** `skills/foundation/references/layer-guides.md`, `skills/draft/references/drafting-rules.md`, `shared/genres/ya.md`, `shared/rubrics/foundation.md`

- [ ] layer-guides, thread ratio sentence: replace `(15 for an 80,000-word novel; a short story owes\none or two, and the form may drop the ledger entirely)` with `(15 for an 80,000-word novel). Where the form drops \`foreshadowing_balance\` from its base dimensions — \`short-story\` does, on the reasoning that a story which plants and pays within four pages does not keep a ledger — the ledger is not owed at all and this section is skipped; the form's decision governs this guide`.
- [ ] layer-guides, `BUILD THE REGISTRY WITH THE ROLES LISTED IN THE PACK'S\n\`## Cast Requirements\`, at the depth each entry specifies.` → append ` Where the form's \`## Foundation Guidance\` says fewer — a short story builds only the characters who appear — the form wins; do not write a paragraph explaining why a pack role is absent (that is prose addressed to the evaluator, and a judge has flagged exactly that).`
- [ ] drafting-rules.md, after rule 4 (`Plant ALL foreshadowing elements listed under "Plants."`) insert a new sentence in rule 1 or a note under the Core rules: `Where the outline's beat prose, a voice.md exemplar, and outline.md's \`## Facts the story must not contradict\` disagree on a number, the facts section wins; beat prose and exemplars are illustrations, the table is the contract (one chapter copied "under five seconds" from a beat when the table said 35).` And in rule 1, after `Do not truncate or summarize.` add ` Text the outline requires verbatim on the page (a letter, a transmission) counts toward the target; the target is the chapter's length, not the prose around the quotation.`
- [ ] drafting-rules.md rule 11 (metaphors/voice) or a new line after rule 8: `Calibrate against voice.md's exemplar passages; do not reproduce them. The judge docks verbatim reuse, and an outline beat that paraphrases an exemplar is a cue to the register, not a sentence to copy.`
- [ ] `shared/genres/ya.md` rule 26: append ` slop_score.py's telling check will flag some of these declaratives ("She was furious."); at this register that is expected and small — absorb the penalty rather than rewriting around the regex, which produces the hedged interiority the rule forbids.` Run `validate_genre_pack.py` on ya.md.
- [ ] `shared/rubrics/foundation.md` cross-checks: add to the `internal_consistency`-relevant cross-check (or 2b's neighbourhood) one line: `Check the outline's own beat prose against its \`## Facts the story must not contradict\` section — a beat that says "under five seconds" beside a table that says 35 is an internal contradiction this dimension exists to catch, and one run passed exactly that through four iterations.`
- [ ] Commit: `docs: the form governs the ledger and cast guidance; the facts table outranks beat prose and exemplars; YA absorbs the telling penalty`.

---

# Task Z: Release 0.20.0

- [ ] `uv run pytest tests/ -q`; genre + form validators; `gate_solver.py shared/genres/*.md` all ok.
- [ ] Bump `0.19.0` → `0.20.0` in `plugin/autoauthor/.claude-plugin/plugin.json` and twice in `.claude-plugin/marketplace.json`; update the test count in AGENTS.md; CHANGELOG entry summarising Parts A–E and the 0.19.0 correction.
- [ ] Commit `release: 0.20.0 — the 2026-08-19 shakedown findings`.

## Coverage

| Finding | Task |
|---|---|
| foundation 1, 2, 3, 6 | C1 |
| foundation 4, 5 | E2 |
| review 1, 3 | A1 |
| review 2, 4, 5 | A2 |
| revise 1, 2, 13, 22 | D1 |
| revise 5, 12, 14 | D2 |
| revise 6, 9, 10 | B2 |
| revise 21 | B1 |
| revise 4, 15 | C3 |
| revise 3, 7, 8, 11, 16, 18, 19, 20, 23 | E1 |
| draft 1, 2 | C2 |
| draft 3, 4, 5, 6 | E2 |
| revise 17 | not a bug (0.98 ≠ ninety-eight); no change |
