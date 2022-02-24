import pandas as pd
import numpy as np
import torch
from sklearn import preprocessing

def read_data(file_name):
    col_name= ['flag','kid', 'uid', 'core', 'warp', 'exe_time', 'inst', 'ibuff_time', 'issued_time', 'latency', 'src_regs', 'dst_regs', 'isload', 'isstore', 'memwidth', 'op', 'sp_op', 'op_pipe', 'mem_op', 'oprd_type', 'initiation_interval',
     'active_inst','isatomic','cache_status','reconvergence','pc','bar_type','red_type','bar_count','cache_op']
    # drop=['flag','uid','core','warp','inst']
    # output=['fetch','issue','execution']
    data = pd.read_csv(file_name, names=col_name,error_bad_lines=False, header=None, )
    num_lines = sum(1 for line in open(file_name))
    print(num_lines,data.shape[0])
    if num_lines!=data.shape[0]:
        print(num_lines-data.shape[0], ' Error lines read by pandas!!')
    return data


def encode_data(data):
    le = preprocessing.LabelEncoder()
    le.fit(data['inst'])
    obj1= le.transform(data['inst'])
    df=data.drop(drop,axis=1)
    df=df.apply(pd.to_numeric)
    df['inst']= obj1
    df['issue']=df['issued_time']-df['fetch_time']
    df['execution']=df['t_time']-df['issued_time']
    drop=['issued_time','fetch_time','t_time']
    df=df.drop(drop,axis=1)
    return df 

if __name__ == '__main__':
    df= read_data('rodina2_data.log')
    import ipdb; ipdb.set_trace()
    
    