# from torch.nn import nn
import torch.nn.functional as F
import torch.optim as optim
import os,sys
from data_processing.common import *
from model import *
from data_processing.read_features_1 import *
from data_processing.common import *
from sklearn.model_selection import train_test_split
#import wandb
#wandb.init(project="MLGPUSim", entity="concept-inversion")

def train(model, device, train_loader, optimizer, epoch):
    ''''
    A function which trains a model with a optimizer for epochs with data from train_loader.
    '''
    pass

def load_data(file_name):
    data= np.fromfile(file_name, dtype=np.int16) 
    data=data.reshape(-1,CONTEXT_LENGTH*len(train_cols_final)+OUT_LATENCY)
    return data


def display_loss(output, y_train, loss):
    #import ipdb; ipdb.set_trace()
    fetch_loss=loss(output[:,0:1],y_train[:,0:1])
    issue_loss= loss(output[:,1:2],y_train[:,1:2])
    execution_loss= loss(output[:,2:3],y_train[:,2:3])
    print("%.2f, %.2f, %.2f"%(fetch_loss.item(),issue_loss.item(),execution_loss.item())) 

if __name__ == '__main__':
    # Read data
    dataset= sys.argv[1]
    #df= read_data(dataset)
    df= load_data(dataset)
    #import ipdb; ipdb.set_trace()
    #print(df.isnull().values.any())
    # df.fillna(0, inplace=True)
    output= df[:,(common.TRIAN_FEATURE_LEN*common.CONTEXT_LENGTH):(common.TRIAN_FEATURE_LEN*common.CONTEXT_LENGTH)+3]
    #output= df[['issue_lat','execution_lat','fetch_lat']]
    inp= df[:,0:(common.TRIAN_FEATURE_LEN*common.CONTEXT_LENGTH)]
    #import ipdb; ipdb.set_trace()
    # print(inp.shape[1])
    X_train, X_test, y_train, y_test = train_test_split(inp, output, random_state=42, test_size=0.15)
    train_size= X_train.shape[0]
    test_size= X_test.shape[0]
    batchsize= 128
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    batchnum = int(train_size/batchsize)
    loss=nn.L1Loss()
    model=CNN(common.OUT_LATENCY)
    model.to(device)
    optimizer = optim.SGD(model.parameters(), lr=0.01, momentum=0.5)
    # train()
    epoch=200
    print(X_train.shape,y_train.shape)
    X_test= torch.from_numpy(X_test).float().to(device)
    y_test= torch.from_numpy(y_test).float().to(device)
    t_loss=0
    for i in range(epoch):
        for j in range(batchnum-1):
            #import ipdb;ipdb.set_trace()
            x_train= X_train[j*batchsize:(j+1)*batchsize]
            Y_train= y_train[j*batchsize:(j+1)*batchsize]
            x_train= torch.from_numpy(x_train).float().to(device)
            Y_train= torch.from_numpy(Y_train).float().to(device)
            # print(x_train.shape)
            output= model(x_train)
            #print(output.shape, Y_train.shape)
            loss_= loss(output, Y_train)
            #display_loss(output,Y_train,loss)
            t_loss= loss_.item()
            #print(loss_)
            optimizer.zero_grad()
            loss_.backward()
            optimizer.step()
        #X_test= torch.from_numpy(X_test.values).float().to(device)
        #x_train= torch.from_numpy(x_train.values).float().to(device)
        #wandb.log({"Train loss": loss.item()})
        #ipdb.set_trace()
        out_= model(X_test)
        v= loss(out_, y_test)
        #print(out_)
        #display_loss(out_,y_test,loss)
        #wandb.log({"Test loss": v.item()})
        print('Epoch:', i, ' Train Loss:', t_loss, ' Test Loss:',v.item(),end=", " )
        display_loss(out_,y_test,loss)

        
