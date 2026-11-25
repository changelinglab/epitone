"""Unicode normalization utilities for epitone.

All G2P modules output strings in Unicode NFD (Normalized Form Decomposed).
This ensures consistent handling of combining characters across all languages.
"""

import unicodedata


def to_nfd(text: str) -> str:
    """Convert text to Unicode NFD (Normalized Form Decomposed).
    
    NFD separates base characters from combining characters, e.g.:
    - 'ã' (U+00E3) → 'a' + '̃' (U+0061 + U+0303)
    - 'ɛ̃' stays as 'ɛ' + '̃' (already decomposed)
    
    Args:
        text: Input text string
        
    Returns:
        NFD-normalized text
    """
    return unicodedata.normalize("NFD", text)


def to_nfc(text: str) -> str:
    """Convert text to Unicode NFC (Normalized Form Composed).
    
    NFC combines base characters with combining characters where possible.
    Used for input normalization before processing.
    
    Args:
        text: Input text string
        
    Returns:
        NFC-normalized text
    """
    return unicodedata.normalize("NFC", text)


def nfd_equal(a: str, b: str) -> bool:
    """Check if two strings are equal when both normalized to NFD.
    
    Useful for comparing strings that may have different normalization forms.
    
    Args:
        a: First string
        b: Second string
        
    Returns:
        True if strings are equivalent in NFD form
    """
    return to_nfd(a) == to_nfd(b)
