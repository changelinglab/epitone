# epitone

G2P libraries for extracting IPA transcriptions with Chao tone marks from orthographic representations.

All output is in **Unicode NFD** (Normalized Form Decomposed), ensuring consistent handling of combining characters like tone diacritics, nasalization markers, and tie bars.

## Installation

```bash
pip install epitone
```

## Usage

### Thai

```python
from epitone import ThaiG2P

g2p = ThaiG2P()

# Convert Thai text to IPA
ipa = g2p.transliterate("สวัสดี")
print(ipa)  # sow˩˥ʔat˩diː˧

# Get tokenized output
tokens = g2p.transliterate_tokenized("กา")
print(tokens)  # ['k', 'aː', '˧']

# Disable tones
g2p_no_tone = ThaiG2P(include_tones=False)
print(g2p_no_tone.transliterate("กา"))  # kaː
```

### Vietnamese

Three dialect varieties are supported:
- **HanoiG2P** - Northern Vietnamese (Hanoi)
- **NgheAnG2P** - Central Vietnamese (Nghệ An)
- **SaiGonG2P** - Southern Vietnamese (Sài Gòn/Ho Chi Minh City)

```python
from epitone import HanoiG2P, NgheAnG2P, SaiGonG2P

# Northern (Hanoi) dialect
hanoi = HanoiG2P()
print(hanoi.transliterate("xin chào"))  # sin˧ tɕaːw˨˩

# Central (Nghệ An) dialect
nghe_an = NgheAnG2P()
print(nghe_an.transliterate("xin chào"))  # sin˧ tɕaːw˧˩

# Southern (Sài Gòn) dialect
saigon = SaiGonG2P()
print(saigon.transliterate("xin chào"))  # sin˧ tɕaːw˨˩

# Dialect comparison - 'd' onset differs
print(hanoi.transliterate("da"))   # zaː˧ (d→z in North)
print(saigon.transliterate("da"))  # jaː˧ (d→j in South)

# Disable tones
hanoi_no_tone = HanoiG2P(include_tones=False)
print(hanoi_no_tone.transliterate("má"))  # maː
```

#### Key Dialect Differences

| Feature | Hanoi (North) | Nghệ An (Central) | Sài Gòn (South) |
|---------|---------------|-------------------|-----------------|
| d, gi | /z/ | /z/ | /j/ |
| r | /z/ | /ʐ/ (retroflex) | /ɹ/ (approximant) |
| s | /s/ | /ʂ/ (retroflex) | /ʂ/ (retroflex) |
| tr | /tɕ/ (=ch) | /ʈ/ (retroflex) | /tɕ/ (=ch) |
| v | /v/ | /v/ | /j/ |
| hỏi tone | ˧˩˧ (distinct) | ˧˩˨ (merged with ngã) | ˨˩˦ (merged with ngã) |
| ngã tone | ˧ˀ˥ (distinct) | ˧˩˨ (merged with hỏi) | ˨˩˦ (merged with hỏi) |

### Yoruba

```python
from epitone import YorubaG2P

g2p = YorubaG2P()

# Convert Yoruba text to IPA
print(g2p.transliterate("bàbá"))   # ba˨ba˦ (father - low + high tone)
print(g2p.transliterate("ọmọ"))    # ɔ˧mɔ˧ (child)

# Labial-velar consonants use tie bars
print(g2p.transliterate("pupa"))   # k͡pu˧k͡pa˧ (red - 'p' is /k͡p/)
print(g2p.transliterate("gbogbo")) # ɡ͡bo˧ɡ͡bo˧ (all - 'gb' digraph)

# Affricates use tie bars
print(g2p.transliterate("ẹja"))    # ɛ˧d͡ʒa˧ (fish - 'j' is /d͡ʒ/)

# Syllabic nasals with syllabicity marker
print(g2p.transliterate("ń lọ"))   # n̩˦ lɔ˧ (I am going)

# Nasal vowels
print(g2p.transliterate("san"))    # sã˧ (run)

# Get tokenized output
tokens = g2p.transliterate_tokenized("bá")
print(tokens)  # ['b', 'a', '˦']

# Disable tones
g2p_no_tone = YorubaG2P(include_tones=False)
print(g2p_no_tone.transliterate("bàbá"))  # baba
```

### Tone Representation

Tones are represented using Chao tone letters (IPA convention):

#### Thai Tones

| Tone | Chao Letter |
|------|-------------|
| Mid | ˧ |
| Low | ˩ |
| Falling | ˥˩ |
| High | ˦˥ |
| Rising | ˩˥ |

#### Vietnamese Tones (Hanoi)

| Tone | Vietnamese Name | Chao Letter |
|------|-----------------|-------------|
| Level | ngang | ˧ |
| Falling | huyền | ˨˩ |
| Rising | sắc | ˧˥ |
| Dipping | hỏi | ˧˩˧ |
| Creaky rising | ngã | ˧ˀ˥ |
| Heavy | nặng | ˧ˀ˩ |

#### Yoruba Tones

| Tone | Mark | Chao Letter |
|------|------|-------------|
| High | á (acute) | ˦ |
| Mid | a (unmarked) | ˧ |
| Low | à (grave) | ˨ |

### Yoruba Special Features

- **Labial-velar consonants**: 'p' → /k͡p/, 'gb' → /ɡ͡b/ (with tie bar ͡)
- **Affricate**: 'j' → /d͡ʒ/ (with tie bar ͡)
- **Syllabic nasals**: m̩, n̩ with syllabicity marker (̩)
- **Nasal vowels**: Vn → Ṽ (ã, ɛ̃, ĩ, ɔ̃, ũ)
- **Open-mid vowels**: ẹ → /ɛ/, ọ → /ɔ/

## Unicode Normalization

All G2P modules output strings in **Unicode NFD** (Normalized Form Decomposed). This means:

- Composite characters are split into base + combining characters
- `ã` (precomposed) becomes `a` + `̃` (combining tilde)
- Tie bars like `͡` are combining characters following the first character

For comparison with NFD output, use the provided utilities:

```python
from epitone import to_nfd, to_nfc, nfd_equal

# Convert to NFD for comparison
result = g2p.transliterate("san")
assert to_nfd("ã") in result  # Compare using NFD form

# Or use nfd_equal for direct comparison
assert nfd_equal(result, expected_output)
```

## Supported Languages

- **Thai** - Full support for Thai orthography to IPA conversion with tone marks
- **Vietnamese** - Three dialect varieties (Hanoi, Nghệ An, Sài Gòn)
- **Yoruba** - Full support with labial-velars, syllabic nasals, and 3-tone system

### Planned

- Lao
- Mixtec varieties
- Additional West African languages

## License

MIT
