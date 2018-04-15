import argparse


def parseargs():
    """ A method to parse all necessary command line arguments. """
    parser = argparse.ArgumentParser()

    # Output
    parser.add_argument('-out', '--output', required=False, default='.',
                        help='Output directory for the results folder.')

    # SEER data files
    parser.add_argument('-inc', '--incidences', required=True,
                        help='SEER incidences TXT file (e.g. RESPIR.TXT).')
    parser.add_argument('-spec', '--specifications', required=True,
                        help='SEER sas field specifications (e.g. read.seer.research.nov16.sas).')
    parser.add_argument('-cas', '--cases', required=True,
                        help='SEER*Stat matrix export csv file containing the fields Patient ID, Record number.')

    # Plots
    parser.add_argument('-plotData',  '--plotData', required=False, default=False, action='store_true',
                        help='Plot data descriptions and save them in the output directory.')
    parser.add_argument('-plotResults', '--plotResults', required=False, default=False, action='store_true',
                        help='Plot results and save them in the output directory.')

    # Task and data specific options
    parser.add_argument('-task', '--task', required=True, choices=['survival12', 'survival60', 'mort12', 'mort60'],
                        help='Select survival or mortality prediction for 12 or 60 months.')
    parser.add_argument('-ohe', '--oneHotEncoding',  required=False, default=False, action='store_true',
                        help='Option to encode categorical inputs and special codes for continuous variables '
                             'as one hot vectors.')
    parser.add_argument('-test', '--test', required=False, default=False, action='store_true',
                        help='Run validation on separate hold-out test data. Careful: do not use to tune model.')
    parser.add_argument('-imp', '--importance', required=False, default=False, action='store_true',
                        help='Analyse the importance of inputs. So far only for LinR/LogR and MLP* models.')

    parser.add_argument('-mod', '--model', required=True, choices=['LogR', 'LinR', 'SVM', 'MLP', 'MLPEmb', 'NAIVE'],
                        help='Model for recognition. MLPEmb is MLP with embedding of encoded features.')

    # Model specific options

    # LogR - Logistic Regression
    parser.add_argument('-logrC', '--logrC', required=False, type=float, default=1.0,
                        help='Regularization parameter for logistic regression.')

    # SVM
    parser.add_argument('-svmg', '--svmGamma', required=False, type=str, default='auto',
                        help='Gamma kernel coefficient for SVM.')
    parser.add_argument('-svmC', '--svmC', required=False, type=float, default=1.0,
                        help='Penalty parameter C of the error term for SVM.')

    # MLP/MLPEmb
    parser.add_argument('-lay', '--mlpLayers', required=False, type=int, default=1,
                        help='Number of layers for MLP*. For MLPEmb embedding counts as first layer.')
    parser.add_argument('-wid', '--mlpWidth', required=False, type=int, default=20,
                        help='Number of nodes/layer for MLP*. For MLPEmb, first layer width depends on number of' +
                             'embedding neurons.')
    parser.add_argument('-drop', '--mlpDropout', required=False, type=float, default=0.0,
                        help='Dropout for MLP* models.')
    parser.add_argument('-epo', '--mlpEpochs', required=False, type=int, default=20,
                        help='Epochs for MLP* models.')

    # MLPEmb
    parser.add_argument('-eneu', '--mlpEmbNeurons', required=False, type=int, default=3,
                        help='Number of neurons used for the embedding of the MLPEmb model.')

    args = parser.parse_args()

    return args
