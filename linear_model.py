# from torch.nn import nn
import torch.nn.functional as F
import torch.optim as optim
import os,sys
from data_processing.common import *
from model import *
from data_processing.read_features_1 import *
from data_processing.common import *
from sklearn.model_selection import train_test_split
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.decomposition import PCA
from sklearn.metrics import mean_squared_error, mean_absolute_error
from data_processing.read_features_1 import read_data
from matplotlib import pyplot


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
    import ipdb; ipdb.set_trace()
    fetch_loss=loss(output[:,0:1],y_train[:,0:1])
    issue_loss= loss(output[:,1:2],y_train[:,1:2])
    execution_loss= loss(output[:,2:3],y_train[:,2:3])


if __name__ == '__main__':
    # Read data
    dataset= sys.argv[1]
    #df= read_data(dataset)
    df= load_data(dataset)
    #import ipdb; ipdb.set_trace()
    #print(df.isnull().values.any())
    # df.fillna(0, inplace=True)
    output= df[:,480:481].flatten()
    #output= df[['issue_lat','execution_lat','fetch_lat']]
    inp= df[:,0:24]
    df= pd.DataFrame(inp,columns=train_cols_final)
    drop=df.columns[df.nunique() <= 1].values
    df=df.drop(drop,axis=1)
    inp=df.values
    import ipdb; ipdb.set_trace()
    X_train, X_test, y_train, y_test = train_test_split(inp, output, random_state=42, test_size=0.15)
    train_size= X_train.shape[0]
    test_size= X_test.shape[0]
    gbr_params = {'n_estimators': 1000,
                  'max_depth': 3,
                  'min_samples_split': 5,
                  'learning_rate': 0.01,
                'loss': 'ls'}
    gbr = GradientBoostingRegressor(**gbr_params)
    gbr.fit(X_train, y_train)
    # Print Coefficient of determination R^2
    mse = mean_absolute_error(y_test, gbr.predict(X_test))
    print("MSE error: %.3f "%mse)
    print("Model Accuracy: %.3f" % gbr.score(X_test, y_test))
    feature_importance = gbr.feature_importances_
    for i in range(len(train_cols_final)):
        print("%s, %.3f"%( train_cols_final[i], feature_importance[i]*100))
    #print(feature_importance)
