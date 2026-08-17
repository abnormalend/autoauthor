---
name: revise
description: Use when a novel project is in the revision phase, or the user asks to revise the draft, tighten chapters, run the reader panel, or apply adversarial edits.
---

# Novel Revise — Phase 3a

Revision cycles: diagnose (cuts + panel) → fix (briefs + rewrites) →
measure (full-novel score). Stop on plateau: full-novel score change
< 0.5 across 2 consecutive cycles, minimum 3 cycles, maximum 6.

## Setup

1. Verify the project (state.json + voice.md present), clean tree
   (dirty → STOP and ask), phase `revision`. Anchor the session in the
   project directory; absolute paths when in doubt.
2. **Resolve the genre.** Run from the project directory:

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/resolve_genre.py"
   ```

   If it exits non-zero, STOP and report — an unresolvable or conflicting
   genre stack must be fixed before any revision work. Keep the reported
   pack paths; every judge dispatch below needs them. If `state.json` has no
   `genre` field at all, or its `genre` is null, STOP and run the migration
   in `novel/SKILL.md` first — a null genre resolves silently to `general`,
   so the resolver exiting 0 is NOT evidence that anyone chose a genre.
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
3. Required reading: `"${CLAUDE_PLUGIN_ROOT}/shared/craft/ANTI-PATTERNS.md"`,
   the project's voice.md, `references/revision-playbook.md` (this
   skill's directory), and every genre pack path the resolver reported.
4. Resume: state.json `revision_cycle` is the last COMPLETED cycle;
   this session runs cycle N = revision_cycle + 1.
5. **Malformed judge responses (applies everywhere in this skill):**
   fence-wrapped but otherwise valid JSON is VALID — strip the fences;
   for genuinely malformed output, one strict retry, then skip that
   dispatch and record it in
   `edit_logs/skipped.md` with the cycle, step, and chapter.

## One cycle (N)

**Resume check:** inspect `git log --oneline -20` for this cycle's
step commits (`cycle N: arc summary`, `cycle N: protected lines`,
`cycle N: adversarial cuts (…)`, `cycle N: reader panel`). Skip any
Diagnose step whose commit already exists — NEVER re-run the
adversarial-edit + apply-cuts pair
for a cycle that already applied cuts; cutting twice compounds and
can gut chapters.

### Diagnose

1. **arc_summary.md** — regenerate it fresh: first line
   `Novel: <total words> words across <count> chapters.`, then per
   chapter: a 4–6 sentence event summary, the opening and closing
   ~100-word passages, and 1–2 key dialogue exchanges. Commit
   `cycle N: arc summary`.
2. **Build `edit_logs/protected.md`** (create on cycle 1, append every
   cycle after). It is a newline-delimited list of lines no cutting
   pass may touch, and it comes from two sources that already exist:
   - every entry in `three_strongest_sentences` from every chapter
     verdict in `eval_logs/` (drafting and prior revision cycles);
   - for each row of outline.md's foreshadowing ledger and each
     `Plants:`/`Payoffs:` entry, open the chapter it names and quote
     the sentence that carries the plant or payoff — the ledger's
     description is not a substring of the prose, so the row itself
     protects nothing.
   Group them under `#` headings by source; the scripts ignore
   headings and blank lines. Cutting judges see one chapter and have
   no memory: across three cycles on one project five lines were
   protected by hand and two of them were attacked in consecutive
   cycles, including the sentence both cycle-1 judges had named the
   chapter's strongest. Commit `cycle N: protected lines` (with
   `--allow-empty` if `edit_logs/` is gitignored, which the default
   template does).
3. **Adversarial edit.**
   **Which chapters.** Before dispatching, archive the previous
   cycle's verdicts so `apply_cuts.py all` sees only this cycle's:
   `mkdir -p edit_logs/cycle<N-1> && mv edit_logs/ch*_cuts.json
   edit_logs/cycle<N-1>/ 2>/dev/null || true`. A stale cuts file
   re-applies last cycle's cuts to a chapter you chose not to
   re-dispatch — including any line you restored by hand. Then: in
   cycle 1, every chapter. In later cycles, only chapters whose score
   fell last cycle, or whose last reported
   `overall_fat_percentage` was 12% or higher. Judges asked for 10–20
   cuts return 10–20 cuts whatever the fat; on a manuscript at 9–13%
   fat one run's cycle-2 pass removed 269 words, needed four
   protections and one restore, left five splice defects, and moved
   the full-novel score 7.86 → 7.86 with `overall_engagement` down a
   point. Record any chapter you skip, and why, in `edit_logs/skipped.md`.

   For EACH chapter, dispatch a fresh judge
   subagent: "Read the rubric at
   `<absolute plugin path>/shared/rubrics/adversarial-edit.md` and the
   genre pack(s) at `<resolved pack paths, primary first, each labeled
   with its role>`, and follow the rubric exactly. The project directory
   is `<absolute project path>`. The target chapter file is `<absolute path to
   chapters/ch_NN.md>`. Return ONLY the JSON the rubric specifies."
   Save each response verbatim to `edit_logs/chNN_cuts.json` (exact
   filename — apply_cuts.py globs it). Dispatch in parallel batches
   of 4–6 (malformed responses: see Setup's shared policy).
4. **Apply mechanical cuts:**
   `python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/apply_cuts.py" all --types OVER-EXPLAIN REDUNDANT --min-fat 15 --protect-file edit_logs/protected.md`
   Review its FAIL lines; apply any high-value failed cuts by hand.
   **Also handle its SKIP [REWRITE] lines** — do not filter the
   script's output down to FAIL/SAVED and move on, or you will silently
   drop this entire category (on a first cycle it can be 250+ items and
   the bulk of the available improvement). These cuts need replacement
   prose, not deletion: apply each using the `rewrite` text from the
   chapter's cuts JSON. They are trims, not rewordings — a good one
   stops a sentence early or drops the second half of a doubled image,
   keeping the author's own words.

   Two filters, both required:
   - **Reject any "rewrite" longer than its quote.** That is an
     expansion wearing a trim's clothes.
   - **Skip any whose containing paragraph contains dialogue.** This
     one is measured, not cautionary. Action beats sitting between
     lines of speech ("She set one measurement beside another, flat, a
     tailor calling numbers") read as redundant to a cutting judge and
     are exactly what stops an exchange from becoming talking heads.
     Applying them wholesale on one project dropped voice_consistency
     8→7 and overall_engagement 8→7 at the full-novel eval; restoring
     only the dialogue-adjacent ones and keeping the narration-only
     ones recovered voice to 8 and lifted the novel score above where
     it started. Apply the narration-only trims freely; leave the
     dialogue paragraphs alone.
   - **Skip any the script reported as `PROTECT`.** It reports them
     even for REWRITE cuts, because the by-hand pass would otherwise
     be the first place protection applied — and on one run it was,
     one step too late.
   **If the run reports `Applied: 0` because every chapter fell under
   `--min-fat 15`,** re-run with `--min-fat 0`, which keeps the type
   filter and drops only the gate, and say so in the commit message.
   This is the usual case, not the exception: a draft that had a
   post-draft slop pass typically comes back at 7–13% fat, and on one
   run the 15% gate excluded three of four chapters on the first pass.
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
   empty-quotes, space-before-punct, no-space-after-quote, doubled-word,
   glued-sentence, leading-whitespace, trailing-whitespace. Six mechanical cuts in one
   cycle produced five of these, and two kinds were outside the
   checklist this step used to carry.

   Repair each by hand against the pre-cut text: usually promoting a
   comma to a period, restoring a paragraph break, or merging two
   speeches that lost the beat between them. Re-run until only the
   false positives you have already checked remain (the exit code will
   still be 1 for those; say so in the commit message). Expect one or
   two of them from intentional oddities (an emoticon on a
   hand-lettered sign) — check them, then leave them.

   Audit against the tree as it stood at the START of this cycle, and
   re-run after ANY later mechanical pass in the same cycle. A defect
   introduced in cycle N and missed by its audit will otherwise sit in
   the manuscript indefinitely, because cycle N+1 diffs against a tree
   that already contains it — that is exactly how a `he said, , and`
   survived a cycle.
   Then verify no chapter fell below the unit floor (Setup step 2)
   (`wc -w chapters/ch_*.md`). If one did, restore it with
   `git checkout HEAD -- chapters/ch_NN.md` and exclude it from cuts
   this cycle. Run the slop scorer over the touched chapters as a
   sanity check.
   **Finally, resync arc_summary.md** (see the resync procedure under
   Measure). This step just edited most of the manuscript, and the file
   built in step 1 now quotes sentences that no longer exist in the
   book — the reader panel in step 5 and the full-novel judge in
   Measure both read it. Commit `cycle N: adversarial cuts (<words
   removed> words)`.
5. **Reader panel** — dispatch FOUR judge subagents in parallel, one
   per persona: "Read the rubric at `<absolute plugin
   path>/shared/rubrics/reader-panel.md` and the genre pack(s) at
   `<resolved pack paths, primary first, each labeled with its role>`,
   and follow the rubric exactly. Your
   assigned persona is <editor|genre_reader|writer|first_reader>. The
   project directory is `<absolute project path>`; the input files are
   arc_summary.md and, if outline.md carries one, its `## Author-facing
   only (never on the page)` section — nothing else from outline.md.
   Return ONLY the JSON the rubric specifies."
   Assemble `edit_logs/reader_panel.json` as:
   `{"readers": {"editor": {...}, "genre_reader": {...}, "writer":
   {...}, "first_reader": {...}}, "consensus": [...],
   "disagreements": [...]}` — consensus = any chapter, character, or
   scene named by 3+ readers for the same question; disagreements use
   the exact shape gen_brief.py consumes: `{"question": "<question
   key>", "chapter": <integer N>, "flagged_by": ["<personas>"],
   "not_flagged": ["<personas>"]}` — `chapter` MUST be a JSON integer,
   not a string, because gen_brief.py matches on int equality. Commit
   `cycle N: reader panel`.

   **What the panel is and isn't evidence of.** All four readers see
   arc_summary.md and never the prose. Their verdicts are therefore
   claims about the *summary*, and the summary is lossy in one
   direction: it compresses dramatized scenes into clauses. So a
   chapter whose strength is texture, restraint, or slow accumulation
   reads to the panel as drag, and a scene the summary renders in six
   words reads as missing. Expect two recurring false positives —
   "missing scene" for a beat that is fully on the page, and "cut
   candidate" for a chapter that is merely quiet. Both can carry 3+
   reader agreement, because all four are misled by the same lossy
   line. Treat a `cut_candidate` verdict as a hypothesis about
   REPETITION, not about length. Verification is mandatory before any
   brief (Fix step 1).
   If `edit_logs/` is gitignored (the default template), the panel and
   cuts JSON are untracked; make the step commit with
   `--allow-empty` so the resume check still finds it.

### Fix (consensus items, priority order per the playbook)

For each consensus item, in playbook priority order (cut candidate →
missing scene → thin character → weak scene → consistency):
1. **Verify the item against the chapter text before briefing
   anything.** Open the chapter (and the outline entry) and confirm the
   defect is on the page. Panel consensus is not evidence that it is —
   the readers saw only arc_summary.md, so an item can carry 3-of-4
   agreement and still be an artifact of one compressed summary line.
   Check the specific claim:
   - *any item already in `edit_logs/skipped.md` from a prior cycle* →
     skip it again unless the panel supplies evidence the earlier
     verification did not have. "Cut chapter 2" carried 4/4 in three
     consecutive cycles on one run and was verified-and-skipped the
     same way each time.
   - *missing scene* → grep the chapter for the beat. If it is already
     dramatized, the summary was lossy, not the chapter. Do not rewrite.
   - *cut candidate* → find what actually repeats. Compare the chapter's
     closing move against its neighbours' closing moves; a real cut
     candidate repeats a beat or a posture, and the fix is to break the
     repetition, which is rarely the same edit as making it shorter.
   - *thin character* → count their actual lines and scenes.
   - any item → check the outline entry, which may already require the
     thing the panel wants added, or forbid it by design.
   If the item does not survive this check, skip it, record it in
   `edit_logs/skipped.md` with what you verified and where, and move to
   the next item. Rewriting a chapter to add a scene it already
   contains costs it its score and gains nothing.
2. Generate a brief:
   `python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/gen_brief.py" --panel <ch> --chapter-words <shape.chapter_words>`
   (or `--cuts <ch>`, which takes the same flag; use `--eval <ch>` once
   this cycle's chapter evals exist). Review the brief; sharpen it by hand if the playbook
   recipe for this item type demands specifics the script missed.
   **Check the brief's TARGET before using it.** Pass
   `--chapter-words <shape.chapter_words>` so the script clamps COMPRESS
   and TIGHTEN targets to the unit floor; without it the floor is the
   novel's 1800. If the brief's TARGET is at the floor, the chapter has
   no compression left in it and the item wants a different fix.
3. Rewrite the chapter in-session following the brief plus the
   playbook's Rewrite rules, with the drafting context recipe
   (every layer file the form builds — voice.md and characters.md
   always; world.md and MYSTERY.md where the form built them — in full;
   the old chapter as raw material — keep what works; previous
   chapter's last ~1000 words;
   next chapter's opening ~1500 chars). Before cutting any element,
   grep the rest of the manuscript for it: a compression brief that
   removes a plant (an object, a card, a named regular) silently breaks
   its payoff chapters later. Check the old chapter's lines against
   `edit_logs/protected.md` too: a rewrite may reword a protected line,
   but it may not lose it.

   **Three canon pre-flight checks before you write a line.** These are
   the errors that actually recur, and each one costs an attempt:
   - *Reserved sentence architectures.* canon.md's dialogue-invariants
     line usually assigns one rhetorical shape to one character
     exclusively (e.g. balanced-antithesis epigrams to a single
     speaker). Writing new dialogue for anyone else, it is very easy to
     reach for that shape at their emotional peak — it happened twice
     in two cycles on one project, to two different characters. Re-read
     that canon line and check your new lines against it before
     dispatching the judge.
   - *Canonical form of any object you touch.* If a drawing, notebook,
     letter or photograph already exists, canon fixes when it was made,
     where it lives, and how it is handled. Do not invent a fresh
     scene for it from memory; grep canon.md and the originating
     chapter first. Inventing a plausible-but-wrong origin, or adding
     an unreconciled second copy of an existing artifact, both read as
     continuity bugs.
   - *Arithmetic you introduce.* Any new interval, count or date
     ("nineteen months", "six Saturdays deep") will be checked against
     the Story Clock. If you do not need the number, do not write one.
4. Score it exactly as draft does: scratch copy to
   `eval_logs/ch_NN_attempt_<k>.md`, slop score, chapter-judge
   dispatch (labeled target/previous paths, per chapter.md's
   contract, and the genre pack(s) at `<resolved pack paths, primary
   first, each labeled with its role>`), final score = judge minus slop
   penalty. The judge writes its own verdict file
   (`eval_logs/<UTC yyyymmdd_hhmmss>_chNN.json`) and returns the path
   and score. Compute the UTC timestamp yourself before dispatching; the
   path in the prompt is literal, and it is the path you will hand to
   score_verdict.py. Keep if the final score beats the chapter's
   baseline (see below); else discard
   (`git reset --hard HEAD`), max 3 attempts per chapter per cycle.
   After 3 failed attempts, leave the chapter as-is this cycle and
   record the item in `edit_logs/skipped.md`. Attempt rows go to
   `eval_logs/attempts.tsv` and fold into results.tsv at commit (same
   columns as draft's rows, but the phase column is `revision`).
   Baseline rows carry `baseline` in the keep_discard column and fold
   in with the rest; they are the record of what each cycle's judge
   thought of the text it started from.
   Commit kept rewrites: `cycle N: <item type> ch NN (<score>)`.

   **The baseline must be same-cycle. This is not optional and it is
   the most common way this step goes wrong.** The obvious baseline —
   the chapter's last score in `eval_logs/` — is usually a DRAFTING
   score, and the drafting judge is measurably more generous than the
   revision judge on identical prose. Measured on one project: a
   chapter carrying a recorded 8.0 scored 7.0 when its near-original
   text was re-judged during revision, and another carrying 7.5 scored
   7.0. Gating a revision-phase score against a drafting-phase number
   silently discards work that is not actually worse.

   So: **baseline before you rewrite, not after a rewrite fails.** At
   the start of Fix, dispatch the chapter judge once for EVERY chapter
   you intend to touch this cycle, in parallel, against the current
   committed text (same labeled paths as a scoring dispatch; write each
   to `eval_logs/<UTC yyyymmdd_hhmmss>_baseline_chNN.json` — the
   `_chNN.json` suffix is what `gen_brief.py --eval` globs for, so the
   brief for that chapter picks the baseline up as its latest eval).
   These run concurrently
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

### Measure

1. **Resync arc_summary.md, then dispatch.** The full-novel judge
   scores the novel from this file alone, so a stale line here is a
   wrong score for the whole cycle.

   **Resync procedure** (used here and at the end of Diagnose step 4;
   run it over EVERY chapter changed since the file was written — cuts
   and by-hand repairs, not just rewritten chapters):
   - Rebuild each changed chapter's opening and closing ~100-word
     passages mechanically from the current chapter text, so they are
     verbatim by construction rather than by transcription.
   - Recompute every per-chapter word count in the `## Chapter NN`
     headers and the header line's total (`wc -w chapters/ch_*.md |
     tail -1`); use that same fresh total in the results.tsv row.
   - Re-verify every remaining quoted line (the key-dialogue
     exchanges): whitespace-normalise both sides and confirm each quote
     still occurs in its chapter. For any that no longer match, locate
     the longest surviving prefix and replace the quote with the
     current paragraph containing it.
   - For any beat a prior cycle's panel consensus asked for and you
     then wrote, the summary must carry it at the granularity that was
     asked for — a scene the panel wanted gets its dialogue, not a
     clause. A 16-line exchange rendered as one clause was named
     "missing" by 3 of 4 readers in each of the next two cycles.
   - Repeat until zero quoted passages fail the check. Do not hand a
     summary containing invented or deleted prose to a judge.

   Dispatch the full-novel judge: "Read the rubric at
   `<absolute plugin path>/shared/rubrics/full-novel.md` and the genre
   pack(s) at `<resolved pack paths, primary first, each labeled with its
   role>`, and follow the rubric exactly. The form is `<form.name>` and
   its band is `<form.band>`. The project directory is
   `<absolute project path>`. The input files are voice.md, characters.md,
   outline.md, `<world.md, where the resolved form builds it>` and
   arc_summary.md. Write the JSON the
   rubric specifies — bare JSON, no fences — to `<absolute project
   path>/eval_logs/<UTC yyyymmdd_hhmmss>_full.json` and return only
   that path and `work_score`." Compute the UTC timestamp yourself
   before dispatching; the path in the prompt is literal, and it is the
   path you will hand to score_verdict.py. Log to results.tsv:

   **Compute the score; do not take the judge's word for it.**

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/score_verdict.py" \
       eval_logs/<the path the judge returned>
   ```

   It averages the dimension scores and compares that to the aggregate
   the judge reported. **Record the computed number.** A judge is
   qualified to score a dimension and has no particular claim to
   averaging seven of them: a live cycle returned dimensions averaging
   7.43 alongside `work_score: 7`, against a phase that stops when that
   number moves by less than 0.5. Exit 1 means they disagreed; the
   message names the value to use.

   `<ISO timestamp>\trevision\t<work_score>\t<total words>\tkeep\tfull-eval cycle N`
   (the `full-eval` description prefix is a contract — the router's
   plateau check greps for it).

   **If you measure more than once in a cycle** — legitimate when a
   measurement comes back down and you repair the cause and re-measure
   — only the FINAL measurement may carry the `full-eval cycle N`
   prefix. Log the intermediate one with a plain description and no
   `full-eval` prefix, or the plateau check will read one cycle as two
   and can stop revision early on a number you already fixed.

   **Read the dimension scores, not just the total.** A total that
   moves 0.2 looks like noise; the dimensions underneath show whether
   it is. Two dimensions dropping a full point each while a third rises
   is a real regression with a specific cause, and comparing the
   per-dimension row against the previous cycle's usually names it.
2. Address the eval's `top_suggestion` if actionable this cycle (the
   playbook's eval-callout patterns have the recipes); at most 2 such
   fixes per cycle, scored and gated like any rewrite.
3. Update state.json: `revision_cycle: N`, `work_score`. Commit
   `cycle N complete (<score>)`.
4. **Plateau check.** If N >= 3 and the last three `full-eval` scores
   in results.tsv show |score(N) − score(N−1)| < 0.5 AND
   |score(N−1) − score(N−2)| < 0.5 → stop. Also stop at N = 6
   regardless.

## Exit

Set state.json `phase: "review"`. Run
`python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/voice_fingerprint.py"`
for the record. Commit `revision complete: <cycles> cycles
(<final score>)`. Pushover notification (pushover skill): title
"autoauthor: revision", message with cycles run, score trajectory, next
step `/autoauthor:review`. Report the same to the user.

## Guardrails (from the playbook — non-negotiable)

Never compress a unit below the floor computed in Setup (0.5 ×
shape.chapter_words; 1800 for a novel). Expect rewrites to run ~30%
long — brief for shorter than you want. If the full-novel eval names a
NEW weakest chapter twice in a row after fixes, stop chasing it.

Never brief a rewrite off a panel consensus item you have not confirmed
in the chapter text. The four readers share one lossy input, so they
share its errors; agreement measures legibility in summary, not truth.

Never hand arc_summary.md to a judge without re-verifying that every
passage it quotes still occurs in the manuscript. It is the sole input
to the reader panel and the full-novel judge, and any step that edits
chapters invalidates it.

Cut narration, not scenes. A compression that summarizes a dramatized
beat scores worse than the bloat it replaced. Inside a scene, leave the
action beats between lines of dialogue alone — they are what keeps an
exchange from being talking heads, and every cutting judge reads them
as redundant.

Never discard a rewrite against a score you did not measure THIS cycle.
Drafting-phase numbers run high and prior-cycle numbers drift by more
than half a point on identical text; baseline every chapter you will
touch at the start of Fix, and re-baseline before any discard that
would otherwise rest on an older number.

## Optional cycle-1 diagnostic: chapter tournament

If the user asks for deeper diagnosis (or cuts and panel disagree about
the weakest chapters), run head-to-head comparisons: dispatch judge
subagents given two chapter files each, asked only "Read both chapters.
Which is the stronger chapter and why — one paragraph, then a final
line WINNER: <NN>." Seed pairings from adjacent per-chapter scores.
Rankings inform which chapters get briefs first. Skip by default.
