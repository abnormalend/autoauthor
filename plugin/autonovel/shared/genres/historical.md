---
{
  "name": "historical",
  "label": "Historical",
  "role": ["modifier"],
  "content_register": {},
  "conflicts_with": [],
  "artifacts": []
}
---

Historical is a period axis, not a genre. A Regency romance is a romance, a
Victorian mystery is a mystery, a Cold War spy novel is a thriller: the
machinery of the primary genre does not change when the book is set in the
past. What changes is the discipline layered on top, which is why this is a
modifier rather than a shelf of its own.

A single pack cannot carry the canon of every era from Ancient Rome to 1965,
and does not try. What transfers across all of them is method — the
anachronism test, the constraint test, the register test, the research-depth
test. Era-specific facts belong in the project's `world.md` and `canon.md`,
or, if a project wants them enforced as rubric criteria, in a pack written
into that novel's own `genres/` directory, where the project copy wins over
the plugin's.

This pack constrains no content register. The past is not more or less
intense than the present — a Regency drawing room and a Viking raid are both
historical — so heat, violence, and language are left to the primary and to
whatever tone or age modifier is loaded beside this one.

## Framing

This modifier supplies no `genre_noun` and no `pillar_noun` — the primary
pack owns both, and a Regency romance is still a romance novel with a
central relationship. Where a rubric names the genre, read the primary's
`genre_noun` with the period applied: "a historical mystery novel". The
comps and personas below do override the primary's, because the panel must
read as this axis's audience.

- comps — Hilary Mantel, Patrick O'Brian, Georgette Heyer, C.J. Sansom, Sarah Waters, Mary Renault, Robert Harris
- seed_persona — a novelist at home in more than one century who chooses a period for what it forbids rather than for how it looks, and who never proposes a premise that a telephone and one frank conversation would end
- reader_persona — a historical reader who knows their era well enough to catch a wrong coin or a phrase coined in 1974, who is there for the texture of a life not their own, and who stops trusting a book the moment its people start behaving like moderns in costume
- writer_persona — an editor of historical fiction who reads for whether the period is generating the obstacles or dressing them, for research that has been digested rather than deposited, and for the exact sentence where the narration steps out of the period to reassure a modern reader

## Genre Contract

These bind the book as a whole when this pack is loaded, alongside every
promise the primary pack makes.

- The book commits to a specific period and place and holds to it. One stated time — a decade or tighter where the period is dense with change — recorded in `world.md`. A setting that is vaguely "the past", or that drifts between eras as scenes require, has breached.
- Nothing in the book postdates its period: not objects, technologies, institutions, or law, and not ideas. A character who reasons in the vocabulary of modern psychology, sociology, or rights-talk breaks the period more thoroughly than a wrong button does. Where the book departs from the record deliberately — an invented town, a compressed campaign, an outright alternate history — the departure is chosen, consistent, and written down in `canon.md`.
- The period generates the obstacles. Apply the re-setting test: move the book to the present day unchanged and ask which obstacles survive. At least the central one — whatever makes this plot hard, whichever genre it belongs to — must disappear. A book whose period supplies costumes, place-names, and modes of address while its characters solve their problems with modern mobility, modern candour, and modern options has breached this.
- Period-plausible belief is rendered without endorsement and without anachronistic correction. Characters may hold the assumptions of their time, including ugly ones; the narrative neither presents the period's cruelties approvingly nor issues every sympathetic character a modern conscience. Sympathy is earned inside the period, not by exempting a character from it.
- Dialogue and narration are period-plausible in register. The book reads neither as modern speech in costume — contemporary idiom, therapy vocabulary, text-message rhythm — nor as pastiche assembled out of archaism. Any phrase that could not have appeared in a letter written that decade does not appear here.

## Drafting Rules

25. Write the constraint operating, not the constraint mentioned. Entail and inheritance, the mechanics of ruin, chaperonage, who may hold money or travel alone, what a letter costs and how many days it takes to arrive — these are the plot's machinery, not its wallpaper. Every act break should turn on something only this period could have done to these people. If a scene's difficulty would survive being re-set today, the period is not yet working in it.
26. Get the register right by writing plainer, not older. The fix for a modern-sounding line is almost never `forsooth`, `'twas`, or an inverted clause; it is shorter words, a longer sentence, and no idiom coined since. Strip contemporary metaphor first — anything drawn from machinery, screens, therapy, or sport the period did not have — and the line will usually sit correctly without a single archaism.
27. Detail is chosen, not inventoried. The writer should know ten times what reaches the page, and the reader should feel that without being taught. One exactly right object — what the room is lit by, what the coat is worth, what the meal actually was — does more than a paragraph of furniture. A passage that exists to deliver research is cut, however hard it was to find.
28. No character explains their own world to someone who lives in it. Information reaches the reader through friction: the thing that goes wrong, the sum that will not come out, the newcomer who breaks a rule and is corrected, the letter that arrives too late to be acted on. If two characters are telling each other what they both know, rewrite the scene as the moment the knowledge fails somebody.
29. Money, distance, and time are real quantities and must stay consistent. Know what a thing costs against what the character earns, how many days the journey takes, how long the news takes to travel, how long the light lasts. Record the values in `canon.md` and hold to them — this is where the reader who knows the period catches a book out, and where the reader who does not still feels the sag.
30. Characters think inside their period, and the book does not rescue them from it. Give a character the reader likes an assumption the reader will dislike, and let holding it cost them something inside the story rather than earning a rebuke from the narration. The narrator does not step forward to reassure the modern reader that this was wrong; the scene is built so the reader does not need telling.
31. Let the period stay strange where it was strange. Illness, smell, noise, cold, what happened after dark, how bodies were washed and fed and buried, how long people waited for anything — the daily textures are where a reader starts believing you, and smoothing them toward the familiar is the quietest way to lose them.
