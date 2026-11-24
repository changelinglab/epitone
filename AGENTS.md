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
- Thai
- Lao
- Vietnamese
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
