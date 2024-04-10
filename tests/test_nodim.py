from src import simulation
from src import nodim
import numpy as np

def test_estimate_params():
    """ test if parameters are estimated correctly """
    values = np.random.normal(0,1,1000)
    param = nodim.estimate_params(values)
    assert np.allclose(param['mu'],np.mean(values))
    assert np.allclose(param['std'],np.std(values))

def test_nodim():
    """ test if nodim is correct """
    min = 20
    max = 60
    N = 100
    population = simulation.get_population(min,max,N)
    slope1 = -0.01
    intercept1 = 2
    slope2 = -0.03
    intercept2 = 4
    measure1 = simulation.ageing(population,slope1,intercept1,noise_level=0)
    measure2 = simulation.ageing(population,slope2,intercept2,noise_level=0)
    param1 = nodim.estimate_params(measure1)
    param2 = nodim.estimate_params(measure2)
    transformed = nodim.transform_nodim(param1,param2,measure1)
    assert np.allclose(transformed,measure2)
