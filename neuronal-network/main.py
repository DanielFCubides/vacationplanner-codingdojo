import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import tensorflow as tf
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import Dense, Dropout, Input, Concatenate
import datetime
import matplotlib.pyplot as plt
import seaborn as sns


def convert_time_to_minutes(time_str):
    """Convert time string (HH:MM:SS) to minutes since midnight."""
    try:
        t = datetime.datetime.strptime(time_str, '%H:%M:%S')
        return t.hour * 60 + t.minute + t.second / 60
    except:
        return np.nan


def feature_engineering(df):
    """Create meaningful features for flight similarity comparison."""
    # Make a copy to avoid modifying the original
    df_copy = df.copy()

    # Convert times to numerical values (minutes)
    df_copy['flight_1_minutes'] = df_copy['Flight_1_time'].apply(convert_time_to_minutes)
    df_copy['flight_2_minutes'] = df_copy['Flight_2_time'].apply(convert_time_to_minutes)

    # Create new features
    # Price difference between flights
    df_copy['price_diff'] = abs(df_copy['flight_1_price'] - df_copy['flight_2_price'])
    df_copy['price_ratio'] = df_copy['flight_1_price'] / df_copy['flight_2_price']

    # Time difference between flights
    df_copy['time_diff'] = abs(df_copy['flight_1_minutes'] - df_copy['flight_2_minutes'])

    # Route similarity features
    df_copy['same_origin'] = (df_copy['flight_1_from'] == df_copy['flight_2_from']).astype(int)
    df_copy['same_destination'] = (df_copy['flight_1_to'] == df_copy['flight_2_to']).astype(int)
    df_copy['reversed_route'] = ((df_copy['flight_1_from'] == df_copy['flight_2_to']) &
                                 (df_copy['flight_1_to'] == df_copy['flight_2_from'])).astype(int)

    # Features for connections
    df_copy['possible_connection'] = ((df_copy['flight_1_to'] == df_copy['flight_2_from']) &
                                      (df_copy['flight_1_minutes'] < df_copy['flight_2_minutes'])).astype(int)

    # Drop the original time columns as we now have numerical versions
    df_copy.drop(['Flight_1_time', 'Flight_2_time'], axis=1, inplace=True)

    return df_copy


def create_preprocessing_pipeline():
    """Create a consistent preprocessing pipeline for both training and prediction."""
    # Define categorical and numerical columns
    categorical_cols = ['flight_1_from', 'flight_1_to', 'flight_2_from', 'flight_2_to']
    numerical_cols = ['flight_1_price', 'flight_2_price', 'flight_1_minutes', 'flight_2_minutes',
                      'price_diff', 'price_ratio', 'time_diff']
    binary_cols = ['same_origin', 'same_destination', 'reversed_route', 'possible_connection']

    # Create transformers
    categorical_transformer = OneHotEncoder(handle_unknown='ignore')
    numerical_transformer = StandardScaler()

    # Create preprocessing steps
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', categorical_transformer, categorical_cols),
            ('num', numerical_transformer, numerical_cols),
            # Binary columns don't need transformation
            ('pass', 'passthrough', binary_cols)
        ])

    return preprocessor


def build_similarity_model(input_dim):
    """Build a neural network model for flight similarity prediction."""
    model = Sequential([
        Dense(64, activation='relu', input_dim=input_dim),
        Dropout(0.3),
        Dense(32, activation='relu'),
        Dropout(0.3),
        Dense(32, activation='relu'),
        Dropout(0.3),
        Dense(32, activation='relu'),
        Dropout(0.3),
        Dense(32, activation='relu'),
        Dropout(0.3),
        Dense(1, activation='sigmoid')  # Output between -1-1 for similarity
    ])


    model.compile(
        optimizer='adam',
        loss='binary_crossentropy',
        metrics=['accuracy', tf.keras.metrics.AUC(), tf.keras.metrics.Precision(), tf.keras.metrics.Recall()]
    )

    return model


def train_model(train_data_path):
    """Train the flight similarity model."""
    # Load data
    print("Loading and preprocessing data...")
    flight_data = pd.read_csv(train_data_path)

    # Check if we have similarity values in the dataset
    if 'similarity' not in flight_data.columns:
        raise ValueError("Training data must include 'similarity' column")

    # Feature engineering
    processed_data = feature_engineering(flight_data)

    # Prepare features and target
    X = processed_data.drop('similarity', axis=1)
    y = (processed_data['similarity'] >= 1).astype(int)  # Convert to binary

    # Split the data
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

    # Create and fit the preprocessing pipeline
    preprocessor = create_preprocessing_pipeline()
    X_train_processed = preprocessor.fit_transform(X_train)
    X_val_processed = preprocessor.transform(X_val)

    # Get input dimension after preprocessing
    input_dim = X_train_processed.shape[1]

    # Build and train the model
    print(f"Building model with input dimension: {input_dim}")
    model = build_similarity_model(input_dim)

    # Define callbacks
    callbacks = [
        tf.keras.callbacks.EarlyStopping(patience=10, restore_best_weights=True),
        tf.keras.callbacks.ReduceLROnPlateau(factor=0.2, patience=5)
    ]

    # Train the model
    print("Training model...")
    history = model.fit(
        X_train_processed, y_train,
        epochs=100,
        batch_size=32,
        validation_data=(X_val_processed, y_val),
        callbacks=callbacks,
        verbose=1
    )

    # Evaluate the model
    print("Evaluating model...")
    evaluation = model.evaluate(X_val_processed, y_val)
    print(f"Validation metrics: {dict(zip(model.metrics_names, evaluation))}")

    # Save the model and preprocessor
    model.save('flight_similarity_model.keras')
    import joblib
    joblib.dump(preprocessor, 'flight_preprocessor.joblib')

    # Plot training history
    plt.figure(figsize=(12, 4))
    plt.subplot(1, 2, 1)
    plt.plot(history.history['loss'])
    plt.plot(history.history['val_loss'])
    plt.title('Model Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend(['Train', 'Validation'])

    plt.subplot(1, 2, 2)
    plt.plot(history.history['accuracy'])
    plt.plot(history.history['val_accuracy'])
    plt.title('Model Accuracy')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.legend(['Train', 'Validation'])

    plt.tight_layout()
    plt.savefig('training_history.png')
    plt.close()

    return model, preprocessor


def predict_similarity(model, preprocessor, test_data_path):
    """Predict similarity scores for new flight pairs."""
    # Load test data
    flight_data_exp = pd.read_csv(test_data_path)

    # Apply the same feature engineering
    processed_data = feature_engineering(flight_data_exp)

    # Apply the same preprocessing
    X_test_processed = preprocessor.transform(processed_data)

    # Make predictions
    similarity_scores = model.predict(X_test_processed)

    # Add predictions to the original data
    results = flight_data_exp.copy()
    results['similarity_score'] = similarity_scores

    # Save results
    results.to_csv('flight_similarity_predictions.csv', index=False)

    return results


def create_synthetic_training_data(csv_path, n_samples=1000):
    """Create synthetic training data with varied similarity scores for training purposes."""
    # Load the base data without similarity scores
    if not os.path.exists(csv_path):
        print(f"File not found: {csv_path}")
        return None

    flight_data = pd.read_csv(csv_path)

    # Sample n_samples rows for creating training data
    if len(flight_data) > n_samples:
        flight_sample = flight_data.sample(n_samples, random_state=42)
    else:
        flight_sample = flight_data.copy()

    # Apply feature engineering to extract useful features
    processed_data = feature_engineering(flight_sample)

    # Create similarity scores based on features
    # This is a heuristic approach - in a real scenario, you'd have actual labeled data

    # Normalize numerical features for scoring
    processed_data['price_diff_norm'] = processed_data['price_diff'] / processed_data['price_diff'].max()
    processed_data['time_diff_norm'] = processed_data['time_diff'] / processed_data['time_diff'].max()

    # Create a composite similarity score (0-1 range)
    processed_data['similarity'] = (
        # Route similarity (highest weight)
            (processed_data['same_origin'] * 0.3) +
            (processed_data['same_destination'] * 0.3) +
            (processed_data['reversed_route'] * 0.2) +
            # Price similarity (inverse of difference)
            ((1 - processed_data['price_diff_norm']) * 0.1) +
            # Time similarity (inverse of difference)
            ((1 - processed_data['time_diff_norm']) * 0.1)
    )

    # Drop the temporary normalized columns
    processed_data.drop(['price_diff_norm', 'time_diff_norm'], axis=1, inplace=True)

    # Convert back to the original format with the new similarity score
    # Get only the original columns plus the similarity
    original_cols = list(flight_sample.columns) + ['similarity']
    synthetic_data = processed_data[original_cols]

    # Save the synthetic training data
    synthetic_data.to_csv('synthetic_training_data.csv', index=False)

    print(f"Created synthetic training data with {len(synthetic_data)} samples")
    print(f"Similarity score distribution:")
    print(synthetic_data['similarity'].describe())

    # Plot the distribution of similarity scores
    plt.figure(figsize=(10, 6))
    sns.histplot(synthetic_data['similarity'], bins=20)
    plt.title('Distribution of Synthetic Similarity Scores')
    plt.savefig('similarity_distribution.png')
    plt.close()

    return synthetic_data


def main():
    model, os, preprocessor = execute_trainning()
    print(f"Training summary: {model.summary()}")
    # Predict similarities for experimental data
    if os.path.exists('flights_exp.csv'):
        results = predict_similarity(model, preprocessor, 'flights_exp.csv')
        print(f"Predicted similarities for {len(results)} flight pairs")
        print(results[['flight_1_from', 'flight_1_to', 'flight_2_from', 'flight_2_to', 'similarity_score']].head(10))
    else:
        print("No experimental data found for predictions.")


def execute_trainning():
    import os

    if os.path.exists('flights.csv'):
        # Check if we need to create synthetic data
        flight_data = pd.read_csv('flights.csv')

        if 'similarity' in flight_data.columns:
            similarity_values = flight_data['similarity'].unique()
            if len(similarity_values) <= 1:
                print("Training data has limited similarity values. Creating synthetic data...")
                # Create synthetic data with varied similarity scores
                create_synthetic_training_data('flights_exp.csv', n_samples=1000)
                train_data_path = 'synthetic_training_data.csv'
            else:
                train_data_path = 'flights.csv'
        else:
            print("Training data missing similarity column. Creating synthetic data...")
            create_synthetic_training_data('flights_exp.csv', n_samples=1000)
            train_data_path = 'synthetic_training_data.csv'
    else:
        print("No training data found. Creating synthetic data...")
        create_synthetic_training_data('flights_exp.csv', n_samples=1000)
        train_data_path = 'synthetic_training_data.csv'
    # Train the model
    model, preprocessor = train_model(train_data_path)
    return model, os, preprocessor


if __name__ == '__main__':
    main()