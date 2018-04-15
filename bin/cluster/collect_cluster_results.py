""" A short helper script that collects the results of the cluster jobs and format them correctly as CSV. """
import sys

import os


def main():
    # Directory with the cluster output
    cluster_output = sys.argv[1] + ('' if sys.argv[1][-1] == '/' else '/')

    # Determine columns.
    argument_columns = ['task', 'model', 'oneHotEncoding',
                        'mlpLayers', 'mlpWidth', 'mlpDropout', 'mlpEpochs',
                        'mlpEmbNeurons', 'logrC']
    result_columns = ['auc', 'f1', 'acc', 'set']
    test_results_columns = ['test_' + c for c in result_columns]

    print('folder', end=',')
    print(','.join(argument_columns), end=',')
    print(','.join(result_columns), end=',')
    print(','.join(test_results_columns), end=',')
    print('auc+f1')

    scores = []
    for output_dir in os.listdir(cluster_output):
        # Now inside a dingle run output.

        # Read in arguments.
        arguments = {}
        arguments_path = cluster_output + output_dir + '/arguments.txt'
        if os.path.isfile(arguments_path):
            with open(arguments_path, 'r') as cluster_output_arguments:
                for line in cluster_output_arguments:
                    line = line.rstrip()

                    if ":" not in line:
                        continue
                    if line.startswith("#"):
                        continue

                    k, v = line.split(":", 1)
                    arguments[k.strip()] = v.strip()

        # Read in results.
        valid_results = {}
        validate_path = cluster_output + output_dir + '/results_validate.txt'
        if os.path.isfile(validate_path):
            with open(validate_path, 'r') as cluster_output_results:
                for line in cluster_output_results:
                    line = line.rstrip()

                    if "=" not in line:
                        continue
                    if line.startswith("#"):
                        continue

                    k, v = line.split("=", 1)
                    valid_results[k.strip()] = v.strip()

        # Read in test results.
        test_results = {}
        test_path = cluster_output + output_dir + '/results_test.txt'
        if os.path.isfile(test_path):
            with open(test_path, 'r') as cluster_output_results:
                for line in cluster_output_results:
                    line = line.rstrip()

                    if "=" not in line:
                        continue
                    if line.startswith("#"):
                        continue

                    k, v = line.split("=", 1)
                    test_results[k.strip()] = v.strip()

        # Build value column
        line = ''
        line += output_dir + ','

        for arg in argument_columns:
            line += (arguments[arg] if arg in arguments else '') + ','

        for res in result_columns:
            line += (valid_results[res] if res in valid_results else '') + ','

        for res in result_columns:
            line += (test_results[res] if res in test_results else '') + ','

        auc = float(valid_results['auc'] if 'auc' in valid_results else '-10')
        f1 = float(valid_results['f1'] if 'f1' in valid_results else '-10')
        scores.append((line, auc + f1))

    scores.sort(key=lambda x: x[1], reverse=True)

    for (line, score) in scores:
        print(line + str(score))


if __name__ == "__main__":
    main()
