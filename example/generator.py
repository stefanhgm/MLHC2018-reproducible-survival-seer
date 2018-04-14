from random import randint
from random import shuffle
import os

''' A helper that generates completely random (!) SEER ASCII files as input examples. '''


def read_char_lengths():
    with open('read.seer.research.nov2016.sas') as file:
        lines = file.readlines()
    del lines[0:6]
    result = []
    index = 1
    for line in lines:
        start = int(line.split()[1])
        result.append(start - index)
        index = start
    # last entry manually
    result.append(2)
    return result


def create_incidences(number, lengths):
    ''' Create example SEER incidences with random numbers between 0 and 9 as attributes. '''
    csv_file = open('INCIDENCES.txt', 'ab+')
    patient_ids_and_record_numbers = []
    for i in range(0, number):
        # field 0 is patient id and field 62 is record number - store patient id ans set record number to zero
        values = ''
        for idx, length in enumerate(lengths):
            value = str(randint(0, 9)).zfill(length)
            # set record number to zero
            if idx == 62:
                value = '00'.zfill(length)
            if idx == 107:
                # set survival between 0 and 120
                value = str(randint(0, 120)).zfill(length)
            # store patient id
            if idx == 0:
                value = str(randint(0, 100000000)).zfill(length)
                patient_ids_and_record_numbers.append((value, '00'))
            values += value
        csv_file.write(bytes(values + '\n', 'UTF-8'))
    csv_file.close()
    return patient_ids_and_record_numbers


def create_cases(number, patient_ids_and_record_numbers):
    ''' Create example SEER*Stat case selection as csv file. '''
    shuffle(patient_ids_and_record_numbers)
    csv_file = open('CASES.csv', 'ab+')
    csv_file.write(bytes('Patient ID,Record number\n', 'UTF-8'))
    for i in range(0, number):
        csv_file.write(bytes(patient_ids_and_record_numbers[i][0] + ',' +
                             patient_ids_and_record_numbers[i][1] + '\n', 'UTF-8'))
        patient_ids_and_record_numbers.pop(0)
    csv_file.close()


if os.path.exists('Incidences.csv'):
    os.remove('Incidences.csv')
if os.path.exists('Cases.csv'):
    os.remove('Cases.csv')
chars = read_char_lengths()

patient_ids_and_record_numbers_filter = create_incidences(10000, chars)
create_cases(5000, patient_ids_and_record_numbers_filter)
