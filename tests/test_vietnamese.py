"""Tests for Vietnamese G2P converters."""

import pytest

from epitone.vietnamese import HanoiG2P, NgheAnG2P, SaiGonG2P, Dialect
from epitone.vietnamese.shared import (
    decompose_char,
    extract_tone_from_nucleus,
    normalize_vietnamese,
    parse_syllable,
    parse_syllables,
    Syllable,
    TONE_NGANG,
)


class TestVietnameseShared:
    """Test shared Vietnamese utilities."""

    def test_normalize_vietnamese(self):
        # Test NFC normalization
        text = "việt nam"
        normalized = normalize_vietnamese(text)
        assert normalized == "việt nam"

    def test_decompose_char_with_tone(self):
        # á (a + acute)
        base, tone = decompose_char("á")
        assert base == "a"
        assert tone == "\u0301"  # acute accent

    def test_decompose_char_without_tone(self):
        base, tone = decompose_char("a")
        assert base == "a"
        assert tone is None

    def test_decompose_char_with_breve_and_tone(self):
        # ắ (a + breve + acute)
        base, tone = decompose_char("ắ")
        assert base == "ă"
        assert tone == "\u0301"

    def test_extract_tone_ngang(self):
        nucleus, tone = extract_tone_from_nucleus("a")
        assert nucleus == "a"
        assert tone == TONE_NGANG

    def test_extract_tone_sac(self):
        nucleus, tone = extract_tone_from_nucleus("á")
        assert nucleus == "a"
        assert tone == "sac"

    def test_extract_tone_huyen(self):
        nucleus, tone = extract_tone_from_nucleus("à")
        assert nucleus == "a"
        assert tone == "huyen"

    def test_extract_tone_hoi(self):
        nucleus, tone = extract_tone_from_nucleus("ả")
        assert nucleus == "a"
        assert tone == "hoi"

    def test_extract_tone_nga(self):
        nucleus, tone = extract_tone_from_nucleus("ã")
        assert nucleus == "a"
        assert tone == "nga"

    def test_extract_tone_nang(self):
        nucleus, tone = extract_tone_from_nucleus("ạ")
        assert nucleus == "a"
        assert tone == "nang"


class TestSyllableParsing:
    """Test Vietnamese syllable parsing."""

    def test_simple_cv(self):
        syllable, _ = parse_syllable("ma")
        assert syllable.onset == "m"
        assert syllable.nucleus == "a"
        assert syllable.coda == ""
        assert syllable.tone == TONE_NGANG

    def test_syllable_with_tone(self):
        syllable, _ = parse_syllable("má")
        assert syllable.onset == "m"
        assert syllable.nucleus == "a"
        assert syllable.tone == "sac"

    def test_syllable_with_coda(self):
        syllable, _ = parse_syllable("man")
        assert syllable.onset == "m"
        assert syllable.nucleus == "a"
        assert syllable.coda == "n"

    def test_syllable_with_digraph_onset(self):
        syllable, _ = parse_syllable("cha")
        assert syllable.onset == "ch"
        assert syllable.nucleus == "a"

    def test_syllable_with_digraph_coda(self):
        syllable, _ = parse_syllable("mang")
        assert syllable.onset == "m"
        assert syllable.nucleus == "a"
        assert syllable.coda == "ng"

    def test_syllable_no_onset(self):
        syllable, _ = parse_syllable("an")
        assert syllable.onset == ""
        assert syllable.nucleus == "a"
        assert syllable.coda == "n"

    def test_checked_syllable(self):
        syllable, _ = parse_syllable("mát")
        assert syllable.is_checked is True

    def test_open_syllable(self):
        syllable, _ = parse_syllable("ma")
        assert syllable.is_checked is False

    def test_diphthong_parsing(self):
        syllable, _ = parse_syllable("mai")
        assert syllable.onset == "m"
        # The nucleus should capture the diphthong
        assert "a" in syllable.nucleus or "i" in syllable.coda

    def test_parse_multiple_syllables(self):
        syllables = list(parse_syllables("xin chào"))
        assert len(syllables) == 2
        assert syllables[0].onset == "x"
        assert syllables[1].onset == "ch"

    def test_parse_with_tone_marks(self):
        syllables = list(parse_syllables("việt nam"))
        assert len(syllables) == 2
        assert syllables[0].tone == "nang"  # ệ has dot below
        assert syllables[1].tone == TONE_NGANG


class TestHanoiG2P:
    """Test Hanoi (Northern) Vietnamese G2P."""

    @pytest.fixture
    def g2p(self):
        return HanoiG2P()

    def test_dialect(self, g2p):
        assert g2p.dialect == Dialect.HANOI

    def test_simple_transliteration(self, g2p):
        result = g2p.transliterate("ma")
        assert "m" in result
        assert "aː" in result
        assert "˧" in result  # ngang tone

    def test_onset_d_becomes_z(self, g2p):
        result = g2p.transliterate("da")
        assert "z" in result  # d → /z/ in Hanoi

    def test_onset_r_becomes_z(self, g2p):
        result = g2p.transliterate("ra")
        assert "z" in result  # r → /z/ in Hanoi

    def test_onset_gi_becomes_z(self, g2p):
        result = g2p.transliterate("già")
        assert "z" in result  # gi → /z/ in Hanoi

    def test_onset_tr_becomes_tc(self, g2p):
        result = g2p.transliterate("tra")
        assert "tɕ" in result  # tr → /tɕ/ in Hanoi

    def test_onset_s_stays_s(self, g2p):
        result = g2p.transliterate("sa")
        assert "s" in result  # s → /s/ in Hanoi (not retroflex)

    def test_tone_huyen(self, g2p):
        result = g2p.transliterate("mà")
        assert "˨˩" in result

    def test_tone_sac(self, g2p):
        result = g2p.transliterate("má")
        assert "˧˥" in result

    def test_tone_hoi(self, g2p):
        result = g2p.transliterate("mả")
        assert "˧˩˧" in result

    def test_tone_nga(self, g2p):
        result = g2p.transliterate("mã")
        assert "˧ˀ˥" in result  # Distinct from hỏi in Hanoi

    def test_tone_nang(self, g2p):
        result = g2p.transliterate("mạ")
        assert "˧ˀ˩" in result

    def test_null_onset_glottal_stop(self, g2p):
        result = g2p.transliterate("an")
        assert "ʔ" in result

    def test_transliterate_tokenized(self, g2p):
        tokens = g2p.transliterate_tokenized("ma")
        assert "m" in tokens
        assert "aː" in tokens
        assert "˧" in tokens

    def test_no_tones_option(self):
        g2p = HanoiG2P(include_tones=False)
        result = g2p.transliterate("má")
        assert "˧" not in result
        assert "˥" not in result

    def test_coda_nh(self, g2p):
        result = g2p.transliterate("minh")
        assert "ɲ" in result  # -nh → /ɲ/ in Hanoi

    def test_coda_ch(self, g2p):
        result = g2p.transliterate("mích")
        assert "c" in result  # -ch → /c/ in Hanoi


class TestNgheAnG2P:
    """Test Nghệ An (Central) Vietnamese G2P."""

    @pytest.fixture
    def g2p(self):
        return NgheAnG2P()

    def test_dialect(self, g2p):
        assert g2p.dialect == Dialect.NGHE_AN

    def test_onset_r_retroflex(self, g2p):
        result = g2p.transliterate("ra")
        assert "ʐ" in result  # r → /ʐ/ in Nghệ An

    def test_onset_s_retroflex(self, g2p):
        result = g2p.transliterate("sa")
        assert "ʂ" in result  # s → /ʂ/ in Nghệ An

    def test_onset_tr_retroflex(self, g2p):
        result = g2p.transliterate("tra")
        assert "ʈ" in result  # tr → /ʈ/ in Nghệ An

    def test_onset_d_becomes_z(self, g2p):
        result = g2p.transliterate("da")
        assert "z" in result  # d → /z/ in Nghệ An (like Hanoi)

    def test_hoi_nga_merge(self, g2p):
        # In Nghệ An, hỏi and ngã merge
        result_hoi = g2p.transliterate("mả")
        result_nga = g2p.transliterate("mã")
        # Both should have same tone: ˧˩˨
        assert "˧˩˨" in result_hoi
        assert "˧˩˨" in result_nga


class TestSaiGonG2P:
    """Test Sài Gòn (Southern) Vietnamese G2P."""

    @pytest.fixture
    def g2p(self):
        return SaiGonG2P()

    def test_dialect(self, g2p):
        assert g2p.dialect == Dialect.SAI_GON

    def test_onset_d_becomes_j(self, g2p):
        result = g2p.transliterate("da")
        assert "j" in result  # d → /j/ in Sài Gòn

    def test_onset_gi_becomes_j(self, g2p):
        result = g2p.transliterate("già")
        assert "j" in result  # gi → /j/ in Sài Gòn

    def test_onset_v_becomes_j(self, g2p):
        result = g2p.transliterate("và")
        assert "j" in result  # v → /j/ in Sài Gòn

    def test_onset_r_approximant(self, g2p):
        result = g2p.transliterate("ra")
        assert "ɹ" in result  # r → /ɹ/ in Sài Gòn

    def test_onset_s_retroflex(self, g2p):
        result = g2p.transliterate("sa")
        assert "ʂ" in result  # s → /ʂ/ in Sài Gòn

    def test_onset_tr_like_ch(self, g2p):
        result = g2p.transliterate("tra")
        assert "tɕ" in result  # tr → /tɕ/ in Sài Gòn (same as ch)

    def test_hoi_nga_merge(self, g2p):
        # In Sài Gòn, hỏi and ngã merge
        result_hoi = g2p.transliterate("mả")
        result_nga = g2p.transliterate("mã")
        # Both should have same tone: ˨˩˦
        assert "˨˩˦" in result_hoi
        assert "˨˩˦" in result_nga

    def test_coda_nh_merges_after_front_vowel(self, g2p):
        result = g2p.transliterate("minh")
        assert "ŋ" in result  # -nh → -ng after front vowel in Southern

    def test_coda_ch_merges_after_front_vowel(self, g2p):
        result = g2p.transliterate("mích")
        assert result.count("t") >= 1  # -ch → -t after front vowel in Southern

    def test_coda_nh_preserved_after_back_vowel(self, g2p):
        # After non-front vowels, -nh should still become ŋ in Southern
        # (this is the Southern merger)
        result = g2p.transliterate("anh")
        # a is not a front vowel, but Southern still has the merger
        assert "ŋ" in result


class TestDialectComparison:
    """Compare outputs across dialects."""

    def test_d_onset_varies(self):
        hanoi = HanoiG2P().transliterate("da")
        nghe_an = NgheAnG2P().transliterate("da")
        sai_gon = SaiGonG2P().transliterate("da")

        assert "z" in hanoi      # /z/ in Hanoi
        assert "z" in nghe_an    # /z/ in Nghệ An
        assert "j" in sai_gon    # /j/ in Sài Gòn

    def test_r_onset_varies(self):
        hanoi = HanoiG2P().transliterate("ra")
        nghe_an = NgheAnG2P().transliterate("ra")
        sai_gon = SaiGonG2P().transliterate("ra")

        assert "z" in hanoi      # /z/ in Hanoi
        assert "ʐ" in nghe_an    # /ʐ/ in Nghệ An
        assert "ɹ" in sai_gon    # /ɹ/ in Sài Gòn

    def test_tr_onset_varies(self):
        hanoi = HanoiG2P().transliterate("tra")
        nghe_an = NgheAnG2P().transliterate("tra")
        sai_gon = SaiGonG2P().transliterate("tra")

        assert "tɕ" in hanoi     # /tɕ/ in Hanoi
        assert "ʈ" in nghe_an    # /ʈ/ in Nghệ An
        assert "tɕ" in sai_gon   # /tɕ/ in Sài Gòn

    def test_hoi_tone_varies(self):
        hanoi = HanoiG2P().transliterate("mả")
        nghe_an = NgheAnG2P().transliterate("mả")
        sai_gon = SaiGonG2P().transliterate("mả")

        assert "˧˩˧" in hanoi    # Distinct hỏi in Hanoi
        assert "˧˩˨" in nghe_an  # Merged in Nghệ An
        assert "˨˩˦" in sai_gon  # Merged in Sài Gòn

    def test_nga_tone_varies(self):
        hanoi = HanoiG2P().transliterate("mã")
        nghe_an = NgheAnG2P().transliterate("mã")
        sai_gon = SaiGonG2P().transliterate("mã")

        assert "˧ˀ˥" in hanoi    # Distinct ngã in Hanoi
        assert "˧˩˨" in nghe_an  # Merged with hỏi in Nghệ An
        assert "˨˩˦" in sai_gon  # Merged with hỏi in Sài Gòn


class TestCommonWords:
    """Test common Vietnamese words across dialects."""

    def test_xin_chao(self):
        """Test 'xin chào' (hello)."""
        hanoi = HanoiG2P()
        result = hanoi.transliterate("xin chào")
        assert "s" in result
        assert "tɕ" in result
        assert "˨˩" in result  # huyền tone on chào

    def test_cam_on(self):
        """Test 'cảm ơn' (thank you)."""
        hanoi = HanoiG2P()
        result = hanoi.transliterate("cảm ơn")
        assert "k" in result
        assert "˧˩˧" in result  # hỏi tone on cảm

    def test_viet_nam(self):
        """Test 'Việt Nam'."""
        hanoi = HanoiG2P()
        result = hanoi.transliterate("Việt Nam")
        assert "v" in result
        assert "n" in result


class TestEdgeCases:
    """Test edge cases and special inputs."""

    def test_empty_string(self):
        g2p = HanoiG2P()
        result = g2p.transliterate("")
        assert result == ""

    def test_non_vietnamese_preserved(self):
        g2p = HanoiG2P()
        result = g2p.transliterate("hello ma world")
        assert "hello" in result
        assert "world" in result

    def test_mixed_text(self):
        g2p = HanoiG2P()
        result = g2p.transliterate("Hello Việt Nam!")
        assert "Hello" in result  # "Hello" is preserved (has non-Vietnamese chars)
        assert "!" in result

    def test_numbers_preserved(self):
        g2p = HanoiG2P()
        result = g2p.transliterate("năm 2024")
        assert "2024" in result

    def test_uppercase_handled(self):
        g2p = HanoiG2P()
        result = g2p.transliterate("MA")
        # Should still parse correctly
        assert "m" in result or "M" in result.lower()
