# Final Project Python File
import numpy as np
import pandas as pd
import glob
import sys
import os
import librosa 
import matplotlib
import matplotlib.pyplot as plt
from sklearn import preprocessing
from sklearn import utils
#import librosa.display
import pydotplus
from IPython.display import Image 

from sklearn import tree, metrics
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, confusion_matrix, ConfusionMatrixDisplay
from scipy.signal import butter, filtfilt, find_peaks
from sklearn.tree import DecisionTreeClassifier,export_graphviz
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# using functions from the Assignment 4 code 

# extract features 
def extract_features(data):
    zero_crossings = librosa.feature.zero_crossing_rate(y=data)
    mfcc = librosa.feature.mfcc(y=data, sr=sample_rate)
    rootms = librosa.feature.rms(y=data)
    mel = librosa.feature.melspectrogram(y=data, sr=sample_rate)
    # might need more parameters?
    spectral_contrast = librosa.feature.spectral_contrast(y=data)
    # Average across columns (axis=1)
    zcr_avg = np.mean(zero_crossings, axis=1)
    # not sure if I need the mfcc part 
    mfcc_avg = np.mean(mfcc, axis=1)
    rms_avg = np.mean(rootms, axis=1) 
    mel_avg = np.mean(mel, axis=1)
    spc_avg = np.mean(spectral_contrast, axis=1)
 
    # Concatenate into single row 
    features = np.concatenate([zcr_avg, mfcc_avg, rms_avg, mel_avg, spc_avg])
    # Convert to dataframe and transpose it so that the shape is 1x150
    df = pd.DataFrame(features).T
    # create an array of the feature names 
    _, df_size = df.shape
    column_names = []
    for x in range(df_size):
        if (x == 0):
            column_names.append("Zero Crossings")
        elif (x > 0 and x < 21):
            column_names.append("mfcc")
        elif (x == 21):
            column_names.append("rootms")
        elif (x > 21 and x < 151):
            column_names.append("Mel Spectogram")
        else:
            column_names.append("Spectral Contrast")

    df.columns = column_names
    return df

#train decision tree 
# error because of lack of data here?
def train_random_forest(frames):
    # Use pandas iloc fn to extract the first 150 columns as features.
    # Careful about how the indexing works (cols start from 0)
    X = frames.iloc[: , 0:157]

    # Use pandas iloc function to extract the 157th column as the prediction target.
    y = frames.iloc[: , 157]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    Sound_rf = RandomForestClassifier()
    Sound_rf_model = Sound_rf.fit(X_train, y_train)
    importance_index = np.argmax(Sound_rf.feature_importances_)
    important_feature = Sound_rf.feature_names_in_[importance_index]
    Sound_rf_pred = Sound_rf_model.predict(X_test)
    print(classification_report(y_test, Sound_rf_pred, target_names=['Whispering', 'Talking', 'Not Speaking']))
    # Evaluate on test set
    acc = Sound_rf_model.score(X_test, y_test)
    Sound_rf_cm = confusion_matrix(y_test, Sound_rf_pred)
    print(Sound_rf_cm)
    print("Most Important Feature: " + important_feature)
    #access single decision tree 
    myTree = Sound_rf.estimators_[1]
    fig = plt.figure(figsize=(25, 20))
    _ = tree.plot_tree(myTree, feature_names=X.columns, class_names=['Whispering', 'Talking', 'Not Speaking'], filled=True)
    
    return Sound_rf_model, Sound_rf_cm, acc


# code to call it 
filenames = glob.glob("AudioFiles/*/*.wav")
frames = pd.DataFrame()
for filename in filenames:
   sound = filename.split('\\')[1]
   data, sample_rate = librosa.load(filename)
   # show the graph
   y_axis_limits = [-0.5, 0.5]
   # code to display the visuals 

   #plt.figure(figsize=(10, 4))
   #librosa.display.waveshow(data, sr=sample_rate, color="blue")
   #plt.ylim(y_axis_limits)

   feature_df = extract_features(data)
   sound_df = pd.DataFrame([sound])
   combined_df = pd.concat([feature_df, sound_df], axis = 1)
   frames = pd.concat([combined_df, frames])

Sound_rf_model, sound_rf_cm, acc = train_random_forest(frames)
display = ConfusionMatrixDisplay(sound_rf_cm)
display.plot()
plt.show()