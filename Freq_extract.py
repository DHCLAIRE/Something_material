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
        ASBC_dataSTR = ASBCcorpus_txt.readlines()
        # segment the data by \n 
        #ASBC_corpusLIST = ASBC_dataSTR.split("\n") 
        #print(type(ASBC_dataSTR)) ##STR
        pprint(ASBC_dataSTR[:12])  ## '一\t113236\n一'
        #pprint(ASBC_corpusLIST[:10])
        
        # Select the freq by its own character
        All_txt_LIST = []
        for rowSTR in ASBC_dataSTR:
            #print(rowSTR)
            # exclude the \n at the end of the strings, and split the data by \t
            rowSTR = rowSTR.replace("\n", "")
            tmpRowLIST = rowSTR.split("\t")
            #print(tmpRowLIST)
            # Append the cleased textLIST into bigger LIST
            All_txt_LIST.append(tmpRowLIST)
            #print(type(tmpRowLIST))
            #print(tmpRowLIST)
            
        #pprint(All_txt_LIST[:10])
    
    
    FFFB_dataLIST = []
    # Load in the FFFB corpus to add the freq at the end of the csv
    with open(corpus_datapath / 'corpus_FF_FB_20161206.csv', 'r', encoding = "utf-8") as FFFBcorpus_csv:
        FFFBcorpus_csv_dataSTR = FFFBcorpus_csv.read().split("\n")
        
        for char_rowSTR in FFFBcorpus_csv_dataSTR[:20]:
            #print(char_rowSTR)
            #print(len(char_rowSTR))
            tmpCharLIST = char_rowSTR.split(",")
            #pprint(tmpCharLIST)
            #print(tmpCharLIST[2])  # the char in the corpus
            for n_rowLIST in All_txt_LIST:
                if tmpCharLIST[2] == n_rowLIST[0]:
                    print("Match", tmpCharLIST[2])
                else:
                    pass
                    #print("Error: 404 not found")
            #FFFB_dataLIST.append(tmpLIST)
            
        
        #pprint(FFFB_dataLIST)
        #print(len(FFFB_dataLIST))
        #print(FFFB_dataLIST[:][3])
        ##pprint(FFFBcorpus_csv_dataSTR[:10])