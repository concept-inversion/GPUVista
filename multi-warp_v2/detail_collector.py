from traceback import FrameSummary
import pandas as pd
import numpy as np
from sqlalchemy import null
#import torch
from sklearn import preprocessing
import sys
import os
import ipdb
from common import *
from operator import is_not
from functools import partial
import json
#from numpyencoder import NumpyEncoder

def mapr(unique_list):
    import ipdb;ipdb.set_trace()
    le = preprocessing.LabelEncoder()
    le.fit(unique_list['instr'])
    obj1 = le.transform(unique_list['instr'])
    mapr = obj1.copy()
    mapr=mapr.astype(int)
    mapping = dict(zip(unique_list['instr'],mapr))
    #import ipdb;ipdb.set_trace()
    json_file=json.dumps(mapping,default=str)
    with open("instr.json","w") as outfile:
        outfile.write(json_file)

def collector(old, new):
    temp = set(np.append(old, new))
    temp = list(filter(partial(is_not, None), temp))
    return np.array(list(temp))


if __name__ == '__main__':
    path = sys.argv[1]
    unique_list = dict.fromkeys(col_name)
    i = 0
    if(os.path.isdir(path)):
        directory = os.listdir(path)
        for f in directory:
            print(f)
            i = i+1
            df = pd.read_csv(path+'/'+f, names=col_name,
                             error_bad_lines=False, header=None, )
            df = df.dropna()
            for col in unique_elements:
                un = (df[col].unique())
                if i == 1:
                    unique_list[col] = un
                else:
                    unique_list[col] = collector(unique_list[col], un)
        #import ipdb;ipdb.set_trace()
    else:
        df = pd.read_csv(path, names=col_name,
                         error_bad_lines=False, header=None, )
        df = df.dropna()
        for col in unique_elements:
            un = (df[col].unique())
            if i == 1:
                unique_list[col] = un
            else:
                unique_list[col] = collector(unique_list[col], un)
        #import ipdb;ipdb.set_trace()
    mapr(unique_list)
