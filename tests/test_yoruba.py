"""Tests for Yoruba G2P converter."""

import unicodedata

import pytest

from epitone.yoruba import YorubaG2P
from epitone.yoruba.data import (
    CONSONANTS,
    ORAL_VOWELS,
    NASAL_VOWELS,
    TONE_TO_CHAO,
    Tone,
    TIE_BAR,
    SYLLABIC,
    decompose_char,
    get_tone_from_char,
    strip_tone,
    is_vowel,
    is_consonant,
    get_consonant_ipa,
    get_vowel_ipa,
)


def nfd(text: str) -> str:
    """Normalize text to NFD for comparison with G2P output."""
    return unicodedata.normalize("NFD", text)


class TestYorubaData:
    """Test Yoruba data utilities."""

    def test_decompose_high_tone(self):
        base, tone = decompose_char("á")
        assert base == "a"
        assert tone == Tone.HIGH

    def test_decompose_low_tone(self):
        base, tone = decompose_char("à")
        assert base == "a"
        assert tone == Tone.LOW

    def test_decompose_mid_tone(self):
        base, tone = decompose_char("a")
        assert base == "a"
        assert tone is None  # Mid tone has no mark

    def test_decompose_underdot_with_tone(self):
        # ẹ́ = ẹ with high tone
        base, tone = decompose_char("ẹ́")
        assert base == "ẹ"
        assert tone == Tone.HIGH

    def test_get_tone_from_char(self):
        assert get_tone_from_char("á") == Tone.HIGH
        assert get_tone_from_char("à") == Tone.LOW
        assert get_tone_from_char("a") == Tone.MID

    def test_strip_tone(self):
        assert strip_tone("á") == "a"
        assert strip_tone("à") == "a"
        assert strip_tone("a") == "a"
        assert strip_tone("ẹ́") == "ẹ"

    def test_is_vowel(self):
        assert is_vowel("a")
        assert is_vowel("á")
        assert is_vowel("ẹ")
        assert is_vowel("ọ́")
        assert not is_vowel("b")
        assert not is_vowel("ṣ")

    def test_is_consonant(self):
        assert is_consonant("b")
        assert is_consonant("ṣ")
        assert is_consonant("g")
        assert not is_consonant("a")
        assert not is_consonant("ẹ")


class TestConsonantMappings:
    """Test consonant IPA mappings."""

    def test_simple_consonants(self):
        assert get_consonant_ipa("b") == "b"
        assert get_consonant_ipa("d") == "d"
        assert get_consonant_ipa("f") == "f"
        assert get_consonant_ipa("k") == "k"
        assert get_consonant_ipa("l") == "l"
        assert get_consonant_ipa("m") == "m"
        assert get_consonant_ipa("n") == "n"
        assert get_consonant_ipa("s") == "s"
        assert get_consonant_ipa("t") == "t"
        assert get_consonant_ipa("w") == "w"

    def test_p_is_labiovelar(self):
        """'p' in Yoruba is /k͡p/, NOT /p/."""
        ipa = get_consonant_ipa("p")
        assert ipa == f"k{TIE_BAR}p"
        assert "k" in ipa
        assert TIE_BAR in ipa

    def test_gb_digraph(self):
        """'gb' is a single labial-velar phoneme /ɡ͡b/."""
        ipa = get_consonant_ipa("gb")
        assert ipa == f"ɡ{TIE_BAR}b"
        assert TIE_BAR in ipa

    def test_j_is_affricate(self):
        """'j' is the affricate /d͡ʒ/."""
        ipa = get_consonant_ipa("j")
        assert ipa == f"d{TIE_BAR}ʒ"
        assert TIE_BAR in ipa

    def test_s_with_underdot(self):
        """'ṣ' is /ʃ/."""
        assert get_consonant_ipa("ṣ") == "ʃ"

    def test_r_is_tap(self):
        """'r' is an alveolar tap /ɾ/."""
        assert get_consonant_ipa("r") == "ɾ"

    def test_y_is_palatal(self):
        """'y' is the palatal approximant /j/."""
        assert get_consonant_ipa("y") == "j"


class TestVowelMappings:
    """Test vowel IPA mappings."""

    def test_oral_vowels(self):
        assert get_vowel_ipa("a") == "a"
        assert get_vowel_ipa("e") == "e"
        assert get_vowel_ipa("ẹ") == "ɛ"
        assert get_vowel_ipa("i") == "i"
        assert get_vowel_ipa("o") == "o"
        assert get_vowel_ipa("ọ") == "ɔ"
        assert get_vowel_ipa("u") == "u"

    def test_oral_vowels_with_tone(self):
        # Tone should be stripped for vowel lookup
        assert get_vowel_ipa("á") == "a"
        assert get_vowel_ipa("è") == "e"
        assert get_vowel_ipa("ẹ́") == "ɛ"

    def test_nasal_vowels(self):
        assert get_vowel_ipa("a", is_nasal=True) == "ã"
        assert get_vowel_ipa("ẹ", is_nasal=True) == "ɛ̃"
        assert get_vowel_ipa("i", is_nasal=True) == "ĩ"
        assert get_vowel_ipa("ọ", is_nasal=True) == "ɔ̃"
        assert get_vowel_ipa("u", is_nasal=True) == "ũ"

    def test_non_nasalizable_vowels(self):
        # e and o don't form nasal vowels
        assert get_vowel_ipa("e", is_nasal=True) == "e"
        assert get_vowel_ipa("o", is_nasal=True) == "o"


class TestTones:
    """Test tone mappings."""

    def test_chao_letters(self):
        assert TONE_TO_CHAO[Tone.HIGH] == "˦"
        assert TONE_TO_CHAO[Tone.MID] == "˧"
        assert TONE_TO_CHAO[Tone.LOW] == "˨"


class TestYorubaG2P:
    """Test Yoruba G2P converter."""

    @pytest.fixture
    def g2p(self):
        return YorubaG2P()

    def test_simple_cv_mid_tone(self, g2p):
        """Test simple CV syllable with mid tone."""
        result = g2p.transliterate("ba")
        assert "b" in result
        assert "a" in result
        assert "˧" in result  # Mid tone

    def test_simple_cv_high_tone(self, g2p):
        """Test simple CV syllable with high tone."""
        result = g2p.transliterate("bá")
        assert "b" in result
        assert "a" in result
        assert "˦" in result  # High tone

    def test_simple_cv_low_tone(self, g2p):
        """Test simple CV syllable with low tone."""
        result = g2p.transliterate("bà")
        assert "b" in result
        assert "a" in result
        assert "˨" in result  # Low tone

    def test_baba_with_tones(self, g2p):
        """Test 'bàbá' (father) - low + high."""
        result = g2p.transliterate("bàbá")
        assert "ba˨" in result
        assert "ba˦" in result

    def test_p_becomes_labiovelar(self, g2p):
        """Test that 'p' becomes /k͡p/."""
        result = g2p.transliterate("pa")
        assert f"k{TIE_BAR}p" in result

    def test_gb_digraph(self, g2p):
        """Test 'gb' digraph becomes /ɡ͡b/."""
        result = g2p.transliterate("gba")
        assert f"ɡ{TIE_BAR}b" in result

    def test_j_affricate(self, g2p):
        """Test 'j' becomes /d͡ʒ/."""
        result = g2p.transliterate("ja")
        assert f"d{TIE_BAR}ʒ" in result

    def test_s_underdot(self, g2p):
        """Test 'ṣ' becomes /ʃ/."""
        result = g2p.transliterate("ṣe")
        assert "ʃ" in result
        assert "e" in result

    def test_open_mid_vowels(self, g2p):
        """Test ẹ and ọ vowels."""
        result_e = g2p.transliterate("bẹ")
        result_o = g2p.transliterate("bọ")
        assert "ɛ" in result_e
        assert "ɔ" in result_o

    def test_nasal_vowel_word_final(self, g2p):
        """Test nasal vowel at word end (Vn)."""
        result = g2p.transliterate("san")  # Nasal 'a'
        assert nfd("ã") in result  # NFD: a + combining tilde

    def test_nasal_vowel_before_consonant(self, g2p):
        """Test nasal vowel before consonant."""
        result = g2p.transliterate("sàn")
        assert nfd("ã") in result  # NFD: a + combining tilde
        assert "˨" in result  # Low tone preserved

    def test_vowel_only_syllable(self, g2p):
        """Test V syllable (no onset)."""
        result = g2p.transliterate("à")  # 'he/she'
        assert "a" in result
        assert "˨" in result

    def test_multiple_syllables(self, g2p):
        """Test multi-syllable word."""
        result = g2p.transliterate("ọmọ")  # 'child'
        # Should have two syllables, both with ɔ
        assert result.count("ɔ") == 2

    def test_gbogbo(self, g2p):
        """Test 'gbogbo' (all)."""
        result = g2p.transliterate("gbogbo")
        # Two gb syllables
        assert result.count(f"ɡ{TIE_BAR}b") == 2
        assert result.count("o") == 2

    def test_no_tones_option(self):
        """Test disabling tones."""
        g2p = YorubaG2P(include_tones=False)
        result = g2p.transliterate("bá")
        assert "˦" not in result
        assert "˧" not in result
        assert "˨" not in result
        assert "ba" in result

    def test_transliterate_tokenized(self, g2p):
        """Test tokenized output."""
        tokens = g2p.transliterate_tokenized("bá")
        assert "b" in tokens
        assert "a" in tokens
        assert "˦" in tokens

    def test_mixed_text_preserved(self, g2p):
        """Test that non-Yoruba text is preserved."""
        result = g2p.transliterate("xyz bá 123")
        assert "xyz" in result  # Non-Yoruba consonant cluster
        assert "123" in result

    def test_empty_string(self, g2p):
        """Test empty input."""
        result = g2p.transliterate("")
        assert result == ""

    def test_numbers_preserved(self, g2p):
        """Test that numbers are preserved."""
        result = g2p.transliterate("ọdún 2024")
        assert "2024" in result


class TestSyllabicNasals:
    """Test syllabic nasal handling."""

    @pytest.fixture
    def g2p(self):
        return YorubaG2P()

    def test_syllabic_m_high_tone(self, g2p):
        """Test syllabic 'm' with high tone."""
        # ḿbà "I grabbed" - m with high tone before consonant
        result = g2p.transliterate("ḿbà")
        # Should have syllabic m with syllabicity mark
        assert SYLLABIC in result or "m̩" in result

    def test_syllabic_n_high_tone(self, g2p):
        """Test syllabic 'n' with high tone."""
        # ń lọ "I am going"
        result = g2p.transliterate("ń lọ")
        assert "˦" in result  # High tone on n


class TestCommonYorubaWords:
    """Test common Yoruba words."""

    @pytest.fixture
    def g2p(self):
        return YorubaG2P()

    def test_oruko(self, g2p):
        """Test 'orúkọ' (name)."""
        result = g2p.transliterate("orúkọ")
        assert "o" in result
        assert "ɾ" in result  # r is tap
        assert "ɔ" in result  # ọ
        assert "˦" in result  # High tone on ú

    def test_omo(self, g2p):
        """Test 'ọmọ' (child)."""
        result = g2p.transliterate("ọmọ")
        assert result.count("ɔ") == 2
        assert "m" in result

    def test_ile(self, g2p):
        """Test 'ilé' (house)."""
        result = g2p.transliterate("ilé")
        assert "i" in result
        assert "l" in result
        assert "e" in result
        assert "˦" in result

    def test_eja(self, g2p):
        """Test 'ẹja' (fish)."""
        result = g2p.transliterate("ẹja")
        assert "ɛ" in result
        assert f"d{TIE_BAR}ʒ" in result  # j → /d͡ʒ/

    def test_pupa(self, g2p):
        """Test 'pupa' (red)."""
        result = g2p.transliterate("pupa")
        # Both p's should become /k͡p/
        assert result.count(f"k{TIE_BAR}p") == 2


class TestTieBarUsage:
    """Test that tie bars are used correctly."""

    @pytest.fixture
    def g2p(self):
        return YorubaG2P()

    def test_tie_bar_in_p(self, g2p):
        result = g2p.transliterate("pa")
        assert TIE_BAR in result
        assert f"k{TIE_BAR}p" in result

    def test_tie_bar_in_gb(self, g2p):
        result = g2p.transliterate("gba")
        assert TIE_BAR in result
        assert f"ɡ{TIE_BAR}b" in result

    def test_tie_bar_in_j(self, g2p):
        result = g2p.transliterate("ja")
        assert TIE_BAR in result
        assert f"d{TIE_BAR}ʒ" in result

    def test_no_tie_bar_in_simple_consonants(self, g2p):
        """Simple consonants should not have tie bars."""
        result = g2p.transliterate("ba da fa ka")
        # Should have tie bars only where expected (none here)
        # Count tie bars - should be 0 for these consonants
        assert result.count(TIE_BAR) == 0


class TestEdgeCases:
    """Test edge cases and special inputs."""

    @pytest.fixture
    def g2p(self):
        return YorubaG2P()

    def test_uppercase(self, g2p):
        """Test uppercase input."""
        result = g2p.transliterate("BA")
        assert "b" in result.lower()
        assert "a" in result.lower()

    def test_mixed_case(self, g2p):
        """Test mixed case input."""
        result = g2p.transliterate("Bàbá")
        assert "b" in result
        assert "˨" in result
        assert "˦" in result

    def test_punctuation_preserved(self, g2p):
        """Test punctuation preservation."""
        result = g2p.transliterate("bá!")
        assert "!" in result

    def test_whitespace_preserved(self, g2p):
        """Test whitespace preservation."""
        result = g2p.transliterate("bá  bà")
        assert "  " in result
