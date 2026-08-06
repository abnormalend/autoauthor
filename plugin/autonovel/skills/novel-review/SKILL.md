---
name: novel-review
description: Use when a novel project is in the review phase, or the user asks for a full manuscript review, a dual-persona literary critique, or the final quality pass before export.
---

# Novel Review — Phase 3b

The final quality push. A fresh clean-room subagent reads the ENTIRE
manuscript and reviews it twice: as a literary critic, then as a
professor of fiction. Fix the top items; repeat. Maximum 4 rounds.

## Setup

1. Verify the project (state.json + voice.md), clean tree (dirty →
   STOP and ask), phase `review`. Anchor in the project directory.
2. Resume: state.json `review_round` is the last COMPLETED round; this
   session runs round R = review_round + 1.
3. Malformed or contract-violating reviewer output anywhere in this
   skill: one strict retry, then stop the round and report to the user
   (a failed full-manuscript review is not silently skippable).
4. Read `plugin/autonovel/skills/novel-revise/SKILL.md`'s Fix stage
   (path: `"${CLAUDE_PLUGIN_ROOT}/skills/novel-revise/SKILL.md"`)
   before any chapter rewrite — its scratch-copy, attempts.tsv,
   keep/discard, and baseline conventions apply verbatim here.

## One round (R)

1. **Build the manuscript.** Concatenate `chapters/ch_*.md` in
   numerical order, separated by `\n\n---\n\n`, into `manuscript.md`.
   Add `manuscript.md` to `.gitignore` if not already there (it is
   derived, never source).
2. **Review.** Dispatch a fresh judge subagent (general-purpose, no
   other context) with exactly: "Read the rubric at `<absolute plugin
   path>/shared/rubrics/manuscript-review.md` and follow it exactly.
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
     chapter in-session exactly as novel-revise's Fix stage does
     (same scratch-copy, scoring, keep/discard, and attempts.tsv
     conventions; baseline per its rules).
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
"autonovel: review", message with rounds, final star rating, stop
reason, next step `/autonovel:novel-export`. Report the same to the
user, including any accepted structural items.
