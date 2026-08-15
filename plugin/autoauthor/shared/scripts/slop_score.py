#!/usr/bin/env python3
"""Mechanical slop scorer — regex-based AI-tell detection. No LLM, no network.

Usage:
  python3 slop_score.py chapters/ch_01.md [more files...]
  python3 slop_score.py chapters/*.md

Prints a JSON report to stdout:
  {"files": [{"path": ..., <slop_score() dict fields>}...],
   "summary": {"worst_file": ..., "max_penalty": N, "mean_penalty": N}}

The slop_penalty (0-10) is subtracted from LLM-judge chapter scores by the
autoauthor skills. Verbatim port of the mechanical scorer from the original
autoauthor pipeline's evaluation tooling.
"""
import argparse
import json
import re
import sys
from pathlib import Path

TIER1_BANNED = [
    "delve", "utilize", "leverage", "facilitate", "elucidate",
    "embark", "endeavor", "encompass", "multifaceted", "tapestry",
    "paradigm", "synergy", "synergize", "holistic", "catalyze",
    "catalyst", "juxtapose", "myriad", "plethora",
]

# Tier 1 entries the token loop above cannot see, because they are more than
# one word. Scored in the same bucket and at the same weight — a phrase is
# not a lesser offence than a word, it is only harder to match.
#
# The hyphen is required. `load bearing` unhyphenated is not reliably the
# metaphor — "the load bearing down on her" is ordinary prose, and a scorer
# that penalises it teaches the drafter to avoid a real sentence. The `\s*`
# is there because chapters are hard-wrapped and the break lands on the
# hyphen, which is exactly where a wrap prefers to land.
TIER1_PHRASES = [
    r"load-\s*bearing",
    r"bear(?:s|ing)? the load",
]

TIER2_SUSPICIOUS = [
    "robust", "comprehensive", "seamless", "seamlessly", "cutting-edge",
    "innovative", "streamline", "empower", "foster", "enhance", "elevate",
    "optimize", "pivotal", "intricate", "profound", "resonate",
    "underscore", "harness", "cultivate", "bolster", "galvanize",
    "cornerstone", "game-changer", "scalable",
]

TIER3_FILLER = [
    r"it'?s worth noting that",
    r"it'?s important to note that",
    r"^importantly,?\s",
    r"^notably,?\s",
    r"^interestingly,?\s",
    r"let'?s dive into",
    r"let'?s explore",
    r"as we can see",
    r"^furthermore,?\s",
    r"^moreover,?\s",
    r"^additionally,?\s",
    r"in today'?s .*(fast-paced|digital|modern)",
    r"at the end of the day",
    r"it goes without saying",
    r"when it comes to",
    r"one might argue that",
    r"not just .+, but",
]

TRANSITION_OPENERS = [
    "however", "furthermore", "additionally", "moreover",
    "nevertheless", "consequently", "nonetheless", "similarly",
]

# Fiction-specific AI tells (prose clichés that betray machine origin)
FICTION_AI_TELLS = [
    r"a sense of \w+",
    r"couldn'?t help but feel",
    r"the weight of \w+",
    r"the air was thick with",
    r"eyes widened",
    r"a wave of \w+ washed over",
    r"a pang of \w+",
    r"heart pounded in (?:his|her|their) chest",
    r"(?:raven|dark|golden|silver) (?:hair|tresses) (?:spilled|cascaded|tumbled|fell)",
    r"piercing (?:blue|green|gray|grey|dark) eyes",
    r"a knowing (?:smile|grin|look|glance)",
    r"(?:he|she|they) felt a (?:surge|rush|wave|pang|flicker) of",
    r"the silence (?:was|hung|stretched|grew) (?:heavy|thick|oppressive|deafening)",
    r"let out a breath (?:he|she|they) didn'?t (?:know|realize)",
    r"something (?:dark|ancient|primal|unnamed) stirred",
]

# Structural AI tics -- rhetorical formulas that betray AI composition
STRUCTURAL_AI_TICS = [
    r"(?:I'm|I am) not (?:saying|asking|suggesting) .{3,40}(?:I'm|I am) (?:saying|asking|suggesting)",  # "I'm not saying X. I'm saying Y"
    r"(?:which|that) means either .{3,40} or ",  # "which means either X, or Y"
    r"[Tt]here'?s a (?:difference|distinction)\.",  # formula capper
    r"[Tt]hose are (?:different|not the same) things\.",  # formula capper
    r"[Nn]ot (?:just|merely|simply) .{3,40}, but ",  # "not just X, but Y"
    r"[Nn]ot (?:from|by|because of) .{3,40}, but (?:from|by|because)",  # "not from X, but from Y" in narration
]

# Show-don't-tell detectors: emotion TELLING patterns
TELLING_PATTERNS = [
    r"\b(?:he|she|they|I|we|[A-Z]\w+) (?:felt|was|seemed|looked|appeared) (?:angry|sad|happy|scared|nervous|excited|jealous|guilty|anxious|lonely|desperate|furious|terrified|elated|miserable|hopeful|confused|relieved|horrified|disgusted|ashamed|proud|bitter|defeated|triumphant)\b",
    r"\b(?:angrily|sadly|happily|nervously|excitedly|desperately|furiously|anxiously|guiltily|bitterly|wearily|miserably)\b",
]


def load_genre_banned(path=None):
    """Extra banned phrases from a genre pack's '## Drafting Rules' section.

    A pack lists them one per line under a `BANNED PHRASES:` marker inside
    that section. Every genre grows its own stock diction that the general
    anti-slop tiers do not cover, and only the pack knows what it is.

    Returns [] when no pack is given, the file is unreadable, or the marker
    is absent — a genre without its own slop vocabulary is the normal case,
    and scoring must never fail because of genre resolution.
    """
    if path is None:
        return []
    try:
        text = Path(path).read_text(encoding="utf-8")
    except OSError:
        return []
    match = re.search(r"^BANNED PHRASES:\s*$(.*?)(?=^##\s|\Z)",
                      text, re.M | re.S)
    if not match:
        return []
    phrases = []
    for line in match.group(1).splitlines():
        phrase = line.strip().lstrip("-").strip().lower()
        if phrase:
            phrases.append(phrase)
    return phrases


def slop_score(text, genre_banned=()):
    """
    Mechanical slop detection. Returns a dict with:
      - tier1_hits: list of (word, count)
      - tier2_hits: list of (word, count)
      - tier3_hits: list of (pattern, count)
      - em_dash_density: em dashes per 1000 words
      - sentence_length_cv: coefficient of variation (higher = more human)
      - transition_opener_ratio: fraction of paragraphs starting with transitions
      - slop_penalty: 0-10 deduction (0 = clean, 10 = pure slop)
    """
    words = text.lower().split()
    word_count = len(words) or 1

    # Chapter files are hard-wrapped prose, so any multi-word phrase can
    # straddle a line break. Collapse whitespace once, up front, and match
    # every phrase scan against this rather than the raw text — otherwise the
    # longer the phrase the likelier it is silently missed, which undercounts
    # exactly the constructions the phrase lists exist to catch.
    lowered = re.sub(r"\s+", " ", text.lower())

    # Tier 1
    tier1_hits = []
    for w in TIER1_BANNED:
        c = sum(1 for token in words if token.strip(".,;:!?\"'()") == w)
        if c > 0:
            tier1_hits.append((w, c))
    for pattern in TIER1_PHRASES:
        c = len(re.findall(pattern, lowered))
        if c > 0:
            tier1_hits.append((pattern, c))

    # Tier 2 -- count per paragraph, flag clusters
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    tier2_hits = []
    tier2_cluster_count = 0
    for w in TIER2_SUSPICIOUS:
        c = sum(1 for token in words if token.strip(".,;:!?\"'()") == w)
        if c > 0:
            tier2_hits.append((w, c))
    for para in paragraphs:
        para_lower = para.lower()
        hits_in_para = sum(1 for w in TIER2_SUSPICIOUS if w in para_lower)
        if hits_in_para >= 3:
            tier2_cluster_count += 1

    # Tier 3
    tier3_hits = []
    for pattern in TIER3_FILLER:
        matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
        if matches:
            tier3_hits.append((pattern, len(matches)))

    # Em dash density
    em_dashes = text.count("—") + text.count("--")
    em_dash_density = (em_dashes / word_count) * 1000

    # Sentence length variation (coefficient of variation)
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if len(s.strip().split()) > 2]
    if len(sentences) > 2:
        lengths = [len(s.split()) for s in sentences]
        mean_len = sum(lengths) / len(lengths)
        variance = sum((l - mean_len) ** 2 for l in lengths) / len(lengths)
        std_len = variance ** 0.5
        sentence_length_cv = std_len / mean_len if mean_len > 0 else 0
    else:
        sentence_length_cv = 0.5  # not enough data, assume OK

    # Transition opener ratio
    transition_starts = 0
    for para in paragraphs:
        first_word = para.split()[0].lower().strip(".,;:!?\"'()") if para.split() else ""
        if first_word in TRANSITION_OPENERS:
            transition_starts += 1
    transition_ratio = transition_starts / len(paragraphs) if paragraphs else 0

    # Fiction AI tells
    fiction_tells = []
    for pattern in FICTION_AI_TELLS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            fiction_tells.append((pattern[:40], len(matches)))
    fiction_tell_count = sum(c for _, c in fiction_tells)

    # Show-don't-tell violations
    telling_count = 0
    for pattern in TELLING_PATTERNS:
        telling_count += len(re.findall(pattern, text, re.IGNORECASE))

    # Structural AI tics (rhetorical formulas)
    structural_tics = []
    for pattern in STRUCTURAL_AI_TICS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            structural_tics.append((pattern[:40], len(matches)))
    structural_tic_count = sum(c for _, c in structural_tics)

    # Composite penalty (0 = clean, 10 = disaster)
    # Genre-specific banned phrases. Multi-word, so matched as substrings
    # rather than through the token loop above, against the collapsed text
    # prepared at the top of the scan.
    genre_hits = []
    for phrase in genre_banned:
        normalized = re.sub(r"\s+", " ", phrase.strip())
        c = lowered.count(normalized)
        if c > 0:
            genre_hits.append((phrase, c))

    penalty = 0.0
    penalty += min(len(genre_hits) * 1.5, 4.0)       # genre banned: up to 4 pts
    penalty += min(len(tier1_hits) * 1.5, 4.0)       # tier1: up to 4 pts
    penalty += min(tier2_cluster_count * 1.0, 2.0)    # tier2 clusters: up to 2 pts
    penalty += min(sum(c for _, c in tier3_hits) * 0.3, 2.0)  # tier3: up to 2 pts
    if em_dash_density > 15:
        penalty += min((em_dash_density - 15) * 0.3, 1.0)  # em dashes: up to 1 pt (threshold raised for voice)
    if sentence_length_cv < 0.3:
        penalty += 1.0  # uniform sentence length: 1 pt
    if transition_ratio > 0.3:
        penalty += min(transition_ratio * 2, 1.0)  # transition abuse: up to 1 pt
    penalty += min(fiction_tell_count * 0.3, 2.0)     # fiction AI tells: up to 2 pts
    penalty += min(telling_count * 0.2, 1.5)          # show-don't-tell: up to 1.5 pts
    penalty += min(structural_tic_count * 0.5, 2.0)   # structural AI tics: up to 2 pts

    penalty = min(penalty, 10.0)

    return {
        "genre_banned_hits": genre_hits,
        "tier1_hits": tier1_hits,
        "tier2_hits": tier2_hits,
        "tier2_clusters": tier2_cluster_count,
        "tier3_hits": tier3_hits,
        "fiction_ai_tells": fiction_tells,
        "structural_ai_tics": structural_tics,
        "telling_violations": telling_count,
        "em_dash_density": round(em_dash_density, 2),
        "sentence_length_cv": round(sentence_length_cv, 3),
        "transition_opener_ratio": round(transition_ratio, 3),
        "slop_penalty": round(penalty, 2),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="+", help="chapter files to score")
    parser.add_argument(
        "--genre-pack", default=None,
        help="genre pack whose BANNED PHRASES extend the Tier 1 scan")
    args = parser.parse_args()

    genre_banned = load_genre_banned(args.genre_pack)
    reports = []
    for p in args.files:
        text = Path(p).read_text()
        r = slop_score(text, genre_banned=genre_banned)
        r["path"] = str(p)
        reports.append(r)
    penalties = [r["slop_penalty"] for r in reports]
    worst = max(reports, key=lambda r: r["slop_penalty"])
    print(json.dumps({
        "files": reports,
        "summary": {
            "worst_file": worst["path"],
            "max_penalty": max(penalties),
            "mean_penalty": round(sum(penalties) / len(penalties), 2),
        },
    }, indent=2))


if __name__ == "__main__":
    main()
