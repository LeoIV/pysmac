# -*- coding: utf-8 -*-
"""
Created on Mon Jul 24 14:05:22 2017

@author: chris
"""
import subprocess
import pickle
import os
path = os.path.dirname(os.path.realpath(__file__))
import scripts.piac_validate as piac_val

def run_piac(destination_dir, working_dir, piac_path, per_partition_time, max_num_partitions, init_time_budget):
    inputfile = open(destination_dir + '/scenario.txt', "r")
    outputfile = open(destination_dir + '/piac_scenario.txt', "w")
    for line in inputfile:
        if not line.lstrip().startswith("output-dir") and not line.lstrip().startswith("algo-exec") and not line.lstrip().startswith("algo-exec-dir") :
            outputfile.write(line.lower())
    outputfile.write('algo-exec-dir %s \n' %(path + '/target_algorithms'))
    outputfile.write('algo-exec python3 -u %s' %(path + '/target_algorithms/branin.py'))
    inputfile.close()
    outputfile.close()
    
    scenario_file = destination_dir + '/piac_scenario.txt'
    
    cmd = ["python3 %s/piac.py -v DEBUG --configurator SMAC2 %s %s --per_partition_time %i --max_num_partitions %i --init_time_budget %i" % (piac_path, scenario_file, working_dir,  per_partition_time, max_num_partitions, init_time_budget)]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    output = process.communicate()[0]
    print("Output: %s"% output)
    process.wait()
    print('Done')

def piac_evaluate(working_dir, inst_feature_file, instance_name):
    '''
    working_dir : where the piac_partition_tree_final.pkl file is stored
    inst_feature_name: path to features.dat
    '''
    with open(working_dir + '/piac_partition_tree_final.pkl', 'rb') as f:
        tree_root = pickle.load(f)
    
    inst_f_dict = {}
    with open(inst_feature_file) as f:
        next(f)
        for line in f:
            line = line.strip()
            vals = line.split(',')
            key = vals[0]
            features = vals[1:]
            inst_f_dict[key] = features
    configuration, node_name = piac_val.trickle_down_tree(tree_root, inst_f_dict, instance_name)
    return configuration, node_name
