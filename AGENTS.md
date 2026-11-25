# Objective

Build a series of rule-based G2P libraries that covert orthographic representations to IPA representations with tones represented using Chao tone letters (following the IPA convention).

# Requirements

- Each library should have a common interface and share code with the other libraries wherever possible.
- The libraries should should be efficient and algorithmically sound
- The code should be structured in a Python package that can easily be uploaded to PyPI and used by end-users.
- They should have the following methods:
  - `transliterate(text)`: return a string of IPA symbols corresponding 
  - `transliterate_tokenized(text)`: return a string of tokens corresponding to IPA segments

# Scope

The goal is to produce libraries for
- Thai ✓ (implemented)
- Lao
- Vietnamese ✓ (implemented - Hanoi, Nghệ An, Sài Gòn)
- Multiple varieties of Mixtec
- One or more West African languages

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

# Project Structure

```
src/epitone/
├── __init__.py          # Main exports: ThaiG2P, HanoiG2P, NgheAnG2P, SaiGonG2P
├── thai/
│   ├── __init__.py
│   ├── data.py          # Thai consonants, vowels, tone marks
│   ├── syllable.py      # Thai syllable parsing
│   ├── tone.py          # Thai tone determination
│   └── g2p.py           # ThaiG2P class
└── vietnamese/
    ├── __init__.py
    ├── shared.py        # Shared data and VietnameseG2PBase class
    ├── hanoi.py         # HanoiG2P (Northern)
    ├── nghe_an.py       # NgheAnG2P (Central)
    └── sai_gon.py       # SaiGonG2P (Southern)
```

# Development

```bash
# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest tests/ -v
```
