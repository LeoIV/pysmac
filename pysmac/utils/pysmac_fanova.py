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

    # getting features
    all_nums = []
    for dict_row in param_dict:
        num_line = str(dict_row).replace("'", "")
        num_line = str(num_line).replace("}", "")
        nums = []
        for line in str(num_line).split(" "):
            line = str(line).replace(",", "")
            if line.isdigit():
                nums.append(np.int(line))
            elif line.replace(".", "", 1).isdigit():
                nums.append(np.float(line))
            elif '-' in line:
                new_line = line.replace("-","")
                if new_line.isdigit():
                    nums.append(np.int(line))
                elif new_line.replace(".", "", 1).isdigit():
                    nums.append(np.float(line))
        all_nums.append(nums)

    x = np.array(all_nums)
    length = len(x)
    Y = data_extractor(response_file, length)
    fh = open(destination_dir + '/param.pcs')
    orig_pcs = fh.readlines()
    cs = pcs_new.read(orig_pcs, debug=True)
    X = np.zeros((x.shape))


    for i in range(x.shape[1]):
        idx = cs.get_idx_by_hyperparameter_name(f_params[i])
        X[:, idx] = x[:, i]   
    # create an instance of fanova with data for the random forest and the configSpace
    return fanova.fANOVA(X = X, Y = Y, config_space= cs)
    
    