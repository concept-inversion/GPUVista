from enum import unique
import sys,os
from read_features_1 import read_data
import numpy as np
from common import *
from context import context
import argparse
'''
Input: trace from each kernel
Output: Context instruction for each instruction
'''     



def benchmark_caller(df, file_name, dump_file):
    df= data.groupby(by=['kid'])
    kernels= [df.get_group(x) for x in df.groups]
    print(file_name,len(kernels))
    bench_max=[]
    i=0
    for frame in kernels:
        out_name= file_name+'_kernel+'+str(i)
        event_lists= event_creator(frame)
        sorted_list= (sorted(event_lists, key = lambda i: i['clock']))
        # count=context_counter(sorted_list)
        clock=context_collector(frame, sorted_list, CONTEXT_LENGTH, dump_file)
        #bench_max.append(max(count))
        print("kernel id: %d, Cycle: %d" % (i,clock))
        i+=1
    return bench_max


if __name__ == '__main__':
    " Input: processed data from read_features_1.py"
    parser = argparse.ArgumentParser(description='Input: processed/<directory> Output: <Training_data>')
    max_count=[]
    path= sys.argv[1]
    if(os.path.isdir(path)):
        file_name= path.split('/')[-2] + ".bin"
        try:
            dump_file= open("test_kernels/"+file_name, "wb")
        except:
            print("Error: dump file not found")
        for file in os.listdir(path):
            #print("bechmark: ", file)
            if file.endswith(".log"):
                data= read_data(path+'/'+file)
                max_count.append(benchmark_caller(data, file, dump_file))
    else:
        file_name= path.split('/')[-2] + ".bin"
        try:
            dump_file= open("training_data/"+file_name, "wb")
        except:
            print("Error: dump file not found")
        # import ipdb; ipdb.set_trace()
        data= read_data(path)
        max_count.append(benchmark_caller(data, file, dump_file))
    dump_file.close()
    # import ipdb; ipdb.set_trace()
