import os,sys
import argparse, gzip
import json, ipdb
import numpy as np
from common import *
from model import *

class instruction(): 
    clock=0 
    inst= None 
    truth= None 
    identifiers=None 
    uid=None
    gmem_f=None
    smem_f=None
    #smem
    def __init__(self, inst=None): 
        #ipdb.set_trace()
        self.truth= inst[['exe_lat', 'issue_lat']] 
        self.uid=inst['uid'] 
        self.identifier= inst.loc[inst_id]
        self.gmem_f= inst.loc[gmem_features]
        self.smem_f= inst.loc[smem_features]
        self.inst= inst.loc[block_features]
        #self.inst= inst.drop(['exe_lat', 'issue_lat','kid', 'core', 'sch_id', 'warp_id', 'uid', 'pc', 'reconvergence']) 
        self.inst['exe_lat']=0 
        self.inst['issue_lat']=0 
        self.gmem_f['exe_lat']=0
        self.smem_f['exe_lat']=0

def load_file(model_name):
    try:
        inp_dump_file= open("train_data/"+model_name+"_inp.bin", "wb")
        out_dump_file= open("train_data/"+model_name+"_out.bin", "wb")
    except:
        print("Error loading dump file.")
        sys.exit(0)
    return inp_dump_file, out_dump_file


def dump_inst(context, model_type):
    shape= context.shape[0]
    # print(shape, end=',')
    #ipdb.set_trace()
    if model_type==BLOCK:
        CONTEXT=BLOCK_CONTEXT
        #cat=np.pad(context, ((0,CONTEXT-shape),(0,0)),'constant', constant_values=0)
    elif model_type==SMEM:
        CONTEXT=SMEM_CONTEXT
        #cat=np.pad(context, ((0,CONTEXT-shape),(0,0)),'constant', constant_values=0)
    else:
        CONTEXT=GMEM_CONTEXT
        #cat=np.pad(context, ((0,CONTEXT-shape),(0,0)),'constant', constant_values=0)
    if CONTEXT-shape<0:
        ipdb.set_trace()
    cat=np.pad(context, ((0,CONTEXT-shape),(0,0)),'constant', constant_values=0)
    #cat=np.append(cat, out).astype(np.int16)
    print(cat.shape)
    cat=cat.astype(np.int32).flatten()
    return cat


def load_mapper():
    try:
        f= open('instr.json')
        instr_map=json.load(f)
        f.close()
    except:
        print("No mapper found!!")
        sys.exit(0)
    return instr_map


class InputBuffer():
    path= None
    inp_dump_file= None
    out_dump_file= None
    model_type=None
    def __init__(self, model_type):
        #self.path= path
        self.inp_dump_file,self.out_dump_file=load_file(model_type)

class InputBufferCollec():
    block= None
    gmem= None
    smem= None
    def __init__(self):
        #ipdb.set_trace()
        self.block=  InputBuffer('block')
        self.gmem=  InputBuffer('gmem')
        self.smem=  InputBuffer('smem')

class ModelCollec():
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

def trace_processor(df, instr_map):
    df.sort_values(by=['issue_cycle'],inplace=True)
    #ipdb.set_trace()
    df=df.set_index('uid')
    derived=df.groupby(['core','sch_id'],sort=False)['issue_cycle'].diff().to_frame()
    derived=derived.rename(columns={"issue_cycle": "issue_lat"})
    derived['issue_lat'].fillna(1,inplace=True)
    df=df.join(derived.astype(int))
    df=df.reset_index()
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
    return df



