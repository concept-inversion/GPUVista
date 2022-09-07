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
    input_out_counter=0
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
                #print("BLOCK: Max count: %d"%(self.count))
        elif self.context_type==GMEM:
            global GMEM_MAX
            if(self.count>GMEM_MAX):
                #print("GMEM: Max count: %d"%(self.count))
                GMEM_MAX=self.count
        elif self.context_type==SMEM:
            global SMEM_MAX
            if(self.count>SMEM_MAX):
                #print("SMEM: Max count: %d"%(self.count))
                #print("+++ new: %d, old: %d"%(self.count, self.max_count))
                SMEM_MAX=self.count
        else:
            print("other category of instruction found!!")
            ipdb.set_trace()
        #print("BLOCK count: %d, GMEM count: %d, SMEM: %d"%(BLOCK_MAX,GMEM_MAX,SMEM_MAX)) 
        self.tail += 1
        return None

    def print_hardware(self):
        global BLOCK_MAX, SMEM_MAX, GMEM_MAX
        print("***************Block: %d, smem: %d, gmem: %d************"%(BLOCK_MAX,SMEM_MAX,GMEM_MAX))
    
    
    def retire(self):
        for inst in self.context_list:
            #if self.context_type==SMEM:
            #print("inst: %d, retire at: %d"%(inst.uid, inst.clock))
            if inst.clock <= self.clock:
                #ipdb.set_trace()
                #print("count: %d, instr with clock: %d retired: %d from block: %d and context_type: %d at cycle: %d"%(self.count, inst.clock, inst.uid, self.block_id, self.context_type,self.clock))
                #ipdb.set_trace()
                self.context_list.remove(inst)
                self.count = self.count -1
                #print("instr retired!!",inst['uid'])
        return None

    def print_status(self):
        print("Context type: %d, sm ID: %d,block ID: %d, count: %d, clock: %d"%(self.context_type, self.sm_id, self.block_id, self.count, self.clock))
    
    def dump_input(self, ib):
        out=None
        if ib==None:
            print("No input provided.")
            sys.exit(0)
        else:
            #ipdb.set_trace()
            if self.context_type==BLOCK:
                inp_dump= ib.block.inp_dump_file
                out_dump= ib.block.out_dump_file
                out=np.array(self.curr_inst.truth.values.astype(np.int32))
                out_dump.write(out)
                print(out.shape)
                print("abcde,",out)
                #ipdb.set_trace()
            elif self.context_type==SMEM:
                inp_dump= ib.smem.inp_dump_file
                out_dump= ib.smem.out_dump_file
                out=self.curr_inst.truth['exe_lat'].astype(np.int32)
                out_dump.write(out)
                #ipdb.set_trace()
            elif self.context_type==GMEM:
                inp_dump= ib.gmem.inp_dump_file
                out_dump= ib.gmem.out_dump_file
                out=self.curr_inst.truth['exe_lat'].astype(np.int32)
                out_dump.write(out)
            else:
                print("Input dump type not detected!!")
                sys.exit(0)
            #print("abcde,",out)
            if out.all()==None:
                ipdb.set_trace()
            input_data=np.array(self.generate_input())
            bin_input=dump_inst(input_data, self.context_type)
            print(bin_input.shape)
            inp_dump.write(bin_input)
            '''
            out=np.array(self.curr_inst.truth.values.astype(np.int32))
            #ipdb.set_trace()
            assert out.shape[0]!= 0
            print(out.shape)
            out_dump.write(out)
            #print(self.context_type, bin_input.shape, out.shape)
            '''
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
        print("Block: Inst %d  will retire at %d, clock %d"%(self.curr_inst.uid,retire, self.clock))
        #self.clock= self.clock + issue_lat
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
        self.clock= self.clock + issue_lat
        self.print_status()
        return (issue_lat, exe_lat)

class mem_simulator(context):
    #input_out_counter=0
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
        if self.clock<issue_lat:
            self.clock= issue_lat
        retire= self.clock + exe_lat
        self.curr_inst.clock= retire
        print("Mem: Inst %d  will retire at %d, clock: %d"%(self.curr_inst.uid, retire, self.clock)) 
        for inst in self.context_list:
            #ipdb.set_trace()
            if inst.uid == self.curr_inst.uid:
                if self.context_type==SMEM:
                    inst.smem_f['exe_lat']= exe_lat
                elif self.context_type==GMEM:
                    inst.gmem_f['exe_lat']= exe_lat


    def generate_input(self):
        input_data=[]
        for inst in self.context_list:
            #ipdb.set_trace()
            if self.context_type==SMEM:
                input_data.append(inst.smem_f.values)
            if self.context_type==GMEM:
                input_data.append(inst.gmem_f.values)
        print("input shape: ",len(input_data))
        #ipdb.set_trace()
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
