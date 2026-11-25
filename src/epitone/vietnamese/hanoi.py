"""Hanoi (Northern) Vietnamese G2P converter.

This module implements the Northern Vietnamese dialect spoken in Hanoi.

Key phonological features:
- d, gi, r → /z/
- s → /s/
- tr → /tɕ/ (same as ch)
- v → /v/
- Distinct hỏi (˧˩˧) and ngã (˧ˀ˥) tones
"""

from epitone.vietnamese.shared import (
    CODAS,
    Dialect,
    ONSETS,
    SEMIVOWEL_CODAS,
    TONE_NGANG,
    VietnameseG2PBase,
)


# Hanoi-specific onset mappings
HANOI_ONSETS = {
    **ONSETS,
    "d": "z",
    "gi": "z",
    "r": "z",
    "s": "s",
    "tr": "tɕ",
    "v": "v",
}

# Hanoi-specific coda mappings
HANOI_CODAS = {
    **CODAS,
    "ch": "c",   # Palatal stop
    "nh": "ɲ",   # Palatal nasal
}

# Hanoi tone Chao letters
# Standard (open/sonorant-final) syllables
HANOI_TONES = {
    "ngang": "˧",       # Level (33)
    "huyen": "˨˩",      # Falling (21)
    "sac": "˧˥",        # Rising (35)
    "hoi": "˧˩˧",       # Dipping-rising (313)
    "nga": "˧ˀ˥",       # Creaky rising (3ʔ5)
    "nang": "˧ˀ˩",      # Heavy/glottalized falling (3ʔ1)
}

# Checked syllables (stop-final: -p, -t, -c, -ch) only allow sắc and nặng
HANOI_CHECKED_TONES = {
    "ngang": "˧˥",      # Defaults to sắc pattern
    "huyen": "˨˩",      # Rare, defaults to nặng-like
    "sac": "˧˥",        # High rising (35)
    "hoi": "˧˥",        # Merges with sắc
    "nga": "˧˥",        # Merges with sắc
    "nang": "˨˩ˀ",      # Low glottalized (21ʔ)
}


class HanoiG2P(VietnameseG2PBase):
    """Convert Hanoi (Northern) Vietnamese orthography to IPA.
    
    Example usage:
        >>> g2p = HanoiG2P()
        >>> g2p.transliterate("xin chào")
        'ʔsin˧ tɕaːw˨˩'
        >>> g2p.transliterate_tokenized("cảm ơn")
        ['ʔ', 'k', 'am', '˧˩˧', 'ʔ', 'əː', 'n', '˧']
    """
    
    @property
    def dialect(self) -> Dialect:
        return Dialect.HANOI
    
    def get_onset_ipa(self, onset: str) -> str:
        """Get IPA for onset consonant in Hanoi dialect."""
        onset_lower = onset.lower()
        return HANOI_ONSETS.get(onset_lower, onset_lower)
    
    def get_coda_ipa(self, coda: str, nucleus: str) -> str:
        """Get IPA for coda consonant in Hanoi dialect."""
        coda_lower = coda.lower()
        
        # Check semivowel codas first
        if coda_lower in SEMIVOWEL_CODAS:
            return SEMIVOWEL_CODAS[coda_lower]
        
        return HANOI_CODAS.get(coda_lower, coda_lower)
    
    def get_tone_chao(self, tone: str, is_checked: bool) -> str:
        """Get Chao tone letter for Hanoi dialect."""
        if is_checked:
            return HANOI_CHECKED_TONES.get(tone, HANOI_CHECKED_TONES["sac"])
        return HANOI_TONES.get(tone, HANOI_TONES["ngang"])
