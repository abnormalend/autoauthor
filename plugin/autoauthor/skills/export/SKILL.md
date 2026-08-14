---
name: export
description: Use when a novel project reaches the export phase, or the user asks to typeset the book, build the PDF or ePub, or produce the final print-ready files.
---

# Novel Export — Phase 4

Produces `typeset/novel.pdf` (LaTeX via tectonic) and `<title-slug>.epub`
(pandoc) inside the novel project.

## Steps

1. **Verify.** Project check (state.json + voice.md), clean tree
   (dirty → STOP and ask), phase `export` (earlier phase → ask before
   proceeding). Tool check: `which tectonic` and `which pandoc`; if
   either is missing tell the user (`brew install tectonic pandoc`)
   and stop for whichever is needed.

1b. **If this is a container**, resolve first
   (`resolve_genre.py`) and branch on `structure.assembles_as_one_book`:

   - **A collection binds as one book.** It has no `chapters/` of its
     own, so build one:

     ```bash
     python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/assemble.py"
     ```

     That writes `assembled/ch_NN.md` — every work's chapters in the
     container's declared running order, renumbered gaplessly, each work
     opening with its own half-title. It exits non-zero if any work
     contributed nothing, because a bound book silently missing a story
     is the failure this path risks. Read its report before continuing;
     the chapter spans it prints are the table of contents.

     Then run steps 2-7 against `assembled/` wherever they say
     `chapters/`. The title is the collection's, from the container's
     state.json, and `voice.md` is `bible/voice.md`.

   - **A series does not.** Each volume is a book and exports on its own:
     stop, and tell the user to `cd works/<volume>` and run export there.
     An omnibus is a real thing to want, and it is not this — it needs
     its own front matter and its own decisions.
2. **Normalize chapter titles.** Every `chapters/ch_NN.md` must start
   `# Chapter N: <Title>` — single `#`, N matching the filename
   without zero-padding. Fix drift by direct edit. If chapters were
   merged or renumbered during revision, verify the sequence is
   gapless (ch_01..ch_NN). Commit if anything changed:
   `git add -A && git commit -m "export: normalize chapter titles"`.
3. **Stage the typeset assets.** `mkdir -p typeset`, then copy every
   file from `"${CLAUDE_PLUGIN_ROOT}/shared/typeset/"` into `typeset/`
   ONLY where the destination file does not already exist — a
   project's customized copies always win.
4. **Fill the placeholders.** Two conventions exist side by side:
   - `typeset/novel.tex`, `typeset/epub_style.css`,
     `typeset/epub_front_matter.md`, `typeset/epub_colophon.md` use
     `NOVEL-TITLE`, `NOVEL-TITLE-SHORT`, `NOVEL-AUTHOR`,
     `NOVEL-EPIGRAPH`, `NOVEL-END-TEXT`, `NOVEL-GENRE`.
   - `typeset/epub_metadata.yaml` is the ONLY file using bare `TITLE`
     and `AUTHOR` tokens (`epub_back_cover.md` has no placeholders —
     nothing to fill there).
   Fill ALL of them. Sources:

   **Title — read `state.json`'s `title`.** For a container, read the
   CONTAINER's; that is the book's title, and each work's own title is
   its half-title inside it. Only ask the user if the field is null or
   missing, and when you do ask, WRITE THE ANSWER BACK to `state.json`
   before continuing — a title asked for and not recorded is a title
   that gets asked for again, and answered differently.

   If the field is null, offer the first heading of `outline.md` as the
   default; a story that named itself during foundation usually put it
   there. Confirm rather than assume: this is the one piece of a book's
   identity that is not in the prose.

   Then: author — ask the user once (suggest
   `git config user.name` as the default);
   genre — run `python3 "${CLAUDE_PLUGIN_ROOT}/shared/scripts/resolve_genre.py"`
   and offer `display_label` as the default `NOVEL-GENRE` (e.g. "Mystery
   Romance"); let the user edit it, since hybrid genre names are not
   reliably composable from pack labels;
   epigraph — choose a resonant NON-SPOILER line from the
   novel's own text and confirm with the user; end-text — a short
   closing line, confirm with the user. Verify afterwards in two
   scoped passes: `grep -rn 'NOVEL-' typeset/` must return nothing,
   and `grep -n 'TITLE\|AUTHOR' typeset/epub_metadata.yaml` must
   return nothing. Do NOT run a bare TITLE/AUTHOR grep across all
   typeset files — novel.tex has innocent `% === TITLE PAGE ===`
   comments, and a global find-and-replace on the bare tokens would
   corrupt the NOVEL-* tokens they're substrings of.
5. **Build the PDF.**
   `python3 typeset/build_tex.py` (the staged copy — it reads
   `chapters/` from the current directory and writes
   `typeset/chapters_content.tex`; it skips non-chapter files with a
   warning — investigate any unexpected skip). Then compile:
   `tectonic typeset/novel.tex`. If tectonic reports LaTeX errors,
   fix them in the generated `chapters_content.tex` pipeline (the
   escaping logic in the staged `build_tex.py`) — never by editing
   chapter prose to accommodate LaTeX.
6. **Build the ePub.**
   `pandoc typeset/epub_front_matter.md chapters/ch_*.md typeset/epub_colophon.md --metadata-file=typeset/epub_metadata.yaml --css=typeset/epub_style.css --toc -o "<title-slug>.epub"`
   where `<title-slug>` is the kebab-case title. Open the ePub's
   metadata (`pandoc --to=native` spot check or unzip) only if pandoc
   warns; otherwise trust a clean exit.
7. **Finish.** Set state.json `phase: "done"`. Commit:
   `git add -A && git commit -m "export: <title> — <total word count> words"`
   (built artifacts are gitignored; the commit records state and any
   filled templates). Pushover notification (pushover skill): title
   "autoauthor: export", message with word count and output paths.
   Report to the user: PDF path, ePub path, word count, and that the
   novel is done.
