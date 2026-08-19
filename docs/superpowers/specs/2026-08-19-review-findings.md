# autoauthor:review (0.18.0) — findings from round 1 on `redshift`

Issues and bugs only. Importance: 1 (cosmetic) – 5 (silently wrong result).

## 1. The judge is never told the resolved form/shape, so it reviews a short story as a failed novel — importance 5
`manuscript-review.md` opens "You are reviewing a complete novel manuscript" and the
skill's dispatch prompt passes only the rubric path, the genre pack paths and the
project dir. The judge read the SF pack's `shape.words.extended: [90000, 110000]`
and returned, as its ONLY major item, "a novelette presented as a novel … against a
declared novel shape of 90–110k" — but `state.json` declares `form: short-story`
(resolver: words 1000–7500, target 5000; 5,071 delivered, on target). Knock-on
damage: item 2 was explicitly conditioned on item 1 ("becomes a major hole the
moment item 1 resolves toward novel"), and the judge's phrasing throughout
("across a novel it would read as a tic") is calibrated to the wrong length.
The review's headline defect was a pipeline artifact, and on a project where the
judge had tagged it `qualified: no` it would have driven a round of "fixes"
toward expanding a finished short story. Fix: have the dispatch prompt (or the
rubric via state.json) pass the resolver's `form.label`, `shape.words` band and
`shape.target_words`, and have the rubric say "manuscript of the declared form"
rather than "novel" — the draft/revise judges already get `shape`, this one
doesn't.

## 2. `gen_brief.py --eval <ch>` invoked without `--chapter-words` — importance 3
Step 5 says `gen_brief.py --eval <ch>` bare. revise/SKILL.md (which this skill
says applies verbatim) warns that without `--chapter-words <shape.chapter_words>`
the COMPRESS/TIGHTEN floor defaults to the novel's 1800, which for this project
(chapter_words 1200, floor 600) would print a target that clamps wrong. Not
exercised this run (stopped before Fix) but latent on every compressed-form
project. Fix: add the flag to the command in step 5.

## 3. Judge is not pointed at the title — importance 1
The review is headed "**REDSHIFT**" (the directory name); `state.json.title` is
"Her Years, Our Years". Cosmetic in the log, but the critic section is meant to
read like a newspaper review and is the piece most likely to be quoted back to
the author. Fix: pass the title in the dispatch prompt or tell the rubric to read
it from state.json.

## 4. Stopping condition fires on round 1 with 4 moderate-unqualified items on the table — importance 2
"zero major unqualified items" stopped the loop immediately, so items 3, 4, 6, 7
(all moderate, `qualified: no`, each a concrete 1–3 line fix) were never attempted.
Arguably by design, but combined with finding 1 (the only major was spurious) the
round did zero fix work against a review that named several cheap, unqualified
defects. Suggest: stop on "zero major-unqualified" only if moderate-unqualified
is also ≤ 2, or always run Fix once on round 1 when unqualified moderates exist.

## 5. Exit commit message grammar — importance 1
`review complete: <R> rounds` → "review complete: 1 rounds".
