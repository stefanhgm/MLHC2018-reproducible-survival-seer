import logging
import datetime
import os
import random as rn
import numpy as np
from keras import backend as k
import tensorflow as tf

from lib import pipelines
from lib.data import Data
from lib.model import Model
from lib.options import parseargs
from lib.experiment import Experiment


def main():
    """ The main routine. """

    # Fix random seeds for reproducibility - these are themselves generated from random.org
    # From https://keras.io/getting-started/faq/#how-can-i-obtain-reproducible-results-using-keras-during-development
    os.environ['PYTHONHASHSEED'] = '0'
    np.random.seed(91)
    rn.seed(95)
    session_conf = tf.ConfigProto(intra_op_parallelism_threads=1, inter_op_parallelism_threads=1)
    tf.set_random_seed(47)
    sess = tf.Session(graph=tf.get_default_graph(), config=session_conf)
    k.set_session(sess)

    # Enable simple logging
    logging.basicConfig(level=logging.INFO, format='%(message)s')

    # Parse command line arguments
    args = parseargs()

    # Create run folder
    output_directory = create_output_folder(args.output)

    # Write arguments to file
    with open(output_directory + 'arguments.txt', 'a') as arguments_file:
        for arg in vars(args):
            arguments_file.write(str(arg) + ': ' + str(getattr(args, arg)) + '\n')

    ##############
    # Prepare data
    print('')
    data = Data(incidences_file=args.incidences, specifications_file=args.specifications, plot_data=args.plotData,
                output_directory=output_directory)
    data.state(message='Raw data')

    data.filter_cases(cases_file=args.cases)
    data.state(message='Filtered SEER*Stat cases from ASCII')

    # Determine inputs, filter, and pre process them
    data.apply_data_pipeline(pipelines.data_pipeline_full, args.oneHotEncoding)
    data.state(message='Remove irrelevant, combined, post-diagnosis, and treatment attributes')

    data.create_target(args.task)
    data.state(message='Create target label indicating cancer survival for ' + args.task)

    encodings = data.finalize()
    data.state(message='Remove inputs with constant values')

    ###############
    # Prepare model
    model = Model(model_type=args.model, task=args.task, input_dim=(len(data.frame.columns) - 1),
                  encodings=encodings, mlp_layers=args.mlpLayers, mlp_width=args.mlpWidth,
                  mlp_dropout=args.mlpDropout, mlp_conv_neurons=args.mlpConvNeurons,
                  svm_gamma=args.svmGamma, svm_c=args.svmC, logr_c=args.logrC)

    if args.plotData:
        model.plot_model(output_directory)

    ################
    # Carry out task
    experiment = Experiment(model=model, data=data, task=args.task, valid_ratio=0.1, test_ratio=0.1,
                          model_type=args.model, encodings=encodings, encode_categorical_inputs=args.oneHotEncoding,
                          plot_results=args.plotResults, output_directory=output_directory)

    experiment.train(mlp_epochs=args.mlpEpochs)

    results_validate = experiment.validate()
    # Write validation results to file
    with open(output_directory + 'results_validate.txt', 'a') as results_file:
        for res in results_validate:
            results_file.write(res + '\n')

    # Only test final model, do not use for tuning
    if args.test:
        results_test = experiment.test()
        # Write validation results to file
        with open(output_directory + 'results_test.txt', 'a') as results_file:
            for res in results_test:
                results_file.write(res + '\n')

    ###################
    # Input importance
    if args.importance:
        importance = experiment.importance(encodings=encodings)
        # Write importance results to file
        with open(output_directory + 'results_importance.txt', 'a') as results_file:
            for (column, rel) in importance:
                results_file.write(column + '=' + str(rel) + '\n')


def create_output_folder(output):
    """ Create a unique output folder. """
    now = datetime.datetime.now()
    run_folder_name = ('{0}-{1}-{2}_{3}-{4}-{5}_experiment'.format(str(now.year), str(now.month), str(now.day),
                                                                   str(now.hour), str(now.minute), str(now.second)))
    output_directory = output + ('' if output[-1] == '/' else '/') + run_folder_name

    i = 0
    while os.path.exists(output_directory + '-%s' % i):
        i += 1

    try:
        os.makedirs(output_directory + '-' + str(i))
    except FileExistsError:
        # Race condition: other process created directory - just try again (recursion should not go to deep here)
        return create_output_folder(output)

    return output_directory + '-' + str(i) + '/'


if __name__ == "__main__":
    main()
