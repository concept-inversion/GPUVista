import numpy as np
import pandas as pd
import os, sys
from common import *
from utils import *
from abc import ABC, abstractmethod
from model import *
class context(ABC):
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
    inp_buffer= None

    #@abstractmethod
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


    def generate_input(self):
        input_data=[]
        for inst in self.context_list:
            input_data.append(inst.inst.values)
        return input_data

    def dump_input(self, inp_buffer):
        if inp_buffer==None:
            print("No input provided.")
        else:
            inp_dump= "inp found" # get files
            out_dump= "out dump"#  i
            print("dump")
                #ipdb.set_trace()
            input_data=np.array(self.generate_input())
            dump_inst(input_data, 'train_input.bin')
                #np.dump_file.write(
            out=np.array(self.curr_inst.truth.values)
            dump_file= open("train_data/out.bin", "wb")
            dump_file.write(out)


class block_simulator(context):
    def __init__(self, model_collection, sm_id, block_id,mode=None):
        self.model=model_collection.block_model
        self.sm_id=sm_id
        self.block_id=block_id

    def update_lat(self, issue_lat, exe_lat):
        #ipdb.set_trace()
        retire= self.clock + issue_lat + exe_lat
        #self.clock= self.clock + issue_lat
        for inst in self.context_list:
            if inst.uid == self.curr_inst.uid:
                inst.clock= retire
                inst.truth['issue_lat']= issue_lat
                inst.truth['exe_lat']= exe_lat


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
            #print(self.curr_inst.truth)
        else:
            print("predict the latency")
            
        print("block id: %d,sm_id: %d, previous clock:%d "%(self.block_id, self.sm_id, self.clock), end=",")
        self.clock= self.clock + issue_lat
        print("new clock: ", self.clock, end=",")
        #print("issue sent: ", issue_lat)
        return (issue_lat, exe_lat)


class mem_simulator(context):
    def __init__(self, model_collection, sm_id,mode=None):
        if mode == SMEM:
            self.model=model_collection.smem_model
            self.sm_id=sm_id
        else:
            self.model=model_collection.gmem_model

    def update_lat(self, exe_lat):
        #ipdb.set_trace()
        retire= self.clock + exe_lat
        self.clock= retire
        for inst in self.context_list:
            if inst.uid == self.curr_inst.uid:
                inst.inst['exe_lat']= exe_lat

    def cycle(self, inst, issue_lat, ib=None):
        self.retire()     
        #self.clock= issue_lat  # Take care of this. 
        self.add_inst(inst)
        return self.simulate(ib)


    def simulate(self, ib=None):
        input_data= self.generate_input()
        if TRUTH:
            exe_lat= self.curr_inst.truth['exe_lat']
        else:
            print("predict the latency")
        self.update_lat(exe_lat)
        return exe_lat


