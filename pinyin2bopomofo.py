#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from pathlib import Path
from typing import List, Tuple, Union

try:
    from pyzhuyin import pinyin_to_zhuyin as _pyzhuyin_pinyin_to_zhuyin
    from pyzhuyin import zhuyin_to_pinyin as _pyzhuyin_zhuyin_to_pinyin
except ImportError:  # pragma: no cover - depends on the user's environment
    _pyzhuyin_pinyin_to_zhuyin = None
    _pyzhuyin_zhuyin_to_pinyin = None

try:
    from pypinyin import Style as _PinyinStyle
    from pypinyin import lazy_pinyin as _lazy_pinyin
except ImportError:  # pragma: no cover - depends on the user's environment
    _PinyinStyle = None
    _lazy_pinyin = None


ZHUTONE_TO_NUMBER = {
    "": 1,
    "ˊ": 2,
    "ˇ": 3,
    "ˋ": 4,
    "˙": 5,
}
NUMBER_TO_ZHUTONE = {value: key for key, value in ZHUTONE_TO_NUMBER.items()}
ZHUTONE_MARKS = set(ZHUTONE_TO_NUMBER) - {""}


class PinyinBopomofoConverter:
    """Convert Mandarin pinyin, zhuyin/bopomofo, and Han text spellings."""

    def __init__(self, neutral_tone_prefix: bool = True):
        self.neutral_tone_prefix = neutral_tone_prefix

    @staticmethod
    def _require_pyzhuyin():
        if _pyzhuyin_pinyin_to_zhuyin is None or _pyzhuyin_zhuyin_to_pinyin is None:
            raise ImportError(
                "pyzhuyin is required for pinyin/zhuyin conversion. "
                "Install it with: pip install pyzhuyin"
            )

    @staticmethod
    def _require_pypinyin():
        if _lazy_pinyin is None or _PinyinStyle is None:
            raise ImportError(
                "pypinyin is required for Han character conversion. "
                "Install it with: pip install pypinyin"
            )

    @staticmethod
    def tone_number_to_mark(tone: Union[int, str]) -> str:
        """Convert tone number 1-5 to a zhuyin tone mark."""
        tone_int = int(tone)
        if tone_int not in NUMBER_TO_ZHUTONE:
            raise ValueError("Tone must be an integer from 1 to 5.")
        return NUMBER_TO_ZHUTONE[tone_int]

    @staticmethod
    def tone_mark_to_number(tone_mark: str) -> int:
        """Convert a zhuyin tone mark to its tone number."""
        if tone_mark not in ZHUTONE_TO_NUMBER:
            raise ValueError("Tone mark must be one of: '', ˊ, ˇ, ˋ, ˙.")
        return ZHUTONE_TO_NUMBER[tone_mark]

    def split_zhuyin_tone(self, zhuyin: str) -> Tuple[str, int]:
        """
        Split marked zhuyin into tone-less zhuyin and a tone number.

        Example:
            "ㄌㄨˇ" -> ("ㄌㄨ", 3)
        """
        if not isinstance(zhuyin, str) or not zhuyin.strip():
            raise ValueError("zhuyin must be a non-empty string.")

        text = zhuyin.strip()
        found_marks = [char for char in text if char in ZHUTONE_MARKS]
        if len(found_marks) > 1:
            raise ValueError(f"Only one tone mark is allowed: {zhuyin}")

        tone_mark = found_marks[0] if found_marks else ""
        bopomofo = "".join(char for char in text if char not in ZHUTONE_MARKS)
        return bopomofo, self.tone_mark_to_number(tone_mark)

    def join_zhuyin_tone(self, zhuyin: str, tone: Union[int, str]) -> str:
        """
        Join tone-less zhuyin and a tone number into marked zhuyin.

        The neutral tone is written before the syllable by default, matching
        common zhuyin spelling and pyzhuyin's accepted input style.
        """
        bopomofo = "".join(char for char in zhuyin.strip() if char not in ZHUTONE_MARKS)
        tone_int = int(tone)
        tone_mark = self.tone_number_to_mark(tone_int)

        if tone_int == 1:
            return bopomofo
        if tone_int == 5 and self.neutral_tone_prefix:
            return f"{tone_mark}{bopomofo}"
        return f"{bopomofo}{tone_mark}"

    def pinyin_to_zhuyin(self, pinyin: str) -> str:
        """Convert numbered pinyin, e.g. 'lu3', to marked zhuyin, e.g. 'ㄌㄨˇ'."""
        self._require_pyzhuyin()
        return _pyzhuyin_pinyin_to_zhuyin(pinyin)

    def pinyin_to_bopomofo(self, pinyin: str) -> str:
        """Alias for pinyin_to_zhuyin."""
        return self.pinyin_to_zhuyin(pinyin)

    def zhuyin_to_pinyin(self, zhuyin: str) -> str:
        """Convert marked zhuyin, e.g. 'ㄌㄨˇ', to numbered pinyin, e.g. 'lu3'."""
        self._require_pyzhuyin()
        return _pyzhuyin_zhuyin_to_pinyin(zhuyin)

    def bopomofo_to_pinyin(self, bopomofo: str) -> str:
        """Alias for zhuyin_to_pinyin."""
        return self.zhuyin_to_pinyin(bopomofo)

    def pinyin_to_zhuyin_parts(self, pinyin: str) -> Tuple[str, int]:
        """Convert pinyin to zhuyin, then split the zhuyin and tone."""
        return self.split_zhuyin_tone(self.pinyin_to_zhuyin(pinyin))

    def hanzi_to_pinyin(self, text: str) -> List[str]:
        """Convert Han characters to numbered pinyin using pypinyin."""
        self._require_pypinyin()
        return _lazy_pinyin(text, style=_PinyinStyle.TONE3, neutral_tone_with_five=True)

    def hanzi_to_zhuyin(self, text: str) -> List[str]:
        """Convert Han characters to marked zhuyin using pypinyin."""
        self._require_pypinyin()
        return _lazy_pinyin(text, style=_PinyinStyle.BOPOMOFO)


_DEFAULT_CONVERTER = PinyinBopomofoConverter()


def pinyin_to_zhuyin(pinyin: str) -> str:
    """Convert numbered pinyin to marked zhuyin."""
    return _DEFAULT_CONVERTER.pinyin_to_zhuyin(pinyin)


def pinyin_to_bopomofo(pinyin: str) -> str:
    """Convert numbered pinyin to marked bopomofo/zhuyin."""
    return _DEFAULT_CONVERTER.pinyin_to_bopomofo(pinyin)


def zhuyin_to_pinyin(zhuyin: str) -> str:
    """Convert marked zhuyin to numbered pinyin."""
    return _DEFAULT_CONVERTER.zhuyin_to_pinyin(zhuyin)


def bopomofo_to_pinyin(bopomofo: str) -> str:
    """Convert marked bopomofo/zhuyin to numbered pinyin."""
    return _DEFAULT_CONVERTER.bopomofo_to_pinyin(bopomofo)


def split_zhuyin_tone(zhuyin: str) -> Tuple[str, int]:
    """Split marked zhuyin into tone-less zhuyin and a tone number."""
    return _DEFAULT_CONVERTER.split_zhuyin_tone(zhuyin)


def join_zhuyin_tone(zhuyin: str, tone: Union[int, str]) -> str:
    """Join tone-less zhuyin and a tone number into marked zhuyin."""
    return _DEFAULT_CONVERTER.join_zhuyin_tone(zhuyin, tone)


def num2tone(inputToneSTR):
    '''
    Switch the Five tones in Mandarin from 12345 into the actual punctuations
    '''

    return PinyinBopomofoConverter.tone_number_to_mark(inputToneSTR)


'''
## NOTES for version of spellings ##

spelling_1_STR: e.g.ㄅㄚ4   # original one from the corpus
spelling_2_STR: e.g.ㄅㄚˋ   # tone changed-mark one  
spelling_3_STR: e.g.ba4    # pinyin version 

'''



if __name__ == "__main__":
    import pandas as pd

    
    # Open the corpus from folder
    #corpus_datapath = Path("/Users/neuroling/Documents/GitHub/Textgrid2TRF_Interface/Materials")
    #corpus_datapath = Path("/Users/kevinhsu/Documents/GitHub/Textgrid2TRF_Interface/Materials")
    corpus_datapath = Path("/Users/ting-hsin/Docs/Github/Textgrid2TRF_Interface/Materials")
    
    FFFB_refined_corpusLIST = []
    spelling_1_LIST = []
    spelling_2_LIST = []
    spelling_3_LIST = []
    ## Open the curpus files from the folder
    with open(corpus_datapath / 'corpus_FF_FB_20161206.csv', 'r', encoding = "utf-8") as corpus_csvf:
        fileLIST = corpus_csvf.read().split("\n")
        
        # See the content row by row
        for row in fileLIST[1:30]:
            rowLIST = row.split(",")
            print(len(rowLIST), rowLIST)
            
            
            ## Select the bpmf & its tone number
            bpmfSTR = str(rowLIST[3])
            toneSTR = str(rowLIST[4])
            print(len(toneSTR), type(toneSTR))
            
            ## Combine the bpmf with the tone (especially following the zhuyin_to_pinyin() arrangement)
            # First type of spelling
            spelling_1_STR = bpmfSTR + toneSTR     # original one  e.g.ㄅㄚ4

            # Second type of spelling
            if toneSTR == str(5):
                # Switch the Five tones in Mandarin from 12345 into the actual punctuations
                n_toneSTR = num2tone(toneSTR)
                spelling_2_STR = n_toneSTR + bpmfSTR    # zhuyin_to_pinyin accept the fifth tone in tone first and bpmf second
            else:
                n_toneSTR = num2tone(toneSTR)
                spelling_2_STR = bpmfSTR + n_toneSTR    # tone mark changed one  e.g.ㄅㄚˋ
            
            # Third type of spelling
            ## Switch the zhuyin to pinyin by pyzhuyin tool
            spelling_3_STR = zhuyin_to_pinyin(spelling_2_STR)   # pinyin version e.g. ba4
            #pinyinLIST.append(ToneTransferedSTR)  # Or should I just add the ToneTransferedSTR at the end of the csv column?? Yes
            
            ## Put all spellings as one small LIST
            spelling_1_LIST.append(spelling_1_STR)
            spelling_2_LIST.append(spelling_2_STR)
            spelling_3_LIST.append(spelling_3_STR)
            
            ## Checking for the results
            print(bpmfSTR, n_toneSTR)
            print(spelling_2_STR)
            #print(spellingSTR)
            #print(type(spellingSTR))
            #print(new_spellingLIST)
            print(len(rowLIST), rowLIST)
            
        
    ## Save the processed spellings in the original csv file (position: at the end of the file)
    corpusfile = corpus_datapath / "corpus_FF_FB_20161206.csv"
    old_DF = pd.read_csv(corpusfile, header=None)
    spelling_1_values = spelling_1_LIST
    spelling_2_values = spelling_1_LIST
    spelling_3_values = spelling_1_LIST
    
    old_DF["ori_zhuyin"] = spelling_1_values
    #old_DF["mrked_zhuyin"] = spelling_2_values
    #old_DF["pinyin"] = spelling_3_values
    
    ## Save the extended columns back to the original file
    old_DF.to_csv(corpus_csvf, index=False)
    
