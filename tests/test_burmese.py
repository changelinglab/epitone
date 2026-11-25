"""Tests for Burmese G2P converter."""

import unicodedata

import pytest

from epitone.burmese import BurmeseG2P
from epitone.burmese.data import (
    ANUSVARA,
    ASAT,
    BREATHY_MARK,
    CONSONANTS,
    CREAKY_MARK,
    FINAL_CONSONANTS,
    MEDIALS,
    Phonation,
    Tone,
    TONE_TO_CHAO,
    VISARGA,
    get_consonant_ipa,
    get_medial_ipa,
    is_consonant,
    is_medial,
    is_myanmar_char,
    normalize_burmese,
)
from epitone.burmese.syllable import Syllable, parse_syllable, parse_syllables
from epitone.burmese.tone import (
    apply_phonation_to_vowel,
    format_syllable_ipa,
    get_phonation_mark,
    get_tone_chao,
)


def nfd(text: str) -> str:
    """Normalize text to NFD for comparison with G2P output."""
    return unicodedata.normalize("NFD", text)


class TestBurmeseData:
    """Test Burmese data utilities."""

    def test_is_myanmar_char(self):
        assert is_myanmar_char("က")
        assert is_myanmar_char("ခ")
        assert is_myanmar_char("ါ")
        assert not is_myanmar_char("a")
        assert not is_myanmar_char("1")

    def test_is_consonant(self):
        assert is_consonant("က")
        assert is_consonant("မ")
        assert is_consonant("သ")
        assert not is_consonant("ါ")
        assert not is_consonant("ိ")

    def test_is_medial(self):
        assert is_medial("ျ")
        assert is_medial("ြ")
        assert is_medial("ွ")
        assert is_medial("ှ")
        assert not is_medial("က")
        assert not is_medial("ါ")

    def test_normalize_burmese(self):
        # Should handle NFC normalization
        text = "မြန်မာ"
        normalized = normalize_burmese(text)
        assert normalized == unicodedata.normalize("NFC", text)


class TestConsonantMappings:
    """Test consonant IPA mappings."""

    def test_basic_consonants(self):
        assert get_consonant_ipa("က") == "k"
        assert get_consonant_ipa("ခ") == "kʰ"
        assert get_consonant_ipa("ဂ") == "ɡ"
        assert get_consonant_ipa("င") == "ŋ"

    def test_palatal_consonants(self):
        assert get_consonant_ipa("စ") == "s"
        assert get_consonant_ipa("ဆ") == "sʰ"
        assert get_consonant_ipa("ဇ") == "z"
        assert get_consonant_ipa("ည") == "ɲ"

    def test_dental_consonants(self):
        assert get_consonant_ipa("တ") == "t"
        assert get_consonant_ipa("ထ") == "tʰ"
        assert get_consonant_ipa("ဒ") == "d"
        assert get_consonant_ipa("န") == "n"

    def test_labial_consonants(self):
        assert get_consonant_ipa("ပ") == "p"
        assert get_consonant_ipa("ဖ") == "pʰ"
        assert get_consonant_ipa("ဗ") == "b"
        assert get_consonant_ipa("မ") == "m"

    def test_other_consonants(self):
        assert get_consonant_ipa("ယ") == "j"
        assert get_consonant_ipa("ရ") == "j"  # r → j in modern Burmese
        assert get_consonant_ipa("လ") == "l"
        assert get_consonant_ipa("ဝ") == "w"
        assert get_consonant_ipa("သ") == "θ"  # Dental fricative
        assert get_consonant_ipa("ဟ") == "h"
        assert get_consonant_ipa("အ") == "ʔ"

    def test_final_consonants(self):
        # Stops become glottal stop in final position
        assert get_consonant_ipa("က", as_final=True) == "ʔ"
        assert get_consonant_ipa("တ", as_final=True) == "ʔ"
        assert get_consonant_ipa("ပ", as_final=True) == "ʔ"
        # Nasals remain
        assert get_consonant_ipa("င", as_final=True) == "ŋ"
        assert get_consonant_ipa("န", as_final=True) == "n"
        assert get_consonant_ipa("မ", as_final=True) == "m"


class TestMedialMappings:
    """Test medial consonant IPA mappings."""

    def test_simple_medials(self):
        assert get_medial_ipa("ျ") == "j"
        assert get_medial_ipa("ြ") == "j"
        assert get_medial_ipa("ွ") == "w"
        assert get_medial_ipa("ှ") == "ʰ"

    def test_combined_medials(self):
        assert get_medial_ipa("ျွ") == "jw"
        assert get_medial_ipa("ျှ") == "jʰ"


class TestTones:
    """Test tone mappings."""

    def test_chao_letters(self):
        assert TONE_TO_CHAO[Tone.LOW] == "˨˩"
        assert TONE_TO_CHAO[Tone.HIGH] == "˥˩"
        assert TONE_TO_CHAO[Tone.CREAKY] == "˧"
        assert TONE_TO_CHAO[Tone.CHECKED] == "˥"

    def test_get_tone_chao(self):
        assert get_tone_chao(Tone.LOW) == "˨˩"
        assert get_tone_chao(Tone.HIGH) == "˥˩"
        assert get_tone_chao(Tone.CREAKY) == "˧"
        assert get_tone_chao(Tone.CHECKED) == "˥"


class TestPhonation:
    """Test phonation marking."""

    def test_phonation_marks(self):
        assert get_phonation_mark(Phonation.MODAL) == ""
        assert get_phonation_mark(Phonation.BREATHY) == BREATHY_MARK
        assert get_phonation_mark(Phonation.CREAKY) == CREAKY_MARK

    def test_apply_phonation_modal(self):
        assert apply_phonation_to_vowel("a", Phonation.MODAL) == "a"
        assert apply_phonation_to_vowel("ou", Phonation.MODAL) == "ou"

    def test_apply_phonation_breathy(self):
        result = apply_phonation_to_vowel("a", Phonation.BREATHY)
        assert BREATHY_MARK in result
        assert result.startswith("a")

    def test_apply_phonation_creaky(self):
        result = apply_phonation_to_vowel("a", Phonation.CREAKY)
        assert CREAKY_MARK in result
        assert result.startswith("a")


class TestSyllableParsing:
    """Test syllable parsing."""

    def test_simple_cv(self):
        """Test simple consonant + vowel syllable."""
        syllable, pos = parse_syllable("က")
        assert syllable is not None
        assert syllable.onset == "က"
        assert syllable.onset_ipa == "k"

    def test_cv_with_aa(self):
        """Test consonant + ါ vowel."""
        syllable, pos = parse_syllable("ကါ")
        assert syllable is not None
        assert syllable.onset == "က"
        assert "ါ" in syllable.vowel_signs

    def test_with_medial(self):
        """Test consonant + medial."""
        syllable, pos = parse_syllable("ကျ")
        assert syllable is not None
        assert syllable.onset == "က"
        assert "ျ" in syllable.medials
        assert "j" in syllable.medial_ipa

    def test_with_coda(self):
        """Test consonant + vowel + coda."""
        # Using proper Burmese with asat
        text = "ကန်"  # kan with asat
        syllable, pos = parse_syllable(text)
        assert syllable is not None
        assert syllable.coda_ipa == "n"

    def test_checked_syllable(self):
        """Test syllable with stop coda (checked tone)."""
        text = "ကပ်"  # kap with asat - should be checked
        syllable, pos = parse_syllable(text)
        assert syllable is not None
        assert syllable.tone == Tone.CHECKED

    def test_visarga_high_tone(self):
        """Test syllable with visarga (high tone)."""
        text = "ကား"  # ka with visarga
        syllable, pos = parse_syllable(text)
        assert syllable is not None
        assert syllable.tone == Tone.HIGH

    def test_leading_vowel(self):
        """Test syllable with leading vowel ေ."""
        text = "ကေ"  # ke
        syllable, pos = parse_syllable(text)
        assert syllable is not None
        assert "e" in syllable.vowel_ipa

    def test_multiple_syllables(self):
        """Test parsing multiple syllables."""
        text = "မြန်မာ"  # Myanmar
        syllables = list(parse_syllables(text))
        assert len(syllables) >= 1


class TestBurmeseG2P:
    """Test Burmese G2P converter."""

    @pytest.fixture
    def g2p(self):
        return BurmeseG2P()

    def test_simple_ka(self, g2p):
        """Test simple syllable."""
        result = g2p.transliterate("က")
        assert "k" in result
        assert "a" in result

    def test_aspirated_consonant(self, g2p):
        """Test aspirated consonant."""
        result = g2p.transliterate("ခ")
        assert "kʰ" in result or ("k" in result and "ʰ" in result)

    def test_with_medial_ya(self, g2p):
        """Test syllable with ya-pin medial."""
        result = g2p.transliterate("ကျ")
        assert "k" in result
        assert "j" in result

    def test_with_medial_wa(self, g2p):
        """Test syllable with wa-hswe medial."""
        result = g2p.transliterate("ကွ")
        assert "k" in result
        assert "w" in result

    def test_tone_markers_in_output(self, g2p):
        """Test that tone markers appear in output."""
        result = g2p.transliterate("က")
        # Should have some Chao tone letter
        tone_chars = "˥˦˧˨˩"
        assert any(c in result for c in tone_chars)

    def test_no_tones_option(self):
        """Test disabling tones."""
        g2p = BurmeseG2P(include_tones=False)
        result = g2p.transliterate("က")
        tone_chars = "˥˦˧˨˩"
        assert not any(c in result for c in tone_chars)

    def test_no_phonation_option(self):
        """Test disabling phonation markers."""
        g2p = BurmeseG2P(include_phonation=False)
        result = g2p.transliterate("က")
        assert BREATHY_MARK not in result
        assert CREAKY_MARK not in result

    def test_visarga_produces_high_tone(self, g2p):
        """Test that visarga produces high tone."""
        result = g2p.transliterate("ကား")  # ka with visarga
        # High tone is ˥˩ 
        assert "˥" in result or "˩" in result

    def test_transliterate_tokenized(self, g2p):
        """Test tokenized output."""
        tokens = g2p.transliterate_tokenized("က")
        assert isinstance(tokens, list)
        assert len(tokens) > 0
        assert "k" in tokens

    def test_mixed_text_preserved(self, g2p):
        """Test that non-Burmese text is preserved."""
        result = g2p.transliterate("hello က world")
        assert "hello" in result
        assert "world" in result

    def test_empty_string(self, g2p):
        """Test empty input."""
        result = g2p.transliterate("")
        assert result == ""

    def test_numbers_preserved(self, g2p):
        """Test that numbers are preserved."""
        result = g2p.transliterate("က 123 ခ")
        assert "123" in result

    def test_nfd_output(self, g2p):
        """Test that output is in NFD form."""
        result = g2p.transliterate("က")
        assert result == unicodedata.normalize("NFD", result)


class TestCommonBurmeseWords:
    """Test common Burmese words."""

    @pytest.fixture
    def g2p(self):
        return BurmeseG2P()

    def test_myanmar_word(self, g2p):
        """Test မြန်မာ (Myanmar)."""
        result = g2p.transliterate("မြန်မာ")
        assert "m" in result
        # Has ya-yit medial
        assert "j" in result

    def test_mingalaba(self, g2p):
        """Test greeting word structure."""
        # မင်္ဂလာပါ - mingalaba (hello)
        result = g2p.transliterate("မင်္ဂလာပါ")
        assert "m" in result
        assert "l" in result
        assert "p" in result

    def test_simple_words(self, g2p):
        """Test various simple words."""
        # ကား (car) - has visarga
        result = g2p.transliterate("ကား")
        assert "k" in result

        # နာမည် (name)
        result = g2p.transliterate("နာမည်")
        assert "n" in result
        assert "m" in result


class TestEdgeCases:
    """Test edge cases and special inputs."""

    @pytest.fixture
    def g2p(self):
        return BurmeseG2P()

    def test_whitespace_preserved(self, g2p):
        """Test whitespace preservation."""
        result = g2p.transliterate("က  ခ")
        assert "  " in result

    def test_punctuation_preserved(self, g2p):
        """Test punctuation preservation."""
        result = g2p.transliterate("က!")
        assert "!" in result

    def test_repeated_parsing(self, g2p):
        """Test that parsing the same text gives consistent results."""
        text = "မြန်မာ"
        result1 = g2p.transliterate(text)
        result2 = g2p.transliterate(text)
        assert result1 == result2

    def test_tokenized_consistency(self, g2p):
        """Test tokenized output consistency."""
        text = "က"
        tokens1 = g2p.transliterate_tokenized(text)
        tokens2 = g2p.transliterate_tokenized(text)
        assert tokens1 == tokens2


class TestTonePatterns:
    """Test specific tone patterns."""

    @pytest.fixture
    def g2p(self):
        return BurmeseG2P()

    def test_low_tone_default(self, g2p):
        """Test that basic open syllables get low tone."""
        result = g2p.transliterate("ကာ")  # Should be low tone
        assert "˨" in result or "˩" in result

    def test_checked_tone_with_stop(self, g2p):
        """Test checked tone with stop coda."""
        result = g2p.transliterate("ကတ်")  # Should be checked
        assert "˥" in result  # Checked tone marker

    def test_creaky_with_anusvara(self, g2p):
        """Test creaky tone with anusvara."""
        result = g2p.transliterate("ကံ")  # With anusvara
        assert "˧" in result  # Creaky tone


class TestMedialCombinations:
    """Test various medial combinations."""

    @pytest.fixture
    def g2p(self):
        return BurmeseG2P()

    def test_ya_pin(self, g2p):
        """Test ya-pin medial ျ."""
        result = g2p.transliterate("ကျ")
        assert "j" in result

    def test_ya_yit(self, g2p):
        """Test ya-yit medial ြ."""
        result = g2p.transliterate("ကြ")
        assert "j" in result

    def test_wa_hswe(self, g2p):
        """Test wa-hswe medial ွ."""
        result = g2p.transliterate("ကွ")
        assert "w" in result

    def test_ha_hto(self, g2p):
        """Test ha-hto medial ှ (aspiration)."""
        result = g2p.transliterate("မှ")
        assert "m" in result
        # Should add aspiration
        assert "ʰ" in result or "h" in result
