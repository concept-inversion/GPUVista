import sys,os
import pandas as pd
import numpy as np
from sklearn import preprocessing
from sklearn.preprocessing import LabelEncoder
'''
Input: trace from each kernel
Output: Context instruction for each instruction
'''

class context():
    def __init__(self, context_size, length):
        self.context_size = context_size
        self.head=0
        self.tail=0
        self.LENGTH=length
        self.clock=0
        self.context_inst=[]
    
    def add(self, inst_id, inst):
        if self.tail>=self.context_size:
            self.head+=1
        self.context_inst.append(inst)
        self.tail+=1

    def is_full(self):
        return self.tail>=self.context_size

        
# '''
# struct Context *cxt = new Context;
#   while (true) {
#     Inst *newInst = cxt->add();
#     if (cxt->is_full())
#       cxt->retire();
#     if (!newInst->read(trace))
#       break;
#     Tick curTick = newInst->inTick;
#     cxt->dump(curTick);
#   }
# '''



        


def read_data(file_name):
    col_name= ['flag', 'uid', 'core', 'warp', 't_time', 'inst', 'fetch_time', 'issued_time', 'latency', 'src_regs', 'dst_regs', 'isload', 'isstore', 'memwidth', 'op', 'sp_op', 'op_pipe', 'mem_op', 'oprd_type', 'initiation_interval', 'active_inst']
    output=['issue','execution']
    data = pd.read_csv(file_name, names=col_name, header=None)
    le = preprocessing.LabelEncoder()
    le.fit(data['inst'])
    obj1= le.transform(data['inst'])
    df=df.apply(pd.to_numeric)
    df['inst']= obj1
    df['issue']=df['issued_time']-df['fetch_time']
    df['execution']=df['t_time']-df['issued_time']
    df=df.drop(drop,axis=1)
    return df 


if __name__ == '__main__':
    df= read_data('data_processing/rodina2_data.log')
    import ipdb; ipdb.set_trace()