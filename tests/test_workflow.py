from src.workflow import WorkflowRepresentation, WorkFlowSpecs, WorkflowResults, WorkflowBuilder
from src.test_config import pipe_config, model_config

from sklearn.pipeline import Pipeline
from sklearn.dummy import DummyRegressor
import pandas as pd

from pathlib import Path
import tempfile
import yaml
import pytest

PIPE_NAME = 'pipeline-test'
MODEL_NAME = 'dummy'
PIPE_FILE = 'pipe_file'
MODEL_FILE = 'model_file'
ROIS = ['rois']

@pytest.fixture
def example_workflow_results():
    workflow_name = 'pipeline-test_model-test'
    scores = pd.DataFrame({'score': [0.8, 0.9, 0.85]})
    results = pd.DataFrame({'result': ['A', 'B', 'C']})
    best_params = pd.DataFrame({'param': ['x', 'y', 'z']})
    weights = pd.DataFrame({'weight': [0.5, 0.3, 0.2]})
    return WorkflowResults(workflow_name, scores, results, best_params, weights)


def test_workflowspecs():
    specs = WorkFlowSpecs(PIPE_FILE, MODEL_FILE, PIPE_NAME, MODEL_NAME, ROIS)
    assert specs.pipe_file == PIPE_FILE
    assert specs.model_file == MODEL_FILE
    assert specs.pipe_name == PIPE_NAME
    assert specs.model_name == MODEL_NAME
    assert specs.rois == ROIS


def test_workflowrepresentation_instance(pipe_config, model_config):
    with tempfile.TemporaryDirectory() as tmpdirname:
        pipe_file = tmpdirname + f'/{PIPE_FILE}.yml'
        model_file = tmpdirname + f'/{MODEL_FILE}.yml'
        
        with open(pipe_file, 'w') as f:
            yaml.dump(pipe_config, f)

        with open(model_file, 'w') as f:
            yaml.dump(model_config, f)

        specs = WorkFlowSpecs(pipe_file, model_file, PIPE_NAME, MODEL_NAME, ROIS)
        workflow = WorkflowRepresentation(specs)

        assert workflow.name == f'{PIPE_NAME}_{MODEL_NAME}'
        assert isinstance(workflow.pipeline, Pipeline)
        assert isinstance(workflow.rois, list)
        assert isinstance(workflow.paramgrid, dict)
        assert isinstance(workflow.name, str)

def test_workflowrepresentation_content(pipe_config, model_config):
    with tempfile.TemporaryDirectory() as tmpdirname:
        pipe_file = tmpdirname + f'/{PIPE_FILE}.yml'
        model_file = tmpdirname + f'/{MODEL_FILE}.yml'
        
        with open(pipe_file, 'w') as f:
            yaml.dump(pipe_config, f)

        with open(model_file, 'w') as f:
            yaml.dump(model_config, f)

        specs = WorkFlowSpecs(pipe_file, model_file, PIPE_NAME, MODEL_NAME, ROIS)
        workflow = WorkflowRepresentation(specs)

        assert workflow.name == f'{PIPE_NAME}_{MODEL_NAME}'
        assert workflow.paramgrid == model_config['dummy']['paramgrid']
        assert workflow.rois == ROIS
        assert isinstance(workflow.pipeline['model'], DummyRegressor)

def test_workflowbuilder(pipe_config, model_config):
    with tempfile.TemporaryDirectory() as tmpdirname:
        pipe_file = tmpdirname + f'/{PIPE_FILE}.yml'
        model_file = tmpdirname + f'/{MODEL_FILE}.yml'
        
        with open(pipe_file, 'w') as f:
            yaml.dump(pipe_config, f)

        with open(model_file, 'w') as f:
            yaml.dump(model_config, f)

        specs = WorkFlowSpecs(pipe_file, model_file, PIPE_NAME, MODEL_NAME, ROIS)
        workflows = WorkflowBuilder.build([specs])

        assert isinstance(workflows, list)
        assert isinstance(workflows[0], WorkflowRepresentation)
        assert workflows[0].name == f'{PIPE_NAME}_{MODEL_NAME}'
        assert workflows[0].paramgrid == model_config['dummy']['paramgrid']
        assert workflows[0].rois == ROIS
        assert isinstance(workflows[0].pipeline['model'], DummyRegressor)

def test_workflowresult_save(example_workflow_results):
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        experiment = 'experiment1'
        example_workflow_results.save(temp_path, experiment)

        scores_path = temp_path / f'{experiment}_pipeline-test_model-test_scores.csv'
        results_path = temp_path / f'{experiment}_pipeline-test_model-test_results.csv'
        best_params_path = temp_path / f'{experiment}_pipeline-test_model-test_best_params.csv'
        weights_path = temp_path / f'{experiment}_pipeline-test_model-test_weights.csv'

        assert scores_path.exists()
        assert results_path.exists()
        assert best_params_path.exists()
        assert weights_path.exists()

        saved_scores = pd.read_csv(scores_path, index_col=0)
        saved_results = pd.read_csv(results_path, index_col=0)
        saved_best_params = pd.read_csv(best_params_path, index_col=0)
        saved_weights = pd.read_csv(weights_path, index_col=0)

        assert saved_scores.equals(example_workflow_results.scores)
        assert saved_results.equals(example_workflow_results.results)
        assert saved_best_params.equals(example_workflow_results.best_params)
        assert saved_weights.equals(example_workflow_results.weights)


def test_workflowresult_load(example_workflow_results):
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        experiment_name = 'experiment1'
        workflow_name = 'pipeline-test_model-test'
        example_workflow_results.save(temp_path, experiment_name)

        loaded_workflow_results = WorkflowResults.load(temp_path, experiment_name, workflow_name)

        assert loaded_workflow_results.name == example_workflow_results.name
        assert loaded_workflow_results.scores.equals(example_workflow_results.scores)
        assert loaded_workflow_results.results.equals(example_workflow_results.results)
        assert loaded_workflow_results.best_params.equals(example_workflow_results.best_params)
        assert loaded_workflow_results.weights.equals(example_workflow_results.weights)

def test_workflowresults_attributes(example_workflow_results):
    assert example_workflow_results.name == 'pipeline-test_model-test'
    assert isinstance(example_workflow_results.scores, pd.DataFrame)
    assert isinstance(example_workflow_results.results, pd.DataFrame)
    assert isinstance(example_workflow_results.best_params, pd.DataFrame)
    assert isinstance(example_workflow_results.weights, pd.DataFrame)