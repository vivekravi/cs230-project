"""Entry-point script to label radiology reports."""
import pandas as pd
import os

from args import ArgParser
from loader import Loader
from stages import Extractor, Classifier, Aggregator
from constants import *


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


if __name__ == "__main__":
    # Initilize the parameters
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
    
    c = 0
    all_reports = pd.DataFrame()
    # Loop through the path to get the dir of subfolder
    for files in sorted(os.listdir(args.reports_path)):
        sub_path = os.path.join(args.reports_path, files)
        if os.path.isdir(sub_path):
            # Convert the text file in each subfolder into csv file that is used in CheXNet format.
            for sub_files in sorted(os.listdir(sub_path)):
                # Currently just try 1500 images.
                # [TODO: Extract labels of all the images.]
                if sub_files.endswith('txt') and c < 1500:
                    single_report_path = os.path.join(sub_path, sub_files)
                    reports, labels = label(single_report_path, args.extract_impression, extractor, classifier, aggregator)
                    basename = os.path.basename(sub_files)
                    output_path = os.path.join(sub_path, '{}_{}.{}'.format(os.path.splitext(basename)[0], 'report', 'csv'))
                    mined_report = write(reports, labels, output_path, verbose=False).fillna(0)
                    mined_report_combined = mined_report.any().astype('int')
                    mined_report_combined['No Finding'] = mined_report['No Finding'].all().astype('int')
                    mined_report_combined['Image Index'] = sub_files
                    mined_report_combined['Patient ID'] = files                    
                    label_concat = ''
                    for single_label in CATEGORIES:
                        if mined_report_combined[single_label]:
                            if label_concat:
                                label_concat = '{}|{}'.format(label_concat, single_label)
                            else:
                                label_concat = single_label
                    if not label_concat:
                        mined_report_combined['No Finding'] = 1
                        label_concat = 'No Finding'
                    mined_report_combined['Finding Labels'] = label_concat
                    all_reports = pd.concat([all_reports, mined_report_combined], axis=1)                    
                    c += 1
                    print(c)
    # Save all the extracted results in the .csv file.
    all_reports = all_reports.transpose()[['Image Index', 'Patient ID', 'Finding Labels'] + CATEGORIES]
    all_reports.to_csv('MIMIC_data_test.csv', index=False)
    
