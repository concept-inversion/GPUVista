from traceback import FrameSummary
import pandas as pd
import numpy as np
from sqlalchemy import null
#import torch
from sklearn import preprocessing
import sys,os
import ipdb
from common import *


# def collector():
#     all=[instr_map.get(instr,instr) for instr in frames['inst'].values]
#     no_integers = [x for x in all if not isinstance(x, int)]
#     set(no_integers)
#     Keymax = max(instr_map, key= lambda x: instr_map[x])
#     max= instr_map.get(Keymax)


def collector(op_list, op_set):
    new_list= set(op_list)
    op_set= op_set.union(new_list)


if __name__ == '__main__':
    #import ipdb; ipdb.set_trace()
    path= sys.argv[1]

    unique_list= dict.fromkeys(col_name)
    if(os.path.isdir(path)):
        directory= os.listdir(path)
        i=0
        for f in directory:
            i=i+1
            df= pd.read_csv(path+'/'+f, names=col_name,error_bad_lines=False, header=None, )
            import ipdb; ipdb.set_trace()
            for col in unique_elements:
                un=(df[col].unique())
                if i==1:
                    unique_list[col]= un
                else:
                    #import ipdb; ipdb.set_trace()
                    temp= set(np.append(unique_list[col],un))
                    unique_list[col]= np.array(list(temp))
        import ipdb; ipdb.set_trace()
    else:
        df= pd.read_csv(path+'/'+f, names=col_name,error_bad_lines=False, header=None, )
        for col in unique_elements:
        	un=(df[col].unique())
                if i==1:
                    unique_list[col]= un
                else:
                    temp= set(np.append(unique_list[col],un))
                    unique_list[col]= np.array(list(temp))
	import ipdb; ipdb.set_trace()


