"""Test cases for machine learning code review with the Code Review Assistant.

This file contains examples of common ML code patterns with intentional issues 
that should be addressed in a comprehensive review, including model selection,
hyperparameter tuning, validation strategies, and production readiness.
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, mean_squared_error


# Example 1: Poor feature engineering and preprocessing
def prepare_data(data_path):
    """Prepare data for modeling."""
    # Load data
    df = pd.read_csv(data_path)
    
    # Drop missing values - not ideal!
    df = df.dropna()
    
    # One-hot encoding without handling high cardinality
    df = pd.get_dummies(df)
    
    # No scaling or normalization
    
    # Simple split with no stratification
    X = df.drop('target', axis=1)
    y = df['target']
    
    return train_test_split(X, y, test_size=0.2)


# Example 2: Basic model training with no hyperparameter tuning
def train_model(X_train, y_train):
    """Train a model without proper tuning or validation."""
    # No model selection process
    model = RandomForestClassifier(n_estimators=100)
    
    # Simple fit with no cross-validation
    model.fit(X_train, y_train)
    
    return model


# Example 3: Poor model evaluation
def evaluate_model(model, X_test, y_test):
    """Basic model evaluation."""
    y_pred = model.predict(X_test)
    
    # Only using accuracy - not suitable for imbalanced datasets
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Accuracy: {accuracy:.4f}")
    
    return accuracy


# Example 4: No pipeline for reproducibility
def end_to_end_ml(data_path):
    """Run the entire ML process."""
    X_train, X_test, y_train, y_test = prepare_data(data_path)
    model = train_model(X_train, y_train)
    score = evaluate_model(model, X_test, y_test)
    
    # No model persistence
    # No preprocessing persistence
    
    return model, score


# Example 5: Time series forecasting with data leakage
def time_series_forecast(time_data):
    """Forecast time series with data leakage issues."""
    # Create features without considering temporal nature
    df = pd.DataFrame(time_data, columns=['value'])
    
    # Adding time-based features
    df['lag1'] = df['value'].shift(1)
    df['lag2'] = df['value'].shift(2)
    
    # Dropping NAs after creating features - loses data
    df = df.dropna()
    
    # Simple split without respecting time order - data leakage!
    X = df[['lag1', 'lag2']]
    y = df['value']
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    
    # Using linear regression for time series - often not optimal
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    print(f"MSE: {mse:.4f}")
    
    return model, mse


# Example 6: Neural network with poor architecture choices
def create_neural_network():
    """Create a neural network with suboptimal design choices."""
    try:
        import tensorflow as tf
        from tensorflow.keras.models import Sequential
        from tensorflow.keras.layers import Dense
        
        # No proper input shape handling
        model = Sequential([
            # Too many neurons in first layer
            Dense(1024, activation='relu', input_shape=(10,)),
            
            # No dropout or batch normalization
            Dense(512, activation='relu'),
            
            # Poor architecture with large jumps in layer sizes
            Dense(64, activation='relu'),
            
            # Output layer with wrong activation for regression
            Dense(1, activation='relu')
        ])
        
        # Using accuracy for a regression problem
        model.compile(optimizer='adam', loss='mse', metrics=['accuracy'])
        
        return model
    
    except ImportError:
        print("TensorFlow not available")
        return None


if __name__ == "__main__":
    # Generate synthetic data for testing
    np.random.seed(42)
    
    # Save synthetic data for the prepare_data function
    X = np.random.rand(1000, 5)
    y = (X[:, 0] > 0.5).astype(int)
    df = pd.DataFrame(X, columns=[f'feature_{i}' for i in range(5)])
    df['target'] = y
    df.to_csv('synthetic_data.csv', index=False)
    
    # Synthetic time series data
    time_steps = 100
    time_data = np.sin(np.linspace(0, 10, time_steps)) + np.random.normal(0, 0.1, time_steps)
    
    # Run the examples
    # model, score = end_to_end_ml('synthetic_data.csv')
    # ts_model, ts_mse = time_series_forecast(time_data)
    # nn_model = create_neural_network()
