#!/usr/bin/env python3
"""Validate one or more genre pack files.

Usage:
  python3 validate_genre_pack.py path/to/fantasy.md [more...]
  python3 validate_genre_pack.py "${CLAUDE_PLUGIN_ROOT}/shared/genres/"*.md

Exit 0 if every pack is valid; 1 otherwise, with errors on stdout.
"""
import sys
from pathlib import Path

from genre_pack import PackError, pack_names_in, parse_pack, validate_pack


def main(argv):
    if not argv:
        print("usage: validate_genre_pack.py <pack.md> [more...]",
              file=sys.stderr)
        return 2

    paths = [Path(a) for a in argv]
    # Packs referenced by conflicts_with may live alongside the ones named
    # on the command line, so every sibling .md in each argument's
    # directory counts as known too. There's no separate "add each
    # argument's own stem" step — for any real .md argument, pack_names_in
    # on its own parent directory already includes it.
    known = set()
    for path in paths:
        known |= pack_names_in(path.parent)

    failed = False
    for path in paths:
        try:
            pack = parse_pack(path)
        except PackError as e:
            print(f"FAIL {path}\n  {e}")
            failed = True
            continue
        errors = validate_pack(pack, known_names=known)
        if errors:
            failed = True
            print(f"FAIL {path}")
            for error in errors:
                print(f"  {error}")
        else:
            print(f"OK   {path}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
