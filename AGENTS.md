# Objective

Build a series of rule-based G2P libraries that covert orthographic representations to IPA representations with tones represented using Chao tone letters (following the IPA convention).

# Requirements

- Each library should have a common interface and share code with the other libraries wherever possible.
- The libraries should should be efficient and algorithmically sound
- The code should be structured in a Python package that can easily be uploaded to PyPI and used by end-users.
- **All output must be in Unicode NFD** (Normalized Form Decomposed) for consistent handling of combining characters
- They should have the following methods:
  - `transliterate(text)`: return a string of IPA symbols in NFD form
  - `transliterate_tokenized(text)`: return a list of IPA tokens in NFD form

# Scope

The goal is to produce libraries for
- Thai ✓ (implemented)
- Lao
- Vietnamese ✓ (implemented - Hanoi, Nghệ An, Sài Gòn)
- Hmong ✓ (implemented - Hmong Daw, Mong Leng via RPA; Dananshan)
- Multiple varieties of Mixtec
- One or more West African languages
  - Yoruba ✓ (implemented)

## Thai

- A through description of the Thai orthography is found [here](https://en.wikipedia.org/wiki/Thai_script). The agent should digest this resource carefully, especially the [decision tree](https://en.wikipedia.org/wiki/File:Thai-tones-flowchart.svg) that provides the logic for determining the tone.
- The Thai tones should be represented as:
  - ˧ (mid)
  - ˩˥ (rising)
  - ˥˩ (falling)
  - ˦˥ (high)
  - ˩ (low)
- Procedure, traverse the text:
  - For each syllable, extract the
	- consonant (IPA)
	- consonant class (special token)
	- vowel (IPA)
	- vowel length
	- tone mark (special token)
	- coda consonant
   - Based on this 6-tuple, construct an IPA sequence of the form <consonat><vowel><length><tone> and add it to the output.

## Vietnamese

- Reference: [Vietnamese alphabet (Wikipedia)](https://en.wikipedia.org/wiki/Vietnamese_alphabet)
- Three dialect varieties implemented:
  - **Hanoi (Northern)**: d/gi/r → /z/, tr → /tɕ/, distinct hỏi/ngã tones
  - **Nghệ An (Central)**: r → /ʐ/, s → /ʂ/, tr → /ʈ/, hỏi/ngã merge
  - **Sài Gòn (Southern)**: d/gi/v → /j/, r → /ɹ/, hỏi/ngã merge, coda mergers

- Procedure, traverse the text:
  - For each syllable, extract the
    - onset consonant (IPA)
    - vowel/nucleus (monophthong, diphthong, or triphthong)
    - tone marker
    - coda consonant
  - Apply dialect-specific rules to map from this 4-tuple to an IPA syllable
  - Use Chao tone letters as specified in the Wikipedia article

- Tone representation (Hanoi):
  - ˧ (ngang - level)
  - ˨˩ (huyền - falling)
  - ˧˥ (sắc - rising)
  - ˧˩˧ (hỏi - dipping)
  - ˧ˀ˥ (ngã - creaky rising)
  - ˧ˀ˩ (nặng - heavy)

## Yoruba

- Reference: [Yoruba alphabet (Wikipedia)](https://en.wikipedia.org/wiki/Yoruba_alphabet)
- Based on Latin alphabet with 7 oral vowels and 3 tones

- Key phonological features:
  - Labial-velar consonants with tie bars: 'p' → /k͡p/, 'gb' → /ɡ͡b/
  - Affricate: 'j' → /d͡ʒ/ (with tie bar)
  - Syllabic nasals: m̩, n̩ carrying tone (marked with ̩ U+0329)
  - Nasal vowels: Vn → Ṽ when n is word-final or before consonant
  - Open-mid vowels: ẹ → /ɛ/, ọ → /ɔ/

- Tone representation:
  - ˦ (high - acute accent: á)
  - ˧ (mid - unmarked: a)
  - ˨ (low - grave accent: à)

- Syllable structure: Strict (C)V - no codas except nasals creating nasal vowels

## Hmong

- Reference: [Hmong language (Wikipedia)](https://en.wikipedia.org/wiki/Hmong_language)
- Two orthography systems supported:
  - **RPA (Romanized Popular Alphabet)**: For Hmong Daw (White Hmong) and Mong Leng (Green/Blue Hmong)
  - **Dananshan**: Pinyin-based system used in China

### RPA Orthography

- Tone indicated by final consonant letter (b, j, v, s, g, m, d) or absence
- Doubled vowels (ee, oo, aa) represent nasalized vowels
- The -g tone marks breathy phonation on the vowel (marked with ̤ U+0324)
- Segmental IPA uses standard characters (no superscripts):
  - Prenasalized consonants: /mp/, /nt/, /ŋk/ (not /ᵐp/, /ⁿt/, /ᵑk/)
  - Lateral clusters: /pl/, /tl/ (not /pˡ/, /tˡ/)

- Tone representation differs between dialects:

| Letter | Hmong Daw | Mong Leng | Description |
|--------|-----------|-----------|-------------|
| -b | ˥ (55) | ˥˧ (53) | High |
| -j | ˥˨ (52) | ˥˨ (52) | High falling |
| -v | ˨˦ (24) | ˨˦ (24) | Mid rising |
| -s | ˨˩ (21) | ˨˩ (21) | Low |
| -g | ˨ (22) | ˧ (33) | Breathy |
| -m | ˩ (11) | ˩ (11) | Low falling |
| -d | ˩˧ (13) | ˩˧ (13) | Low rising |
| (none) | ˧ (33) | ˧˥ (35) | Mid / Mid rising |

### Dananshan Orthography

- Pinyin-based system with numeric tone markers (1-8)
- Different consonant-to-IPA mappings than RPA (e.g., b → /p/, p → /pʰ/)

- Tone representation:
  - 1: ˦˦ (44) high level
  - 2: ˧˩ (31) mid falling
  - 3: ˦˧ (43) high-mid falling
  - 4: ˥˧˥ (535) contour
  - 5: ˧˧ (33) mid level
  - 6: ˨˦ (24) low rising
  - 7: ˧˥ (35) mid rising
  - 8: ˩˧ (13) low-mid rising

# Project Structure

```
src/epitone/
├── __init__.py          # Main exports: ThaiG2P, Vietnamese*, Yoruba, Hmong*
├── unicode_utils.py     # NFD/NFC normalization utilities (to_nfd, to_nfc, nfd_equal)
├── thai/
│   ├── __init__.py
│   ├── data.py          # Thai consonants, vowels, tone marks
│   ├── syllable.py      # Thai syllable parsing
│   ├── tone.py          # Thai tone determination
│   └── g2p.py           # ThaiG2P class
├── vietnamese/
│   ├── __init__.py
│   ├── shared.py        # Shared data and VietnameseG2PBase class
│   ├── hanoi.py         # HanoiG2P (Northern)
│   ├── nghe_an.py       # NgheAnG2P (Central)
│   └── sai_gon.py       # SaiGonG2P (Southern)
├── yoruba/
│   ├── __init__.py
│   ├── data.py          # Yoruba consonants, vowels, tones
│   └── g2p.py           # YorubaG2P class with syllable parsing
└── hmong/
    ├── __init__.py
    ├── data.py          # Hmong consonants, vowels, tones for RPA and Dananshan
    ├── rpa.py           # HmongDawG2P and MongLengG2P (RPA orthography)
    └── dananshan.py     # DananshanG2P (Pinyin-based orthography)
```

# Development

```bash
# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest tests/ -v
```
