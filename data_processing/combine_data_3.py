import numpy as np
import pandas as pd
import os,sys
from common import *

if __name__ == '__main__':
    path= sys.argv[1]
    if(os.path.isdir(path)):
        directory=os.listdir(path)
        final= np.array([],dtype=np.uint8)
        for bench in directory:
            try: 
                #print(bench)
                data= np.fromfile(path+bench, dtype=np.uint8)
                data=data.reshape(-1,CONTEXT_LENGTH*len(train_cols_final)+OUT_LATENCY)
                print(bench, data.shape)
                final=np.append(final,data) 
                #import ipdb; ipdb.set_trace()
            except:
                print("Error")
        to_write= open("combined_v1.bin", "wb")
        to_write.write(final)
        to_write.close()
        #import ipdb; ipdb.set_trace()
