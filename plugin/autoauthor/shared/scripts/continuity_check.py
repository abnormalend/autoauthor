#!/usr/bin/env python3
"""List every number a chapter states and whether a fact-bearing document
states it too.

Usage (from the project directory):
  python continuity_check.py chapters/ch_04.md
  python continuity_check.py chapters/ch_*.md
  python continuity_check.py chapters/ch_04.md --facts outline.md canon.md

Why this exists. On one drafting run the weakest dimension in three of four
chapters was canon_compliance, and every violation the judges raised was a
clock time or a bare number — a character read a block before the window
opened, an age off by eight years, a distance wrong by orders of magnitude.
All eight were derivable from the outline's fact table. slop_score.py runs
mechanically on every chapter and catches diction; nothing ran on facts.

What it does. Extracts from the chapter every clock time (`04:02`), every
digit-run (`2091`, `1,200`, `0.98`), and every number word or hyphenated
number word phrase (`sixty`, `twenty-six`, `eighty`), then looks for the
same value in the fact-bearing documents that exist — by default
outline.md, canon.md, world.md, characters.md, whichever are present. It
prints two lists: FOUND and NOT FOUND, and exits 1 if NOT FOUND is
non-empty.

What it does not do. It cannot tell a legitimate invention ("she counted
eleven steps") from a contradiction, and it does not try. It hands the
drafter a short list to eyeball before the judge is dispatched. Number
words below MIN_WORD_VALUE are skipped because "one" and "two" are
articles in disguise; digit forms are never skipped.
"""
import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

DEFAULT_FACT_FILES = ("outline.md", "canon.md", "world.md", "characters.md")
MIN_WORD_VALUE = 3

UNITS = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11,
    "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
    "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19,
}
TENS = {
    "twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60,
    "seventy": 70, "eighty": 80, "ninety": 90,
}
SCALES = {"hundred": 100, "thousand": 1000, "million": 1_000_000}
NUMBER_WORDS = set(UNITS) | set(TENS) | set(SCALES)

CLOCK_RE = re.compile(r"\b(\d{1,2}:\d{2})\b")
DIGITS_RE = re.compile(r"(?<![\d:])(\d+(?:[.,]\d+)*)(?![\d:])")
_WORD_ALT = "(?:" + "|".join(sorted(NUMBER_WORDS, key=len, reverse=True)) + ")"
_AFTER_SCALE = "(?:" + "|".join(f"(?<={w})" for w in SCALES) + ")"
# "and" joins only after a scale word: "one hundred and twenty" is one
# number, "eight and eighty" is two.
WORDS_RE = re.compile(
    r"\b(" + _WORD_ALT +
    r"(?:[-\s]" + _WORD_ALT + r"|" + _AFTER_SCALE + r"\s+and\s+" + _WORD_ALT +
    r")*)\b", re.IGNORECASE)
# Chapter and scene headers carry ordinals, not facts; a heading that is
# itself a clock ("### 14:02") is a fact the chapter states.
SKIP_HEADING_RE = re.compile(r"^#+\s*(?:chapter|ch\.?|scene)\b|^#\s", re.IGNORECASE)


@dataclass(frozen=True)
class Number:
    key: object      # "04:02" for clocks, int/float for values
    text: str        # as written in the chapter
    line: int


def words_to_int(phrase):
    """'twenty-six' -> 26, 'two hundred' -> 200, 'one hundred and twenty' -> 120.

    Returns None if unparsable, including joins English does not make:
    a units or tens word directly after another units or tens word
    ("nineteen eighty", "twenty ten") — the one exception being a unit
    below ten after a tens word ("twenty-six") — or "and" anywhere but
    after a scale word. Refusing is safer than a wrong key — "nineteen
    eighty" once came out as 103.
    """
    total, current = 0, 0
    prev = None
    for w in re.split(r"[-\s]+", phrase.lower()):
        if w == "and":
            if prev not in SCALES:
                return None
        elif w in UNITS or w in TENS:
            joins_number = prev in UNITS or prev in TENS
            if joins_number and not (prev in TENS and w in UNITS and UNITS[w] < 10):
                return None
            current += UNITS.get(w) or TENS.get(w) or 0
        elif w in SCALES:
            current = max(current, 1) * SCALES[w]
            if SCALES[w] >= 1000:
                total += current
                current = 0
        else:
            return None
        prev = w
    return total + current


def _clock_key(text):
    """'4:02' and '04:02' are the same time."""
    h, mm = text.split(":")
    return f"{int(h):02d}:{mm}"


def _digit_key(text):
    cleaned = text.replace(",", "")
    try:
        return float(cleaned) if "." in cleaned else int(cleaned)
    except ValueError:
        return None


def numbers_in(text, min_word_value=MIN_WORD_VALUE):
    """Every number the text states, deduplicated by (key, text)."""
    found = {}
    for lineno, line in enumerate(text.splitlines(), 1):
        if SKIP_HEADING_RE.match(line.lstrip()):
            continue  # "# Chapter 4" is not a fact the chapter states
        for m in CLOCK_RE.finditer(line):
            key = _clock_key(m.group(1))
            found.setdefault((key, m.group(1)), Number(key, m.group(1), lineno))
        stripped = CLOCK_RE.sub(" ", line)
        for m in DIGITS_RE.finditer(stripped):
            key = _digit_key(m.group(1))
            if key is not None:
                found.setdefault((key, m.group(1)), Number(key, m.group(1), lineno))
        for m in WORDS_RE.finditer(stripped):
            value = words_to_int(m.group(1))
            if value is None or value < min_word_value:
                continue
            found.setdefault((value, m.group(1)), Number(value, m.group(1), lineno))
    return list(found.values())


def fact_keys(paths):
    keys = set()
    for p in paths:
        if p.exists():
            keys.update(n.key for n in numbers_in(p.read_text(encoding="utf-8"), 0))
    return keys


def check(chapter_path, fact_paths):
    text = chapter_path.read_text(encoding="utf-8")
    facts = fact_keys(fact_paths)
    numbers = sorted(numbers_in(text), key=lambda n: (n.line, n.text))
    found = [n for n in numbers if n.key in facts]
    missing = [n for n in numbers if n.key not in facts]
    return found, missing


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("chapters", nargs="+", help="chapter files to check")
    parser.add_argument("--facts", nargs="+", metavar="FILE",
                        help="fact-bearing files (default: whichever of "
                             f"{', '.join(DEFAULT_FACT_FILES)} exist in CWD)")
    args = parser.parse_args(argv)

    fact_paths = ([Path(f) for f in args.facts] if args.facts
                  else [Path(f) for f in DEFAULT_FACT_FILES])
    present = [p for p in fact_paths if p.exists()]
    if not present:
        print("ERROR: no fact-bearing files found "
              f"(looked for {', '.join(str(p) for p in fact_paths)})", file=sys.stderr)
        return 2

    absent = [ch for ch in args.chapters if not Path(ch).exists()]
    if absent:
        print(f"ERROR: chapter file not found: {', '.join(absent)}", file=sys.stderr)
        return 2

    any_missing = False
    for ch in args.chapters:
        found, missing = check(Path(ch), present)
        print(f"=== {ch} — facts from {', '.join(p.name for p in present)} ===")
        print(f"FOUND ({len(found)}):")
        for n in found:
            print(f"  L{n.line:<4} {n.text}")
        print(f"NOT FOUND ({len(missing)}) — check each against the fact table:")
        for n in missing:
            print(f"  L{n.line:<4} {n.text}")
        print()
        any_missing = any_missing or bool(missing)
    return 1 if any_missing else 0


if __name__ == "__main__":
    sys.exit(main())
