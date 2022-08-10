# How to train a command word detection model for the ESP32

Your first step would be to generate the dataset.
Now the problem that I faced with how [atomic14](github.com/atomic14) approached this, is that they generate all spectrograms in memory and then suhffles it and saves it as npz (numpy compressed files). I only have 4Gb of RAM on my laptop, and the data is just bigger, so I had to come up with a way to not load everything into memory. Another problem (before we move on to how I solved these problems) is that his scripts are too static for the sake of his own application (can't blame him, it's his code after all and I'm grateful he shared it), more specifically, if I wanted to train a new model with new keywords (which I did) I couldn't simply tweak the scripts to do so.
So what I did is:

- Generate a new dataset comprised of .npy files containing the spectrograms of each .wav file (maintaining the structure of the original dataset)

- Allow for a list to be modified (model_classes) that defines the classes the model will train on (the script reads this list and copies files accordingly)

## Generate Training Data.pynb

We make use of the speech commands dataset available from here:

[https://storage.cloud.google.com/download.tensorflow.org/data/speech_commands_v0.02.tar.gz](https://storage.cloud.google.com/download.tensorflow.org/data/speech_commands_v0.02.tar.gz)

Download and expand the data using:

```
tar -xzf data_speech_commands_v0.02.tar.gz -C speech_data
```

For my training, I add a lot more data to the `_background_noise_` folder. I also created a `_problem_noise_` folder and recorded sounds that seemed to confuse the model - low frequency humming noises around 100Hz seem to cause problems.

You can get this data from here:

* [\_background\_noise.zip](https://data.atomic14.com/_background_noise_.zip)
* [\_problem_noise\_.zip](https://data.atomic14.com/_problem_noise_.zip)

The notebook will run through all these samples and output files for the training step. You will need about 15GB of free space to save these files.

## Train Model.ipynb

This will train a model against the training data. This will train on a CPU in 2-3 hours. If you have a suitable GPU this training will be considerably faster.

The training will output ~a file called `checkpoint.model` every time is sees an improvement in the validation performance and~ a file called `trained.model` on training completion.

You can optionally take these and train them on the complete dataset.

The ```train_script.py``` takes in the dataset and generates a suitable dataset that's consumed from disk, not loaded entirely into RAM, saves the model once done, and prints the testing accuracy.

## Convert Trained Model To TFLite.ipynb

This will take the TensorFlow model and convert it for use in TensorFlow lite.

Copy the output of this workbook into `firmware/lib/nerual_network/model.cc`.

A pre-trained model has already been generated and placed in that location.
