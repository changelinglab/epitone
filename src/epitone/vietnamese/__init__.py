"""Vietnamese G2P modules for three dialect varieties.

Supported dialects:
- Hanoi (Northern): HanoiG2P
- Nghệ An (Central): NgheAnG2P  
- Sài Gòn (Southern): SaiGonG2P

Example usage:
    >>> from epitone.vietnamese import HanoiG2P, NgheAnG2P, SaiGonG2P
    >>> 
    >>> hanoi = HanoiG2P()
    >>> hanoi.transliterate("xin chào")
    'ʔsin˧ tɕaːw˨˩'
    >>>
    >>> saigon = SaiGonG2P()
    >>> saigon.transliterate("đi đâu")
    'ɗi˧ jəw˧'
"""

from epitone.vietnamese.hanoi import HanoiG2P
from epitone.vietnamese.nghe_an import NgheAnG2P
from epitone.vietnamese.sai_gon import SaiGonG2P
from epitone.vietnamese.shared import Dialect

__all__ = [
    "HanoiG2P",
    "NgheAnG2P",
    "SaiGonG2P",
    "Dialect",
]
