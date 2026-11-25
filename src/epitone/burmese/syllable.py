"""Burmese syllable parsing and representation.

Burmese syllable structure:
    (Leading V) + Consonant + (Medials) + (Above V) + (Below V) + (Following V) + (Coda) + (Tone)

Where:
- Leading V: ေ (always appears before consonant graphically)
- Consonant: Base consonant from က to အ
- Medials: ျ (ya-pin), ြ (ya-yit), ွ (wa-hswe), ှ (ha-hto)
- Above V: ိ, ီ, ံ, etc.
- Below V: ု, ူ
- Following V: ါ, ာ, etc.
- Coda: Consonant + ် (asat) or stacked consonant with ္
- Tone: း (visarga) for high tone, ံ (anusvara) for creaky/nasal
"""

from dataclasses import dataclass
from typing import Iterator

from epitone.burmese.data import (
    ABOVE_VOWELS,
    ASAT,
    BELOW_VOWELS,
    CONSONANTS,
    FOLLOWING_VOWELS,
    LEADING_VOWELS,
    MEDIALS,
    Phonation,
    Tone,
    VIRAMA,
    VISARGA,
    ANUSVARA,
    VOWELS,
    get_consonant_ipa,
    get_medial_ipa,
    is_asat,
    is_consonant,
    is_medial,
    is_myanmar_char,
    is_tone_mark,
    is_virama,
    is_vowel_sign,
    add_phonation_mark,
)


@dataclass
class Syllable:
    """Represents a parsed Burmese syllable."""

    onset: str                 # Base consonant character(s)
    onset_ipa: str             # IPA for onset
    medials: str               # Medial characters
    medial_ipa: str            # IPA for medials
    vowel_signs: str           # All vowel sign characters
    vowel_ipa: str             # IPA for vowel
    coda: str                  # Coda consonant character
    coda_ipa: str              # IPA for coda
    tone: Tone                 # Determined tone
    phonation: Phonation       # Voice quality
    raw: str                   # Original text span

    @property
    def is_checked(self) -> bool:
        """A syllable is checked if it ends in a stop consonant."""
        return self.tone == Tone.CHECKED


def _parse_leading_vowel(text: str, pos: int) -> tuple[str, int]:
    """Parse any leading vowel at position.
    
    Note: In Myanmar Unicode, "leading" vowels like ေ (U+1031) visually appear
    BEFORE the consonant but are stored AFTER the consonant in the character
    stream. This function handles the rare case where text might have the
    visual order (non-standard).
    """
    leading = ""
    while pos < len(text) and text[pos] in LEADING_VOWELS:
        leading += text[pos]
        pos += 1
    return leading, pos


def _parse_onset(text: str, pos: int) -> tuple[str, str, int]:
    """Parse the onset consonant(s).
    
    Returns: (raw_onset, ipa, new_pos)
    """
    if pos >= len(text) or not is_consonant(text[pos]):
        return "", "ʔ", pos

    consonant = text[pos]
    pos += 1

    # Check for stacked consonants (consonant + virama + consonant)
    stacked = ""
    while pos + 1 < len(text) and text[pos] == VIRAMA and is_consonant(text[pos + 1]):
        stacked += text[pos]  # virama
        stacked += text[pos + 1]  # subscript consonant
        pos += 2

    full_onset = consonant + stacked
    
    # Get IPA - for stacked consonants, they typically form clusters
    if stacked:
        # Extract consonants from stacked form
        ipa_parts = [get_consonant_ipa(consonant)]
        for i in range(1, len(stacked), 2):  # Skip viramas
            ipa_parts.append(get_consonant_ipa(stacked[i]))
        ipa = "".join(ipa_parts)
    else:
        ipa = get_consonant_ipa(consonant)

    return full_onset, ipa, pos


def _parse_medials(text: str, pos: int) -> tuple[str, str, int]:
    """Parse medial consonant markers.
    
    Returns: (raw_medials, ipa, new_pos)
    """
    medials = ""
    
    # Medials can appear in a specific order: ျ/ြ, ွ, ှ
    # But we'll collect whatever we find
    while pos < len(text) and is_medial(text[pos]):
        medials += text[pos]
        pos += 1

    ipa = get_medial_ipa(medials)
    return medials, ipa, pos


def _parse_vowel_signs(text: str, pos: int, leading_vowel: str) -> tuple[str, str, int]:
    """Parse vowel signs (above, below, leading, following).
    
    In Myanmar Unicode, dependent vowel signs appear after the consonant,
    including "leading" vowels like ေ (U+1031) which visually render before
    the consonant but are stored after it in the character stream.
    
    Returns: (vowel_signs, vowel_ipa, new_pos)
    """
    signs = ""
    captured_leading = ""
    
    # First check for the "leading" vowel ေ which comes after consonant in Unicode
    # but renders visually before it
    while pos < len(text) and text[pos] in LEADING_VOWELS:
        captured_leading += text[pos]
        pos += 1
    
    # Collect above vowel signs (ိ, ီ, ံ, etc.)
    while pos < len(text) and text[pos] in ABOVE_VOWELS:
        signs += text[pos]
        pos += 1
    
    # Collect below vowel signs (ု, ူ)
    while pos < len(text) and text[pos] in BELOW_VOWELS:
        signs += text[pos]
        pos += 1

    # Collect following vowel signs (ါ, ာ, etc.)
    while pos < len(text) and text[pos] in FOLLOWING_VOWELS:
        signs += text[pos]
        pos += 1

    # Combine any captured leading vowel (from either position) with other signs
    all_leading = leading_vowel + captured_leading
    full_vowel_key = all_leading + signs

    # Try to find in vowel mappings
    if full_vowel_key in VOWELS:
        return full_vowel_key, VOWELS[full_vowel_key].ipa, pos

    # Try just the signs
    if signs in VOWELS:
        return all_leading + signs, VOWELS[signs].ipa, pos

    # Handle leading vowel ေ specially
    if "ေ" in all_leading:
        if not signs:
            return all_leading, "e", pos
        # ေ + ါ/ာ = ော (ɔ sound)
        if "ါ" in signs or "ာ" in signs:
            return all_leading + signs, "ɔ", pos
        # ေ + ါ် = checked ɔ
        return all_leading + signs, "e", pos

    # Default: inherent vowel 'a' if no vowel signs
    if not signs and not all_leading:
        return "", "a", pos

    # Fallback based on individual signs
    if "ိ" in signs or "ီ" in signs:
        return all_leading + signs, "i", pos
    if "ု" in signs or "ူ" in signs:
        return all_leading + signs, "u", pos
    if "ဲ" in signs:
        return all_leading + signs, "ɛ", pos
    if "ံ" in signs:
        return all_leading + signs, "ã", pos

    return all_leading + signs, "a", pos


def _parse_coda(text: str, pos: int) -> tuple[str, str, bool, int]:
    """Parse coda consonant (consonant + asat).
    
    Returns: (coda_char, coda_ipa, is_checked, new_pos)
    """
    if pos >= len(text):
        return "", "", False, pos

    # Check for anusvara (nasalization marker) - this is part of vowel, not coda
    if text[pos] == ANUSVARA:
        return "", "", False, pos

    # Check for consonant + asat pattern
    if is_consonant(text[pos]):
        coda_start = pos
        coda_char = text[pos]
        pos += 1
        
        # Must be followed by asat to be a coda
        if pos < len(text) and is_asat(text[pos]):
            pos += 1  # Consume asat
            coda_ipa = get_consonant_ipa(coda_char, as_final=True)
            # Check if this is a stop (checked tone) or sonorant
            is_checked = coda_ipa == "ʔ"
            return coda_char + ASAT, coda_ipa, is_checked, pos
        else:
            # Not followed by asat - this is likely the next syllable's onset
            return "", "", False, coda_start

    return "", "", False, pos


def _parse_tone_marker(text: str, pos: int) -> tuple[str, Tone | None, int]:
    """Parse tone marker (visarga or anusvara).
    
    Returns: (marker, implied_tone, new_pos)
    """
    if pos >= len(text):
        return "", None, pos

    if text[pos] == VISARGA:
        return VISARGA, Tone.HIGH, pos + 1
    
    # Anusvara is typically parsed with vowels, but check here too
    if text[pos] == ANUSVARA:
        return ANUSVARA, Tone.CREAKY, pos + 1

    return "", None, pos


def _determine_tone(vowel_signs: str, coda_ipa: str, tone_marker: str, 
                   vowel_info_tone: Tone | None, is_checked: bool) -> Tone:
    """Determine the tone of a syllable based on various factors.
    
    Priority:
    1. Checked syllables (stop coda) → Checked tone
    2. Explicit tone marker (visarga) → High tone
    3. Vowel form implies tone → Use that tone
    4. Anusvara → Creaky tone
    5. Default → Low tone
    """
    if is_checked:
        return Tone.CHECKED
    
    if tone_marker == VISARGA:
        return Tone.HIGH
    
    if tone_marker == ANUSVARA or ANUSVARA in vowel_signs:
        return Tone.CREAKY
    
    if vowel_info_tone is not None:
        return vowel_info_tone
    
    # Long vowel markers (ီ, ူ) often indicate high tone
    if "ီ" in vowel_signs or "ူ" in vowel_signs:
        return Tone.HIGH

    # Default to low tone for open syllables
    return Tone.LOW


def _determine_phonation(tone: Tone, vowel_signs: str) -> Phonation:
    """Determine phonation type based on tone and context.
    
    - Creaky tone syllables have creaky phonation
    - Some low tone syllables may be breathy
    - Otherwise modal
    """
    if tone == Tone.CREAKY:
        return Phonation.CREAKY
    
    # Checked syllables are typically modal but short
    if tone == Tone.CHECKED:
        return Phonation.MODAL
    
    # Low tone can have slight breathiness but we mark as modal
    return Phonation.MODAL


def parse_syllable(text: str, pos: int = 0) -> tuple[Syllable | None, int]:
    """Parse a single Burmese syllable starting at position.
    
    Returns: (Syllable or None, new position)
    """
    # Skip non-Myanmar characters
    while pos < len(text) and not is_myanmar_char(text[pos]):
        pos += 1

    if pos >= len(text):
        return None, pos

    start_pos = pos

    # 1. Parse leading vowel (if any)
    leading_vowel, pos = _parse_leading_vowel(text, pos)

    # 2. Parse onset consonant(s)
    onset, onset_ipa, pos = _parse_onset(text, pos)

    # 3. Parse medial markers
    medials, medial_ipa, pos = _parse_medials(text, pos)

    # 4. Parse vowel signs
    vowel_signs, vowel_ipa, pos = _parse_vowel_signs(text, pos, leading_vowel)

    # 5. Parse coda
    coda, coda_ipa, is_checked, pos = _parse_coda(text, pos)

    # 6. Parse tone marker
    tone_marker, marker_tone, pos = _parse_tone_marker(text, pos)

    # Get tone info from vowel if available
    full_vowel_key = leading_vowel + vowel_signs
    vowel_info = VOWELS.get(full_vowel_key) or VOWELS.get(vowel_signs)
    vowel_implied_tone = vowel_info.tone if vowel_info else None

    # Determine final tone
    tone = _determine_tone(vowel_signs, coda_ipa, tone_marker, 
                          vowel_implied_tone, is_checked)

    # Determine phonation
    phonation = _determine_phonation(tone, vowel_signs)

    raw = text[start_pos:pos]

    # If we didn't parse anything meaningful, skip this character
    if not onset and not vowel_signs and not leading_vowel:
        return None, start_pos + 1

    return Syllable(
        onset=onset,
        onset_ipa=onset_ipa,
        medials=medials,
        medial_ipa=medial_ipa,
        vowel_signs=leading_vowel + vowel_signs,
        vowel_ipa=vowel_ipa,
        coda=coda,
        coda_ipa=coda_ipa,
        tone=tone,
        phonation=phonation,
        raw=raw,
    ), pos


def parse_syllables(text: str) -> Iterator[Syllable]:
    """Parse Burmese text into syllables."""
    pos = 0
    while pos < len(text):
        syllable, new_pos = parse_syllable(text, pos)
        if syllable is None:
            pos = new_pos if new_pos > pos else pos + 1
            continue
        yield syllable
        pos = new_pos
