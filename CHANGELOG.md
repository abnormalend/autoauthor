# Changelog

Versions are the plugin's, declared in `plugin/autonovel/.claude-plugin/plugin.json`
and mirrored in `.claude-plugin/marketplace.json`. Updating the marketplace
is not the same as updating the plugin — see [README](README.md#install).

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
- Genre selection moved into `novel-seed` step 2, before the project
  directory exists, closing a window where an interrupted run could build an
  entire book as general fiction silently.
- The marketplace manifest moved to the repo root, which is where
  git-sourced marketplaces look for it.

**Migration:** projects created before 0.2.0 have no `genre` field. Running
`/autonovel:novel` inside one detects this, explains that existing scores
came from the fantasy rubric, and migrates on confirmation.

---

## 0.1.0 — 2026-08-05

Initial release. The original Python pipeline rebuilt as a Claude Code
plugin.

**Added**

- Eight skills: `novel` (status and routing), `novel-seed`,
  `novel-import`, `novel-foundation`, `novel-draft`, `novel-revise`,
  `novel-review`, `novel-export`.
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
