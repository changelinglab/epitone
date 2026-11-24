"""Thai tone determination logic based on consonant class, syllable type, and tone marks."""

from epitone.thai.data import (
    ConsonantClass,
    MAI_CHATTAWA,
    MAI_EK,
    MAI_THO,
    MAI_TRI,
    Tone,
    TONE_TO_CHAO,
)
from epitone.thai.syllable import Syllable

# Tone rules table
# Key: (consonant_class, is_live, tone_mark)
# Value: Tone

TONE_RULES: dict[tuple[ConsonantClass, bool, str | None], Tone] = {
    # Mid class consonants
    (ConsonantClass.MID, True, None): Tone.MID,
    (ConsonantClass.MID, True, MAI_EK): Tone.LOW,
    (ConsonantClass.MID, True, MAI_THO): Tone.FALLING,
    (ConsonantClass.MID, True, MAI_TRI): Tone.HIGH,
    (ConsonantClass.MID, True, MAI_CHATTAWA): Tone.RISING,
    (ConsonantClass.MID, False, None): Tone.LOW,
    (ConsonantClass.MID, False, MAI_EK): Tone.LOW,
    (ConsonantClass.MID, False, MAI_THO): Tone.FALLING,
    (ConsonantClass.MID, False, MAI_TRI): Tone.HIGH,
    (ConsonantClass.MID, False, MAI_CHATTAWA): Tone.RISING,
    # High class consonants
    (ConsonantClass.HIGH, True, None): Tone.RISING,
    (ConsonantClass.HIGH, True, MAI_EK): Tone.LOW,
    (ConsonantClass.HIGH, True, MAI_THO): Tone.FALLING,
    (ConsonantClass.HIGH, False, None): Tone.LOW,
    (ConsonantClass.HIGH, False, MAI_EK): Tone.LOW,
    (ConsonantClass.HIGH, False, MAI_THO): Tone.FALLING,
    # Low class consonants - live syllables
    (ConsonantClass.LOW, True, None): Tone.MID,
    (ConsonantClass.LOW, True, MAI_EK): Tone.FALLING,
    (ConsonantClass.LOW, True, MAI_THO): Tone.HIGH,
}

# Special rules for low class dead syllables (depends on vowel length)
LOW_DEAD_SHORT_RULES: dict[str | None, Tone] = {
    None: Tone.HIGH,
    MAI_EK: Tone.FALLING,
    MAI_THO: Tone.HIGH,
}

LOW_DEAD_LONG_RULES: dict[str | None, Tone] = {
    None: Tone.FALLING,
    MAI_EK: Tone.FALLING,
    MAI_THO: Tone.HIGH,
}


def determine_tone(syllable: Syllable) -> Tone:
    """Determine the tone of a Thai syllable based on the tone rules.
    
    The tone is determined by:
    1. Consonant class (high, mid, low)
    2. Syllable type (live vs dead)
    3. Tone mark (if present)
    4. Vowel length (for low-class dead syllables)
    """
    consonant_class = syllable.consonant_class
    is_live = syllable.is_live
    tone_mark = syllable.tone_mark

    # Try the main rules table first
    key = (consonant_class, is_live, tone_mark)
    if key in TONE_RULES:
        return TONE_RULES[key]

    # Handle low class dead syllables specially
    if consonant_class == ConsonantClass.LOW and not is_live:
        if syllable.vowel_is_long:
            return LOW_DEAD_LONG_RULES.get(tone_mark, Tone.FALLING)
        else:
            return LOW_DEAD_SHORT_RULES.get(tone_mark, Tone.HIGH)

    # Default to mid tone if no rule matches
    return Tone.MID


def get_tone_chao(tone: Tone) -> str:
    """Get the Chao tone letter(s) for a tone."""
    return TONE_TO_CHAO[tone]
