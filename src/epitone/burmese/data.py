"""Burmese orthographic data: consonants, vowels, medials, tones, and phonation.

Burmese features:
- 4-tone system: low, high, creaky, checked
- 3 phonation types: modal, breathy, creaky
- Complex syllable structure with medials
- Consonant-final syllables marked with asat (်)

References:
- https://en.wikipedia.org/wiki/Burmese_phonology
- https://en.wikipedia.org/wiki/Burmese_alphabet
"""

import unicodedata
from enum import Enum
from typing import NamedTuple


class Tone(Enum):
    """Burmese tones."""
    LOW = "low"           # Low, relatively long, may be slightly breathy
    HIGH = "high"         # High, falling, often tense
    CREAKY = "creaky"     # Mid, with creaky phonation
    CHECKED = "checked"   # Short, with glottal stop


class Phonation(Enum):
    """Voice phonation types."""
    MODAL = "modal"       # Normal voice
    BREATHY = "breathy"   # Breathy voice (marked with ̤ U+0324)
    CREAKY = "creaky"     # Creaky voice (marked with ̰ U+0330)


# Chao tone letters for Burmese
# Based on typical phonetic analyses of Standard Burmese
TONE_TO_CHAO = {
    Tone.LOW: "˨˩",        # Low falling (21)
    Tone.HIGH: "˥˩",       # High falling (51)
    Tone.CREAKY: "˧",      # Mid level (33)
    Tone.CHECKED: "˥",     # Short high (5), typically with glottal
}

# Unicode combining marks for phonation
BREATHY_MARK = "\u0324"   # ̤ Combining diaeresis below
CREAKY_MARK = "\u0330"    # ̰ Combining tilde below


class ConsonantInfo(NamedTuple):
    """Information about a Burmese consonant."""
    ipa: str              # IPA representation
    is_aspirated: bool    # Whether the consonant is aspirated
    can_be_final: bool    # Whether it can appear as a coda


# Base consonants (single characters)
# Modern spoken Burmese often neutralizes voiced/voiceless distinctions
CONSONANTS: dict[str, ConsonantInfo] = {
    # Velar series (က row)
    "က": ConsonantInfo("k", False, True),    # ka
    "ခ": ConsonantInfo("kʰ", True, True),    # kha
    "ဂ": ConsonantInfo("ɡ", False, True),    # ga (often /k/ in modern speech)
    "ဃ": ConsonantInfo("ɡ", False, True),    # gha (literary, rare)
    "င": ConsonantInfo("ŋ", False, True),    # nga

    # Palatal series (စ row)
    "စ": ConsonantInfo("s", False, True),    # ca → /s/ in modern Burmese
    "ဆ": ConsonantInfo("sʰ", True, True),    # cha → /sʰ/ 
    "ဇ": ConsonantInfo("z", False, True),    # ja → /z/
    "ဈ": ConsonantInfo("z", False, True),    # jha (rare)
    "ည": ConsonantInfo("ɲ", False, True),    # nya

    # Retroflex series (ဋ row) - mostly literary
    "ဋ": ConsonantInfo("t", False, True),    # tta (literary)
    "ဌ": ConsonantInfo("tʰ", True, True),    # ttha (literary)
    "ဍ": ConsonantInfo("d", False, True),    # dda (literary)
    "ဎ": ConsonantInfo("d", False, True),    # ddha (literary)
    "ဏ": ConsonantInfo("n", False, True),    # nna (literary)

    # Dental series (တ row)
    "တ": ConsonantInfo("t", False, True),    # ta
    "ထ": ConsonantInfo("tʰ", True, True),    # tha
    "ဒ": ConsonantInfo("d", False, True),    # da
    "ဓ": ConsonantInfo("d", False, True),    # dha
    "န": ConsonantInfo("n", False, True),    # na

    # Labial series (ပ row)
    "ပ": ConsonantInfo("p", False, True),    # pa
    "ဖ": ConsonantInfo("pʰ", True, True),    # pha
    "ဗ": ConsonantInfo("b", False, True),    # ba
    "ဘ": ConsonantInfo("b", False, True),    # bha
    "မ": ConsonantInfo("m", False, True),    # ma

    # Semivowels and fricatives (ယ row)
    "ယ": ConsonantInfo("j", False, True),    # ya
    "ရ": ConsonantInfo("j", False, True),    # ra → /j/ in modern standard Burmese
    "လ": ConsonantInfo("l", False, True),    # la
    "ဝ": ConsonantInfo("w", False, True),    # wa
    "သ": ConsonantInfo("θ", False, True),    # sa/tha → /θ/ (dental fricative)
    "ဟ": ConsonantInfo("h", False, False),   # ha
    "ဠ": ConsonantInfo("l", False, True),    # lla (literary)
    "အ": ConsonantInfo("ʔ", False, False),   # a (glottal stop)
}

# Final consonant IPA (when in coda position with asat)
# Many finals are unreleased or neutralized
FINAL_CONSONANTS: dict[str, str] = {
    "က": "ʔ",   # Stops become glottal stop
    "ခ": "ʔ",
    "ဂ": "ʔ",
    "ဃ": "ʔ",
    "င": "ŋ",   # Nasals remain
    "စ": "ʔ",
    "ဆ": "ʔ",
    "ဇ": "ʔ",
    "ဈ": "ʔ",
    "ည": "ɲ",
    "ဋ": "ʔ",
    "ဌ": "ʔ",
    "ဍ": "ʔ",
    "ဎ": "ʔ",
    "ဏ": "n",
    "တ": "ʔ",
    "ထ": "ʔ",
    "ဒ": "ʔ",
    "ဓ": "ʔ",
    "န": "n",
    "ပ": "ʔ",
    "ဖ": "ʔ",
    "ဗ": "ʔ",
    "ဘ": "ʔ",
    "မ": "m",
    "ယ": "j",
    "ရ": "j",
    "လ": "l",
    "ဝ": "w",
    "သ": "ʔ",
    "ဟ": "h",
    "ဠ": "l",
    "အ": "ʔ",
}

# Medial consonants (combine with base consonant)
MEDIALS = {
    "ျ": "j",    # ya-pin (medial y)
    "ြ": "j",    # ya-yit (also medial y, older form)
    "ွ": "w",    # wa-hswe (medial w)
    "ှ": "h",    # ha-hto (aspiration marker)
}

# Medial combinations
MEDIAL_COMBINATIONS = {
    "ျ": "j",
    "ြ": "j",
    "ွ": "w",
    "ှ": "ʰ",   # Treated as aspiration
    "ျွ": "jw",
    "ြွ": "jw",
    "ျှ": "jʰ",
    "ြှ": "jʰ",
    "ွှ": "wʰ",
    "ျွှ": "jwʰ",
    "ြွှ": "jwʰ",
}


class VowelInfo(NamedTuple):
    """Information about a Burmese vowel."""
    ipa: str
    tone: Tone | None     # Some vowel forms imply a specific tone
    is_checked: bool      # Whether this form creates a checked tone


# Vowels - combinations of dependent vowel signs
# The key is the combination of vowel signs (sorted: leading, above, below, following)
VOWELS: dict[str, VowelInfo] = {
    # Inherent vowel (no explicit vowel sign) - typically /a/
    "": VowelInfo("a", None, False),

    # Simple vowels with ါ (tall aa)
    "ါ": VowelInfo("a", Tone.LOW, False),
    "ာ": VowelInfo("a", Tone.LOW, False),  # Short form

    # Above vowels
    "ိ": VowelInfo("i", None, False),     # Short i
    "ီ": VowelInfo("i", Tone.HIGH, False), # Long i (high tone marker)
    "ု": VowelInfo("u", None, False),     # Short u
    "ူ": VowelInfo("u", Tone.HIGH, False), # Long u (high tone marker)
    "ဲ": VowelInfo("ɛ", None, False),     # ai → /ɛ/

    # Leading vowel ေ combinations
    "ေ": VowelInfo("e", None, False),     # e vowel
    "ေါ": VowelInfo("ɔ", Tone.LOW, False), # aw vowel
    "ော": VowelInfo("ɔ", Tone.LOW, False), # Alternative aw
    "ေါ်": VowelInfo("ɔ", Tone.CHECKED, True), # Checked aw

    # Complex vowels with multiple signs
    "ိုး": VowelInfo("o", Tone.HIGH, False),   # ou with visarga
    "ို": VowelInfo("o", None, False),    # ou vowel
    "ို": VowelInfo("o", None, False),    # ou alternative

    # Vowels with asat (checked syllables)
    "ိတ်": VowelInfo("eɪʔ", Tone.CHECKED, True),
    "ုတ်": VowelInfo("oʊʔ", Tone.CHECKED, True),
    "ိန်": VowelInfo("eɪn", None, False),
    "ုန်": VowelInfo("oʊn", None, False),

    # Nasalized codas
    "ံ": VowelInfo("ã", Tone.CREAKY, False),  # Anusvara - nasalization
    "ိံ": VowelInfo("ĩ", Tone.CREAKY, False),
    "ုံ": VowelInfo("ũ", Tone.CREAKY, False),
    "ောင်": VowelInfo("aʊ̃", None, False),    # aung
    "ိုင်": VowelInfo("aɪ̃", None, False),     # aing

    # With visarga (high tone marker)
    "း": VowelInfo("", Tone.HIGH, False),  # Visarga alone
    "ါး": VowelInfo("a", Tone.HIGH, False),
    "ားး": VowelInfo("a", Tone.HIGH, False),
    "ေး": VowelInfo("e", Tone.HIGH, False),
    "ိုး": VowelInfo("o", Tone.HIGH, False),
}

# Leading vowel characters (appear before consonant graphically)
LEADING_VOWELS = frozenset(["ေ"])

# Above vowel characters
ABOVE_VOWELS = frozenset(["ိ", "ီ", "ံ", "ဲ", "ဴ", "ြ", "ျ", "ှ"])

# Below vowel characters  
BELOW_VOWELS = frozenset(["ု", "ူ", "ွ"])

# Following vowel characters
FOLLOWING_VOWELS = frozenset(["ါ", "ာ", "ော", "ေါ", "ို"])

# Tone markers
ASAT = "်"            # Virama/asat - marks coda consonant
VISARGA = "း"         # Visarga - typically high tone
ANUSVARA = "ံ"        # Anusvara - nasalization, creaky tone

# Tone marks set
TONE_MARKS = frozenset([VISARGA, ANUSVARA])

# Stacking marker
VIRAMA = "္"          # For consonant stacking (subscript consonants)

# Myanmar Unicode range
MYANMAR_RANGE = range(0x1000, 0x109F)

# Extended Myanmar range
MYANMAR_EXTENDED_A = range(0xAA60, 0xAA7F)
MYANMAR_EXTENDED_B = range(0xA9E0, 0xA9FF)


def is_myanmar_char(char: str) -> bool:
    """Check if a character is in the Myanmar Unicode block."""
    if len(char) != 1:
        return False
    code = ord(char)
    return (code in MYANMAR_RANGE or 
            code in MYANMAR_EXTENDED_A or 
            code in MYANMAR_EXTENDED_B)


def is_consonant(char: str) -> bool:
    """Check if a character is a Burmese consonant."""
    return char in CONSONANTS


def is_medial(char: str) -> bool:
    """Check if a character is a medial marker."""
    return char in MEDIALS


def is_vowel_sign(char: str) -> bool:
    """Check if a character is a dependent vowel sign."""
    return (char in LEADING_VOWELS or 
            char in ABOVE_VOWELS or 
            char in BELOW_VOWELS or 
            char in FOLLOWING_VOWELS)


def is_tone_mark(char: str) -> bool:
    """Check if a character is a tone mark."""
    return char in TONE_MARKS


def is_asat(char: str) -> bool:
    """Check if a character is the asat (virama)."""
    return char == ASAT


def is_virama(char: str) -> bool:
    """Check if a character is the stacking virama."""
    return char == VIRAMA


def get_consonant_ipa(char: str, as_final: bool = False) -> str:
    """Get IPA for a consonant.
    
    Args:
        char: The consonant character
        as_final: Whether the consonant is in final/coda position
        
    Returns:
        IPA string for the consonant
    """
    if as_final:
        return FINAL_CONSONANTS.get(char, "")
    if char in CONSONANTS:
        return CONSONANTS[char].ipa
    return ""


def get_medial_ipa(medial_chars: str) -> str:
    """Get IPA for medial consonant combination.
    
    Args:
        medial_chars: String of medial characters
        
    Returns:
        IPA string for the medial cluster
    """
    if medial_chars in MEDIAL_COMBINATIONS:
        return MEDIAL_COMBINATIONS[medial_chars]
    
    # Build from individual medials
    result = []
    for char in medial_chars:
        if char in MEDIALS:
            result.append(MEDIALS[char])
    return "".join(result)


def normalize_burmese(text: str) -> str:
    """Normalize Burmese text to NFC form for consistent processing."""
    return unicodedata.normalize("NFC", text)


def add_phonation_mark(vowel: str, phonation: Phonation) -> str:
    """Add phonation marking to a vowel.
    
    Args:
        vowel: The vowel IPA string
        phonation: The phonation type
        
    Returns:
        Vowel with phonation diacritic added
    """
    if phonation == Phonation.MODAL:
        return vowel
    elif phonation == Phonation.BREATHY:
        # Add breathy mark after first vowel character
        if vowel:
            return vowel[0] + BREATHY_MARK + vowel[1:]
        return vowel
    elif phonation == Phonation.CREAKY:
        # Add creaky mark after first vowel character
        if vowel:
            return vowel[0] + CREAKY_MARK + vowel[1:]
        return vowel
    return vowel
