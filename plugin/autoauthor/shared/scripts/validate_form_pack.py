#!/usr/bin/env python3
"""Validate one or more form pack files.

Usage:
  python3 validate_form_pack.py path/to/<name>.md [more...]
  python3 validate_form_pack.py "${CLAUDE_PLUGIN_ROOT}/shared/forms/"*.md

The sibling of validate_genre_pack.py, kept separate rather than folded
into it because the two schemas share almost nothing: a form declares a
band, a word range and a gate, and must NOT declare the role, weights or
pillar dimensions that a genre pack is mostly made of. One command that
guessed which kind of pack it was looking at would report a genre pack's
missing `band` as an error.

Exit 0 if every form is valid; 1 otherwise, with errors on stdout.
"""
import sys
from pathlib import Path

from form_pack import TEMPLATE_STEM, parse_form, validate_form
from genre_pack import PackError


def main(argv):
    if not argv:
        print("usage: validate_form_pack.py <form.md> [more...]",
              file=sys.stderr)
        return 2

    failed = False
    for path in [Path(a) for a in argv]:
        if path.stem == TEMPLATE_STEM:
            print(f"SKIP {path} (authoring template, not a form)")
            continue
        try:
            form = parse_form(path)
        except PackError as e:
            print(f"FAIL {path}\n  {e}")
            failed = True
            continue
        errors = validate_form(form)
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
