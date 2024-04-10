import pytest
from src.config_handler import read_yaml, get_entry
from pathlib import Path

@pytest.fixture
def pipe_config():
    return {
        'pipeline-test': {
            'descr': 'Test Pipeline',
            'steps': [
                {
                    'name': 'scaler'
                },
                {
                    'name': 'colselector'
                }
            ]
        }
    }

@pytest.fixture
def model_config():
    return {
        'dummy': {
            'name': 'dummyregressor',
            'kwargs': {
                'strategy': 'mean'
            },
            'paramgrid': {
            }
        }
    }

@pytest.fixture
def step_config():
    return {
    'name': 'scaler',
    'kwargs': {
        'with_mean': False
        }
    }

@pytest.fixture
def supported_steps():
    return [
        'scaler',
        'colselector',
        'columnscaler',
        'normeitv',
        'colpattern',
        'bayesianridge',
        'ardregression',
        'lingpr',
        'rbfgpr',
        'linearsvr',
        'xgbregressor',
        'dummyregressor',
        'pyment',
        'ens_bridge',
        'ens_rvm',
        'ens_lingpr',
        'ens_rbfgpr'
    ]
  
def get_step_config(name: str):
    # read yaml file
    config = read_yaml(Path(__file__).parent / 'supported_steps.yml')
    # get entry
    step_config = get_entry(config, name)
    return step_config
    