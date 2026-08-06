# Revision Playbook

Ported from the original pipeline's revision cycle notes (PIPELINE.md).
Read this before Fixing any consensus item or eval callout in
novel-revise's SKILL.md.

## Consensus-item playbook

Work consensus items in this priority order.

**a. Cut candidate (agreement across most/all readers)**

Write a compression brief (`gen_brief.py --cuts <ch>` or `--panel <ch>`)
and rewrite the chapter in-session per that brief.
Target: cut 40-60% of the chapter's words.
Keep: the 2-3 essential beats the panel identified.
WARNING: don't over-compress. Below ~1800 words is too thin for any chapter.
Sweet spot: 2200-3000 words for a compressed chapter.

**b. Missing scene**

Write an expansion brief and rewrite the target chapter in-session, OR
apply a surgical patch by hand if the missing scene is under 400 words.
Key: the brief must specify what to KEEP (existing good material) and
what to ADD (the missing beat).

**c. Thin character**

Identify 1-2 existing scenes where the character appears. Add a
private/unguarded moment the POV character catches. Connect it to the
character's backstory in characters.md. Don't add a new scene — deepen
an existing one.

**d. Weak scene**

Write a dramatization brief and rewrite in-session. Change HOW
information arrives, not WHAT information arrives. Convert "reading a
document" into an investigation or confrontation. Convert "briefing"
into a confrontation with resistance.

**e. Consistency / timeline**

Search for contradictions (years, ages, sequence of events). Fix in
canon.md AND all source files AND chapter references — a fix that
touches only one of the three leaves the contradiction live elsewhere.

**f. Chapter renumbering**

If chapters were merged or deleted, every internal title needs
updating. Do this with a script or a systematic find-and-replace pass,
not scattered manual edits — a missed rename produces a silent
continuity break.

After each structural change: re-score the affected chapter(s) with
the chapter judge. Keep if improved, discard if not. Commit with a
detailed message.

## Eval-callout patterns

Full-novel eval output (`weakest_dimension`, `weakest_chapter`,
`top_suggestion`) tends to fall into one of these patterns. Match the
pattern before writing a fix.

**a. Pacing (the stubborn score)**

- A stretch of similar scenes (investigation, negotiation, travel)
  reads as repetitive → compress the weakest instance, vary scene
  types around it.
- A late stretch feels compressed relative to its structural weight →
  expand the gathering/build-up and the climax around it.
- Reveals fire too fast, back to back → add breathing beats between
  reveals.

WARNING: fixing one stretch tends to expose the next stretch as the
new weak point. A pacing score of 7 may be a structural ceiling for an
LLM-evaluated novel of this length — don't chase it past diminishing
returns.

**b. Chapter too short for its structural importance**

Write an expansion brief and rewrite in-session. Target: +800-1500
words. Focus on physical accumulation, dread, or silence-with-duration
rather than new plot. The brief should specify WHICH BEATS to expand,
not just "make it longer."

**c. Repeated phrases across chapters**

Search for the phrase across all chapters. Change all instances except
the most impactful one. Common repeats to watch for: opening
descriptions, emotional formulas, "the way [X] did [Y]" constructions,
triadic lists.

**d. Unresolved threads**

Check the foreshadowing ledger in outline.md. Add resolution beats
where threads were planted but never harvested. Use surgical patches,
not full rewrites, unless the chapter also needs a rewrite for other
reasons.

If scores are unchanged after 2 cycles of addressing callouts on the
same dimension, stop — diminishing returns.

## Dangers

- **Over-compressing.** Cutting a chapter below 1800 words tends to
  make it the new weakest chapter. Sweet spot for a compressed chapter
  is 2200-3000 words.
- **Expansion bloat.** Rewrites driven by a brief tend to run ~30%
  longer than briefed. A brief targeting 3200 words will often produce
  3800-4200 words — brief for shorter than the actual target.
- **Score chasing.** After cycle 4, fixing one dimension's score often
  drops another (e.g. arc_completion regressing when a chapter is
  over-compressed for pacing). Watch the full score trajectory, not
  just the dimension you're targeting.
- **Weakest-chapter whack-a-mole.** The full-novel judge's
  `weakest_chapter` rotates between a small set of chapters as each
  gets fixed and exposes the next. Chasing it indefinitely doesn't
  converge — after 2 rotations back to a chapter already fixed once
  this revision, stop chasing that dimension and move on.

## Rewrite rules (apply to every chapter rewrite)

Ported verbatim from the original pipeline's revision-generation
prompt. Every in-session chapter rewrite in this skill must follow
these rules in addition to voice.md and the outline entry:

- NO triadic sensory lists (X. Y. Z.)
- NO "He did not [verb]" more than once
- NO "He thought about [X]" constructions
- NO "the way [X] did [Y]" more than twice
- NO "not X, but Y" formula in narration
- NO over-explaining after showing
- MAX 2 section breaks
- At least one moment that genuinely surprises
- 70%+ in-scene (dialogue and action, not summary)
- Dialogue should sound like speech, not prose
