"""Yoruba G2P (Grapheme-to-Phoneme) converter.

Converts Yoruba orthography to IPA transcription with:
- Chao tone letters at the end of each syllable
- Tie bar (͡) for affricates (j → d͡ʒ) and labiovelars (gb → ɡ͡b, p → k͡p)
- Syllabicity mark (̩) for syllabic nasals
"""

import unicodedata
from dataclasses import dataclass
from typing import Iterator

from epitone.yoruba.data import (
    ALL_CONSONANTS,
    ALL_VOWELS,
    CONSONANTS,
    DIGRAPHS,
    NASAL_VOWELS,
    NASALIZABLE_VOWELS,
    SYLLABIC,
    TONE_TO_CHAO,
    Tone,
    decompose_char,
    get_consonant_ipa,
    get_tone_from_char,
    get_vowel_ipa,
    is_consonant,
    is_nasal,
    is_vowel,
    is_yoruba_char,
    normalize_yoruba,
    strip_tone,
)


@dataclass
class Syllable:
    """Represents a parsed Yoruba syllable.
    
    Yoruba has strict (C)V syllable structure:
    - V: vowel only
    - CV: consonant + vowel
    - N: syllabic nasal (m̩ or n̩)
    """
    
    onset: str           # Consonant onset (may be empty or digraph)
    nucleus: str         # Vowel nucleus (or nasal for syllabic nasal)
    tone: str            # Tone.HIGH, Tone.MID, or Tone.LOW
    is_nasal_vowel: bool # Whether the vowel is nasalized
    is_syllabic_nasal: bool  # Whether this is a syllabic nasal (m̩/n̩)
    raw: str             # Original text
    
    @property
    def onset_ipa(self) -> str:
        """Get IPA for onset consonant."""
        if not self.onset:
            return ""
        return get_consonant_ipa(self.onset)
    
    @property
    def nucleus_ipa(self) -> str:
        """Get IPA for nucleus."""
        if self.is_syllabic_nasal:
            # Syllabic nasal: add syllabicity mark
            base = strip_tone(self.nucleus).lower()
            ipa = CONSONANTS.get(base, base)
            return ipa + SYLLABIC
        return get_vowel_ipa(self.nucleus, self.is_nasal_vowel)
    
    @property
    def tone_chao(self) -> str:
        """Get Chao tone letter."""
        return TONE_TO_CHAO.get(self.tone, TONE_TO_CHAO[Tone.MID])


def _is_syllabic_nasal_context(text: str, pos: int) -> bool:
    """Check if nasal at position is syllabic (carries tone, before consonant or word boundary).
    
    A nasal is syllabic if:
    1. It has a tone mark (high or low), AND
    2. It's followed by a consonant or word boundary (not a vowel)
    """
    if pos >= len(text):
        return False
    
    char = text[pos]
    base = strip_tone(char).lower()
    
    if base not in ("m", "n"):
        return False
    
    # Check if it has a tone mark
    tone = get_tone_from_char(char)
    if tone == Tone.MID:
        # Mid tone nasals without explicit marks are ambiguous
        # Check if followed by consonant (then likely syllabic)
        next_pos = pos + 1
        if next_pos >= len(text):
            return False  # Word-final, could be part of nasal vowel
        next_char = text[next_pos]
        # If followed by consonant (not vowel), could be syllabic
        if is_consonant(next_char) and not is_vowel(next_char):
            return True
        return False
    
    # Has explicit tone mark - likely syllabic if not followed by vowel
    next_pos = pos + 1
    if next_pos >= len(text) or not is_yoruba_char(text[next_pos]):
        return True  # End of word
    
    next_char = text[next_pos]
    return not is_vowel(next_char)


def _check_nasal_vowel(text: str, vowel_pos: int, n_pos: int) -> bool:
    """Check if vowel + n forms a nasal vowel.
    
    Nasal vowels occur when:
    1. The vowel is nasalizable (a, ẹ, i, ọ, u)
    2. 'n' follows the vowel
    3. 'n' is at word end OR followed by a consonant (not a vowel)
    """
    vowel_base = strip_tone(text[vowel_pos]).lower()
    
    if vowel_base not in NASALIZABLE_VOWELS:
        return False
    
    if n_pos >= len(text) or text[n_pos].lower() != "n":
        return False
    
    # Check what follows 'n'
    after_n = n_pos + 1
    if after_n >= len(text):
        return True  # Word-final 'n' after nasalizable vowel
    
    next_char = text[after_n]
    if not is_yoruba_char(next_char):
        return True  # End of Yoruba text (space, punctuation, etc.)
    
    # 'n' followed by consonant = nasal vowel
    # 'n' followed by vowel = separate syllable
    return is_consonant(next_char)


def parse_syllable(text: str, pos: int = 0) -> tuple[Syllable | None, int]:
    """Parse a single Yoruba syllable starting at position.
    
    Returns: (Syllable or None, new position)
    """
    # Skip non-Yoruba characters
    while pos < len(text) and not is_yoruba_char(text[pos]):
        pos += 1
    
    if pos >= len(text):
        return None, pos
    
    start_pos = pos
    char = text[pos]
    char_lower = strip_tone(char).lower()
    
    # Check for syllabic nasal first
    if _is_syllabic_nasal_context(text, pos):
        tone = get_tone_from_char(char)
        return Syllable(
            onset="",
            nucleus=char,
            tone=tone,
            is_nasal_vowel=False,
            is_syllabic_nasal=True,
            raw=char,
        ), pos + 1
    
    onset = ""
    
    # Check for consonant onset
    if is_consonant(char):
        # Check for digraph 'gb' first
        if pos + 1 < len(text):
            potential_digraph = char_lower + text[pos + 1].lower()
            if potential_digraph in DIGRAPHS:
                onset = potential_digraph
                pos += 2
            else:
                onset = char_lower
                pos += 1
        else:
            onset = char_lower
            pos += 1
    
    # Now expect a vowel (nucleus)
    if pos >= len(text):
        # Consonant at end without vowel - shouldn't happen in standard Yoruba
        # Return what we have
        if onset:
            return None, start_pos + 1
        return None, pos
    
    char = text[pos]
    
    if not is_vowel(char):
        # No vowel after consonant - might be syllabic nasal handled above
        # or malformed input
        if onset:
            return None, start_pos + 1
        return None, pos + 1
    
    # We have a vowel
    vowel = char
    tone = get_tone_from_char(vowel)
    pos += 1
    
    # Check for nasal vowel (V + n)
    is_nasal_v = False
    if pos < len(text) and _check_nasal_vowel(text, pos - 1, pos):
        is_nasal_v = True
        pos += 1  # Consume the 'n'
    
    raw = text[start_pos:pos]
    
    return Syllable(
        onset=onset,
        nucleus=vowel,
        tone=tone,
        is_nasal_vowel=is_nasal_v,
        is_syllabic_nasal=False,
        raw=raw,
    ), pos


def parse_syllables(text: str) -> Iterator[Syllable]:
    """Parse Yoruba text into syllables."""
    text = normalize_yoruba(text)
    pos = 0
    while pos < len(text):
        syllable, new_pos = parse_syllable(text, pos)
        if syllable is None:
            pos = new_pos if new_pos > pos else pos + 1
            continue
        yield syllable
        pos = new_pos


class YorubaG2P:
    """Convert Yoruba orthography to IPA transcription.
    
    Features:
    - Tie bar (͡) for affricates and labiovelars
    - Syllabicity mark (̩) for syllabic nasals
    - Chao tone letters at syllable end
    
    Example usage:
        >>> g2p = YorubaG2P()
        >>> g2p.transliterate("bàbá")
        'ba˨ba˦'
        >>> g2p.transliterate("gbogbo")
        'ɡ͡boɡ͡bo˧'
        >>> g2p.transliterate("ń lọ")
        'n̩˦ lɔ˧'
    """
    
    def __init__(self, include_tones: bool = True):
        """Initialize the Yoruba G2P converter.
        
        Args:
            include_tones: Whether to include Chao tone letters in output.
        """
        self.include_tones = include_tones
    
    def _syllable_to_ipa(self, syllable: Syllable) -> str:
        """Convert a parsed syllable to IPA string."""
        parts = []
        
        # Onset
        if syllable.onset:
            parts.append(syllable.onset_ipa)
        
        # Nucleus
        parts.append(syllable.nucleus_ipa)
        
        # Tone
        if self.include_tones:
            parts.append(syllable.tone_chao)
        
        return "".join(parts)
    
    def _syllable_to_tokens(self, syllable: Syllable) -> list[str]:
        """Convert a parsed syllable to list of IPA tokens."""
        tokens = []
        
        # Onset
        if syllable.onset:
            tokens.append(syllable.onset_ipa)
        
        # Nucleus
        tokens.append(syllable.nucleus_ipa)
        
        # Tone
        if self.include_tones:
            tokens.append(syllable.tone_chao)
        
        return tokens
    
    def transliterate(self, text: str) -> str:
        """Convert Yoruba text to IPA transcription.
        
        Args:
            text: Yoruba text to transliterate.
            
        Returns:
            IPA transcription with Chao tone letters.
        """
        result = []
        pos = 0
        text = normalize_yoruba(text)
        
        while pos < len(text):
            # Try to parse a syllable
            syllable, new_pos = parse_syllable(text, pos)
            
            if syllable is None:
                # No syllable found, preserve non-Yoruba character
                if new_pos > pos:
                    result.append(text[pos:new_pos])
                    pos = new_pos
                else:
                    result.append(text[pos])
                    pos += 1
                continue
            
            # Add any skipped non-Yoruba text
            if syllable.raw:
                start = text.find(syllable.raw, pos)
                if start > pos:
                    result.append(text[pos:start])
            
            # Convert syllable to IPA
            ipa = self._syllable_to_ipa(syllable)
            result.append(ipa)
            pos = new_pos
        
        return "".join(result)
    
    def transliterate_tokenized(self, text: str) -> list[str]:
        """Convert Yoruba text to tokenized IPA segments.
        
        Args:
            text: Yoruba text to transliterate.
            
        Returns:
            List of IPA tokens (segments and tones).
        """
        tokens = []
        
        for syllable in parse_syllables(text):
            tokens.extend(self._syllable_to_tokens(syllable))
        
        return tokens
