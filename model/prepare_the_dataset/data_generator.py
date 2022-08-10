'''
This is a hacked together script to generate a dataset of numpy arrays
representing spectrograms as .npy files.
This dataset shall be fed to the model through the use of the custom 
DataGenerator class.
'''
from wav_2_spectr_utils import *

import os
from time import time
import shutil

# Datasets' folders
WAV_DATASET_PATH = "/home/Radhi/Desktop/TinyML_Book/voice-controlled-robot/model/speech_data"
NPY_DATASET_PATH = "/home/Radhi/Desktop/TinyML_Book/voice-controlled-robot/model/speech_data_npy_arrays"
CLASSES_DATASET_PATH = "/home/Radhi/Desktop/TinyML_Book/voice-controlled-robot/model/speech_data_classes_npy"

# Only needs to be done once (generate pictures once)
GENERATE_WORDS                 = False # Takes around 1h
GENERATE_BACKGROUND_NOISE_DATA = False 
GENERATE_PROBLEM_NOISE_DATA    = False 

# To prepare the data for training the model
SPLIT_DATASET_INTO_CLASSES     = True

# We don't have as many data images as invalid data, so we reapeat images
REPEAT_IMAGES = 10

# Folders containing random noises that enhance the model's performance
BACKGROUND_DATA_FOLDER = '_background_noise_'
PROBLEM_NOISE_DATA_FOLDER = '_problem_noise_'

# List of all available words in the dataset
keywords = [
    'yes',
    'off',
    'up',
    'down',
    'sheila',
    'stop',
    'go',
    'on',
    'forward',
    'backward',
    'left',
    'right',
    'learn',
    'no',
    'zero',
    'one',
    'two',
    'three',
    'four',
    'five',
    'six',
    'seven',
    'eight',
    'nine',
    'follow',
    'tree',
    'bed',
    'bird',
    'cat',
    'dog',
    'happy',
    'house',
    'marvin',
    'visual',
    'wow',
]

# The classes the model will classify
model_classes = [
    'yes',
    'off',
    'left',
    'right',

    # Keep the _invalid one always last
    '_invalid',
]

# The words that make up the _invalid class
invalid_class = [word for word in keywords if word not in model_classes] \
              + [BACKGROUND_DATA_FOLDER, PROBLEM_NOISE_DATA_FOLDER]

# Decorator to time functions
def time_me(func, *args):
    def inner(*args):
        start = time()
        func(*args)
        seconds = time() - start
        print(f"*** Ran in: {(int(seconds/3600))}h, {int((seconds%3600)/60)}m, and {int((seconds%3600)%60)}s ***")
    return inner

@time_me
def main():

    set_speech_data_folder(WAV_DATASET_PATH)

    if GENERATE_WORDS:
        print(f'### GENRATING WORDS SPECTROGRAMS ###\n')

        for idx, word in enumerate(keywords):
            print(f"=== Processing: Word <{word}> N°{idx+1}%{len(keywords)} ===")
            
            out_dir_path = os.path.join(NPY_DATASET_PATH, word)
            os.makedirs(out_dir_path, exist_ok=True)

            print(f"--- Getting files list for word <{word}> ---")
            files_list = get_files_list_for_word(word)
            print(f"--- Done. Found {len(files_list)} valid files! ---")

            print(f"--- Generating spectrograms for word <{word}> ---")
            for idx, file in enumerate(files_list):
                out_path = os.path.join(out_dir_path, str(idx)+'.npy')
                wav_2_numpy_npy(file, out_path)
    else:
        print("### WILL NOT GENERATE WORDS SPECTROGRAMS -- FLAG IS FALSE ###")
    
    if GENERATE_BACKGROUND_NOISE_DATA:
        print(f'### GENRATING BACKGROUND NOISE SPECTROGRAMS ###\n')

        print(f"--- Getting files list for <{BACKGROUND_DATA_FOLDER}> ---")
        files_list = get_wav_files(BACKGROUND_DATA_FOLDER)
        print(f"--- Done. Found {len(files_list)} files! ---")

        save_folder = os.path.join(NPY_DATASET_PATH, BACKGROUND_DATA_FOLDER)
        os.makedirs(save_folder, exist_ok=True)
        for file in files_list:
            generate_background_data(file, save_folder)
    else:
        print("### WILL NOT GENERATE BACKGROUND NOISE SPECTROGRAMS -- FLAG IS FALSE ###")

    if GENERATE_PROBLEM_NOISE_DATA:
        print(f'### GENRATING PROBLEM NOISE SPECTROGRAMS ###\n')
        
        print(f"--- Getting files list for <{PROBLEM_NOISE_DATA_FOLDER}> ---")
        files_list = get_wav_files(PROBLEM_NOISE_DATA_FOLDER)
        print(f"--- Done. Found {len(files_list)} files! ---")

        save_folder = os.path.join(NPY_DATASET_PATH, PROBLEM_NOISE_DATA_FOLDER)
        os.makedirs(save_folder, exist_ok=True)
        for file in files_list:
            generate_problem_noise_data(file, save_folder)
    else:
        print("### WILL NOT GENERATE PROBLEM NOISE SPECTROGRAMS -- FLAG IS FALSE ###")

    if SPLIT_DATASET_INTO_CLASSES: 
        print("### COPYING THE DATA INTO CLASSES FOLDERS ###\n")

        print("--- Creating the folders ---")
        classes_folders = []
        # 1- Make the folder containing the folders for the classes
        for model_class in model_classes:
            folder_path = os.path.join(CLASSES_DATASET_PATH, model_class)
            classes_folders.append(folder_path)
            os.makedirs(folder_path , exist_ok=True)
        
        # Make a dictionary containing the "class:path" pairs  
        classes_folders = dict(zip(model_classes, classes_folders))

        # 2- copy the model classes as they are to the new destination
        for word_idx, word in enumerate(model_classes[:-1]): # Exclude the _invalid keyword

            print(f'--- Copying <{word}> data N°{word_idx+1}%{len(model_classes)-1} to its class folder ---')
            files_list = get_spectr_files(NPY_DATASET_PATH, word)
            for idx, file in enumerate(files_list):
                for i in range(REPEAT_IMAGES):
                    destination = os.path.join(classes_folders[word], f'{word}_{idx}_{i}.npy')
                    shutil.copy(file, destination)

        # 3- copy the files of each word into an _invalid folder
        # while renaming each file to its word (for debugging purposes)
        for word_idx, word in enumerate(invalid_class):
            files_list = get_spectr_files(NPY_DATASET_PATH, word)

            # Copy the file from its source to the _invalid folder with its name 
            # being the label + its index
            print(f'--- Copying <{word}> N°{word_idx+1}%{len(invalid_class)} data to <_invalid> class ---')
            for idx, file in enumerate(files_list):
                destination = os.path.join(classes_folders['_invalid'], f'{word}_{idx}.npy')
                shutil.copy(file, destination)

    print("### DONE GENERATING THE DATASET ###")

if __name__ == "__main__":
    main()
