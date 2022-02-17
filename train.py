# from torch.nn import nn
import torch.nn.functional as F
import torch.optim as optim
import os,sys
from common import *
from model import *
from dp import *
from sklearn.model_selection import train_test_split

def train(model, device, train_loader, optimizer, epoch):
    ''''
    A function which trains a model with a optimizer for epochs with data from train_loader.
    '''




if __name__ == '__main__':
    # Read data
    dataset= sys.argv[1]
    df= read_data(dataset)
    output= df[['issue','execution']]
    inp= df.drop(['issue','execution'],axis=1)
    X_train, X_test, y_train, y_test = train_test_split(inp, output, random_state=42, test_size=0.1)
    train_size= X_train.shape[0]
    test_size= X_test.shape[0]
    batchsize= 8192
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    batchnum = int(train_size/batchsize)
    loss=nn.L1Loss()
    model= FC()
    model.to(device)
    optimizer = optim.SGD(model.parameters(), lr=0.01, momentum=0.5)
    # train()
    epoch=100
    print(X_train.shape,y_train.shape)
    X_test= torch.from_numpy(X_test.values).float().to(device)
    y_test= torch.from_numpy(y_test.values).float().to(device)
    for i in range(epoch):
        for j in range(batchnum-1):
            # import ipdb;ipdb.set_trace()
            x_train= X_train[j*batchsize:(j+1)*batchsize]
            Y_train= y_train[j*batchsize:(j+1)*batchsize]
            # print(Y_train.shape)
            #print( np.max(Y_train['issue'].values), np.max(Y_train['execution'].values))
            #import ipdb;ipdb.set_trace()
            x_train= torch.from_numpy(x_train.values).float().to(device)
            Y_train= torch.from_numpy(Y_train.values).float().to(device)
            # print(x_train.shape)
            output= model(x_train)
            loss_= loss(output, Y_train)
            #print(loss_)
            optimizer.zero_grad()
            loss_.backward()
            optimizer.step()
        #X_test= torch.from_numpy(X_test.values).float().to(device)
        #x_train= torch.from_numpy(x_train.values).float().to(device)
        out_= model(X_test)
        v= loss(out_, y_test)
        print('Epoch:', i, ' Train Loss:', loss_.item(), ' Test Loss:',v.item() )

        
