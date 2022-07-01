from traceback import FrameSummary
import pandas as pd
import numpy as np
from sqlalchemy import null
import torch
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
    path= sys.argv[1]
    unique_list= dict.fromkeys(col_name_file)
    if(os.path.isdir(path)):
        directory= os.listdir(path)
        for file in directory:
            df= pd.read_csv(file, names=col_name_file,error_bad_lines=False, header=None, )
            






if __name__ == '__main__':
    # Process all the file in the given directory
    path= sys.argv[1]
    op_set= set()
    if(os.path.isdir(path)):
        directory= os.listdir(path)
        # import ipdb;ipdb.set_trace()
        for file in directory:
            df= null
            df= pd.read_csv(file, names=col_name_file,error_bad_lines=False, header=None, )
            split=sys.argv[1].split('/')
            if os.path.isdir('processed/'+split[1])==False:
                os.mkdir('processed/'+split[1])
            df.to_csv('processed/'+ split[1]+'/'+file,index=False,header=False)
            # break
    else:
        df= process_data_first_time(path)
        df.to_csv('processed/'+path.split('/')[-2]+'/'+path.split('/')[-1],index=False,header=False)