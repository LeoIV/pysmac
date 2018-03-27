# -*- coding: utf-8 -*-
"""
performs multiple independent smac runs, merges them and runs fanova on them
"""

import numpy as np
import fanova
from smac.configspace import pcs_new
import csv
from glob import glob
import pysmac.utils.state_merge as state_merge
import pysmac.utils.smac_output_readers as output_reader
import ConfigSpace as CS
from ConfigSpace.util import fix_types


import os
path = os.path.dirname(os.path.realpath(__file__))

def data_extractor(responsefile, length):
    y = []
    with open(responsefile, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        # skip first row
        next(csvreader)
        for row in csvreader:
            y.append(row[3])
    Y = np.array([float(i) for i in y[:length]])
    return Y
    
def smac_to_fanova(state_run_directory, destination_dir):
    '''
    Takes the state-run files, merges them and prepares the configuration space for fANOVA.
    
    outputs: fANOVA object
    
    state_run_directory: str
                        path to the directory of the pysmac_output/out/scenario file
    destination_dir: str
                    path to the directory in which the merged states should be stored
    '''

    state_run_list =[]
    files = glob(state_run_directory + "/*")
    for file in files:
        if file.startswith(state_run_directory + "/state-run"):
            state_run_list.append(file)
    state_merge.state_merge(state_run_list, destination_dir)
    merged_files = glob(destination_dir + '/*')

    for file in merged_files:
        if file.startswith(destination_dir + '/runs_and_results'):
            response_file = file
        if file.startswith(destination_dir + '/paramstrings'):
            paramstrings = file
    param_dict = output_reader.read_paramstrings_file(paramstrings)
    
    num_line = str(param_dict[0]).replace("'", "")
    num_line = str(num_line).replace("}", "")
    # messy way to get the parameter names wrt order
    f_params = []
    for line in str(num_line).split(" "):
        line = str(line).replace(",", "")
        line = line.replace('{',  '')
        if ':' in line:
            parameter = line.replace(':', '')
            f_params.append(parameter)
    
    # get configspace
    with open(destination_dir + '/param.pcs') as fh:
        cs = pcs_new.read(fh.readlines(), debug=True)

    X = []
    hps = cs.get_hyperparameters()


    for p in param_dict:
        c = CS.Configuration(cs, fix_types(p, cs), allow_inactive_with_values=True)
        X.append([])
        for hp in hps:
            if hasattr(hp, 'choices'):
                value = hp.choices.index(c[hp.name])
            else:
                value = c[hp.name]
            X[-1].append(value)
    
    X = np.array(X)
    Y = data_extractor(response_file, X.shape[0])

    return fanova.fANOVA(X = X, Y = Y, config_space= cs)
