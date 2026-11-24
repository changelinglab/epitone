"""Thai syllable parsing and representation."""

from dataclasses import dataclass
from typing import Iterator

from epitone.thai.data import (
    ABOVE_VOWELS,
    BELOW_VOWELS,
    CLUSTER_FIRST,
    CLUSTER_SECOND,
    CONSONANTS,
    ConsonantClass,
    FOLLOWING_VOWELS,
    HO_NAM_CONSONANTS,
    LEADING_VOWELS,
    O_NAM_CONSONANTS,
    SONORANT_FINALS,
    TONE_MARKS,
    VOWELS,
    VowelInfo,
    is_consonant,
    is_thai_char,
    is_tone_mark,
    is_vowel_char,
)


@dataclass
class Syllable:
    """Represents a parsed Thai syllable."""

    onset: str
    onset_ipa: str
    consonant_class: ConsonantClass
    vowel_chars: str
    vowel_ipa: str
    vowel_is_long: bool
    tone_mark: str | None
    coda: str
    coda_ipa: str
    raw: str

    @property
    def is_live(self) -> bool:
        """A syllable is 'live' if it ends in a sonorant or long vowel with no coda."""
        if self.coda:
            return self.coda in SONORANT_FINALS
        return self.vowel_is_long

    @property
    def is_dead(self) -> bool:
        """A syllable is 'dead' if it ends in a stop or short vowel with no coda."""
        return not self.is_live


def _parse_leading_vowel(text: str, pos: int) -> tuple[str, int]:
    """Parse any leading vowel at position."""
    leading = ""
    while pos < len(text) and text[pos] in LEADING_VOWELS:
        leading += text[pos]
        pos += 1
    return leading, pos


def _parse_onset(text: str, pos: int) -> tuple[str, str, ConsonantClass, int]:
    """Parse the onset consonant(s) and determine effective consonant class.
    
    Returns: (raw_onset, ipa, consonant_class, new_pos)
    """
    if pos >= len(text) or not is_consonant(text[pos]):
        return "", "ʔ", ConsonantClass.MID, pos

    first_char = text[pos]
    onset = first_char
    pos += 1

    # Check for ho nam (ห leading low-class consonant)
    if first_char == "ห" and pos < len(text) and text[pos] in HO_NAM_CONSONANTS:
        second_char = text[pos]
        onset += second_char
        pos += 1
        ipa = CONSONANTS[second_char].ipa_initial
        return onset, ipa, ConsonantClass.HIGH, pos

    # Check for o nam (อ leading ย)
    if first_char == "อ" and pos < len(text) and text[pos] in O_NAM_CONSONANTS:
        second_char = text[pos]
        onset += second_char
        pos += 1
        ipa = CONSONANTS[second_char].ipa_initial
        return onset, ipa, ConsonantClass.MID, pos

    # Check for consonant cluster (e.g., กร, ปล)
    if first_char in CLUSTER_FIRST and pos < len(text) and text[pos] in CLUSTER_SECOND:
        second_char = text[pos]
        # Check if this is actually a cluster or if second is a coda
        # Look ahead to see if there's a vowel after
        next_pos = pos + 1
        has_vowel_after = False
        if next_pos < len(text):
            next_char = text[next_pos]
            if is_vowel_char(next_char) or is_tone_mark(next_char):
                has_vowel_after = True
        
        # If there's a vowel/tone mark immediately after, it's likely a cluster
        if has_vowel_after or (next_pos < len(text) and not is_consonant(text[next_pos])):
            onset += second_char
            pos += 1
            ipa = CONSONANTS[first_char].ipa_initial + CONSONANTS[second_char].ipa_initial
            return onset, ipa, CONSONANTS[first_char].consonant_class, pos

    ipa = CONSONANTS[first_char].ipa_initial
    return onset, ipa, CONSONANTS[first_char].consonant_class, pos


def _parse_vowel_and_tone(
    text: str, pos: int, leading_vowel: str
) -> tuple[str, str, bool, str | None, int]:
    """Parse vowel characters and tone mark after onset.
    
    Returns: (vowel_chars, vowel_ipa, is_long, tone_mark, new_pos)
    """
    vowel_chars = ""
    tone_mark = None

    # Collect above/below vowels and tone marks
    while pos < len(text):
        char = text[pos]
        if char in ABOVE_VOWELS | BELOW_VOWELS:
            vowel_chars += char
            pos += 1
        elif is_tone_mark(char):
            tone_mark = char
            pos += 1
        else:
            break

    # Collect following vowels (ะ า อ ำ)
    while pos < len(text) and text[pos] in FOLLOWING_VOWELS:
        vowel_chars += text[pos]
        pos += 1

    # Combine with leading vowel to determine full vowel
    full_vowel_key = leading_vowel + vowel_chars

    # Try to find the vowel in our mapping
    if full_vowel_key in VOWELS:
        info = VOWELS[full_vowel_key]
        return full_vowel_key, info.ipa, info.is_long, tone_mark, pos

    # Try without leading vowel
    if vowel_chars in VOWELS:
        info = VOWELS[vowel_chars]
        return vowel_chars, info.ipa, info.is_long, tone_mark, pos

    # Handle special cases
    # เ-อ (long mid vowel)
    if leading_vowel == "เ" and "อ" in vowel_chars:
        return leading_vowel + vowel_chars, "ɤː", True, tone_mark, pos

    # เ-ีย (ia diphthong)
    if leading_vowel == "เ" and "ี" in vowel_chars:
        return leading_vowel + vowel_chars, "ia", True, tone_mark, pos

    # เ-ือ (ɯa diphthong)
    if leading_vowel == "เ" and "ื" in vowel_chars:
        return leading_vowel + vowel_chars, "ɯa", True, tone_mark, pos

    # Standalone leading vowels (long)
    if leading_vowel and not vowel_chars:
        if leading_vowel in VOWELS:
            info = VOWELS[leading_vowel]
            return leading_vowel, info.ipa, info.is_long, tone_mark, pos

    # Default: inherent short 'o' or 'a'
    if not vowel_chars and not leading_vowel:
        return "", "o", False, tone_mark, pos

    # Try partial match
    for key in VOWELS:
        if vowel_chars.startswith(key) or key.startswith(vowel_chars):
            info = VOWELS[key]
            return vowel_chars, info.ipa, info.is_long, tone_mark, pos

    # Fallback
    return vowel_chars, "a", False, tone_mark, pos


def _parse_coda(text: str, pos: int) -> tuple[str, str, int]:
    """Parse the coda consonant if present.
    
    Returns: (coda_char, coda_ipa, new_pos)
    """
    if pos >= len(text):
        return "", "", pos

    char = text[pos]

    # Not a consonant - no coda
    if not is_consonant(char):
        return "", "", pos

    # Check if this consonant is actually the onset of the next syllable
    # by looking ahead for vowels
    next_pos = pos + 1
    if next_pos < len(text):
        next_char = text[next_pos]
        # If followed by a vowel or tone mark, it's likely the next onset
        if is_vowel_char(next_char) and next_char not in LEADING_VOWELS:
            # It's a coda
            coda_ipa = CONSONANTS[char].ipa_final
            return char, coda_ipa, pos + 1
        elif next_char in LEADING_VOWELS:
            # Next syllable has leading vowel, this is next onset
            return "", "", pos
        elif is_tone_mark(next_char):
            # Tone mark after - this is coda if next-next is consonant or end
            if next_pos + 1 < len(text) and is_consonant(text[next_pos + 1]):
                return "", "", pos
            coda_ipa = CONSONANTS[char].ipa_final
            return char, coda_ipa, pos + 1

    # At end of text or followed by space/punctuation - it's a coda
    if next_pos >= len(text) or not is_thai_char(text[next_pos]):
        coda_ipa = CONSONANTS[char].ipa_final
        return char, coda_ipa, pos + 1

    # Check for consonant cluster that could be next onset
    if char in CLUSTER_FIRST and next_pos < len(text) and text[next_pos] in CLUSTER_SECOND:
        return "", "", pos

    # Default: treat as coda
    coda_ipa = CONSONANTS[char].ipa_final
    return char, coda_ipa, pos + 1


def parse_syllable(text: str, pos: int = 0) -> tuple[Syllable | None, int]:
    """Parse a single Thai syllable starting at position.
    
    Returns: (Syllable or None, new position)
    """
    # Skip non-Thai characters
    while pos < len(text) and not is_thai_char(text[pos]):
        pos += 1

    if pos >= len(text):
        return None, pos

    # Mark the actual start of Thai content
    syllable_start = pos

    # 1. Parse leading vowel (if any)
    leading_vowel, pos = _parse_leading_vowel(text, pos)

    # 2. Parse onset consonant(s)
    onset, onset_ipa, consonant_class, pos = _parse_onset(text, pos)

    # 3. Parse vowel (above/below/following) and tone mark
    vowel_chars, vowel_ipa, is_long, tone_mark, pos = _parse_vowel_and_tone(
        text, pos, leading_vowel
    )

    # 4. Parse coda consonant (if any)
    coda, coda_ipa, pos = _parse_coda(text, pos)

    # Handle special case: ำ includes the 'm' coda
    if vowel_chars == "ำ" or "ำ" in vowel_chars:
        vowel_ipa = "a"
        is_long = False
        coda = "ม"
        coda_ipa = "m"

    raw = text[syllable_start:pos]

    return Syllable(
        onset=onset,
        onset_ipa=onset_ipa,
        consonant_class=consonant_class,
        vowel_chars=vowel_chars,
        vowel_ipa=vowel_ipa,
        vowel_is_long=is_long,
        tone_mark=tone_mark,
        coda=coda,
        coda_ipa=coda_ipa,
        raw=raw,
    ), pos


def parse_syllables(text: str) -> Iterator[Syllable]:
    """Parse Thai text into syllables."""
    pos = 0
    while pos < len(text):
        syllable, new_pos = parse_syllable(text, pos)
        if syllable is None:
            pos = new_pos + 1 if new_pos == pos else new_pos
            continue
        yield syllable
        pos = new_pos
