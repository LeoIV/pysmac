import os,sys
import math

import numpy as np

import pysmac
import pysmac.piac


from branin_cli import branin, parameter_definition


# 
path = '/tmp/pySMAC_run'
os.makedirs(path, exist_ok=True)
num_instances=5


features = np.random.randint(9,size=(num_instances,3))
# parameter definition    

wallclock_limit = 300
"""
# optimizer object
opt = pysmac.SMAC_optimizer(t_limit_total_s=wallclock_limit, mem_limit_smac_mb= 300, working_directory = path + '/pysmac_output', persistent_files=True,debug=True)


# call its minimize method
value, parameters = opt.minimize(branin,      # the function to be minimized
                                 30,                 # the maximum number of function evaluations
                                 parameter_definition,
                                 num_train_instances = num_instances, 
                                 train_instance_features = features,
                                 mem_limit_function_mb=150, 
                                 t_limit_function_s= 5,
                                 num_runs = 1,)
"""
pysmac.piac.run_piac("/tmp/pySMAC_run/pysmac_output", 'branin_cli.py', "/tmp/pySMAC_run/piac_output", exploration_time_budget = 60, verbosity='DEBUG')
