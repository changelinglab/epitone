"""Epitone: G2P libraries for extracting IPA transcriptions with Chao tone marks."""

from epitone.thai import ThaiG2P
from epitone.vietnamese import HanoiG2P, NgheAnG2P, SaiGonG2P
from epitone.yoruba import YorubaG2P

__version__ = "0.1.0"
__all__ = [
    "ThaiG2P",
    "HanoiG2P",
    "NgheAnG2P",
    "SaiGonG2P",
    "YorubaG2P",
]
