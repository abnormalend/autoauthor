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

# --- Figurative density ----------------------------------------------------
# Identified from a 0.2.0 draft that ran one figurative construction every 83
# words. Individually most were good; collectively they became the narrator's
# tic, and nothing stood out because everything was reaching.
#
# WHAT THIS MEASURES, precisely: the simile family. Metaphor cannot be
# regexed, and pretending otherwise would be worse than the gap. On the
# motivating chapter a hand count found 31 figures where these patterns find
# 15, so read the density as a PROXY that tracks roughly half the true
# figurative load — the thresholds below are calibrated against the proxy,
# not against the hand count.
#
# Dialogue is excluded before counting. A distinctive speaker's similes
# characterise the speaker and should differ from the narration's; scoring
# them as narration would penalise a book for having a vivid character in it.
FIGURATIVE_CONSTRUCTIONS = {
    # `like` is a verb at least as often as it is a simile marker. Requiring
    # a determiner after it, and refusing a subject pronoun before it, is
    # what separates "like a man selling a car on fire" from "I like the
    # quiet". Precision matters more than recall here: a false positive
    # teaches the drafter to avoid a sentence that was fine.
    "like + noun phrase":
        r"(?<!\bi )(?<!\byou )(?<!\bwe )(?<!\bthey )(?<!\bhe )(?<!\bshe )"
        r"(?<!\bit )(?<!\bwho )(?<!\bwould )"
        r"\blike (?:a|an|the|some|someone|somebody|something|his|her|their)\b",
    "the way + person":
        r"\bthe way (?:a|an|the|some|someone|somebody|people|he|she|they|"
        r"you|his|her|their)\b",
    "as if / as though": r"\bas (?:if|though)\b",
    "as ADJ as": r"\bas [a-z]+ as (?:a|an|the|any)\b",
}

# Straight and typographic quotes both, because chapters carry either.
DIALOGUE_RE = re.compile(r'"[^"]*"|“[^”]*”')

# Per 1000 words of NARRATION. Grounded in a 36-chapter corpus across four
# projects: median 2.9, and the chapter this feature was written for is the
# corpus maximum at 6.9. A threshold of 5.0 penalises the top four chapters,
# all of them from the project the fault was identified in.
#
# Only `extended` is corpus-grounded — every chapter measured was
# novel-length. The tighter numbers below it are a stated judgement, on the
# roadmap's reasoning that a compressed form cannot afford the same ornament
# budget, and they should be re-derived when short-form chapters exist to
# measure.
BAND_FIGURATIVE_THRESHOLD = {
    "compressed": 3.5,
    "intermediate": 4.5,
    "extended": 5.0,
}
DEFAULT_FIGURATIVE_THRESHOLD = 5.0

# A rate needs enough events to be a rate. One figure in an 89-word passage
# computes to 11.6 per 1000 and means nothing — which is exactly what the
# existing clean fixture did the first time this ran, and it was right to.
# The fault being detected is a TIC, and a tic requires repetition: you
# cannot have a monoculture of one. Below this count no penalty applies at
# any density. Five costs nothing in recall — the chapters that motivated
# this feature carry nine to sixteen.
MIN_FIGURES_FOR_DENSITY = 5

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


def load_figurative_threshold(form_pack=None, genre_pack=None, explicit=None):
    """How much ornament this work can afford, most specific source winning.

    An explicit number beats a genre pack, which beats the form's band,
    which falls back to the default. The genre override exists because the
    tolerance genuinely differs by genre — literary fiction carries figures
    a thriller cannot — and only the pack knows its own appetite. A pack
    declares one with a `FIGURATIVE DENSITY: N` line in its Drafting Rules,
    the same forgiving shape as `BANNED PHRASES:`.

    Every lookup fails soft to the next source. Scoring a chapter must never
    fail because a pack is missing, unreadable, or says something strange —
    the scorer runs inside the drafting loop, and a crash there costs a
    chapter.
    """
    if explicit is not None:
        return float(explicit)

    if genre_pack:
        try:
            text = Path(genre_pack).read_text(encoding="utf-8")
            match = re.search(r"^FIGURATIVE DENSITY:\s*([0-9.]+)\s*$", text, re.M)
            if match:
                return float(match.group(1))
        except (OSError, ValueError):
            pass

    if form_pack:
        try:
            text = Path(form_pack).read_text(encoding="utf-8")
            match = re.search(r'"band"\s*:\s*"([a-z]+)"', text)
            if match:
                return BAND_FIGURATIVE_THRESHOLD.get(
                    match.group(1), DEFAULT_FIGURATIVE_THRESHOLD)
        except OSError:
            pass

    return DEFAULT_FIGURATIVE_THRESHOLD


def strip_dialogue(text):
    """Narration only. See FIGURATIVE_CONSTRUCTIONS for why."""
    return DIALOGUE_RE.sub(" ", text)


def figurative_report(text):
    """Count simile-family constructions in the narration.

    Returns (count, per-1000-words, {construction: count}). The breakdown is
    reported but NOT scored, and that is a measured decision rather than an
    omission: the roadmap expected a repeated-construction penalty so that
    monoculture would score worse than the same count spread across varied
    figures, and across the 36-chapter corpus that check INVERTS. The
    motivating chapter repeats its commonest construction 53% of the time
    against a corpus median of 83% — it is more varied than typical, not
    less, and a penalty on repetition would have hit the wrong chapters.

    What distinguishes it is volume. So volume is what this scores, and
    monoculture is left to the judged half, where a reader can see that
    fifteen good figures still add up to a tic.
    """
    narration = strip_dialogue(text)
    words = len(narration.split()) or 1
    counts = {}
    for name, pattern in FIGURATIVE_CONSTRUCTIONS.items():
        found = len(re.findall(pattern, narration, re.IGNORECASE))
        if found:
            counts[name] = found
    total = sum(counts.values())
    return total, (total / words) * 1000, counts


def slop_score(text, genre_banned=(),
               figurative_threshold=DEFAULT_FIGURATIVE_THRESHOLD):
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

    figurative_count, figurative_density, figurative_constructions = \
        figurative_report(text)

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
    if (figurative_count >= MIN_FIGURES_FOR_DENSITY
            and figurative_density > figurative_threshold):
        # Graduated from the threshold rather than stepped at it: the fault
        # is a gradient, and a chapter one figure over the line is not a
        # different kind of chapter from one just under it.
        penalty += min((figurative_density - figurative_threshold) * 0.6, 2.0)

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
        "figurative_count": figurative_count,
        "figurative_density": round(figurative_density, 2),
        "figurative_threshold": figurative_threshold,
        "figurative_constructions": figurative_constructions,
        "sentence_length_cv": round(sentence_length_cv, 3),
        "transition_opener_ratio": round(transition_ratio, 3),
        "slop_penalty": round(penalty, 2),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="+", help="chapter files to score")
    parser.add_argument(
        "--genre-pack", default=None,
        help="genre pack whose BANNED PHRASES extend the Tier 1 scan, and "
             "whose FIGURATIVE DENSITY line overrides the form's threshold")
    parser.add_argument(
        "--form-pack", default=None,
        help="form pack whose band sets the figurative density threshold")
    parser.add_argument(
        "--figurative-threshold", type=float, default=None,
        help="figures per 1000 words of narration before a penalty applies")
    args = parser.parse_args()

    genre_banned = load_genre_banned(args.genre_pack)
    figurative_threshold = load_figurative_threshold(
        form_pack=args.form_pack, genre_pack=args.genre_pack,
        explicit=args.figurative_threshold)
    reports = []
    for p in args.files:
        text = Path(p).read_text()
        r = slop_score(text, genre_banned=genre_banned,
                       figurative_threshold=figurative_threshold)
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
