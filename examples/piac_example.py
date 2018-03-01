import os,sys
import math

import numpy as np
import logging
logging.basicConfig(level=logging.DEBUG)


import pysmac
import pysmac.piac


from branin_cli import branin as a_function
from branin_cli import parameter_definition

# 
path = '/tmp/pySMAC_run'
os.makedirs(path, exist_ok=True)
num_instances=16

# random features, 
features = np.random.randint(9,size=(num_instances,3))

# optimizer object
opt = pysmac.SMAC_optimizer(t_limit_total_s=360, mem_limit_smac_mb= 300,
							working_directory = path + '/pysmac_output',
							persistent_files=True)


# call its minimize method
value, parameters = opt.minimize(a_function,  # the function to be minimized
                                 10,         # the maximum number of function evaluations
                                 parameter_definition,
                                 num_train_instances = num_instances, 
                                 train_instance_features = features,
                                 mem_limit_function_mb=1200, 
                                 t_limit_function_s= 5,
                                 num_runs = 1)

model = pysmac.piac.run_ISMAC("/tmp/pySMAC_run/pysmac_output", './branin_cli.py', "/tmp/pySMAC_run/piac_output",
              init_default_evaluations=10,
              exploration_evaluations=20,
              insts_for_PEI=5,
              per_partition_time=30,
              max_num_partitions=4)

#config = model.get_config_for_instance(tuple(features[0]))
