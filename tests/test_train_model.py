import pytest
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from src.train_model import log_system_info


@pytest.fixture
def sample_dataset():
    """Create a sample dataset for testing"""
    np.random.seed(42)
    n_samples = 100

    # Create features
    X = pd.DataFrame(
        {
            'feature1': np.random.normal(0, 1, n_samples),
            'feature2': np.random.normal(0, 1, n_samples),
            'feature3': np.random.normal(0, 1, n_samples),
        }
    )

    # Create target (binary classification)
    y = (X['feature1'] + X['feature2'] > 0).astype(int)

    return X, y


def test_train_test_split_consistency(sample_dataset):
    """Test that train-test split maintains data consistency"""
    X, y = sample_dataset
    test_size = 0.2
    random_state = 42

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )

    # Check sizes
    assert len(X_train) == int(len(X) * (1 - test_size))
    assert len(X_test) == int(len(X) * test_size)
    assert len(y_train) == len(X_train)
    assert len(y_test) == len(X_test)

    # Check class distribution preservation
    train_class_dist = np.bincount(y_train) / len(y_train)
    test_class_dist = np.bincount(y_test) / len(y_test)
    np.testing.assert_almost_equal(train_class_dist, test_class_dist, decimal=1)


def test_data_preprocessing_pipeline(sample_dataset):
    """Test the preprocessing pipeline (imputation and scaling)"""
    X, _ = sample_dataset

    # Add some missing values
    X.iloc[0:10, 0] = np.nan

    # Preprocessing pipeline
    imputer = SimpleImputer(strategy='median')
    scaler = StandardScaler()

    # Apply preprocessing
    X_imputed = imputer.fit_transform(X)
    X_scaled = scaler.fit_transform(X_imputed)

    # Check no missing values
    assert not np.isnan(X_imputed).any()

    # Check scaling properties
    assert np.abs(X_scaled.mean(axis=0)).max() < 1e-10  # mean close to 0
    assert np.abs(X_scaled.std(axis=0) - 1).max() < 1e-10  # std close to 1


def test_model_initialization():
    """Test model initialization with correct parameters"""
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    lr = LogisticRegression(max_iter=1000, random_state=42)

    # Check parameters were set correctly
    assert rf.n_estimators == 100
    assert rf.random_state == 42
    assert lr.max_iter == 1000
    assert lr.random_state == 42


def test_model_training_and_prediction(sample_dataset):
    """Test that models can be trained and make predictions"""
    X, y = sample_dataset
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    models = {
        'RandomForest': RandomForestClassifier(n_estimators=100, random_state=42),
        'LogisticRegression': LogisticRegression(max_iter=1000, random_state=42),
    }

    for name, model in models.items():
        # Train model
        model.fit(X_train, y_train)

        # Make predictions
        y_pred = model.predict(X_test)

        # Basic checks
        assert len(y_pred) == len(y_test)
        assert set(y_pred) <= set([0, 1])  # Binary classification
        assert model.score(X_test, y_test) > 0.5  # Better than random


def test_log_system_info():
    """Test that system info logger function runs without errors"""
    try:
        log_system_info()
    except Exception as e:
        pytest.fail(f'log_system_info() raised an exception: {e}')


def test_feature_importance(sample_dataset):
    """Test feature importance extraction"""
    X, y = sample_dataset

    # Train RandomForest
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(X, y)

    # Get feature importance
    importances = rf.feature_importances_

    # Check properties
    assert len(importances) == X.shape[1]
    assert np.all(importances >= 0)  # Non-negative importance
    assert np.isclose(sum(importances), 1)  # Sum to 1
