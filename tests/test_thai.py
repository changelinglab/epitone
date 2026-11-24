"""Tests for Thai G2P converter."""

import pytest

from epitone.thai import ThaiG2P
from epitone.thai.data import ConsonantClass, CONSONANTS, Tone
from epitone.thai.syllable import parse_syllable, parse_syllables, Syllable
from epitone.thai.tone import determine_tone


class TestConsonantData:
    """Test consonant data mappings."""

    def test_consonant_count(self):
        assert len(CONSONANTS) == 44

    def test_consonant_classes(self):
        # High class (11)
        high = [c for c, info in CONSONANTS.items() if info.consonant_class == ConsonantClass.HIGH]
        assert len(high) == 11
        assert "ข" in high
        assert "ส" in high
        assert "ห" in high

        # Mid class (9)
        mid = [c for c, info in CONSONANTS.items() if info.consonant_class == ConsonantClass.MID]
        assert len(mid) == 9
        assert "ก" in mid
        assert "จ" in mid
        assert "อ" in mid

        # Low class (24)
        low = [c for c, info in CONSONANTS.items() if info.consonant_class == ConsonantClass.LOW]
        assert len(low) == 24
        assert "ค" in low
        assert "ง" in low
        assert "ม" in low

    def test_initial_ipa(self):
        assert CONSONANTS["ก"].ipa_initial == "k"
        assert CONSONANTS["ข"].ipa_initial == "kʰ"
        assert CONSONANTS["ง"].ipa_initial == "ŋ"
        assert CONSONANTS["จ"].ipa_initial == "tɕ"
        assert CONSONANTS["ส"].ipa_initial == "s"

    def test_final_ipa(self):
        assert CONSONANTS["ก"].ipa_final == "k"
        assert CONSONANTS["ด"].ipa_final == "t"
        assert CONSONANTS["บ"].ipa_final == "p"
        assert CONSONANTS["น"].ipa_final == "n"
        assert CONSONANTS["ม"].ipa_final == "m"
        assert CONSONANTS["ง"].ipa_final == "ŋ"


class TestSyllableParsing:
    """Test syllable parsing."""

    def test_simple_cv(self):
        # กา (kaa) - mid class, long vowel, live
        syllable, _ = parse_syllable("กา")
        assert syllable.onset == "ก"
        assert syllable.onset_ipa == "k"
        assert syllable.consonant_class == ConsonantClass.MID
        assert syllable.vowel_ipa == "aː"
        assert syllable.vowel_is_long is True
        assert syllable.coda == ""
        assert syllable.is_live is True

    def test_cvc_syllable(self):
        # กัน (kan) - mid class, short vowel, sonorant coda, live
        syllable, _ = parse_syllable("กัน")
        assert syllable.onset == "ก"
        assert syllable.onset_ipa == "k"
        assert syllable.vowel_ipa == "a"
        assert syllable.vowel_is_long is False
        assert syllable.coda == "น"
        assert syllable.coda_ipa == "n"
        assert syllable.is_live is True

    def test_leading_vowel(self):
        # เก (kee) - leading vowel เ
        syllable, _ = parse_syllable("เก")
        assert syllable.onset == "ก"
        assert syllable.vowel_ipa == "eː"
        assert syllable.vowel_is_long is True

    def test_tone_mark_parsing(self):
        # ก่า (kàa) - with mai ek
        syllable, _ = parse_syllable("ก่า")
        assert syllable.tone_mark == "\u0e48"  # mai ek

    def test_ho_nam(self):
        # หน (nǒ-) - ห leading น makes it high class
        syllable, _ = parse_syllable("หนา")
        assert syllable.onset == "หน"
        assert syllable.onset_ipa == "n"
        assert syllable.consonant_class == ConsonantClass.HIGH

    def test_dead_syllable_stop_coda(self):
        # กัก (kak) - stop coda makes it dead
        syllable, _ = parse_syllable("กัก")
        assert syllable.coda == "ก"
        assert syllable.coda_ipa == "k"
        assert syllable.is_dead is True

    def test_dead_syllable_short_vowel(self):
        # กะ (ka) - short vowel, no coda, dead
        syllable, _ = parse_syllable("กะ")
        assert syllable.vowel_is_long is False
        assert syllable.coda == ""
        assert syllable.is_dead is True


class TestToneDetermination:
    """Test tone determination logic."""

    def test_mid_class_live_no_mark(self):
        # กา - mid class, live, no mark -> mid tone
        syllable, _ = parse_syllable("กา")
        tone = determine_tone(syllable)
        assert tone == Tone.MID

    def test_mid_class_dead_no_mark(self):
        # กะ - mid class, dead, no mark -> low tone
        syllable, _ = parse_syllable("กะ")
        tone = determine_tone(syllable)
        assert tone == Tone.LOW

    def test_mid_class_with_mai_ek(self):
        # ก่า - mid class, mai ek -> low tone
        syllable, _ = parse_syllable("ก่า")
        tone = determine_tone(syllable)
        assert tone == Tone.LOW

    def test_mid_class_with_mai_tho(self):
        # ก้า - mid class, mai tho -> falling tone
        syllable, _ = parse_syllable("ก้า")
        tone = determine_tone(syllable)
        assert tone == Tone.FALLING

    def test_high_class_live_no_mark(self):
        # ขา - high class, live, no mark -> rising tone
        syllable, _ = parse_syllable("ขา")
        tone = determine_tone(syllable)
        assert tone == Tone.RISING

    def test_high_class_dead_no_mark(self):
        # ขะ - high class, dead, no mark -> low tone
        syllable, _ = parse_syllable("ขะ")
        tone = determine_tone(syllable)
        assert tone == Tone.LOW

    def test_low_class_live_no_mark(self):
        # คา - low class, live, no mark -> mid tone
        syllable, _ = parse_syllable("คา")
        tone = determine_tone(syllable)
        assert tone == Tone.MID

    def test_low_class_dead_short_no_mark(self):
        # คะ - low class, dead (short), no mark -> high tone
        syllable, _ = parse_syllable("คะ")
        tone = determine_tone(syllable)
        assert tone == Tone.HIGH

    def test_low_class_dead_long_no_mark(self):
        # คาก - low class, dead (long vowel + stop), no mark -> falling tone
        syllable, _ = parse_syllable("คาก")
        tone = determine_tone(syllable)
        assert tone == Tone.FALLING


class TestThaiG2P:
    """Test the main G2P converter."""

    @pytest.fixture
    def g2p(self):
        return ThaiG2P()

    def test_simple_word(self, g2p):
        # กา (kaa) - mid tone
        result = g2p.transliterate("กา")
        assert "k" in result
        assert "aː" in result
        assert "˧" in result  # mid tone

    def test_transliterate_tokenized(self, g2p):
        tokens = g2p.transliterate_tokenized("กา")
        assert "k" in tokens
        assert "aː" in tokens
        assert "˧" in tokens

    def test_no_tones_option(self):
        g2p = ThaiG2P(include_tones=False)
        result = g2p.transliterate("กา")
        assert "˧" not in result
        assert "˩" not in result
        assert "˥" not in result
        assert "˦" not in result

    def test_multiple_syllables(self, g2p):
        # Test that multiple syllables are processed
        result = g2p.transliterate("กากา")
        # Should have tone markers for each syllable
        assert result.count("˧") >= 1

    def test_preserves_non_thai(self, g2p):
        result = g2p.transliterate("hello กา world")
        assert "hello" in result
        assert "world" in result

    def test_thai_word(self, g2p):
        # ไทย (Thai) - should produce tʰaj with appropriate tone
        result = g2p.transliterate("ไทย")
        assert "tʰ" in result or "t" in result

    def test_special_vowel_am(self, g2p):
        # น้ำ (nam) - water
        result = g2p.transliterate("น้ำ")
        assert "n" in result
        assert "a" in result
        assert "m" in result


class TestToneChaoLetters:
    """Test that correct Chao tone letters are used."""

    @pytest.fixture
    def g2p(self):
        return ThaiG2P()

    def test_mid_tone_letter(self, g2p):
        # กา - mid tone ˧
        result = g2p.transliterate("กา")
        assert "˧" in result

    def test_low_tone_letter(self, g2p):
        # ก่า - low tone ˩
        result = g2p.transliterate("ก่า")
        assert "˩" in result

    def test_falling_tone_letter(self, g2p):
        # ก้า - falling tone ˥˩
        result = g2p.transliterate("ก้า")
        assert "˥˩" in result

    def test_high_tone_letter(self, g2p):
        # ก๊า - high tone ˦˥
        result = g2p.transliterate("ก๊า")
        assert "˦˥" in result

    def test_rising_tone_letter(self, g2p):
        # ก๋า or ขา - rising tone ˩˥
        result = g2p.transliterate("ก๋า")
        assert "˩˥" in result
