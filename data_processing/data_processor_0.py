import pandas as pd
import numpy as np
from sklearn import preprocessing
import os,sys
# import context_collector
import read_features_1

if __name__ == '__main__':
    path= sys.argv[1]
    if(os.path.isdir(path)):
        directory= os.listdir(path)
        for file in directory:
            print(file)
            os.system('./preprocess.sh '+path+'/'+file)
    else:
        os.system('./preprocess.sh '+path)
