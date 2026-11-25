"""Thai Grapheme-to-Phoneme converter."""

from epitone.thai.data import TONE_TO_CHAO
from epitone.thai.syllable import Syllable, parse_syllables
from epitone.thai.tone import determine_tone, get_tone_chao
from epitone.unicode_utils import to_nfd


class ThaiG2P:
    """Convert Thai orthography to IPA transcription with Chao tone letters.
    
    Example usage:
        >>> g2p = ThaiG2P()
        >>> g2p.transliterate("ไทย")
        'tʰaj˧'
        >>> g2p.transliterate_tokenized("ไทย")
        ['tʰ', 'a', 'j', '˧']
    """

    def __init__(self, include_tones: bool = True):
        """Initialize the Thai G2P converter.
        
        Args:
            include_tones: Whether to include Chao tone letters in output.
        """
        self.include_tones = include_tones

    def _syllable_to_ipa(self, syllable: Syllable) -> str:
        """Convert a parsed syllable to IPA string."""
        tone = determine_tone(syllable)
        tone_chao = get_tone_chao(tone) if self.include_tones else ""

        # Build IPA: onset + vowel + coda + tone
        parts = []
        if syllable.onset_ipa:
            parts.append(syllable.onset_ipa)
        if syllable.vowel_ipa:
            parts.append(syllable.vowel_ipa)
        if syllable.coda_ipa:
            parts.append(syllable.coda_ipa)
        
        ipa = "".join(parts)
        return ipa + tone_chao

    def _syllable_to_tokens(self, syllable: Syllable) -> list[str]:
        """Convert a parsed syllable to list of IPA tokens."""
        tokens = []

        if syllable.onset_ipa:
            tokens.append(syllable.onset_ipa)
        if syllable.vowel_ipa:
            tokens.append(syllable.vowel_ipa)
        if syllable.coda_ipa:
            tokens.append(syllable.coda_ipa)

        if self.include_tones:
            tone = determine_tone(syllable)
            tone_chao = get_tone_chao(tone)
            tokens.append(tone_chao)

        return tokens

    def transliterate(self, text: str) -> str:
        """Convert Thai text to IPA transcription.
        
        Args:
            text: Thai text to transliterate.
            
        Returns:
            IPA transcription with Chao tone letters in NFD form.
        """
        result = []
        pos = 0
        syllables = list(parse_syllables(text))

        for syllable in syllables:
            # Find where this syllable's raw text appears in the original
            start = text.find(syllable.raw, pos)
            if start == -1:
                # Shouldn't happen, but handle gracefully
                ipa = self._syllable_to_ipa(syllable)
                result.append(ipa)
                continue
                
            # Add any non-Thai characters between current pos and syllable start
            if start > pos:
                non_thai = text[pos:start]
                result.append(non_thai)
            
            ipa = self._syllable_to_ipa(syllable)
            result.append(ipa)
            pos = start + len(syllable.raw)

        # Add any trailing non-Thai characters
        if pos < len(text):
            result.append(text[pos:])

        return to_nfd("".join(result))

    def transliterate_tokenized(self, text: str) -> list[str]:
        """Convert Thai text to tokenized IPA segments.
        
        Args:
            text: Thai text to transliterate.
            
        Returns:
            List of IPA tokens (segments and tones) in NFD form.
        """
        tokens = []

        for syllable in parse_syllables(text):
            syllable_tokens = self._syllable_to_tokens(syllable)
            tokens.extend(syllable_tokens)

        return [to_nfd(token) for token in tokens]
