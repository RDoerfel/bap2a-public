from src.weights import get_feature_weights
from src.step_factory import StepFactory
from src.test_config import get_step_config
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn import set_config
import numpy as np
import pytest


def _fit_test_pipeline(model) -> Pipeline:
    set_config(transform_output='pandas')

    # generate a dataframe with random data, 100 rows, 10 columns. half of the column names start with 'mri' and the other half are 'pet'
    column_names = ['mri_' + str(i) if i < 5 else 'pet_' + str(i) for i in range(10)]
    data = np.random.rand(100, 10)
    X = pd.DataFrame(data, columns=column_names)
    y = np.random.rand(100)

    # create a pipeline with a scaler and the model
    pipe = Pipeline([
        ('scaler', StandardScaler()),
        ('model', model)
    ])

    # fit the pipeline
    pipe.fit(X, y)

    return pipe

def test_get_weights_linear():
    """Test get_feature_weights for linear model.
    """
    config = get_step_config('ardregression')
    _, model = StepFactory.create_step(config)
    pipe = _fit_test_pipeline(model)
    weights = get_feature_weights(pipe['model'])
    assert isinstance(weights, pd.DataFrame)
    assert weights.shape == (1,10)

def test_get_weights_tree():
    """Test get_feature_weights for tree-based model.
    """
    config = get_step_config('xgbregressor')
    _, model = StepFactory.create_step(config)
    pipe = _fit_test_pipeline(model)
    weights = get_feature_weights(pipe['model'])
    assert isinstance(weights, pd.DataFrame)
    assert weights.shape == (1,10)

def test_get_weights_dummy():
    """Test get_feature_weights for dummy model.
    """
    config = get_step_config('dummyregressor')
    _, model = StepFactory.create_step(config)
    pipe = _fit_test_pipeline(model)
    weights = get_feature_weights(pipe['model'])
    assert isinstance(weights, pd.DataFrame)
    assert weights.shape == (1,1)

def test_get_weights_stacking():
    """Test get_feature_weights for stacking model.
    """
    config = get_step_config('ens_bridge')
    _, model = StepFactory.create_step(config)
    pipe = _fit_test_pipeline(model)
    weights = get_feature_weights(pipe['model'])
    assert isinstance(weights, pd.DataFrame)
    assert weights.shape == (1,12)

def test_get_weights_gpr():
    """Test get_feature_weights for Gaussian Process Regressor.
    """
    # generate a dataframe with random data, 100 rows, 10 columns. half of the column names start with 'mri' and the other half are 'pet'
    column_names = ['mri_' + str(i) if i < 5 else 'pet_' + str(i) for i in range(10)]

    config = get_step_config('lingpr')
    _, model = StepFactory.create_step(config)
    pipe = _fit_test_pipeline(model)
    weights = get_feature_weights(pipe['model'])
    assert isinstance(weights, pd.DataFrame)
    assert weights.shape == (1,1)

if __name__ == '__main__':
    pytest.main(['-s', __file__])