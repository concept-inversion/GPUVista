import numpy as np
import pandas as pd

class scheduler:
    '''
        This function is used to update the scheduler.        
    '''
    def __init__(self, warp_pool, num_warps, scheduler):
        self.cols=['warps','total_inst','inst_index','ready','running','order']
        self.data=pd.DataFrame(columns=self.cols)
        self.warp_pool= warp_pool
        self.num_warps= num_warps
        self.scheduler= scheduler
        self.running= []
        self.ready= []

    def next(self, data):
        if self.scheduler=='rr':
            return self.round_robin(data)
        elif self.scheduler=='lrr':
            return self.least_recently_used(data)
        elif scheduler=='gto':
            return self.greedy_than_old(data)
        pass

    def update(self, data):
        
        pass


    def round_robin(self, data):
        """ issued cycle,  """
        pass

    def greedy_than_old(self, data):
        pass

    def least_recently_used(self, data):
        pass

class warp_tracker:
    '''
    This function is used to update the warp tracker.
    '''
    def __init__(self, warp_pool, num_warps):
        self.cols= ['warp_id','retire_cycle']
        self.data=[]
        self.warp_pool= warp_pool
        self.num_warps= num_warps

    def add(self, warp_id, inst_id, instruction, latency):
        self.data= self.data.append({'warp_id':warp_id,'inst_id':inst_id,'retire_cycle':latency, 'inst':instruction}, ignore_index=True)
        pass

    def retire(self, clock):
        len= len(self.data)
        for i in range(len):
            retire= self.data[i]['retire_cycle']
            if retire<=clock:
                self.data.drop(self.data.index[i], inplace=True)
                self.num_warps-=1
        
    def dump_instruction(self):
        len= len(self.data)
        for i in range(len):
            output=output.append(self.data[i]['inst'])
        return output
