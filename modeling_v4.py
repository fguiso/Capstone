# Usage: python -u modeling_v4.py hidden_dim bsize ep LR
#!/bin/bash

# Import packages
import numpy as np
import random
import torch
from torch import nn
from torch import optim
from torch.utils.data import random_split
import matplotlib.pyplot as plt
import sys
import pandas as pd

hidden_dim = sys.argv[1]
bsize = sys.argv[2]
ep = sys.argv[3]
LR = sys.argv[4]

hidden_dim = int(hidden_dim)
bsize = int(bsize)
ep = int(ep)
LR = float(LR)
print( 'hidden dim:', hidden_dim, 'batch size:', bsize, 'epoch:', ep, 'learning rate:', LR)

print('loading data')
X = pd.read_csv('X_train.csv')
y = pd.read_csv('y_train.csv')
X = X.sort_values(by  = 'time')
y = y.sort_values(by = 'time')
assert np.max(X['time']) == np.max(y['time'])
X = X.drop(['time'], axis = 1)
y = y.drop(['time'], axis = 1)
X_tensor = torch.from_numpy(np.array(X)).float()
y_tensor = torch.from_numpy(np.array(y)).float()
assert len(X_tensor) == len(y_tensor)
assert X_tensor.size()[1] == 1877
assert y_tensor.size()[1] == 4385
print("X and y shape:", X_tensor.size(), y_tensor.size())
print('done loading')

# Set up device
cuda = torch.cuda.is_available()
device = torch.device("cuda:0" if cuda else "cpu")
print('device:',device)

seed = 1006
random.seed(seed)
np.random.seed(seed)
torch.manual_seed(seed)
if cuda:
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True


# Train, val, test
train_ratio = 0.6
validation_ratio = 0.2
test_ratio = 0.2

train_length = int(np.floor(train_ratio*len(X_tensor)))

X_train_data_tensor, X_val_data_tensor = X_tensor[:train_length].float(), X_tensor[train_length+1:].float()
y_train_data_tensor, y_val_data_tensor = y_tensor[:train_length].float(), y_tensor[train_length+1:].float()
print('X train, val sizes:', X_train_data_tensor.size(), X_val_data_tensor.size())
print('y train, val sizes:', y_train_data_tensor.size(), y_val_data_tensor.size())

val_length = int(np.floor(0.5*len(X_val_data_tensor)))

X_val_data_tensor, X_test_data_tensor = X_tensor[train_length+1:train_length+val_length].float(), X_tensor[train_length+val_length+1:train_length+2*val_length].float()
y_val_data_tensor, y_test_data_tensor = y_tensor[train_length+1:train_length+val_length].float(), y_tensor[train_length+val_length+1:train_length+2*val_length].float()
print('X train, val, test sizes:', X_train_data_tensor.size(), X_val_data_tensor.size(), X_test_data_tensor.size())
print('y train, val, test sizes:', y_train_data_tensor.size(), y_val_data_tensor.size(), y_test_data_tensor.size())

print('indices train:', 0, train_length)
print('indices val:', train_length+1, train_length+val_length)
print('indices test:', train_length+val_length+1, train_length+2*val_length)

input_dim = 1877
output_dim = 4385
print('input, output, hidden dim:',input_dim, output_dim, hidden_dim)

# Define model
model = nn.Sequential(
    nn.Linear(input_dim,hidden_dim),
    nn.Sigmoid(),
    nn.Linear(hidden_dim,hidden_dim),
    nn.Sigmoid(),
    nn.Linear(hidden_dim,output_dim),
    nn.Sigmoid()
)

params = list(model.parameters())

# Define optimizer
optimizer = optim.SGD(params, lr=LR)

# Define loss
loss_criterion = nn.BCELoss()

# Training loop
def train(model, batch_size, epochs, x, y, x_val, y_val, optimizer, criterion):
    print('inside train loop sizes:', x.size(), y.size(), x_val.size(), y_val.size())
    x, y = x.to(device), y.to(device)
    x_val, y_val = x_val.to(device), y_val.to(device)

    model.to(device)
    model.train()

    num_batches = (len(x)+batch_size-1) // batch_size # floor operator
    print('number of batches:',num_batches)
    losslists = []
    vlosslists = []
    for epoch in range(epochs):

        torch.cuda.empty_cache()

        losses = list()
        for b in range(num_batches):

            b_start = b * batch_size
            b_end = (b + 1) * batch_size
            #print('b_start and b_end:', b_start, b_end, flush = True)
            #print('x and y size', x.size(), y.size(), flush =True)
            x_batch = x[b_start:b_end]
            y_batch = y[b_start:b_end]

            torch.cuda.empty_cache()

            y_pred = model(x_batch) # logits
            #print('y pred',y_pred)
            loss = criterion(y_pred, y_batch)
            #print('loss',loss)

            model.zero_grad()

            loss.backward()

            optimizer.step()

            losses.append(loss.item())
            # print(loss.item(), losses)
        losslists.append(np.mean(losses))
        print('Training loss: {}, {}'.format(loss.item(), torch.tensor(losses).mean() ))

        model.eval()

        vlosses = list()

        with torch.no_grad():
            y_pred_val = model(x_val)

            vloss = criterion(y_pred_val, y_val)

            vlosses.append(vloss.item())
        vlosslists.append(torch.tensor(vlosses).mean())

        print('Validation loss: {}, {}'.format(vloss.item(), torch.tensor(vlosses).mean() ))
        if (epoch+1) % 20 == 0:
            print('Epoch {} loss: {}, {}'.format(epoch+1, loss.item(), torch.tensor(losses).mean() ))

        if torch.tensor(losses).mean() < 1e-2:
            print('Epoch {} loss: {}, {}'.format(epoch+1, loss.item(), torch.tensor(losses).mean() ))
            break
    return y_pred.detach(), y_pred_val.detach(), losslists, vlosslists

def validation(model, x, y, criterion):

    model.eval()

    losses = list()

    with torch.no_grad():
        y_pred = model(x)
        print(y_pred)

    loss = criterion(y_pred, y)

    losses.append(loss.item())
    print('Validation loss: {}, {}'.format(loss.item(), torch.tensor(losses).mean() ))

    return y_pred.detach(), losses

# Training data
x = X_train_data_tensor
y_true = y_train_data_tensor
print('number of changes in training set:',np.sum(np.array(y_true),axis=1))

# Set number of epochs
#ep = 100
#bsize = int(subset_size//10)
print('batch size',bsize)
x_val = X_val_data_tensor
y_val_true = y_val_data_tensor
#print('epochs:',ep)
#print('len x:',len(x)/5, int(len(x)/5))

y_pred, y_val_pred, train_losses, val_losses = train(model, batch_size=bsize, epochs=ep, x=x, y=y_true, x_val = x_val, y_val = y_val_true, optimizer=optimizer, criterion = loss_criterion)
torch.cuda.empty_cache()

# Validation data
print('number of changes in validation set:',np.sum(np.array(y_val_true),axis=1))

fig = plt.figure(figsize=(7,7))
plt.plot(train_losses)
plt.plot(val_losses)
plt.title('Train & Validation Loss')
plt.legend(['Train', 'Validation'], loc='upper right')
plt.title('Trainning and Validation Losses')
#plt.close()
plt.savefig('loss_hdim{}_bs{}_ep{}_lr{}.png'.format(hidden_dim,bsize,ep,LR))

# Use model to predict next state given previous state's prediction
n = 1
# Predict first state
x_new = X_val_data_tensor[0:n,:].float()
x_new = x_new.to(device)
print(len(x_new))
# Generate first prediction
y_new = y_val_data_tensor[0:n,:].float().to(device)
print(len(y_new))

print('len validation',len(x_val))

# Store generated predictions
y_gen = list()
# Store losses
losses_list = list()
# Loop over validation set
for n in range(1,len(x_val)):
    # Predict next state using trained model
    y_next, losses = validation(model, x=x_new, y=y_new, criterion = loss_criterion)
    # print('y_next:', 1*(np.array(y_next)>0.5), np.sum(np.array(y_next)), len(y_next))

    # Update new input to be the prediction of the previous state
    y_next = y_next.cpu()
    x_new = torch.from_numpy(1*(np.array(y_next)>0.5)).float().to(device)

    # Update ground truth
    y_new = y_val_data_tensor[n-1:n,input_dim:].float().to(device)
    # print('y_new:',np.sum(np.array(y_new)), len(y_new))

    losses_list.append(losses)

    # Store generated predictions
    y_gen.append( (y_next>0.5).float().numpy() )

print('generate a new input to model based on iterative predictions')

# Convert predictions to binary
y_gen = y_gen.cpu()
gen_data = torch.from_numpy(1*(np.array(y_gen)>0.5)).float()
gen_data = gen_data.to(device)
#print(gen_data)
#print(np.sum(1*(np.array(y_gen)>0.5),0))

#print(gen_data.shape)
# Reshape [n x d]
gen_data = gen_data.view((len(y_gen),input_dim),-1)
print('reshaped:',gen_data.shape)

# Store losses
losses_new = list()
print('validate input made up of n successive states')
# Loop over number of successive steps
for n in range(1,len(x_val)-1):
    x_new = gen_data[0:n].float().to(device)
    y_new = y_val_data_tensor[0:n,input_dim:].float().to(device)
    # Predict next state using trained model
    print(x_new.size(), y_new.size())
    y_next, losses = validation(model, x=x_new, y=y_new, criterion = loss_criterion)
    # print('y_next:', 1*(np.array(y_next)>0.5), np.sum(np.array(y_next)), len(y_next))
    losses_new.append(losses)

print(np.array(losses_new).shape)
fig = plt.figure(figsize=(7,7))
plt.plot(np.arange(0,n,n/len(losses_new)),losses_new)
plt.xlabel('n')
plt.ylabel('BCELoss')
plt.title('BCELoss predicting n successive steps')
#plt.close()
plt.savefig('figure2.png')
