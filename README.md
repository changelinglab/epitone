# epitone

G2P libraries for extracting IPA transcriptions with Chao tone marks from orthographic representations.

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

## Supported Languages

- **Thai** - Full support for Thai orthography to IPA conversion with tone marks
- **Vietnamese** - Three dialect varieties (Hanoi, Nghệ An, Sài Gòn)

### Planned

- Lao
- Mixtec varieties
- West African languages

## License

MIT
