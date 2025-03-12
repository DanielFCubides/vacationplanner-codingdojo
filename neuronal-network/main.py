import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


def preprocesing(flight_data):
    # Extract relevant features
    features = flight_data[
        ['flight_1_from', 'flight_1_to', 'flight_1_price', 'flight_2_from', 'flight_2_to',
         'flight_2_price', 'similarity']]

    features = pd.get_dummies(features, columns=['flight_1_from', 'flight_1_to', 'flight_2_from', 'flight_2_to'])

    target = (flight_data['similarity'] >= 1).astype(int)

    X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=42)
    # Normalize numerical features
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    input_dim = X_train.shape[1]
    return input_dim, X_train, y_train,


def preprocesing_experiment(flight_data):
    # Extract relevant features
    features = flight_data[
        ['flight_1_from', 'flight_1_to', 'flight_1_price', 'flight_2_from', 'flight_2_to',
         'flight_2_price']]

    features = pd.get_dummies(features, columns=['flight_1_from', 'flight_1_to', 'flight_2_from', 'flight_2_to'])


    scaler = StandardScaler()
    X_train = scaler.fit_transform(features)
    X_train = scaler.transform(X_train)
    return X_train


def train_model(flight_data):
    input_dim, X_train, y_train = preprocesing(flight_data)
    model = Sequential([
        Dense(6, activation='relu', input_dim=input_dim),
        Dropout(0.2),
        Dense(36, activation='relu'),
        Dropout(0.2),
        Dense(1, activation='sigmoid')
    ])
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

    model.summary()

    model.fit(
        X_train, y_train,
        epochs=50,  # Maximum number of training rounds
        batch_size=200,  # Process 32 samples before updating weights
        validation_split=0.2,  # Use 20% of training data for validation
        callbacks=[]  # Stop when validation loss stops improving
    )


    model.save('model.keras')

    return model


def print_hi(name):
    flight_data = pd.read_csv('flights.csv')
    model = train_model(flight_data)
    flight_data_exp = pd.read_csv('flights_exp.csv')
    x_train = preprocesing_experiment(flight_data_exp)
    print(flight_data_exp.iloc[12])
    result = model.predict(x_train)
    print(result)

    print(f'Hi', ' {name}')  # Press ⌘F8 to toggle the breakpoint.


if __name__ == '__main__':
    print_hi('PyCharm')
