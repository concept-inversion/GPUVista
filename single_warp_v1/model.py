import data_processing.common as common
import torch
import torch.nn as nn
import torch.nn.functional as F
import ipdb

class FC(nn.Module):
    def __init__(self, out):
        super(FC, self).__init__()
        self.fc1 = nn.Linear(common.TRIAN_FEATURE_LEN, 256)
        self.fc2 = nn.Linear(256, 128)
        self.fc3 = nn.Linear(128, common.OUT_LATENCY)
    def forward(self, x):
        # print(x.shape)
        #ipdb.set_trace()
        x=x.view(-1, common.TRIAN_FEATURE_LEN)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x    
        
class CNN(nn.Module):
    def __init__(self,out):
        super(CNN, self).__init__()
        self.conv1 = nn.Conv1d(in_channels=common.TRIAN_FEATURE_LEN, out_channels=256, kernel_size=5)
        #self.conv1_bn=nn.BatchNorm2d(32)
        self.conv2 = nn.Conv1d(in_channels=256, out_channels=128, kernel_size=5)
        self.dropout1=nn.Dropout(0.1)
        self.conv3 = nn.Conv1d(in_channels=128, out_channels=32, kernel_size=3)
        self.f1_input= 32*(common.CONTEXT_LENGTH-5-5-3+3)
        self.fc1 = nn.Linear(self.f1_input, 256)
        self.fc2 = nn.Linear(256, out)
    def forward(self, x):
        #x=x.view(-1,common.TRIAN_FEATURE_LEN,common.CONTEXT_LENGTH)
        x=x.view(-1,common.CONTEXT_LENGTH,common.TRIAN_FEATURE_LEN).transpose(2,1)
        #ipdb.set_trace()
        #x=x.view(-1,common.TRIAN_FEATURE_LEN)
        #print(x.shape)
        x = F.relu(self.conv1(x))
        #print(x.shape)
        x = F.relu(self.conv2(x))
        #print(x.shape)
        x = self.dropout1(x)
        x = F.relu(self.conv3(x))
        #print(x.shape)
        x=x.view(-1, self.f1_input)
        #print(x.shape)
        x=  F.relu(self.fc1(x))
        #print(x.shape)
        x = self.fc2(x)
        #print(x.shape)
        return x
