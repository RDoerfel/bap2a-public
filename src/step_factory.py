from sklearn.linear_model import BayesianRidge, ARDRegression
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import DotProduct, RBF
from sklearn.compose import ColumnTransformer, make_column_selector, make_column_transformer
from sklearn.svm import LinearSVR
from sklearn.ensemble import StackingRegressor
from xgboost import XGBRegressor
from sklearn.dummy import DummyRegressor
from src.transform import DiMap, SelectCols, get_column_transformer, NormEITV
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from src.estimator import Pyment
from sklearn.pipeline import Pipeline
import numpy as np

class Step():
    """
    A class representing a step in a data processing pipeline.

    Attributes:
    -----------
    name : str
        The name of the step.
    kwargs : dict
        A dictionary of keyword arguments to be passed to the step's object.
    object : object
        The object associated with the step.

    Methods:
    --------
    __call__():
        A method that returns the name of the step and its object when called.
    """
    def __init__(self, step_config): 
        """
        Initializes a Step instance.

        Parameters:
        -----------
        step_config : dict
            A dictionary containing the configuration of the step.
        """
        print(f"Step {step_config['name']} created")
        self.name = step_config['name']
        self._get_kwargs(step_config)
        self.object = None

    def _get_kwargs(self, step_config):
        if 'kwargs' in step_config:
            self.kwargs = step_config['kwargs']
        else:
            self.kwargs = {}
        
    def __call__(self):
        return (self.name, self.object)
    
class StepScaler(Step):
    def __init__(self, step_config): 
        super().__init__(step_config)
        self.object = StandardScaler(**self.kwargs)

class StepDiMap(Step):
    def __init__(self, step_config): 
        super().__init__(step_config)
        self.object = DiMap(**self.kwargs)

class StepNormEITV(Step):
    def __init__(self, step_config): 
        super().__init__(step_config)
        self.object = NormEITV(**self.kwargs)

class StepColSelector(Step):
    def __init__(self, step_config): 
        super().__init__(step_config)
        self.object = SelectCols(**self.kwargs)
    
class StepColumnScaler(Step):
    def __init__(self, step_config): 
        super().__init__(step_config)
        ct = make_column_transformer(
              (StandardScaler(),
                make_column_selector(dtype_include=np.number)),  # rating
              (OneHotEncoder(),
              make_column_selector(dtype_include=object)))
        ct.set_params(verbose_feature_names_out=False)
        ct.set_output(transform='pandas')
        self.object = ct

class StepColPattern(Step):
    def __init__(self, step_config): 
        super().__init__(step_config)
        self.object = get_column_transformer(**self.kwargs).set_output(transform='pandas')

class StepBayesianRidge(Step):
    def __init__(self, step_config): 
        super().__init__(step_config)
        self.object = BayesianRidge(**self.kwargs)

class StepARDRegression(Step):
    def __init__(self, step_config): 
        super().__init__(step_config)
        self.object = ARDRegression(**self.kwargs)

class StepLinGPR(Step):
    def __init__(self, step_config): 
        super().__init__(step_config)
        self.object = GaussianProcessRegressor(kernel=DotProduct(),**self.kwargs)

class StepRBFGPR(Step):
    def __init__(self, step_config): 
        super().__init__(step_config)
        self.object = GaussianProcessRegressor(kernel=RBF(),**self.kwargs)

class StepLinearSVR(Step):
    def __init__(self, step_config): 
        super().__init__(step_config)
        self.object = LinearSVR(**self.kwargs)

class StepXGBRegressor(Step):
    def __init__(self, step_config): 
        super().__init__(step_config)
        self.object = XGBRegressor(**self.kwargs)

class StepDummyRegressor(Step):
    def __init__(self, step_config): 
        super().__init__(step_config)
        self.object = DummyRegressor(**self.kwargs)

class StepPyment(Step):
    def __init__(self, step_config): 
        super().__init__(step_config)
        self.object = Pyment(**self.kwargs)

class StepEnsemble(Step):
    def __init__(self, step_config: dict, model: Step):
        super().__init__(step_config)
        ct_mri = get_column_transformer('mri')
        ct_pet = get_column_transformer('pet')
        model = model.object
        pipe_mri = Pipeline([('ct', ct_mri), ('model', model)])
        pipe_pet = Pipeline([('ct', ct_pet), ('model',model)])
        self.object = StackingRegressor([('mri', pipe_mri), ('pet', pipe_pet)], BayesianRidge())

class StepPyEnsemble(Step):
    def __init__(self, step_config: dict, model: Step):
        super().__init__(step_config)
        ct_mri = get_column_transformer('pyment')
        ct_pet = get_column_transformer('pet')
        model = model.object
        pipe_mri = Pipeline([('ct', ct_mri), ('model', Pyment())])
        pipe_pet = Pipeline([('ct', ct_pet), ('model', model)])
        self.object = StackingRegressor([('mri', pipe_mri), ('pet', pipe_pet)], BayesianRidge())

class StepFactory():
    """
    A factory class for creating Step instances.

    Methods:
    --------
    create_step(step_config):
        Creates a Step instance based on the step's configuration.
    """
    @staticmethod
    def create_step(step_config):
        # Preproc Steps
        if step_config['name'] == 'dimap':
            step = StepDiMap(step_config)
            return step()
        elif step_config['name'] == 'colselector':
            step = StepColSelector(step_config)
            return step()
        elif step_config['name'] == 'scaler':
            step = StepScaler(step_config)
            return step()
        elif step_config['name'] == 'columnscaler':
            step = StepColumnScaler(step_config)
            return step()
        elif step_config['name'] == 'normeitv':
            step = StepNormEITV(step_config)
            return step()
        elif step_config['name'] == 'colpattern':
            step = StepColPattern(step_config)
            return step()
        
        # Model Steps
        elif step_config['name'] == 'bayesianridge':
            step = StepBayesianRidge(step_config)
            return step()
        elif step_config['name'] == 'ardregression':
            step = StepARDRegression(step_config)
            return step()
        elif step_config['name'] == 'lingpr':
            step = StepLinGPR(step_config)
            return step()
        elif step_config['name'] == 'rbfgpr':
            step = StepRBFGPR(step_config)
            return step()
        elif step_config['name'] == 'linearsvr':
            step = StepLinearSVR(step_config)
            return step()
        elif step_config['name'] == 'xgbregressor':
            step = StepXGBRegressor(step_config)
            return step()
        elif step_config['name'] == 'dummyregressor':
            step = StepDummyRegressor(step_config)
            return step()
        elif step_config['name'] == 'pyment':
            step = StepPyment(step_config)
            return step()
        
        # Ensemble Steps
        elif step_config['name'] == 'ens_bridge':
            model = StepBayesianRidge(step_config)
            step = StepEnsemble(step_config, model)
            return step()
        elif step_config['name'] == 'ens_rvm':
            model = StepARDRegression(step_config)
            step = StepEnsemble(step_config, model)
            return step()        
        elif step_config['name'] == 'ens_lingpr':
            model = StepLinGPR(step_config)
            step = StepEnsemble(step_config, model)
            return step()        
        elif step_config['name'] == 'ens_rbfgpr':
            model = StepRBFGPR(step_config)
            step = StepEnsemble(step_config, model)
            return step()        
        elif step_config['name'] == 'ens_lsvr':
            model = StepLinearSVR(step_config)
            step = StepEnsemble(step_config, model)
            return step()
        elif step_config['name'] == 'ens_xgb':
            model = StepXGBRegressor(step_config)
            step = StepEnsemble(step_config, model)
            return step()
        
        # Ensemble Py Steps
        elif step_config['name'] == 'ens_py_bridge':
            model = StepBayesianRidge(step_config)
            step = StepPyEnsemble(step_config, model)
            return step()
        elif step_config['name'] == 'ens_py_rvm':
            model = StepARDRegression(step_config)
            step = StepPyEnsemble(step_config, model)
            return step()
        elif step_config['name'] == 'ens_py_lingpr':
            model = StepLinGPR(step_config)
            step = StepPyEnsemble(step_config, model)
            return step()
        elif step_config['name'] == 'ens_py_rbfgpr':
            model = StepRBFGPR(step_config)
            step = StepPyEnsemble(step_config, model)
            return step()
        elif step_config['name'] == 'ens_py_lsvr':
            model = StepLinearSVR(step_config)
            step = StepPyEnsemble(step_config, model)
            return step()
        elif step_config['name'] == 'ens_py_xgb':
            model = StepXGBRegressor(step_config)
            step = StepPyEnsemble(step_config, model)
            return step()

        else:
            raise ValueError("Step type '{}' not recognized".format(step_config['name']))
        
