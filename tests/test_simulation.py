from src import simulation
import numpy as np
from numpy.random import default_rng

def test_population_minmax():
    """ test if population is between min and max """
    min = 20
    max = 60
    N = 100
    population = simulation.get_population(min,max,N)
    assert np.all(population >= min)
    assert np.all(population <= max)

def test_population_N():
    """ test if population has N samples """
    min = 20
    max = 60
    N = 100
    population = simulation.get_population(min,max,N)
    assert len(population) == N

def test_population():
    """ test if population is correct """
    min = 20
    max = 60
    N = 100
    seed = 123
    population = simulation.get_population(min,max,N,seed)
    rng = default_rng(seed)
    assert np.all(population == rng.integers(min,max,N))

def test_ageing_no_noise():
    """ test if slope is correct """
    population = np.arange(20,60)
    slope = -0.01
    intercept = 2
    bpp = simulation.ageing(population,slope,intercept,noise_level=0)
    assert np.all(bpp == population * slope + intercept)

def test_ageing_noise():
    """ test if slope is correct """
    population = np.arange(20,60)
    slope = -0.01
    intercept = 2
    seed = 123
    rng = default_rng(seed)
    bpp = simulation.ageing(population,slope,intercept,seed=seed)
    assert np.all(bpp == population * slope + intercept + rng.normal(0,0.1,len(population)))

def test_brainage():
    """ test if brainage is correct """
    population = np.arange(20,60)
    seed = 123
    brainage = simulation.brainage(population,seed=seed)
    rng = default_rng(seed)
    assert np.all(brainage == population + rng.normal(0,1,len(population)) * 5)
