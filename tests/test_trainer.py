#%%
from src.trainer import Trainer
from src.workflow import WorkflowBuilder, WorkFlowSpecs, WorkflowResults
import numpy as np
import pandas as pd
from sklearn.model_selection import KFold
from sklearn import set_config
from src.test_config import pipe_config, model_config
import yaml
import tempfile
import pytest

set_config(transform_output="pandas")

#%%
PIPE_NAME = 'pipeline-test'
MODEL_NAME = 'dummy'
PIPE_FILE = 'pipe_file'
MODEL_FILE = 'model_file'
ROIS = ['rois']

@pytest.fixture
def _generate_data():
    """ Generate zeros for testing """
    # simulate data
    data = np.zeros((10, 3))
    df = pd.DataFrame(data, columns=['cat1', 'pyment', 'age'])
    return df

def test_trainer(_generate_data, pipe_config, model_config):
    with tempfile.TemporaryDirectory() as tmpdirname:
        pipe_file = tmpdirname + f'/{PIPE_FILE}.yml'
        model_file = tmpdirname + f'/{MODEL_FILE}.yml'
        
        with open(pipe_file, 'w') as f:
            yaml.dump(pipe_config, f)

        with open(model_file, 'w') as f:
            yaml.dump(model_config, f)

        specs = WorkFlowSpecs(pipe_file, model_file, PIPE_NAME, MODEL_NAME, ROIS)
        workflows = WorkflowBuilder.build([specs])

        cv_inner = KFold(n_splits=2, shuffle=True, random_state=42)
        cv_outer = KFold(n_splits=2, shuffle=True, random_state=42)
        trainer = Trainer()

        for workflow in workflows:
            workflow_results = trainer.train(data=_generate_data,
                                            strat_col="cat1",
                                            label_col="age",
                                            cv_inner=cv_inner,
                                            cv_outer=cv_outer,
                                            workflow=workflow)   

        assert isinstance(workflow_results, WorkflowResults)

# %%
