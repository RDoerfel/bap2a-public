#%%
from src.config_handler import read_yaml, get_entry
from src.step_factory import StepFactory          


class PipelineRepresentation():
    """
    A class representing a pipeline with a name, description, and steps.

    Attributes:
    -----------
    name : str
        The name of the pipeline.
    description : str
        A description of the pipeline.
    pipeline : sklearn.pipeline.Pipeline
        The pipeline object.

    Methods:
    --------
    modify_step(step_names, step_kwargs):
        Modifies the parameters of a step in the pipeline.

    """
    def __init__(self, name, description, steps):
        """
        Initializes a new instance of the PipelineRepresentation class.

        Parameters:
        -----------
        name : str
            The name of the pipeline.
        description : str
            A description of the pipeline.
        steps : list of tuples
            A list of tuples, where each tuple contains a step name and a step object.
        """
        self.name = name
        self.description = description
        self.steps = steps
    
class PipelineBuilder:
    """
    A class that builds a PipelineRepresentation based on a configuration file.
    """
    @staticmethod
    def build(config_file: str, name: str) -> PipelineRepresentation:
        """
        Builds the scikit-learn pipeline based on a configuration file.

        Parameters:
        -----------
        config_file : str
            The path of the configuration file.
        name : str
            The name of the pipeline to be built.

        Returns:
        --------
        pipeline : PipelineRepresentation object
            The built pipeline object.
        """
        config = read_yaml(config_file)
        pipeline_config = get_entry(config, name)
        description = get_entry(pipeline_config, 'descr')
        step_configs = get_entry(pipeline_config, 'steps')

        steps = []
        for step_config in step_configs:
            step = StepFactory.create_step(step_config)
            steps.append(step)

        return PipelineRepresentation(name, description, steps)
    

    
# %%
