import os,sys
import argparse, gzip
import json
import numpy as np
from common import *
from model import *

class instruction(): 
    clock=0 
    inst= None 
    truth= None 
    identifiers=None 
    uid=None 
    def __init__(self, inst=None): 
        self.truth= inst[['exe_lat', 'issue_lat']] 
        self.uid=inst['uid'] 
        self.identifier= inst[['kid', 'core', 'sch_id', 'warp_id', 'uid', 'pc', 'reconvergence']] 
        self.inst= inst.drop(['exe_lat', 'issue_lat','kid', 'core', 'sch_id', 'warp_id', 'uid', 'pc', 'reconvergence']) 
        self.inst['exe_lat']=0 
        self.inst['issue_lat']=0 


def load_file(model_name):
    try:
        inp_dump_file= open("train_data/"+model_name+"inp.bin", "wb")
        out_dump_file= open("train_data/"+model_name+"out.bin", "wb")
    except:
        print("Error loading dump file.")
        sys.exit(0)
    return inp_dump_file, out_dump_file


def dump_inst(context):
    shape= context.shape[0]
    # print(shape, end=',')
    cat=np.pad(context, ((0,BLOCK_CONTEXT-shape),(0,0)),'constant', constant_values=0)
    #cat=np.append(cat, out).astype(np.int16)
    cat=cat.flatten()
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
        block=  InputBuffer('block')
        gmem=  InputBuffer('gmem')
        smem=  InputBuffer('smem')

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

