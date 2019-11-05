# CheXNet-Labeler

## Introduction
 This tool is used to convert observations from multiple radiology reports into class labels and save them in a single `.csv` file. The `.csv` file will be used as input list for deep learning model study on chest X-ray disease classification. This tool is based on [CheXpert NLP tool](https://github.com/stanfordmlgroup/chexpert-labeler).

## Prerequisites
1. Clone the [NegBio repository](https://github.com/ncbi-nlp/NegBio):
    
    `git clone git@github.com:ncbi-nlp/NegBio.git`

2. Add the NegBio directory to your `PYTHONPATH`:
    
    `export PYTHONPATH={path to negbio directory}:$PYTHONPATH`

3. Make the virtual environment:
    
    `conda env create -f environment.yml`

4. Install NLTK data:
    
    `python -m nltk.downloader universal_tagset punkt wordnet`

5. Run `model_donwloader.py` to download the `GENIA+PubMed` parsing model.

## Usage
Run the following command to convert the multiple reports into a single `.csv` file. The input `reports_parent_path` should be a parent path that includes multiple subfolders. Each subfolder can have multiple radiology `.txt` reports. See `sample_reports.csv` as an example of a single report, and `MIMIC_data_test.csv` as an example of output `.csv` file with extracted labels of multiple reports.

`python label.py --reports_path reports_parent_path`


## Author
Viveak Ravichandiran (SUNet ID: vravicha), Aditya Srivastava(SUNet ID: adityaks), Ying Chen (SUNet ID: smileyc)