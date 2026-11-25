"""Hmong RPA (Romanized Popular Alphabet) G2P converter.

Supports two dialects:
- Hmong Daw (White Hmong)
- Mong Leng (Green/Blue Hmong, Mong Njua)

RPA orthography notes:
- Tone is marked by a final consonant letter (b, j, v, s, g, m, d) or absence
- Doubled vowels ee, oo, aa represent nasalized vowels
- The -g tone indicates breathy/murmured phonation on the vowel
- Consonant clusters use standard letters: pl, tl, etc.
"""

from dataclasses import dataclass
from typing import Iterator

from epitone.hmong.data import (
    HMONG_DAW_TONES,
    HmongDialect,
    MONG_LENG_TONES,
    RPA_CONSONANTS,
    RPA_CONSONANTS_BY_LENGTH,
    RPA_TONE_LETTERS,
    RPA_VOWELS,
    RPA_VOWELS_BY_LENGTH,
    add_breathy_voice,
    is_rpa_consonant_char,
    is_rpa_tone_letter,
    is_rpa_vowel_char,
    normalize_text,
)
from epitone.unicode_utils import to_nfd


@dataclass
class Syllable:
    """Represents a parsed Hmong RPA syllable.
    
    Hmong syllables have the structure: (C)(C)V(V)(T)
    - One or two initial consonants (onset)
    - One or two vowels (nucleus)
    - Optional tone letter (determines tone and sometimes phonation)
    """
    
    onset: str            # Initial consonant(s) in RPA orthography
    nucleus: str          # Vowel(s) in RPA orthography
    tone_letter: str      # Tone letter (b, j, v, s, g, m, d, or "")
    raw: str              # Original text
    
    @property
    def tone_name(self) -> str:
        """Get the tone name from the tone letter."""
        return RPA_TONE_LETTERS.get(self.tone_letter, "mid")
    
    @property
    def is_breathy(self) -> bool:
        """Check if this syllable has breathy phonation (-g tone)."""
        return self.tone_letter == "g"
    
    @property 
    def is_nasal_vowel(self) -> bool:
        """Check if the nucleus is a nasal vowel (ee, oo, aa)."""
        return self.nucleus.lower() in ("ee", "oo", "aa")


def _match_onset(text: str, pos: int) -> tuple[str, int]:
    """Match the longest possible onset consonant(s) at position.
    
    Returns: (onset_str, new_position)
    """
    text_lower = text.lower()
    
    for consonant in RPA_CONSONANTS_BY_LENGTH:
        if not consonant:  # Skip empty string
            continue
        end_pos = pos + len(consonant)
        if end_pos <= len(text) and text_lower[pos:end_pos] == consonant:
            # Verify it's not followed by another consonant that would form a longer match
            # This is handled by sorting by length, so first match is longest
            return consonant, end_pos
    
    # No consonant found - could be vowel-initial syllable
    return "", pos


def _match_nucleus(text: str, pos: int) -> tuple[str, int]:
    """Match the vowel nucleus at position.
    
    Returns: (nucleus_str, new_position)
    """
    if pos >= len(text):
        return "", pos
    
    text_lower = text.lower()
    
    # Try matching longest vowel patterns first
    for vowel in RPA_VOWELS_BY_LENGTH:
        end_pos = pos + len(vowel)
        if end_pos <= len(text) and text_lower[pos:end_pos] == vowel:
            return vowel, end_pos
    
    # Try single vowel character
    char = text_lower[pos]
    if is_rpa_vowel_char(char):
        return char, pos + 1
    
    return "", pos


def _match_tone_letter(text: str, pos: int) -> tuple[str, int]:
    """Match a tone letter at position.
    
    Tone letters: b, j, v, s, g, m, d
    No tone letter = mid tone
    
    Returns: (tone_letter, new_position)
    """
    if pos >= len(text):
        return "", pos
    
    char = text[pos].lower()
    
    # Check if this is a tone letter
    if is_rpa_tone_letter(char):
        # Verify it's at syllable boundary (followed by space, end, or consonant)
        next_pos = pos + 1
        if next_pos >= len(text):
            return char, next_pos
        
        next_char = text[next_pos]
        # Tone letter is valid if followed by space, punctuation, or new word
        if next_char.isspace() or not next_char.isalpha():
            return char, next_pos
        
        # Could be followed by consonant (new syllable) - check if next is a consonant pattern
        if is_rpa_consonant_char(next_char) and not is_rpa_vowel_char(next_char):
            return char, next_pos
        
        # If followed by a vowel, this might not be a tone letter but part of next word
        # However, in RPA, tone letters are always at syllable end
        # Let's be conservative and treat it as a tone letter
        return char, next_pos
    
    return "", pos


def parse_syllable(text: str, pos: int = 0) -> tuple[Syllable | None, int]:
    """Parse a single Hmong RPA syllable starting at position.
    
    Returns: (Syllable or None, new position)
    """
    # Skip whitespace and non-alphabetic characters
    while pos < len(text) and (text[pos].isspace() or not text[pos].isalpha()):
        pos += 1
    
    if pos >= len(text):
        return None, pos
    
    start_pos = pos
    
    # 1. Match onset consonant(s)
    onset, pos = _match_onset(text, pos)
    
    # 2. Match nucleus vowel(s) - required
    nucleus, pos = _match_nucleus(text, pos)
    
    if not nucleus:
        # No vowel found - not a valid syllable
        # Might be just a consonant or malformed input
        return None, start_pos + 1
    
    # 3. Match optional tone letter
    tone_letter, pos = _match_tone_letter(text, pos)
    
    raw = text[start_pos:pos]
    
    return Syllable(
        onset=onset,
        nucleus=nucleus,
        tone_letter=tone_letter,
        raw=raw,
    ), pos


def parse_syllables(text: str) -> Iterator[Syllable]:
    """Parse Hmong RPA text into syllables."""
    text = normalize_text(text)
    pos = 0
    
    while pos < len(text):
        syllable, new_pos = parse_syllable(text, pos)
        
        if syllable is None:
            pos = new_pos if new_pos > pos else pos + 1
            continue
        
        yield syllable
        pos = new_pos


class HmongRPAG2P:
    """Base class for Hmong RPA G2P converters.
    
    Handles both Hmong Daw and Mong Leng dialects.
    """
    
    def __init__(
        self,
        dialect: HmongDialect = HmongDialect.HMONG_DAW,
        include_tones: bool = True,
    ):
        """Initialize the Hmong RPA G2P converter.
        
        Args:
            dialect: Which Hmong dialect to use (HMONG_DAW or MONG_LENG)
            include_tones: Whether to include Chao tone letters in output
        """
        if dialect not in (HmongDialect.HMONG_DAW, HmongDialect.MONG_LENG):
            raise ValueError(f"RPA converter only supports HMONG_DAW and MONG_LENG, not {dialect}")
        
        self.dialect = dialect
        self.include_tones = include_tones
        
        # Select tone mapping based on dialect
        self._tone_map = (
            HMONG_DAW_TONES if dialect == HmongDialect.HMONG_DAW else MONG_LENG_TONES
        )
    
    def _get_onset_ipa(self, onset: str) -> str:
        """Get IPA for onset consonant(s)."""
        onset_lower = onset.lower()
        
        if onset_lower in RPA_CONSONANTS:
            return RPA_CONSONANTS[onset_lower]
        
        # Default to glottal stop for empty onset
        if not onset:
            return "ʔ"
        
        return onset  # Return as-is if unknown
    
    def _get_nucleus_ipa(self, nucleus: str, is_breathy: bool) -> str:
        """Get IPA for vowel nucleus.
        
        Args:
            nucleus: The vowel nucleus in RPA
            is_breathy: Whether to add breathy voice diacritic
            
        Returns:
            IPA string for the nucleus
        """
        nucleus_lower = nucleus.lower()
        
        if nucleus_lower in RPA_VOWELS:
            ipa, _ = RPA_VOWELS[nucleus_lower]
        else:
            # Fallback - try to build from individual vowels
            ipa = nucleus_lower
        
        # Add breathy voice marker if this is a -g tone syllable
        if is_breathy:
            ipa = add_breathy_voice(ipa)
        
        return ipa
    
    def _get_tone_chao(self, tone_name: str) -> str:
        """Get Chao tone letter for the given tone name."""
        return self._tone_map.get(tone_name, "˧")  # Default to mid
    
    def _syllable_to_ipa(self, syllable: Syllable) -> str:
        """Convert a parsed syllable to IPA string."""
        parts = []
        
        # Onset
        if syllable.onset:
            parts.append(self._get_onset_ipa(syllable.onset))
        else:
            parts.append(self._get_onset_ipa(""))  # Glottal stop
        
        # Nucleus (with breathy voice if -g tone)
        nucleus_ipa = self._get_nucleus_ipa(syllable.nucleus, syllable.is_breathy)
        parts.append(nucleus_ipa)
        
        # Tone
        if self.include_tones:
            tone_chao = self._get_tone_chao(syllable.tone_name)
            parts.append(tone_chao)
        
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
        nucleus_ipa = self._get_nucleus_ipa(syllable.nucleus, syllable.is_breathy)
        tokens.append(nucleus_ipa)
        
        # Tone
        if self.include_tones:
            tokens.append(self._get_tone_chao(syllable.tone_name))
        
        return tokens
    
    def transliterate(self, text: str) -> str:
        """Convert Hmong RPA text to IPA transcription.
        
        Args:
            text: Hmong text in RPA orthography
            
        Returns:
            IPA transcription with Chao tone letters in NFD form
        """
        result = []
        pos = 0
        text = normalize_text(text)
        
        while pos < len(text):
            # Preserve whitespace and punctuation
            if text[pos].isspace() or not text[pos].isalpha():
                result.append(text[pos])
                pos += 1
                continue
            
            # Try to parse a syllable
            syllable, new_pos = parse_syllable(text, pos)
            
            if syllable is None:
                # No valid syllable, preserve character
                result.append(text[pos])
                pos = new_pos if new_pos > pos else pos + 1
                continue
            
            # Convert syllable to IPA
            ipa = self._syllable_to_ipa(syllable)
            result.append(ipa)
            pos = new_pos
        
        return to_nfd("".join(result))
    
    def transliterate_tokenized(self, text: str) -> list[str]:
        """Convert Hmong RPA text to tokenized IPA segments.
        
        Args:
            text: Hmong text in RPA orthography
            
        Returns:
            List of IPA tokens (segments and tones) in NFD form
        """
        tokens = []
        
        for syllable in parse_syllables(text):
            tokens.extend(self._syllable_to_tokens(syllable))
        
        return [to_nfd(token) for token in tokens]


class HmongDawG2P(HmongRPAG2P):
    """G2P converter for Hmong Daw (White Hmong) using RPA orthography.
    
    Example usage:
        >>> g2p = HmongDawG2P()
        >>> g2p.transliterate("kuv")
        'kuv˨˦'
        >>> g2p.transliterate("peb")
        'pe˥'
        >>> g2p.transliterate("noog")  # Nasal vowel + breathy tone
        'nɔ̤̃˨'
    """
    
    def __init__(self, include_tones: bool = True):
        """Initialize the Hmong Daw G2P converter.
        
        Args:
            include_tones: Whether to include Chao tone letters in output
        """
        super().__init__(dialect=HmongDialect.HMONG_DAW, include_tones=include_tones)


class MongLengG2P(HmongRPAG2P):
    """G2P converter for Mong Leng (Green/Blue Hmong, Mong Njua) using RPA.
    
    Example usage:
        >>> g2p = MongLengG2P()
        >>> g2p.transliterate("kuv")
        'kuv˨˦'
        >>> g2p.transliterate("peb")
        'pe˥˧'
        >>> g2p.transliterate("noog")  # Nasal vowel + breathy tone
        'nɔ̤̃˧'
    """
    
    def __init__(self, include_tones: bool = True):
        """Initialize the Mong Leng G2P converter.
        
        Args:
            include_tones: Whether to include Chao tone letters in output
        """
        super().__init__(dialect=HmongDialect.MONG_LENG, include_tones=include_tones)
