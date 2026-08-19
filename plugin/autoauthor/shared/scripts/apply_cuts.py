#!/usr/bin/env python3
"""Apply adversarial edit cuts to chapter files in the current novel project (CWD).

Usage:
  python apply_cuts.py 12                                  # apply cuts to ch 12
  python apply_cuts.py all                                 # apply cuts to all chapters
  python apply_cuts.py all --types OVER-EXPLAIN REDUNDANT  # filter by type
  python apply_cuts.py all --min-fat 17                    # only chapters with >=17% fat
  python apply_cuts.py all --dry-run                       # show what would be cut
  python apply_cuts.py all --protect-file edit_logs/protected.md
                                                           # never cut a line listed there
  python apply_cuts.py --verify-protected edit_logs/protected.md
                                                           # which protected lines the
                                                           # manuscript no longer contains
"""

import argparse
import json
import re
import sys
from pathlib import Path

BASE = Path.cwd()
CHAPTERS_DIR = BASE / "chapters"
EDIT_LOGS_DIR = BASE / "edit_logs"

VALID_TYPES = {"OVER-EXPLAIN", "REDUNDANT", "FAT", "TELL", "STRUCTURAL", "GENERIC"}
MIN_QUOTE_LEN = 25

_WS = re.compile(r"\s+")
_QUOTES = str.maketrans({"’": "'", "‘": "'", "“": '"', "”": '"'})
OVERLAP = 20  # chars of shared prefix/suffix that count as touching a protected line


def _norm(s: str) -> str:
    """Whitespace-collapsed, curly quotes straightened — a judge quotes the
    prose in whichever quote style it happens to emit."""
    return _WS.sub(" ", s.translate(_QUOTES)).strip()


def load_protected(path: Path | None) -> list[str]:
    """Newline-delimited substrings that must never be cut.

    Blank lines and lines starting with '#' are ignored, so the skill can
    keep the file as readable markdown with a heading per source (chapter
    judges' three_strongest_sentences, the outline's plant/harvest quotes).
    Whitespace-normalised, because the file is hand-maintained.
    """
    if path is None:
        return []
    lines = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        lines.append(_norm(line))
    return lines


def verify_protected(protected: list[str]) -> tuple[list[str], list[str]]:
    """Split the protected lines into (found, not_found) against every
    `chapters/ch_*.md`, whitespace/quote-normalised on both sides.

    A protected line that is not in the manuscript protects nothing. Two
    ways it happens: a kept rewrite reworded it (cycle 1 protected a line,
    cycle 1's REWRITE changed it, and cycle 2's file still quoted the old
    wording), or it was sourced from the verdict of a superseded drafting
    attempt and was never in the manuscript at all. Either way a cut that
    removes the current wording sails through `protected_by`. The skill
    runs this at the start of each cycle and re-quotes every NOT FOUND
    line from the current manuscript; on one run two cycle-1 lines
    protected nothing in cycle 2 until a hand diff found them.
    """
    corpus = " ".join(
        _norm(p.read_text(encoding="utf-8"))
        for p in sorted(CHAPTERS_DIR.glob("ch_*.md"))
    )
    found, not_found = [], []
    for line in protected:
        (found if line in corpus else not_found).append(line)
    return found, not_found


def protected_by(quote: str, protected: list[str]) -> str | None:
    """The protected line a quote collides with, or None.

    Collides in either direction: the quote contains a protected line
    (the cut would remove it), or a protected line contains the quote (the
    cut would remove part of it). Both destroy the line. A partial overlap
    — the quote's tail is the protected line's head or vice versa, by at
    least OVERLAP chars — is a hit too: a cut that starts mid-sentence and
    runs into a protected one takes its opening clause with it.
    """
    q = _norm(quote)
    if not q:
        return None
    for p in protected:
        if p in q or q in p:
            return p
        if _overlaps(q, p) or _overlaps(p, q):
            return p
    return None


def _overlaps(head: str, tail: str) -> bool:
    """True if some suffix of `head`, at least OVERLAP chars long, is a
    prefix of `tail`."""
    for k in range(min(len(head), len(tail)), OVERLAP - 1, -1):
        if head[-k:] == tail[:k]:
            return True
    return False


def load_cuts(chapter_num: int) -> dict | None:
    """Load the cuts JSON for a given chapter number. Returns None if missing."""
    cuts_file = EDIT_LOGS_DIR / f"ch{chapter_num:02d}_cuts.json"
    if not cuts_file.exists():
        return None
    try:
        data = json.loads(cuts_file.read_text(encoding="utf-8"))
        return data
    except (json.JSONDecodeError, OSError) as exc:
        print(f"  WARNING: failed to parse {cuts_file.name}: {exc}")
        return None


def chapter_path(chapter_num: int) -> Path:
    return CHAPTERS_DIR / f"ch_{chapter_num:02d}.md"


def find_and_remove(text: str, quote: str) -> tuple[str, bool, str]:
    """Try to find and remove quote from text.

    Returns (new_text, success, failure_reason).
    """
    # Exact match first
    count = text.count(quote)
    if count == 1:
        text = text.replace(quote, "", 1)
        return text, True, ""
    if count > 1:
        return text, False, f"ambiguous ({count} matches)"

    # Normalised whitespace match: collapse runs of whitespace in both the
    # text and the quote to single spaces, search, then map back to the
    # original span.
    ws = re.compile(r"\s+")
    norm_quote = ws.sub(" ", quote).strip()
    if len(norm_quote) < MIN_QUOTE_LEN:
        return text, False, "quote too short after normalisation"

    # Build a regex that matches the quote with flexible whitespace
    # Escape each token and join with \s+
    tokens = norm_quote.split(" ")
    pattern = r"\s+".join(re.escape(t) for t in tokens)
    matches = list(re.finditer(pattern, text))
    if len(matches) == 1:
        m = matches[0]
        text = text[:m.start()] + text[m.end():]
        return text, True, ""
    if len(matches) > 1:
        return text, False, f"ambiguous after ws-norm ({len(matches)} matches)"

    return text, False, "not found"


def collapse_blank_lines(text: str) -> str:
    """Collapse runs of 3+ newlines down to 2 (one blank line)."""
    return re.sub(r"\n{3,}", "\n\n", text)


def discover_chapters() -> list[int]:
    """Return sorted list of chapter numbers that have both a chapter file and a cuts file."""
    nums = set()
    for p in EDIT_LOGS_DIR.glob("ch*_cuts.json"):
        m = re.match(r"ch(\d+)_cuts\.json", p.name)
        if m:
            nums.add(int(m.group(1)))
    return sorted(nums)


STALE_SPAN_HOURS = 12


def warn_if_cuts_span_cycles() -> None:
    """Warn on stderr when the cuts files were not all written together.

    `all` globs every ch*_cuts.json. In a later cycle the skill dispatches
    judges only for some chapters, so a chapter it skipped still has last
    cycle's file — and `all` re-applies it, including any line restored by
    hand since. The skill archives old files first; this is the check for
    when it did not.
    """
    mtimes = [p.stat().st_mtime for p in EDIT_LOGS_DIR.glob("ch*_cuts.json")]
    if len(mtimes) < 2:
        return
    if max(mtimes) - min(mtimes) > STALE_SPAN_HOURS * 3600:
        print(f"WARNING: cuts files span more than {STALE_SPAN_HOURS}h — some may "
              "be from a prior cycle; see revise Diagnose step 3", file=sys.stderr)


def process_chapter(
    chapter_num: int,
    type_filter: set[str] | None,
    min_fat: int,
    dry_run: bool,
    protected: list[str] | None = None,
) -> dict:
    """Process cuts for one chapter. Returns stats dict."""
    stats = {"applied": 0, "failed": 0, "skipped": 0, "protected": 0,
             "words_removed": 0, "error": None}
    label = f"ch{chapter_num:02d}"

    # Load cuts
    data = load_cuts(chapter_num)
    if data is None:
        stats["error"] = "no cuts file"
        return stats

    fat_pct = data.get("overall_fat_percentage", 0)
    if fat_pct < min_fat:
        stats["skipped"] = len(data.get("cuts", []))
        stats["error"] = f"fat {fat_pct}% < threshold {min_fat}%"
        return stats

    cuts = data.get("cuts", [])
    if not cuts:
        stats["error"] = "no cuts in file"
        return stats

    # Load chapter text
    ch_path = chapter_path(chapter_num)
    if not ch_path.exists():
        stats["error"] = f"{ch_path.name} not found"
        return stats

    text = ch_path.read_text(encoding="utf-8")
    original_words = len(text.split())

    for cut in cuts:
        quote = cut.get("quote", "")
        cut_type = cut.get("type", "UNKNOWN")
        reason = cut.get("reason", "")

        # Filter by type
        if type_filter and cut_type not in type_filter:
            stats["skipped"] += 1
            continue

        hit = protected_by(quote, protected or [])
        if hit:
            stats["protected"] += 1
            print(f"  PROTECT [{cut_type}] {quote[:40]!r} touches protected line: {hit[:40]!r}")
            continue

        # REWRITE cuts need replacement prose, not deletion — leave them
        # for the by-hand pass the skill runs after this script.
        if cut.get("action") == "REWRITE":
            stats["skipped"] += 1
            if not dry_run:
                rewrite = cut.get("rewrite") or ""
                shown = (repr(rewrite[:80]) if rewrite else
                         "(no rewrite supplied — the cuts JSON is malformed for a REWRITE)")
                print(f"  SKIP [REWRITE] REWRITE cuts are applied by hand — "
                      f"rewrite: {shown}  (quote: {quote[:40]!r})")
            continue

        # Skip short quotes
        if len(quote.strip()) < MIN_QUOTE_LEN:
            stats["skipped"] += 1
            if not dry_run:
                print(f"  SKIP [{cut_type}] quote too short ({len(quote.strip())} chars)")
            continue

        if dry_run:
            preview = quote[:80].replace("\n", "\\n")
            if len(quote) > 80:
                preview += "..."
            words = len(quote.split())
            print(f"  CUT  [{cut_type}] ~{words}w: {preview}")
            print(f"        reason: {reason}")
            stats["applied"] += 1
            stats["words_removed"] += words
            continue

        # Apply the cut
        new_text, success, fail_reason = find_and_remove(text, quote)
        if success:
            words_cut = len(quote.split())
            stats["applied"] += 1
            stats["words_removed"] += words_cut
            text = new_text
            preview = quote[:60].replace("\n", "\\n")
            if len(quote) > 60:
                preview += "..."
            print(f"  CUT  [{cut_type}] ~{words_cut}w: {preview}")
        else:
            stats["failed"] += 1
            preview = quote[:60].replace("\n", "\\n")
            if len(quote) > 60:
                preview += "..."
            print(f"  FAIL [{cut_type}] {fail_reason}: {preview}")

    # Write back
    if not dry_run and stats["applied"] > 0:
        text = collapse_blank_lines(text)
        ch_path.write_text(text, encoding="utf-8")
        new_words = len(text.split())
        print(f"  SAVED {ch_path.name}: {original_words} -> {new_words} words")

    return stats


def main():
    parser = argparse.ArgumentParser(
        description="Apply adversarial edit cuts to chapter files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python apply_cuts.py 12\n"
            "  python apply_cuts.py all --types OVER-EXPLAIN REDUNDANT\n"
            "  python apply_cuts.py all --min-fat 17\n"
            "  python apply_cuts.py all --dry-run\n"
            "  python apply_cuts.py --verify-protected edit_logs/protected.md\n"
        ),
    )
    parser.add_argument(
        "chapter",
        nargs="?",
        help="Chapter number (e.g. 12) or 'all' to process every chapter. "
             "Omitted only with --verify-protected.",
    )
    parser.add_argument(
        "--types",
        nargs="+",
        metavar="TYPE",
        choices=sorted(VALID_TYPES),
        help=f"Only apply cuts of these types. Choices: {', '.join(sorted(VALID_TYPES))}",
    )
    parser.add_argument(
        "--min-fat",
        type=int,
        default=0,
        metavar="PCT",
        help="Only process chapters with overall_fat_percentage >= this value.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be cut without modifying files.",
    )
    parser.add_argument(
        "--protect-file",
        type=Path,
        metavar="PATH",
        help="Newline-delimited substrings that must never be cut; a cut "
             "whose quote contains one (or is contained by one) is skipped "
             "and reported as PROTECT.",
    )
    parser.add_argument(
        "--verify-protected",
        type=Path,
        metavar="PATH",
        help="Report which lines in this protect file the manuscript still "
             "contains (FOUND) and which it does not (NOT FOUND); exit 1 if "
             "any NOT FOUND. Applies nothing; the chapter argument is ignored.",
    )
    args = parser.parse_args()

    if args.verify_protected is not None:
        if not args.verify_protected.exists():
            parser.error(f"--verify-protected {args.verify_protected} not found")
        if not CHAPTERS_DIR.is_dir():
            parser.error("no chapters/ directory here — run from the project directory")
        found, not_found = verify_protected(load_protected(args.verify_protected))
        print(f"=== verify-protected {args.verify_protected}: "
              f"{len(found)} found, {len(not_found)} not found ===\n")
        print(f"FOUND ({len(found)}):")
        for line in found:
            print(f"  {line}")
        print(f"\nNOT FOUND ({len(not_found)}) — re-quote from the current manuscript:")
        for line in not_found:
            print(f"  {line}")
        sys.exit(1 if not_found else 0)

    if args.chapter is None:
        parser.error("a chapter number or 'all' is required "
                     "(only --verify-protected runs without one)")

    type_filter = set(args.types) if args.types else None
    if args.protect_file is not None and not args.protect_file.exists():
        parser.error(f"--protect-file {args.protect_file} not found; build it "
                     "(revise Diagnose step 2) or omit it")
    protected = load_protected(args.protect_file)

    # Determine which chapters to process
    if args.chapter.lower() == "all":
        chapters = discover_chapters()
        if not chapters:
            print("No cuts files found in edit_logs/")
            sys.exit(1)
        warn_if_cuts_span_cycles()
    else:
        try:
            chapters = [int(args.chapter)]
        except ValueError:
            parser.error(f"Invalid chapter: {args.chapter!r} (use a number or 'all')")

    # Banner
    mode = "DRY RUN" if args.dry_run else "APPLY"
    type_info = f", types={','.join(sorted(type_filter))}" if type_filter else ""
    fat_info = f", min-fat={args.min_fat}%" if args.min_fat > 0 else ""
    print(f"=== apply_cuts [{mode}] chapters={len(chapters)}{type_info}{fat_info} ===\n")

    # Aggregate stats
    totals = {"applied": 0, "failed": 0, "skipped": 0, "protected": 0, "words_removed": 0}

    for ch_num in chapters:
        label = f"ch{ch_num:02d}"
        print(f"--- {label} ---")
        stats = process_chapter(ch_num, type_filter, args.min_fat, args.dry_run, protected)
        if stats["error"]:
            print(f"  {stats['error']}")
        for k in totals:
            totals[k] += stats[k]
        print()

    # Summary
    print("=" * 50)
    print(f"Applied: {totals['applied']}  |  Failed: {totals['failed']}  |  "
          f"Skipped: {totals['skipped']}  |  Protected: {totals['protected']}")
    print(f"Words removed: ~{totals['words_removed']}")
    if args.dry_run:
        print("(dry run — no files were modified)")
    print("=" * 50)

    if totals["failed"] > 0:
        sys.exit(2)


if __name__ == "__main__":
    main()
