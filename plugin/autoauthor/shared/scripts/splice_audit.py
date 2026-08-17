#!/usr/bin/env python3
"""Audit chapters for splice damage after a mechanical cut pass.

Usage (from the project directory):
  python splice_audit.py chapters/ch_*.md                    # compare against git HEAD
  python splice_audit.py chapters/ch_04.md --before-dir /tmp/precut
  python splice_audit.py chapters/ch_*.md --ref cycle-3-start  # any git ref

apply_cuts.py deletes quoted spans mid-paragraph. A cut that removes a
trailing or interior sentence can leave a paragraph ending on a comma,
ending with no terminal punctuation, two speeches glued into one line, a
doubled comma, or stray whitespace at either end. Neither the word count
nor the slop scorer sees any of it. This audits ONLY paragraphs that
changed between the before-text and the current text — unchanged prose is
not this pass's damage and would drown the signal — and exits 1 if it
found anything.

The checks, each named in the output so a repair can be logged by kind:
  ends-on-comma            paragraph ends in , or ;
  no-terminal-punctuation  paragraph ends without . ! ? … a closing quote,
                           a closing bracket, or an em-dash
  double-space             two spaces inside a paragraph
  doubled-comma            ", ," with any whitespace between
  empty-quotes             "" or " " — an emptied speech
  space-before-punct       whitespace before , . ; : ! ?
  doubled-word             "the the", case-insensitive
  glued-sentence           [,;] then space then a capitalised word that did
                           NOT follow a comma or semicolon anywhere in the
                           before-text — proper nouns after commas are
                           learned from the before-text, so "left, Kalei
                           said" passes and "down,  She called" does not
  leading-whitespace       paragraph starts with a space
  trailing-whitespace      paragraph ends with a space (this one survived
                           a whole cycle by eye)

Expect one or two false positives from intentional oddities; check them,
then leave them.
"""
import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

TERMINAL = '.!?…"”’\')*_—–'


@dataclass(frozen=True)
class Finding:
    kind: str
    para: int
    text: str


def paragraphs(text):
    """Non-empty, non-heading paragraphs with their index in the raw split."""
    out = []
    for i, p in enumerate(text.split("\n\n")):
        raw = p.rstrip("\n")
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        out.append((i, raw))
    return out


def _capitalised_after_comma(text):
    """Words that legitimately follow , or ; in the before-text — proper
    nouns, 'I', dialogue tags with names — so they are not glued sentences."""
    return {m.group(1) for m in re.finditer(r"[,;]\s+([A-Z][\w'’-]*)", text)}


def audit_paragraph(idx, raw, allow):
    findings = []
    stripped = raw.strip()
    add = lambda kind: findings.append(Finding(kind, idx, stripped[:80]))  # noqa: E731

    if raw != raw.lstrip(" \t"):
        add("leading-whitespace")
    if raw != raw.rstrip(" \t"):
        add("trailing-whitespace")
    if stripped.endswith((",", ";")):
        add("ends-on-comma")
    elif stripped and stripped[-1] not in TERMINAL:
        add("no-terminal-punctuation")
    if "  " in stripped:
        add("double-space")
    if re.search(r",\s*,", stripped):
        add("doubled-comma")
    if re.search(r'"\s*"', stripped) or re.search(r"“\s*”", stripped):
        add("empty-quotes")
    if re.search(r"\s[,.;:!?]", stripped):
        add("space-before-punct")
    if re.search(r"\b(\w+)\s+\1\b", stripped, re.IGNORECASE):
        add("doubled-word")
    for m in re.finditer(r"[,;]\s+([A-Z][\w'’-]*)", stripped):
        if m.group(1) not in allow and m.group(1) != "I":
            add("glued-sentence")
            break
    return findings


def audit(before, after):
    """Findings in paragraphs of `after` that do not appear verbatim in `before`."""
    before_paras = {raw.strip() for _, raw in paragraphs(before)}
    allow = _capitalised_after_comma(before)
    findings = []
    for idx, raw in paragraphs(after):
        if raw.strip() in before_paras and raw == raw.strip():
            continue
        findings.extend(audit_paragraph(idx, raw, allow))
    return findings


def before_text(path, before_dir, ref):
    if before_dir is not None:
        p = Path(before_dir) / Path(path).name
        return p.read_text(encoding="utf-8") if p.exists() else ""
    r = subprocess.run(["git", "show", f"{ref}:{path}"],
                       capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("chapters", nargs="+")
    parser.add_argument("--before-dir", metavar="DIR",
                        help="directory holding the pre-cut copies (same filenames)")
    parser.add_argument("--ref", default="HEAD",
                        help="git ref to read the pre-cut text from (default HEAD)")
    args = parser.parse_args(argv)

    total = 0
    for ch in args.chapters:
        after = Path(ch).read_text(encoding="utf-8")
        before = before_text(ch, args.before_dir, args.ref)
        findings = audit(before, after)
        total += len(findings)
        print(f"=== {ch}: {len(findings)} finding(s) ===")
        for f in findings:
            print(f"  [{f.kind}] para {f.para}: {f.text}")
    print(f"\n{total} finding(s) total")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
