import pytest
from src.pipeline import PipelineBuilder, PipelineRepresentation
from src.transform import SelectCols
from src.test_config import pipe_config
from sklearn.preprocessing import StandardScaler
import tempfile
import yaml

def test_pipeline_representation():
    name = 'pipeline1'
    description = 'Example Pipeline'
    steps = [('Step1', None), ('Step2', None)]

    pipe_rep = PipelineRepresentation(name, description, steps)

    assert pipe_rep.name == name
    assert pipe_rep.description == description
    assert pipe_rep.steps == steps

def test_pipeline_builder(pipe_config):
    # Create a temporary YAML file
    with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False) as temp_file:
        temp_file.write(yaml.dump(pipe_config).encode('utf-8'))
        temp_file.flush()

        config_file = temp_file.name
        name = 'pipeline-test'

        pipeline = PipelineBuilder.build(config_file, name)

        assert pipeline.name == name
        assert pipeline.description == 'Test Pipeline'
        assert pipeline.steps[0][0] == 'scaler' 
        assert pipeline.steps[1][0] == 'colselector'
        assert isinstance(pipeline.steps[0][1], StandardScaler)
        assert isinstance(pipeline.steps[1][1], SelectCols)
