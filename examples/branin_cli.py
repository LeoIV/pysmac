import math
from pysmac.utils.smac_argparser import wrapper

def branin(x1, x2, instance):
    # note, this function doesn't actually use the instance id for anything!
    print('branin input: ', x1, x2, instance)
    a = 1
    b = 5.1 / (4*math.pi**2)
    c = 5 / math.pi
    r = 6
    s = 10
    t = 1 / (8*math.pi)
    ret  = a*(x2-b*x1**2+c*x1-r)**2+s*(1-t)*math.cos(x1)+s
    print('branin output: ', ret)
    return ret


# parameter definition    
parameter_definition=dict(\
                x1=('real',    [-5, 5],  1),     # this line means x1 is a float between -5 and 5, with a default of 1
                x2=('real',    [-5, 5], -1),     # same as x1, but the default is -1
                )

if __name__=="__main__":
    wrapper(branin, parameter_definition)
