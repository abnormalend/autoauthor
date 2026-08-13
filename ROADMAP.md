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
