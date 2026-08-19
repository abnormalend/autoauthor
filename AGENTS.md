# Working in this repo

For coding agents. What the code cannot tell you by itself, plus the traps
that have actually cost a release. Everything derivable from reading a file
lives in that file's docstring — this document is for facts that span files,
and no single file can own.

## The first thing to understand

**Most of this plugin is markdown that a model reads at runtime.** The
Python under `shared/scripts/` is a thin layer that parses, validates, and
computes; the behaviour lives in the prose.

That inverts the usual rule about editing. A change to
`shared/genres/mystery.md` changes what the plugin does, and no test needs to
fail for that change to be wrong. A change to `gate_solver.py` is ordinary
code with ordinary tests. Treat the markdown under `shared/genres/`,
`shared/forms/`, `shared/rubrics/`, `shared/craft/` and `shared/templates/`
as program text: it is read by a model, in context, as instructions.

A consequence that has bitten: **required reading primes.**
`skills/foundation/SKILL.md` and `skills/draft/SKILL.md` require reading
`ANTI-SLOP.md` *and* every genre pack. In 0.16.0 the packs used a banned
phrase 22 times, so the drafter met it two dozen times in the same context
window as the instruction to kill it on sight. That is not an inconsistency
to tidy up later; it is the ban failing. `test_required_reading_is_clean.py`
guards the narrow version of this.

## Orientation

| File | Owns |
|---|---|
| `genre_pack.py` | pack parsing, `[cap N]`, dimension bullets, band sections |
| `form_pack.py` | the SCALE axis — words, gate, layers, base dimensions |
| `base_dimensions.py` | the character/structure/craft dimensions a form resolves |
| `structure.py` | standalone / collection / series — containers and inheritance |
| `resolve_genre.py` | merging a genre stack, conflicts, what every skill reads |
| `gate_solver.py` | whether a set of caps can actually clear a gate |
| `score_verdict.py` | computing the aggregate instead of trusting the judge |
| `convergence.py` | cross-work variety (collection) and drift (series) |
| `assemble.py` | binding a collection's works into one manuscript |
| `slop_score.py` | the tier lists that can fail a chapter |
| `continuity_check.py` | numbers a chapter states that no fact-bearing document states |
| `splice_audit.py` | paragraph-level damage a mechanical cut leaves behind |

Read the module docstrings. They are long on purpose and they carry the
reasoning, not just the interface.

## Invariants that span files

**Precedence runs in opposite directions, deliberately.** A project's own
copy of a genre or form pack **overrides** the shipped one
(`resolve_genre.py:9`) — that is a user customising their own book. A
container's genre and form **override the child's** (`structure.inherit`),
and a work setting its own is an error the resolver reports — those are what
make N works one book rather than a folder. Same repo, opposite rules, and
each is correct for its own reason. Do not "fix" one to match the other.

**Scale is a pack. Structure is not.** A form changes which dimensions apply,
which is exactly what a pack expresses. A structure changes the state schema
and the phase graph, which no pack can do. This distinction is the reason
`structure` is a `state.json` field.

**Collection and series are the same machine pointed at opposite goals.** A
collection wants variety: works that read alike is the defect, and a low
coefficient of variation is a finding. A series wants continuity: sameness is
the point, and the volume that reads *unlike* its neighbours is the finding.
Anything you add to one cross-work pass probably inverts rather than copies
into the other.

**Caps are applied, not weighed.** `- dimension [cap 6] — ...` means the
score cannot exceed 6 when the condition fires. It is not a hint to score
low. A live judge wrote *"Cap applied, not weighed"* back verbatim, which is
the behaviour to preserve when rewording any dimension.

**Run `gate_solver.py` before adding or changing a cap.** With N dimensions
and a 7.0 pillar gate, the pillar scores must sum to at least 7N+1; every cap
that can co-fire raises what the uncapped dimensions must average to
compensate. This is not intuition-checkable. The solver's first run found
`general.md` — the fallback pack for every project without a genre — shipping
a ceiling of 6.4 against a 7.0 gate, meaning it could never pass.

**Scores are computed, never requested.** Rubrics emit dimension scores;
`score_verdict.py` averages them. Three releases were spent learning this: a
paragraph asking for a decimal was read and ignored (0.13.1), moving the type
into the JSON schema token helped (0.13.2), and removing the judge's
discretion entirely was what actually worked (0.14.0). A judge is qualified
to score a dimension and has no particular claim to averaging seven of them —
one live cycle returned dimensions averaging 7.43 alongside `work_score: 7`,
against a phase that stops when that number moves by less than 0.5.

**Judges score exactly the dimensions handed to them, and nothing else.**
Five of five live runs confirmed it. When a skill dispatches a judge it must
pass `base_dimensions.scored` through **verbatim** — not summarised, and not
replaced with the ones you remember. That substitution is the entire failure
the parameterisation exists to prevent.

**The judge model is part of the instrument.** Every scored dispatch goes to
`agents/judge.md`, which pins one model; the cheaper `editor` and `reader`
agents carry only work that is verified or gated downstream (cuts run through
the protection list and splice audit, panel verdicts are checked against the
prose before anything is briefed). Each skill pins its own orchestrator model
in `SKILL.md` frontmatter. Do not dispatch a judge as `general-purpose`, and
do not change the judge's pinned model without noting it — a project's
`results.tsv` is only comparable with itself if one instrument produced it,
which is why every verdict JSON and results row now carries `judge_model`.
`test_agents.py` guards the shape.

**Dimension keys are a compatibility surface.** A key appears in the
`eval_logs/` and `results.tsv` of every project ever run against it. Renaming
one makes a user's score history incomparable with itself, silently. 0.16.0
banned the phrase `load-bearing` and still left `darkness_load_bearing`
standing in `dark-romance.md` for exactly this reason. Rewrite prose freely;
treat keys as public API.

**`results.tsv` has one score column and it is 0–10.** The `full-eval`
description prefix is a contract the plateau check greps for. See
`test_results_tsv.py` before touching either.

## Guards you will trip

Each is narrow on purpose, and each exemption is **per-file rather than
per-directory**, so that everything sitting beside an exempt file stays
strict.

- **`test_no_genre_leak.py`** — no genre name and no comp author in a base
  file. `ANTI-SLOP.md` and `voice.md` may say `realm` and `tapestry` because
  they are banning them. `skills/status/SKILL.md` may say `fantasy` because
  pre-pack projects really were scored under the fantasy rubric.
- **`test_required_reading_is_clean.py`** — the plugin may not teach the
  drafter a phrase it bans. Scoped to the multi-word Tier 1 phrases and the
  structural formulas: an audit of the full tier lists returned 34 hits of
  which 33 were false positives (`leverage` as a noun, `Catalyst` as a beat
  name), and a guard that cries wolf gets muted.
- **`test_fixture_ledgers.py`** — a shakedown fixture's foreshadowing ledger
  may not cite a chapter that does not carry the plant. Judges found two such
  rows only after nine clean-room runs, and fixing the class mechanically
  found a third they had all missed. Scoped to what needs no reading for
  sense: a quoted line must appear in the chapter it is attributed to, and a
  cited chapter must exist.
- **`test_rubric_contract.py`** — any computed aggregate is written `N.NN`.
  An integer cannot express a change smaller than 1, and revision stops on a
  change of less than 0.5.
- **`test_bands.py` / `test_form_pack.py`** — a pack needs a length-scoped
  section to be judged below novel length. Band fallback is
  intermediate → compressed → default.

## Workflow

```bash
uv run pytest tests/ -q
```

547 tests, about 7 seconds. CI runs exactly that, then validates every genre
pack, every form pack, and runs `gate_solver.py` across all packs — so a cap
that makes a gate unreachable fails the build rather than a user's book.

**The version lives in two files and both must move:**
`plugin/autoauthor/.claude-plugin/plugin.json` and
`.claude-plugin/marketplace.json` (twice in the latter). Updating the
marketplace is not the same as updating the plugin — a user can refresh the
marketplace and still run a cached older build.

Commit messages here are a sentence about what changed and why, then the
reasoning. Use `git commit -F -` with a heredoc: backticks in a `-m` string
get executed by the shell, which has already happened once.

## House style for prose in this repo

The packs, rubrics and skills are written in a specific register, and a patch
that ignores it reads as a patch. Be concrete over general. Name the failure
that motivated a rule, with its version or its live run, because a rule whose
reason is recorded survives the next person who thinks it is arbitrary. State
the test a judge should run, not the quality it should look for. Do not add a
comment claiming work the code does not do — a dead `PROSE_CAP_EXCLUDE` was
deleted rather than documented.

And read `ANTI-SLOP.md` before writing prose here. It applies to this
document too.
