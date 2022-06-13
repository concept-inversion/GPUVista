import data_processing.common as common
import torch
import torch.nn as nn
import torch.nn.functional as F


class FC(nn.Module):
    def __init__(self):
        super(FC, self).__init__()
        self.fc1 = nn.Linear(common.FEATURE_LENGTH, 256)
        self.fc2 = nn.Linear(256, 128)
        self.fc3 = nn.Linear(128, common.OUT_LATENCY)
    def forward(self, x):
        # print(x.shape)
        x=x.view(-1, common.FEATURE_LENGTH)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x    

class CNN(nn.Module):
    def __init__(self,out):
        super(CNN, self).__init__()
        self.conv1 = nn.Conv1d(in_channels=common.INPUT_SIZE, out_channels=32, kernel_size=5)
        self.conv2 = nn.Conv1d(in_channels=32, out_channels=64, kernel_size=5)
        self.conv3 = nn.Conv1d(in_channels=64, out_channels=32, kernel_size=5)
        self.f1_input=32*common.INPUT_SIZE
        self.fc1 = nn.Linear(self.f1_input, 256)
        self.fc2 = nn.Linear(256, 2)
    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv2(x))
        x = F.relu(self.conv3(x))
        x=x.view(-1, self.f1_input)
        x=  F.relu(self.fc1(x))
        x = self.fc2(x)
        return x