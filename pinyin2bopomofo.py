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


def num2tone(inputToneSTR):
    '''
    Switch the Five tones in Mandarin from 12345 into the actual punctuations
    '''
    
    if inputToneSTR == str(1):
        inputToneSTR = "" #*zhuyin_to_pinyin(): use without the space to represent the first tone
    elif inputToneSTR == str(2):
        inputToneSTR = "ˊ"
    elif inputToneSTR == str(3):
        inputToneSTR = "ˇ"
    elif inputToneSTR == str(4):
        inputToneSTR = "ˋ"
    elif inputToneSTR == str(5):
        inputToneSTR = "˙"
        
    return inputToneSTR


'''
## NOTES for version of spellings ##

spelling_1_STR: e.g.ㄅㄚ4   # original one from the corpus
spelling_2_STR: e.g.ㄅㄚˋ   # tone changed-mark one  
spelling_3_STR: e.g.ba4    # pinyin version 

'''



if __name__ == "__main__":
    
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
    