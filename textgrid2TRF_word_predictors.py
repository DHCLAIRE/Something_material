#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from pathlib import Path

#from eelbrain import *
import eelbrain
from trftools import gammatone_bank
import numpy as np
from trftools.neural import edge_detector

# Source Github repo: https://github.com/Eelbrain/Alice

if __name__ == "__main__":
    DATA_ROOT = Path("/Volumes/Neurolang_1/Master Program/New_Thesis_topic")  #Path("~").expanduser() / 'Data' / 'Alice'
    STIMULUS_DIR = DATA_ROOT / "Alice(EEG dataset_mat_and stimuli)/audio"
    
    #print(STIMULUS_DIR)
    """
    ## THE FIRST STEP ## #from Alice/predictors/make_gammatone.py
    # Make Gammatone from audio file
    for i in range(1, 13):
        audio_gammatone = STIMULUS_DIR / f'{i}-gammatone.pickle'
        if audio_gammatone.exists():
            continue
        wav = load.wav(STIMULUS_DIR / f'DownTheRabbitHoleFinal_SoundFile{i}.wav')
        gt = gammatone_bank(wav, 20, 5000, 256, location='left', pad=False, tstep=0.001)
        save.pickle(gt, audio_gammatone)
    
    
    ## THE SECOND STEP ##  # from Alice/predictors/make_gammatone_predictors.py
    # Make predictors from gammatone
    
    #DATA_ROOT = Path("~").expanduser() / 'Data' / 'Alice'
    #STIMULUS_DIR = DATA_ROOT / 'stimuli'
    PREDICTOR_DIR = STIMULUS_DIR / 'audio_predictors'  # This command could automatically create a new folder
    #print(PREDICTOR_DIR)
    
    #PREDICTOR_DIR.mkdir(exist_ok=True)
    for i in range(1, 13):
        gt = load.unpickle(STIMULUS_DIR / f'{i}-gammatone.pickle')
    
        # Remove resampling artifacts
        gt = gt.clip(0, out=gt)
        # apply log transform
        gt = (gt + 1).log()
        # generate onset detector model
        gt_on = edge_detector(gt, c=30)
    
        # 1 band predictors
        save.pickle(gt.sum('frequency'), PREDICTOR_DIR / f'{i}~gammatone-1.pickle')
        save.pickle(gt_on.sum('frequency'), PREDICTOR_DIR / f'{i}~gammatone-on-1.pickle')
        
        # 8 band predictors
        x = gt.bin(nbins=8, func=np.sum, dim='frequency')
        save.pickle(x, PREDICTOR_DIR / f'{i}~gammatone-8.pickle')
        x = gt_on.bin(nbins=8, func=np.sum, dim='frequency')
        save.pickle(x, PREDICTOR_DIR / f'{i}~gammatone-on-8.pickle')
    
    """
    ## THE THIRD STEP ##  # from Alice/predictors/make_word_predictors.py
    """
    Generate predictors for word-level variables
    
    See the `explore_word_predictors.py` notebook for more background
    """
    #from pathlib import Path
    #import eelbrain
    #DATA_ROOT = Path("E:\\").expanduser() / 'Alice'
    #STIMULUS_DIR = DATA_ROOT  / 'Data' / 'stimuli'
    #PREDICTOR_DIR = DATA_ROOT / 'predictors'
    # /Volumes/Neurolang_1/Master Program/New_Thesis_topic/Alice(EEG dataset_mat_and stimuli)
    word_table = eelbrain.load.tsv(DATA_ROOT /'Alice(EEG_mat_and stimuli)'/ 'AliceChapterOne-EEG.csv')
    # Add word frequency as variable that scales with the expected response: larger response for less frequent words
    word_table['InvLogFreq'] = 17 - word_table['LogFreq']
    
    for segment in range(1, 13):
        segment_table = word_table.sub(f"Segment == {segment}") # still don't understand the  .sub() means
        # recreate a dataset for the pre-TRFs making
        ds = eelbrain.Dataset({'time': segment_table['onset']}, info={'tstop': segment_table[-1, 'offset']})  # segment_table[-1, 'offset'] == the last offset of segment 1~13
        # add predictor variables(add InvLogFreq as the LogFreq; for the purpose of line 73 in here)
        ds['LogFreq'] = segment_table['InvLogFreq']
        for key in ['NGRAM', 'CFG', 'Position']:  #'RNN', do not include
            ds[key] = segment_table[key]
        # create masks for lexical and non-lexical words
        ds['lexical'] = segment_table['IsLexical'] == True
        ds['nlexical'] = segment_table['IsLexical'] == False
        #print(ds)
        # save
        eelbrain.save.pickle(ds, STIMULUS_DIR / f'{segment}~Ngram-CFG_word.pickle')
   # /Volumes/Neurolang_1/Master Program/New_Thesis_topic/Alice(EEG dataset_mat_and stimuli)