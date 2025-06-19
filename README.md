# Something_material
Aim: To organize and annotate linguistic materials used in neuroscience experiments. Start with Mandarin materials first.  
Input units: single character, word (character length 2+), phrase, sentence, context.


## Progress Roadmap
Phase 1. Lable material input
 - List out most commonly used or needed linguistic attributes for experimental materials
 - Framework the material template, and the dataset format
 - Allow input of all sizes
 - Get license of the corpus
 
Phase 2.
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
