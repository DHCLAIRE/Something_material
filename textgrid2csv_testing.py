#!/usr/bin/env python3
# -*- coding:utf-8 -*-

"""#!/usr/bin/python
# textgrid2csv.py
# D. Gibbon
# 2016-03-15
# 2016-03-15 (V02, includes filename in CSV records)
"""
#-------------------------------------------------
# Import modules

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
#-------------------------------------------------
# Text file input / output

def inputtextlines(filename):
    handle = open(filename,'r')
    print(handle)
    linelist = handle.readlines()
    handle.close()
    return linelist

def outputtext(filename, text):
    handle = open(filename,'w')  #, encoding="utf-8"
    handle.write(text)
    handle.close()

#-------------------------------------------------
# Conversion routines

def converttextgrid2csv(textgridlines,textgridname):

    csvtext = '# TextGrid to CSV (D. Gibbon, 2008-11-23)\n# Open the file with OpenOffice.org Calc or MS-Excel.\nFileName\tTierType\tTierName\tLabel\tStart\tEnd\tDuration\n'

    newtier = False
    for line in textgridlines[9:]:
        line = re.sub('\n','',line)
        line = re.sub('^ *','',line)
        linepair = line.split(' = ')
        if len(linepair) == 2:
            if linepair[0] == 'class':
                classname = linepair[1]
            if linepair[0] == 'name':
                tiername = linepair[1]
            if linepair[0] == 'xmin':
                xmin = linepair[1]
            if linepair[0] == 'xmax':
                xmax = linepair[1]
            if linepair[0] == 'text':
                text = linepair[1]
                diff = str(float(xmax)-float(xmin))
                csvtext += textgridname + '\t' + classname + '\t' + tiername + '\t' + text + '\t' + xmin + '\t' + xmax + '\t' + diff + '\n'
    return csvtext

#-------------------------------------------------
# Main caller
"""
def main():

    if len(sys.argv) < 2:
        print("Usage: textgrid2csv.py <textgridfilename>")
        exit()
    textgridname = sys.argv[1]
    csvname = textgridname + '.csv'

    textgrid = inputtextlines(textgridname)

    textcsv = converttextgrid2csv(textgrid,textgridname)

    outputtext(csvname,textcsv)

    print("Output file: " + csvname)

    return
"""

def LISTblankEraser(rawLIST):
    '''
    Remove the blank that inside the list
    '''
    newrawLIST = []
    for row in rawLIST:
        if len(row) == 0:
            rawLIST.pop(rawLIST.index(row))
        else:
            pass
    newrawLIST = rawLIST
    #print(len(newrawLIST))
    return newrawLIST

def WordCleaner(WordLIST):
    '''
    Remove redundant symbol in wordLIST
    '''
    newWordLIST = []
    for word in WordLIST:
        if len(word) != 1:
            word = re.sub(r'[^\w]', '', word)
            print(len(word), word)
        else:
            print("Here:", word)
        newWordLIST.append(word)
    return newWordLIST

def characCleaner(STR):
    '''
    Remove redundant symbol in a string
    '''
    n_word = re.sub(r'[^\w]', '', STR)
    return n_word
"""
add ckip2articut self-defined function
add pos options for ckip or articut or others??
"""

if __name__ == "__main__":
    
    textgrid_path = "/Users/neuroling/Downloads/Sound/"
    #textgrid_path = "/Users/kevinhsu/Downloads/Sound/"
    
    textgridname = textgrid_path + "story1.TextGrid"
    csvname = textgridname + '.csv'

    textgrid = inputtextlines(textgridname)

    textcsv = converttextgrid2csv(textgrid,textgridname)

    outputtext(csvname,textcsv)

    print("Output file: " + csvname)
    
    
    # Open the corpus from folder
    corpus_datapath = Path("/Users/neuroling/Documents/GitHub/Textgrid2TRF_Interface/Materials")
    #corpus_datapath = Path("/Users/kevinhsu/Documents/GitHub/Textgrid2TRF_Interface/Materials")
    
    FFFB_refined_corpusLIST = []
    with open(corpus_datapath / 'corpus_FF_FB_20161206.csv', 'r', encoding = "utf-8") as corpus_csvf:
        fileLIST = corpus_csvf.read().split("\n")
        for row in fileLIST[1:]:
            rowLIST = row.split(",")
            #print(len(rowLIST), rowLIST)
            # Extract the syllable info & its homophone & its LogFreqeuncy
            syllableSTR = rowLIST[2]
            homophone_countINT = int(rowLIST[9])
            LogFreq_SylbFLOAT = float(rowLIST[17])
            #print(syllableSTR, type(syllableSTR), "; ", homophone_countINT, type(homophone_countINT), "; ", LogFreq_SylbFLOAT, type(LogFreq_SylbFLOAT))
            tmpLIST = [syllableSTR, homophone_countINT, LogFreq_SylbFLOAT]
            FFFB_refined_corpusLIST.append(tmpLIST)
    #pprint(FFFB_refined_corpusLIST)
            
    # The predictor items
    SyllableLIST = []       #  = textgrid.csv_syllable
    SegmentLIST = []        #  = the sequence of the story
    Sylb_OnsetLIST = []     #  = textgrid.csv_start from syllable
    Sylb_OffsetLIST = []    #  = textgrid.csv_end from syllable
    Sylb_OrderLIST = []     #  = count by the index of the syllable
    Sylb_LogFreqLIST = []   #  = LogFreq by the index of the syllable
    Sylb_LogFreq_PrevLIST = []
    Sylb_LogFreq_NextLIST = []
    #SndPowerLIST = []
    HomophoneCountLIST = []  # = the count of homophone on syllable
    LengthLIST = []    #  = textgrid.csv_duration of syllable
    PositionLIST = []  #  = 
    SentenceLIST = []  #  = 
    POS_LIST = []
    IsLexicalLIST = [] #  = textgrid.csv_POS (or universal pos)
    #NGRAM_LIST = []
    #CFG_LIST = []
    #Fractality_LIST = []
    Word_LIST = []     #  = textgrid.csv_word
    Word_OrderLIST = [] 
    Word_LogFreqLIST = []
    Word_OnsetLIST = []  

    # The List of unwanted Segmentation results 
    skipLIST = ['"SILPAUSE" ', '"\\" ', '"n" ']
    
    # Open the csv file
    with open (csvname, "r", encoding="utf-8") as textgrid_csvfile:
        textgrid_fileLIST = textgrid_csvfile.read().split("\n")
        textgrid_fileLIST = LISTblankEraser(textgrid_fileLIST)
        #fileLIST.pop(0)
        #print(len(textgrid_fileLIST)) # length Should be 30 
        #pprint(fileLIST)
        
        # find the word out of the textgrid file
        for textgrid_row in textgrid_fileLIST[2818:2900]:#[1000:110]:  # [2818:4048]
            textgrid_rowLIST = textgrid_row.split("\t")
            
            # Syllable (with the exclusion of )
            if textgrid_rowLIST[2] == '"Syllable" ' and textgrid_rowLIST[3] not in skipLIST:  
                syllableSTR = characCleaner(textgrid_rowLIST[3])
                print(syllableSTR)
                
                #if syllableSTR not in skipLIST:
                sylb_onsetFLOAT = round(float(textgrid_rowLIST[4]), 4)
                sylb_offsetFLOAT = round(float(textgrid_rowLIST[5]), 4)
                sylb_lengthFLOAT = round(float(textgrid_rowLIST[6]), 4)
                
                SyllableLIST.append(syllableSTR)
                #SegmentLIST.append(1)  # because it is story 1
                Sylb_OnsetLIST.append(sylb_onsetFLOAT)
                Sylb_OffsetLIST.append(sylb_offsetFLOAT)
                LengthLIST.append(sylb_lengthFLOAT)
                #Sylb_OrderLIST.append(1)  # not 1, it should be sequence from 1 to the total amount
                
                
                ## Matching the syllable onto the FFFB corpus
                for corpusLIST in FFFB_refined_corpusLIST:
                    if re.search(corpusLIST[0], syllableSTR):
                        print(corpusLIST[1], corpusLIST[2])
                        HomophoneCountLIST.append(corpusLIST[1])
                        Sylb_LogFreqLIST.append(corpusLIST[2])
                    else:
                        pass
                
            else:
                pass
            
        # Checking the results
        print(len(SyllableLIST), SyllableLIST)
        print(len(Sylb_OnsetLIST), Sylb_OnsetLIST)
        print(len(Sylb_OffsetLIST), Sylb_OffsetLIST)
        print(len(LengthLIST), LengthLIST)
        print(len(HomophoneCountLIST), HomophoneCountLIST)
        print(len(Sylb_LogFreqLIST), Sylb_LogFreqLIST)
        #print(len(IsLexicalLIST), IsLexicalLIST)
        
        """
                # Word 
                if textgrid_rowLIST[2] == '"Word" ':
                    wordSTR = textgrid_rowLIST[3]
                    # exclude the skip information >> but I decided this step would be the last step
                    if wordSTR not in skipLIST:  # '"SILPAUSE" ' and '"\\" ' and '"n" ':
                        # get the onset/offset/length of the word
                        Word_LIST.append(wordSTR)

                        
                    else:
                        print(textgrid_rowLIST[3])
                
                # POS for Islexical(lexciality)
                if rowLIST[2] == '"POS" ':
                    #detailed_word_posSTR = rowLIST[3]
                    pass
                # UniversalPOS >> What's the difference??
                if rowLIST[2] == '"UniversalPOS" ':
                    simp_word_posSTR = rowLIST[3]
                    IsLexicalLIST.append(simp_word_posSTR)
                    #pass
                else:
                    print(rowLIST[2])
                """

"""
    # Saving the self_paced_rt result into csv file
    dataDICT = pd.DataFrame({
        'Syllable':SyllableLIST,
        #'Segment':SegmentLIST,
        'Sylb_Onset':Sylb_OnsetLIST,
        'Sylb_Offset':Sylb_OffsetLIST,
        #'Sylb_Order':Sylb_OrderLIST,
        'Sylb_LogFreq':Sylb_LogFreqLIST,
        #'Sylb_LogFreq_Prev':LogFreq_PrevLIST,
        #'Sylb_LogFreq_Next':LogFreq_NextLIST,
        #'SndPower':SndPowerLIST,
        'Homophone_cnts':HomophoneCountLIST,
        #'Position':PositionLIST,
        #'Sentence':SentenceLIST,
        #'POS': POS_LIST,
        #'IsLexical':IsLexicalLIST,
        #'NGRAM':NGRAM_LIST,
        #'CFG':CFG_LIST,
        #'Fractality':Fractality_LIST
        #'Word':Word_LIST,
        #'Word_order': Word_OrderLIST,
        #'Word_LogFreq': Word_LogFreqLIST,
        #'Word_Onset': Word_OnsetLIST
        })
                           
    #data_path = "/Users/ting-hsin/Docs/Github/ICN_related/"
    file_name = 'story1_predictor_tables.csv' 
    save_path = textgrid_path / Path(file_name)
    dataDICT.to_csv(save_path, sep = "," ,index = False , header = True, encoding = "UTF-8")
"""