"""Burmese Grapheme-to-Phoneme converter.

Converts Burmese script to IPA transcription with:
- Chao tone letters indicating the 4-tone system
- Phonation diacritics for breathy and creaky voice
- Proper handling of medial consonants
- Syllable-by-syllable processing

Note: Burmese orthography has many irregularities and spelling conventions
that this rule-based system cannot fully capture. This implementation
handles standard/regular spellings according to phonological rules.
"""

from epitone.burmese.data import normalize_burmese
from epitone.burmese.syllable import Syllable, parse_syllable, parse_syllables
from epitone.burmese.tone import format_syllable_ipa, format_syllable_tokens
from epitone.unicode_utils import to_nfd


class BurmeseG2P:
    """Convert Burmese orthography to IPA transcription.
    
    Features:
    - 4 tones represented with Chao tone letters
    - Phonation types (modal, breathy, creaky)
    - Medial consonant clusters
    - Proper handling of checked (stopped) syllables
    
    Example usage:
        >>> g2p = BurmeseG2P()
        >>> g2p.transliterate("မြန်မာ")
        'mjàn˨˩ma˨˩'
        >>> g2p.transliterate_tokenized("ကောင်း")
        ['k', 'aʊ̃', '˥']
    
    Note:
        Burmese G2P is inherently one-to-many due to:
        - Historical spellings
        - Pali/Sanskrit loanwords with silent letters
        - Colloquial vs. literary pronunciations
        
        This converter aims for modern spoken (colloquial) Burmese.
    """

    def __init__(self, include_tones: bool = True, include_phonation: bool = True):
        """Initialize the Burmese G2P converter.
        
        Args:
            include_tones: Whether to include Chao tone letters in output.
            include_phonation: Whether to include phonation diacritics (̤ ̰).
        """
        self.include_tones = include_tones
        self.include_phonation = include_phonation

    def _syllable_to_ipa(self, syllable: Syllable) -> str:
        """Convert a parsed syllable to IPA string."""
        return format_syllable_ipa(
            syllable,
            include_tone=self.include_tones,
            include_phonation=self.include_phonation,
        )

    def _syllable_to_tokens(self, syllable: Syllable) -> list[str]:
        """Convert a parsed syllable to list of IPA tokens."""
        return format_syllable_tokens(
            syllable,
            include_tone=self.include_tones,
            include_phonation=self.include_phonation,
        )

    def transliterate(self, text: str) -> str:
        """Convert Burmese text to IPA transcription.
        
        Args:
            text: Burmese text to transliterate.
            
        Returns:
            IPA transcription with Chao tone letters in NFD form.
        """
        result = []
        pos = 0
        text = normalize_burmese(text)

        while pos < len(text):
            # Try to parse a syllable
            syllable, new_pos = parse_syllable(text, pos)

            if syllable is None:
                # No syllable found, preserve non-Burmese character
                if new_pos > pos:
                    result.append(text[pos:new_pos])
                    pos = new_pos
                else:
                    result.append(text[pos])
                    pos += 1
                continue

            # Find where syllable starts (may have skipped non-Myanmar chars)
            if syllable.raw:
                start = text.find(syllable.raw, pos)
                if start > pos:
                    result.append(text[pos:start])

            # Convert syllable to IPA
            ipa = self._syllable_to_ipa(syllable)
            result.append(ipa)
            pos = new_pos

        return to_nfd("".join(result))

    def transliterate_tokenized(self, text: str) -> list[str]:
        """Convert Burmese text to tokenized IPA segments.
        
        Args:
            text: Burmese text to transliterate.
            
        Returns:
            List of IPA tokens (segments and tones) in NFD form.
        """
        tokens = []
        text = normalize_burmese(text)

        for syllable in parse_syllables(text):
            syllable_tokens = self._syllable_to_tokens(syllable)
            tokens.extend(syllable_tokens)

        return [to_nfd(token) for token in tokens]
