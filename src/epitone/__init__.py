"""Epitone: G2P libraries for extracting IPA transcriptions with Chao tone marks.

All G2P modules output strings in Unicode NFD (Normalized Form Decomposed).
"""

from epitone.hmong import DananshanG2P, HmongDawG2P, MongLengG2P
from epitone.thai import ThaiG2P
from epitone.unicode_utils import nfd_equal, to_nfc, to_nfd
from epitone.vietnamese import HanoiG2P, NgheAnG2P, SaiGonG2P
from epitone.yoruba import YorubaG2P

__version__ = "0.1.0"
__all__ = [
    "ThaiG2P",
    "HanoiG2P",
    "NgheAnG2P",
    "SaiGonG2P",
    "YorubaG2P",
    "HmongDawG2P",
    "MongLengG2P",
    "DananshanG2P",
    "to_nfd",
    "to_nfc",
    "nfd_equal",
]
