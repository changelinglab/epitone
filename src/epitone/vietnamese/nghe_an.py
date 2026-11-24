"""Nghệ An (Central) Vietnamese G2P converter.

This module implements the Central Vietnamese dialect spoken in Nghệ An province.

Key phonological features:
- d, gi → /z/
- r → /ʐ/ (retroflex)
- s → /ʂ/ (retroflex)
- tr → /ʈ/ or /ʈɽ/ (retroflex)
- v → /v/
- Hỏi and ngã tones merge to ˧˩˨ (312)
"""

from epitone.vietnamese.shared import (
    CODAS,
    Dialect,
    ONSETS,
    SEMIVOWEL_CODAS,
    TONE_NGANG,
    VietnameseG2PBase,
)


# Nghệ An-specific onset mappings
NGHE_AN_ONSETS = {
    **ONSETS,
    "d": "z",
    "gi": "z",
    "r": "ʐ",       # Retroflex approximant/fricative
    "s": "ʂ",       # Retroflex fricative
    "tr": "ʈ",      # Retroflex stop
    "v": "v",
}

# Nghệ An-specific coda mappings
NGHE_AN_CODAS = {
    **CODAS,
    "ch": "c",      # Palatal stop
    "nh": "ɲ",      # Palatal nasal
}

# Nghệ An tone Chao letters
# Hỏi and ngã merge in Central dialects
NGHE_AN_TONES = {
    "ngang": "˧",       # Level (33)
    "huyen": "˧˩",      # Falling (31) - slightly higher start than Hanoi
    "sac": "˧˥",        # Rising (35)
    "hoi": "˧˩˨",       # Dipping (312) - merged with ngã
    "nga": "˧˩˨",       # Merged with hỏi (312)
    "nang": "˧ˀ˩",      # Heavy/glottalized (3ʔ1)
}

# Checked syllables
NGHE_AN_CHECKED_TONES = {
    "ngang": "˧˥",
    "huyen": "˨˩",
    "sac": "˧˥",        # High rising
    "hoi": "˧˥",        # Merges with sắc
    "nga": "˧˥",        # Merges with sắc
    "nang": "˨˩ˀ",      # Low glottalized
}


class NgheAnG2P(VietnameseG2PBase):
    """Convert Nghệ An (Central) Vietnamese orthography to IPA.
    
    Example usage:
        >>> g2p = NgheAnG2P()
        >>> g2p.transliterate("xin chào")
        'ʔʂin˧ tɕaːw˧˩'
        >>> g2p.transliterate("trời")
        'ʈəːj˨˩'
    """
    
    @property
    def dialect(self) -> Dialect:
        return Dialect.NGHE_AN
    
    def get_onset_ipa(self, onset: str) -> str:
        """Get IPA for onset consonant in Nghệ An dialect."""
        onset_lower = onset.lower()
        return NGHE_AN_ONSETS.get(onset_lower, onset_lower)
    
    def get_coda_ipa(self, coda: str, nucleus: str) -> str:
        """Get IPA for coda consonant in Nghệ An dialect."""
        coda_lower = coda.lower()
        
        # Check semivowel codas first
        if coda_lower in SEMIVOWEL_CODAS:
            return SEMIVOWEL_CODAS[coda_lower]
        
        return NGHE_AN_CODAS.get(coda_lower, coda_lower)
    
    def get_tone_chao(self, tone: str, is_checked: bool) -> str:
        """Get Chao tone letter for Nghệ An dialect."""
        if is_checked:
            return NGHE_AN_CHECKED_TONES.get(tone, NGHE_AN_CHECKED_TONES["sac"])
        return NGHE_AN_TONES.get(tone, NGHE_AN_TONES["ngang"])
