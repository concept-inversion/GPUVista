from traceback import FrameSummary
import pandas as pd
import numpy as np
from sqlalchemy import null
import torch
from sklearn import preprocessing
import sys,os
import ipdb
from common import *
BUFFER_LENGTH= 2


def process_data_first_time(file_name):
    data = pd.read_csv(file_name, names=col_name_file,error_bad_lines=False, header=None, )
    num_lines = sum(1 for line in open(file_name))
    print(file_name,num_lines,data.shape[0])
    if num_lines!=data.shape[0]:
        print(num_lines-data.shape[0], ' Error lines read by pandas!!')
    df= data.groupby(by=['kid'])
    kernels= [df.get_group(x) for x in df.groups]
    p_kernels=[]
    for frames in kernels:
        # le = preprocessing.LabelEncoder()
        # le.fit(frames['inst'])
        # obj1= le.transform(frames['inst'])
        # frames['instr']= obj1.copy()
        try:
            frames['instr']= frames['inst'].map(instr_map).astype(int)
        except:
            print("Error in mapping instruction")
            all=[instr_map.get(instr,instr) for instr in frames['inst'].values]
            no_integers = [x for x in all if not isinstance(x, int)]
            #print("Missing instruction map:", set(no_integers))
            missing= list(set(no_integers))
            print("Missing instr map: ", missing)
            Keymax = max(instr_map, key= lambda x: instr_map[x])
            max_value= instr_map.get(Keymax)
            print("max: ", max_value) 
            '''
            for each in missing:
                print("in the loop", each, Keymax+1)
                print(each,Keymax+1)
                Keymax+=1
                '''
            import ipdb; ipdb.set_trace()
        frames['wb_id']=frames.index.values.copy()
        ibuff_order= frames['uid']%BUFFER_LENGTH
        frames['buffer_order']= ibuff_order
        # frames=frames.set_index('uid').sort_index()
        frames=frames.sort_values(by=['uid'])
        frames['issue_lat']=frames['issued_time'].diff()
        frames['issue_lat'].fillna(0,inplace=True)
        frames['fetch_lat']=frames['issued_time']-frames['ibuff_time']
        frames['execution_lat']=frames['exe_time']-frames['issued_time']
        # frames.reset_index(inplace=True)
        frames.fetch_lat=frames.fetch_lat.astype(int)
        frames=frames.drop(['inst','flag','core','warp','pc'],axis=1)
        p_kernels.append(frames)
        # ipdb.set_trace()
    data_= pd.concat(p_kernels)
    # ipdb.set_trace()
    return data_

def read_data(path): 
    data=pd.read_csv(path,header=None,names=col_name_processed)
    return data


def encode_data(data):
    le = preprocessing.LabelEncoder()
    le.fit(data['inst'])
    obj1= le.transform(data['inst'])
    df=data.drop(drop,axis=1)
    df=df.apply(pd.to_numeric)
    df['inst']= obj1
    return df 

if __name__ == '__main__':
    # Process all the file in the given directory
    path= sys.argv[1]
    if(os.path.isdir(path)):
        directory= os.listdir(path)
        # import ipdb;ipdb.set_trace()
        for file in directory:
            df= null
            df= process_data_first_time(path+'/'+file)
            split=sys.argv[1].split('/')
            if os.path.isdir('processed/'+split[1])==False:
                os.mkdir('processed/'+split[1])
            df.to_csv('processed/'+ split[1]+'/'+file,index=False,header=False)
            # break
    else:
        df= process_data_first_time(path)
        df.to_csv('processed/'+path.split('/')[-2]+'/'+path.split('/')[-1],index=False,header=False)

    
    
