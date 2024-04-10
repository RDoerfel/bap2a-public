from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import Kernel, RBF, ConstantKernel, DotProduct

import sys

class GPR(GaussianProcessRegressor):
    """ interface to sklearn GaussianProcessRegression"""
    def __init__(self, kernel = None, alpha=1e-10, kernel_wargs = {}) -> None:
        """ Initialize the GPR model.
        Args:
            kernel: kernel to use for GPR. Can be string or instance default: None
            kernel_wargs (dict): keyword arguments for kernel"""
        if kernel in ['RBF', 'ConstantKernel', 'DotProduct']:
            kernel = self._get_kernel_from_string(kernel, kernel_wargs)
        elif isinstance(kernel, Kernel):
            kernel.set_params(**kernel_wargs)
        else:
            print("Falling back to default kernel")
            kernel = None
        
        self.kernel = kernel
        self.kernel_wargs = kernel_wargs
        super().__init__(kernel=kernel, alpha=alpha)
        
    def _get_kernel_from_string(self,kernel:str, kernel_wargs={}) -> None:
        """ Get kernel from string
        Args:
            kernel (str): kernel to use for GPR"""
        # get class from string
        class_ = getattr(sys.modules[__name__], kernel)
        # instantiate class
        return class_(**kernel_wargs)

class Pyment(RegressorMixin, BaseEstimator):
    """ Pyment model """
    def fit(self, X, y=None):
        """Fit the transformer.
        Args:
            X (pd.DataFrame): dataframe to subsample
            y (pd.Series): target variable (not used)"""
        self.n_features_in_ = X.shape[1]
        return self

    def predict(self, X):
        return X


