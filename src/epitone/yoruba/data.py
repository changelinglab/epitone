"""Yoruba orthographic data: consonants, vowels, tones, and mappings.

Yoruba uses a Latin-based alphabet with:
- 18 consonants (including digraph 'gb')
- 7 oral vowels + 5 nasal vowels
- 3 tones (high, mid, low) marked with diacritics
- Syllabic nasals (m, n) that carry tone
"""

import re
import unicodedata
from typing import NamedTuple


# Tie bar for affricates and labiovelars
TIE_BAR = "\u0361"  # ͡

# Syllabicity mark (combining vertical line below)
SYLLABIC = "\u0329"  # ̩


class Tone:
    """Yoruba tone constants."""
    HIGH = "high"
    MID = "mid"
    LOW = "low"


# Chao tone letters for Yoruba's 3-tone system
TONE_TO_CHAO = {
    Tone.HIGH: "˦",    # High (4)
    Tone.MID: "˧",     # Mid (3)
    Tone.LOW: "˨",     # Low (2)
}


# Unicode combining characters for tones
TONE_ACUTE = "\u0301"  # ́ (combining acute accent) - HIGH
TONE_GRAVE = "\u0300"  # ̀ (combining grave accent) - LOW
# No mark = MID tone


# Consonant IPA mappings
# Note: 'p' is realized as /k͡p/ in Yoruba, NOT /p/
# 'gb' is a single labial-velar phoneme /ɡ͡b/
# 'j' is an affricate /d͡ʒ/
CONSONANTS = {
    "b": "b",
    "d": "d",
    "f": "f",
    "g": "ɡ",
    "gb": f"ɡ{TIE_BAR}b",  # Voiced labial-velar plosive
    "h": "h",
    "j": f"d{TIE_BAR}ʒ",   # Voiced postalveolar affricate
    "k": "k",
    "l": "l",
    "m": "m",
    "n": "n",
    "p": f"k{TIE_BAR}p",   # Voiceless labial-velar plosive (NOT /p/!)
    "r": "ɾ",              # Alveolar tap
    "s": "s",
    "ṣ": "ʃ",              # Voiceless postalveolar fricative
    "t": "t",
    "w": "w",
    "y": "j",              # Palatal approximant
}

# Alternative spellings
CONSONANT_ALTERNATES = {
    "sh": "ʃ",  # Alternative for ṣ
}

# Digraphs (must be checked before single consonants)
DIGRAPHS = frozenset(["gb", "sh"])


# Oral vowel IPA mappings (without tone marks)
ORAL_VOWELS = {
    "a": "a",
    "e": "e",
    "ẹ": "ɛ",
    "i": "i",
    "o": "o",
    "ọ": "ɔ",
    "u": "u",
}

# Nasal vowels (V + n becomes nasal vowel in certain contexts)
# These occur when 'n' follows a vowel at word end or before a consonant
NASAL_VOWELS = {
    "a": "ã",
    "ẹ": "ɛ̃",
    "i": "ĩ",
    "ọ": "ɔ̃",
    "u": "ũ",
}

# Vowels that can be nasalized (not e, o - they form sequences, not nasal vowels)
NASALIZABLE_VOWELS = frozenset(["a", "ẹ", "i", "ọ", "u"])

# All vowel base characters (lowercase)
ALL_VOWELS = frozenset(["a", "e", "ẹ", "i", "o", "ọ", "u"])

# All consonant characters (lowercase, single chars)
ALL_CONSONANTS = frozenset(["b", "d", "f", "g", "h", "j", "k", "l", "m", "n", "p", "r", "s", "ṣ", "t", "w", "y"])

# Characters that form Yoruba text
YORUBA_CHARS = ALL_VOWELS | ALL_CONSONANTS | frozenset(["́", "̀", "̣"])


def normalize_yoruba(text: str) -> str:
    """Normalize Yoruba text to NFC form for consistent processing."""
    return unicodedata.normalize("NFC", text)


def decompose_char(char: str) -> tuple[str, str | None]:
    """Decompose a Yoruba character into base + tone mark.
    
    Returns: (base_char, tone_mark) where tone_mark is None for mid tone.
    """
    decomposed = unicodedata.normalize("NFD", char)
    base = ""
    tone = None
    
    for c in decomposed:
        if c == TONE_ACUTE:
            tone = Tone.HIGH
        elif c == TONE_GRAVE:
            tone = Tone.LOW
        else:
            base += c
    
    # Re-compose base without tone (preserves ẹ, ọ, ṣ)
    base = unicodedata.normalize("NFC", base)
    return base, tone


def get_tone_from_char(char: str) -> str:
    """Extract tone from a character. Returns Tone.HIGH, Tone.MID, or Tone.LOW."""
    _, tone = decompose_char(char)
    return tone if tone else Tone.MID


def strip_tone(char: str) -> str:
    """Remove tone mark from a character, keeping base form."""
    base, _ = decompose_char(char)
    return base


def is_vowel(char: str) -> bool:
    """Check if character is a Yoruba vowel (ignoring tone marks)."""
    base = strip_tone(char).lower()
    return base in ALL_VOWELS


def is_consonant(char: str) -> bool:
    """Check if character is a Yoruba consonant."""
    return char.lower() in ALL_CONSONANTS


def is_nasal(char: str) -> bool:
    """Check if character is a nasal consonant (m or n)."""
    return char.lower() in ("m", "n")


def is_yoruba_char(char: str) -> bool:
    """Check if character is part of Yoruba orthography."""
    base = strip_tone(char).lower()
    return base in YORUBA_CHARS or base in ALL_VOWELS or base in ALL_CONSONANTS


def get_consonant_ipa(consonant: str) -> str:
    """Get IPA for a consonant or digraph."""
    c_lower = consonant.lower()
    
    # Check digraphs first
    if c_lower in CONSONANT_ALTERNATES:
        return CONSONANT_ALTERNATES[c_lower]
    
    if c_lower in CONSONANTS:
        return CONSONANTS[c_lower]
    
    return consonant  # Return as-is if unknown


def get_vowel_ipa(vowel: str, is_nasal: bool = False) -> str:
    """Get IPA for a vowel.
    
    Args:
        vowel: The vowel character (may include tone mark)
        is_nasal: Whether this is a nasal vowel
        
    Returns:
        IPA string for the vowel (without tone - tone handled separately)
    """
    base = strip_tone(vowel).lower()
    
    if is_nasal and base in NASAL_VOWELS:
        return NASAL_VOWELS[base]
    
    if base in ORAL_VOWELS:
        return ORAL_VOWELS[base]
    
    return base  # Return as-is if unknown
