from enum import unique
import sys
import os,ipdb
#from read_features_1 import read_data
import numpy as np
from common import *
#from context import context
import argparse
import pandas as pd
import json       
from model import *
import gzip
from context import *
from utils import *

class simulator_configurator():
    sm_count= 0
    block_count= 0
    block_models= None
    gmem_model= None
    smem_models= None
    models= None
    cycle=0
    def __init__(self,super_model):
        self.models= super_model

    def counter(self,df):
        self.sm_count=df['core'].nunique()
        block_unique=df['sch_id'].nunique()
        self.block_count= block_unique * self.sm_count

    def context_init(self):
        self.blocks= [[block_simulator(self.models,i,j) for j in range(self.block_count)] for i in range(self.sm_count)]
        self.smems= [ mem_simulator(self.models,i,SMEM) for i in range(self.sm_count)]
        self.gmem= mem_simulator(self.models,0)
        #self.blocks[i][j].append(context_list(S_MEM))

def trace_processor(df, instr_map):
    df.sort_values(by=['issue_cycle'],inplace=True)
    df['issue_lat']=df['issue_cycle'].diff()  
    df['issue_lat'].fillna(0,inplace=True)
    df['issue_lat']=df['issue_lat'].astype(int)
    df['exe_lat']= df['wb_cycle']-df['issue_cycle']
    df = df.drop(['fetch_cycle', 'wb_cycle', 'issue_cycle'],axis=1)
    try:
        values=df['instr'].map(instr_map).astype(int)
    except:
        all=[instr_map.get(instr,instr) for instr in df['instr'].values]
        no_integers = [x for x in all if not isinstance(x, int)]
        missing= list(set(no_integers))
        print("missing:", missing)
        ipdb.set_trace()
    df['instr']=values
    #f.close()
    return df

def context_collector(df, super_model, ib=None): 
    simulator_config= simulator_configurator(super_model)
    simulator_config.counter(df)
    simulator_config.context_init()
    instructions = df.shape[0]
    if not ib:
        print("ib none in context collector.")
    count=0
    for i in range(instructions):
        count=count+1
        if count==10:
            print()#sys.exit(0)
        inst = df.iloc[i].copy()
        print("\n***********\n Instruction:%d, uid:%d,  issue: %d, exe: %d "%(i, inst['uid'], inst['issue_lat'], inst['exe_lat']))
        data=instruction(inst)
        issue_lat=0
        exe_lat=0
        gpu_context=simulator_config.blocks[inst['core']][inst['sch_id']]
        issue_lat,exe_lat=gpu_context.cycle(data, ib)
        #print(i,issue_lat,exe_lat, end=", ")
        if inst['space']==11:
            temp_context=simulator_config.gmem
            exe_lat= temp_context.cycle(data, issue_lat,ib)
            #print("global mem: ",exe_lat, end=",")
        elif inst['space']==3:
            #ipdb.set_trace()
            temp_context=simulator_config.smems[inst['core']]
            exe_lat= temp_context.cycle(data, issue_lat, ib) 
            #print("smem: ",exe_lat,end=",")
        gpu_context.update_lat(issue_lat, exe_lat)
        
        #print("issue: %d, exe: %d, core: %d clock:%d"%(issue_lat, exe_lat,inst['core'],gpu_context.clock))
    return gpu_context.clock

def benchmark_caller(data, file_name, super_model, ib= None):
    df = data.groupby(by=['kid'])
    kernels = [df.get_group(x) for x in df.groups]
    print(file_name, len(kernels))
    bench_max = []
    i = 0
    for frame in kernels:
        clock = context_collector(frame, super_model, ib)
        print("kernel id: %d, Cycle: %d" % (i, clock))
        i += 1
    return bench_max

if __name__ == '__main__':
    if len(sys.argv)!=3:
        print("simulator.py <kernels trace directory> <models directory>")
        sys.exit()
    path = sys.argv[1]
    model_path = sys.argv[2]
    super_model= ModelCollec()
    instr_map= load_mapper()
    input_buffer= None
    model_collection= None
    if DUMP:
        input_buffer= InputBufferCollec()
        print("Dump detected!!")
        #ipdb.set_trace()
    if not TRAIN:
        print("Loading model!!")
        try:
            super_model.load_model(model_path)
        except:
            print("Model not loaded!")
            sys.exit()
    if(os.path.isdir(path)):
        directory = os.listdir(path)
        for f in directory:
            df = pd.read_csv(path+'/'+f, names=col_name, error_bad_lines=False, header=None, )
            df = df.dropna()
            df= trace_processor(df,instr_map)
            benchmark_caller(df, f, super_model, input_buffer)
    else:
        df = pd.read_csv(path, names=col_name, error_bad_lines=False, header=None, )
        df = df.dropna()
        df= trace_processor(df,instr_map)
        benchmark_caller(df, path, super_model, input_buffer)
