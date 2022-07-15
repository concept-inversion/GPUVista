import numpy as np
import pandas as pd
import os, sys
import ipdb
from common import *
from utils import *
from abc import ABC, abstractmethod
from model import *

BLOCK_MAX=0
GMEM_MAX=0
SMEM_MAX=0

class context(ABC):
    head = 0
    tail = 0
    clock = 0
    count = 0
    max_count=0
    size = None
    model= None
    curr_inst= None
    sm_id=0
    block_id=0 
    inp_buffer= None
    model_type= None
    context_list=None
    context_type= None
    #global BLOCK_MAX
    global GMEM_MAX
    global SMEM_MAX

    def add_inst(self, data):
        
        self.curr_inst= data
        self.context_list.append(data)
        self.count += 1
        if self.context_type==BLOCK:
            global BLOCK_MAX
            if(self.count>BLOCK_MAX):
                BLOCK_MAX=self.count
                print("BLOCK: Max count: %d"%(self.count))
        if self.context_type==GMEM:
            global GMEM_MAX
            if(self.count>GMEM_MAX):
                print("GMEM: Max count: %d"%(self.count))
                GMEM_MAX=self.count
        if self.context_type==BLOCK:
            global SMEM_MAX
            if(self.count>SMEM_MAX):
                print("SMEM: Max count: %d"%(self.count))
                #print("+++ new: %d, old: %d"%(self.count, self.max_count))
                SMEM_MAX=self.count
 
        
        self.tail += 1
        return None

    def retire(self):
        #ipdb.set_trace()
        for inst in self.context_list:
            if inst.clock <= self.clock:
                #ipdb.set_trace()
                print("count: %d, instr with clock: %d retired: %d from block: %d and context_type: %d at cycle: %d"%(self.count, inst.clock, inst.uid, self.block_id, self.context_type,self.clock))
                #ipdb.set_trace()
                self.context_list.remove(inst)
                self.count = self.count -1
                #print("instr retired!!",inst['uid'])
        return None

    def print_status(self):
        print("Context type: %d, sm ID: %d,block ID: %d, count: %d, clock: %d"%(self.context_type, self.sm_id, self.block_id, self.count, self.clock))
    
    def dump_input(self, ib):
        if ib==None:
            print("No input provided.")
            sys.exit(0)
        else:
            #ipdb.set_trace()
            if self.context_type==BLOCK:
                inp_dump= ib.block.inp_dump_file
                out_dump= ib.block.out_dump_file
            elif self.context_type==SMEM:
                inp_dump= ib.smem.inp_dump_file
                out_dump= ib.smem.out_dump_file
            elif self.context_type==GMEM:
                inp_dump= ib.gmem.inp_dump_file
                out_dump= ib.gmem.out_dump_file
            else:
                print("Input dump type not detected!!")
                sys.exit(0)
            #ipdb.set_trace()
            input_data=np.array(self.generate_input())
            bin_input=dump_inst(input_data, self.context_type)
            inp_dump.write(bin_input)
            out=np.array(self.curr_inst.truth.values.astype(np.int32))
            out_dump.write(out)
            print(self.context_type, bin_input.shape, out.shape)

class block_simulator(context): 
    def __init__(self, model_collection, sm_id, block_id,mode=None):
        self.model=model_collection.block_model
        self.sm_id=sm_id
        self.block_id=block_id
        self.context_type= BLOCK
        self.context_list= []
    
    def update_lat(self, issue_lat, exe_lat):
        #ipdb.set_trace()
        retire= self.clock + issue_lat + exe_lat
        #self.clock= self.clock + issue_lat
        
        print("Block: Inst %d  will retire at %d, prev clock: %d, next clock: %d"%(self.curr_inst.uid,retire, self.clock, self.clock + issue_lat))
        self.clock= self.clock + issue_lat
        for inst in self.context_list:
            if inst.uid == self.curr_inst.uid:
                inst.clock= retire
                inst.inst['issue_lat']= issue_lat
                inst.inst['exe_lat']= exe_lat

    def generate_input(self):
        input_data=[]
        for inst in self.context_list:
            input_data.append(inst.inst.values)
        return input_data


    def cycle(self, inst,ib=None):
        self.retire()
        self.add_inst(inst)
        #self.print_status()
        #print("Inst retire from block.")
        return self.simulate(ib)


    def simulate(self, ib=None):
        input_data= self.generate_input()
        issue_lat=0
        exe_lat=0
        if TRUTH:
            issue_lat=self.curr_inst.truth['issue_lat']
            exe_lat= self.curr_inst.truth['exe_lat']
            #if (self.curr_inst.inst['space']==3) or (self.curr_inst.inst['space']==11):
             #   self.curr_inst.truth['exe_lat']=-1
            if DUMP:
                self.dump_input(ib)
        else:
            print("predict the latency") 
        #print("block id: %d,sm_id: %d, previous clock:%d "%(self.block_id, self.sm_id, self.clock), end=",")
        self.clock= self.clock + issue_lat
        #print("new clock: ", self.clock, end=",")
        #print("issue sent: ", issue_lat)
        self.print_status()
        return (issue_lat, exe_lat)

class mem_simulator(context):
    def __init__(self, model_collection, sm_id,mode=None):
        self.context_list= []
        if mode == SMEM:
            self.model=model_collection.smem_model
            self.sm_id=sm_id
            self.context_type= SMEM
        else:
            self.model=model_collection.gmem_model
            self.context_type= GMEM

    def update_lat(self, issue_lat, exe_lat):
        #ipdb.set_trace()
        if exe_lat==None:
            ipdb.set_trace()
        retire= self.clock + exe_lat
        print("Mem: Inst %d  will retire at %d, prv clock: %d, new clock: %d"%(self.curr_inst.uid,retire,self.clock, self.clock + issue_lat))
        self.clock= self.clock + issue_lat
        #print("Mem: Inst %d  will retire at %d"%(self.curr_inst.uid,retire))
        for inst in self.context_list:
            #ipdb.set_trace()
            if inst.uid == self.curr_inst.uid:
                inst.inst['exe_lat']= exe_lat


    def generate_input(self):
        input_data=[]
        for inst in self.context_list:
            #ipdb.set_trace()
            if self.context_type==SMEM:
                input_data.append(inst.smem_f.values)
            if self.context_type==GMEM:
                input_data.append(inst.gmem_f.values)
        return input_data

    def cycle(self, inst, issue_lat, ib=None):
        self.retire()     
        self.add_inst(inst)
        return self.simulate(issue_lat, ib)

    def simulate(self, issue_lat, ib=None):
        exe_lat=0
        if issue_lat==None:
            ipdb.set_trace()
        input_data= self.generate_input()
        if TRUTH:
            exe_lat= self.curr_inst.truth['exe_lat']
            if DUMP:
                self.dump_input(ib) 
        else:
            print("predict the latency")
        self.update_lat(issue_lat, exe_lat)
        self.print_status()
        return exe_lat
