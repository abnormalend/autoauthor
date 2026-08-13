---
name: review
description: Use when a novel project is in the review phase, or the user asks for a full manuscript review, a dual-persona literary critique, or the final quality pass before export.
---

# Novel Review — Phase 3b

The final quality push. A fresh clean-room subagent reads the ENTIRE
manuscript and reviews it twice: as a literary critic, then as a
professor of fiction. Fix the top items; repeat. Maximum 4 rounds.

## Setup

1. Verify the project (state.json + voice.md), clean tree (dirty →
   STOP and ask), phase `review`. Anchor in the project directory.
2. **Resolve the genre.** Run from the project directory:

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/resolve_genre.py"
   ```

   If it exits non-zero, STOP and report — an unresolvable or conflicting
   genre stack must be fixed before any review work. Keep the reported pack
   paths; every judge dispatch below needs them. If `state.json` has no
   `genre` field at all, or its `genre` is null, STOP and run the migration
   in `novel/SKILL.md` first — a null genre resolves silently to `general`,
   so the resolver exiting 0 is NOT evidence that anyone chose a genre.
3. Resume: state.json `review_round` is the last COMPLETED round; this
   session runs round R = review_round + 1.
4. Malformed or contract-violating reviewer output anywhere in this
   skill: one strict retry, then stop the round and report to the user
   (a failed full-manuscript review is not silently skippable).
5. Required reading before any chapter rewrite:
   - `plugin/autoauthor/skills/revise/SKILL.md`'s Fix stage
     (path: `"${CLAUDE_PLUGIN_ROOT}/skills/revise/SKILL.md"`)
     and `"${CLAUDE_PLUGIN_ROOT}/skills/revise/references/revision-playbook.md"`
     — specifically its "Rewrite rules" section. The Fix stage's
     scratch-copy, attempts.tsv, keep/discard, and baseline conventions
     apply verbatim here, and the Rewrite rules bind every chapter rewrite
     in this skill too.
   - every genre pack path the resolver reported in step 2. This skill
     rewrites chapters, and the packs are where the genre's
     `## Drafting Rules` and `content_register` live — a rewrite judged
     against the packs but written without them will drift off the
     register the rest of the book was drafted to.

## One round (R)

1. **Build the manuscript.** Concatenate `chapters/ch_*.md` in
   numerical order, separated by `\n\n---\n\n`, into `manuscript.md`.
   Add `manuscript.md` to `.gitignore` if not already there (it is
   derived, never source).
2. **Review.** Dispatch a fresh judge subagent (general-purpose, no
   other context) with exactly: "Read the rubric at `<absolute plugin
   path>/shared/rubrics/manuscript-review.md` and the genre pack(s) at
   `<resolved pack paths, primary first, each labeled with its role>`,
   and follow the rubric exactly.
   The project directory is `<absolute project path>`. Return ONLY the
   output the rubric specifies." Request the strongest available model
   for this dispatch if the Agent tool exposes a model choice —
   literary judgment is the one place model quality dominates.
   Save the returned markdown verbatim to
   `edit_logs/<UTC yyyymmdd_hhmmss>_review.md`.
3. **Parse the tags.** From the Professor section count: total items,
   major-unqualified items, qualified items; extract the star rating
   from the Critic section's final "Rating:" line. Items missing tag
   lines count as unqualified moderate revision items (and note the
   contract violation). Record a summary row in results.tsv:
   `<ISO timestamp>\treview\t<stars>\t<total manuscript words>\tkeep\treview round R: <total> items, <major-unqualified> major-unqualified, <qualified> qualified`
4. **STOPPING CONDITIONS — stop revising when ANY holds:**
   - zero major unqualified items
   - qualified items > 50% of total items
   - total items <= 2
   - R >= 4
   Also weigh the qualitative signal: when the reviewer's language
   shifts from "the novel has problems" to "these are the costs of
   ambition," you are done. An item persisting across 3+ rounds is
   probably structural to the novel's approach — accept it and say so.
   If stopping: go to Exit.
5. **Fix the top items** (major first, then moderate; unqualified
   before qualified; skip minor unless trivial). Fix at most 4 items
   per round; the loop exists to converge, not to fix everything at
   once. For items tagged `compression`, `addition`, or `revision`,
   first map the item to its chapter number: match its quoted
   passages or scene references against `chapters/ch_*.md` (grep a
   distinctive phrase). If such an item spans multiple chapters or
   matches none, treat it as `structural` (queue for the user). Items
   tagged `mechanical` skip mapping — they are cross-chapter by
   nature and go straight to the grep-and-fix path; items tagged
   `structural` skip mapping too.
   - type `compression` or `revision` → generate a brief
     (`python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/gen_brief.py" --eval <ch>`
     when a chapter eval exists, else hand-write the brief into
     `briefs/chNN_review.md` from the item text), then rewrite the
     chapter in-session exactly as revise's Fix stage does
     (same scratch-copy, scoring, keep/discard, and attempts.tsv
     conventions; baseline per its rules; attempt rows use phase
     `review`).
   - type `mechanical` (tics, repeated phrases) → grep the phrase
     across all chapters, fix every instance but the strongest, by
     direct edit. Run the slop scorer over touched chapters.
   - type `addition` → surgical patch in place if < 400 words of new
     material; otherwise brief + rewrite as above.
   - type `structural` (reordering/merging chapters) → STOP work on
     THAT item and queue it for the user; continue fixing the other
     items in the round, then present all queued structural items
     together before committing the round.
   Rebuild manuscript.md after fixes (next round re-reads it).
6. Update state.json `review_round: R`; commit:
   `git add -A && git commit -m "review round R: <total> items, <fixed> fixed"`.

## Exit

Set state.json `phase: "export"`. Commit:
`git add -A && git commit -m "review complete: <R> rounds, <stars> stars"`.
Pushover notification (pushover skill): title
"autoauthor: review", message with rounds, final star rating, stop
reason, next step `/autoauthor:export`. Report the same to the
user, including any accepted structural items.
