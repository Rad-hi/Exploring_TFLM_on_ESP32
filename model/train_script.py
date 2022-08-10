'''
This script loads the dataset (generated using the prepare_the_dataset/data_generator.py script),
trains the model, and then saves it as a .model file, and finally tests the model on the test data.
'''
import tensorflow as tf
import numpy as np
from tensorflow import keras
from tensorflow.keras import regularizers
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Conv2D, Flatten, Dropout, MaxPooling2D

from tensorflow.io import gfile
import random


CLASSES_DATASET_PATH = "/home/Radhi/Desktop/TinyML_Book/voice-controlled-robot/model/speech_data_classes_npy"
MODEL_SAVE_PATH = 'trained.model'

# These must be the same as the ones used to split the data into classes in the data generator script
model_classes = [
    'yes',
    'off',
    'left',
    'right',
    '_invalid',
]

BATCH_SIZE  = 32
IMG_WIDTH   = 99
IMG_HEIGHT  = 43

# The whole dataset will be (shuffled) split into 3 sub-sets, choose your ratios 
TRAIN_RATIO = 0.80
VALID_RATIO = 0.15
TEST_RATIO  = 0.05

# Utils to load the data
def get_spectr_files(source, word):
    return gfile.glob(source + '/'+word+'/*.npy')

# Ref: https://medium.com/analytics-vidhya/write-your-own-custom-data-generator-for-tensorflow-keras-1252b64e41c3
class CustomDataGen(tf.keras.utils.Sequence):
    
    def __init__(self, files_list,
                 output_classes,
                 batch_size=32,
                 input_size=(99, 43, 1),
                 shuffle=True):
        
        self.output_classes = output_classes
        self.files_list = files_list
        self.batch_size = batch_size
        self.input_size = input_size
        self.shuffle = shuffle
        
        self.n = len(self.files_list)
    

    def on_epoch_end(self):
        if self.shuffle:
            random.shuffle(self.files_list)

    def __get_data(self, file):
        # data/yes/yes_0_3.npy --> ['yes', 'yes_0_3.npy'] --> 'yes'
        y_str = file.split('/')[-2:][0]
        y = self.output_classes.index(y_str)
        return (np.load(file), y)
    
    def __getitem__(self, index):
        X = []
        y = []
        for file in self.files_list[index : index+self.batch_size]:
            spectr, label = self.__get_data(file)
            X.append(spectr)
            y.append(label)
        
        return (np.array(X), np.array(y))
    
    def __len__(self):
        return self.n // self.batch_size

print("=== Collecting spectrograms' (.npy) files ===")
files_list = []
for word in model_classes:
    files_list = files_list + [file for file in get_spectr_files(CLASSES_DATASET_PATH, word)]
print(f'Found {len(files_list)} files!')
random.shuffle(files_list)

dataset_len = len(files_list)
train_len = int(dataset_len*TRAIN_RATIO)
valid_len = int(dataset_len*VALID_RATIO)
test_len  = int(dataset_len*TEST_RATIO)
print(f'%80 of files for Training: {train_len}')
print(f'%10 of files for Validation: {valid_len}')
print(f'%10 of files for Testing: {test_len}')

traingen = CustomDataGen(files_list[:train_len],
                         model_classes,
                         batch_size=BATCH_SIZE,
                         input_size=(IMG_WIDTH, IMG_HEIGHT, 1))

validgen = CustomDataGen(files_list[train_len:train_len+valid_len],
                         model_classes,
                         batch_size=BATCH_SIZE,
                         input_size=(IMG_WIDTH, IMG_HEIGHT, 1))

model = Sequential([
    Conv2D(4, 3, 
           padding='same',
           activation='relu',
           kernel_regularizer=regularizers.l2(0.001),
           name='conv_layer1',
           input_shape=(IMG_WIDTH, IMG_HEIGHT, 1)
           ),
    MaxPooling2D(name='max_pooling1', pool_size=(2,2)),
    Conv2D(4, 3, 
           padding='same',
           activation='relu',
           kernel_regularizer=regularizers.l2(0.001),
           name='conv_layer2'),
    MaxPooling2D(name='max_pooling2', pool_size=(2,2)),
    Flatten(),
    Dropout(0.1),
    Dense(
        80,
        activation='relu',
        kernel_regularizer=regularizers.l2(0.001),
        name='hidden_layer1'
    ),
    Dropout(0.1),
    Dense(
        len(model_classes), 
        activation='softmax',
        kernel_regularizer=regularizers.l2(0.001),
        name='output'
    )
])

epochs=10
model.compile(optimizer='adam',
              loss=keras.losses.SparseCategoricalCrossentropy(),
              metrics=['accuracy'])


print("=== Training the model ===")

history = model.fit(
    traingen,
    epochs=epochs,
    validation_data=validgen
)

print('=== Saving the model ===')

model.save(MODEL_SAVE_PATH)


print("=== Testing the model ===")

testgen = CustomDataGen(files_list[train_len+valid_len:],
                        model_classes,
                        batch_size=BATCH_SIZE,
                        input_size=(IMG_WIDTH, IMG_HEIGHT, 1))

# Fill data
test_spectr = []
test_labels = []

for spectro, label in testgen:
  for im, lbl in zip(spectro, label):
    test_spectr.append(im)
    test_labels.append(lbl)

test_spectr = np.array(test_spectr)
test_labels = np.array(test_labels)

results = model.evaluate(test_spectr, test_labels, batch_size=128)