"""Burmese G2P module for orthography to IPA conversion.

Burmese features:
- 4-tone system: low ˨˩, high ˥˩, creaky ˧, checked ˥
- 3 phonation types: modal, breathy (̤), creaky (̰)
- Complex syllable structure with medials (ျ, ြ, ွ, ှ)
- Consonant codas marked with asat (်)

Example usage:
    >>> from epitone.burmese import BurmeseG2P
    >>> g2p = BurmeseG2P()
    >>> g2p.transliterate("မြန်မာ")
    'mja̰n˧ma˨˩'

Note:
    This converter handles regular/standard spellings. Burmese orthography
    has many irregularities from historical spellings and loanwords that
    require lexical lookup for accurate conversion.
"""

from epitone.burmese.g2p import BurmeseG2P

__all__ = ["BurmeseG2P"]
