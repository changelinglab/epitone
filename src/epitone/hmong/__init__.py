"""Hmong G2P modules for multiple orthographies and dialects.

Supported orthographies and dialects:
- RPA (Romanized Popular Alphabet):
  - HmongDawG2P: White Hmong (Hmong Daw)
  - MongLengG2P: Green/Blue Hmong (Mong Leng/Mong Njua)
- Dananshan:
  - DananshanG2P: Dananshan Miao Pinyin-based orthography

RPA orthography notes:
- Tone is indicated by final consonant letter (b, j, v, s, g, m, d) or absence
- Doubled vowels ee, oo, aa represent nasalized vowels
- The -g tone marks breathy phonation on the vowel
- Uses standard IPA for prenasalized consonants (mp, nt, ŋk, not ᵐp, ⁿt, ᵑk)
- Uses /l/ in clusters like /pl/, /tl/ (not /ˡ/)

Example usage:
    >>> from epitone.hmong import HmongDawG2P, MongLengG2P, DananshanG2P
    >>> 
    >>> # White Hmong
    >>> hmong_daw = HmongDawG2P()
    >>> hmong_daw.transliterate("kuv")
    'ku˨˦v'
    >>>
    >>> # Green Hmong
    >>> mong_leng = MongLengG2P()
    >>> mong_leng.transliterate("kuv")
    'ku˨˦v'
    >>>
    >>> # Dananshan orthography
    >>> dananshan = DananshanG2P()
    >>> dananshan.transliterate("ba1")
    'pa˦˦'
"""

from epitone.hmong.dananshan import DananshanG2P
from epitone.hmong.data import HmongDialect
from epitone.hmong.rpa import HmongDawG2P, HmongRPAG2P, MongLengG2P

__all__ = [
    "HmongDawG2P",
    "MongLengG2P",
    "HmongRPAG2P",
    "DananshanG2P",
    "HmongDialect",
]
