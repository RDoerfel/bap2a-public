import numpy as np
from numpy.random import default_rng


def get_population(min, max, N, seed=None):
    """get population between min and max with N samples
    args:
        min: minimum value
        max: maximum value
        N: number of samples
        seed: seed for random number generator
    returns:
        population: array of samples"""
    rng = default_rng(seed=seed)
    return rng.integers(min, max, N)


def ageing(population, slope, intercept, noise_level=0.1, seed=None):
    """calculate deciline in bpp with age for population
    args:
        population: array of samples
        slope: slope of linear function
        intercept: intercept of linear function
        noise_level: sd of noise
        seed: seed for random number generator
    returns:
        bpp: array of bpp"""
    rng = default_rng(seed)
    return population * slope + intercept + rng.normal(0, noise_level, len(population))


def brainage(population, seed=None):
    """calculate brainage for population by adding noise
    args:
        population: array of samples
        seed: seed for random number generator
    returns:
        brainage: array of brainage"""
    rng = default_rng(seed)
    return population + rng.normal(0, 1, len(population)) * 5
