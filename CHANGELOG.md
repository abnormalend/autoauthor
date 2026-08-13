# Changelog

Versions are the plugin's, declared in `plugin/autoauthor/.claude-plugin/plugin.json`
and mirrored in `.claude-plugin/marketplace.json`. Updating the marketplace
is not the same as updating the plugin — see [README](README.md#install).

---

## 0.5.0 — 2026-08-13

Phase 0 of the form work. Score caps stop being prose and become data the
machine checks, which makes two things possible that were not: computing a
pack's gate instead of guessing it, and telling a judge that a cap binds.

Scoring behaviour changes for **general fiction** projects (a fifth pillar
dimension, and three caps raised from 5 to 6) and, in principle, for every
genre — a judge that previously weighed a met cap against a dimension's
other tests must now apply it. No schema or state changes; existing
projects need no migration.

**Added**

- `[cap N]` on a pillar dimension bullet: `- lore_interconnection [cap 6] —
  ...`. The value is the lowest tier the dimension's criteria can force.
  Fifty-five dimensions across eleven packs now declare one.
- `shared/scripts/gate_solver.py`. Given a dimension count and its caps it
  computes what the uncapped dimensions must average when the *k* lowest
  caps co-fire, and the highest gate the design can support. TEMPLATE has
  stated that policy in prose since the genre work and asked authors to
  check it by hand; this inverts it.
- The validator now rejects a primary pack whose own caps put the
  pipeline's 7.0 pillar gate out of reach — no book can be finished under
  such a pack however good it is. It also fails a `[cap N]` that disagrees
  with what the criteria say in words, since the judge reads one and the
  arithmetic reads the other.
- CI prints the gate ceiling for every shipped pack.

**Fixed**

- **`general` shipped unreachable.** Four dimensions with three caps at 5:
  two caps firing demanded 9.50 from the remaining two, and its highest
  legal gate was 6.4 against a pipeline gating at 7.0. Found by the solver
  on its first run, which is the argument for having built it. Fixed by
  TEMPLATE's own remedy — dimension count is the lever — with a fifth
  dimension, `cultural_particularity`, scoring the one World Section the
  pack demanded and never graded. The three 5-caps become 6s, which the
  arithmetic then forces and which also brings the pack in line with every
  other one in the set, where 6 is the severest ordinary cap.
- **Caps were advisory.** The 0.3.1 shakedown proved two judges meeting
  the same structure — three tests pass, one fails, criteria say "score 6
  max" — where one capped and one scored 8 because "every other test
  passes strongly". `rubrics/foundation.md` now states that a met cap is
  applied and not weighed, and says why: the criteria already decided what
  the other tests are worth by capping in spite of them. Fixed once at the
  rubric layer rather than pack by pack.

---

## 0.4.1 — 2026-08-13

No change to the plugin. This removes the last upstream-derived code from
the repository around it.

**Removed**

- `gen_art.py`, `gen_art_directions.py`, `gen_cover_composite.py`,
  `gen_cover_print.py` — the standalone image tools.
- `gen_audiobook.py`, `gen_audiobook_script.py`, `audiobook_voices.json`,
  `landing/` — removed just before this, for the same reason.
- `.env.example`, and both runtime dependencies (`httpx`, `python-dotenv`),
  which existed only for those tools.

None of them was ever called by the pipeline, covered by a test, or shipped
in the plugin. Each hardcoded the first book's title, byline or cast as a
**default** rather than as an example — an upstream defect
([#7](https://github.com/NousResearch/autonovel/issues/7),
[#9](https://github.com/NousResearch/autonovel/issues/9)) that had survived
into this tree because the genre-leak scrub was scoped to the plugin and
these sat outside it. They also carried upstream
[#5](https://github.com/NousResearch/autonovel/issues/5), fixed `max_tokens`
that breaks against a thinking model.

**Consequences**

- Everything that ships is now original to this project, which is the
  cleanest position for eventually going public while upstream's licensing
  is unresolved. The remaining debt is architectural — `PIPELINE.md` is
  upstream's own document, kept deliberately as the record of what this
  descends from.
- The repo has **no runtime dependencies**. The plugin's scripts were
  already stdlib-only by design, since they run inside Claude Code on
  whatever Python is present and a third-party import would fail silently
  on someone else's machine. `pyproject.toml` now says so.
- No API keys are needed for anything in this repository.

**Added**

- The De-Bells rule is finally executable. `tests/test_no_genre_leak.py` has
  described itself as that rule's successor since it was written while
  checking only for genre furniture — the content it was named after was
  never guarded. It now scans the whole repo rather than the plugin-scoped
  directories, because the leak's last hiding place was exactly the tooling
  those directories do not cover.

---

## 0.4.0 — 2026-08-13

**Renamed from autonovel to autoauthor.** Breaking: you must **reinstall**,
not update, because the marketplace id changed.

```bash
/plugin marketplace add abnormalend/autoauthor
```
```bash
/plugin install autoauthor@autoauthor-dev
```

The old plugin can be removed once the new one resolves. Existing novel
projects keep working — see Migration below.

**Why now.** The product is growing past novels: short stories, novellas,
collections and series are all specced. "autonovel" was already wrong on the
tin, and every skill named `novel-*` misdescribed itself. The rename was
scheduled as phase 4 of the form work and moved ahead of phases 0–3 because
everything those phases create — structured caps across fifteen packs, the
form pack type, band sections on every genre pack — would otherwise have
been born under the old name and needed rewriting afterward.

**Changed**

- Plugin `autonovel` → `autoauthor`; marketplace `autonovel-dev` →
  `autoauthor-dev`; plugin directory `plugin/autonovel/` →
  `plugin/autoauthor/`.
- All eight skills drop the redundant `novel-` prefix, and the router is
  named for what it does:

  | before | after |
  |---|---|
  | `/autonovel:novel` | `/autoauthor:status` |
  | `/autonovel:novel-seed` | `/autoauthor:seed` |
  | `/autonovel:novel-import` | `/autoauthor:import` |
  | `/autonovel:novel-foundation` | `/autoauthor:foundation` |
  | `/autonovel:novel-draft` | `/autoauthor:draft` |
  | `/autonovel:novel-revise` | `/autoauthor:revise` |
  | `/autonovel:novel-review` | `/autoauthor:review` |
  | `/autonovel:novel-export` | `/autoauthor:export` |

- `state.json`: `novel_score` → `work_score`.

**Migration.** One key. Run `/autoauthor:status` inside any existing
project — it detects a `novel_score` key, renames it to `work_score`, and
tells you what changed without committing. This check is independent of the
0.2.0 genre migration and fires on its own, since a 0.3.x project already
has a `genre` and still carries the old key. Nothing else in a project
directory carries the old name: chapters, `results.tsv`, `canon.md`,
`outline.md` and the rest are all name-agnostic.

**Not changed.** The dated design record under `docs/superpowers/` was
deliberately left under the old names, for the same reason `PIPELINE.md`
still records `lore_score` — a design document edited to match later
decisions stops being evidence of what was decided. See
[docs/superpowers/README.md](docs/superpowers/README.md) for a translation
table.

**Attribution.** The README now credits the upstream project this began
from — autonovel by emozilla / Jeffrey Quesnelle at Nous Research — and
records the licensing position. Note that "autonovel" continues to refer to
*their* project throughout; this rename does not reach it.

---

## 0.3.1 — 2026-08-13

Two pack-criteria fixes, both confirmed by a planted-defect run against the
new packs and then verified by re-judging. Scoring behaviour changes for
dark romance and romantasy projects; no schema or state changes, so existing
projects need no migration.

**Fixed**

- `dark-romance` / `redemption_cost` now totals the ledger in **both**
  directions. Its three previous tests asked what the darker lead lost and
  never whether losses exceed gains, so a book could retire one arrangement
  and then be handed immunity, a replacement contract and a promotion while
  answering every stated test truthfully. The new fourth test caps at 6 when
  net position at the end is equal to or better than at the start, and names
  the two disguises the run exposed: a windfall arriving on someone else's
  timetable, and a surrendered role that is in substance a promotion.
- `romantasy` / `magic_barrier_dependency`'s deletion test now runs as a
  **redenomination**. Deleting the magic from a barrier *priced* in magic
  destroys its unit of account and makes any such barrier look
  magic-dependent — so a debt-settlement betrothal passed a test designed to
  catch exactly that. The test now reprices the obligation in grain, coin or
  land and asks whether the enforcer still enforces. The distinction is
  stated plainly: the question is not whether the obstacle is written in the
  magic's terms, it is whether the magic is what makes it binding.

Neither pack changed dimension count or cap values, so calibration holds at
7.40 / 7.75 / 8.33 for one, two and three caps firing.

**Known, unfixed:** dimension caps are advisory. Two judges met the same
structure — three tests pass, one fails, criteria say "score 6 max" — and
one capped while the other averaged. Every cap in every pack is currently a
suggestion. This is a rubric-layer defect and is deliberately not being
patched pack by pack; see [ROADMAP](ROADMAP.md).

---

## 0.3.0 — 2026-08-13

Six new genre packs, taking the shipped set from nine to fifteen, plus five
fixes to packs the new ones surfaced. Requires a plugin update, not just a
marketplace refresh.

**Added**

- Four primary packs — `paranormal-romance`, `romantasy`,
  `romantic-suspense`, `dark-romance` — admitted only where composing
  existing packs is *wrong* rather than merely thin. A secondary pack
  contributes its dimensions and contract but never its `beat_system`,
  `shape` or `weights`, so `fantasy` + `romance` outlines on Save the Cat
  and never places a romance beat; and unioning two packs' dimensions
  dilutes the pillar gate until caps stop biting.
- Two modifiers — `historical` and `inspirational` — because period and
  faith are orthogonal axes. `inspirational` sets `violence: moderate`
  rather than cozy's `off-page`, so inspirational suspense stays writable.
- Three new per-book artifacts: `braid.md`, `braid_map.md`,
  `power_ledger.md`.

Erotic paranormal romance needs no pack of its own — it is
`paranormal-romance` plus the `erotica` modifier, which is what the modifier
role exists for.

**Fixed**

- `pillar_score` no longer dilutes when a secondary loads. The gate now
  averages the **primary's** dimensions alone; the secondary's still reach
  `overall_score` through the pillar weight. Every pack's authored cap
  arithmetic was wrong whenever a secondary was loaded.
- `fantasy` was out of calibration by TEMPLATE's own rejection rule — two
  4-caps meant two firing required a 9. The severest case moved to the Genre
  Contract, where a breach caps `overall_score` at 6 without touching
  `pillar_score`.
- `cozy` capped its own exemplars: Louise Penny and M.C. Beaton sat in its
  comps while its contract made professional standing a breach.
- `romance`'s pillar preamble was unscoped for its secondary role, telling
  judges to score a fantasy novel as though its main plot were subordinate
  to its romance.
- `display_label` no longer renders "Paranormal Romance Romance" on export
  title pages.
- `ya`'s register promise now yields explicitly to a lower clamp, so YA
  inspirational is writable.

---

## 0.2.0 — 2026-08-12

Genre parameterization. The pipeline stopped assuming every book is a
fantasy novel.

**Added**

- The genre pack system: single markdown files with JSON frontmatter
  declaring `role`, `weights`, `pillar_label`, `beat_system`, `shape`,
  `content_register`, `conflicts_with` and `artifacts`, plus prose sections
  a judge reads directly. Nine packs shipped — `general`, `fantasy`,
  `science-fiction`, `mystery`, `thriller`, `romance`, `erotica`, and `ya`
  and `cozy` as modifiers.
- Three roles: `primary` owns the pillar dimensions and book shape,
  `secondary` layers a second genre's concerns additively, `modifier` is an
  orthogonal axis. Packs may declare more than one.
- Genre contracts — binary promises checked at planning time and against the
  finished manuscript. A breach caps `overall_score` at 6 and never touches
  `pillar_score`.
- `content_register`, clamped per axis to the most restrictive level any
  loaded pack declares, with the source reported so an unexpected clamp is
  explicable.
- `resolve_genre.py`, `validate_genre_pack.py`, `genre_pack.py`, a pack
  authoring guide, and a leak guard test keeping genre content out of the
  base machinery.
- Project-level pack override: a pack in a novel's own `genres/` directory
  wins over the plugin's.

**Changed**

- `lore_score` → `pillar_score` throughout; the foundation rubric's output
  schema became nested under `pillar` / `character` / `structure` / `craft`.
- `overall_score` and `pillar_score` are now reported as two-decimal means.
  Integer-only scores could not express any value between 7 and 8 — exactly
  the band the gate sits in.
- Genre selection moved into `seed` step 2, before the project
  directory exists, closing a window where an interrupted run could build an
  entire book as general fiction silently.
- The marketplace manifest moved to the repo root, which is where
  git-sourced marketplaces look for it.

**Migration:** projects created before 0.2.0 have no `genre` field. Running
`/autoauthor:status` inside one detects this, explains that existing scores
came from the fantasy rubric, and migrates on confirmation.

---

## 0.1.0 — 2026-08-05

Initial release. The original Python pipeline rebuilt as a Claude Code
plugin.

**Added**

- Eight skills: `novel` (status and routing), `seed`,
  `import`, `foundation`, `draft`, `revise`,
  `review`, `export`.
- Score-gated phases — each runs a modify → evaluate → keep-or-discard loop
  against a rubric rather than finishing a checklist, and a phase that
  cannot clear its bar keeps working.
- Clean-room LLM judges: each receives only a rubric and the text, with no
  drafting context and no memory of how the text was produced.
- A mechanical slop scanner with no LLM in the loop — banned vocabulary, AI
  fiction clichés, telling-not-showing, sentence-length uniformity, em-dash
  density.
- A four-persona reader panel in the revision phase.
- Per-project git repositories, committed at every kept iteration, so a
  regression costs nothing to discard.
- LaTeX PDF and ePub export.
