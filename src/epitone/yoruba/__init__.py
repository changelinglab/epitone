"""Yoruba G2P module for orthography to IPA conversion.

Yoruba features:
- 3-tone system (high ˦, mid ˧, low ˨) with Chao tone letters
- Labial-velar consonants: p → /k͡p/, gb → /ɡ͡b/
- Affricate: j → /d͡ʒ/
- Syllabic nasals: ḿ/ń → /m̩//n̩/ with tone
- Nasal vowels: Vn → Ṽ in certain contexts

Example usage:
    >>> from epitone.yoruba import YorubaG2P
    >>> g2p = YorubaG2P()
    >>> g2p.transliterate("bàbá")
    'ba˨ba˦'
"""

from epitone.yoruba.g2p import YorubaG2P

__all__ = ["YorubaG2P"]
