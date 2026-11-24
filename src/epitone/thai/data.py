"""Thai orthographic data: consonants, vowels, tone marks, and mappings."""

from enum import Enum
from typing import NamedTuple


class ConsonantClass(Enum):
    HIGH = "high"
    MID = "mid"
    LOW = "low"


class Tone(Enum):
    MID = "mid"
    LOW = "low"
    FALLING = "falling"
    HIGH = "high"
    RISING = "rising"


TONE_TO_CHAO = {
    Tone.MID: "˧",
    Tone.LOW: "˩",
    Tone.FALLING: "˥˩",
    Tone.HIGH: "˦˥",
    Tone.RISING: "˩˥",
}


class ConsonantInfo(NamedTuple):
    ipa_initial: str
    ipa_final: str
    consonant_class: ConsonantClass


CONSONANTS: dict[str, ConsonantInfo] = {
    "ก": ConsonantInfo("k", "k", ConsonantClass.MID),
    "ข": ConsonantInfo("kʰ", "k", ConsonantClass.HIGH),
    "ฃ": ConsonantInfo("kʰ", "k", ConsonantClass.HIGH),
    "ค": ConsonantInfo("kʰ", "k", ConsonantClass.LOW),
    "ฅ": ConsonantInfo("kʰ", "k", ConsonantClass.LOW),
    "ฆ": ConsonantInfo("kʰ", "k", ConsonantClass.LOW),
    "ง": ConsonantInfo("ŋ", "ŋ", ConsonantClass.LOW),
    "จ": ConsonantInfo("tɕ", "t", ConsonantClass.MID),
    "ฉ": ConsonantInfo("tɕʰ", "t", ConsonantClass.HIGH),
    "ช": ConsonantInfo("tɕʰ", "t", ConsonantClass.LOW),
    "ซ": ConsonantInfo("s", "t", ConsonantClass.LOW),
    "ฌ": ConsonantInfo("tɕʰ", "t", ConsonantClass.LOW),
    "ญ": ConsonantInfo("j", "n", ConsonantClass.LOW),
    "ฎ": ConsonantInfo("d", "t", ConsonantClass.MID),
    "ฏ": ConsonantInfo("t", "t", ConsonantClass.MID),
    "ฐ": ConsonantInfo("tʰ", "t", ConsonantClass.HIGH),
    "ฑ": ConsonantInfo("tʰ", "t", ConsonantClass.LOW),
    "ฒ": ConsonantInfo("tʰ", "t", ConsonantClass.LOW),
    "ณ": ConsonantInfo("n", "n", ConsonantClass.LOW),
    "ด": ConsonantInfo("d", "t", ConsonantClass.MID),
    "ต": ConsonantInfo("t", "t", ConsonantClass.MID),
    "ถ": ConsonantInfo("tʰ", "t", ConsonantClass.HIGH),
    "ท": ConsonantInfo("tʰ", "t", ConsonantClass.LOW),
    "ธ": ConsonantInfo("tʰ", "t", ConsonantClass.LOW),
    "น": ConsonantInfo("n", "n", ConsonantClass.LOW),
    "บ": ConsonantInfo("b", "p", ConsonantClass.MID),
    "ป": ConsonantInfo("p", "p", ConsonantClass.MID),
    "ผ": ConsonantInfo("pʰ", "p", ConsonantClass.HIGH),
    "ฝ": ConsonantInfo("f", "p", ConsonantClass.HIGH),
    "พ": ConsonantInfo("pʰ", "p", ConsonantClass.LOW),
    "ฟ": ConsonantInfo("f", "p", ConsonantClass.LOW),
    "ภ": ConsonantInfo("pʰ", "p", ConsonantClass.LOW),
    "ม": ConsonantInfo("m", "m", ConsonantClass.LOW),
    "ย": ConsonantInfo("j", "j", ConsonantClass.LOW),
    "ร": ConsonantInfo("r", "n", ConsonantClass.LOW),
    "ล": ConsonantInfo("l", "n", ConsonantClass.LOW),
    "ว": ConsonantInfo("w", "w", ConsonantClass.LOW),
    "ศ": ConsonantInfo("s", "t", ConsonantClass.HIGH),
    "ษ": ConsonantInfo("s", "t", ConsonantClass.HIGH),
    "ส": ConsonantInfo("s", "t", ConsonantClass.HIGH),
    "ห": ConsonantInfo("h", "", ConsonantClass.HIGH),
    "ฬ": ConsonantInfo("l", "n", ConsonantClass.LOW),
    "อ": ConsonantInfo("ʔ", "", ConsonantClass.MID),
    "ฮ": ConsonantInfo("h", "", ConsonantClass.LOW),
}

# Low-class consonants that can be led by ห (ho nam) to become high-class
HO_NAM_CONSONANTS = frozenset("งญณนมยรลวฬ")

# ย can be led by อ to become mid-class
O_NAM_CONSONANTS = frozenset("ย")


class VowelInfo(NamedTuple):
    ipa: str
    is_long: bool


VOWELS: dict[str, VowelInfo] = {
    # Short vowels
    "ะ": VowelInfo("a", False),
    "ิ": VowelInfo("i", False),
    "ึ": VowelInfo("ɯ", False),
    "ุ": VowelInfo("u", False),
    "เะ": VowelInfo("e", False),
    "แะ": VowelInfo("ɛ", False),
    "โะ": VowelInfo("o", False),
    "เาะ": VowelInfo("ɔ", False),
    "เอะ": VowelInfo("ɤ", False),
    # Long vowels
    "า": VowelInfo("aː", True),
    "ี": VowelInfo("iː", True),
    "ือ": VowelInfo("ɯː", True),
    "ู": VowelInfo("uː", True),
    "เ": VowelInfo("eː", True),
    "แ": VowelInfo("ɛː", True),
    "โ": VowelInfo("oː", True),
    "อ": VowelInfo("ɔː", True),
    "เอ": VowelInfo("ɤː", True),
    # Diphthongs (long)
    "เีย": VowelInfo("ia", True),
    "เือ": VowelInfo("ɯa", True),
    "ัว": VowelInfo("ua", True),
    "ว": VowelInfo("ua", True),
    # Diphthongs (short)
    "เียะ": VowelInfo("ia", False),
    "เือะ": VowelInfo("ɯa", False),
    "ัวะ": VowelInfo("ua", False),
    # Special vowels ending in consonant
    "ไ": VowelInfo("aj", True),
    "ใ": VowelInfo("aj", True),
    "เา": VowelInfo("aw", True),
    # Inherent vowels (when no vowel written) - short 'o' or 'a'
    "": VowelInfo("o", False),
    # Vowel + ย ending (treated as long)
    "าย": VowelInfo("aːj", True),
    "อย": VowelInfo("ɔːj", True),
    "ัย": VowelInfo("aj", False),
    "ุย": VowelInfo("uj", False),
    "โย": VowelInfo("oːj", True),
    "เย": VowelInfo("ɤːj", True),
    "ูย": VowelInfo("uːj", True),
    "เือย": VowelInfo("ɯaj", True),
    # Vowel + ว ending
    "าว": VowelInfo("aːw", True),
    "เว": VowelInfo("eːw", True),
    "แว": VowelInfo("ɛːw", True),
    "เียว": VowelInfo("iaw", True),
    "ิว": VowelInfo("iw", False),
    # Short 'a' (written with ั or implied)
    "ั": VowelInfo("a", False),
    # Combination vowel
    "ำ": VowelInfo("am", False),
}

# Leading vowels that appear before the consonant graphically
LEADING_VOWELS = frozenset("เแโไใ")

# Vowels that appear above the consonant
ABOVE_VOWELS = frozenset("ิีึืั็")

# Vowels that appear below the consonant
BELOW_VOWELS = frozenset("ุู")

# Vowels that appear after the consonant
FOLLOWING_VOWELS = frozenset("ะาอำ")

# Tone marks
TONE_MARKS = {
    "\u0e48": "mai_ek",
    "\u0e49": "mai_tho",
    "\u0e4a": "mai_tri",
    "\u0e4b": "mai_chattawa",
}

MAI_EK = "\u0e48"
MAI_THO = "\u0e49"
MAI_TRI = "\u0e4a"
MAI_CHATTAWA = "\u0e4b"

# Thai digits
THAI_DIGITS = "๐๑๒๓๔๕๖๗๘๙"

# Punctuation and special characters
THAI_PUNCTUATION = "ๆฯ"

# Characters that mark end of syllable/word
SYLLABLE_FINAL_MARKERS = frozenset(" \n\t.,!?;:\"'()[]{}ๆฯ")

# Sonorant finals (make syllables "live")
SONORANT_FINALS = frozenset("มนงญณรลฬวย")

# Stop finals (make syllables "dead")
STOP_FINALS = frozenset("กขคฆจชซฌฎฏฐฑฒดตถทธบปผฝพฟภศษส")

# Common consonant clusters (first consonant)
CLUSTER_FIRST = frozenset("กขคตปผพ")

# Common consonant clusters (second consonant)
CLUSTER_SECOND = frozenset("รลว")

# Thai Unicode range
THAI_RANGE = range(0x0E00, 0x0E80)


def is_thai_char(char: str) -> bool:
    """Check if a character is in the Thai Unicode block."""
    return len(char) == 1 and ord(char) in THAI_RANGE


def is_consonant(char: str) -> bool:
    """Check if a character is a Thai consonant."""
    return char in CONSONANTS


def is_vowel_char(char: str) -> bool:
    """Check if a character is a Thai vowel character."""
    return char in LEADING_VOWELS | ABOVE_VOWELS | BELOW_VOWELS | FOLLOWING_VOWELS


def is_tone_mark(char: str) -> bool:
    """Check if a character is a Thai tone mark."""
    return char in TONE_MARKS


def get_consonant_class(char: str) -> ConsonantClass | None:
    """Get the consonant class of a Thai consonant."""
    if char in CONSONANTS:
        return CONSONANTS[char].consonant_class
    return None
