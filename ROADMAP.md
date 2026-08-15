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

**The largest risk in this project is no longer missing features, and it is
no longer that nothing has been run.** One work has now been through the
whole per-work pipeline — `small-hours/01-porter`, under `mystery` +
`short-story`, seed to a PDF and an ePub — and every release from 0.13.1 to
0.15.0 exists because that run found something a test could not. Fourteen
clean-room judges have since confirmed that caps bind.

The risk now is **narrow coverage read as broad coverage**. That run was one
pack, one form, four chapters, one work. 0.17.1 is the cautionary case:
`export` ran against a real book, emitted four correct drop caps, and still
left the dialogue branch cold, where it had been producing a backtick for a
capital since before the rename.

So the honest statement of what is unrun is now specific rather than
sweeping, and it lives in Engineering: no container has run the cross-work
pass, `assemble.py` has bound nothing but a `--check`, `series` and `import`
have never executed at all, and four of five genre artifacts have never been
produced.

## Next — specced, ready to plan

One item. [The form spec](docs/superpowers/specs/2026-08-13-form-parameterization-design.md)
that filled this section is delivered through phase 6; its phase 7 is in the
parking lot.

- **Finish `small-hours`.** The highest-value work in this file, the only
  item that cannot be done by reading, and now much cheaper than it was:
  the collection exists and is one-third built. `01-porter` went seed →
  foundation → draft → revise → review → export and produced a PDF and an
  ePub on 2026-08-14. What is still cold is everything that needs a
  *second* work:

  - the collection cross-work pass — the container is still at phase
    `foundation` and its `results.tsv` has only a header, so
    `convergence.py` and `collection-pass.md` have never seen real works
  - `assemble.py` binding — no `assembled/` exists; it has only ever run
    `--check`
  - export against a *container* rather than a child

  Two more short stories under the same mystery pack gets all three. The
  variety check is meaningless at n=1 and marginal at n=2, so three is the
  floor for the pass to say anything.

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
- **A `horror` pack.** A top-level Goodreads genre with no pack at all, and
  the largest gap in the set by readership. Passes the interaction test on
  its face — dread is a pacing contract and a withholding discipline, not a
  premise — but nobody has written the dimensions that would score it.
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

## Engineering — ordered by what has already cost something

Coverage here is now measurable rather than assumed: one real book has been
through seed → foundation → draft → revise → review → export. What that run
did *not* touch is what this section is for, and 0.17.1 is the warning about
reading it too generously — `export` ran, emitted four correct drop caps, and
still left a common branch cold.

**Has already bitten.**

- **Nothing tests the rubric → JSON contract.** Every test is structural:
  parse, validate, resolve. Rubrics are prompts, and the verdict schema six
  skills parse is verified by nobody. It has bitten once already —
  `gen_brief.py` read `lore_integration` and `world_consistency` through
  `.get()` after they were renamed, silently dropping feedback from every
  revision brief, covered by no plan task and no test. A fixture verdict per
  rubric, asserting the keys the skills actually read, needs no live judge
  and is the cheapest real coverage left in the repo. **Do this first.**
- **Packs require a framework the judge never receives.** Eleven of twelve
  genre packs demand "three sliders with justification" in Cast
  Requirements. The sliders are defined only in `shared/craft/CRAFT.md`,
  which `foundation` lists as required reading for *itself* but does not
  include in the judge dispatch — the judge gets `foundation.md`, the packs,
  and the project directory. So it is asked to verify a framework it was
  never given, and will guess, skip, or invent criteria. Fix by inlining the
  axes into the packs, adding CRAFT.md to the dispatch, or dropping the
  requirement. Found by a shakedown author writing against the pack.
- **Interaction dimensions and their Genre Contract promises are the same
  test at two severities, with no stated boundary.** Two shakedown authors
  reported this independently about different packs. Each pack says to score
  on degree and not double-count; none says where graded shortfall ends and
  total failure begins. Not cosmetic — a contract breach caps
  `overall_score` at 6, so two judges can differ by several points on
  identical evidence. Systemic, and it includes the remedy TEMPLATE
  currently recommends.

**Untouched by any live run.**

- **`import` has never been exercised.** It infers a genre from a finished
  manuscript and writes it into `state.json` — across fifteen packs, with
  distinctions that are genuinely fine (paranormal romance vs romantasy).
  The one skill no work in this repo has ever run.
- **`series` has never been exercised.** The whole structure: no volume, no
  container, no continuity pass. `collection` is about to get its first real
  run; its opposite twin has had none, and the two invert rather than share
  behaviour, so the collection run will not cover it.
- **Four of five genre artifacts have never been produced.** `clue_ledger.md`
  now exists, written by the live mystery run. `braid.md`, `braid_map.md`,
  `power_ledger.md` and `encounter_ledger.md` are declared by packs and have
  never been generated by anything but a fixture author.

**Known to be narrow rather than untested.**

- **`export` has run once**, under `mystery` + `short-story`, as a child of a
  container, four chapters. Untried: any other pack, a standalone project, a
  bound container, and — until 0.17.1 — a chapter opening on dialogue. Treat
  "export works" as "export worked on that shape".
- **Shakedown slice 2 — chapter, drafting, reader panel.** The 2026-08-13 run
  covered foundation only. `drafting-rules.md`, `chapter.md` and
  `reader-panel.md` all read genre packs, and while the live run exercised
  them for real, nothing has tested whether they *catch a planted defect*.
  Use the same method; it worked, and it is now cheap because the fixtures
  are committed.
- **Modifier stacking is only checked pairwise.** Three modifiers put four
  contracts against one book, and `conflicts_with` compares packs two at a
  time. Nothing catches a triple that is jointly unsatisfiable while every
  pair is individually fine.

**Constrains how everything above is tested.**

- **Judge variance is unmeasured.** Re-judging an unchanged planting set
  moved four dimensions and lifted `overall_score` by 0.36. Single-dimension
  deltas are noise, which is why both 0.3.1 fixes were accepted on the judge
  *naming the new test* rather than on a score moving, and why the
  fourteen-judge caps result was read as a rate rather than a mean. Any
  rubric-fixture test must pin keys and schema, never values, or it encodes
  the noise.

## Open decisions

Questions to answer, not work to schedule.

- **Should `general` be usable as a secondary?** It is `["primary"]` alone
  while every other genre pack is `["primary", "secondary"]`, so literary
  fiction with a mystery thread cannot be expressed. Possibly deliberate —
  a genre-neutral pack contributes little as an overlay — but the asymmetry
  is currently undocumented either way.

## Known gaps

- **One pack, one form, one work.** `small-hours/01-porter` is the entire
  body of evidence that the per-work pipeline works: `mystery` at
  `short-story` length, four chapters, as a child of a container. Thirteen
  other primaries, two other forms and the standalone structure have cleared
  tests and nothing else. This is not "untested" — it is a single sample
  being asked to speak for a matrix, and the failure it will produce looks
  like 0.17.1: a real run, a correct-looking artifact, and a cold branch.
- **No long-form work has been drafted.** Every chapter this repo has
  produced is short-story length. `novel` and `novella` set different gates,
  different layer lists and a different chapter budget, and the drafting loop
  at 46 chapters has never been exercised at all — the freshness decay the
  base rules fight after chapter 6 has never actually been tested past four.

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
