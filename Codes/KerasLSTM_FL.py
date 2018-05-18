# use Keras LSTM to build multimodal LSTM regression model with FL fusion

# import the required modules
from __future__ import print_function
import pandas as pd
import numpy as np

from keras.models import Sequential
from keras.layers import LSTM, Merge, Dense
from keras.callbacks import EarlyStopping
from keras.optimizers import RMSprop
from keras.utils.visualize_util import plot


# define variables
nb_HRHRV_features = 10 # dimensionality of feature set 1
nb_EDA_features = 8 # dimensionality of feature set 2
nb_features = nb_HRHRV_features + nb_EDA_features # total number of features, also the number of neurons in the input layer of LSTM

time_step = 5  # the length of history (number of previous data instances) to include
batch_size = 10 # training in batches, won't influence the performance much
nb_epoch = 50 # number of total epochs to train the model

H1 = 8 # number of neurons in the bottom hidden layer
H2 = 6 # number of neurons in the middle hidden layer
H3 = 4 # number of neurons in the top hidden layer
dropout_W1 = 0.2 # drop out weight (for preventing over-fitting) in H1
dropout_U1 = 0.2 # drop out weight (for preventing over-fitting) in H1
dropout_W2 = 0.2 # drop out weight (for preventing over-fitting) in H2
dropout_U2 = 0.2 # drop out weight (for preventing over-fitting) in H2
dropout_W3 = 0.2 # drop out weight (for preventing over-fitting) in H3
dropout_U3 = 0.2 # drop out weight (for preventing over-fitting) in H3

opt_func = RMSprop(lr=0.0001) # training function

# if the validation loss isn't decreasing for a number of epochs, stop training to prevent over-fitting
early_stopping = EarlyStopping(monitor='val_loss', patience=10)

# data files
# the emotion/highlight labels we want to predict
trn_label_file = 'data/A_rating_train.csv' # training set 
tst_label_file = 'data/A_rating_devel.csv' # testing set
# feature set 1
trn_HRHRV_file = 'data/A_HRHRV_train.csv' # training set
tst_HRHRV_file = 'data/A_HRHRV_devel.csv' # test set
# feature set 2
trn_EDA_file = 'data/A_EDA_train.csv' # training set
tst_EDA_file = 'data/A_EDA_devel.csv' # test set
# output files
trn_pred_file = 'prediction/A_FL_pred_train.csv'
tst_pred_file = 'prediction/A_FL_pred_devel.csv'


# read in csv data files with panda, remove useless columns
print('Loading data...')
trn_label_raw = pd.read_csv(trn_label_file, header=None, usecols=[2])
y_train = trn_label_raw.values
tst_label_raw = pd.read_csv(tst_label_file, header=None, usecols=[2])
y_test = tst_label_raw.values
trn_HRHRV_raw = pd.read_csv(trn_HRHRV_file, header=None, usecols=range(1,nb_HRHRV_features+1))
tst_HRHRV_raw = pd.read_csv(tst_HRHRV_file, header=None, usecols=range(1,nb_HRHRV_features+1))
trn_EDA_raw = pd.read_csv(trn_EDA_file, header=None, usecols=range(1,nb_EDA_features+1))
tst_EDA_raw = pd.read_csv(tst_EDA_file, header=None, usecols=range(1,nb_EDA_features+1))

# concatenate the features (FL fusion)
trn_conc = pd.concat([trn_HRHRV_raw, trn_EDA_raw], axis=1)
tst_conc = pd.concat([tst_HRHRV_raw, tst_EDA_raw], axis=1)

# function to reshape the panda.DataFrame format data to Keras style: (batch_size, time_step, nb_features)
def reshape_data(data, n_prev = time_step):
    docX = []
    for i in range(len(data)):
        if i < (len(data)-n_prev):
            docX.append(data.iloc[i:i+n_prev].as_matrix())
        else: # the frames in the last window use the same context
            docX.append(data.iloc[(len(data)-n_prev):len(data)].as_matrix())
    alsX = np.array(docX)
    return alsX

X_train = reshape_data(trn_conc)
X_test = reshape_data(tst_conc)


# define model structure
# FL fusion: build LSTM model on top of the concatenated feature set
print('Building model...')
model = Sequential()
model.add(LSTM(H1, input_shape=(time_step, nb_features),
                     dropout_W=dropout_W1, dropout_U=dropout_U1, return_sequences=True)) # bottom hidden layer
model.add(LSTM(H2, dropout_W=dropout_W2, dropout_U=dropout_U2, return_sequences=True)) # middle hidden layer
model.add(LSTM(H3, dropout_W=dropout_W3, dropout_U=dropout_U3, return_sequences=False)) # top hidden layer
model.add(Dense(1, activation='tanh')) # output layer, regression task, value range [-1,1]
model.compile(loss='mse', optimizer=opt_func, metrics=['mse']) # define the optimizer for training, use mean squared error as the evaluation metric

# for classification, change the output node and the optimizer to the following
# model.add(Dense(1, activation='sigmoid'))
# model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])


# visualize the model structure
# plot(model, to_file='FL_model.png')

# carry out training
print('Training...')
model.fit(X_train, y_train, batch_size=batch_size, nb_epoch=nb_epoch,
          validation_data=(X_test, y_test), callbacks=[early_stopping])

# evaluation
print('Evaluating on train set...')
trn_score, trn_mse = model.evaluate(X_train, y_train, batch_size=batch_size)
print('Train mse:', trn_mse)
print('Evaluating on test set...')
tst_score, tst_mse = model.evaluate(X_test, y_test, batch_size=batch_size)
print('Test mse:', tst_mse)

# for classification
# print('Evaluating on train set...')
# trn_score, trn_acc = model.evaluate(X_train, y_train, batch_size=batch_size)
# print('Train accuracy:', trn_acc)
# print('Evaluating on test set...')
# tst_score, tst_acc = model.evaluate(X_test, y_test, batch_size=batch_size)
# print('Test accuracy:', tst_acc)


# output predictions
print('Printing predictions...')
trn_pred = model.predict(X_train)
trn_df = pd.DataFrame(trn_pred)
trn_df.to_csv(trn_pred_file, index=False, header=False)
tst_pred = model.predict(X_test)
tst_df = pd.DataFrame(tst_pred)
tst_df.to_csv(tst_pred_file, index=False, header=False)

print('Done!')
