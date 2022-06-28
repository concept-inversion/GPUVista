from enum import unique
import sys,os
from read_features_1 import read_data
import numpy as np
from common import *
from context import context
'''
Input: trace from each kernel
Output: Context instruction for each instruction
'''     



def event_creator(df):
    event_lists=[]
    for i in range((df.shape[0])):
        kid= df.iloc[i]['kid']
        uid= df.iloc[i]['uid']
        fetch=df.iloc[i]['ibuff_time']
        issue=df.iloc[i]['issued_time']
        execute=df.iloc[i]['exe_time']
        op=df.iloc[i]['instr']
        event_lists.append({'kid':kid, 'uid':uid, 'clock':fetch, 'type':0, 'op':op })
        event_lists.append({'kid':kid, 'uid':uid, 'clock':issue, 'type':1, 'op':op})
        event_lists.append({'kid':kid, 'uid':uid, 'clock':execute, 'type':2, 'op':op})
        # import ipdb; ipdb.set_trace()
    return event_lists
  

def context_counter(event_lists):
    fetched= set()
    issued= set()
    ops= []
    count= []
    event_count=0
    for i in range(len(event_lists)):
        # ipdb.set_trace()
        data= event_lists[i]
        if data['type']==0:
            fetched.add(data['uid'])
        elif data['type']==1:
            fetched.remove(data['uid'])
            issued.add(data['uid'])
            ops.append(data['op'])
        elif data['type']==2:
            issued.remove(data['uid'])
            ops.remove(data['op'])
        count.append(len(fetched) + len(issued))
        # print("%s,%d,%d,%d,%d"%(data['op'],event_count,len(set(ops)), len(fetched), len(issued)))
        print("%s,%d,%d,%d,%d"%(ops,event_count,len(set(ops)), len(fetched), len(issued)))
        # print("%s,%d,%d,%d,%d"%(list(instr_map.keys())[list(instr_map.values()).index(data['op'])],event_count,len(set(ops)), len(fetched), len(issued)))
        event_count+=1
    return count


def benchmark_caller(df, dump_file):
    df= data.groupby(by=['kid'])
    kernels= [df.get_group(x) for x in df.groups]
    bench_max=[]
    i=0
    for frame in kernels:
        event_lists= event_creator(frame)
        sorted_list= (sorted(event_lists, key = lambda i: i['clock']))
        # count=context_counter(sorted_list)
        context_collector(frame, sorted_list, CONTEXT_LENGTH, dump_file)
        break
        bench_max.append(max(count))
        print("kernel id: %d, Max count: %d" % (i,(max(count))))
        i+=1
        break
    return bench_max


def context_collector(df, event_lists, context_length, dump_file):
    instructions= df.shape[0]
    dump_instructions=[]
    clock=0
    gpu_context= context(context_length)
    for i in range(instructions):
        inst= df.iloc[i]
        inst=inst.drop(['exe_time', 'ibuff_time', 'issued_time'])
        gpu_context.retire()
        gpu_context.add(inst)
        gpu_context.get_clock()
        gpu_context.set_retire_list(inst)
        gpu_context.dump_inst(inst, dump_file)

    print("Simulation over in cycles: ", gpu_context.clock)


if __name__ == '__main__':
    " Input processed data from read_features_1.py"
    max_count=[]
    path= sys.argv[1]
    if(os.path.isdir(path)):
        file_name= path.split('/')[-2] + ".bin"
        try:
            dump_file= open("training_data/"+file_name, "wb")
        except:
            print("Error: dump file not found")
        for file in os.listdir(path):
            print("bechmark: ", file)
            if file.endswith(".log"):
                data= read_data(path+'/'+file)
                max_count.append(benchmark_caller(data, dump_file))
    else:
        file_name= path.split('/')[-2] + ".bin"
        try:
            dump_file= open("training_data/"+file_name, "wb")
        except:
            print("Error: dump file not found")
        # import ipdb; ipdb.set_trace()
        data= read_data(path)
        max_count.append(benchmark_caller(data, dump_file))
    dump_file.close()
    # import ipdb; ipdb.set_trace()