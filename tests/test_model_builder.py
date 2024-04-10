import pytest
import tempfile
import yaml
from sklearn.dummy import DummyRegressor

from src.model_builder import ModelBuilder, ModelRepresentation
from src.test_config import model_config

def test_model_representation():
    name = 'dummy'
    model = DummyRegressor(strategy='mean')
    paramgrid = {'C': [0.1, 1.0, 10.0]}
    model_rep = ModelRepresentation(name, model, paramgrid)

    assert model_rep.name == name
    assert model_rep.model == model
    assert model_rep.paramgrid == paramgrid

def test_model_representation_call():
    name = 'dummy'
    model = DummyRegressor(strategy='mean')
    paramgrid = {'C': [0.1, 1.0, 10.0]}
    model_rep = ModelRepresentation(name, model, paramgrid)

    assert model_rep() == ('model', model)

def test_build_model(model_config):
    """Test that ModelBuilder can build a model from a configuration file."""
    model_name = "dummy"

    with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as temp_file:
        temp_file.write(yaml.dump(model_config).encode("utf-8"))
        temp_file.flush()
        
        model_rep = ModelBuilder.build(temp_file.name, model_name)

        assert isinstance(model_rep, ModelRepresentation)
        assert model_rep.name == model_name
        assert isinstance(model_rep.model, DummyRegressor)
        assert model_rep.paramgrid == {}

