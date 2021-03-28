import numpy as np
import pandas as pd
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from sklearn.preprocessing import MinMaxScaler
from keras import backend as K
from keras.callbacks import EarlyStopping, ModelCheckpoint
from keras.models import load_model, Sequential
from keras.layers import LSTM, Dropout, Dense
from keras.preprocessing.sequence import TimeseriesGenerator
from os import path

symbol = 'GOOGL'

data = pd.read_csv('data/stocks/{}.csv'.format(symbol))
# set invalid passing as NaN
data['Close'] = pd.to_numeric(data.Close, errors='coerce')
# drop missing values
data = data.dropna()
# train, test split
test_percent = 0.1
test_point = np.round(len(data) * test_percent)
test_index = int(len(data) - test_point)
train = data.iloc[:test_index, 1:6].values
test = data.iloc[test_index:, 1:6].values
scaler = MinMaxScaler(feature_range=(0, 1))
scaled_train = scaler.fit_transform(train)
scaled_test = scaler.fit_transform(test)

timesteps = 60
n_features = train.shape[1]
batch_size = 32
epochs = 50

x_train = []
y_train = []
x_test = []
y_test = test[timesteps:,]

for i in range(timesteps, len(train)):
    x_train.append(scaled_train[i-timesteps:i,])
    y_train.append(scaled_train[i,])

for i in range(timesteps, len(test)):
    x_test.append(scaled_test[i-timesteps:i,])

x_train, y_train = np.array(x_train), np.array(y_train)
x_train = np.reshape(x_train, (x_train.shape[0], x_train.shape[1], n_features)) # adding the batch size axis

x_test = np.array(x_test)
x_test = np.reshape(x_test, (x_test.shape[0], x_test.shape[1], n_features))

model_path = '{}.hdf5'.format(symbol)
if path.exists(model_path):
    model = load_model(model_path)
else:
    early_stop = EarlyStopping(monitor='val_loss', patience=2)

    model = Sequential()
    model.add(LSTM(100, return_sequences=True, input_shape=(timesteps, n_features)))
    model.add(Dropout(0.2))
    # model.add(LSTM(100, return_sequences=True))
    # model.add(Dropout(0.2))
    # model.add(LSTM(100, return_sequences=True))
    # model.add(Dropout(0.2))
    model.add(LSTM(50, return_sequences=False))
    model.add(Dropout(0.2))
    model.add(Dense(n_features))
    model.compile(optimizer='adam', loss='mse', metrics=['accuracy'])

    checkpoint = ModelCheckpoint(model_path, monitor='loss', verbose=1,
        save_best_only=True, mode='auto', period=1)

    hist = model.fit(x_train, y_train, batch_size, epochs, verbose=1, callbacks=[checkpoint])

    plt.plot(hist.history['loss'])
    plt.title('Training model loss')
    plt.ylabel('loss')
    plt.xlabel('epoch')
    plt.legend(['train'], loc='upper left')
    plt.show()

    plt.plot(hist.history['accuracy'])
    plt.title('Training model accuracy')
    plt.ylabel('accuracy')
    plt.xlabel('epoch')
    plt.legend(['train'], loc='upper left')
    plt.show()

# predictions
y_pred = model.predict(x_test)
predicted_price = scaler.inverse_transform(y_pred)

forecast = []
first_eval_batch = scaled_train[-timesteps:]
current_batch = first_eval_batch.reshape(1,timesteps,n_features)

for i in range(len(x_test)):
  current_pred = model.predict(current_batch)[0]
  forecast.append(current_pred)
  current_batch = np.append(current_batch[:,1:,:],[[current_pred]],axis = 1)

forecast = scaler.inverse_transform(forecast)
# forecast_index = np.arange(len(x_test),len(x_test)+60,step=1)

date_formatter = mdates.DateFormatter('%d-%m-%Y')
fig, ax = plt.subplots()
locator = mdates.DayLocator()
ax.xaxis.set_major_locator(locator)
## Rotate date labels automatically
plt.xticks(rotation=90)
ax.plot(y_test[:,3], label='Actual stock price')
ax.plot(forecast[:,3], label='Predicted stock price')
# ax.plot(data.Date[test_index+timesteps:], y_test[:,3], label='Actual stock price')
# ax.plot(data.Date[test_index+timesteps:], predicted_price[:,3], label='Predicted stock price')
plt.title('{} stock price prediction'.format(symbol))
plt.xlabel('Date')
plt.ylabel('Stock price')
plt.legend()
plt.show()
