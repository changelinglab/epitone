"""Hmong Dananshan Miao G2P converter.

Dananshan is a Pinyin-based orthography used for Hmong/Miao languages in China.
It uses numeric tone marks (1-8) at the end of syllables.

References:
- https://en.wikipedia.org/wiki/Hmong_language
- https://en.wikipedia.org/wiki/Dananshan_Miao_language
"""

from dataclasses import dataclass
from typing import Iterator

from epitone.hmong.data import (
    DANANSHAN_CONSONANTS,
    DANANSHAN_CONSONANTS_BY_LENGTH,
    DANANSHAN_TONES,
    DANANSHAN_VOWELS,
    DANANSHAN_VOWELS_BY_LENGTH,
    HmongDialect,
    is_dananshan_tone_digit,
    normalize_text,
)
from epitone.unicode_utils import to_nfd


@dataclass
class Syllable:
    """Represents a parsed Dananshan Miao syllable.
    
    Dananshan syllables have the structure: (C)(C)V(V)(T)
    - One or two initial consonants
    - One or two vowels (including diphthongs)
    - Tone digit (1-8)
    """
    
    onset: str            # Initial consonant(s)
    nucleus: str          # Vowel(s)
    tone_digit: str       # Tone number (1-8, or "" for default)
    raw: str              # Original text


def _match_onset(text: str, pos: int) -> tuple[str, int]:
    """Match the longest possible onset consonant(s) at position.
    
    Returns: (onset_str, new_position)
    """
    text_lower = text.lower()
    
    for consonant in DANANSHAN_CONSONANTS_BY_LENGTH:
        if not consonant:  # Skip empty string
            continue
        end_pos = pos + len(consonant)
        if end_pos <= len(text) and text_lower[pos:end_pos] == consonant:
            return consonant, end_pos
    
    # No consonant found
    return "", pos


def _match_nucleus(text: str, pos: int) -> tuple[str, int]:
    """Match the vowel nucleus at position.
    
    Returns: (nucleus_str, new_position)
    """
    if pos >= len(text):
        return "", pos
    
    text_lower = text.lower()
    
    # Try matching longest vowel patterns first (diphthongs, triphthongs)
    for vowel in DANANSHAN_VOWELS_BY_LENGTH:
        end_pos = pos + len(vowel)
        if end_pos <= len(text) and text_lower[pos:end_pos] == vowel:
            return vowel, end_pos
    
    # Try single vowel
    char = text_lower[pos]
    if char in "aeiouüyw":
        return char, pos + 1
    
    return "", pos


def _match_tone_digit(text: str, pos: int) -> tuple[str, int]:
    """Match a tone digit (1-8) at position.
    
    Returns: (tone_digit, new_position)
    """
    if pos >= len(text):
        return "", pos
    
    char = text[pos]
    
    if is_dananshan_tone_digit(char):
        return char, pos + 1
    
    return "", pos


def parse_syllable(text: str, pos: int = 0) -> tuple[Syllable | None, int]:
    """Parse a single Dananshan syllable starting at position.
    
    Returns: (Syllable or None, new position)
    """
    # Skip whitespace and non-letter characters (except digits for tones)
    while pos < len(text) and text[pos].isspace():
        pos += 1
    
    if pos >= len(text):
        return None, pos
    
    # Skip if starting with a digit that's not part of a syllable
    if text[pos].isdigit() and (pos == 0 or not text[pos-1].isalpha()):
        return None, pos + 1
    
    start_pos = pos
    
    # 1. Match onset consonant(s)
    onset, pos = _match_onset(text, pos)
    
    # 2. Match nucleus vowel(s) - required
    nucleus, pos = _match_nucleus(text, pos)
    
    if not nucleus:
        # No vowel found - not a valid syllable
        return None, start_pos + 1 if start_pos < len(text) else start_pos
    
    # 3. Match optional tone digit (1-8)
    tone_digit, pos = _match_tone_digit(text, pos)
    
    raw = text[start_pos:pos]
    
    return Syllable(
        onset=onset,
        nucleus=nucleus,
        tone_digit=tone_digit,
        raw=raw,
    ), pos


def parse_syllables(text: str) -> Iterator[Syllable]:
    """Parse Dananshan text into syllables."""
    text = normalize_text(text)
    pos = 0
    
    while pos < len(text):
        syllable, new_pos = parse_syllable(text, pos)
        
        if syllable is None:
            pos = new_pos if new_pos > pos else pos + 1
            continue
        
        yield syllable
        pos = new_pos


class DananshanG2P:
    """G2P converter for Dananshan Miao orthography.
    
    Example usage:
        >>> g2p = DananshanG2P()
        >>> g2p.transliterate("ba1")
        'pa˦˦'
        >>> g2p.transliterate("ma3")
        'ma˦˧'
    """
    
    def __init__(self, include_tones: bool = True):
        """Initialize the Dananshan G2P converter.
        
        Args:
            include_tones: Whether to include Chao tone letters in output
        """
        self.dialect = HmongDialect.DANANSHAN
        self.include_tones = include_tones
    
    def _get_onset_ipa(self, onset: str) -> str:
        """Get IPA for onset consonant(s)."""
        onset_lower = onset.lower()
        
        if onset_lower in DANANSHAN_CONSONANTS:
            return DANANSHAN_CONSONANTS[onset_lower]
        
        # Default to glottal stop for empty onset
        if not onset:
            return "ʔ"
        
        return onset  # Return as-is if unknown
    
    def _get_nucleus_ipa(self, nucleus: str) -> str:
        """Get IPA for vowel nucleus."""
        nucleus_lower = nucleus.lower()
        
        if nucleus_lower in DANANSHAN_VOWELS:
            return DANANSHAN_VOWELS[nucleus_lower]
        
        return nucleus_lower  # Return as-is if unknown
    
    def _get_tone_chao(self, tone_digit: str) -> str:
        """Get Chao tone letter for the given tone digit."""
        return DANANSHAN_TONES.get(tone_digit, DANANSHAN_TONES[""])
    
    def _syllable_to_ipa(self, syllable: Syllable) -> str:
        """Convert a parsed syllable to IPA string."""
        parts = []
        
        # Onset
        if syllable.onset:
            parts.append(self._get_onset_ipa(syllable.onset))
        else:
            parts.append(self._get_onset_ipa(""))  # Glottal stop
        
        # Nucleus
        parts.append(self._get_nucleus_ipa(syllable.nucleus))
        
        # Tone
        if self.include_tones:
            parts.append(self._get_tone_chao(syllable.tone_digit))
        
        return "".join(parts)
    
    def _syllable_to_tokens(self, syllable: Syllable) -> list[str]:
        """Convert a parsed syllable to list of IPA tokens."""
        tokens = []
        
        # Onset
        if syllable.onset:
            tokens.append(self._get_onset_ipa(syllable.onset))
        else:
            tokens.append(self._get_onset_ipa(""))
        
        # Nucleus
        tokens.append(self._get_nucleus_ipa(syllable.nucleus))
        
        # Tone
        if self.include_tones:
            tokens.append(self._get_tone_chao(syllable.tone_digit))
        
        return tokens
    
    def transliterate(self, text: str) -> str:
        """Convert Dananshan text to IPA transcription.
        
        Args:
            text: Hmong text in Dananshan orthography
            
        Returns:
            IPA transcription with Chao tone letters in NFD form
        """
        result = []
        pos = 0
        text = normalize_text(text)
        
        while pos < len(text):
            # Preserve whitespace
            if text[pos].isspace():
                result.append(text[pos])
                pos += 1
                continue
            
            # Try to parse a syllable
            syllable, new_pos = parse_syllable(text, pos)
            
            if syllable is None:
                # No valid syllable, preserve character (unless it's a stray digit)
                if not text[pos].isdigit():
                    result.append(text[pos])
                pos = new_pos if new_pos > pos else pos + 1
                continue
            
            # Convert syllable to IPA
            ipa = self._syllable_to_ipa(syllable)
            result.append(ipa)
            pos = new_pos
        
        return to_nfd("".join(result))
    
    def transliterate_tokenized(self, text: str) -> list[str]:
        """Convert Dananshan text to tokenized IPA segments.
        
        Args:
            text: Hmong text in Dananshan orthography
            
        Returns:
            List of IPA tokens (segments and tones) in NFD form
        """
        tokens = []
        
        for syllable in parse_syllables(text):
            tokens.extend(self._syllable_to_tokens(syllable))
        
        return [to_nfd(token) for token in tokens]
