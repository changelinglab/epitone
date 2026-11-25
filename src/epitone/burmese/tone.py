"""Burmese tone determination and representation.

Burmese has 4 tones:
1. Low (အသံနိမ့်): Low falling, relatively long, may have slight breathiness
2. High (အသံမြင့်): High falling, often with tension
3. Creaky (သက်သံ): Mid level with creaky voice
4. Checked (အသံပိတ်): Short, with glottal stop coda

Phonation types:
- Modal: Normal voice quality
- Breathy: Relaxed vocal folds, associated with some low tone contexts
- Creaky: Constricted vocal folds, associated with creaky tone
"""

from epitone.burmese.data import (
    BREATHY_MARK,
    CREAKY_MARK,
    Phonation,
    Tone,
    TONE_TO_CHAO,
)
from epitone.burmese.syllable import Syllable


def get_tone_chao(tone: Tone) -> str:
    """Get Chao tone letter(s) for a tone."""
    return TONE_TO_CHAO[tone]


def get_phonation_mark(phonation: Phonation) -> str:
    """Get the combining diacritic for a phonation type.
    
    Returns:
        Empty string for modal voice, appropriate combining mark otherwise.
    """
    if phonation == Phonation.BREATHY:
        return BREATHY_MARK
    elif phonation == Phonation.CREAKY:
        return CREAKY_MARK
    return ""


def apply_phonation_to_vowel(vowel_ipa: str, phonation: Phonation) -> str:
    """Apply phonation marking to a vowel IPA string.
    
    The phonation mark is added after the first vowel character
    to properly combine with the base vowel.
    
    Args:
        vowel_ipa: The vowel IPA string
        phonation: The phonation type
        
    Returns:
        Vowel IPA with phonation diacritic if applicable
    """
    if phonation == Phonation.MODAL:
        return vowel_ipa
    
    if not vowel_ipa:
        return vowel_ipa
    
    mark = get_phonation_mark(phonation)
    if not mark:
        return vowel_ipa
    
    # Insert mark after first character (the base vowel)
    return vowel_ipa[0] + mark + vowel_ipa[1:]


def format_syllable_ipa(syllable: Syllable, include_tone: bool = True,
                        include_phonation: bool = True) -> str:
    """Format a syllable as an IPA string with tone and phonation.
    
    Args:
        syllable: The parsed syllable
        include_tone: Whether to include Chao tone letters
        include_phonation: Whether to include phonation diacritics
        
    Returns:
        IPA string for the syllable
    """
    parts = []
    
    # Onset
    if syllable.onset_ipa:
        parts.append(syllable.onset_ipa)
    
    # Medials
    if syllable.medial_ipa:
        parts.append(syllable.medial_ipa)
    
    # Vowel (with optional phonation marking)
    vowel = syllable.vowel_ipa
    if include_phonation:
        vowel = apply_phonation_to_vowel(vowel, syllable.phonation)
    if vowel:
        parts.append(vowel)
    
    # Coda
    if syllable.coda_ipa:
        parts.append(syllable.coda_ipa)
    
    # Tone
    if include_tone:
        parts.append(get_tone_chao(syllable.tone))
    
    return "".join(parts)


def format_syllable_tokens(syllable: Syllable, include_tone: bool = True,
                           include_phonation: bool = True) -> list[str]:
    """Format a syllable as a list of IPA tokens.
    
    Args:
        syllable: The parsed syllable
        include_tone: Whether to include tone as a token
        include_phonation: Whether to include phonation in vowel
        
    Returns:
        List of IPA tokens
    """
    tokens = []
    
    # Onset (may include aspiration)
    if syllable.onset_ipa:
        tokens.append(syllable.onset_ipa)
    
    # Medials
    if syllable.medial_ipa:
        tokens.append(syllable.medial_ipa)
    
    # Vowel
    vowel = syllable.vowel_ipa
    if include_phonation:
        vowel = apply_phonation_to_vowel(vowel, syllable.phonation)
    if vowel:
        tokens.append(vowel)
    
    # Coda
    if syllable.coda_ipa:
        tokens.append(syllable.coda_ipa)
    
    # Tone
    if include_tone:
        tokens.append(get_tone_chao(syllable.tone))
    
    return tokens
