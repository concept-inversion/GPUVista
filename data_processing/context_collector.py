from enum import unique
import sys,os
import pandas as pd
import numpy as np
from sklearn import preprocessing
from sklearn.preprocessing import LabelEncoder
from read_features_1 import read_data
import ipdb
import logging
from common import *
'''
Input: trace from each kernel
Output: Context instruction for each instruction
'''
class context():
    def __init__(self, context_size):
        self.context_size = context_size
        self.head=0
        self.tail=0
        self.clock=0
        self.length=0
        self.context_inst=[]
    
    def add(self, inst_id, inst):
        if self.is_full():
            print('Context is full!')
        self.context_inst.append(inst)
        self.length+=1

    def is_full(self):
        return self.length>=self.context_size

    def sort_context():
        pass

    def retire(self, clock):
        for instruction in self.context_inst:
            if instruction['execute_time']>=clock:
                self.context_inst.remove(instruction)
        self.sort_context()

    def dump_inst(inst):
        pass
    

        



def event_creator(df):
    event_lists=[]
    for i in range((df.shape[0])):
        kid= df.iloc[i]['kid']
        uid= df.iloc[i]['uid']
        fetch=df.iloc[i]['ibuff_time']
        issue=df.iloc[i]['issued_time']
        execute=df.iloc[i]['exe_time']
        op=df.iloc[i]['instr']
        event_lists.append({'kid':kid, 'uid':uid, 'clock':fetch, 'type':0, 'op':op })
        event_lists.append({'kid':kid, 'uid':uid, 'clock':issue, 'type':1, 'op':op})
        event_lists.append({'kid':kid, 'uid':uid, 'clock':execute, 'type':2, 'op':op})
        # import ipdb; ipdb.set_trace()
    return event_lists
        

def context_counter(event_lists):
    fetched= set()
    issued= set()
    ops= []
    count= []
    event_count=0
    for i in range(len(event_lists)):
        # ipdb.set_trace()
        data= event_lists[i]
        if data['type']==0:
            fetched.add(data['uid'])
        elif data['type']==1:
            fetched.remove(data['uid'])
            issued.add(data['uid'])
            ops.append(data['op'])
        elif data['type']==2:
            issued.remove(data['uid'])
            ops.remove(data['op'])
        count.append(len(fetched) + len(issued))
        print("%d,%d,%d,%d"%(event_count,len(set(ops)), len(fetched), len(issued)))
        event_count+=1
    return count


def benchmark_caller(df):
    df= data.groupby(by=['kid'])
    kernels= [df.get_group(x) for x in df.groups]
    bench_max=[]
    i=0
    for frame in kernels:
        event_lists= event_creator(frame)
        sorted_list= (sorted(event_lists, key = lambda i: i['clock']))
        # count=context_counter(sorted_list)
        context_collector(frame, sorted_list, CONTEXT_LENGTH)
        bench_max.append(max(count))
        print("kernel id: %d, Max count: %d" % (i,(max(count))))
        i+=1
        break
    return bench_max


def context_collector(df, event_lists, context_length):
    instructions= df.shape[0]
    dump_instructions=[]
    clock=0
    context= context(context_length, OUT_LATENCY)
    for i in range(instructions):
        inst= df.iloc[i].values
        context.add(inst)
        context.retire()


if __name__ == '__main__':
    max_count=[]
    path= sys.argv[1]
    if(os.path.isdir(path)):
        for file in os.listdir(path):
            print("bechmark: ", file)
            if file.endswith(".log"):
                data= read_data(path+'/'+file)
                max_count.append(benchmark_caller(data))
    else:
        data= read_data(path)
        max_count.append(benchmark_caller(data))