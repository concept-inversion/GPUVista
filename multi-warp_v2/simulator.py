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

class instruction():
    clock=0
    inst= None
    truth= None
    identifier=None
    def __init__(self, inst=None):
        #self.inst=inst
        ipdb.set_trace()
        self.truth= inst[['exe_lat', 'issue_lat']]
        self.identifier= inst[['kid', 'core', 'sch_id', 'warp_id', 'uid', 'pc', 'reconvergence']]
        self.inst= inst.drop(['exe_lat', 'issue_lat','kid', 'core', 'sch_id', 'warp_id', 'uid', 'pc', 'reconvergence'])


class model_collection():
    block_model= None
    smem_model= None
    gmem_model= None
    def __init__(self):
        self.block_model= CNN_block(BLOCK_INPUT_SIZE, 2)
        self.smem_model= CNN_smem(SMEM_INPUT_SIZE, 1)
        self.gmem_model= CNN_gmem(GMEM_INPUT_SIZE, 1)
    
    def load_model(self, path):
        if(os.path.isdir(path)):
            directory = os.listdir(path)
            for f in directory:
                if search('BLOCK' ,f):
                    print("block model found!")
                    bm = path + '/' + f
                    self.block_model.load_state_dict(torch.load(bm))
                elif search('SMEM',f):
                    print("shared model found!")
                    bm = path + '/' + f
                    self.smem_model.load_state_dict(torch.load(sm))
                elif search('GMEM',f):
                    print("global model found!")
                    gm = path + '/' + f
                    self.gmem_model.load_state_dict(torch.load(gm))
        else:
            print("No trained models.")

class context_list():
    context_list = []
    head = 0
    tail = 0
    clock = 0
    count = 0
    size = None
    model= None
    inst= None
    def __init__(self, type=None):
        if type == BLOCK:
            self.model=model_collection.block_model
        elif type == S_MEM:
            self.model=model_collection.smem_model
        else:
            self.model=model_collection.gmem_model

    def add(self, data):
        ipdb.set_trace()
        self.inst= data
        context_list.append(data)
        count += 1
        tail += 1
        return None

    def retire(self):
        for inst in self.context_list:
            if inst.clock > self.clock:
                self.context_list.remove(inst)
        return None

    def cycle(self, inst):
        self.retire() 
        self.add(inst)

    def generate_input():
        input_data=[]
        for inst in range(context_list):
            input_data.append(inst.inst)
        return input_data 

    def simulate():
        input_data= self.generate_input()
        if TRUTH:
                    
        else:
            print("predict the latency")

class simulator_config():
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
        self.block_models = [[models.block_model for j in range(self.block_count)] for i in range(self.sm_count)]
        self.smem_models= [models.smem_model for i in range(self.sm_count)]
        self.gmem_models= models.gmem_model
        #self.blocks[i][j].append(context_list(S_MEM))
        

def context_collector(df, super_model): 
    simulator_instance= simulator_config(super_model)
    simulator_instance.counter(df)
    simulator_instance.context_init()
    instructions = df.shape[0]
    #ipdb.set_trace()
    df.sort_values(by=['issue_cycle'],inplace=True)
    df['issue_lat']=df['issue_cycle'].diff()  
    df['issue_lat'].fillna(0,inplace=True)
    df['issue_lat']=df['issue_lat'].astype(int)
    df['exe_lat']= df['wb_cycle']-df['issue_cycle']
    df = df.drop(['fetch_cycle', 'wb_cycle', 'issue_cycle'],axis=1)
    f= open('instr.json')
    instr_map=json.load(f)
    try:
        values=df['instr'].map(instr_map).astype(int)
    except:
        all=[instr_map.get(instr,instr) for instr in df['instr'].values]
        no_integers = [x for x in all if not isinstance(x, int)]
        missing= list(set(no_integers))
        print("missing:", missing)
        ipdb.set_trace()
    df['instr']=values
    f.close()
    #ipdb.set_trace()
    for i in range(instructions):
        inst = df.iloc[i].copy()
        data=instruction(inst)
        gpu_context=simulator_instance.block[inst['s_mem']][inst['sch_id']]
        issue_lat=gpu_context.cycle(data)
        if inst['space']==11:
            temp_context=simulator_instance.g_mem
            exe_lat= temp_context.cycle(data)
        elif inst['space']==3:
            temp_context=simulator_instance.s_mem[inst['core']]
            exe_lat= temp_context.cycle(data)
            
            gpu_context=simulator_instance.block[inst['s_mem']][inst['sch_id']]
            simulator_instance.cycle=gpu_context.cycle(data)
    return gpu_context.clock

def benchmark_caller(data, file_name, super_model):
    df = data.groupby(by=['kid'])
    kernels = [df.get_group(x) for x in df.groups]
    print(file_name, len(kernels))
    bench_max = []
    i = 0
    for frame in kernels:
        clock = context_collector(frame, super_model)
        print("kernel id: %d, Cycle: %d" % (i, clock))
        i += 1
    return bench_max

if __name__ == '__main__':
    if len(sys.argv)!=3:
        print("simulator.py <kernels trace directory> <models directory>")
        sys.exit()
    path = sys.argv[1]
    model_path = sys.argv[2]
    super_model= model_collection()
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
            benchmark_caller(df, f, super_model)
    else:
        df = pd.read_csv(path, names=col_name, error_bad_lines=False, header=None, )
        df = df.dropna()
        benchmark_caller(df, path, super_model)
