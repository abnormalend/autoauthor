# Roadmap

**Future work only.** Detail lives in `docs/superpowers/specs/` (design) and
`docs/superpowers/plans/` (execution); this file is the index above them and
the home for work not yet worth a spec.

Nothing that has landed belongs here. Shipped history is in
[CHANGELOG.md](CHANGELOG.md), including the dated entries with no version
number — work that changed nothing installable, which is most of the
verification this project runs on.

**This repo only.** Work belonging to another repository does not go here
even when it depends on something this one ships; that repository can track
its own.

Last updated 2026-08-15.

---

## In flight

Nothing. The form and structure axes are both complete and both reachable
end to end in code. The one phase of the original spec never built is
`serial`, which the spec itself said to ship last or drop; it is in the
parking lot with the reason.

**The largest risk in this project is no longer missing features.** It is
that a great deal of machinery has shipped that no book has run through —
see Known gaps. Every release from 0.5.0 to 0.12.0 was verified by tests
and by reading, and not one of them by a finished work.

That has partly changed. `small-hours` took a collection's first work from
seed through foundation, drafting, two revision cycles and review, and every
release from 0.13.1 to 0.15.0 exists because that run found something a test
could not. Fourteen clean-room judges have since confirmed that caps bind.
What remains unrun is the back half at scale: no container has been through
the cross-work pass, `assemble.py` has bound nothing but a check, and no book
has been drafted end to end under any non-fantasy pack.

## Next — specced, ready to plan

One item. [The form spec](docs/superpowers/specs/2026-08-13-form-parameterization-design.md)
that filled this section is delivered through phase 6; its phase 7 is in the
parking lot.

- **Run something through it.** The highest-value work in this file, and
  the only item that cannot be done by reading. Seed a small collection —
  three short stories, one genre — and take it to export. Every part of
  that path now exists and none of it has been exercised together: no
  container has run the cross-work pass, and `assemble.py` has bound
  nothing but a `--check`.

## Later — identified, not specced

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
- **Urban fantasy's masquerade.** Composes adequately as `fantasy` +
  `mystery` secondary, but nothing scores why the ordinary world does not
  know.
- **LitRPG / progression fantasy.** Runs on a power-milestone cadence rather
  than Save the Cat, so it has a genuine beat conflict — the strongest
  remaining candidate for a pack by the interaction test.

## Parking lot — not soon, not forgotten

**No decision has been made about these.** They are not scheduled and not
rejected; the moment for them has not come. Each entry states what would
bring it back, because a parking lot without that is a graveyard with better
manners.

Contrast **Not doing**, which is the opposite state: a decision was made, and
the entry exists so it is not made again.

- **`epic` form.** Blocked on craft, not on plumbing. The form axis would
  take it tomorrow — a band, a gate, a layer list — but `epic` is not a
  longer `novel`, it is multi-POV with braided subplots, and neither exists
  as a scored dimension anywhere in the repo. Adding the form before the
  dimensions would ship a length with nothing to judge it by.
  **Returns when** multi-POV and subplot braiding are real dimensions.
  Watch: `romantasy` already declares 110,000–140,000 against a novel band
  that stops at 120,000, which is the strongest live argument that `epic`
  is a real form rather than a wider `novel`.

- **`structure: serial`.** Phase 7 of the form spec, which said to ship it
  last or drop it. One work released in parts, and the only structure that
  breaks the score-plateau model the whole pipeline rests on: a serial
  cannot revise to a plateau, because earlier parts are published and
  unrevisable while later ones are still being drafted. That is not an
  implementation difficulty, it is a different quality model.
  **Returns when** there is a reason to want it that is worth designing a
  second quality model for. No user has asked.

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

**Decisions already made**, recorded so they are not argued again. Several
carry the condition that would reopen them, which is part of the record
rather than a hedge — the point is that the thinking was done once and does
not need redoing.

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
- **A `flash` form.** Below the useful floor of a five-phase pipeline: five
  phases cost more than a thousand-word story is worth. This is already the
  shipped position rather than a new one — `short-story` refuses under 1,000
  words on the SFWA boundary, and says so in the pack. Reopen only if a
  two-phase path (seed → draft, no foundation loop) is built for its own
  reasons, in which case flash is its first user rather than its
  justification.
- **A pack per hybrid.** Compose unless you can name a dimension that scores
  the *interaction*. Cozy mystery, erotic paranormal romance, and sci-fi
  romance are all correctly composed today.
- **Restoring the standalone art/cover tools.** Removed in 0.4.1. If cover
  art is wanted later, write it fresh against the current project layout
  rather than recovering code that was written for one specific book and
  never tested.
