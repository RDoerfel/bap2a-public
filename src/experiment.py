#%%
from pathlib import Path
import pandas as pd
from src.config_handler import read_yaml, get_entry
from src.data_wrangler import DataWrangler, DataSpec
from src.cv import CVGenerator, CVSpec
from src.fs_roi_lut import read_roi_names
from src.trainer import Trainer
from src.workflow import WorkFlowSpecs, WorkflowBuilder, WorkflowResults

class ExperimentSpec():
    def __init__(self, data_dir: Path, exp_file_name: str, name: str, result_dir: Path) -> None:
        self.name = name
        self.resultdir = result_dir
        self.datadir = data_dir

        config = read_yaml(self.datadir / exp_file_name)
        exp_config = get_entry(config, name)
        self.description = get_entry(exp_config,'description')
        
        files = get_entry(exp_config,'files')
        self._setup_files(files)

        data_config = get_entry(exp_config,'data')
        self._setup_dataspec(data_config)

        cv_config = get_entry(exp_config,'cv')
        self._setup_cvspec(cv_config)

        self._read_rois()
        self._exclude_rois()

        pipelines = get_entry(exp_config,'pipelines')
        self._setup_workflows(pipelines)
        
        self._print_config()

    def _setup_files(self,files):
        self.data_file = self.datadir / files['data_file']
        self.roi_file = self.datadir / files['roi_file']
        self.pipeline_file = self.datadir / files['pipeline_file']
        self.model_file = self.datadir / files['model_file']
        self.logdir = self.resultdir / "logs"

    def _setup_cvspec(self,cv_config):
        self.cv = CVSpec(cv_config['splits'], 
                         cv_config['repeats'])

    def _setup_dataspec(self,data_config):
        self.dataspec = DataSpec(self.data_file, 
                                 data_config['covarities'], 
                                 data_config['exclude'],
                                 data_config['tracer'],
                                 data_config['type'])

    def _print_config(self):
        print(f"Experiment: {self.name}")
        print(f"Description: {self.description}")
        print(f"Files: \n\tData: {self.data_file}\n\tROI: {self.roi_file}\n\tPipeline: {self.pipeline_file}\n\tModel: {self.model_file}")
        print(f"Data: {self.dataspec}")
        print(f"CV: {self.cv}")
        print(f"Workflows:")
        for workflow in self.workflows:
            print(workflow)

    def _read_rois(self):
        self.rois = read_roi_names(self.roi_file)
        return 

    def _exclude_rois(self):
        for roi in self.dataspec.exclude:
            # check if roi is in rois
            if roi in self.rois:
                self.rois.remove(roi)
        return
               
    def _setup_workflows(self,pipelines):
        self.workflows = []
        for pipeline in pipelines:
            for model in pipeline['models']:
                workflow = WorkFlowSpecs(self.pipeline_file, self.model_file, pipeline['name'], model, self.rois)
                self.workflows.append(workflow)
        return
    

class ExperimentRunner():
    def __init__(self, exp_spec: ExperimentSpec) -> None:
        self.name = exp_spec.name
        self.resultdir = exp_spec.resultdir
        self.datadir = exp_spec.datadir

        self.data_wrangler = DataWrangler(exp_spec.dataspec)
        self.cv = CVGenerator(exp_spec.cv)
        self.workflows = WorkflowBuilder.build(exp_spec.workflows)

    def run(self, n_jobs: int = 1):
        self.data_wrangler.prepare_data()
        self.data_wrangler.save_data(self.resultdir, self.name)

        data = self.data_wrangler.get_data()

        cv_inner = self.cv.generate_inner()
        cv_outer = self.cv.generate_outer()
        trainer = Trainer()
        self.results = []
        for workflow in self.workflows:
            workflow_results = trainer.train(data=data,
                                             strat_col="chron_age_group",
                                             label_col="chron_age",
                                             cv_inner=cv_inner,
                                             cv_outer=cv_outer,
                                             workflow=workflow,
                                             n_jobs=n_jobs)   
            workflow_results.save(self.resultdir,self.name)
            self.results.append(workflow_results)
        return ExperimentResults(self.name, data, self.results, self.resultdir)
    
    def load(self):
        self.results = []
        for workflow in self.workflows:
            workflow_results = WorkflowResults.load(self.resultdir, self.name, workflow.name)
            self.results.append(workflow_results)
        data = pd.read_excel(self.resultdir / f"prepared_data_{self.name}.xlsx")
        return ExperimentResults(self.name, data, self.results, self.resultdir)
        

class ExperimentResults():
    def __init__(self, name: str, data: pd.DataFrame, results: list[WorkflowResults], result_dir: Path) -> None:
        self.name = name
        self.data = data
        self.results = results
        self.result_dir = result_dir
        self._get_workflow_names()
        self._compress_predictions(results)

    def _get_workflow_names(self):
        self.workflow_names = [workflow.name for workflow in self.results]
        self.pipe_names = [workflow.pipe_name for workflow in self.results]
        self.model_names = [workflow.model_name for workflow in self.results]
        
    def _compress_predictions(self,results: list[WorkflowResults]):
        pipeline_predictions = [result.results for result in results]
        
        for i, pipeline in enumerate(pipeline_predictions):
            # rename columns [pred] to [pred_pipeline]
            pipeline_predictions[i] = pipeline.rename(columns={'pred': f'{self.workflow_names[i]}', 'index':'subject_id', 'true':'true'})
            # drop column [std]
            pipeline_predictions[i] = pipeline_predictions[i].drop(columns=['std'])

        merged = pipeline_predictions[0] # start with the first dataframe in the list
        for i in range(1, len(pipeline_predictions)):
            merged = pd.merge(merged, pipeline_predictions[i], on=['true', 'subject_id', 'fold'])
        
        self.predictions = merged

    def get_workflow_results(self, result_type: str, worflow_name: str = None):
        if result_type == 'predictions':
            return self._find_workflow_by_name(worflow_name).results
        elif result_type == 'scores':
            return self._find_workflow_by_name(worflow_name).scores
        elif result_type == 'best_params':
            return self._find_workflow_by_name(worflow_name).best_params
        elif result_type == 'weights':
            return self._find_workflow_by_name(worflow_name).weights

    def _find_workflow_by_name(self, name):
        for workflow in self.results:
            if workflow.name == name:
                return workflow
        return None

    

class ExperimentBuilder():
    @staticmethod
    def build(config_file, name, data_dir, result_dir) -> ExperimentRunner:
        exp_spec = ExperimentSpec(config_file, name, data_dir, result_dir)
        return ExperimentRunner(exp_spec)
         

    