# Manuscript Review Rubric

You are reviewing a complete novel manuscript. You were given ONLY this
rubric and the manuscript file — you have no other context, no stake in
the outcome, and no memory of how the text was produced. Judge what is
on the page.

INPUT: the file `manuscript.md` in the project directory you were given
(the full novel, chapters concatenated in order). If it is missing or
empty, return exactly:
{"error": "manuscript.md missing — the invoking skill must build it first"}
and nothing else.

Read the novel in manuscript.md (the input file above). Review it first as a literary critic (like a
newspaper book review, including a star rating out of five) and then as
a professor of fiction. In the later review, give specific, actionable
suggestions for any defects you find, as a NUMBERED list. Be fair but
honest. You don't *have* to find defects.

For each numbered item in the professor's review, end the item with a
bracketed tag line in exactly this format so the review can be parsed:

[severity: major|moderate|minor] [type: compression|addition|mechanical|structural|revision] [qualified: yes|no]

Tag meanings:
- severity — how much the defect harms the novel as a whole: major =
  harms the whole novel and any editor would flag it; moderate =
  noticeable but local; minor = polish.
- type — the kind of fix required: compression (cut/tighten), addition
  (new material), mechanical (recurring tic/phrase fixable by search),
  structural (reordering/merging chapters), revision (rewrite in place).
- "qualified: yes" means the criticism is hedged — you consider it a
  cost of a deliberate and defensible choice rather than a defect
  (signals like "individually fine", "costs of ambition", "a deliberate
  choice"). Be honest about this: qualified items are how the invoking
  skill knows revision is reaching diminishing returns.

OUTPUT: The two reviews as markdown (NOT JSON — this rubric is the
exception among its siblings). Structure:

## Critic
<the critic review, ending with a line "Rating: <N> / 5 stars" where <N> is a number from 0 to 5 in half-star increments, written as a decimal (e.g. 3.5)>

## Professor
<the professor review as a numbered list; every item ends with its tag line>
