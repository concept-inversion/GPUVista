from ast import dump
import pandas as pd
import numpy as np
from common import *

class context():
    def __init__(self, context_size):
        self.context_size = context_size
        self.clock=0
        self.length=0
        self.context= pd.DataFrame(columns=train_cols)
        self.retire_list= pd.DataFrame(columns=['uid', 'retire'])
        self.data= np.array([])
        
    
    def add(self, inst):
        if self.is_full():
            print('Context is full!')
        # self.context_inst.append(inst)
        self.context= self.context.append(inst)
        self.context.sort_values(by=['uid'],ascending=False, inplace=True)
        self.clock= self.clock + inst['fetch_lat']
        self.length+=1
        # print("Added instruction: ",inst['uid'], self.length, self.clock)

    def is_full(self):
        return self.length>=self.context_size

    def sort_context(self):
        pass

    def set_retire_list(self, inst):
        retire_lat= inst['fetch_lat'] + inst['issue_lat'] + inst['execution_lat']
        self.retire_list= self.retire_list.append({'uid':inst['uid'], 'retire':retire_lat},ignore_index=True)


    def retire(self):
        uid_list=[]
        # Determine the uid of instructions to retire
        for instruction in range(self.context.shape[0]):
            try:
                instruction= self.context.iloc[instruction]
            except:
                import ipdb; ipdb.set_trace()
            instr_id= instruction['uid']
            retire_lat= self.retire_list[self.retire_list['uid']==instr_id]['retire'].values[0]
            if retire_lat<=self.clock:
                uid_list.append(instr_id)
        # Remove the instructions from the context
        for uid in uid_list:
            self.context.drop(self.context.index[self.context['uid']==uid], inplace=True)
            self.retire_list.drop(self.retire_list.index[self.retire_list['uid']==uid], inplace=True)
            # print("Retired instruction: ", instr_id, retire_lat, self.clock)
            self.length-=1
        # import ipdb; ipdb.set_trace()
        self.context.sort_values(by=['uid'],ascending=False, inplace=True)

    def get_clock(self):
        return self.clock

    def dump_inst(self, inst, dump_file):
        #import ipdb; ipdb.set_trace()
        out= inst[FEATURE_LENGTH:FEATURE_LENGTH+OUT_LATENCY].values.copy()
        inst[FEATURE_LENGTH:FEATURE_LENGTH+OUT_LATENCY]=0
        inst=inst.drop(drop_before_train)
        # print(inst.shape, end=',')
        cat=np.append(inst.values,self.context.iloc[1:,].drop(drop_before_train,axis=1).values.copy())
        shape= self.context.shape[0]
        # print(shape, end=',')
        cat=np.pad(cat, (0, (CONTEXT_LENGTH-shape)*(len(train_cols_final))), 'constant', constant_values=0)
        # print(cat.shape, end=',')
        cat=np.append(cat, out).astype(np.int16)
        # print(cat.shape)
        dump_file.write(cat)

