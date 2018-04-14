import logging
import numpy as np
from sklearn import preprocessing
from sklearn.metrics import accuracy_score, mean_squared_error, f1_score, roc_auc_score, roc_curve, auc, \
    mean_absolute_error
from sklearn.model_selection import train_test_split
import matplotlib as mpl

mpl.use('Agg')
import matplotlib.pyplot as plt


class Datarama:
    """ Class for main functionality. """

    def __init__(self, data, model, task, valid_ratio, test_ratio, model_type, encodings, encode_categorical_inputs,
                 plot_results, output_directory):
        """ Initialize main functionality and split data according to given ratios. """
        self.model = model
        self.model_type = model_type
        self.task = task

        self.plot_results = plot_results
        self.output_directory = output_directory

        input_columns = list(data.frame)
        x, y = [], []
        if task in ['mort12', 'mort60']:
            n = int(task[-2:])
            input_columns.remove("Survival months")
            # inputs
            x = data.frame[input_columns].as_matrix().astype(np.float32)
            # labels
            y = data.frame["Survival months"].as_matrix().reshape((data.frame["Survival months"].as_matrix().shape[0],))
            # Survival month must be scaled explicitly by max_survival_month.
            # If scaling it with the max value and the max is smaller than 12 or 60, this leads to wrong labels.
            y = y / n
        elif task in ['survival12', 'survival60']:
            n = int(task[-2:])
            input_columns.remove("Survived cancer for " + str(n) + " months")
            # inputs
            x = data.frame[input_columns].as_matrix().astype(np.float32)
            # labels
            y = data.frame["Survived cancer for " + str(n) + " months"].as_matrix().reshape(
                (data.frame["Survived cancer for " + str(n) + " months"].as_matrix().shape[0],)).astype(np.int32)

        # Fix random state to obtain same sets across experiments
        self.train_x, self.test_x, self.train_y, self.test_y \
            = train_test_split(x, y, test_size=valid_ratio + test_ratio, shuffle=True, random_state=73)

        # Fix random state to obtain same sets across experiments
        self.valid_x, self.test_x, self.valid_y, self.test_y \
            = train_test_split(self.test_x, self.test_y, test_size=(test_ratio / (valid_ratio + test_ratio)),
                               shuffle=True, random_state=63)

        # Unique hash for set splits to ensure that same sets are used throughout experiments
        self.set_split_hash = hash(np.sum(self.train_x)) + hash(np.sum(self.train_y)) + hash(np.sum(self.valid_x))\
            + hash(np.sum(self.valid_y)) + hash(np.sum(self.test_x)) + hash(np.sum(self.test_y))

        # Normalize data
        if encode_categorical_inputs:
            # Only normalize continuous fields
            continuous_columns = [idc for idc, c in enumerate(list(data.frame)) if c.endswith(' continuous')]
            scaler = preprocessing.StandardScaler().fit(self.train_x[:, continuous_columns])
            self.train_x[:, continuous_columns] = scaler.transform(self.train_x[:, continuous_columns])
            self.valid_x[:, continuous_columns] = scaler.transform(self.valid_x[:, continuous_columns])
            self.test_x[:, continuous_columns] = scaler.transform(self.test_x[:, continuous_columns])
        else:
            # Normalize all fields
            scaler = preprocessing.StandardScaler().fit(self.train_x)
            self.train_x = scaler.transform(self.train_x)
            self.valid_x = scaler.transform(self.valid_x)
            self.test_x = scaler.transform(self.test_x)

        logging.info("Data:  " + str(data.frame.shape) + " -> x:" + str(x.shape) + ", y:" + str(y.shape))
        logging.info("Train: x:{0}, y:{1}".format(str(self.train_x.shape), str(self.train_y.shape)))
        logging.info("Valid: x:{0}, y:{1}".format(str(self.valid_x.shape), str(self.valid_y.shape)))
        logging.info("Test:  x:{0}, y:{1}".format(str(self.test_x.shape), str(self.test_y.shape)))

        # Split up the data into distinct inputs for each convolution
        if model_type == 'MLPConv':
            print("")
            logging.info("Embed input data.")
            encoding_splits = np.cumsum(list(encodings.values()))
            self.train_x = np.hsplit(self.train_x, encoding_splits)[:-1]
            self.train_x = [np.expand_dims(x, axis=2) for x in self.train_x]
            self.valid_x = np.hsplit(self.valid_x, encoding_splits)[:-1]
            self.valid_x = [np.expand_dims(x, axis=2) for x in self.valid_x]
            self.test_x = np.hsplit(self.test_x, encoding_splits)[:-1]
            self.test_x = [np.expand_dims(x, axis=2) for x in self.test_x]

    def train(self, mlp_epochs):
        """ Training procedure. """
        mlp_batch_size = 20

        if self.model_type in ['MLP', 'MLPConv']:
            self.model.model.fit(self.train_x, self.train_y, epochs=mlp_epochs, batch_size=mlp_batch_size, verbose=2,
                                 validation_data=(self.valid_x, self.valid_y))
        elif self.model_type in ['LogR', 'LinR', 'SVM', 'NAIVE']:
            self.model.model.fit(self.train_x, self.train_y)

    def validate(self):
        """ Validation evaluation wrapper. """
        print('Validation results: ', end='')
        return self.evaluate(self.valid_x, self.valid_y)

    def test(self):
        """ Testing evaluation wrapper. """
        print('Test results: ', end='')
        return self.evaluate(self.test_x, self.test_y)

    def evaluate(self, eval_x, eval_y):
        """ Generic evaluation method. """

        if self.task in ['survival12', 'survival60'] and (self.model_type == 'SVM' or self.model_type == 'LogR'):
            # Use decision function value as score
            # http://scikit-learn.org/stable/auto_examples/model_selection/plot_roc.html)
            scores_y = self.model.model.decision_function(eval_x)
        else:
            scores_y = self.model.model.predict(eval_x)

        measurements = []
        # Regression
        if self.task in ['mort12', 'mort60']:
            n = float(self.task[-2:])
            scaled_eval_y = eval_y * n
            scaled_scores_y = scores_y * n

            measurements.append('rmse = ' + str(np.sqrt(mean_squared_error(eval_y, scores_y))))
            measurements.append('srmse = ' + str(np.sqrt(mean_squared_error(scaled_eval_y, scaled_scores_y))))
            measurements.append('smae = ' + str(mean_absolute_error(scaled_eval_y, scaled_scores_y)))

            if self.plot_results:
                fig = plt.figure(dpi=200)
                self.plot_scatter(scaled_eval_y, scaled_scores_y, plt)
                fig.savefig(self.output_directory + 'scatter.png')

        # Classification
        elif self.task in ['survival12', 'survival60']:
            if self.model_type == 'SVM' or self.model_type == 'LogR':
                predict_y = self.model.model.predict(eval_x)
            else:
                predict_y = scores_y.round()

            measurements.append('auc = ' + str(roc_auc_score(eval_y, scores_y)))
            measurements.append('f1 = ' + str(f1_score(eval_y, predict_y)))
            measurements.append('acc = ' + str(accuracy_score(eval_y, predict_y)))

            if self.plot_results:
                fig = plt.figure(dpi=200)
                self.plot_roc(eval_y, scores_y, plt)
                fig.savefig(self.output_directory + 'roc.png')

        print(', '.join(measurements))
        return measurements

    def importance(self, encodings):
        """ Method that analyzes the importance of input variables for LogR/LinR and MLP* models. """
        importance = []

        if self.model_type in ['LogR', 'LinR'] and self.task in ['survival12', 'survival60']:
            # Use coefficients
            abs_coefficients = np.abs(self.model.model.coef_[0])
            i = 0
            for column, encoding_size in encodings.items():
                coefficient_sum = 0.
                for idx in range(i, i + encoding_size):
                    coefficient_sum += abs_coefficients[idx]
                i += encoding_size
                importance.append(coefficient_sum)
            importance = np.array(importance)

        if self.model_type in ['MLP', 'MLPConv'] and self.task in ['survival12', 'survival60']:
            # Ablate attributes and measure effect on output
            scores_y = self.model.model.predict(self.test_x)
            i = 0
            for column, encoding_size in encodings.items():
                ablated_test_x = self.test_x
                if self.model_type == 'MLP':
                    ablated_test_x[:, i:(i + encoding_size)] = 0
                    i += encoding_size
                elif self.model_type == 'MLPConv':
                    ablated_test_x[i][:, :] = 0
                    i += 1
                ablated_scores_y = self.model.model.predict(ablated_test_x)
                ablated_diff = np.sum(np.abs(scores_y - ablated_scores_y))
                importance.append(ablated_diff)

            importance = np.array(importance)

        # Normalize importance
        importance = importance / np.sum(importance)
        result = dict(zip([column for column, encoding_size in encodings.items()], importance))

        # Sort results
        result = [(k, result[k]) for k in sorted(result, key=result.get, reverse=True)]
        return result

    @staticmethod
    def plot_scatter(labels, predictions, plot):
        """ Method to plot a scatter plot of predictions vs labels """
        plot.scatter(labels, predictions)
        plot.xlabel('Labels')
        plot.ylabel('Predictions')
        plot.title('Labels vs predictions')

    @staticmethod
    def plot_roc(labels, scores, plot):
        """ Method to plot ROC curve from http://scikit-learn.org/stable/auto_examples/model_selection/plot_roc.html """
        fpr, tpr, _ = roc_curve(labels, scores)
        roc_auc = auc(fpr, tpr)

        lw = 2
        plot.plot(fpr, tpr, color='darkorange', lw=lw, label='ROC curve (area = %0.2f)' % roc_auc)
        plot.plot([0, 1], [0, 1], color='navy', lw=lw, linestyle='--')
        plot.xlim([0.0, 1.0])
        plot.ylim([0.0, 1.05])
        plot.xlabel('False Positive Rate')
        plot.ylabel('True Positive Rate')
        plot.title('Receiver operating characteristic example')
        plot.legend(loc="lower right")
