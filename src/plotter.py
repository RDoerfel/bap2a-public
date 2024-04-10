from pathlib import Path
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

from src import plotting
from src.analyzier import StatsAnalyzer
from src.experiment import ExperimentResults

class Plotter(StatsAnalyzer):
    def __init__(self, results:ExperimentResults):
        super().__init__(results)
        self._cm = 1/2.54
        self._imgsize = (15*self._cm, 10*self._cm)

    def set_imgsize(self, imgsize:tuple=(15,10)):
        self._imgsize = (imgsize[0]*self._cm, imgsize[1]*self._cm)
        
    def plot(self, reference:str, select_best:bool=False):
        self.analyze(reference)
        return self._prepare_scores(reference, suffix='', select_best=select_best)

    def set_image_params(self, imgsize:tuple=(15,10), rc:dict={'small':8, 'medium':10, 'large':12}):
        plotting.set_r_params(**rc)
        self._imgsize = (imgsize[0]*self._cm, imgsize[1]*self._cm)
        
    def _prepare_scores(self, reference:str, suffix:str, select_best:bool):
        mae_names = [f'{pipe}_mae' for pipe in self.workflow_names]
        scores_mae = self.scores[mae_names]
        scores_mae = scores_mae.reset_index()
        scores_mae = scores_mae.melt(id_vars='index', value_vars=mae_names, var_name='pipeline', value_name='mae')

        # remove suffix from pipeline name
        scores_mae['pipeline'] = scores_mae['pipeline'].str.replace(f'{suffix}', '')

        # substract mean of pyment to better see improvement
        scores_mae['pipeline'] = scores_mae['pipeline'].str.replace('_mae', '')
        scores_mae['pipe'] = scores_mae['pipeline'].str.split('_').str[0]
        scores_mae['model'] = scores_mae['pipeline'].str.split('_').str[-1]

        # replace pipe names: pipeline-I -> ref, pipeline-IIa -> PET, pipeline-IIb -> MRI, pipeline-IIc -> Pet+MRI
        scores_mae['pipe'] = scores_mae['pipe'].str.replace('pipeline-IIa', '5-HT2AR')
        scores_mae['pipe'] = scores_mae['pipe'].str.replace('pipeline-IIb', 'GM')
        scores_mae['pipe'] = scores_mae['pipe'].str.replace('pipeline-IIc', '5-HT2AR+GM')
        scores_mae['pipe'] = scores_mae['pipe'].str.replace('pipeline-I', 'ref')

        # compose new pipeline name
        scores_mae['workflow'] = scores_mae['pipe'] + ' ' + scores_mae['model'] 
        
        # only select best model for each pipeline (PET, MRI, PET+MRI). Still show both models for reference
        if select_best:
            # compute the mean mae for each pipeline
            best_scores_mae = scores_mae.groupby(['pipe', 'workflow']).mean().reset_index()

            # get the workflow name with the lowest mae for each pipeline
            best_scores_mae = best_scores_mae.loc[best_scores_mae.groupby('pipe')['mae'].idxmin()]
  
            # select only the best model for each pipeline
            select = best_scores_mae[best_scores_mae['pipe'].isin(['5-HT2AR', 'GM', '5-HT2AR+GM'])]['workflow'].to_list()
            select.append('ref dummy')
            select.append('ref pyment')

            # select only the best model for each pipeline
            scores_mae = scores_mae[scores_mae['workflow'].isin(select)]

        # reference is the min mae of PET
        mae_ref = scores_mae.loc[scores_mae['pipe'] == '5-HT2AR'].groupby('model')['mae'].mean().min()
        
        return self._plot(scores_mae, mae_ref)
        
    def _plot(self,scores_mae:pd.DataFrame, scores_ref:pd.DataFrame):
        fig, ax = plotting.get_figures(1,1, figsize=self._imgsize,sharex=False, sharey=False) 

        # color palette
        unique_pipes = scores_mae['pipe'].unique()
        n_colors = len(unique_pipes)

        palette_b = sns.color_palette('Set2', n_colors)
        palette_s = sns.color_palette('Dark2', n_colors)
        
        colors_b = []
        colors_s = []

        for i in range(0,n_colors):
            n_models_per_pipe = len(scores_mae[scores_mae['pipe'] == unique_pipes[i]]['model'].unique())
            colors_b.append(n_models_per_pipe * [palette_b[i]])
            colors_s.append(n_models_per_pipe * [palette_s[i]])

        # flatten list
        colors_b = [item for sublist in colors_b for item in sublist]
        colors_s = [item for sublist in colors_s for item in sublist]

        sns.stripplot(data=scores_mae, x='mae', y='workflow', ax=ax, jitter=0.2, size=4, alpha=0.4 ,dodge=True, palette=colors_s)
        sns.boxplot(data=scores_mae, x='mae', y='workflow', showfliers=False, dodge=True, ax=ax, width=0.5, color='C7', linewidth=1.5, palette=colors_b)

        ax.set_ylabel('')
        ax.set_xlabel('Mean absolute error [years]')
        ylim = ax.get_ylim()

        ax.vlines(scores_ref,ymin=ylim[0], ymax=ylim[1], linestyles='dashed', colors='C7')
        fig = plotting.set_style_ax(fig,np.array([ax]))
        return fig, ax
   

    


