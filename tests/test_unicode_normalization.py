"""Tests for Unicode NFD normalization in all G2P modules.

All G2P modules should output strings in Unicode NFD (Normalized Form Decomposed).
This ensures consistent handling of combining characters across all languages.
"""

import unicodedata

import pytest

from epitone import (
    HanoiG2P,
    NgheAnG2P,
    SaiGonG2P,
    ThaiG2P,
    YorubaG2P,
    nfd_equal,
    to_nfc,
    to_nfd,
)


class TestUnicodeUtils:
    """Test unicode utility functions."""

    def test_to_nfd(self):
        """Test NFD normalization."""
        # Precomposed to decomposed
        result = to_nfd("ã")  # a with tilde
        assert len(result) == 2  # a + combining tilde
        assert result[0] == "a"
        assert result[1] == "\u0303"  # combining tilde

    def test_to_nfc(self):
        """Test NFC normalization."""
        # Decomposed to precomposed
        result = to_nfc("a\u0303")  # a + combining tilde
        assert len(result) == 1
        assert result == "ã"

    def test_nfd_equal(self):
        """Test NFD equality comparison."""
        assert nfd_equal("ã", "a\u0303")
        assert nfd_equal("ẹ́", "e\u0323\u0301")
        assert not nfd_equal("a", "b")


class TestThaiNFDOutput:
    """Test Thai G2P outputs NFD-normalized strings."""

    @pytest.fixture
    def g2p(self):
        return ThaiG2P()

    def test_transliterate_is_nfd(self, g2p):
        """Test that transliterate output is NFD."""
        result = g2p.transliterate("กา")
        assert unicodedata.is_normalized("NFD", result)

    def test_transliterate_tokenized_is_nfd(self, g2p):
        """Test that transliterate_tokenized output is NFD."""
        tokens = g2p.transliterate_tokenized("กา")
        for token in tokens:
            assert unicodedata.is_normalized("NFD", token)

    def test_aspirated_consonant_nfd(self, g2p):
        """Test that aspirated consonants (with superscript h) are NFD."""
        result = g2p.transliterate("ขา")  # kh onset
        assert unicodedata.is_normalized("NFD", result)
        assert "kʰ" in result or to_nfd("kʰ") in result


class TestVietnameseNFDOutput:
    """Test Vietnamese G2P outputs NFD-normalized strings."""

    @pytest.fixture
    def hanoi(self):
        return HanoiG2P()

    @pytest.fixture
    def nghe_an(self):
        return NgheAnG2P()

    @pytest.fixture
    def sai_gon(self):
        return SaiGonG2P()

    def test_hanoi_transliterate_is_nfd(self, hanoi):
        """Test that Hanoi transliterate output is NFD."""
        result = hanoi.transliterate("xin chào")
        assert unicodedata.is_normalized("NFD", result)

    def test_hanoi_transliterate_tokenized_is_nfd(self, hanoi):
        """Test that Hanoi transliterate_tokenized output is NFD."""
        tokens = hanoi.transliterate_tokenized("xin chào")
        for token in tokens:
            assert unicodedata.is_normalized("NFD", token)

    def test_nghe_an_transliterate_is_nfd(self, nghe_an):
        """Test that Nghệ An transliterate output is NFD."""
        result = nghe_an.transliterate("xin chào")
        assert unicodedata.is_normalized("NFD", result)

    def test_sai_gon_transliterate_is_nfd(self, sai_gon):
        """Test that Sài Gòn transliterate output is NFD."""
        result = sai_gon.transliterate("xin chào")
        assert unicodedata.is_normalized("NFD", result)

    def test_long_vowel_nfd(self, hanoi):
        """Test that long vowels with length mark are NFD."""
        result = hanoi.transliterate("ba")  # has long 'a'
        assert unicodedata.is_normalized("NFD", result)


class TestYorubaNFDOutput:
    """Test Yoruba G2P outputs NFD-normalized strings."""

    @pytest.fixture
    def g2p(self):
        return YorubaG2P()

    def test_transliterate_is_nfd(self, g2p):
        """Test that transliterate output is NFD."""
        result = g2p.transliterate("bàbá")
        assert unicodedata.is_normalized("NFD", result)

    def test_transliterate_tokenized_is_nfd(self, g2p):
        """Test that transliterate_tokenized output is NFD."""
        tokens = g2p.transliterate_tokenized("bàbá")
        for token in tokens:
            assert unicodedata.is_normalized("NFD", token)

    def test_nasal_vowel_nfd(self, g2p):
        """Test that nasal vowels (with combining tilde) are NFD."""
        result = g2p.transliterate("san")  # nasal 'a'
        assert unicodedata.is_normalized("NFD", result)
        # Should have decomposed tilde, not precomposed
        assert "a\u0303" in result  # a + combining tilde

    def test_syllabic_nasal_nfd(self, g2p):
        """Test that syllabic nasals (with syllabicity mark) are NFD."""
        result = g2p.transliterate("ń")  # syllabic n with high tone
        assert unicodedata.is_normalized("NFD", result)
        # Should have combining syllabicity mark
        assert "\u0329" in result  # combining vertical line below

    def test_tie_bar_nfd(self, g2p):
        """Test that affricates/labiovelars with tie bar are NFD."""
        result = g2p.transliterate("gbà")
        assert unicodedata.is_normalized("NFD", result)
        # Tie bar should be combining
        assert "\u0361" in result  # combining double inverted breve

    def test_open_mid_vowels_nfd(self, g2p):
        """Test that open-mid vowels (ɛ, ɔ) are NFD."""
        result_e = g2p.transliterate("bẹ")
        result_o = g2p.transliterate("bọ")
        assert unicodedata.is_normalized("NFD", result_e)
        assert unicodedata.is_normalized("NFD", result_o)


class TestNFDConsistency:
    """Test that all modules produce consistent NFD output."""

    def test_comparing_across_normalizations(self):
        """Test that NFD output can be compared regardless of input normalization."""
        g2p = YorubaG2P()

        # Input in NFC (precomposed)
        nfc_input = "bàbá"
        # Input in NFD (decomposed)
        nfd_input = unicodedata.normalize("NFD", "bàbá")

        result_from_nfc = g2p.transliterate(nfc_input)
        result_from_nfd = g2p.transliterate(nfd_input)

        # Both should produce identical NFD output
        assert result_from_nfc == result_from_nfd
        assert unicodedata.is_normalized("NFD", result_from_nfc)
        assert unicodedata.is_normalized("NFD", result_from_nfd)
