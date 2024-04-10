from sklearn.linear_model import BayesianRidge, ARDRegression
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.svm import LinearSVR
from xgboost import XGBRegressor
from sklearn.dummy import DummyRegressor

from src.config_handler import read_yaml, get_entry
from src.step_factory import StepFactory

class ModelRepresentation():
    """
    Class for storing information about a machine learning model.

    Methods:
    --------
    None

    Attributes:
    -----------
    name : str
        The name of the model.
    model : sklearn.base.BaseEstimator
        An instance of the model.
    paramgrid : dict
        A dictionary of hyperparameters to be tuned during GridSearchCV.
    """
    def __init__(self, name, model, paramgrid):
        self.name = name
        self.model = model
        self.paramgrid = paramgrid

    def __call__(self) -> tuple:
        return ('model', self.model)
    
class ModelBuilder(): 
    """
    Class for building machine learning models.
    """
    @staticmethod
    def build(config_file, name) -> ModelRepresentation:
        """
        Builds and returns a ModelRepresentation object.

        Parameters:
        -----------
        config_file : str
            The path to the model configuration file.
        name : str
            The name of the model to be created.

        Returns:
        --------
        model : ModelRepresentation
            A ModelRepresentation object.
        """
        config = read_yaml(config_file)
        model_config = get_entry(config, name)
        (_, model) = StepFactory.create_step(model_config)
        paramgrid = get_entry(model_config, 'paramgrid')
        return ModelRepresentation(name, model, paramgrid)
