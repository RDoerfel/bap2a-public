from src.step_factory import Step, StepScaler, StepFactory
from src.test_config import step_config, supported_steps, get_step_config
from sklearn.preprocessing import StandardScaler

def test_step(step_config):
    step = Step(step_config)
    assert step.name == 'scaler'
    assert step.kwargs == step_config['kwargs']
    assert step.object == None

def test_step_call(step_config):
    step = Step(step_config)
    assert step() == ('scaler', None)

def test_step_scaler(step_config):
    step = StepScaler(step_config)
    assert step.object.with_mean == False
    assert step.name == 'scaler'
    assert step.kwargs == step_config['kwargs']
    assert isinstance(step.object, StandardScaler)

def test_step_scaler_call(step_config):
    step = StepScaler(step_config)
    assert step() == ('scaler', step.object)
    assert isinstance(step.object, StandardScaler)

def test_step_factory(step_config):
    name, object = StepFactory.create_step(step_config)
    assert name == 'scaler'
    assert isinstance(object, StandardScaler)

def test_supported_steps(supported_steps):
    for step in supported_steps:
        config = get_step_config(step)
        assert StepFactory.create_step(config) != None



