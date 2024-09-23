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
from pyzhuyin import pinyin_to_zhuyin  #, zhuyin_to_pinyin

## To-Do List ##
# 1. Think how to include CKIP / Stanford Parser as one of the options
# 2. Organize the texts into corpus (Or at least do some text preprocessing first for better efficiency on text analysis)
# 3. Analyze the organized texts and then divided them into different levels of difficulties based on the complexity of the sentences
# 4. ** (Ongoing) Another Project ** Combine with the materials production interface function (for psycholinguistics/neurolinguistics use corpus)


## To-Do List FOR NOW ##
# 1. Check the tools and look for obstacles

if __name__ == "__main__":
    
    # Import the text, run the parsing and then produce the syntax tree drawing
    
    ## The current progress: Still reading every script, and figuring out what to put in this script. 
    ## So far, most likely is the syntax_tree.py commands would be put inside this script. 
    