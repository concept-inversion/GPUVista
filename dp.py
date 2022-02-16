
from email.errors import NonPrintableDefect
import pandas as pd
import numpy as np
import torch

def read_data(file_name):
    col_name= ['flag', 'uid', 'core', 'warp', 't_time', 'inst', 'fetch_time', 'issued_time', 'latency', 'src_regs', 'dst_regs', 'isload', 'isstore', 'memwidth', 'op', 'sp_op', 'op_pipe', 'mem_op', 'oprd_type', 'initiation_interval', 'active_inst']
    drop=['flag','uid','core','warp','inst']
    output=['issue','execution']
    data = pd.read_csv(file_name, names=col_name, header=None)
    columnSeriesObj= data['inst']
    df=data.drop(drop,axis=1)
    df=df.apply(pd.to_numeric)
    df['inst']= columnSeriesObj.values
    import ipdb; ipdb.set_trace()
    df['issue']=df['issued_time']-df['fetch_time']
    df['execution']=df['t_time']-df['issued_time']
    drop=['issued_time','fetch_time','t_time']
    df=df.drop(drop,axis=1)
    return df 

df= read_data('data_processing/rodina2_data.log')

    
    