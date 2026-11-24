"""Shared data and utilities for Vietnamese G2P converters.

This module contains common code used by all Vietnamese dialect converters:
- Orthographic data (consonants, vowels, tone marks)
- Syllable parsing logic
- Base classes and utilities
"""

import re
import unicodedata
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Iterator


class Dialect(Enum):
    """Vietnamese dialect varieties."""
    HANOI = "hanoi"
    NGHE_AN = "nghe_an"
    SAI_GON = "sai_gon"


# Tone mark Unicode combining characters
TONE_MARKS = {
    "\u0300": "huyen",      # grave ̀  - huyền (falling)
    "\u0301": "sac",        # acute ́  - sắc (rising)
    "\u0303": "nga",        # tilde ̃  - ngã (creaky rising)
    "\u0309": "hoi",        # hook ̉  - hỏi (dipping-rising)
    "\u0323": "nang",       # dot below ̣ - nặng (heavy)
}

# Reverse mapping: name to combining character
TONE_MARK_CHARS = {v: k for k, v in TONE_MARKS.items()}

# No tone mark = ngang (level tone)
TONE_NGANG = "ngang"


# Vietnamese vowel letters (base, without tone marks)
VOWEL_CHARS = frozenset("aăâeêioôơuưyAĂÂEÊIOÔƠUƯY")

# All possible vowel base letters
VOWELS_BASE = {
    "a": "a", "A": "a",
    "ă": "ă", "Ă": "ă",
    "â": "â", "Â": "â",
    "e": "e", "E": "e",
    "ê": "ê", "Ê": "ê",
    "i": "i", "I": "i",
    "o": "o", "O": "o",
    "ô": "ô", "Ô": "ô",
    "ơ": "ơ", "Ơ": "ơ",
    "u": "u", "U": "u",
    "ư": "ư", "Ư": "ư",
    "y": "y", "Y": "y",
}

# Monophthong IPA mappings (base vowels)
VOWEL_IPA = {
    "a": "aː",
    "ă": "a",
    "â": "ə",
    "e": "ɛ",
    "ê": "e",
    "i": "i",
    "o": "ɔ",
    "ô": "o",
    "ơ": "əː",
    "u": "u",
    "ư": "ɨ",
    "y": "i",
}

# Diphthongs and their IPA (without coda)
DIPHTHONG_IPA = {
    "ai": "aːj",
    "ao": "aːw",
    "au": "aw",
    "âu": "əw",
    "ay": "aj",
    "ây": "əj",
    "eo": "ɛw",
    "êu": "ew",
    "ia": "iə",
    "iu": "iw",
    "oa": "waː",
    "oă": "wa",
    "oe": "wɛ",
    "oi": "ɔj",
    "ôi": "oj",
    "ơi": "əːj",
    "ua": "uə",
    "uâ": "wə",
    "ưa": "ɨə",
    "ui": "uj",
    "ưi": "ɨj",
    "uy": "wi",
}

# Diphthongs that change form before codas (iê vs ia, etc.)
DIPHTHONG_WITH_CODA = {
    "iê": "iə",
    "yê": "iə",
    "uô": "uə",
    "ươ": "ɨə",
}

# Triphthongs
TRIPHTHONG_IPA = {
    "iêu": "iəw",
    "yêu": "iəw",
    "oai": "waːj",
    "oay": "waj",
    "oao": "waːw",
    "oeo": "wɛw",
    "uôi": "uəj",
    "ươi": "ɨəj",
    "ươu": "ɨəw",
    "uya": "wiə",
    "uyê": "wiə",
    "uyu": "wiw",
}

# Onset consonants (orthographic -> base IPA, dialect differences handled separately)
ONSETS = {
    "b": "ɓ",
    "c": "k",
    "ch": "tɕ",
    "d": "z",       # Varies by dialect
    "đ": "ɗ",
    "g": "ɣ",
    "gh": "ɣ",
    "gi": "z",      # Varies by dialect
    "h": "h",
    "k": "k",
    "kh": "x",
    "l": "l",
    "m": "m",
    "n": "n",
    "ng": "ŋ",
    "ngh": "ŋ",
    "nh": "ɲ",
    "p": "p",
    "ph": "f",
    "qu": "kw",
    "r": "z",       # Varies by dialect
    "s": "s",       # Varies by dialect
    "t": "t",
    "th": "tʰ",
    "tr": "tɕ",     # Varies by dialect
    "v": "v",       # Varies by dialect
    "x": "s",
}

# Coda consonants (orthographic -> base IPA)
CODAS = {
    "c": "k",
    "ch": "k",      # Varies by dialect
    "m": "m",
    "n": "n",
    "ng": "ŋ",
    "nh": "ɲ",      # Varies by dialect
    "p": "p",
    "t": "t",
}

# Semivowel codas
SEMIVOWEL_CODAS = {
    "i": "j",
    "y": "j",
    "o": "w",
    "u": "w",
}

# Stop codas (checked syllables - restrict tones)
STOP_CODAS = frozenset(["p", "t", "c", "ch"])


# All vowels including those with tone marks (precomposed forms)
# Base vowels: a ă â e ê i o ô ơ u ư y
# Each can have: grave, acute, hook above, tilde, dot below
VOWELS_WITH_TONES = (
    "aàáảãạăằắẳẵặâầấẩẫậ"
    "eèéẻẽẹêềếểễệ"
    "iìíỉĩị"
    "oòóỏõọôồốổỗộơờớởỡợ"
    "uùúủũụưừứửữự"
    "yỳýỷỹỵ"
)

# Regex pattern for parsing Vietnamese syllables
# Order matters: longer patterns first
ONSET_PATTERN = r"(?P<onset>ngh|ng|nh|ch|gh|gi|kh|ph|qu|th|tr|[bcdđghjklmnprstvx])?"
NUCLEUS_PATTERN = r"(?P<nucleus>[" + VOWELS_WITH_TONES + r"]+)"
CODA_PATTERN = r"(?P<coda>ng|nh|ch|[cmnpt]|[iyu])?"

SYLLABLE_REGEX = re.compile(
    ONSET_PATTERN + NUCLEUS_PATTERN + CODA_PATTERN,
    re.IGNORECASE
)


def normalize_vietnamese(text: str) -> str:
    """Normalize Vietnamese text to NFC form for consistent processing."""
    return unicodedata.normalize("NFC", text)


def decompose_char(char: str) -> tuple[str, str | None]:
    """Decompose a Vietnamese character into base + tone mark.
    
    Returns: (base_char, tone_mark) where tone_mark is None for ngang tone.
    """
    decomposed = unicodedata.normalize("NFD", char)
    base = ""
    tone = None
    
    for c in decomposed:
        if c in TONE_MARKS:
            tone = c
        else:
            base += c
    
    # Re-compose base without tone (handles ă, â, etc.)
    base = unicodedata.normalize("NFC", base)
    return base, tone


def extract_tone_from_nucleus(nucleus: str) -> tuple[str, str]:
    """Extract tone mark from nucleus and return (clean_nucleus, tone_name).
    
    Returns: (nucleus_without_tone, tone_name)
    """
    tone_name = TONE_NGANG
    clean_chars = []
    
    for char in nucleus:
        base, tone_mark = decompose_char(char)
        clean_chars.append(base)
        if tone_mark is not None:
            tone_name = TONE_MARKS[tone_mark]
    
    return "".join(clean_chars), tone_name


def is_vietnamese_char(char: str) -> bool:
    """Check if a character is a Vietnamese letter."""
    # Check if it's a vowel with or without tone mark
    if char.lower() in VOWELS_WITH_TONES:
        return True
    base, _ = decompose_char(char)
    return base.lower() in VOWELS_BASE or base.lower() in "bcdfghjklmnpqrstvxđ"


@dataclass
class Syllable:
    """Represents a parsed Vietnamese syllable."""
    
    onset: str
    nucleus: str
    coda: str
    tone: str
    raw: str
    
    @property
    def is_checked(self) -> bool:
        """Check if syllable ends in a stop (p, t, c, ch)."""
        return self.coda.lower() in STOP_CODAS


def parse_syllable(text: str, pos: int = 0) -> tuple[Syllable | None, int]:
    """Parse a single Vietnamese syllable starting at position.
    
    Returns: (Syllable or None, new position)
    """
    # Skip non-Vietnamese characters
    while pos < len(text) and not is_vietnamese_char(text[pos]):
        pos += 1
    
    if pos >= len(text):
        return None, pos
    
    start_pos = pos
    
    # Find the end of this syllable (until space or non-Vietnamese char)
    end_pos = pos
    while end_pos < len(text):
        char = text[end_pos]
        if char.isspace() or (not is_vietnamese_char(char) and char not in "̣̀́̃̉"):
            break
        end_pos += 1
    
    syllable_text = text[start_pos:end_pos]
    if not syllable_text:
        return None, pos + 1
    
    # Normalize and try to match
    normalized = normalize_vietnamese(syllable_text.lower())
    match = SYLLABLE_REGEX.fullmatch(normalized)
    
    if not match:
        # Try to handle as simple vowel
        clean_nucleus, tone = extract_tone_from_nucleus(normalized)
        if clean_nucleus and all(c in VOWELS_BASE for c in clean_nucleus):
            return Syllable(
                onset="",
                nucleus=clean_nucleus,
                coda="",
                tone=tone,
                raw=syllable_text,
            ), end_pos
        return None, end_pos
    
    onset = match.group("onset") or ""
    raw_nucleus = match.group("nucleus") or ""
    coda = match.group("coda") or ""
    
    # Handle 'gi' onset special case - the 'i' might be part of nucleus
    if onset == "gi" and raw_nucleus and raw_nucleus[0] not in "iIyY":
        # 'gi' is onset, nucleus starts with non-i vowel
        pass
    elif onset == "gi" and (not raw_nucleus or raw_nucleus[0] in "iIyY"):
        # Could be 'g' + 'i...' nucleus or 'gi' + 'i...'
        # If nucleus is just 'i', treat 'gi' as onset
        if raw_nucleus == "i" or raw_nucleus == "":
            # gi + (optional coda) - keep as is
            if not raw_nucleus:
                raw_nucleus = "i"
                onset = "g"
    
    # Handle 'qu' - the 'u' is part of onset (labialized)
    if onset == "qu":
        # qu is treated as /kw/, nucleus follows
        pass
    
    # Extract tone from nucleus
    clean_nucleus, tone = extract_tone_from_nucleus(raw_nucleus)
    
    # Handle semivowel codas that might be part of nucleus
    if not coda and clean_nucleus:
        last_char = clean_nucleus[-1].lower()
        if len(clean_nucleus) > 1 and last_char in "iouy":
            # Could be diphthong ending
            potential_nucleus = clean_nucleus[:-1]
            potential_coda = last_char
            # Only split if remaining nucleus is valid
            if potential_nucleus and all(c.lower() in VOWELS_BASE for c in potential_nucleus):
                clean_nucleus = potential_nucleus
                coda = potential_coda
    
    return Syllable(
        onset=onset,
        nucleus=clean_nucleus,
        coda=coda,
        tone=tone,
        raw=syllable_text,
    ), end_pos


def parse_syllables(text: str) -> Iterator[Syllable]:
    """Parse Vietnamese text into syllables."""
    text = normalize_vietnamese(text)
    pos = 0
    while pos < len(text):
        syllable, new_pos = parse_syllable(text, pos)
        if syllable is None:
            pos = new_pos + 1 if new_pos == pos else new_pos
            continue
        yield syllable
        pos = new_pos


def get_nucleus_ipa(nucleus: str, coda: str) -> str:
    """Get IPA for a vowel nucleus, considering coda presence.
    
    Args:
        nucleus: The vowel nucleus (without tone mark)
        coda: The coda consonant (may affect vowel realization)
        
    Returns:
        IPA string for the nucleus
    """
    nucleus = nucleus.lower()
    
    # Check triphthongs first (longest match)
    if nucleus in TRIPHTHONG_IPA:
        return TRIPHTHONG_IPA[nucleus]
    
    # Check diphthongs with coda forms
    if nucleus in DIPHTHONG_WITH_CODA and coda:
        return DIPHTHONG_WITH_CODA[nucleus]
    
    # Check regular diphthongs
    if nucleus in DIPHTHONG_IPA:
        return DIPHTHONG_IPA[nucleus]
    
    # Build from individual vowels
    result = []
    for char in nucleus:
        char_lower = char.lower()
        if char_lower in VOWEL_IPA:
            result.append(VOWEL_IPA[char_lower])
    
    return "".join(result) if result else nucleus


class VietnameseG2PBase(ABC):
    """Base class for Vietnamese G2P converters."""
    
    def __init__(self, include_tones: bool = True):
        """Initialize the Vietnamese G2P converter.
        
        Args:
            include_tones: Whether to include Chao tone letters in output.
        """
        self.include_tones = include_tones
    
    @property
    @abstractmethod
    def dialect(self) -> Dialect:
        """Return the dialect this converter handles."""
        pass
    
    @abstractmethod
    def get_onset_ipa(self, onset: str) -> str:
        """Get IPA for onset consonant in this dialect."""
        pass
    
    @abstractmethod
    def get_coda_ipa(self, coda: str, nucleus: str) -> str:
        """Get IPA for coda consonant in this dialect."""
        pass
    
    @abstractmethod
    def get_tone_chao(self, tone: str, is_checked: bool) -> str:
        """Get Chao tone letter for this dialect."""
        pass
    
    def _syllable_to_ipa(self, syllable: Syllable) -> str:
        """Convert a parsed syllable to IPA string."""
        parts = []
        
        # Onset
        if syllable.onset:
            onset_ipa = self.get_onset_ipa(syllable.onset)
            parts.append(onset_ipa)
        else:
            # Null onset = glottal stop
            parts.append("ʔ")
        
        # Nucleus
        nucleus_ipa = get_nucleus_ipa(syllable.nucleus, syllable.coda)
        parts.append(nucleus_ipa)
        
        # Coda
        if syllable.coda:
            coda_ipa = self.get_coda_ipa(syllable.coda, syllable.nucleus)
            if coda_ipa:
                parts.append(coda_ipa)
        
        # Tone
        if self.include_tones:
            tone_chao = self.get_tone_chao(syllable.tone, syllable.is_checked)
            parts.append(tone_chao)
        
        return "".join(parts)
    
    def _syllable_to_tokens(self, syllable: Syllable) -> list[str]:
        """Convert a parsed syllable to list of IPA tokens."""
        tokens = []
        
        # Onset
        if syllable.onset:
            tokens.append(self.get_onset_ipa(syllable.onset))
        else:
            tokens.append("ʔ")
        
        # Nucleus
        nucleus_ipa = get_nucleus_ipa(syllable.nucleus, syllable.coda)
        tokens.append(nucleus_ipa)
        
        # Coda
        if syllable.coda:
            coda_ipa = self.get_coda_ipa(syllable.coda, syllable.nucleus)
            if coda_ipa:
                tokens.append(coda_ipa)
        
        # Tone
        if self.include_tones:
            tone_chao = self.get_tone_chao(syllable.tone, syllable.is_checked)
            tokens.append(tone_chao)
        
        return tokens
    
    def transliterate(self, text: str) -> str:
        """Convert Vietnamese text to IPA transcription.
        
        Args:
            text: Vietnamese text to transliterate.
            
        Returns:
            IPA transcription with Chao tone letters.
        """
        result = []
        pos = 0
        text = normalize_vietnamese(text)
        syllables = list(parse_syllables(text))
        
        for syllable in syllables:
            # Find where this syllable appears in original text
            start = text.find(syllable.raw, pos)
            if start == -1:
                start = pos
            
            # Add non-Vietnamese text between syllables
            if start > pos:
                result.append(text[pos:start])
            
            ipa = self._syllable_to_ipa(syllable)
            result.append(ipa)
            pos = start + len(syllable.raw)
        
        # Add trailing non-Vietnamese text
        if pos < len(text):
            result.append(text[pos:])
        
        return "".join(result)
    
    def transliterate_tokenized(self, text: str) -> list[str]:
        """Convert Vietnamese text to tokenized IPA segments.
        
        Args:
            text: Vietnamese text to transliterate.
            
        Returns:
            List of IPA tokens (segments and tones).
        """
        tokens = []
        
        for syllable in parse_syllables(text):
            tokens.extend(self._syllable_to_tokens(syllable))
        
        return tokens
