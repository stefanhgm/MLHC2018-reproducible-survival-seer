import numpy as np
import pandas as pd

""" Column specific filters that receive the data and column name as default arguments. """


def merge_columns(data, column, target_column, **kwargs):
    """ Merge column into target column for all values that are empty, i.e. -1. """
    data_column = data.loc[:, column]
    non_empty_indices = np.where(data_column != -1)
    data_target_column = data.loc[:, target_column]
    data_target_column.iloc[non_empty_indices] = data_column.iloc[non_empty_indices]

    return data


def map_values(data, column, mapping, **kwargs):
    """ Map values according to the mapping in the specified field. """
    data_column = data.loc[:, column]
    mapper = np.vectorize(lambda x: mapping.get(x, x))
    data.loc[:, column] = mapper(data_column)
    # data[1][:, field_index] = mapper(data[1][:, field_index])
    return data


def encode_values(data, column, values, **kwargs):
    """ Encode given values as categorical inputs. """
    if kwargs['encode_inputs']:
        data_column = data.loc[:, column]
        contained_values = np.array([v for v in values if v in data_column])

        # First determine and create total number of additional columns
        additional_column_names = [column + ' continuous']
        additional_column_names += [column + ' ' + str(v) for v in contained_values]

        # Now add the according continuous and categorical inputs
        additional_columns = np.zeros((data.shape[0], len(additional_column_names)), dtype=np.int32)

        # Copy over values for continuous
        additional_columns[:, 0] = data_column
        for idx, v in enumerate(data_column):
            if v in contained_values:
                additional_columns[idx, 0] = 0
                additional_columns[idx, np.where(contained_values == v)[0][0] + 1] = 1

        del data[column]
        kwargs['encodings'].pop(column)
        data = data.join(pd.DataFrame(additional_columns, columns=additional_column_names))
        kwargs['encodings'][column] = len(contained_values) + 1

    return data


def constraint(data, column, operator, value):
    """ Filter a specific field in the data according to the operator and value. """
    constrained_indices = np.arange(data[column].size)[np.invert(operator(data[column], value))]
    data = data.drop(constrained_indices)
    # Refresh indices starting from zero
    data = data.set_index(np.arange(data[column].size))
    return data


def encode_field(data, column, **kwargs):
    """ Transform the given field into an encoded 1-n vector. """
    data_column = data.loc[:, column]
    unique_values = np.unique(data_column)
    size_x, size_y = data.shape

    additional_columns = [column + " " + str(v) for v in unique_values]
    additional_incidences = np.zeros((size_x, len(unique_values)), dtype=np.int32)

    # For each incidence fill the according value in the vector
    embedded_value_indices = [np.where(unique_values == v)[0][0] for v in data_column]
    additional_incidences[np.arange(len(data_column)), embedded_value_indices] = 1

    # Delete non-embedded specification and values
    data = remove_column(data, column)
    # Add embedded specification and values
    additional_embedded_data = pd.DataFrame(additional_incidences, columns=additional_columns, dtype=np.int32)
    data = data.join(additional_embedded_data)

    return data


def remove_column(data, column, **kwargs):
    """ Remove the field named field """
    del data[column]
    return data
