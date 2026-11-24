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

### Tone Representation

Tones are represented using Chao tone letters (IPA convention):

| Tone | Chao Letter |
|------|-------------|
| Mid | ˧ |
| Low | ˩ |
| Falling | ˥˩ |
| High | ˦˥ |
| Rising | ˩˥ |

## Supported Languages

- **Thai** - Full support for Thai orthography to IPA conversion with tone marks

### Planned

- Lao
- Vietnamese
- Mixtec varieties
- West African languages

## License

MIT
