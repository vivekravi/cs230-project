# ChexNet-CS230 Project
Install dependencies by running `pip3 install -r requirements.txt` at first.

## Introduction
ChexNet(https://arxiv.org/pdf/1711.05225.pdf) is a deep learning algorithm that can detect and categorize 14 kinds of diseases from chest X-ray images. As described in the paper, a 121-layer densely connected convolutional neural network is trained on ChestX-ray14 dataset, which contains 112,120 frontal view X-ray images from 30,805 unique patients.

The codes of implemented models were based on [Chou's work](https://github.com/brucechou1983/CheXNet-Keras). This project started from pre-trained weights in `data/default_split/best_weights.h5`. However, AUROC scores are very low as 0.5 for some classes. Then this pre-trained weights were used as the staring point for training dataset to update weights. After it, the AUROC scores were improved a lot.

## Train and Test Models
1. Modify parameters in `config.ini` to specify the output_dir for saving ouput results, image_source_dir for input path of images.
2. The retrained weights `data/default_split/best_weights_20191029_test2.h5` file.
3. Run `python train.py` to train a new model on the training dataset. 
4. Run `python test.py` to evaluate the model on the test dataset.

## Dataset
**Note that currently this project can only be executed in Linux and macOS. You might run into some issues in Windows.**
1. Currently [NIH dataset](https://nihcc.app.box.com/v/ChestXray-NIHCC) were added into `train.csv`, `dev.csv` and `test.csv` in `data/default_split` folder.
2. Another new dataset [MIMIC-CXR](https://physionet.org/content/mimic-cxr/2.0.0/) will be added. The X-ray report will be converted to the class labels for new train, dev and test dataset. 

## Author
Viveak Ravichandiran (SUNet ID: vravicha)
Aditya Srivastava(SUNet ID: adityaks)
Ying Chen (SUNet ID: smileyc)
