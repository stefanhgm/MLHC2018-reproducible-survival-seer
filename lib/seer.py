import logging
import numpy as np
import pandas as pd

""" Methods to read SEER ASCII files. """


def parse_specification(seer_specification_path):
    """Parse specification file into list"""
    seer_field_specification = []
    with open(seer_specification_path) as specification:
        for line in specification:
            line_entries = line.split()
            if len(line_entries) > 6 and line_entries[0] is '@':
                description = ' '.join(map(str, line_entries[5:]))
                # Remove trailing comment
                description = description.split("*/", 1)[0]
                description = description.strip()
                seer_field_specification.append([int(line_entries[1]), line_entries[2], line_entries[3], description])
    return seer_field_specification


def parse_incidences(seer_specification_path, seer_incidences_path):
    """Parse incidences from incidence file and an according specification"""
    specification = parse_specification(seer_specification_path)

    # Derive tuples with start and end index for each column using field_specification
    delimiter = []
    colspecs = []
    descriptions = []
    for spec in specification:
        char_length = int(spec[2][5:spec[2].index('.')])
        delimiter.append(char_length)
        colspecs.append((spec[0] - 1, spec[0] - 1 + char_length))
        descriptions.append(spec[3])

    # Only support inputs of length 18
    assert (all(d < 19 for d in delimiter))
    # Checksum 1: total size w/out holes
    assert (sum(delimiter) == 362 - (1 + 3 + 2 + 1 + 3 + 2 + 13 + 5 + 6 + 1 + 2 + 4 + 5 + 5))

    # Read in at once
    logging.info("Read ASCII data files.")
    # The main line for loading the data, using pandas
    # .appl() is used to convert all entries to floats and replace strings with NaN
    # .fillna(-1) is used to replace all NaNs with -1 and .as_matrix() to convert everything to a matrix
    data = pd.read_fwf(seer_incidences_path, colspecs=colspecs, header=None, names=descriptions) \
        .apply(pd.to_numeric, errors='coerce').fillna(-1).astype(np.int32)

    return data
