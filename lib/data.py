import numpy as np
import pandas as pd
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from lib.seer import parse_incidences
import lib.filter_column as fc
import operator
import logging
from collections import OrderedDict


class Data:
    """ Class that encapsulates the data set and related functions. """

    def __init__(self, incidences_file, specifications_file, plot_data, output_directory):
        # Pandas frame for the data
        self.frame = parse_incidences(specifications_file, incidences_file)
        # Flag whether data shall be plotted
        self.plot_data = plot_data
        # Output directory for plots
        self.output_directory = output_directory
        # Embed categorical variables, initially simply number of inputs
        columns = self.frame.columns
        self.encodings = OrderedDict((c, 1) for c in columns)

    def state(self, message=''):
        """ Print the number of cases and features contained in the data along with a message. """
        logging.info(('%s: (%d; %d) cases and attributes' % (message, self.frame.shape[0], self.frame.shape[1])))

    def filter_cases(self, cases_file):
        """ Filter cases according to SEER*Stat matrix export and fields Patient ID, Record number."""

        cases_mask = []
        cases = pd.read_csv(cases_file)

        # Parse SEER Registry coding and store all cases in set for fast access
        cases_set = set()
        for idx, case in cases.iterrows():
            entry = (case['Patient ID'], case['Record number'])
            cases_set.add(entry)

        for idx, row in self.frame.iterrows():
            entry = (row['Patient ID'], row['Record number'])
            if entry in cases_set:
                cases_mask.append(False)
            else:
                cases_mask.append(True)

        cases_columns = np.arange(self.frame['Survival months'].size)[cases_mask]
        self.frame = self.frame.drop(cases_columns)
        # Refresh indices starting from zero
        self.frame = self.frame.set_index(np.arange(self.frame['Survival months'].size))

    def apply_data_pipeline(self, data_pipeline, encode_categorical_inputs):
        """ Process the given data according to the specified data pipeline. """

        specification = list(self.frame)
        pipeline_specification = [x[0] for x in data_pipeline]
        size_x, size_y = self.frame.shape

        # First remove all unnecessary columns from the data
        for spec in specification:
            if spec not in pipeline_specification:
                del self.frame[spec]
                self.encodings.pop(spec)
        specification = list(self.frame)

        # Add all additional columns from the pipeline to the data
        for pipeline_spec in pipeline_specification:
            if pipeline_spec not in specification:
                self.frame[pipeline_spec] = pd.Series(np.full(size_x, -1, dtype=np.int32), index=self.frame.index)
                self.encodings[pipeline_spec] = 1
        specification = list(self.frame)

        assert (len(list(pipeline_specification)) == len(specification))

        # Process all filters
        for pipeline_entry in data_pipeline:
            column, filters, _, _ = pipeline_entry
            for filter_function, args in filters:
                self.frame = filter_function(self.frame, column, *args, encode_inputs=encode_categorical_inputs,
                                             encodings=self.encodings)

        # Process all constraints
        for pipeline_entry in data_pipeline:
            column, _, constraints, _ = pipeline_entry
            for constraint, value in constraints:
                self.frame = fc.constraint(self.frame, column, constraint, value)

        # Process status remove
        for pipeline_entry in data_pipeline:
            column, _, _, status = pipeline_entry
            if status == 'remove':
                self.frame = fc.remove_column(self.frame, column)
                self.encodings.pop(column)

        if self.plot_data:
            fig = plt.figure(figsize=(8, int(len(self.frame.columns)/8)), dpi=200)
            self.heatmap_data(fig, "Output of non-encoded data pipeline", 1, 1, 1)
            fig.savefig(self.output_directory + 'data_non_encoded.png')

        if encode_categorical_inputs:
            # First determine and create total number of additional columns
            additional_columns_names = []
            for pipeline_entry in data_pipeline:
                column, _, _, status = pipeline_entry
                if status == 'categorical':
                    data_column = self.frame.loc[:, column]
                    unique_values = np.unique(data_column)
                    additional_columns_names += [column + ' ' + str(v) for v in unique_values]
                    self.encodings.pop(column)
                    self.encodings[column] = len(unique_values)

            additional_columns = np.zeros((self.frame.shape[0], len(additional_columns_names)), dtype=np.int32)
            # Now add the according values
            column_offset = 0
            for pipeline_entry in data_pipeline:
                column, _, _, status = pipeline_entry
                if status == 'categorical':
                    data_column = self.frame.loc[:, column]
                    unique_values = np.unique(data_column)

                    encoded_value_indices = [np.where(unique_values == v)[0][0] + column_offset for v in data_column]
                    additional_columns[np.arange(len(data_column)), encoded_value_indices] = 1
                    column_offset += len(unique_values)
                    del self.frame[column]

            self.frame = self.frame.join(pd.DataFrame(additional_columns, columns=additional_columns_names))

        if sum(self.encodings.values()) != (len(self.frame.columns)):
            logging.error("Bad encodings: " + str(len(self.frame.columns)) +
                          " vs. " + str(sum(self.encodings.values())))
            exit(1)

    def filter_start_date(self, date):
        """ A helper method to filter cases after a certain year. """
        self.frame = fc.constraint(self.frame, 'Year of diagnosis', operator.ge, date)

    def create_target(self, task):
        """ Create target variable according to the chosen task. """

        # Inputs relevant for target:
        # 'SEER cause of death classification'
        # 'Survival months'

        if task in ['mort12', 'mort60']:
            # SEER: The variable [...] will only indicate if a patient died from that particular cancer
            # (also before study cutoff).
            # SEER: If you want to determine if they died from ANY cancer (not necessarily the cancer in question), then
            # you should use the “Cause of death to SEER site recode” and specify any of the cancer causes of death.
            self.frame = fc.constraint(self.frame, 'SEER cause of death classification', operator.eq, 1)
            if task == 'mort12':
                self.frame = fc.constraint(self.frame, 'Survival months', operator.le, 12)
            elif task == 'mort60':
                self.frame = fc.constraint(self.frame, 'Survival months', operator.le, 60)

            # Remove target - from now on encodings only for inputs.
            self.encodings.pop('Survival months')

        elif task in ['survival12', 'survival60']:
            # Do not add this new input to the encoding - from now on encodings only for inputs.
            if task == 'survival12':
                self.create_survived_cancer_for_n_months(12)
            elif task == 'survival60':
                self.create_survived_cancer_for_n_months(60)

            # Remove now irrelevant inputs
            del self.frame['SEER cause of death classification']
            del self.frame['Survival months']
            self.encodings.pop('SEER cause of death classification')
            self.encodings.pop('Survival months')

    def create_survived_cancer_for_n_months(self, n):
        """ Function to create target variable for cancer survival: Survived cancer for n months.

        Remove unknown survival
        Remove cases that died within n month of other cause
        0: Dead due to cancer and within n months
        1: Remaining
        Merged the fields:
        'SEER cause of death classification'
        'Survival months'
        into target
        'Survived cancer for n months'
        """

        # Remove unknown survival
        self.frame = fc.constraint(self.frame, 'Survival months', operator.lt, 999)

        # Remove cases that died within n month of other cause
        early_other_death_mask =\
            (self.frame['Survival months'] < n) & (self.frame['SEER cause of death classification'] != 1)
        early_other_death_columns = np.arange(self.frame['Survival months'].size)[early_other_death_mask]
        self.frame = self.frame.drop(early_other_death_columns)

        # Refresh indices starting from zero
        self.frame = self.frame.set_index(np.arange(self.frame['Survival months'].size))

        # Assigns 0/1 labels to the new column
        def survived_cancer_for_n_months(row):
            # Died within n months of cancer
            if row['Survival months'] < n and row['SEER cause of death classification'] == 1:
                return 0
            # Survived at least n months
            return 1

        # Create new target column
        self.frame['Survived cancer for ' + str(n) + ' months'] =\
            self.frame.apply(lambda row: survived_cancer_for_n_months(row), axis=1)

    def finalize(self):
        """ A method that summarizes some final pre processing for the data. """
        self.remove_constant_fields()

        if self.plot_data:
            fig = plt.figure(figsize=(8, int(len(self.frame.columns)/8)), dpi=300)
            self.heatmap_data(fig, "Final input data", 1, 1, 1)
            fig.savefig(self.output_directory + 'data_final.png')

        return self.encodings

    def remove_constant_fields(self):
        """ Remove all constant fields from the data. These are irrelevant for the prediction. """
        not_unique = self.frame.apply(pd.Series.nunique)
        cols_to_drop = not_unique[not_unique == 1].index
        self.frame = self.frame.drop(cols_to_drop, axis=1)
        # Remove columns from encoding, problem: they could be encoding already
        for column in cols_to_drop:
            c = column
            while c not in self.encodings:
                c = c[:-1]
                if len(c) == 0:
                    logging.error("Unable to remove encoding column: " + column)
                    exit(1)
            if self.encodings[c] > 1:
                self.encodings[c] = self.encodings[c] - 1
            else:
                self.encodings.pop(c)

    def heatmap_data(self, fig, title, x, y, i):
        """ Adds a heat map of the normalized data columns to fig. """
        ax = fig.add_subplot(x, y, i)
        ax.set_title(str(i) + ". " + title + " (" + str(self.frame.shape) + ")")

        data_normed = self.normalize_data(self.frame)
        # Normalize all data columns to 0-10
        data_normed = (data_normed * 10).astype(np.int32)
        # Top interval also includes maximum
        data_normed[data_normed == 10] = 9

        # Put normalized entries into bins for frequency analysis
        bins = np.apply_along_axis(lambda v: np.bincount(v, minlength=10), axis=0, arr=data_normed)
        bins = np.transpose(bins)
        ax.imshow(bins, cmap='gray', interpolation='nearest')
        labels = []
        for column in self.frame:
            # Show Min and Max, Mean, and std deviation
            empty = self.frame[column][self.frame[column] == -1].size
            values = len(np.unique(self.frame[column]))
            minimum, maximum = self.frame[column].min(), self.frame[column].max()
            mean, std = self.frame[column].mean(), self.frame[column].std()
            labels.append("%s (%.1f - %.1f, %.2f, %.2f) [%d, %d]" % (column, minimum, maximum, mean, std,
                                                                     values, empty))
        ax.set_xticks([0, 9])
        ax.set_xticklabels(['min', 'max'], fontsize=8)
        ax.set_yticks(np.arange(len(labels)))
        ax.set_yticklabels(labels, fontsize=8)

    @staticmethod
    def normalize_data(data):
        """ Normalizes the data from 0. to 1. """
        data_zeroed = (data - data.min())
        maximums = data_zeroed.max(axis=0)
        # Use max values to divide - if zero use one instead to prevent dividing by zero
        maximums[maximums == 0] = 1
        data_normed = data_zeroed / maximums
        return data_normed