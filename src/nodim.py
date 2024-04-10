import numpy as np
from scipy.stats import norm
from scipy import interpolate
from statsmodels.distributions.empirical_distribution import ECDF

def estimate_params(values):
    """
    Estimate parameters of a gaussian distribution from values.
    args:
        values: values to estimate parameters from
    returns:
        dict of (mu,std) of the distribution
    """
    mu, std = norm.fit(values)
    return {"mu": mu, "std": std}

def estimate_ecdf(values):
    """
    Estimate empirical distribution function from values.
    args:
        values: values to estimate ecdf from
    returns:
        dict of (x,y) of the empirical distribution
    """
    ecdf = ECDF(values)
    return {"x": ecdf.x, "y": ecdf.y}

def transorm_ecdf_nodim(param1, param2, values):
    """
    Apply Nonlinear Distritbution Mapping (NODIM) to transform values from one distribution to another.
    The distributions are defined by the empirical distribution functions ecdf1 and ecdf2.
    args:
        param1: fitted ECDF object of the first distribution (from)
        param2: fitted ECDF object of the second distribution (to)
        values: values to be transformed (from)
    returns:
        transformed values
    """
    # create an x-vector for for both distributions for mu +-4 std
    x1 = param1["x"]
    x2 = param2["x"]
    
    # create cdf for both distributions
    cdf1 = param1["y"]
    cdf2 = param2["y"]

    # % resample points for both cdfs at same points aka mapping probability to outcome
    ip1 = interpolate.PchipInterpolator(cdf1, x1)
    ip2 = interpolate.PchipInterpolator(cdf2, x2)

    x = np.linspace(0, 1, 1000)

    v1_resampled = ip1(x)
    v2_resampled = ip2(x)

    # create interpolation function for mapping v1 to v2
    nodim = interpolate.interp1d(v1_resampled, v2_resampled)

    # apply nodim to values
    return nodim(values)

def transform_nodim(param1, param2, values):
    """
    Apply Nonlinear Distritbution Mapping (NODIM) to transform values from one distribution to another.
    The gaussian distributions are defined by the parameters param1 and param2.
    args:
        param1: dict of (mu,std) of the first distribution (from)
        param2: dict of (mu,std) of the second distribution (to)
        values: values to be transformed (from)
    returns:
        transformed values
    """
    # create an x-vector for for both distributions for mu +-4 std
    x1 = np.linspace(
        param1["mu"] - 5 * param1["std"], param1["mu"] + 5 * param1["std"], 1000
    )
    x2 = np.linspace(
        param2["mu"] - 5 * param2["std"], param2["mu"] + 5 * param2["std"], 1000
    )

    # create cdf for both distributions
    cdf1 = norm.cdf(x1, param1["mu"], param1["std"])
    cdf2 = norm.cdf(x2, param2["mu"], param2["std"])

    # % resample points for both cdfs at same points aka mapping probability to outcome
    ip1 = interpolate.PchipInterpolator(cdf1, x1)
    ip2 = interpolate.PchipInterpolator(cdf2, x2)

    x = np.linspace(0, 1, 1000)

    v1_resampled = ip1(x)
    v2_resampled = ip2(x)

    # create interpolation function for mapping v1 to v2
    nodim = interpolate.interp1d(v1_resampled, v2_resampled)

    # apply nodim to values
    return nodim(values)
