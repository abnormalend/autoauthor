# Design record

Specs (`specs/`) describe what was designed; plans (`plans/`) describe how
it was executed; loose files at this level record results of verification
runs.

**These are dated records and are not kept current.** Documents written
before 2026-08-13 use the project's former name, **autonovel**, its former
plugin path `plugin/autonovel/`, and its former skill names (`novel-seed`,
`novel-draft`, and so on, invoked as `/autonovel:novel-*`). They were
deliberately left alone during the rename to `autoauthor` in 0.4.0, for the
same reason `PIPELINE.md` still records `lore_score`: a design document that
is edited to match later decisions stops being evidence of what was actually
decided, and this project's whole failure mode is confident text nobody can
check.

Translating an old path forward:

| then | now |
|---|---|
| `plugin/autonovel/` | `plugin/autoauthor/` |
| `/autonovel:novel` | `/autoauthor:status` |
| `/autonovel:novel-<x>` | `/autoauthor:<x>` |
| `skills/novel-<x>/` | `skills/<x>/` |
| `novel_score` | `work_score` |
| `lore_score` | `pillar_score` (0.2.0) |

One document is deliberately *about* the rename and reads correctly as
written: `specs/2026-08-13-form-parameterization-design.md`, whose phase 4
proposed it. It shipped early, ahead of phases 0–3, because everything those
phases create would otherwise have been born under the old name.
