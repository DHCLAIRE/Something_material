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
#from nltk import tokenizer

if __name__ == "__main__":
    
    # Open the csv file
    #corpus_datapath = Path("/Users/neuroling/Documents/GitHub/Textgrid2TRF_Interface/Materials")
    #corpus_datapath = Path("/Users/kevinhsu/Downloads/Sound/")
    corpus_datapath = Path("/Users/ting-hsin/Docs/Github/Textgrid2TRF_Interface/Materials")
    with open(corpus_datapath / 'corpus_FF_FB_20161206.csv', 'r', encoding = "utf-8") as csvf:
        fileLIST = csvf.read().split("\n")
        
        FFFB_refined_corpusLIST = []
        for row in fileLIST[1:100]:
            rowLIST = row.split(",")
            #print(fileLIST[0]) # this is the index of every column, therefore please exclude it
            print(rowLIST)
            #print(len(rowLIST))
            
            #print(rowLIST[2], rowLIST[9], rowLIST[17])  # 2 = syllable; 9 = homophone counts; 17 = Frequency of syllable, all in str
            #print(type(rowLIST[2]), type(rowLIST[9]), type(rowLIST[17]))
            
            syllableSTR = rowLIST[2]
            homophone_countINT = int(rowLIST[9])
            LogFreq_SylbFLOAT = float(rowLIST[17])
            
            print(syllableSTR, type(syllableSTR), "; ", homophone_countINT, type(homophone_countINT), "; ", LogFreq_SylbFLOAT, type(LogFreq_SylbFLOAT))
            
    ## TEST SO FAR  ##
            tmpLIST = [syllableSTR, homophone_countINT, LogFreq_SylbFLOAT]
            FFFB_refined_corpusLIST.append(tmpLIST)
    pprint(FFFB_refined_corpusLIST)
    
    ## The next part is to get syllable/homophone/LogFreq info of the LTTC script's target words from the FFFB corpus
    
    
    """
    ## This is just for checking and for user to search for the target word later ##
    testingSTR = input("word: ")
    
    for corpusLIST in FFFB_refined_corpusLIST:
        if re.search(corpusLIST[0], testingSTR):
            print(corpusLIST[1], corpusLIST[2])
        else:
            pass
    """
            
            
            
            
            
            
            
            
    