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
    #DATA_ROOT = Path("/Users/neuroling/Downloads")  #Path("~").expanduser() / 'Data' / 'Alice'
    DATA_ROOT = Path("/Users/kevinhsu/Downloads")
    STIMULUS_DIR = DATA_ROOT / "SetB_Story_sound"  #"SetA_Story_sound" & "SetB_Story_sound"
    
    print(STIMULUS_DIR)
    
    #SetA_HCD_story_nameLIST = ["Witch_s_Broom", "Animal_Hospital", "Meatball_Soup", "No_Tomatoes", "Mouse_Kiki", "Rabbit_With_Short_Ears"]  #Set_A_HCD_6_Rabbit_With_Short_Ears_sheng1_chu4_ji3_an4.wav
    #SetA_LCD_story_nameLIST = ["Braveness"]  #Set_A_LCD_1_Braveness_pu2_zu2_bo4_luo2.wav
    SetB_HCD_story_nameLIST = ["Magician", "Giant", "Rabbit_With_Short_Ears", "Mouse_Kiki", "Braveness", "Witch_s_Broom"]
    #SetB_LCD_story_nameLIST = ["Animal_Hospital"]  #Set_B_LCD_1_Animal_Hospital_sheng1_chu4_ji3_an4_mono.wav
    
    """
    ## THE FIRST STEP ## #from Alice/predictors/make_gammatone.py
    # Make Gammatone from audio file
    for i in range(1, 7):
        audio_gammatone = STIMULUS_DIR / "Set_A_gammatone" / f'Set_A_HCD_{i}_{SetA_HCD_story_nameLIST[i-1]}_sheng1_chu4_ji3_an4-gammatone.pickle'   # Set_B_HCD_1_Magician_pu2_zu2_bo4_luo2
        if audio_gammatone.exists():
            continue
        wav = eelbrain.load.wav(STIMULUS_DIR / f'Set_A_HCD_{i}_{SetA_HCD_story_nameLIST[i-1]}_sheng1_chu4_ji3_an4_mono.wav')  #Set_B_HCD_1_Magician_pu2_zu2_bo4_luo2  >> Magician: this part is different in each tape, so...
        gt =  eelbrain.gammatone_bank(wav, 20, 5000, 256, location='left', tstep=0.001) #, pad=False 
        #n_gt =  eelbrain.gammatone_bank(wav, 80, 15000, 128, location='left', tstep=0.001)
        eelbrain.save.pickle(gt, audio_gammatone)
    """
    
    ## THE SECOND STEP ##  # from Alice/predictors/make_gammatone_predictors.py
    # Make predictors from gammatone
    
    #DATA_ROOT = Path("~").expanduser() / 'Data' / 'Alice'
    #STIMULUS_DIR = DATA_ROOT / 'stimuli'
    PREDICTOR_DIR = STIMULUS_DIR / 'Set_B_audio_predictors'  # This command could automatically create a new folder #'Set_B_audio_predictors'
    #print(PREDICTOR_DIR)
    
    #PREDICTOR_DIR.mkdir(exist_ok=True)
    for i in range(1, 7):
        gt = eelbrain.load.unpickle(STIMULUS_DIR / "Set_B_gammatone" / f'Set_B_HCD_{i}_{SetB_HCD_story_nameLIST[i-1]}_pu2_zu2_bo4_luo2-gammatone.pickle')
        
        """
        ### For old version ###
        # Remove resampling artifacts
        gt = gt.clip(0, out=gt)
        # apply log transform
        gt = (gt + 1).log()
        # generate onset detector model
        gt_on = eelbrain.edge_detector(gt, c=30)
    
        # 1 band predictors
        save.pickle(gt.sum('frequency'), PREDICTOR_DIR / f'Set_A_HCD_{i}~gammatone-1.pickle')
        save.pickle(gt_on.sum('frequency'), PREDICTOR_DIR / f'Set_A_HCD_{i}~gammatone-on-1.pickle')
        
        # 8 band predictors
        x = gt.bin(nbins=8, func=np.sum, dim='frequency')
        save.pickle(x, PREDICTOR_DIR / f'Set_A_HCD_{i}~gammatone-8.pickle')
        x = gt_on.bin(nbins=8, func=np.sum, dim='frequency')
        save.pickle(x, PREDICTOR_DIR / f'Set_A_HCD_{i}~gammatone-on-8.pickle')
        """
        
        ### Below is the new version ###
        # Apply a log transform to approximate peripheral auditory processing
        gt_log = (gt + 1).log()
        # Apply the edge detector model to generate an acoustic onset spectrogram
        gt_on = eelbrain.edge_detector(gt_log, c=30)
    
        # Create and save 1 band versions of the two predictors (i.e., temporal envelope predictors)
        eelbrain.save.pickle(gt_log.sum('frequency'), PREDICTOR_DIR / f'Set_B_HCD_{i}~gammatone-1.pickle')
        eelbrain.save.pickle(gt_on.sum('frequency'), PREDICTOR_DIR / f'Set_B_HCD_{i}~gammatone-on-1.pickle')
        # Create and save 8 band versions of the two predictors (binning the frequency axis into 8 bands)
        x = gt_log.bin(nbins=8, func='sum', dim='frequency')
        eelbrain.save.pickle(x, PREDICTOR_DIR / f'Set_B_HCD_{i}~gammatone-8.pickle')
        x = gt_on.bin(nbins=8, func='sum', dim='frequency')
        eelbrain.save.pickle(x, PREDICTOR_DIR / f'Set_B_HCD_{i}~gammatone-on-8.pickle')

    
    
    ## THE THIRD STEP ##  # from Alice/predictors/make_word_predictors.py
    """
    Generate predictors for word-level variables
    
    See the `explore_word_predictors.py` notebook for more background
    """
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
   """