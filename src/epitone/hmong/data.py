"""Hmong orthographic data: consonants, vowels, tones, and mappings.

This module contains common data for Hmong G2P converters:
- RPA (Romanized Popular Alphabet) for Hmong Daw and Mong Leng dialects
- Dananshan Miao orthography

References:
- https://en.wikipedia.org/wiki/Hmong_language
- Chao tone letters per dialect from Wikipedia's Hmong language phonology tables
"""

import unicodedata
from enum import Enum
from typing import NamedTuple


class HmongDialect(Enum):
    """Hmong dialect varieties."""
    
    HMONG_DAW = "hmong_daw"      # White Hmong
    MONG_LENG = "mong_leng"      # Green/Blue Hmong (Mong Njua)
    DANANSHAN = "dananshan"      # Dananshan Miao


# ============================================================================
# Shared IPA symbols
# ============================================================================

# Combining diacritics
BREATHY_VOICE = "\u0324"   # ̤ - combining diaeresis below (breathy voice marker)
TILDE = "\u0303"           # ̃ - combining tilde (nasalization)


# ============================================================================
# RPA Consonant mappings (shared by both Hmong Daw and Mong Leng)
# ============================================================================

# Initial consonants in RPA orthography
# Using standard IPA without superscripts for prenasalized stops
# Clusters like /pl/, /tl/ use regular /l/ not /ˡ/
RPA_CONSONANTS: dict[str, str] = {
    # Simple stops
    "p": "p",
    "t": "t",
    "k": "k",
    "c": "tʃ",           # Voiceless palato-alveolar affricate
    
    # Aspirated stops
    "ph": "pʰ",
    "th": "tʰ",
    "kh": "kʰ",
    "ch": "tʃʰ",         # Aspirated affricate
    
    # Prenasalized stops (plain IPA, no superscripts)
    "np": "mp",
    "nt": "nt",
    "nk": "ŋk",
    "nc": "ntʃ",
    
    # Aspirated prenasalized stops
    "nph": "mpʰ",
    "nth": "ntʰ",
    "nkh": "ŋkʰ",
    "nch": "ntʃʰ",
    
    # Voiced stops (realized as prenasalized)
    "d": "d",            # Can be [nd] in some analyses
    
    # Laterals and lateral clusters
    "l": "l",
    "hl": "l̥",           # Voiceless lateral
    "pl": "pl",          # /pl/ cluster, not /pˡ/
    "plh": "plʰ",
    "dl": "dl",          # Actually prenasalized lateral cluster [ndl]
    "npl": "mpl",        # Prenasalized lateral cluster
    
    # Nasals
    "m": "m",
    "n": "n",
    "ny": "ɲ",
    "ng": "ŋ",
    "hm": "m̥",           # Voiceless nasal
    "hn": "n̥",
    "hny": "ɲ̊",
    "hng": "ŋ̊",
    
    # Approximants
    "y": "j",
    "w": "w",
    
    # Fricatives
    "f": "f",
    "v": "v",
    "s": "s",
    "x": "ʃ",            # Voiceless palato-alveolar fricative
    "h": "h",
    "xy": "ʃ",           # Same as x in many contexts
    
    # Voiceless approximants
    "hw": "ʍ",           # Voiceless labialized velar approximant
    
    # Retroflex/alveolar series
    "ts": "ts",
    "tsh": "tsʰ",
    "nts": "nts",
    "ntsh": "ntsʰ",
    
    # Velar nasalized series
    "nq": "ɴq",
    "nqh": "ɴqʰ",
    "q": "q",
    "qh": "qʰ",
    
    # Rhotics
    "r": "ɣ",            # Often a uvular/velar continuant
    "rh": "ɣ̊",           # Voiceless rhotic
    
    # Tx series (retroflexes in some dialects)
    "tx": "tʂ",
    "txh": "tʂʰ",
    "ntx": "ntʂ",
    "ntxh": "ntʂʰ",
    
    # Glottal
    "": "ʔ",             # Null onset = glottal stop
}

# Order consonants by length for matching (longest first)
RPA_CONSONANTS_BY_LENGTH = sorted(RPA_CONSONANTS.keys(), key=len, reverse=True)


# ============================================================================
# RPA Vowel mappings
# ============================================================================

# Oral vowels in RPA
RPA_ORAL_VOWELS: dict[str, str] = {
    "i": "i",
    "e": "e",
    "a": "a",
    "o": "ɔ",
    "u": "u",
    "w": "ɨ",            # High central unrounded vowel (when in nucleus position)
}

# Nasal vowels in RPA (ee, oo, aa represent nasalized vowels)
RPA_NASAL_VOWELS: dict[str, str] = {
    "ee": "ẽ",           # Nasalized /e/
    "oo": "ɔ̃",           # Nasalized /ɔ/
    "aa": "ã",           # Nasalized /a/
}

# Diphthongs in RPA
RPA_DIPHTHONGS: dict[str, str] = {
    "ai": "ai",
    "au": "au",
    "aw": "aɨ",
    "ia": "ia",
    "ua": "ua",
    "oo": "ɔ̃",           # Nasal vowel (overlaps with diphthong pattern)
}

# Combined vowel lookup (oral + nasal)
RPA_VOWELS: dict[str, tuple[str, bool]] = {
    # Oral vowels (IPA, is_nasal)
    "i": ("i", False),
    "e": ("e", False),
    "a": ("a", False),
    "o": ("ɔ", False),
    "u": ("u", False),
    "w": ("ɨ", False),
    # Diphthongs
    "ai": ("ai", False),
    "au": ("au", False),
    "aw": ("aɨ", False),
    "ia": ("ia", False),
    "ua": ("ua", False),
    # Nasal vowels (double letters)
    "ee": ("ẽ", True),
    "oo": ("ɔ̃", True),
    "aa": ("ã", True),
}

# Order vowels by length for matching (longest first)
RPA_VOWELS_BY_LENGTH = sorted(RPA_VOWELS.keys(), key=len, reverse=True)


# ============================================================================
# RPA Tone mappings
# ============================================================================

# RPA uses final consonant letters to indicate tone
# The tones have different pitch values in Hmong Daw vs Mong Leng

# Tone letter -> tone name mapping
RPA_TONE_LETTERS: dict[str, str] = {
    "b": "high",         # High level
    "j": "high_falling", # High falling
    "v": "mid_rising",   # Mid rising
    "s": "low",          # Low level (breathy in some contexts)
    "g": "breathy_low",  # Low breathy (murmured, creaky)
    "m": "low_falling",  # Low falling/checked
    "d": "low_rising",   # Low rising
    "": "mid",           # Mid level (no tone letter)
}

# Chao tone letters for Hmong Daw (White Hmong)
# Based on Wikipedia: https://en.wikipedia.org/wiki/Hmong_language
HMONG_DAW_TONES: dict[str, str] = {
    "high": "˥",         # 55 - high level (-b)
    "high_falling": "˥˨", # 52 - high falling (-j)
    "mid_rising": "˨˦",  # 24 - mid rising (-v)
    "low": "˨˩",         # 21 - low level (-s) 
    "breathy_low": "˨",  # 22 - low breathy (-g) with breathy voice on vowel
    "low_falling": "˩",  # 11 - low falling/glottalized (-m)
    "low_rising": "˩˧",  # 13 - low rising (-d)
    "mid": "˧",          # 33 - mid level (no letter)
}

# Chao tone letters for Mong Leng (Green/Blue Hmong, Mong Njua)
MONG_LENG_TONES: dict[str, str] = {
    "high": "˥˧",        # 53 - high falling (-b)
    "high_falling": "˥˨", # 52 - high falling (-j)
    "mid_rising": "˨˦",  # 24 - mid rising (-v)
    "low": "˨˩",         # 21 - low falling (-s)
    "breathy_low": "˧",  # 33 - mid breathy (-g) with breathy voice on vowel
    "low_falling": "˩",  # 11 - low checked (-m)
    "low_rising": "˩˧",  # 13 - low rising (-d)
    "mid": "˧˥",         # 35 - mid rising (no letter)
}


# ============================================================================
# Dananshan orthography mappings
# ============================================================================

# Dananshan initial consonants
DANANSHAN_CONSONANTS: dict[str, str] = {
    # Labials
    "b": "p",
    "p": "pʰ",
    "m": "m",
    "hm": "m̥",
    "f": "f",
    "v": "v",
    "w": "w",
    
    # Alveolars
    "d": "t",
    "t": "tʰ",
    "n": "n",
    "hn": "n̥",
    "l": "l",
    "hl": "l̥",
    "s": "s",
    "z": "z",
    
    # Retroflex
    "zh": "tʂ",
    "ch": "tʂʰ",
    "sh": "ʂ",
    "r": "ʐ",
    
    # Palatals
    "j": "tɕ",
    "q": "tɕʰ",
    "ny": "ɲ",
    "hny": "ɲ̊",
    "x": "ɕ",
    "y": "j",
    
    # Velars
    "g": "k",
    "k": "kʰ",
    "ng": "ŋ",
    "hng": "ŋ̊",
    "h": "h",
    
    # Prenasalized
    "nb": "mp",
    "nd": "nt",
    "nz": "nts",
    "nj": "ntɕ",
    "ng": "ŋk",
    
    # Null onset
    "": "ʔ",
}

# Order Dananshan consonants by length for matching
DANANSHAN_CONSONANTS_BY_LENGTH = sorted(DANANSHAN_CONSONANTS.keys(), key=len, reverse=True)

# Dananshan vowels
DANANSHAN_VOWELS: dict[str, str] = {
    "i": "i",
    "e": "e",
    "a": "a",
    "o": "o",
    "u": "u",
    "ü": "y",           # Front rounded
    "eu": "ɤ",          # Back unrounded mid
    "ai": "ai",
    "ei": "ei",
    "ao": "au",
    "ou": "ou",
    "ia": "ia",
    "ie": "ie",
    "iu": "iu",
    "ua": "ua",
    "uo": "uɔ",
    "ui": "ui",
    "üe": "ye",
}

# Order Dananshan vowels by length for matching
DANANSHAN_VOWELS_BY_LENGTH = sorted(DANANSHAN_VOWELS.keys(), key=len, reverse=True)

# Dananshan tones (8-tone system)
DANANSHAN_TONES: dict[str, str] = {
    "1": "˦˦",          # 44 - high level
    "2": "˧˩",          # 31 - mid falling
    "3": "˦˧",          # 43 - high-mid falling
    "4": "˥˧˥",         # 535 - high-low-high (contour)
    "5": "˧˧",          # 33 - mid level
    "6": "˨˦",          # 24 - low rising
    "7": "˧˥",          # 35 - mid rising
    "8": "˩˧",          # 13 - low-mid rising
    "": "˧˧",           # Default to mid if no tone number
}


# ============================================================================
# Utility functions
# ============================================================================

def normalize_text(text: str) -> str:
    """Normalize text to NFC form for consistent processing."""
    return unicodedata.normalize("NFC", text)


def add_breathy_voice(vowel_ipa: str) -> str:
    """Add breathy voice diacritic to vowel(s).
    
    For the -g tone, breathiness is marked on the vowel nucleus.
    The diacritic goes under the first vowel character.
    """
    if not vowel_ipa:
        return vowel_ipa
    
    # Find the first vowel character and add diacritic after it
    result = []
    added = False
    for char in vowel_ipa:
        result.append(char)
        # Add breathy marker after first vowel letter
        if not added and char in "aeiouɔɨəɤyãẽɔ̃":
            # Check if this char is not already a combining character
            if unicodedata.category(char).startswith("L"):
                result.append(BREATHY_VOICE)
                added = True
    
    return "".join(result)


def is_rpa_consonant_char(char: str) -> bool:
    """Check if character could be part of an RPA consonant."""
    return char.lower() in "bcdfghjklmnpqrstvwxyz"


def is_rpa_vowel_char(char: str) -> bool:
    """Check if character is an RPA vowel."""
    return char.lower() in "aeiouw"


def is_rpa_tone_letter(char: str) -> bool:
    """Check if character is an RPA tone letter."""
    return char.lower() in "bjvsgmd"


def is_dananshan_tone_digit(char: str) -> bool:
    """Check if character is a Dananshan tone digit."""
    return char in "12345678"
