import sys,os
import pandas as pd
import numpy as np
from common import *

if __name__=='__main__':
    path=sys.argv[1]
    df=pd.read_csv(path,names=col_name_processed_multi_core)
    import ipdb; ipdb.set_trace()
    df=df[df['core']==0]
    df=df[df['sch_id']==0]
    df=df[df['warp_id']==1]
    import ipdb; ipdb.set_trace()
