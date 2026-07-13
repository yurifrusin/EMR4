"""Lossless language normalization for Bernie receptionist utterances.

The normalizer produces a ``NormalizedUtterance`` that preserves the original
text while providing a derived matching view.  Normalization is one-way
(NFKC, whitespace-collapsed, case-folded, punctuation-normalised) but always
tracks the original form and source spans so that evidence can be traced back.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from typing import Dict, Tuple

# ---------------------------------------------------------------------------
# Number-word map (supports the coverage lattice's language_form dimension)
# ---------------------------------------------------------------------------
_NUMBER_WORDS: Dict[str, str] = {
    "zero": "0",
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
    "ten": "10",
    "eleven": "11",
    "twelve": "12",
    "thirteen": "13",
    "fourteen": "14",
    "fifteen": "15",
    "sixteen": "16",
    "seventeen": "17",
    "eighteen": "18",
    "nineteen": "19",
    "twenty": "20",
    "thirty": "30",
    "forty": "40",
    "fifty": "50",
    "sixty": "60",
}

# Time form patterns in order of precedence (longest match first).
_TIME_PATTERNS = [
    # 12-hour with colon or dot: 3:00pm, 3.00pm
    re.compile(
        r"(?P<hour>\d{1,2})[:.](?P<min>\d{2})\s*(?P<ampm>am|pm)\b", re.IGNORECASE
    ),
    # 24-hour: 15:00
    re.compile(r"(?P<hour>\d{2}):(?P<min>\d{2})\b"),
    # 12-hour without minutes: 3pm, 3 pm, 3.30pm (handled above)
    re.compile(r"(?P<hour>\d{1,2})\s*(?P<ampm>am|pm)\b", re.IGNORECASE),
]

_OPERATOR_WORDS: frozenset[str] = frozenset({
    "at",
    "before",
    "after",
    "from",
    "to",
    "not",
    "without",
    "around",
    "about",
    "between",
    "and",
})


@dataclass
class NormalizedUtterance:
    """The result of lossless normalisation of a receptionist utterance.

    Fields:
        original:  The untouched original utterance.
        normalized:  Unicode NFKC, whitespace-collapsed, case-folded,
                     punctuation-normalised form.
        time_forms:  Detected time fragments mapped to canonical HH:MM.
        number_forms:  Detected number words mapped to digit form.
        source_spans:  Field -> (start, end) character offsets in *original*.
    """

    original: str
    normalized: str
    time_forms: Dict[str, str] = field(default_factory=dict)
    number_forms: Dict[str, str] = field(default_factory=dict)
    source_spans: Dict[str, Tuple[int, int]] = field(default_factory=dict)


def _collapse_whitespace(text: str) -> str:
    """Collapse runs of whitespace characters to a single space."""
    return re.sub(r"\s+", " ", text)


def _normalize_punctuation(text: str) -> str:
    """Normalise repeated punctuation marks.

    .. -> ., !! -> !, ?? -> ?, ,, -> ,  (single pass).
    """
    text = re.sub(r"\.{2,}", ".", text)
    text = re.sub(r"!{2,}", "!", text)
    text = re.sub(r"\?{2,}", "?", text)
    text = re.sub(r",{2,}", ",", text)
    return text


def _detect_time_forms(original: str) -> Dict[str, str]:
    """Detect time-like fragments in *original* and map them to HH:MM.

    Returns:
        dict mapping the detected fragment string -> canonical HH:MM.
    """
    detected: Dict[str, str] = {}
    for pat in _TIME_PATTERNS:
        for m in pat.finditer(original):
            fragment = m.group(0).strip()
            if fragment in detected:
                continue
            hour = int(m.group("hour"))
            minute = int(m.group("min")) if m.lastgroup and "min" in m.groupdict() and m.group("min") else 0
            ampm = m.group("ampm").lower() if "ampm" in m.groupdict() and m.group("ampm") else None
            if ampm == "pm" and hour != 12:
                hour += 12
            elif ampm == "am" and hour == 12:
                hour = 0
            detected[fragment] = f"{hour:02d}:{minute:02d}"
    return detected


def _detect_number_words(text: str) -> Dict[str, str]:
    """Detect number-word fragments and map them to digit form.

    Operates on the already-normalised text to keep detection simple.
    """
    detected: Dict[str, str] = {}
    for word, digit in _NUMBER_WORDS.items():
        # Look for whole-word matches (word boundary)
        pattern = re.compile(rf"\b{re.escape(word)}\b", re.IGNORECASE)
        for m in pattern.finditer(text):
            fragment = m.group(0)
            if fragment not in detected:
                detected[fragment] = digit
    return detected


def _compute_source_spans(
    original: str, time_forms: Dict[str, str], number_forms: Dict[str, str]
) -> Dict[str, Tuple[int, int]]:
    """Compute (start, end) character offsets in *original* for each detected form."""
    spans: Dict[str, Tuple[int, int]] = {}
    for fragment in time_forms:
        idx = original.find(fragment)
        if idx != -1:
            spans.setdefault(f"time:{fragment}", (idx, idx + len(fragment)))
    for fragment in number_forms:
        idx = original.lower().find(fragment.lower())
        if idx != -1:
            spans.setdefault(f"number:{fragment}", (idx, idx + len(fragment)))
    return spans


def normalize_utterance(original: str) -> NormalizedUtterance:
    """Lossless normalisation of a receptionist utterance.

    Rules applied in order:
        1.  Unicode NFKC.
        2.  Collapse runs of whitespace.
        3.  Case-fold (lowercase).
        4.  Normalise repeated punctuation.
        5.  Detect time forms -> canonical HH:MM.
        6.  Detect number words -> digit form.
        7.  *Preserve* operator words (at, before, after, …).
        8.  No stop-word removal, stemming, or lemmatization.
    """
    # Step 1-4: produce the normalised string.
    normalized = unicodedata.normalize("NFKC", original)
    normalized = _collapse_whitespace(normalized).strip()
    normalized = normalized.casefold()
    normalized = _normalize_punctuation(normalized)

    # Step 5-6: detections (on the original for time, on normalised for numbers).
    time_forms = _detect_time_forms(original)
    number_forms = _detect_number_words(normalized)

    # Step 7: source spans. Operator evidence is retained as well as detected
    # number/time forms, because negation and open-bound words carry authority.
    source_spans = _compute_source_spans(original, time_forms, number_forms)
    for operator in sorted(_OPERATOR_WORDS):
        for index, match in enumerate(
            re.finditer(rf"\b{re.escape(operator)}\b", original, re.IGNORECASE)
        ):
            source_spans[f"operator:{operator}:{index}"] = match.span()

    return NormalizedUtterance(
        original=original,
        normalized=normalized,
        time_forms=time_forms,
        number_forms=number_forms,
        source_spans=source_spans,
    )
