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
    file_datapath = Path("/Users/ting-hsin/Downloads/LTTC_TZUCHI/LTTC_TZUCHI-1/SET A/SetA_updated_TextGrid_w_VOT+POS")
    
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
            
        pprint(All_txt_LIST[:10])
    
    
    
    ### YOU GOT THE WRONG FILE, THE ONE YOU SHOULD BE USING IS THE CHINESE SCRIPT FROM THE AUDIO USED IN THE EXPERIMENT###
    ### MODIFY THE INPUT FILE !!! ###
    csv_dataLIST = []
    # Load in the FFFB corpus to add the freq at the end of the csv
    with open(file_datapath / 'n_Set_A_HCD_1_Witch_s_Broom_sheng1_chu4_ji3_an4.TextGrid.csv', 'r', encoding = "utf-8") as LTTC_csvF:
        LTTC_csv_dataSTR = LTTC_csvF.read().split("\n")
        
        pprint(LTTC_csv_dataSTR)
        
        #LTTC_csv_dataSTR[0] = LTTC_csv_dataSTR[0].append("freq_char_ASBC")
        #print(LTTC_csv_dataSTR[0])
        
        ## Start the search of the 
        for seg_rowSTR in LTTC_csv_dataSTR[1:20]:
            segmentLIST = seg_rowSTR.split(",")
            pprint(segmentLIST)
            print(segmentLIST[3])  # the char in the file
            
            for n_rowLIST in All_txt_LIST:
                if segmentLIST[3] == n_rowLIST[0]:
                    print("Match", segmentLIST[3])
                    print(n_rowLIST[1]) # the freq of the char
                    segmentLIST.append(n_rowLIST[1])
                    print(segmentLIST)
                else:
                    pass
                    #print("Error: 404 not found")  # DIDN'T FIND ANYTHING ?!!!
            #FFFB_dataLIST.append(tmpLIST)
        
        
        #pprint(FFFB_dataLIST)
        #print(len(FFFB_dataLIST))
        #print(FFFB_dataLIST[:][3])
        ##pprint(FFFBcorpus_csv_dataSTR[:10])