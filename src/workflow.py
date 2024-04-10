from src.model_builder import ModelBuilder, ModelRepresentation
from src.pipeline import PipelineBuilder, PipelineRepresentation

from sklearn.pipeline import Pipeline
import pandas as pd
from pathlib import Path


class WorkFlowSpecs():
    def __init__(self, pipe_file, model_file, pipe_name, model_name, rois):
        self.pipe_file = pipe_file
        self.model_file = model_file
        self.pipe_name = pipe_name
        self.model_name = model_name
        self.rois = rois

    def __str__(self) -> str:
        return f'\t\n Pipeline: {self.pipe_name}, Model: {self.model_name}'

class WorkflowResults():
    def __init__(self, workflow_name:str, scores: pd.DataFrame, results: pd.DataFrame, best_params: pd.DataFrame, weights: pd.DataFrame):
        self.name = workflow_name
        self.pipe_name = workflow_name.split('_')[0]
        self.model_name = workflow_name.split('_')[1]
        self.scores = scores
        self.results = results
        self.best_params = best_params
        self.weights = weights

    def save(self, path: Path, experiment: str):
        path.mkdir(parents=True, exist_ok=True)
        self.scores.to_csv(path / f'{experiment}_{self.name}_scores.csv')
        self.results.to_csv(path / f'{experiment}_{self.name}_results.csv')
        self.best_params.to_csv(path / f'{experiment}_{self.name}_best_params.csv')
        self.weights.to_csv(path / f'{experiment}_{self.name}_weights.csv')

    @staticmethod
    def load(path: Path, experiment_name: str, workflow_name: str):
        scores = pd.read_csv(path / f'{experiment_name}_{workflow_name}_scores.csv', index_col=0)
        results = pd.read_csv(path / f'{experiment_name}_{workflow_name}_results.csv', index_col=0)
        best_params = pd.read_csv(path / f'{experiment_name}_{workflow_name}_best_params.csv', index_col=0)
        weights = pd.read_csv(path / f'{experiment_name}_{workflow_name}_weights.csv', index_col=0)
        return WorkflowResults(workflow_name, scores, results, best_params, weights)
        

class WorkflowRepresentation():
    def __init__(self, spec: WorkFlowSpecs):
        # modify DiMap Step
        pipe_spec = PipelineBuilder.build(spec.pipe_file, spec.pipe_name)
        model_spec = ModelBuilder.build(spec.model_file, spec.model_name)
    
        steps = pipe_spec.steps
        model = model_spec.model
        
        # add model to steps
        steps.append(('model', model))

        pipeline = Pipeline(steps = steps)

        self.name = f'{pipe_spec.name}_{model_spec.name}'    
        self.pipeline = pipeline
        self.rois = spec.rois
        self.paramgrid = model_spec.paramgrid


class WorkflowBuilder():
    """
    A class for building a workflow.

    Attributes:
    -----------
    name : str
        The name of the workflow.
    description : str
        A description of the workflow.
    model : src.model_builder.ModelRepresentation
        The model representation.
    pipeline : src.pipeline_builder.PipelineRepresentation
        The pipeline representation.
    """

    @staticmethod
    def build(workflow_specs: list[WorkFlowSpecs]) -> list[WorkflowRepresentation]:
        """
        Builds a workflow from a list of WorkFlowSpecs objects.

        Parameters:
        -----------
        specs : WorkFlowSpecs
            The workflow specifications.
        """
        workflows = []
        for spec in workflow_specs:
            workflow = WorkflowRepresentation(spec)
            workflows.append(workflow)

        return workflows

