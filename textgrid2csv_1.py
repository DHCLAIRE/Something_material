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


"""
add ckip2articut self-defined function
add pos options for ckip or articut (or others? Jeiba at least?)
add problem solver for different parsing result between CKIP & Articut >> Is there a ultimate solution for different parsing results??
for TRF(continue to add it):
add freq count

POS = CKIP POS from Academia Sinica, Taiwan
Universal POS = Universal Dependencies, an community for NLP, 

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
    
    
    # The predictor items
    Word_LIST = []     #  = textgrid.csv_word
    SegmentLIST = []   #  = the sequence of the story
    OnsetLIST = []     #  = textgrid.csv_start
    OffsetLIST = []    #  = textgrid.csv_end
    OrderLIST = []     #  = count by the index of the word
    LogFreqLIST = []
    LogFreq_PrevLIST = []
    LogFreq_NextLIST = []
    SndPowerLIST = []
    LengthLIST = []    #  = textgrid.csv_duration
    PositionLIST = []  #  = count from the raw txt file (office word file)
    SentenceLIST = []  #  = count from the raw txt file (office word file)
    IsLexicalLIST = [] #  = textgrid.csv_POS (or universal pos)
    #NGRAM_LIST = []
    #CFG_LIST = []
    #Fractality_LIST = []
    
    # The List of unwanted Segmentation results 
    skipLIST = ['"SILPAUSE" ', '"\\" ', '"n" ']
    TierTypeLIST = ['"Text" ', '"Word" ', '"POS" ', '"UniversalPOS" ', '"Syllable" ', '"Pinyin" ', '"Segment" ']  # 7 tiers
    
    
    # Count the amount of each Tier type
    TextCountINT = 0
    WordCountINT = 0
    POSCountINT = 0
    UniPOSCountINT = 0
    SyllCountINT = 0
    PinyCountINT = 0
    SegmentCountINT = 0
    outliersINT = 0
    
    # Open the csv file
    with open (csvname, "r", encoding="utf-8") as csvfile:
        fileLIST = csvfile.read().split("\n")
        fileLIST = LISTblankEraser(fileLIST)
        #fileLIST.pop(0)
        print(len(fileLIST)) # length Should be 30 
        #pprint(fileLIST)
        
        # Go through every Tier for wanted infos
        for row in fileLIST:#[1000:110]:
            #print(row)
            #print(len(row))
            rowLIST = row.split("\t")
            #print(rowLIST)
            #print(len(rowLIST))  # len = 7 items
            #print(rowLIST[0])
            
            # Count the quantity of every Tiers
            if len(rowLIST) > 2:
                # Text =len 1
                if TierTypeLIST[0] == rowLIST[2]:
                    TextCountINT +=1
                # Word =len 938
                if TierTypeLIST[1] == rowLIST[2]:
                    WordCountINT +=1
                # POS =len 938
                if TierTypeLIST[2] == rowLIST[2]:
                    POSCountINT +=1
                # UniversalPOS =len 938
                if TierTypeLIST[3] == rowLIST[2]:
                    UniPOSCountINT +=1
                # Syllable =len 1231
                if TierTypeLIST[4] == rowLIST[2]:
                    SyllCountINT +=1
                # Pinyin =len 1231
                if TierTypeLIST[5] == rowLIST[2]:
                    PinyCountINT +=1
                # Segment =len 2455
                if TierTypeLIST[6] == rowLIST[2]:
                    SegmentCountINT +=1
                # Show outliers
                else:
                    #outliersINT +=1
                    #print(rowLIST)
                    pass
                    
            else:
                pass
        print(TextCountINT)
        print(WordCountINT)
        print(POSCountINT)
        print(UniPOSCountINT)
        print(SyllCountINT)
        print(PinyCountINT)
        print(SegmentCountINT)
        
        # We should save the counts into DICT!!!!  later >>

    """
            if len(rowLIST) > 2:
                # Word 
                if rowLIST[2] == '"Word" ':
                    wordSTR = rowLIST[3]
                    # exclude the skip information >> but I decided this step would be the last step
                    if wordSTR not in skipLIST:  # '"SILPAUSE" ' and '"\\" ' and '"n" ':
                        # get the onset/offset/length of the word
                        onsetFLOAT = round(float(rowLIST[4]), 4)
                        offsetFLOAT = round(float(rowLIST[5]), 4)
                        lengthFLOAT = round(float(rowLIST[6]), 4)
                        Word_LIST.append(wordSTR)
                        #SegmentLIST.append(1)  # because it is story 1
                        #OnsetLIST.append(onsetFLOAT)
                        #OffsetLIST.append(offsetFLOAT)
                        #LengthLIST.append(lengthFLOAT)
                        #LogFreqLIST.append(0)
                        #LogFreq_NextLIST.append(0)
                        #LogFreq_PrevLIST.append(0)
                        
                    else:
                        print(rowLIST[3])
                        
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
                    
            else:
                pass
        """
            
            
        
        # Checking the results
        #n_WordLIST = WordCleaner(Word_LIST)
        #print(len(n_WordLIST[0]), n_WordLIST[0])
        #print(len(n_WordLIST), n_WordLIST)
        #print(len(OnsetLIST), OnsetLIST)
        #print(len(OffsetLIST), OffsetLIST)
        ##print(len(LengthLIST), LengthLIST)
        #print(len(IsLexicalLIST), IsLexicalLIST)
        #print(len(LogFreqLIST), LogFreqLIST)  # we might found this in the corpus of Academia Sinica
        #print(len(LogFreq_NextLIST), LogFreq_NextLIST)
        #print(len(LogFreq_PrevLIST), LogFreq_PrevLIST)
        
    
    """
    # Saving the self_paced_rt result into csv file
    dataDICT = pd.DataFrame({'Word':Word_LIST,
                           'Segment':SegmentLIST,
                           'Onset':OnsetLIST,
                           'Offset':OffsetLIST,
                           'Order':OrderLIST,
                           'LogFreq':LogFreqLIST,
                           'LogFreq_Prev':LogFreq_PrevLIST,
                           'LogFreq_Next':LogFreq_NextLIST,
                           'SndPower':SndPowerLIST,
                           'Position':PositionLIST,
                           'Sentence':SentenceLIST,
                           'IsLexical':IsLexicalLIST
                           #'NGRAM':NGRAM_LIST,
                           #'CFG':CFG_LIST,
                           #'Fractality':Fractality_LIST
                           })
                           
    #data_path = "/Users/ting-hsin/Docs/Github/ICN_related/"
    file_name = 'story1_predictor_tables.csv' 
    save_path = textgrid_path / Path(file_name)
    dataDICT.to_csv(save_path, sep = "," ,index = False , header = True, encoding = "UTF-8")
"""