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
    #corpus_datapath = Path("/Users/kevinhsu/Documents/GitHub/Textgrid2TRF_Interface/Materials")
    corpus_datapath = Path("/Users/ting-hsin/Docs/Github/Textgrid2TRF_Interface/Materials")
    
    ASBC_corpusLIST = []
    with open(corpus_datapath / 'word_freq.txt', 'r', encoding = "utf-8") as ASBCcorpus_txt:
        ASBC_dataSTR = ASBCcorpus_txt.read()
        # segment the 
        ASBC_corpusLIST = ASBC_dataSTR.split("\n") 
        #print(type(ASBC_dataSTR)) ##STR
        #pprint(ASBC_dataSTR[:12])  ## '一\t113236\n一'
        #pprint(ASBC_corpusLIST[:10])
        
        All_txt_LIST = []
        for rowSTR in ASBC_corpusLIST[:100]:
            
            print(rowSTR)
            """
            tmpRowLIST = rowSTR.split("]\n")
            print(tmpRowLIST)
            All_txt_LIST.append(tmpRowLIST)
            #print(type(tmpRowLIST))
            #print(tmpRowLIST)
            
        pprint(All_txt_LIST[:10])
        """
        
