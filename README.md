# Playing with TensorFlow Lite for Microcontrollers on the ESP32

The voice recognition is carried out using a model trained with TensorFlow and runs on the ESP32 using TensorFlow Lite. A pre-trained model is included in the Firmware folder so you can get up and running straight away.

There are two folders in this repo `model` and `firmware` check the `README.md` file in each one for complete details.

## Audio input

I created my own mediocre Mic, 

Schematics: TODO

## Model

Jupyter notebooks for creating a TensorFlow Lite model for "wake word" recognition.

A pre-trained model has already been generated and added to the firmware folder.

If you want to train your own, I added a couple of extra folders to the training data they are available here:

## Firmware

~ESP32 firmware built using Platform.io. This runs the neural network trying to detect the words `Left`, `Right`, `Forward` and `Backward`.~

Commands: ```yes, off, left, right```

Left and right navigate between LEDs, and Yes turns the LED ON, whilst Off turns it off.
