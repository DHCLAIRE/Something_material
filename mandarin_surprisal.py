#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""N-gram and PCFG surprisal utilities for Traditional Mandarin.

The POS n-gram model follows the broad setup used in the 2019 Mandarin
surprisal paper: word-by-word POS surprisal in bits, estimated with a
Witten-Bell-smoothed trigram. The CFG path expects a parsed treebank, estimates
a PCFG from bracketed trees, and uses an incremental prefix parser to produce
left-to-right surprisal estimates. Exact reproduction of the paper's CFG
numbers still requires the same parsed corpus and EarleyX settings.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
import sys
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Iterator, List, Mapping, Optional, Sequence, Tuple


START = "<s>"
END = "</s>"
UNK = "<UNK>"
PUNCT_RE = re.compile(r"^[\s，。！？、；：,.!?;:\"'「」『』（）()《》〈〉\[\]【】…—-]+$")
HAN_RE = re.compile(r"[\u3400-\u9fff]+")


@dataclass
class Token:
    word: str
    pos: str = ""
    sent_id: str = "0"
    onset: str = ""
    offset: str = ""


def bits(probability: float) -> float:
    if probability <= 0.0:
        return float("inf")
    return -math.log2(probability)


def clean_word(value: str) -> str:
    value = (value or "").strip()
    if len(value) >= 2 and value[0] == value[-1] == '"':
        value = value[1:-1]
    return value.strip()


def is_skip_label(value: str) -> bool:
    word = clean_word(value)
    return (
        not word
        or word.upper() in {"SIL", "SILPAUSE", "SP", "PAUSE"}
        or word in {"\\", "\\n", "n"}
    )


def open_text(path: str) -> str:
    return Path(path).read_text(encoding="utf-8-sig")


def sniff_dialect(sample: str) -> csv.Dialect:
    try:
        return csv.Sniffer().sniff(sample[:4096], delimiters=",\t;")
    except csv.Error:
        class Fallback(csv.excel):
            delimiter = "\t" if "\t" in sample[:4096] else ","

        return Fallback


def read_token_table(
    path: str,
    word_col: str = "word",
    pos_col: str = "pos",
    sent_col: str = "sentence",
    onset_col: str = "Start",
    offset_col: str = "End",
    tier_col: str = "TierName",
    tier_value: str = "Word",
) -> List[Token]:
    text = open_text(path)
    lines = [line for line in text.splitlines() if line.strip() and not line.lstrip().startswith("#")]
    text = "\n".join(lines)
    dialect = sniff_dialect(text)
    rows = list(csv.DictReader(text.splitlines(), dialect=dialect))
    if not rows:
        return []

    fieldnames = rows[0].keys()
    actual_word_col = word_col if word_col in fieldnames else None
    if actual_word_col is None:
        for candidate in ("Label", "Word", "token", "Item", "word"):
            if candidate in fieldnames:
                actual_word_col = candidate
                break
    if actual_word_col is None:
        raise ValueError(f"Could not find a word column in {path}. Use --word-col.")

    actual_pos_col = pos_col if pos_col in fieldnames else ""
    actual_sent_col = sent_col if sent_col in fieldnames else ""
    actual_onset_col = onset_col if onset_col in fieldnames else ""
    actual_offset_col = offset_col if offset_col in fieldnames else ""

    tokens: List[Token] = []
    current_sent = 0
    for row in rows:
        if tier_col in row and tier_value:
            tier = row.get(tier_col, "").replace('"', "").strip()
            if tier and tier != tier_value:
                continue
        word = clean_word(row.get(actual_word_col, ""))
        if is_skip_label(word):
            current_sent += 1
            continue
        if PUNCT_RE.match(word):
            current_sent += 1
            continue
        sent_id = row.get(actual_sent_col, "") if actual_sent_col else str(current_sent)
        tokens.append(
            Token(
                word=word,
                pos=row.get(actual_pos_col, "") if actual_pos_col else "",
                sent_id=sent_id or str(current_sent),
                onset=row.get(actual_onset_col, "") if actual_onset_col else "",
                offset=row.get(actual_offset_col, "") if actual_offset_col else "",
            )
        )
    return tokens


def read_plain_text(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def group_sentences(tokens: Sequence[Token]) -> List[List[Token]]:
    grouped: Dict[str, List[Token]] = defaultdict(list)
    order: List[str] = []
    for token in tokens:
        if token.sent_id not in grouped:
            order.append(token.sent_id)
        grouped[token.sent_id].append(token)
    return [grouped[key] for key in order if grouped[key]]


class TaggerAdapter:
    name = "base"

    def tag(self, text: str) -> List[List[Token]]:
        raise NotImplementedError


class RuleBasedMandarinAdapter(TaggerAdapter):
    """Small offline fallback for smoke tests and pre-tokenized material.

    This is not a research-grade segmenter. Use CKIP, Stanford CoreNLP, or
    Articut for real estimates.
    """

    name = "rule"

    function_words = {
        "的": "DE",
        "了": "AS",
        "著": "AS",
        "過": "AS",
        "在": "P",
        "把": "P",
        "被": "P",
        "和": "C",
        "與": "C",
        "及": "C",
        "或": "C",
        "也": "ADV",
        "都": "ADV",
        "很": "ADV",
        "不": "NEG",
        "沒": "NEG",
        "沒有": "NEG",
        "是": "V",
        "有": "V",
        "會": "V",
        "能": "V",
        "要": "V",
        "我": "N",
        "你": "N",
        "他": "N",
        "她": "N",
        "它": "N",
        "們": "N",
        "這": "DET",
        "那": "DET",
        "什麼": "N",
        "誰": "N",
        "嗎": "PART",
        "呢": "PART",
        "吧": "PART",
        "啊": "PART",
    }

    def tag_words(self, words: Sequence[str], sent_id: str = "0") -> List[Token]:
        tagged: List[Token] = []
        for word in words:
            pos = self.function_words.get(word)
            if pos is None and re.fullmatch(r"\d+(\.\d+)?", word):
                pos = "NUM"
            elif pos is None and PUNCT_RE.match(word):
                pos = "PU"
            elif pos is None:
                pos = "N" if len(word) <= 2 else "V"
            tagged.append(Token(word=word, pos=pos, sent_id=sent_id))
        return tagged

    def tag(self, text: str) -> List[List[Token]]:
        sentences: List[List[Token]] = []
        sent_id = 0
        for segment in re.split(r"([。！？!?;\n]+)", text):
            words = [match.group(0) for match in re.finditer(r"[\u3400-\u9fff]+|[A-Za-z0-9.]+", segment)]
            if words:
                sentences.append(self.tag_words(words, str(sent_id)))
                sent_id += 1
        return sentences


class CKIPTaggerAdapter(TaggerAdapter):
    name = "ckiptagger"

    def __init__(self, data_dir: Optional[str] = None):
        try:
            from ckiptagger import POS, WS
        except ImportError as exc:
            raise RuntimeError("Install ckiptagger and download CKIP model data to use --parser ckiptagger.") from exc
        data_dir = data_dir or os.environ.get("CKIPTAGGER_DATA")
        if not data_dir:
            raise RuntimeError("Set CKIPTAGGER_DATA or pass --ckip-data for ckiptagger.")
        self.ws = WS(data_dir)
        self.pos = POS(data_dir)

    def tag(self, text: str) -> List[List[Token]]:
        raw_sentences = [s.strip() for s in re.split(r"[。！？!?\n]+", text) if s.strip()]
        word_sentences = self.ws(raw_sentences)
        pos_sentences = self.pos(word_sentences)
        return [
            [Token(word=w, pos=p, sent_id=str(i)) for w, p in zip(words, poses) if not is_skip_label(w)]
            for i, (words, poses) in enumerate(zip(word_sentences, pos_sentences))
        ]


class CKIPNLPAdapter(TaggerAdapter):
    name = "ckipnlp"

    def __init__(self):
        try:
            from ckipnlp.pipeline import CkipPipeline
        except ImportError as exc:
            raise RuntimeError(
                "Install ckipnlp. If its API has changed, export pre-tokenized word/POS CSV and use that as input."
            ) from exc
        self.pipeline = CkipPipeline()

    def tag(self, text: str) -> List[List[Token]]:
        doc = self.pipeline(text)
        sentences: List[List[Token]] = []
        for i, sentence in enumerate(getattr(doc, "sentences", [])):
            sent_tokens = []
            for word in getattr(sentence, "words", []):
                sent_tokens.append(Token(word=str(getattr(word, "text", word)), pos=str(getattr(word, "pos", "")), sent_id=str(i)))
            if sent_tokens:
                sentences.append(sent_tokens)
        if not sentences:
            raise RuntimeError("ckipnlp returned no sentence tokens; check the installed ckipnlp API version.")
        return sentences


class ArticutAdapter(TaggerAdapter):
    name = "articut"

    def __init__(self):
        try:
            from ArticutAPI import Articut
        except ImportError as exc:
            raise RuntimeError("Install ArticutAPI to use --parser articut.") from exc
        username = os.environ.get("ARTICUT_USERNAME")
        api_key = os.environ.get("ARTICUT_API_KEY")
        if not username or not api_key:
            raise RuntimeError("Set ARTICUT_USERNAME and ARTICUT_API_KEY to use Articut.")
        self.articut = Articut(username=username, apikey=api_key)

    def tag(self, text: str) -> List[List[Token]]:
        result = self.articut.parse(text)
        pos = result.get("result_pos", "")
        sentences: List[List[Token]] = []
        sent_tokens: List[Token] = []
        for tag, word in re.findall(r"<([^>]+)>([^<]+)</[^>]+>", pos):
            if PUNCT_RE.match(word):
                if sent_tokens:
                    sentences.append(sent_tokens)
                    sent_tokens = []
                continue
            sent_tokens.append(Token(word=word, pos=tag, sent_id=str(len(sentences))))
        if sent_tokens:
            sentences.append(sent_tokens)
        return sentences


class StanfordCoreNLPAdapter(TaggerAdapter):
    name = "stanford"

    def __init__(self, url: Optional[str] = None):
        self.url = (url or os.environ.get("STANFORD_CORENLP_URL") or "http://localhost:9000").rstrip("/")

    def tag(self, text: str) -> List[List[Token]]:
        props = {
            "annotators": "tokenize,ssplit,pos",
            "outputFormat": "json",
            "tokenize.language": "zh",
            "pos.model": "edu/stanford/nlp/models/pos-tagger/chinese-distsim/chinese-distsim.tagger",
        }
        query = urllib.parse.urlencode({"properties": json.dumps(props)})
        request = urllib.request.Request(
            f"{self.url}/?{query}",
            data=text.encode("utf-8"),
            headers={"Content-Type": "text/plain; charset=utf-8"},
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                doc = json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            raise RuntimeError(f"Could not reach Stanford CoreNLP server at {self.url}.") from exc
        sentences: List[List[Token]] = []
        for i, sentence in enumerate(doc.get("sentences", [])):
            sent_tokens = [
                Token(word=t.get("word", ""), pos=t.get("pos", ""), sent_id=str(i))
                for t in sentence.get("tokens", [])
                if not is_skip_label(t.get("word", ""))
            ]
            if sent_tokens:
                sentences.append(sent_tokens)
        return sentences


def make_adapter(name: str, ckip_data: Optional[str] = None, stanford_url: Optional[str] = None) -> TaggerAdapter:
    if name == "rule":
        return RuleBasedMandarinAdapter()
    if name == "ckiptagger":
        return CKIPTaggerAdapter(ckip_data)
    if name == "ckipnlp":
        return CKIPNLPAdapter()
    if name == "articut":
        return ArticutAdapter()
    if name == "stanford":
        return StanfordCoreNLPAdapter(stanford_url)
    raise ValueError(f"Unknown parser/tagger: {name}")


class WittenBellNgram:
    def __init__(self, order: int = 3, min_count: int = 1):
        if order < 1:
            raise ValueError("order must be >= 1")
        self.order = order
        self.min_count = min_count
        self.vocab: set[str] = set()
        self.counts: List[Dict[Tuple[str, ...], Counter[str]]] = [defaultdict(Counter) for _ in range(order + 1)]

    def _map(self, token: str) -> str:
        return token if token in self.vocab else UNK

    def fit(self, sequences: Sequence[Sequence[str]]) -> "WittenBellNgram":
        raw = Counter(token for seq in sequences for token in seq)
        self.vocab = {token for token, count in raw.items() if count >= self.min_count}
        self.vocab.add(UNK)
        for seq in sequences:
            mapped = [self._map(token) for token in seq] + [END]
            padded = [START] * (self.order - 1) + mapped
            for i in range(self.order - 1, len(padded)):
                token = padded[i]
                for n in range(1, self.order + 1):
                    context = tuple(padded[max(0, i - n + 1) : i])
                    self.counts[n][context][token] += 1
        return self

    def probability(self, token: str, context: Sequence[str], order: Optional[int] = None) -> float:
        order = order or self.order
        mapped = self._map(token)
        if order <= 1:
            counter = self.counts[1].get((), Counter())
            total = sum(counter.values())
            types = len(counter)
            denom = total + max(types, 1)
            if counter.get(mapped, 0) > 0:
                return counter[mapped] / denom
            unseen_types = max(len(self.vocab) - types, 1)
            return max(types, 1) / denom / unseen_types

        ctx = tuple(self._map(t) if t != START else START for t in context[-(order - 1) :])
        counter = self.counts[order].get(ctx)
        if not counter:
            return self.probability(mapped, ctx, order - 1)
        total = sum(counter.values())
        types = len(counter)
        denom = total + types
        seen = counter.get(mapped, 0)
        if seen:
            return seen / denom
        return (types / denom) * self.probability(mapped, ctx[1:], order - 1)

    def sequence_surprisals(self, sequence: Sequence[str]) -> List[Tuple[float, float]]:
        context = [START] * (self.order - 1)
        results = []
        for token in sequence:
            prob = self.probability(token, context)
            results.append((prob, bits(prob)))
            context.append(token if token in self.vocab else UNK)
        return results


Tree = Tuple[str, List[object]]


def tokenize_tree(text: str) -> List[str]:
    return re.findall(r"\(|\)|[^\s()]+", text)


def parse_tree_tokens(tokens: Sequence[str], index: int = 0) -> Tuple[Tree, int]:
    if tokens[index] != "(":
        raise ValueError("Tree must start with '('")
    label = tokens[index + 1]
    children: List[object] = []
    index += 2
    while index < len(tokens) and tokens[index] != ")":
        if tokens[index] == "(":
            child, index = parse_tree_tokens(tokens, index)
            children.append(child)
        else:
            children.append(tokens[index])
            index += 1
    if index >= len(tokens):
        raise ValueError("Unbalanced tree")
    return (label, children), index + 1


def read_bracketed_trees(path: str) -> List[Tree]:
    text = open_text(path)
    trees: List[Tree] = []
    buffer: List[str] = []
    balance = 0
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        buffer.append(stripped)
        balance += stripped.count("(") - stripped.count(")")
        if balance == 0 and buffer:
            tree, index = parse_tree_tokens(tokenize_tree(" ".join(buffer)))
            if index:
                trees.append(tree)
            buffer = []
    if buffer:
        raise ValueError(f"Unbalanced final tree in {path}")
    return trees


def is_tree(value: object) -> bool:
    return isinstance(value, tuple) and len(value) == 2 and isinstance(value[1], list)


def is_preterminal(tree: Tree) -> bool:
    return bool(tree[1]) and all(not is_tree(child) for child in tree[1])


class PCFG:
    def __init__(self, start_symbol: str, rules: Mapping[str, Mapping[Tuple[str, ...], float]]):
        self.start_symbol = start_symbol
        self.rules = {lhs: dict(rhs_probs) for lhs, rhs_probs in rules.items()}
        self.nonterminals = set(self.rules)
        self.terminals = {
            symbol
            for rhs_probs in self.rules.values()
            for rhs in rhs_probs
            for symbol in rhs
            if symbol not in self.nonterminals
        }
        self.unigram = Counter()
        for rhs_probs in self.rules.values():
            for rhs, prob in rhs_probs.items():
                for symbol in rhs:
                    if symbol not in self.nonterminals:
                        self.unigram[symbol] += prob

    @classmethod
    def from_trees(cls, trees: Sequence[Tree], mode: str = "syntactic") -> "PCFG":
        if mode not in {"syntactic", "semantic"}:
            raise ValueError("mode must be syntactic or semantic")
        counts: Dict[str, Counter[Tuple[str, ...]]] = defaultdict(Counter)
        start_symbol = trees[0][0]

        def add(tree: Tree) -> str:
            label, children = tree
            if mode == "syntactic" and is_preterminal(tree):
                return label
            rhs: List[str] = []
            for child in children:
                if is_tree(child):
                    if mode == "syntactic" and is_preterminal(child):
                        rhs.append(child[0])
                    else:
                        rhs.append(child[0])
                        add(child)
                else:
                    rhs.append(str(child))
            if rhs:
                counts[label][tuple(rhs)] += 1
            return label

        for tree in trees:
            add(tree)

        rules = {
            lhs: {rhs: count / sum(counter.values()) for rhs, count in counter.items()}
            for lhs, counter in counts.items()
        }
        return cls(start_symbol, rules)

    def save_json(self, path: str) -> None:
        data = {
            "start_symbol": self.start_symbol,
            "rules": {
                lhs: [{"rhs": list(rhs), "prob": prob} for rhs, prob in rhs_probs.items()]
                for lhs, rhs_probs in self.rules.items()
            },
        }
        Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


class IncrementalPCFGParser:
    """Beam-pruned top-down prefix parser for PCFG surprisal estimates."""

    def __init__(self, grammar: PCFG, beam: int = 5000, min_probability: float = 1e-12, max_expansions: int = 100000):
        self.grammar = grammar
        self.beam = beam
        self.min_probability = min_probability
        self.max_expansions = max_expansions
        self.reset()

    def reset(self) -> None:
        self.states: Dict[Tuple[str, ...], float] = {(self.grammar.start_symbol,): 1.0}
        self.states = self._closure(self.states)

    def _prune(self, states: Dict[Tuple[str, ...], float]) -> Dict[Tuple[str, ...], float]:
        if not states:
            return {}
        total = sum(states.values()) or 1.0
        normalized = {stack: prob / total for stack, prob in states.items() if prob / total >= self.min_probability}
        if len(normalized) > self.beam:
            normalized = dict(sorted(normalized.items(), key=lambda item: item[1], reverse=True)[: self.beam])
            total = sum(normalized.values()) or 1.0
            normalized = {stack: prob / total for stack, prob in normalized.items()}
        return normalized

    def _closure(self, states: Mapping[Tuple[str, ...], float]) -> Dict[Tuple[str, ...], float]:
        agenda = list(states.items())
        closed: Dict[Tuple[str, ...], float] = defaultdict(float)
        expansions = 0
        while agenda and expansions < self.max_expansions:
            stack, prob = agenda.pop()
            if prob < self.min_probability:
                continue
            if not stack:
                closed[stack] += prob
                continue
            top = stack[0]
            if top not in self.grammar.nonterminals:
                closed[stack] += prob
                continue
            for rhs, rule_prob in self.grammar.rules.get(top, {}).items():
                new_stack = tuple(rhs) + stack[1:]
                new_prob = prob * rule_prob
                if new_prob >= self.min_probability:
                    agenda.append((new_stack, new_prob))
            expansions += 1
        return self._prune(dict(closed))

    def next_distribution(self) -> Dict[str, float]:
        distribution: Dict[str, float] = defaultdict(float)
        for stack, prob in self.states.items():
            if stack:
                top = stack[0]
                if top not in self.grammar.nonterminals:
                    distribution[top] += prob
        total = sum(distribution.values())
        if total <= 0:
            total = sum(self.grammar.unigram.values()) or 1.0
            return {token: count / total for token, count in self.grammar.unigram.items()}
        return {token: prob / total for token, prob in distribution.items()}

    def scan(self, token: str) -> float:
        distribution = self.next_distribution()
        fallback = 1.0 / max(len(self.grammar.terminals), 1)
        probability = distribution.get(token, 0.0)
        if probability <= 0.0:
            probability = fallback * 1e-6
        next_states: Dict[Tuple[str, ...], float] = defaultdict(float)
        for stack, prob in self.states.items():
            if stack and stack[0] == token:
                next_states[stack[1:]] += prob
        if not next_states:
            next_states[(self.grammar.start_symbol,)] = self.min_probability
        self.states = self._closure(next_states)
        return probability

    def sequence_surprisals(self, sequence: Sequence[str]) -> List[Tuple[float, float]]:
        self.reset()
        results = []
        for token in sequence:
            prob = self.scan(token)
            results.append((prob, bits(prob)))
        return results


def sequence_values(sentences: Sequence[Sequence[Token]], attr: str) -> List[List[str]]:
    return [[getattr(token, attr) for token in sentence if getattr(token, attr)] for sentence in sentences]


def ensure_pos(sentences: List[List[Token]], parser_name: str, ckip_data: Optional[str], stanford_url: Optional[str]) -> List[List[Token]]:
    if all(token.pos for sentence in sentences for token in sentence):
        return sentences
    adapter = make_adapter(parser_name, ckip_data=ckip_data, stanford_url=stanford_url)
    if isinstance(adapter, RuleBasedMandarinAdapter):
        for sentence in sentences:
            tagged = adapter.tag_words([token.word for token in sentence], sentence[0].sent_id if sentence else "0")
            for token, tagged_token in zip(sentence, tagged):
                token.pos = tagged_token.pos
        return sentences
    text = "\n".join("".join(token.word for token in sentence) for sentence in sentences)
    return adapter.tag(text)


def write_tagged(sentences: Sequence[Sequence[Token]], path: Optional[str]) -> None:
    fieldnames = ["sentence", "word", "pos", "onset", "offset"]
    handle = open(path, "w", encoding="utf-8", newline="") if path else sys.stdout
    try:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for i, sentence in enumerate(sentences):
            for token in sentence:
                writer.writerow(
                    {
                        "sentence": token.sent_id or str(i),
                        "word": token.word,
                        "pos": token.pos,
                        "onset": token.onset,
                        "offset": token.offset,
                    }
                )
    finally:
        if path:
            handle.close()


def read_input_sentences(args: argparse.Namespace, require_table: bool = False) -> List[List[Token]]:
    if args.input_text:
        adapter = make_adapter(args.parser, ckip_data=args.ckip_data, stanford_url=args.stanford_url)
        return adapter.tag(args.input_text)
    if args.input and args.input.endswith((".txt", ".text")) and not require_table:
        adapter = make_adapter(args.parser, ckip_data=args.ckip_data, stanford_url=args.stanford_url)
        return adapter.tag(read_plain_text(args.input))
    if not args.input:
        raise ValueError("Provide --input or --input-text.")
    tokens = read_token_table(
        args.input,
        word_col=args.word_col,
        pos_col=args.pos_col,
        sent_col=args.sent_col,
        tier_col=args.tier_col,
        tier_value=args.tier_value,
    )
    return group_sentences(tokens)


def run_tag(args: argparse.Namespace) -> None:
    sentences = read_input_sentences(args)
    sentences = ensure_pos(sentences, args.parser, args.ckip_data, args.stanford_url)
    write_tagged(sentences, args.output)


def train_ngram_from_path(args: argparse.Namespace, attr: str) -> WittenBellNgram:
    train_path = args.train or args.input
    train_tokens = read_token_table(
        train_path,
        word_col=args.word_col,
        pos_col=args.pos_col,
        sent_col=args.sent_col,
        tier_col=args.tier_col,
        tier_value=args.tier_value,
    )
    train_sentences = group_sentences(train_tokens)
    if attr == "pos":
        train_sentences = ensure_pos(train_sentences, args.parser, args.ckip_data, args.stanford_url)
    sequences = sequence_values(train_sentences, attr)
    return WittenBellNgram(order=args.order, min_count=args.min_count).fit(sequences)


def run_ngram(args: argparse.Namespace) -> None:
    sentences = read_input_sentences(args, require_table=True)
    sentences = ensure_pos(sentences, args.parser, args.ckip_data, args.stanford_url)
    word_model = train_ngram_from_path(args, "word")
    pos_model = train_ngram_from_path(args, "pos")
    rows = []
    for sentence in sentences:
        word_scores = word_model.sequence_surprisals([token.word for token in sentence])
        pos_scores = pos_model.sequence_surprisals([token.pos for token in sentence])
        for token, (word_prob, word_bits), (pos_prob, pos_bits) in zip(sentence, word_scores, pos_scores):
            rows.append(
                {
                    "sentence": token.sent_id,
                    "word": token.word,
                    "pos": token.pos,
                    "ngram_semantic_prob": word_prob,
                    "ngram_semantic_surprisal": word_bits,
                    "ngram_syntactic_prob": pos_prob,
                    "ngram_syntactic_surprisal": pos_bits,
                }
            )
    write_rows(rows, args.output)


def write_rows(rows: Sequence[Mapping[str, object]], path: Optional[str]) -> None:
    if not rows:
        return
    handle = open(path, "w", encoding="utf-8", newline="") if path else sys.stdout
    try:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    finally:
        if path:
            handle.close()


def run_cfg(args: argparse.Namespace) -> None:
    if not args.treebank:
        raise ValueError("CFG surprisal requires --treebank with bracketed parsed sentences.")
    sentences = read_input_sentences(args, require_table=True)
    sentences = ensure_pos(sentences, args.parser, args.ckip_data, args.stanford_url)
    trees = read_bracketed_trees(args.treebank)
    syntactic_grammar = PCFG.from_trees(trees, mode="syntactic")
    semantic_grammar = PCFG.from_trees(trees, mode="semantic")
    rows = []
    for sentence in sentences:
        syntactic_parser = IncrementalPCFGParser(syntactic_grammar, beam=args.beam)
        semantic_parser = IncrementalPCFGParser(semantic_grammar, beam=args.beam)
        syntactic_scores = syntactic_parser.sequence_surprisals([token.pos for token in sentence])
        semantic_scores = semantic_parser.sequence_surprisals([token.word for token in sentence])
        for token, (syn_prob, syn_bits), (sem_prob, sem_bits) in zip(sentence, syntactic_scores, semantic_scores):
            rows.append(
                {
                    "sentence": token.sent_id,
                    "word": token.word,
                    "pos": token.pos,
                    "cfg_semantic_prob": sem_prob,
                    "cfg_semantic_surprisal": sem_bits,
                    "cfg_syntactic_prob": syn_prob,
                    "cfg_syntactic_surprisal": syn_bits,
                }
            )
    write_rows(rows, args.output)
    if args.save_grammar:
        syntactic_grammar.save_json(args.save_grammar.replace(".json", ".syntactic.json"))
        semantic_grammar.save_json(args.save_grammar.replace(".json", ".semantic.json"))


def run_all(args: argparse.Namespace) -> None:
    sentences = read_input_sentences(args, require_table=True)
    sentences = ensure_pos(sentences, args.parser, args.ckip_data, args.stanford_url)
    word_model = train_ngram_from_path(args, "word")
    pos_model = train_ngram_from_path(args, "pos")
    syntactic_grammar = semantic_grammar = None
    if args.treebank:
        trees = read_bracketed_trees(args.treebank)
        syntactic_grammar = PCFG.from_trees(trees, mode="syntactic")
        semantic_grammar = PCFG.from_trees(trees, mode="semantic")

    rows = []
    for sentence in sentences:
        word_scores = word_model.sequence_surprisals([token.word for token in sentence])
        pos_scores = pos_model.sequence_surprisals([token.pos for token in sentence])
        cfg_syn_scores = [(None, None)] * len(sentence)
        cfg_sem_scores = [(None, None)] * len(sentence)
        if syntactic_grammar and semantic_grammar:
            cfg_syn_scores = IncrementalPCFGParser(syntactic_grammar, beam=args.beam).sequence_surprisals(
                [token.pos for token in sentence]
            )
            cfg_sem_scores = IncrementalPCFGParser(semantic_grammar, beam=args.beam).sequence_surprisals(
                [token.word for token in sentence]
            )
        for token, nsem, nsyn, csem, csyn in zip(sentence, word_scores, pos_scores, cfg_sem_scores, cfg_syn_scores):
            rows.append(
                {
                    "sentence": token.sent_id,
                    "word": token.word,
                    "pos": token.pos,
                    "ngram_semantic_surprisal": nsem[1],
                    "ngram_syntactic_surprisal": nsyn[1],
                    "cfg_semantic_surprisal": csem[1],
                    "cfg_syntactic_surprisal": csyn[1],
                }
            )
    write_rows(rows, args.output)


def add_common_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--input", help="CSV/TSV token table, TextGrid CSV, or plain .txt for tag.")
    parser.add_argument("--input-text", help="Raw Traditional Mandarin text.")
    parser.add_argument("--output", help="Output CSV path. Defaults to stdout.")
    parser.add_argument("--word-col", default="word", help="Word/token column; falls back to Label/Word/token/Item.")
    parser.add_argument("--pos-col", default="pos", help="POS column when available.")
    parser.add_argument("--sent-col", default="sentence", help="Sentence/document grouping column.")
    parser.add_argument("--tier-col", default="TierName", help="TextGrid CSV tier column.")
    parser.add_argument("--tier-value", default="Word", help="TextGrid CSV tier value to keep; use '' to disable.")
    parser.add_argument(
        "--parser",
        choices=["rule", "ckiptagger", "ckipnlp", "articut", "stanford"],
        default="rule",
        help="Parser/tagger used when POS is missing or raw text is supplied.",
    )
    parser.add_argument("--ckip-data", help="ckiptagger model-data directory; also read from CKIPTAGGER_DATA.")
    parser.add_argument("--stanford-url", help="Stanford CoreNLP server URL; default http://localhost:9000.")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Calculate Traditional Mandarin n-gram and CFG semantic/syntactic surprisal."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    tag = subparsers.add_parser("tag", help="Segment/POS-tag text or fill POS for a token table.")
    add_common_args(tag)
    tag.set_defaults(func=run_tag)

    ngram = subparsers.add_parser("ngram", help="Calculate Witten-Bell word and POS n-gram surprisal.")
    add_common_args(ngram)
    ngram.add_argument("--train", help="Training token CSV/TSV. Defaults to --input.")
    ngram.add_argument("--order", type=int, default=3, help="N-gram order; the paper used POS trigrams.")
    ngram.add_argument("--min-count", type=int, default=1, help="Map rarer training items to <UNK>.")
    ngram.set_defaults(func=run_ngram)

    cfg = subparsers.add_parser("cfg", help="Calculate PCFG semantic and syntactic prefix surprisal.")
    add_common_args(cfg)
    cfg.add_argument("--treebank", required=True, help="Bracketed parsed treebank.")
    cfg.add_argument("--beam", type=int, default=5000, help="Beam size for incremental PCFG prefix parser.")
    cfg.add_argument("--save-grammar", help="Base JSON path for saving induced grammars.")
    cfg.set_defaults(func=run_cfg)

    all_cmd = subparsers.add_parser("all", help="Calculate n-gram surprisal and, if treebank is supplied, CFG surprisal.")
    add_common_args(all_cmd)
    all_cmd.add_argument("--train", help="Training token CSV/TSV. Defaults to --input.")
    all_cmd.add_argument("--treebank", help="Bracketed parsed treebank.")
    all_cmd.add_argument("--order", type=int, default=3)
    all_cmd.add_argument("--min-count", type=int, default=1)
    all_cmd.add_argument("--beam", type=int, default=5000)
    all_cmd.set_defaults(func=run_all)
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    if getattr(args, "tier_value", None) == "":
        args.tier_value = ""
    try:
        args.func(args)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
