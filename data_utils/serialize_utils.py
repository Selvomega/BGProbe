"""
This module provides the serialization tool for the testcase
"""

import pickle

def save_variable_to_file(variable, filename, save_mode='ab'):
    """
    Save variable to files. 
    By default use 'append binary' (`ab`)
    """
    with open(filename, save_mode) as file: 
        pickle.dump(variable, file)

def read_variables_from_file(filename):
    """
    Read variables item by item from the file
    """
    variables = []
    with open(filename, 'rb') as file:
        while True:
            try:
                var = pickle.load(file)
                variables.append(var)
            except EOFError:  # triggered when meet the end of the file
                break
    return variables
