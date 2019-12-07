"""Entry-point script to label radiology reports."""
import pandas as pd
import os

from args import ArgParser
from loader import Loader
from stages import Extractor, Classifier, Aggregator
from constants import *
import pydicom as dicom
import cv2
import numpy as np
import csv
import time
from image_crop_resize import crop_resize_img
import string


def write(reports, labels, output_path, verbose=False):
    """Write labeled reports to specified path."""
    labeled_reports = pd.DataFrame({REPORTS: reports})
    for index, category in enumerate(CATEGORIES):
        labeled_reports[category] = labels[:, index]

    if verbose:
        print(f"Writing reports and labels to {output_path}.")
    labeled_reports[[REPORTS] + CATEGORIES].to_csv(output_path,
                                                   index=False)
    return labeled_reports[[REPORTS] + CATEGORIES]


def label(single_report_path, extract_impression, extractor, classifier, aggregator):
    """Label the provided report(s)."""

    loader = Loader(single_report_path, extract_impression)

    # Load reports in place.
    loader.load()
    # Extract observation mentions in place.
    extractor.extract(loader.collection)
    # Classify mentions in place.
    classifier.classify(loader.collection)
    # Aggregate mentions to obtain one set of labels for each report.
    labels = aggregator.aggregate(loader.collection)
    
    return loader.reports, labels


def get_single_report_frame(mined_report, dcm_png, files):
    mined_report = mined_report.replace(-1.0, 0.0)
    mined_report_combined = mined_report.any().astype('int')
    mined_report_combined['No Finding'] = mined_report['No Finding'].all().astype('int')
    mined_report_combined['Image Index'] = dcm_png
    mined_report_combined['Patient ID'] = files                    
    label_concat = ''
    for single_label in CATEGORIES:
        if mined_report_combined[single_label]:
            current_label = single_label
            if current_label == 'Pleural Effusion':
                current_label = 'Effusion'
            if label_concat:
                label_concat = '{}|{}'.format(label_concat, current_label)
            else:
                label_concat = current_label
    if not label_concat:
        mined_report_combined['No Finding'] = 1
        label_concat = 'No Finding'
    mined_report_combined['Finding Labels'] = label_concat
    mined_report_combined = mined_report_combined.drop(labels='No Finding')
    return mined_report_combined


def report_merge_line(r_file, out_file):
    new_line = []
    with open(r_file, 'r') as fp:
        lines = fp.readlines()
        for l in lines:
            words = [word.strip(string.punctuation) for word in l.split()]
            # If current line has capital letter of the first world, then add " at the end of previous line.
            # Also add " at the beginning of current line.
            if len(words) > 0:
                if len(words[0]) > 0:
                    if words[0][0].isupper():
                        if len(new_line) > 0:
                            new_line_content = new_line[-1].split('\n')
                            new_line[-1] = new_line_content[0] + '"' + '\n'
                            new_line.append('"' + l)
                        else:
                            new_line.append('"' + l)
                    else:
                        new_line.append(l)
        fp.close()
    # Add the last " in the last line with valid content.
    for i in range(len(new_line)):
        new_line_content = new_line[-1 - i].split('\n')[0]
        if len(new_line_content) > 0 and new_line_content[-1] != '"':
            new_line[-1 - i] = new_line_content + '"' + '\n'
            break
            
    with open(out_file, 'w') as fp:
        for l in new_line:
            fp.write(l)
        fp.close()
        
        
def output_final_report(all_reports, out_csv):
    # Save all the extracted results in the .csv file. Remove 'No Finding' - the first one in CATEGORIES.
    all_reports_save = all_reports.transpose()[['Image Index', 'Patient ID', 'Finding Labels'] + CATEGORIES[1:]]
    all_reports_save = all_reports_save.rename(columns={'Pleural Effusion': 'Effusion'})
    all_reports_save.insert(6, 'Infiltration', 0)
    all_reports_save.insert(7, 'Mass', 0)
    all_reports_save.insert(8, 'Nodule', 0)
    all_reports_save.insert(13, 'Emphysema', 0)
    all_reports_save.insert(14, 'Fibrosis', 0)
    all_reports_save.insert(15, 'Pleural_Thickening', 0)
    all_reports_save.insert(16, 'Hernia', 0)
    all_reports_save.to_csv(out_csv, index=False)
    

if __name__ == "__main__":
    # Initilize the parameters
    start = time.time()
    parser = ArgParser()
    args = parser.parse_args()
    extractor = Extractor(args.mention_phrases_dir,
                          args.unmention_phrases_dir,
                          verbose=args.verbose)
    classifier = Classifier(args.pre_negation_uncertainty_path,
                            args.negation_path,
                            args.post_negation_uncertainty_path,
                            verbose=args.verbose)
    aggregator = Aggregator(CATEGORIES,
                            verbose=args.verbose)
    
    out_file = 'test_report.txt'
    c = 0
    all_reports = pd.DataFrame()
    # Loop through the path to get the dir of subfolder
    # reports_path = 'MIMIC/dataset/files/p10'
    b = 0
    for files in sorted(os.listdir(args.reports_path)):
        c0 = 0
        # Example sub_path = 'MIMIC/dataset/files/p10/p10000764'
        sub_path = os.path.join(args.reports_path, files)
        if os.path.isdir(sub_path):
            # Convert the text file in each subfolder into csv file that is used in CheXNet format.
            for sub_files in sorted(os.listdir(sub_path)):
                # Currently just try 1500 images.
                # [TODO: Extract labels of all the images.]
                # Example sub_files is 'MIMIC/dataset/files/p10/p10000764/s57375967' or 's57375967.txt'
                single_report_path = os.path.join(sub_path, sub_files)
                if os.path.isdir(single_report_path):
                    for dcm in sorted(os.listdir(single_report_path)):
                        if dcm.endswith('dcm'):
                            dcm_file_dir = os.path.join(single_report_path, dcm)
                            dcm_png = dcm.replace('.dcm', '.png')
                            ds = dicom.dcmread(dcm_file_dir, specific_tags=['ViewPosition'])
                            report_file = '{}.{}'.format(single_report_path, 'txt')
                            if os.path.exists(report_file):
                                report_merge_line(report_file, out_file)
                            else:
                                continue
                            if ds.data_element('ViewPosition').value == 'PA':
                                ds = dicom.dcmread(dcm_file_dir)
                                pixel_array_numpy = np.uint8(ds.pixel_array / float(ds.pixel_array.max() + 1)* 255)
                                img_resize = crop_resize_img(pixel_array_numpy)
                                cv2.imwrite(os.path.join('MIMIC_images_crop_1201', dcm_png), img_resize)
                                reports, labels = label(out_file, args.extract_impression, extractor, classifier, aggregator)
                                output_path = os.path.join('MIMIC_mined_report', '{}_{}.{}'.format(sub_files, 'report', 'csv'))
                                mined_report = write(reports, labels, output_path, verbose=False).fillna(0)
                                mined_report_combined = get_single_report_frame(mined_report, dcm_png, files)
                                all_reports = pd.concat([all_reports, mined_report_combined], axis=1)                    
                                c += 1 
                                c0 += 1
                                if c0 == 1:   
                                    break
                    if c0 == 1:
                        break

            if c % 5 == 0 and c > 0:
                print("it took", time.time() - start, "seconds.")
                print('layer4 :')
                print(c)
                print(b)
                output_final_report(all_reports, 'MIMIC_data_test_1204_p14.csv')
        b += 1
    
