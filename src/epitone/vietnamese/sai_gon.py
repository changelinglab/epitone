"""Sài Gòn (Southern) Vietnamese G2P converter.

This module implements the Southern Vietnamese dialect spoken in Sài Gòn/Ho Chi Minh City.

Key phonological features:
- d, gi → /j/ (palatal approximant, not /z/)
- r → /ɹ/ or /ɾ/ (approximant or tap)
- s → /ʂ/ (retroflex, like Central)
- tr → /tɕ/ (same as ch, like Northern)
- v → /j/ (often merges with d/gi)
- Hỏi and ngã tones merge to ˨˩˦ (214)
- Final -nh → -ng after front vowels
- Final -ch → -t after front vowels
"""

from epitone.vietnamese.shared import (
    CODAS,
    Dialect,
    ONSETS,
    SEMIVOWEL_CODAS,
    TONE_NGANG,
    VietnameseG2PBase,
)


# Sài Gòn-specific onset mappings
SAI_GON_ONSETS = {
    **ONSETS,
    "d": "j",       # Palatal approximant
    "gi": "j",      # Palatal approximant
    "r": "ɹ",       # Approximant (can also be /ɾ/)
    "s": "ʂ",       # Retroflex fricative
    "tr": "tɕ",     # Same as ch
    "v": "j",       # Often merges with /j/
}

# Sài Gòn-specific coda mappings
# Southern dialect has coda mergers after front vowels
SAI_GON_CODAS = {
    **CODAS,
    "ch": "t",      # Merges to -t after front vowels
    "nh": "ŋ",      # Merges to -ng after front vowels
}

# Front vowels that trigger coda mergers
FRONT_VOWELS = frozenset(["i", "ê", "e", "y"])

# Sài Gòn tone Chao letters
# Hỏi and ngã merge in Southern dialect
SAI_GON_TONES = {
    "ngang": "˧",       # Level (33)
    "huyen": "˨˩",      # Falling (21)
    "sac": "˧˥",        # Rising (35)
    "hoi": "˨˩˦",       # Rising from low (214) - merged with ngã
    "nga": "˨˩˦",       # Merged with hỏi (214)
    "nang": "˨˩ˀ",      # Low glottalized (21ʔ)
}

# Checked syllables
SAI_GON_CHECKED_TONES = {
    "ngang": "˧˥",
    "huyen": "˨˩",
    "sac": "˧˥",        # High rising
    "hoi": "˧˥",        # Defaults to sắc-like
    "nga": "˧˥",        # Defaults to sắc-like
    "nang": "˨˩ˀ",      # Low glottalized
}


class SaiGonG2P(VietnameseG2PBase):
    """Convert Sài Gòn (Southern) Vietnamese orthography to IPA.
    
    Example usage:
        >>> g2p = SaiGonG2P()
        >>> g2p.transliterate("xin chào")
        'ʔʂin˧ tɕaːw˨˩'
        >>> g2p.transliterate("đi")
        'ɗi˧'
        >>> g2p.transliterate("da")  # 'd' becomes /j/ in Southern
        'jaː˧'
    """
    
    @property
    def dialect(self) -> Dialect:
        return Dialect.SAI_GON
    
    def get_onset_ipa(self, onset: str) -> str:
        """Get IPA for onset consonant in Sài Gòn dialect."""
        onset_lower = onset.lower()
        return SAI_GON_ONSETS.get(onset_lower, onset_lower)
    
    def get_coda_ipa(self, coda: str, nucleus: str) -> str:
        """Get IPA for coda consonant in Sài Gòn dialect.
        
        Note: -nh and -ch merge to -ng and -t respectively after front vowels.
        """
        coda_lower = coda.lower()
        
        # Check semivowel codas first
        if coda_lower in SEMIVOWEL_CODAS:
            return SEMIVOWEL_CODAS[coda_lower]
        
        # Check for Southern coda mergers after front vowels
        nucleus_lower = nucleus.lower() if nucleus else ""
        has_front_vowel = any(v in nucleus_lower for v in FRONT_VOWELS)
        
        if has_front_vowel:
            if coda_lower == "nh":
                return "ŋ"  # -nh → -ng
            elif coda_lower == "ch":
                return "t"  # -ch → -t
        
        return SAI_GON_CODAS.get(coda_lower, coda_lower)
    
    def get_tone_chao(self, tone: str, is_checked: bool) -> str:
        """Get Chao tone letter for Sài Gòn dialect."""
        if is_checked:
            return SAI_GON_CHECKED_TONES.get(tone, SAI_GON_CHECKED_TONES["sac"])
        return SAI_GON_TONES.get(tone, SAI_GON_TONES["ngang"])
