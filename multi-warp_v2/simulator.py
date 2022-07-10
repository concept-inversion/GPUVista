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
    identifiers=None
    uid=None
    def __init__(self, inst=None):
        #self.inst=inst
        #ipdb.set_trace()
        self.truth= inst[['exe_lat', 'issue_lat']]
        self.uid=inst['uid']
        self.identifier= inst[['kid', 'core', 'sch_id', 'warp_id', 'uid', 'pc', 'reconvergence']]
        self.inst= inst.drop(['exe_lat', 'issue_lat','kid', 'core', 'sch_id', 'warp_id', 'uid', 'pc', 'reconvergence'])
        self.inst['exe_lat']=0
        self.inst['issue_lat']=0

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

class mem_simulator():
    context_list = []
    head = 0
    tail = 0
    clock = 0
    count = 0
    size = None
    model= None
    curr_inst= None
    sm_id=0
    def __init__(self, model_collection, sm_id,mode=None):
        if mode == SMEM:
            self.model=model_collection.smem_model
            self.sm_id=sm_id
        else:
            self.model=model_collection.gmem_model

    def add_inst(self, data):
        #ipdb.set_trace()
        self.curr_inst= data
        self.context_list.append(data)
        self.count += 1
        self.tail += 1
        return None

    def retire(self):
        for inst in self.context_list:
            if inst.clock > self.clock:
                self.context_list.remove(inst)
        return None

    def cycle(self, inst, issue_lat):
        self.retire()
        self.clock= issue_lat
        self.add_inst(inst)
        return self.simulate()
    def update_lat(self, exe_lat):
        #ipdb.set_trace()
        retire= self.clock + exe_lat
        self.clock= retire
        for inst in self.context_list:
            if inst.uid == self.curr_inst.uid:
                inst.inst['exe_lat']= exe_lat

    def generate_input(self):
        input_data=[]
        for inst in self.context_list:
            input_data.append(inst.inst.values)
        return input_data 

    def simulate(self):
        input_data= self.generate_input()
        if TRUTH:
            exe_lat= self.curr_inst.truth['exe_lat']            
            if DUMP:
                print("dump")
                # open files
                # write input
                # write output
        else:
            print("predict the latency")
        self.update_lat(exe_lat)
        return exe_lat


class block_simulator():
    context_list = []
    head = 0
    tail = 0
    clock = 0
    count = 0
    size = None
    model= None
    curr_inst= None
    sm_id=0
    block_id=0
    def __init__(self, model_collection, sm_id, block_id,mode=None):
        self.model=model_collection.block_model
        self.sm_id=sm_id
        self.block_id=block_id
    
    def add_inst(self, data):
        #ipdb.set_trace()
        self.curr_inst= data
        self.context_list.append(data)
        self.count += 1
        self.tail += 1

    def retire(self):
        for inst in self.context_list:
            if inst.clock > self.clock:
                self.context_list.remove(inst)
        return None

    def cycle(self, inst):
        self.retire() 
        self.add_inst(inst)
        return self.simulate()

    def update_lat(self, issue_lat, exe_lat):
        #ipdb.set_trace()
        retire= self.clock + issue_lat + exe_lat
        #self.clock= self.clock + issue_lat
        for inst in self.context_list:
            if inst.uid == self.curr_inst.uid:
                inst.clock= retire
                inst.truth['issue_lat']= issue_lat 
                inst.truth['exe_lat']= exe_lat

    def generate_input(self):
        input_data=[]
        for inst in self.context_list:
            input_data.append(inst.inst.values)
        #ipdb.set_trace()
        return input_data 

    def simulate(self):
        input_data= self.generate_input()
        issue_lat=0
        exe_lat=0
        if TRUTH:
            issue_lat=self.curr_inst.truth['issue_lat'] 
            exe_lat= self.curr_inst.truth['exe_lat']
            #print(self.curr_inst.truth)
        else:
            print("predict the latency") 
        print("block id: %d,sm_id: %d, previous clock:%d "%(self.block_id, self.sm_id, self.clock), end=",")
        self.clock= self.clock + issue_lat
        print("new clock: ", self.clock, end=",")
        #print("issue sent: ", issue_lat)
        return (issue_lat, exe_lat)

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
        

def context_collector(df, super_model): 
    simulator_config= simulator_configurator(super_model)
    simulator_config.counter(df)
    simulator_config.context_init()
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
    count=0
    for i in range(instructions):
        count=count+1
        #if count==10:
        #    break
        inst = df.iloc[i].copy()
        data=instruction(inst)
        issue_lat=0
        exe_lat=0
        gpu_context=simulator_config.blocks[inst['core']][inst['sch_id']]
        issue_lat,exe_lat=gpu_context.cycle(data)
        #print("i: %d, issue recev:%d "%(i,gpu_context.cycle(data)),end=",")
        print(i,issue_lat,exe_lat, end=", ")
        if inst['space']==11:
            temp_context=simulator_config.gmem
            exe_lat= temp_context.cycle(data, issue_lat)
            print("global mem: ",exe_lat, end=",")
        elif inst['space']==3:
            temp_context=simulator_config.smems[inst['core']]
            exe_lat= temp_context.cycle(data, issue_lat) 
            print("smem: ",exe_lat,end=",")
        gpu_context.update_lat(issue_lat, exe_lat)
        print("issue: %d, exe: %d, core: %d clock:%d"%(issue_lat, exe_lat,inst['core'],gpu_context.clock))
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
