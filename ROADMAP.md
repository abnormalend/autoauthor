# Roadmap

Direction and open work. Detail lives in `docs/superpowers/specs/` (design)
and `docs/superpowers/plans/` (execution); this file is the index above them
and the home for work not yet worth a spec.

Last updated 2026-08-13. Shipped history is in [CHANGELOG.md](CHANGELOG.md).

---

## In flight

Nothing. Phases 0 through 6 have landed. What remains of the original spec
is `serial`, which the spec itself said to ship last or drop — plus the
verification debts below, which are now the larger risk: a great deal of
machinery has shipped that no book has run through.

## Recently landed

- **`structure: series`**, 0.11.0, 2026-08-13. Phase 6, and the same
  machine as a collection pointed the opposite way — continuity and arc
  where a collection checks variety and independence. `series-pass.md`
  with seven dimensions, a series skill, and `bible/canon.md` plus
  `bible/arc.md` required because they are what the pass reads.
  `convergence.py` now states which reading applies rather than leaving a
  reader of the JSON to invert it, and its outlier detection uses a
  modified z-score after the ordinary one turned out to be arithmetically
  incapable of firing at the sizes a series has.

- **`structure: collection`**, 0.10.0, 2026-08-13. Phase 5, and the first
  of the structure axis. A container project with a shared bible, a
  declared running order, and `works/` beneath it; children inherit genre
  and form downward, which inverts the pack precedent on purpose.
  `convergence.py` and `rubrics/collection-pass.md` port autoanthology's
  real contribution — the pass that sees every work at once — along with
  the correction its first run produced, that scale metrics converge
  because the form set one target and are not evidence about voice.

- **Length coverage for the whole pack set**, 0.9.0, 2026-08-13. Phase 4.
  Compressed sections for `thriller`, `romance` and `erotica`; an
  intermediate section for `romance` that rewrites criteria without
  dropping any dimension; an intermediate-only section for
  `paranormal-romance`, the first pack to support a middle length and not
  a short one. `dark-romance`, `romantasy` and `romantic-suspense` stay
  novel-only with the reasoning written into each pack, and a test
  requires that explanation to exist.

- **`short-story` and `novella`**, 0.8.0, 2026-08-13. Phase 3, and the
  first phase that changes what the pipeline produces. Length bands on
  genre packs, band arithmetic checked per band and across the full genre ×
  form matrix, and the shape migration phase 1 deferred: `shape.words` is
  band-keyed and `shape.chapters` is derived. Four packs ship compressed
  sections; the rest are refused below novel length rather than judged on
  criteria written for eighty thousand words.

- **Base dimension parameterization**, 0.7.0, 2026-08-13. Phase 2, and the
  largest of them. The eight base dimensions moved out of `foundation.md`
  into `shared/rubrics/base-dimensions.md`, in the same bullet form the
  pillar dimensions use, and a form now selects which apply. No scoring
  change for a novel. It also fixed `outline_completeness`, which demanded
  act structure that five of the fifteen packs do not use — a defect that
  capped a correctly built romance outline at 4 on a base dimension.

- **Form pack type**, 0.6.0, 2026-08-13. Phase 1. `shared/forms/`, the
  form schema and its validator, and a resolver that returns a `form`
  block the foundation skill now reads its gate from. Only `novel` ships,
  with today's values, and the acceptance test asserts each of them —
  nothing moved. Two cross-pack checks landed with it, both invisible to
  either pack alone: a genre whose length cannot fit the form, and a form
  that gates above what the genre's caps can reach.

- **Structured caps and the gate solver**, 0.5.0, 2026-08-13. Phase 0 of
  the form work. `[cap N]` on fifty-five dimensions across eleven packs,
  `gate_solver.py` computing the highest gate a design supports, and a
  validator that rejects a pack whose gate its own caps put out of reach.
  It earned itself on the first run: `general` — the pack every project
  without a genre falls back to — shipped with a ceiling of 6.4 against a
  7.0 gate. Caps also stopped being advisory, fixed in one sentence at the
  rubric layer as planned rather than pack by pack.

- **Pruned the last upstream code**, 0.4.1, 2026-08-13. The standalone art,
  cover, audiobook and landing-page tools are gone — never called, never
  tested, each hardcoding the first book's title, byline or cast as a
  default (upstream #7 and #9). Everything shipping is now original, the
  repo has no runtime dependencies, and the De-Bells rule is an executable
  test rather than a docstring.

- **CI**, 2026-08-13. `.github/workflows/ci.yml` runs the suite and the pack
  validator CLI on every push and PR. The consistency checks live in
  `tests/test_plugin_manifest.py` rather than in YAML, so they run locally
  too — version agreement across the three plugin strings, and skill
  frontmatter matching its directory, which is the defect 0.4.0 shipped and
  a human caught. Both mutation-tested.

- **Rename to `autoauthor`**, 0.4.0, 2026-08-13. Was phase 4 of the form
  work; shipped ahead of phases 0–3 so that everything they create is born
  correctly named. Breaking — requires reinstall, not update. The dated
  design record under `docs/superpowers/` keeps the old names deliberately.

- **Pack shakedown**, 2026-08-13 —
  [result](docs/superpowers/2026-08-13-pack-shakedown-result.md). Four
  planted-defect planning sets, four clean-room judges. One pack caught its
  plant cleanly and blocked the book; two had gaps, since fixed and verified
  in 0.3.1; one was inconclusive because its author out-wrote their own
  plant. It also produced the artifact design rule now used for new packs —
  *an artifact bites when it directly encodes the dimension's test* — and
  surfaced most of the Engineering section below.

## Next — specced, ready to plan

All from [the form spec](docs/superpowers/specs/2026-08-13-form-parameterization-design.md),
in its phase order. Phases 0–2 are behaviour-preserving and A/B-verifiable
the way the fantasy port was.

- **Containers are not yet reachable from `seed` or `export`.** Both
  structures resolve, validate and can be passed, and neither can be
  CREATED or SHIPPED: `seed` builds a standalone project only, and
  `export` assembles one work. Those two gaps are what stand between "a
  collection resolves" and "a collection is a book", and they are now the
  highest-value work in the file.
- **Verify a collection end to end**, then retire `autoanthology`.
  Nothing has run through the container machinery — no collection or
  series has been seeded, drafted, or passed.
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
- **Verify that caps now bind.** 0.5.0 declared them as data and told the
  rubric a met cap is applied rather than weighed, but the defect was
  found by observing two judges, and only a judge can show it is gone.
  Re-run the two shakedown sets whose structure produced the split —
  three dimension tests pass, one fails, criteria say "score 6 max" — and
  check that both now cap. Cheap, and it closes the loop on the deepest
  finding the shakedown produced.
- **`fantasy` caps only two of its five dimensions.** Visible for the first
  time now that the solver prints the cap list per pack: every other
  primary caps all or nearly all of its dimensions, while `magic_system`,
  `world_history` and `geography_and_culture` state failure modes and
  attach no ceiling to any of them ("decorative history counts against the
  score, not for it" is a deduction of unstated size). Not a calibration
  bug — the arithmetic is fine and the headroom is real — but it means
  three of the oldest pack's five dimensions rest entirely on judge
  discretion, which is the variance the shakedown measured at ±1.
- **Rename `resolve_genre.py` to `resolve_packs.py`.** It resolves a form
  now as well as a genre stack, so the name is wrong on the tin. Cosmetic,
  touches nine skill files, and deliberately not bundled into a phase that
  had to prove it changed nothing.
- **`romantasy` straddles the novel/epic boundary.** It declares
  110,000–140,000 against a novel band that stops at 120,000. Not an error
  — the form check is overlap rather than containment precisely so a genre
  may sit at the top of its form — but it is the strongest argument yet
  for `epic` being a real form rather than a wider `novel`.
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

- **Nothing tests the rubric → JSON contract.** Every test is structural:
  parse, validate, resolve. Rubrics are prompts, and the verdict schema six
  skills parse is verified by nobody. This has already bitten once —
  `gen_brief.py` read `lore_integration` and `world_consistency` through
  `.get()` after they were renamed, silently dropping feedback from every
  revision brief, covered by no plan task and no test. A fixture verdict per
  rubric, asserting the keys the skills actually read, needs no live judge.
- **`import` has never been exercised.** It infers a genre from a
  finished manuscript and writes it into `state.json` — now across fifteen
  packs rather than nine, including distinctions that are genuinely fine
  (paranormal romance vs romantasy). The one skill this work never touched.
- **`export` is untested and its input just changed.** It reads
  `display_label` for `NOVEL-GENRE`; that is now a deduplicating function.
  Export has also never run under any non-fantasy pack.
- **Modifier stacking is only checked pairwise.** Three modifiers put four
  contracts against one book, and `conflicts_with` compares packs two at a
  time. Nothing catches a triple that is jointly unsatisfiable while every
  pair is individually fine.
- **Shakedown slice 2 — chapter, drafting, reader panel.** The 2026-08-13
  run covered foundation only. `drafting-rules.md`, `chapter.md` and
  `reader-panel.md` all read genre packs and none has been exercised. Use
  the same planted-defect method; it worked.
- **Judge variance is unmeasured and it constrains everything above.**
  Re-judging an unchanged planting set moved four dimensions and lifted
  `overall_score` by 0.36. Single-dimension deltas are noise, which is why
  both 0.3.1 fixes were accepted on the judge *naming the new test* rather
  than on a score moving. Any rubric-fixture test must pin keys and schema,
  never values, or it encodes the noise.
- **Packs require a framework the judge never receives.** Eleven of twelve
  genre packs demand "three sliders with justification" in Cast
  Requirements. The sliders are defined only in `shared/craft/CRAFT.md`,
  which `foundation` lists as required reading for *itself* (step 3)
  but does not include in the judge dispatch — the judge gets
  `foundation.md`, the packs, and the project directory. So the judge is
  asked to verify a framework it was never given, and will guess, skip, or
  invent criteria. Fix by inlining the axes into the packs, adding CRAFT.md
  to the dispatch, or dropping the requirement. Surfaced by a shakedown
  author who hit it while writing against the pack.
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
- **Restoring the standalone art/cover tools.** Removed in 0.4.1. If cover
  art is wanted later, write it fresh against the current project layout
  rather than recovering code that was written for one specific book and
  never tested.
