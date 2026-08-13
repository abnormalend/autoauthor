# Revision Playbook

Ported from the original pipeline's revision cycle notes (PIPELINE.md).
Read this before Fixing any consensus item or eval callout in
revise's SKILL.md.

## Consensus-item playbook

Work consensus items in this priority order.

**a. Cut candidate (agreement across most/all readers)**

FIRST: verify the item against the chapter (SKILL.md Fix step 1). The
panel reads only arc_summary.md, and summary flattens texture — a quiet
chapter and a repetitive chapter look identical in summary form, but
only one of them has a defect.

What the panel is actually detecting when it is right is REPETITION: a
beat, a posture, or a closing move the chapter shares with its
neighbours. Diagnose that before touching length. Compare the chapter's
final paragraph against the final paragraphs of the chapters on either
side; in a withholding arc the recurring offender is usually the ending
(protagonist alone, restating what they did not say). Re-ending the
chapter on a different move fixes what the readers felt. Removing words
does not.

Then write a compression brief (`gen_brief.py --cuts <ch>` or
`--panel <ch>`) and rewrite in-session per that brief.
Target: cut 40-60% of the chapter's words.
Keep: the 2-3 essential beats the panel identified.
WARNING: don't over-compress. Below ~1800 words is too thin for any chapter.
Sweet spot: 2200-3000 words for a compressed chapter.
WARNING: the script's COMPRESS target (55% of current) will ask for a
count under the 1800 floor on any chapter below ~3,300 words. Override
it by hand; the guardrail wins.

**The compression trap — read before any cut-candidate rewrite.**
The panel and the chapter judge want opposite things, and the chapter
judge holds the gate. Compression that turns dramatized scene into
narrated summary reliably drops `beat_coverage` to 6, because the
chapter rubric scores a summarized beat as half-hit. A rewrite can be
shorter, tighter and cleaner and still score BELOW the baggier original
on that alone. So cut narration, gloss, retrospective essays and
repeated interiority — never scenes, dialogue, or dramatized beats. If
a chapter is long because it is eventful, the right outcome may be that
it keeps its words and loses its repetition. Length is the panel's
proxy, not its finding.

**b. Missing scene**

FIRST: grep the chapter for the beat. "Missing scene" is the panel's
most common false positive, because a scene the summary renders in one
clause reads to four summary-readers as absent. If it is already
dramatized, the summary was lossy — skip the item and log it. Check the
outline entry too: it may already require the beat (proving it should
be there) or forbid it by design (a withholding the book chose on
purpose, which the panel will keep asking you to undo).

Otherwise write an expansion brief and rewrite the target chapter
in-session, OR apply a surgical patch by hand if the missing scene is
under 400 words.
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
- **Trusting panel consensus as fact.** The four readers share one
  input (arc_summary.md), so they share its blind spots: agreement
  measures how legible a defect is in summary, NOT how real it is. Three
  readers naming the same chapter for the same reason can all be wrong
  in the same way. Verify every consensus item against the prose before
  briefing it (SKILL.md Fix step 1). Consensus also moves between
  cycles: an item four readers agreed on can come back contested when
  two of them say the thing is correct by design. A reversal like that
  is evidence the original consensus was soft — drop the item rather
  than spending a fourth attempt on it.
- **Stale baselines (the gate's blind spot).** A chapter's recorded
  score usually comes from the drafting judge, which runs 0.5-1.0 above
  the revision judge on identical prose. Every rewrite you gate against
  that number is being held to a bar that does not exist. Re-score the
  current committed text before discarding anything (SKILL.md Fix step
  4). Related: same-judge variance on identical text is about ±0.5, so
  treat a single score as a reading, not a verdict.
- **Cutting a chapter whose real problem is somewhere else.** When the
  panel names a stretch (ch 10-12, ch 8-17), the defect is usually the
  repeated BEAT running through all of them, not any one chapter's
  length. Compressing the middle instance leaves the pattern intact and
  costs you the chapter's texture. Look for the repetition first; if it
  spans six chapters it is an outline problem and no single rewrite
  will move the score.
- **Editing a high-scoring chapter at all.** The keep gate is "beats
  the previous score," so any chapter already at 8.0 is a bad bet: it
  has the least room above it and the most to lose, and normal judge
  variance (±0.5) can sink a genuinely good edit. Spend the cycle's
  attempts on the 7.0s. When the panel's top consensus item lands on
  the book's strongest chapter, that is itself a signal the item is a
  summary artifact.
- **Patches that pass every check you thought to run and still fail.**
  A surgical patch can be canon-safe, slop-clean, correctly voiced, and
  still cost the chapter its score. Budget 3 attempts and expect to
  spend them: attempt 1 typically surfaces a canon seam the patch
  introduced (an object moved out of its established handling), attempt
  2 a voice-architecture seam (a reserved sentence shape given to the
  wrong character). Preserve the best attempt in
  `eval_logs/ch_NN_attempt_<k>.md`, log the trajectory in
  `edit_logs/skipped.md`, and resume it next cycle rather than
  restarting from scratch — a monotonic 7.5 → 7.8 with canon now clean
  is a near miss, not a dead end.

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
