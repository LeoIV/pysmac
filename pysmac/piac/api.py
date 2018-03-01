<<<<<<< HEAD
import subprocess
import shutil
import pickle
import os
import glob
import numpy as np
from pysmac.utils import state_merge 

from kraken.piac.kraken import kraken

def run_ISMAC(source_dir, function_file, working_dir, python_executable='python3',
              verbosity='ERROR', seed=None,
              exploration_time_budget=np.float('inf'),
              per_partition_time=60,
              init_rand_exploration_evaluations=20,
              init_default_evaluations=5,
              exploration_evaluations=20,
              insts_for_PEI=-1,
              max_num_partitions=4,
              min_partition_size=4,
              tae_str='old', #  options 'aclib', 'old'
              save_rounds=False,
              regularize=False,
              modus='SMAC', # other choice 'ROAR'
              only_use_known_configs=False,
              budget_strat="equal" # other choice 'inc' for increasing
              ):
    state_run_directory = os.path.join(source_dir, 'out/scenario')
    merge_dir = os.path.join(working_dir, "scenario")
    state_run_list = glob.glob(state_run_directory + "/state-run*")
    state_merge.state_merge(state_run_list, merge_dir)
    
   
    # copy necessary files
    with open(merge_dir + '/scenario.txt', "r") as inputfile:
        with open(working_dir + '/piac_scenario.txt', "w") as outputfile:
            for line in inputfile:
                header, rest = line.split(" ", 1)
                if not header in ['output-dir', 'algo-exec', 'algo-exec-dir', 'run-obj']:
                    outputfile.write(line)
                if header == 'run-obj':
                    outputfile.write(" ".join([header, rest.lower()]))
            outputfile.write('algo-exec-dir = %s \n' %(working_dir))
            outputfile.write('algo-exec = %s %s' %(python_executable, function_file))
    
    scenario_file = working_dir + '/piac_scenario.txt'

    #shutil.copyfile(source_dir+'/features.dat', working_dir+'/features.dat')


    
    
    if seed is None:
        seed = np.random.seed()
    
    model = kraken(scen_file=scenario_file, per_partition_time=per_partition_time,
              working_dir=working_dir, verbosity=verbosity, seed=seed,
              exploration_time_budget=exploration_time_budget,
              init_rand_exploration_evaluations=init_rand_exploration_evaluations,
              init_default_evaluations=init_default_evaluations,
              exploration_evaluations=exploration_evaluations, insts_for_PEI=insts_for_PEI,
              max_num_partitions=max_num_partitions, tae_str=tae_str, save_rounds=save_rounds,
              min_partition_size=min_partition_size, regularize=regularize, modus=modus,
              only_known_configs=only_use_known_configs, budget_strat=budget_strat)
    return(model)
    

def piac_evaluate(working_dir, instance_features):
    '''
    working_dir : where the piac_partition_tree_final.pkl file is stored
    inst_features: valid feature vector
    '''
    with open(working_dir + '/piac_partition_tree_final.pkl', 'rb') as f:
        tree_root = pickle.load(f)
    
    configuration = tree_root.configuration_for_instance(instance_features)
    return configuration
