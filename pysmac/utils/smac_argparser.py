import os
import sys
import time
import math

import inspect
import pickle

import resource
import pynisher
from pysmac.remote_smac import process_parameter_definitions



def parse_args(parser_dict):
    args = sys.argv
    if args[0] in ['python', 'python2', 'python3']:
        args = args[1:]

    config_dict = {}

    config_dict['instance'] = int(args[1][3:])
    config_dict['cutoff_time'] = float(args[3])
    config_dict['seed'] = int(args[5])

    config_def = args[6:]

    if len(config_def)%2 != 0:
        raise("Invalid parameter definition:\n%s"%" ".join(config_def))

    
    for i in range(0,len(config_def), 2):
        #split of leading "-"
        name = config_def[i][1:]
        value = config_def[i+1]
        # do type conversion
        config_dict[name] = parser_dict[name](value)

    return(config_dict)



def evaluate_function(function, config_dict, deterministic=False, has_instances=False):

    current_t_limit = int(math.ceil(config_dict.pop('cutoff_time')))
    
    wrapped_function = pynisher.enforce_limits(
            wall_time_in_s=current_t_limit,
            grace_period_in_s = 1)(function)

    # delete the unused variables from the dict
    if not has_instances:
        del config_dict['instance']
    if deterministic:
        del config_dict['seed']
    start = time.time()
    res = wrapped_function(**config_dict)
    wall_time = time.time()-start
    cpu_time = resource.getrusage(resource.RUSAGE_CHILDREN).ru_utime

    # try to infere the status of the function call:
    # if res['status'] exsists, it will be used in 'report_result'
    # if there was no return value, it has either crashed or timed out
    # for simple function, we just use 'SAT'
    result_dict = {
                'value' : (2**31)-1,
                'status': b'CRASHED' if res is None else b'SAT',
                'runtime': cpu_time
                }

    if res is not None:
        if isinstance(res, dict):
            result_dict.update(res)
        else:
            result_dict['value'] = res

    # account for timeeouts
    if not current_t_limit is None:
        if ( (result_dict['runtime'] > current_t_limit-2e-2) or
                (wall_time >= 10*current_t_limit) ):
            result_dict['status']=b'TIMEOUT'
    
    return(result_dict)

def generate_output(result_dict, seed=0):
    print('Result for SMAC: {0[status]}, {0[runtime]}, 0, {0[value]}, {1}'.format(result_dict, seed))


def wrapper(function, parameter_definition):

    _, parser_dict = process_parameter_definitions(parameter_definition)
    
    signature = inspect.signature(function)
    
    is_deterministic = (not ('seed' in signature.parameters))
    has_instances    = ('instance' in signature.parameters)
    
    
    config_dict = parse_args(parser_dict)
    result = evaluate_function(function, config_dict, is_deterministic, has_instances)
    generate_output(result, config_dict.get('seed', 0))
