# Roadmap

Direction and open work. Detail lives in `docs/superpowers/specs/` (design)
and `docs/superpowers/plans/` (execution); this file is the index above them
and the home for work not yet worth a spec.

Last updated 2026-08-13.

---

## In flight

- **Pack shakedown.** Planted-defect run against the four new primary packs,
  testing whether their criteria actually bite a judge or merely read well.
  Foundation phase only. Blocks phase 2 below, which lifts the base
  dimensions out of `rubrics/foundation.md` and should not be built on packs
  that have never judged anything.

## Next — specced, ready to plan

All from [the form spec](docs/superpowers/specs/2026-08-13-form-parameterization-design.md),
in its phase order. Phases 0–2 are behaviour-preserving and A/B-verifiable
the way the fantasy port was.

- **0. Structured caps + gate solver.** `[cap N]` on every dimension across
  the fifteen packs, `DIMENSION_RE` extended, and a script that computes the
  highest gate consistent with TEMPLATE's policy instead of an author
  guessing one. Independently useful: run against the pack set as first
  shipped, it reports fantasy's max legal gate as 6.3 against a pipeline
  gating it at 7.0 — a bug that took a subagent reading prose to find.
  Prototype at `docs/superpowers/specs/2026-08-13-gate-solver-prototype.py`.
- **1. Form pack type.** `shared/forms/`, parser, validator, resolver. Ships
  `novel` only, with today's values, proving nothing moves.
- **2. Base dimension parameterization.** Lift `character_depth`,
  `outline_completeness`, `foreshadowing_balance`, `canon_coverage` and the
  rest out of `foundation.md`, the way the pillar dimensions were lifted.
  Largest single piece and the most silent-wrong-prone.
- **3. `short-story` and `novella` forms**, plus compressed-band sections on
  the genre packs.
- **4. Rename to `autoauthor`**, with migration. Bundled here because the
  installed base is effectively zero and grows monotonically.
- **5. `structure: collection`** — absorbs `autoanthology`, which is a
  pre-0.2.0 fork carrying four genre packs in the old prose format and none
  of the genre or form work.
- **6. `structure: series`** — series bible at the project root, `books/`
  beneath, per-book canon that may add to series canon but never contradict
  it.
- **7. `structure: serial`** — last, or dropped. The only value that breaks
  the score-plateau model the pipeline rests on.

## Later — identified, not specced

- **Literary device overuse.** Identified from a 0.2.0 draft
  (`time-squatting/ch_01.md`): 31 figurative constructions in 2,577 words,
  one every 83. Three distinct faults, needing two layers to catch:
  - *Monoculture.* ~25 of the 31 are one construction — `like` / `the way`
    + a specific human scenario. Individually most are good; collectively
    they become the narrator's tic, and nothing stands out because
    everything is reaching.
  - *Redundancy.* One character's single trait drew five separate figures
    inside ten lines. The reader had it at the first.
  - *Detachability.* "flat, like a total she was reading off a register" —
    `flat` already did the work. This is the operative test: **delete the
    figure; if the sentence loses nothing, it was ornament.**

  Mechanical half: a `figurative_density` metric in `slop_score.py`, built
  exactly like the existing `em_dash_density` (per 1000 words, threshold,
  graduated penalty), plus a repeated-construction check so monoculture
  scores worse than the same count spread across varied figures. Judged
  half: the detachability test cannot be regexed and belongs in
  `ANTI-SLOP.md` and `voice_clarity`. Thresholds should vary by form and
  genre — a compressed form cannot afford this at all, and literary fiction
  tolerates more than a thriller.

  Must not become "fewer similes". The same chapter earns figures where
  they carry the book's argument — a credit card "load-bearing since her
  sophomore year", a debt that "worked weekends", a metaphor in dialogue
  that a later line pays off. Figures tied to the subject earn their place;
  figures generated to make a sentence interesting do not. Character
  dialogue is exempt: a distinctive speaker's similes characterize the
  speaker and should differ from the narration's.
- **A `consent` axis in `CONTENT_AXES`.** `dark-romance` cannot express its
  defining constraint in frontmatter and had to buy the same protection with
  a blunt `conflicts_with` against `ya` and `cozy`. romance.io's taxonomy
  separates steam level from consent warnings for the same reason.
- **A `horror` pack.** A top-level Goodreads genre with no pack at all.
  `autoanthology` has one; this repo does not.
- **Shakedown slice 2 — chapter, drafting, reader panel.** The current run
  covers foundation only. `drafting-rules.md`, `chapter.md`, and
  `reader-panel.md` all read genre packs and none has been exercised.
- **Exercise the artifacts.** `braid.md`, `braid_map.md`, `power_ledger.md`,
  `clue_ledger.md`, and `encounter_ledger.md` are declared by packs and have
  never been produced by anything.
- **Warn on a dropped `beat_system`.** `merge()` silently takes the
  primary's. A secondary declaring a *different* one is detectable and
  always wrong; there is no `beat_system_sources` analogue to
  `content_register_sources`.
- **`epic` form.** Deferred until multi-POV and subplot braiding are written
  as actual dimensions rather than asserted as a difference from `novel`.
- **`flash` form.** Below the useful floor of a five-phase pipeline; only
  returns if a two-phase path is worth building.
- **Urban fantasy's masquerade.** Composes adequately as `fantasy` +
  `mystery` secondary, but nothing scores why the ordinary world does not
  know.
- **LitRPG / progression fantasy.** Runs on a power-milestone cadence rather
  than Save the Cat, so it has a genuine beat conflict — the strongest
  remaining candidate for a pack by the interaction test.

## Engineering — untested surfaces and missing scaffolding

- **No CI.** There is no `.github/workflows`. The 135 tests run only when
  someone remembers, and they are the only thing standing between the pack
  system and silent breakage. Cheapest item here by a distance.
- **Nothing tests the rubric → JSON contract.** Every test is structural:
  parse, validate, resolve. Rubrics are prompts, and the verdict schema six
  skills parse is verified by nobody. This has already bitten once —
  `gen_brief.py` read `lore_integration` and `world_consistency` through
  `.get()` after they were renamed, silently dropping feedback from every
  revision brief, covered by no plan task and no test. A fixture verdict per
  rubric, asserting the keys the skills actually read, needs no live judge.
- **`novel-import` has never been exercised.** It infers a genre from a
  finished manuscript and writes it into `state.json` — now across fifteen
  packs rather than nine, including distinctions that are genuinely fine
  (paranormal romance vs romantasy). The one skill this work never touched.
- **`novel-export` is untested and its input just changed.** It reads
  `display_label` for `NOVEL-GENRE`; that is now a deduplicating function.
  Export has also never run under any non-fantasy pack.
- **Modifier stacking is only checked pairwise.** Three modifiers put four
  contracts against one book, and `conflicts_with` compares packs two at a
  time. Nothing catches a triple that is jointly unsatisfiable while every
  pair is individually fine.
- **No changelog.** The README tells users to want `0.3.0` and fifteen
  packs; nothing tells them what updating gets them.
- **Packs require a framework the judge never receives.** Eleven of twelve
  genre packs demand "three sliders with justification" in Cast
  Requirements. The sliders are defined only in `shared/craft/CRAFT.md`,
  which `novel-foundation` lists as required reading for *itself* (step 3)
  but does not include in the judge dispatch — the judge gets
  `foundation.md`, the packs, and the project directory. So the judge is
  asked to verify a framework it was never given, and will guess, skip, or
  invent criteria. Fix by inlining the axes into the packs, adding CRAFT.md
  to the dispatch, or dropping the requirement. Surfaced by a shakedown
  author who hit it while writing against the pack.
- **`outline_completeness` assumes act structure that five packs do not
  use.** `rubrics/foundation.md:146` scores "5+ only if act structure
  exists" and `templates/outline.md` scaffolds `## Act 1`. But `romance`,
  `paranormal-romance`, `dark-romance`, `romantasy`, and
  `romantic-suspense` run on Romancing the Beat's four Parts or a braided
  threat/relationship ladder. A literal judge caps a correctly structured
  romance outline at 4 on a base dimension. A third of the pack set is
  exposed.
- **Interaction dimensions and their Genre Contract promises are the same
  test at two severities, with no stated boundary.** Two shakedown authors
  reported this independently about different packs —
  `supernatural_indispensability` against paranormal romance's
  load-bearing promise, and `redemption_cost` against dark romance's
  earned-ending promise. Each pack says to score on degree and not
  double-count, but none says where graded shortfall ends and total failure
  begins. The consequence is not cosmetic: a contract breach caps
  `overall_score` at 6, so two judges can differ by several points on
  identical evidence. This applies to the `fantasy` fix in `b1265d2` as
  well, which added a no-double-count note without a boundary — so it is
  systemic and includes the remedy TEMPLATE currently recommends.

## Open decisions

Questions to answer, not work to schedule.

- **Should `general` be usable as a secondary?** It is `["primary"]` alone
  while every other genre pack is `["primary", "secondary"]`, so literary
  fiction with a mystery thread cannot be expressed. Possibly deliberate —
  a genre-neutral pack contributes little as an overlay — but the asymmetry
  is currently undocumented either way.

## Known gaps

- **No book has been drafted end to end under any non-fantasy pack.**
  `clean-bill` cleared foundation under general fiction and stopped. This is
  the largest untested surface in the project.
- **`clean-bill` carries 5 open craft debts** in its `canon.md`. Project
  work, not repo work, but it is the only non-fantasy project that exists.
- **Shape arithmetic is loose.** Several packs' `chapters × chapter_words`
  only partially intersects their declared `words` — `mystery` spans
  70,400–83,200 against 80,000–95,000. Becomes unrepresentable once the form
  axis makes `chapters` derived, so it is deliberately not being fixed
  first.

## Not doing

Recorded so they are not re-litigated.

- **Screenplay, teleplay, graphic novel script, poetry, interactive,
  nonfiction.** Different output medium, different craft rubric, different
  notion of voice. `voice.md` and `CRAFT.md` assume prose. A sibling
  product, not a form.
- **Packs for sports, mafia, military, western, billionaire, and the rest of
  romance.io's occupational tags.** These are premise, not genre. They have
  no beat conflict and no interaction dimension worth scoring; "is the job
  real or wallpaper" is already `setting_specificity`.
- **A `novelette` form.** An awards bucket with no market behind it, sharing
  the intermediate band with `novella` anyway.
- **A pack per hybrid.** Compose unless you can name a dimension that scores
  the *interaction*. Cozy mystery, erotic paranormal romance, and sci-fi
  romance are all correctly composed today.
- **Retiring the `autoanthology` repo** before `collection` ships and is
  verified end to end.
