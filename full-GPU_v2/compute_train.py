# from torch.nn import nn
import numpy as np
import torch.nn.functional as F
import torch.optim as optim
import os,sys
from model import *
from sklearn.model_selection import train_test_split
from common import *
import ipdb
#import wandb
#wandb.init(project="MLGPUSim", entity="concept-inversion")

def train(model, device, train_loader, optimizer, epoch):
    ''''
    A function which trains a model with a optimizer for epochs with data from train_loader.
    '''
    pass

def save_model(name, model):
    traced_script_module = torch.jit.trace(model, torch.rand(1, BLOCK_FEATURE*BLOCK_CONTEXT).to(device))
    traced_script_module.save(name)

def load_model(name, model):
    cp = torch.load(name, map_location=torch.device('cpu'))
    model.load_state_dict(cp['model_state_dict'])

def load_data(dataset):
    #ipdb.set_trace()
    model_name= 'block'
    #inp_file= open(dataset+'/'+model_name+"_inp.bin", "wb")
    inp_file= dataset+model_name+"_inp.bin"
    out_file= dataset+model_name+"_out.bin"
    #out_file= open(dataset+'/'+model_name+"_out.bin", "wb")
    inp_data= np.fromfile(inp_file, dtype=np.int32) 
    out_data= np.fromfile(out_file, dtype=np.int32)
    inp_data= inp_data.reshape(-1,BLOCK_FEATURE,BLOCK_CONTEXT)
    out_data= out_data.reshape(-1, 2) 
    ipdb.set_trace()
    assert out_data.shape[0]==inp_data.shape[0]
    #ipdb.set_trace()
    return inp_data, out_data

def display_loss(output, y_train, loss):
    #import ipdb; ipdb.set_trace()
    fetch_loss=loss(output[:,0:1],y_train[:,0:1])
    issue_loss= loss(output[:,1:2],y_train[:,1:2])
    execution_loss= loss(output[:,2:3],y_train[:,2:3])
    print("%.2f, %.2f, %.2f"%(fetch_loss.item(),issue_loss.item(),execution_loss.item())) 

if __name__ == '__main__':
    dataset= sys.argv[1]
    inp_data, out_data= load_data(dataset)
    #ipdb.set_trace()
    X_train, X_test, y_train, y_test = train_test_split(inp_data, out_data, random_state=42, test_size=0.15)
    train_size= X_train.shape[0]
    test_size= X_test.shape[0]
    batchsize= 128
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    batchnum = int(train_size/batchsize)
    loss=nn.L1Loss()
    #model=CNN(common.OUT_LATENCY)
    model=CNN_block(BLOCK_INPUT_SIZE, 2)
    model.to(device)
    optimizer = optim.SGD(model.parameters(), lr=0.01, momentum=0.5)
    # train()
    epoch=200
    print(X_train.shape,y_train.shape)
    X_test= torch.from_numpy(X_test).float().to(device)
    y_test= torch.from_numpy(y_test).float().to(device).type(torch.int)
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
            #print(t_loss)
            optimizer.zero_grad()
            loss_.backward()
            optimizer.step()
        #wandb.log({"Train loss": loss.item()})
        #ipdb.set_trace()
        out_= model(X_test).type(torch.int).type(torch.float)
        v= loss(out_, y_test)
        if i%20==0:
            print()
            #save_model(name,model)
        #print(out_)
        #display_loss(out_,y_test,loss)
        #wandb.log({"Test loss": v.item()})
        print('Epoch:', i, ' Train Loss:', t_loss, ' Test Loss:',v.item() )
        #display_loss(out_,y_test,loss)

        
