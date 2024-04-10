import numpy as np
import pandas as pd
from sklearn.inspection import permutation_importance

SUPPORTED_LIN_REG = ['LinearRegression','ARDRegression','BayesianRidge','LinearSVR']
SUPPORTED_TREE_REG = ['XGBRegressor']
SUPPORTED_DUMMY_REG = ['DummyRegressor', 'Pyment']
SUPPORTED_STACKING_REG = ['StackingRegressor']
SUPPORTED_GPR_REG = ['GaussianProcessRegressor']

def get_feature_weights(model, X=None, y=None):
    """Get feature weights for model.
    Args:
        model (sklearn estimator): pipeline to get weights for
        X (pd.DataFrame): data to get weights for (only when feature importance needs to be computed)
        y (pd.Series): target to get weights for (only when feature importance needs to be computed)
    Returns:
        weights (pd.DataFrame): weights
    """
    names = _get_info(model, 'names')
    weights = _get_info(model, 'weights')
    return pd.DataFrame(weights, index=names).T

def _get_info(model, info_type: str, X=None, y=None):
    """Get info for model.
    Args:
        model (sklearn model): model to get info for
        info_type (str): type of info to get (weight, names)
        X (pd.DataFrame): data to get weights for (only when feature importance needs to be computed)
        y (pd.Series): target to get weights for (only when feature importance needs to be computed)
    Returns:
        info (list): info
    """
    model_name = type(model).__name__

    #get model type
    if model_name in SUPPORTED_LIN_REG:
        return _get_linear_info(model, info_type)
    elif model_name in SUPPORTED_TREE_REG:
        return _get_tree_info(model, info_type)
    elif model_name in SUPPORTED_DUMMY_REG:
        return _get_dummy_info(model, info_type)
    elif model_name in SUPPORTED_STACKING_REG:
        return _get_stacking_info(model, info_type)
    elif model_name in SUPPORTED_GPR_REG:
        return _get_gpr_info(model, info_type)
    else:
        raise ValueError(f"Model type {model_name} not supported.")

def _get_linear_info(model, info_type: str):
    if info_type == 'weights':
        return _get_linear_weights(model)
    elif info_type == 'names':
        return _get_linear_names(model)
    
def _get_tree_info(model, info_type: str):
    if info_type == 'weights':
        return _get_tree_weights(model)
    elif info_type == 'names':
        return _get_tree_names(model)
    
def _get_dummy_info(model, info_type: str):
    if info_type == 'weights':
        return _get_dummy_weights(model)
    elif info_type == 'names':
        return _get_dummy_names(model)
    
def _get_stacking_info(model, info_type: str):
    if info_type == 'weights':
        return _get_stacking_weights(model)
    elif info_type == 'names':
        return _get_stacking_names(model)

def _get_gpr_info(model, info_type: str):
    if info_type == 'weights':
        return _get_gpr_weights(model)
    elif info_type == 'names':
        return _get_gpr_names(model)

def _get_linear_weights(model):
    return model.coef_

def _get_linear_names(model):
    return model.feature_names_in_
    
def _get_tree_weights(model):
    return model.feature_importances_

def _get_tree_names(model):
    return model.get_booster().feature_names

def _get_dummy_weights(model):
    return np.array([1])

def _get_dummy_names(model):
    return ['dummy']

def _get_stacking_weights(model):
    weights = []
    for estimator in model.estimators_:
        weights.append(_get_info(estimator['model'], 'weights'))
    # append final estimator
    weights.append(_get_info(model.final_estimator_, 'weights'))
    # flatten list
    weights = [item for sublist in weights for item in sublist]
    return np.array(weights)

def _get_stacking_names(model):
    names = []
    for estimator in model.estimators_:
        names.append(_get_info(estimator['model'], 'names'))
    names.append(list(model.named_estimators_.keys()))
    # append keys to np.array names
    names = [item for sublist in names for item in sublist]
    return names

def _get_gpr_weights(model):
    # get feature importance
    return [0]

def _get_gpr_names(model):
    return ['gpr']