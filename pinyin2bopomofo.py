#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import sys, re

from pprint import pprint
import csv
import json
import random
from random import sample
import os
#from gtts import gTTS
import pandas as pd
import time
from pathlib import Path
#import nltk
#import re
#from nltk import sent_tokenize
#from nltk import tokenize
from pyzhuyin import pinyin_to_zhuyin, zhuyin_to_pinyin


if __name__ == "__main__":
    
    # Open the corpus from folder
    #corpus_datapath = Path("/Users/neuroling/Documents/GitHub/Textgrid2TRF_Interface/Materials")
    corpus_datapath = Path("/Users/kevinhsu/Documents/GitHub/Textgrid2TRF_Interface/Materials")
    
    FFFB_refined_corpusLIST = []
    with open(corpus_datapath / 'corpus_FF_FB_20161206.csv', 'r', encoding = "utf-8") as corpus_csvf:
        fileLIST = corpus_csvf.read().split("\n")
        
        for row in fileLIST[1:100]:
            rowLIST = row.split(",")
            print(len(rowLIST), rowLIST)
            
            
            bpmfSTR = rowLIST[3]
            toneSTR = rowLIST[4]
            
            
            print(bpmfSTR, toneSTR)
            
            
            """
            # the transformation
            assert(pinyin_to_zhuyin("lu3") == "ㄌㄨˇ")
            assert(pinyin_to_zhuyin("dan4") == "ㄉㄢˋ")
            #assert(map(pinyin_to_zhuyin, ["lu3", "dan4"]) == ["ㄌㄨˇ", "ㄉㄢˋ"])
            
            assert(zhuyin_to_pinyin("ㄌㄩˊ") == "lü2")
            assert(zhuyin_to_pinyin("˙ㄗ") == "zi5")
            #assert(map(lambda z: zhuyin_to_pinyin(z, u_to_v=True), ["ㄌㄩˊ", "˙ㄗ"]) == ["lv2", "zi5"])
            """
        