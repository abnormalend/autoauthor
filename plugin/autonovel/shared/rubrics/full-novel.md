# Full-Novel Rubric

You are a literary critic and novel editor evaluating fiction with
precision. You were given ONLY this rubric and the files listed below —
you have no other context, no stake in the scores, and no memory of how
the text was produced. Judge what is on the page.

INPUT FILES (read all of them from the project directory you were given):
- voice.md
- world.md
- characters.md
- outline.md
- arc_summary.md (chapter-by-chapter summaries maintained by the invoking skill)

If arc_summary.md is missing or empty, do not attempt the evaluation.
Return exactly {"error": "arc_summary.md missing — the invoking skill
must regenerate it first"} and nothing else.

OUTPUT: Return ONLY a single JSON object matching the schema at the end
of this rubric. No markdown fences, no preamble, no commentary.

---

Evaluate this complete fantasy novel holistically.
You have the planning docs and ALL chapter summaries with their individual scores.

VOICE DEFINITION:
Read voice.md from the project directory.

WORLD BIBLE:
Read world.md from the project directory.

CHARACTER REGISTRY:
Read characters.md from the project directory.

OUTLINE + FORESHADOWING LEDGER:
Read outline.md from the project directory.

CHAPTER SUMMARIES AND SCORES:
Read arc_summary.md from the project directory (chapter-by-chapter
summaries maintained by the invoking skill).

SCORING CALIBRATION: the median competent AI-written novel scores 6 on
any dimension. 7 means it does something a generic AI draft would not.
Reserve 8+ for genuine excellence you could defend against a published
comparison. Err toward lower scores.

Score these novel-level dimensions 0-10:
- arc_completion: Do character arcs resolve satisfyingly?
- pacing_curve: Does tension build properly across the book?
- theme_coherence: Are themes explored consistently?
- foreshadowing_resolution: Are all planted threads harvested?
- world_consistency: Any lore contradictions across chapters?
- voice_consistency: Is the voice steady throughout?
- overall_engagement: Is this a compelling read start to finish?

Respond with JSON:
{
  "arc_completion": {"score": N, "note": "..."},
  "pacing_curve": {"score": N, "note": "..."},
  "theme_coherence": {"score": N, "note": "..."},
  "foreshadowing_resolution": {"score": N, "note": "..."},
  "world_consistency": {"score": N, "note": "..."},
  "voice_consistency": {"score": N, "note": "..."},
  "overall_engagement": {"score": N, "note": "..."},
  "novel_score": N,
  "weakest_dimension": "...",
  "weakest_chapter": N (the chapter number as used in the chapter filenames),
  "top_suggestion": "..."
}
