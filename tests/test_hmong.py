"""Tests for Hmong G2P converters (RPA and Dananshan)."""

import unicodedata

import pytest

from epitone.hmong import (
    DananshanG2P,
    HmongDawG2P,
    HmongDialect,
    HmongRPAG2P,
    MongLengG2P,
)
from epitone.hmong.data import (
    BREATHY_VOICE,
    HMONG_DAW_TONES,
    MONG_LENG_TONES,
    RPA_CONSONANTS,
    RPA_VOWELS,
    add_breathy_voice,
)
from epitone.hmong.rpa import parse_syllable, parse_syllables


def nfd(s: str) -> str:
    """Normalize string to NFD form for comparison."""
    return unicodedata.normalize("NFD", s)


# ============================================================================
# RPA Syllable Parsing Tests
# ============================================================================

class TestRPASyllableParsing:
    """Test RPA syllable parsing."""
    
    def test_parse_simple_cv(self):
        """Test parsing simple CV syllables."""
        syllable, pos = parse_syllable("pa")
        assert syllable is not None
        assert syllable.onset == "p"
        assert syllable.nucleus == "a"
        assert syllable.tone_letter == ""
        assert pos == 2
    
    def test_parse_cv_with_tone(self):
        """Test parsing CV syllables with tone letter."""
        syllable, pos = parse_syllable("pab")
        assert syllable is not None
        assert syllable.onset == "p"
        assert syllable.nucleus == "a"
        assert syllable.tone_letter == "b"
        assert syllable.tone_name == "high"
    
    def test_parse_all_tone_letters(self):
        """Test all RPA tone letters."""
        tone_tests = [
            ("pab", "b", "high"),
            ("paj", "j", "high_falling"),
            ("pav", "v", "mid_rising"),
            ("pas", "s", "low"),
            ("pag", "g", "breathy_low"),
            ("pam", "m", "low_falling"),
            ("pad", "d", "low_rising"),
            ("pa", "", "mid"),
        ]
        for text, expected_letter, expected_name in tone_tests:
            syllable, _ = parse_syllable(text)
            assert syllable is not None, f"Failed to parse: {text}"
            assert syllable.tone_letter == expected_letter, f"Wrong tone letter for {text}"
            assert syllable.tone_name == expected_name, f"Wrong tone name for {text}"
    
    def test_parse_cluster_onset(self):
        """Test consonant cluster onsets."""
        clusters = ["pl", "plh", "ts", "tsh", "nts", "ntsh", "tx", "ntx"]
        for cluster in clusters:
            text = cluster + "a"
            syllable, _ = parse_syllable(text)
            assert syllable is not None, f"Failed to parse: {text}"
            assert syllable.onset == cluster, f"Wrong onset for {text}: got {syllable.onset}"
    
    def test_parse_prenasalized_onset(self):
        """Test prenasalized consonant onsets."""
        prenasalized = ["np", "nt", "nk", "nc", "nph", "nth", "nkh", "nch"]
        for pn in prenasalized:
            text = pn + "a"
            syllable, _ = parse_syllable(text)
            assert syllable is not None, f"Failed to parse: {text}"
            assert syllable.onset == pn, f"Wrong onset for {text}: got {syllable.onset}"
    
    def test_parse_nasal_vowels(self):
        """Test nasal vowel parsing (ee, oo, aa)."""
        nasal_tests = [
            ("ee", True),
            ("oo", True),
            ("aa", True),
            ("a", False),
            ("e", False),
            ("o", False),
        ]
        for nucleus, expected_nasal in nasal_tests:
            syllable, _ = parse_syllable("p" + nucleus)
            assert syllable is not None
            assert syllable.is_nasal_vowel == expected_nasal, f"Wrong nasal flag for {nucleus}"
    
    def test_parse_diphthongs(self):
        """Test diphthong parsing."""
        diphthongs = ["ai", "au", "aw", "ia", "ua"]
        for diph in diphthongs:
            text = "p" + diph
            syllable, _ = parse_syllable(text)
            assert syllable is not None, f"Failed to parse: {text}"
            assert syllable.nucleus == diph, f"Wrong nucleus for {text}"
    
    def test_parse_multiple_syllables(self):
        """Test parsing multiple syllables."""
        syllables = list(parse_syllables("kuv hlub koj"))
        assert len(syllables) == 3
        assert syllables[0].raw == "kuv"
        assert syllables[1].raw == "hlub"
        assert syllables[2].raw == "koj"
    
    def test_parse_vowel_initial(self):
        """Test parsing vowel-initial syllables."""
        syllable, _ = parse_syllable("ab")
        assert syllable is not None
        assert syllable.onset == ""
        assert syllable.nucleus == "a"
        assert syllable.tone_letter == "b"


# ============================================================================
# Hmong Daw (White Hmong) G2P Tests
# ============================================================================

class TestHmongDawG2P:
    """Test Hmong Daw G2P converter."""
    
    @pytest.fixture
    def g2p(self):
        return HmongDawG2P()
    
    @pytest.fixture
    def g2p_no_tones(self):
        return HmongDawG2P(include_tones=False)
    
    def test_simple_syllable(self, g2p):
        """Test simple syllable conversion."""
        result = g2p.transliterate("pa")
        # pa with mid tone (no letter) = /pa˧/
        assert "p" in result
        assert "a" in result
        assert "˧" in result  # Mid tone for Hmong Daw
    
    def test_tone_b_high(self, g2p):
        """Test -b tone (high level)."""
        result = g2p.transliterate("peb")
        # -b tone in Hmong Daw = ˥ (high)
        assert "˥" in result
    
    def test_tone_j_high_falling(self, g2p):
        """Test -j tone (high falling)."""
        result = g2p.transliterate("poj")
        assert "˥˨" in result
    
    def test_tone_v_mid_rising(self, g2p):
        """Test -v tone (mid rising)."""
        result = g2p.transliterate("kuv")
        assert "˨˦" in result
    
    def test_tone_s_low(self, g2p):
        """Test -s tone (low level)."""
        result = g2p.transliterate("tus")
        assert "˨˩" in result
    
    def test_tone_g_breathy(self, g2p):
        """Test -g tone (breathy low)."""
        result = g2p.transliterate("pog")
        # Should have breathy voice diacritic on vowel
        assert nfd(BREATHY_VOICE) in nfd(result)
        assert "˨" in result
    
    def test_tone_m_low_falling(self, g2p):
        """Test -m tone (low falling/checked)."""
        result = g2p.transliterate("tam")
        assert "˩" in result
    
    def test_tone_d_low_rising(self, g2p):
        """Test -d tone (low rising)."""
        result = g2p.transliterate("tad")
        assert "˩˧" in result
    
    def test_nasal_vowel_ee(self, g2p):
        """Test nasalized vowel ee."""
        result = g2p.transliterate("neeb")
        # ee = nasalized /e/ = ẽ
        assert nfd("ẽ") in nfd(result)
    
    def test_nasal_vowel_oo(self, g2p):
        """Test nasalized vowel oo."""
        result = g2p.transliterate("noog")
        # oo = nasalized /ɔ/ = ɔ̃
        assert nfd("ɔ̃") in nfd(result) or nfd("ɔ") in nfd(result)
    
    def test_nasal_vowel_aa(self, g2p):
        """Test nasalized vowel aa."""
        result = g2p.transliterate("kaab")
        # aa = nasalized /a/ = ã
        assert nfd("ã") in nfd(result)
    
    def test_prenasalized_onset(self, g2p):
        """Test prenasalized consonant onsets."""
        result = g2p.transliterate("ntawv")
        # nt = /nt/
        assert "nt" in result
    
    def test_cluster_pl(self, g2p):
        """Test /pl/ cluster (not superscript)."""
        result = g2p.transliterate("plab")
        # Should be /pl/, not /pˡ/
        assert "pl" in result
        assert "ˡ" not in result  # No superscript lateral
    
    def test_voiceless_lateral(self, g2p):
        """Test voiceless lateral hl."""
        result = g2p.transliterate("hlub")
        # hl = /l̥/
        assert "l̥" in result or nfd("l̥") in nfd(result)
    
    def test_no_tones_option(self, g2p_no_tones):
        """Test converter without tones."""
        result = g2p_no_tones.transliterate("kuv")
        # Should not have tone letters
        assert "˥" not in result
        assert "˩" not in result
        assert "˧" not in result
        assert "˨" not in result
        assert "˦" not in result
    
    def test_tokenized(self, g2p):
        """Test tokenized output."""
        tokens = g2p.transliterate_tokenized("kuv")
        assert len(tokens) == 3  # onset, nucleus, tone
        assert tokens[0] == "k"
        assert tokens[1] == "u"
        assert tokens[2] == "˨˦"  # mid_rising tone
    
    def test_multiple_syllables(self, g2p):
        """Test multiple syllables with spaces preserved."""
        result = g2p.transliterate("kuv hlub koj")
        assert " " in result  # Spaces preserved
    
    def test_nfd_output(self, g2p):
        """Test that output is in NFD form."""
        result = g2p.transliterate("noog")
        # Result should be NFD normalized
        assert result == nfd(result)
    
    def test_glottal_stop_onset(self, g2p):
        """Test vowel-initial syllables get glottal stop."""
        result = g2p.transliterate("ab")
        assert "ʔ" in result


# ============================================================================
# Mong Leng (Green Hmong) G2P Tests  
# ============================================================================

class TestMongLengG2P:
    """Test Mong Leng G2P converter."""
    
    @pytest.fixture
    def g2p(self):
        return MongLengG2P()
    
    def test_tone_b_different_from_hmong_daw(self, g2p):
        """Test -b tone has different value in Mong Leng."""
        result = g2p.transliterate("peb")
        # -b in Mong Leng = ˥˧ (53, high falling) vs Hmong Daw ˥ (55)
        assert "˥˧" in result
    
    def test_tone_g_different_from_hmong_daw(self, g2p):
        """Test -g tone has different value in Mong Leng."""
        result = g2p.transliterate("pog")
        # -g in Mong Leng = ˧ (33, mid) vs Hmong Daw ˨ (22)
        # Both should have breathy voice marker
        assert nfd(BREATHY_VOICE) in nfd(result)
        assert "˧" in result
    
    def test_mid_tone_different(self, g2p):
        """Test unmarked tone (mid) is different in Mong Leng."""
        result = g2p.transliterate("pa")
        # Unmarked in Mong Leng = ˧˥ (35, mid rising) vs Hmong Daw ˧ (33)
        assert "˧˥" in result
    
    def test_dialect_property(self, g2p):
        """Test dialect property."""
        assert g2p.dialect == HmongDialect.MONG_LENG


# ============================================================================
# Dananshan G2P Tests
# ============================================================================

class TestDananshanG2P:
    """Test Dananshan Miao G2P converter."""
    
    @pytest.fixture
    def g2p(self):
        return DananshanG2P()
    
    @pytest.fixture
    def g2p_no_tones(self):
        return DananshanG2P(include_tones=False)
    
    def test_simple_syllable(self, g2p):
        """Test simple syllable."""
        result = g2p.transliterate("ba1")
        # b = /p/, a = /a/, tone 1 = ˦˦
        assert "p" in result
        assert "a" in result
        assert "˦˦" in result
    
    def test_all_tones(self, g2p):
        """Test all 8 Dananshan tones."""
        tone_tests = [
            ("ba1", "˦˦"),   # High level
            ("ba2", "˧˩"),   # Mid falling
            ("ba3", "˦˧"),   # High-mid falling
            ("ba4", "˥˧˥"),  # Contour
            ("ba5", "˧˧"),   # Mid level
            ("ba6", "˨˦"),   # Low rising
            ("ba7", "˧˥"),   # Mid rising
            ("ba8", "˩˧"),   # Low-mid rising
        ]
        for text, expected_tone in tone_tests:
            result = g2p.transliterate(text)
            assert expected_tone in result, f"Wrong tone for {text}: got {result}"
    
    def test_aspirated_consonant(self, g2p):
        """Test aspirated consonants."""
        result = g2p.transliterate("pa1")
        # p in Dananshan = /pʰ/
        assert "pʰ" in result
    
    def test_retroflex_consonant(self, g2p):
        """Test retroflex consonants."""
        result = g2p.transliterate("zha1")
        # zh = /tʂ/
        assert "tʂ" in result
    
    def test_palatal_consonant(self, g2p):
        """Test palatal consonants."""
        result = g2p.transliterate("ja1")
        # j = /tɕ/
        assert "tɕ" in result
    
    def test_diphthong(self, g2p):
        """Test diphthongs."""
        result = g2p.transliterate("bai1")
        assert "ai" in result
    
    def test_front_rounded_vowel(self, g2p):
        """Test front rounded vowel ü."""
        result = g2p.transliterate("nü1")
        # ü = /y/
        assert "y" in result
    
    def test_no_tones_option(self, g2p_no_tones):
        """Test converter without tones."""
        result = g2p_no_tones.transliterate("ba1")
        assert "˦" not in result
        assert "˧" not in result
    
    def test_tokenized(self, g2p):
        """Test tokenized output."""
        tokens = g2p.transliterate_tokenized("ba1")
        assert len(tokens) == 3  # onset, nucleus, tone
        assert tokens[0] == "p"  # b -> p
        assert tokens[1] == "a"
        assert tokens[2] == "˦˦"
    
    def test_nfd_output(self, g2p):
        """Test that output is in NFD form."""
        result = g2p.transliterate("ma3")
        assert result == nfd(result)
    
    def test_dialect_property(self, g2p):
        """Test dialect property."""
        assert g2p.dialect == HmongDialect.DANANSHAN


# ============================================================================
# Data Module Tests
# ============================================================================

class TestHmongData:
    """Test Hmong data module utilities."""
    
    def test_add_breathy_voice(self):
        """Test breathy voice diacritic addition."""
        result = add_breathy_voice("a")
        assert BREATHY_VOICE in result
        assert result.startswith("a")
    
    def test_add_breathy_voice_diphthong(self):
        """Test breathy voice on diphthong (goes on first vowel)."""
        result = add_breathy_voice("ai")
        # Breathy marker should be after 'a', before 'i'
        assert BREATHY_VOICE in result
        a_pos = result.index("a")
        breathy_pos = result.index(BREATHY_VOICE)
        i_pos = result.index("i")
        assert a_pos < breathy_pos < i_pos
    
    def test_tone_mappings_differ_between_dialects(self):
        """Test that tone mappings differ between Hmong Daw and Mong Leng."""
        # These tones should differ
        assert HMONG_DAW_TONES["high"] != MONG_LENG_TONES["high"]
        assert HMONG_DAW_TONES["breathy_low"] != MONG_LENG_TONES["breathy_low"]
        assert HMONG_DAW_TONES["mid"] != MONG_LENG_TONES["mid"]
    
    def test_rpa_consonants_no_superscripts(self):
        """Test that RPA consonants use standard IPA, no superscripts."""
        # Check prenasalized consonants use regular m, n, ŋ
        assert RPA_CONSONANTS["np"] == "mp"
        assert RPA_CONSONANTS["nt"] == "nt"
        assert RPA_CONSONANTS["nk"] == "ŋk"
        # No superscript markers
        for ipa in RPA_CONSONANTS.values():
            assert "ᵐ" not in ipa
            assert "ⁿ" not in ipa
            assert "ᵑ" not in ipa
            assert "ˡ" not in ipa
    
    def test_rpa_nasal_vowels(self):
        """Test that ee, oo, aa are nasal vowels."""
        assert RPA_VOWELS["ee"][1] is True  # is_nasal
        assert RPA_VOWELS["oo"][1] is True
        assert RPA_VOWELS["aa"][1] is True
        # Regular vowels are not nasal
        assert RPA_VOWELS["e"][1] is False
        assert RPA_VOWELS["o"][1] is False
        assert RPA_VOWELS["a"][1] is False


# ============================================================================
# Integration Tests
# ============================================================================

class TestHmongIntegration:
    """Integration tests for Hmong G2P."""
    
    def test_import_from_epitone(self):
        """Test that Hmong classes can be imported from epitone root."""
        from epitone import DananshanG2P, HmongDawG2P, MongLengG2P
        
        assert HmongDawG2P is not None
        assert MongLengG2P is not None
        assert DananshanG2P is not None
    
    def test_hmong_daw_common_words(self):
        """Test common Hmong Daw words."""
        g2p = HmongDawG2P()
        
        # "kuv" (I/me) - mid rising tone
        result = g2p.transliterate("kuv")
        assert "k" in result
        assert "u" in result
        assert "˨˦" in result
        
        # "koj" (you) - high falling tone
        result = g2p.transliterate("koj")
        assert "˥˨" in result
    
    def test_hmong_rpa_base_class(self):
        """Test that HmongRPAG2P can be instantiated directly."""
        g2p = HmongRPAG2P(dialect=HmongDialect.HMONG_DAW)
        result = g2p.transliterate("kuv")
        assert "˨˦" in result
        
        g2p = HmongRPAG2P(dialect=HmongDialect.MONG_LENG)
        result = g2p.transliterate("kuv")
        assert "˨˦" in result
    
    def test_invalid_dialect_for_rpa(self):
        """Test that RPA converter rejects invalid dialect."""
        with pytest.raises(ValueError):
            HmongRPAG2P(dialect=HmongDialect.DANANSHAN)
