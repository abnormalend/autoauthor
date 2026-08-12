# Genre Pack Authoring Guide

Copy this file to `<name>.md`, fill it in, and validate:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/validate_genre_pack.py" <name>.md
```

A pack may live in the plugin (`shared/genres/`) or in a single novel
project (`<project>/genres/`). The project copy wins.

## Roles

`role` is a list, because most packs serve more than one:

- **primary** — owns the pillar dimensions, category weights, plot
  architecture, book shape, and seed prompt.
- **secondary** — contributes additively to a primary. Its weights,
  `pillar_label`, `beat_system`, `shape`, and Plot Architecture are ignored.
- **modifier** — an orthogonal axis (age category, heat level, tone). Only
  its Framing, Genre Contract, Drafting Rules, and `content_register` are
  read. It may not declare `weights`, `pillar_label`, `beat_system`,
  `shape`, or a Pillar Dimensions section.

Romance is `["primary", "secondary"]` — a romance novel, or a romantic
subplot in a fantasy. Erotica is `["primary", "modifier"]`.

## Required

A primary needs `## Framing` and `## Pillar Dimensions`. A modifier needs
neither. Everything else is optional; omit `## Plot Architecture` to inherit
the base Save the Cat structure.

---

```
---
{
  "name": "<must match the filename stem>",
  "label": "<human-readable; feeds NOVEL-GENRE at export>",
  "role": ["primary"],
  "pillar_label": "<names the rubric category, e.g. 'Relationship Architecture'>",
  "weights": {"pillar": 40, "character": 30, "structure": 20, "craft": 10},
  "beat_system": "save-the-cat",
  "content_register": {},
  "conflicts_with": [],
  "shape": {
    "chapters": [22, 26],
    "words": [80000, 95000],
    "chapter_words": 3200,
    "pov_default": "third limited past"
  },
  "artifacts": []
}
---
```

`weights` must be integers summing to 100. `content_register` declares
intensity axes and their levels — `{"heat": "explicit"}`,
`{"violence": "off-page"}` — and a declared level becomes a Genre Contract
promise the book must keep. `artifacts` names extra project files this genre
requires; describe each under `## Artifacts`.

## Framing

Terms and personas the rubrics substitute wherever they refer to genre, the
central system, or comparable authors. Use these exact keys.

- genre_noun — "<e.g. 'fantasy novel'>"
- pillar_noun — "<what the prose calls the central system, e.g. 'magic system'>"
- comps — <4-6 authors a genre reader would compare this to>
- seed_persona — <one sentence: who is generating concepts>
- reader_persona — <one sentence: the Genre Reader panel persona>
- writer_persona — <one sentence: the Writer panel persona>

## Pillar Dimensions

Three to six scored dimensions. Each bullet MUST read `- key — criteria`
with an em dash; the validator extracts keys from that shape. Keys must not
collide with the base dimensions (`character_depth`,
`character_distinctiveness`, `character_secrets`, `outline_completeness`,
`foreshadowing_balance`, `internal_consistency`, `voice_clarity`,
`canon_coverage`).

This section takes dimension bullets only — no prose bullets. The parser
reads every `- key <dash> ...` line in this section as a dimension
declaration (or, with the wrong dash, a malformed one), so a stray prose
bullet such as `- write carefully, judges score 0-10` will be parsed as a
dimension key and can trip the validator. Put prose elsewhere (a
paragraph above the bullets, or another section).

Write real rubric criteria, not labels. A judge scores 0-10 against these.

- example_dim — What excellent looks like, what a gap looks like, and one
  concrete test the judge can apply.

## Genre Contract

Binary, checkable promises — not 0-10 scores. A breach caps the score.
`foundation.md` checks these against the outline; `full-novel.md` and
`novel-review` check them against the manuscript.

- <e.g. "The central relationship resolves HEA or HFN.">

## World Sections

Required headings for `world.md`, one per line, in order.

## Cast Requirements

The roster the foundation loop must build, with the depth each role needs.

## Plot Architecture

Act-by-act shape. Omit this section entirely to inherit the base structure.

## Canon Categories

Categories for `canon.md`, each with one example entry in the genre.

## Artifacts

One subsection per file named in `artifacts:` — its template, which phase
fills it, and what the rubric checks about it.

## Drafting Rules

Appended to the base 24 in `drafting-rules.md`. Number from 25. May include
a genre-specific banned-phrase list.

## Seed Prompt

Required concept fields, the DO-NOT list, and diversity requirements for
`novel-seed`.
