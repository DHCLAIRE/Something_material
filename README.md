# Something_material
Aim: To organize and annotate linguistic materials used in neuroscience experiments. Start with Mandarin materials first.  
Input units: single character, word (character length 2+), phrase, sentence, context.


## Progress Roadmap
Phase 1. Lable material input
 - List out most commonly used or needed linguistic attributes for experimental materials
 - Framework the material template, and the dataset format
 - Allow input of all sizes
 - Get license of the corpus
 
Phase 2. Use criteria to build the desire materials you need
 - Standardize every dataset we're allowed to have (i.e. unified format for all corpora)
 - Add options to let the tool to find suitable materials for users when submit the criteria request

Phase 3. Integrate with AI tools for material generations (pseudowords, texts, sentences, writing style rewrite)
 - TBC (Hopefully)


### Format Demo
Similarly to the format of materials of [The Open Alice EEG Dataset](https://openneuro.org/datasets/ds002322/versions/1.0.4)  
Materials:
| Index | Item | Type | Zhuyin | Pinyin | Tone | Stroke | Homograph Cnts | Homophone Cnts | Freq Char | Freq Word | POS | NOTE |
|-------|------|------|--------|--------|------|--------|----------------|----------------|-----------|-----------|-----|------|
|       |      |      |        |        |      |        |                |                |           |           |     |      |

Corpus:
?




## Useful python tools for conversion between zhuyin & pinyin
1. [pypinyin](https://www.readfog.com/a/1679197351046123520)
2. [pyzhuyin](https://pypi.org/project/pyzhuyin/) >> Now I'm currently using in 'pinyin2bopomofo.py'


## Mandarin surprisal tool

`mandarin_surprisal.py` calculates word-by-word surprisal for Traditional Mandarin materials.
It includes:

- `ngram_semantic_surprisal`: word n-gram surprisal, `-log2 p(word_i | context)`.
- `ngram_syntactic_surprisal`: POS n-gram surprisal, `-log2 p(pos_i | context)`.
- `cfg_semantic_surprisal`: lexicalized PCFG prefix surprisal from bracketed parsed trees.
- `cfg_syntactic_surprisal`: delexicalized POS/structure PCFG prefix surprisal from bracketed parsed trees.

The POS n-gram model follows the 2019 paper's setup at the implementation level:
Witten-Bell-smoothed trigrams over POS tags. The CFG mode induces a PCFG from
parsed trees and uses an incremental beam-pruned prefix parser. Exact replication
of the paper's CFG values still requires the same parsed treebank and EarleyX
configuration used in that work.

### Basic usage

Run n-gram surprisal on the included TextGrid CSV. If no POS column exists, the
offline rule fallback adds coarse POS tags:

```bash
python3 mandarin_surprisal.py ngram \
  --input Materials/story1.TextGrid.csv \
  --parser rule \
  --output Materials/story1.ngram_surprisal.csv
```

Use a separate training token table:

```bash
python3 mandarin_surprisal.py ngram \
  --train path/to/training_tokens.csv \
  --input path/to/target_tokens.csv \
  --word-col word \
  --pos-col pos \
  --sent-col sentence \
  --order 3 \
  --output path/to/target.ngram_surprisal.csv
```

Run CFG surprisal from a Stanford/CKIP/Treebank-style bracketed treebank:

```bash
python3 mandarin_surprisal.py cfg \
  --treebank path/to/parsed_trees.mrg \
  --input path/to/target_tokens.csv \
  --word-col word \
  --pos-col pos \
  --sent-col sentence \
  --output path/to/target.cfg_surprisal.csv
```

Run both n-gram and CFG columns:

```bash
python3 mandarin_surprisal.py all \
  --train path/to/training_tokens.csv \
  --treebank path/to/parsed_trees.mrg \
  --input path/to/target_tokens.csv \
  --output path/to/target.surprisal.csv
```

### Parser and tagger options

The tool can fill missing POS tags or tokenize raw text with:

- `--parser rule`: built-in offline fallback for smoke tests and already segmented materials.
- `--parser ckiptagger`: requires `ckiptagger` and model data; pass `--ckip-data` or set `CKIPTAGGER_DATA`.
- `--parser ckipnlp`: requires `ckipnlp`.
- `--parser articut`: requires `ArticutAPI`, `ARTICUT_USERNAME`, and `ARTICUT_API_KEY`.
- `--parser stanford`: requires a running Stanford CoreNLP server; pass `--stanford-url` or set `STANFORD_CORENLP_URL`.

For research estimates, prefer a real Mandarin segmenter/POS tagger and keep the
same token/POS standard across training, treebank induction, and target stimuli.
