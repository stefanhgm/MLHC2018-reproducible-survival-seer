import keras.models
from keras.layers import Dense, Dropout, Input, Conv1D, Concatenate, Flatten
from keras.utils.vis_utils import plot_model
import logging

from sklearn.dummy import DummyRegressor, DummyClassifier
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.svm import SVC, SVR


class Model:
    """ Class that encapsulates the machine learning model and related functions. """

    def __init__(self, model_type, task, input_dim, encodings, mlp_layers, mlp_width, mlp_dropout, mlp_emb_neurons,
                 svm_gamma, svm_c, logr_c):
        self.model_type = model_type
        if model_type == 'MLP':
            self.model = mlp_model(input_dim=input_dim, width=mlp_width, depth=mlp_layers,
                                   dropout=mlp_dropout, binary=(task not in ['mort12', 'mort60']))
        elif model_type == 'MLPEmb':
            self.model = mlp_emb_model(input_dim=input_dim, width=mlp_width, depth=mlp_layers,
                                       dropout=mlp_dropout, binary=(task not in ['mort12', 'mort60']),
                                       encodings=encodings, emb_neurons=mlp_emb_neurons)
        elif model_type == 'SVM':
            # Gamma parameter can also be a string
            if task in ['mort12', 'mort60']:
                self.model = SVR(verbose=True, gamma=('auto' if svm_gamma == 'auto' else float(svm_gamma)), C=svm_c)
            elif task in ['survival12', 'survival60']:
                self.model = SVC(verbose=True, gamma=('auto' if svm_gamma == 'auto' else float(svm_gamma)), C=svm_c)
        elif model_type == 'LogR' and task in ['survival12', 'survival60']:
            self.model = LogisticRegression(C=logr_c)
        elif model_type == 'LinR' and task in ['mort12', 'mort60']:
            self.model = LinearRegression()
        elif model_type == 'NAIVE':
            if task in ['mort12', 'mort60']:
                self.model = DummyRegressor(strategy='mean')
            elif task in ['survival12', 'survival60']:
                self.model = DummyClassifier(strategy='most_frequent')
        else:
            logging.error('Invalid model.')
            exit(-1)

    def plot_model(self, output_directory):
        if self.model_type in ['MLP', 'MLPEmb']:
            plot_model(self.model, to_file=output_directory + 'model.png')


def mlp_compile(model, binary):
    """ Compile method for all MLP* models. """
    if binary:
        model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    else:
        model.compile(loss='mean_squared_error', optimizer='adam', metrics=['mae'])

    return model


def mlp_model(input_dim, width, depth, dropout, binary):
    """ Function to create the MLP model. """
    model = keras.models.Sequential()

    for i in range(0, depth):
        model.add(Dense(units=width, input_dim=input_dim, kernel_initializer='normal', activation='relu'))
        model.add(Dropout(dropout))

    if binary:
        model.add(Dense(1, kernel_initializer='normal', activation='sigmoid'))
    else:
        model.add(Dense(1, kernel_initializer='normal'))

    model = mlp_compile(model, binary)
    return model


def mlp_emb_model(input_dim, width, depth, dropout, binary, encodings, emb_neurons):
    """ Function to create MLP model with embedding layer for encoded inputs. """

    if input_dim != sum(encodings.values()):
        logging.error("Bad encoding: " + str(input_dim) + " vs. " + str(sum(encodings.values())))
        exit(1)

    # Embedding layer per encoding
    embeddings = []
    inputs = []
    for encoding in encodings.values():
        input_segment = Input(shape=(encoding, 1))
        embeddings.append(Dropout(dropout)(Conv1D(emb_neurons, encoding)(input_segment)))
        inputs.append(input_segment)
    tensors = Concatenate(axis=-1)(embeddings)
    tensors = Flatten()(tensors)

    # Additional feedforward layers
    for i in range(0, depth - 1):
        tensors = Dense(width, kernel_initializer='normal', activation='relu')(tensors)
        tensors = Dropout(dropout)(tensors)

    # Output layer
    if binary:
        predictions = Dense(1, kernel_initializer='normal', activation='sigmoid')(tensors)
    else:
        predictions = Dense(1, kernel_initializer='normal')(tensors)

    model = keras.models.Model(inputs=inputs, outputs=predictions)

    model = mlp_compile(model, binary)
    return model
