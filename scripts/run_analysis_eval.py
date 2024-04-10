#%%
from src.experiment import  ExperimentBuilder
from src.analyzier import StatsAnalyzer
from src.plotter import Plotter
from src import plotting
from pathlib import Path
from sklearn.linear_model import BayesianRidge
import argparse
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import statsmodels.api as sm
import pandas as pd

#%% set plotting styles
plotting.add_font()
plotting.set_r_params(small=8, medium=10, big=12)

inch_to_cm = 1/2.54

#%% set Paths and configs 
RESULTDIR = Path(__file__).parent.parent / "results"
DATADIR= Path(__file__).parent.parent / "data" 
# %%
data_dir = DATADIR
result_dir = RESULTDIR
exp_name = "experiment-I"
reference="pipeline-IIa_bridge"
experiment = ExperimentBuilder.build(data_dir, "experiment.yml", exp_name, result_dir)
results = experiment.load()

#%% print demographics
data = pd.read_excel(result_dir / f'prepared_data_{exp_name}.xlsx')

print(f"Subjects: {len(data['pet_id'].unique())}")
print(f"Age min/max: {data['chron_age'].min()} / {data['chron_age'].max()}")
print(f"Age mean/std: {data['chron_age'].mean()} / {data['chron_age'].std()}")

# %% Results Table 1
analyzer = StatsAnalyzer(results)
analyzer.analyze(reference=reference)
analyzer.save()

# %% Results Figure 2
plotter = Plotter(results)
plotter.set_imgsize((17,12))
fig, ax = plotter.plot(reference=reference)
fig.savefig(Path(result_dir, 'figures', f"fig2_{exp_name}_suppl_results.pdf"), dpi=300)
fig.savefig(Path(result_dir, 'figures', f"fig2_{exp_name}_suppl_results.png"), dpi=300)

plotter = Plotter(results)
plotter.set_imgsize((17,6))
fig, ax = plotter.plot(reference=reference,select_best=True)
fig.savefig(Path(result_dir, 'figures', f"fig2_{exp_name}_results.pdf"), dpi=300)
fig.savefig(Path(result_dir, 'figures', f"fig2_{exp_name}_results.png"), dpi=300)

# %% define function to get regression line and std for plotting
def get_regression_line(x, y):
    """Get regression line and std for plotting."""
    # fit model
    model = BayesianRidge()
    model.fit(x.reshape(-1,1),y.reshape(-1,1))

    # get regression line
    y_pred, y_std = model.predict(x.reshape(-1,1), return_std=True)
    return y_pred, y_std

def plot_scatter(ax, data, x, y, color_scatter):
    sns.scatterplot(data=data, x=x, y=y, ax=ax, alpha = 0.4, edgecolor='black', color=color_scatter, s=20)

def plot_regression_line(ax, data, x, y, color_line):
    x = data[x].values
    y = data[y].values
    y_pred, y_std = get_regression_line(x,y)
    ax.plot(x, y_pred, color=color_line, lw=1)

# %% Results Figure 3

# prepare data
from scipy import stats
data = results.predictions
# average over folds
data_average_mean = data.groupby(['subject_id']).mean().reset_index()
data_average_mean['tracer'] = data_average_mean['subject_id'].str[0]
data_average_std = data.groupby(['subject_id']).std().reset_index()

# inch to cm
fig, axs = plotting.get_figures(2,3, figsize=(18*inch_to_cm,9*inch_to_cm), sharex=True, sharey=False)

models = ['pipeline-IIa_bridge', 'pipeline-IIb_rbfgpr', 'pipeline-IIc_ens_rvm']
titles = ['5-HT2AR', 'GM', '5-HT2AR + GM']

palette_b = sns.color_palette('Dark2', 4)
palette_s = sns.color_palette('Set2', 4)

color_line_palette = palette_b[1:]
color_scatter_palette = palette_s[1:]

for i, model in enumerate(models):
    # get colors
    color_line = color_line_palette[i]
    color_scatter = color_scatter_palette[i]
    
    # plot brain-age vs age
    axs[0,i].set_title(titles[i])
    plot_scatter(axs[0,i], data_average_mean, 'true', model, color_scatter)

    # plot identity line
    axs[0,i].axline((0, 0), slope=1, color='black', linestyle='--', lw=.8)

    # plot regression line scipy stats
    plot_regression_line(axs[0,i], data_average_mean, 'true', model, color_line)

    # set ylabel
    if i == 0:
        axs[0,i].set_ylabel('Predicted Age\n[years]')
    else:
        axs[0,i].set_ylabel('')
    
    # set yticks 
    axs[0,i].set_yticks([20,50,80])
    axs[0,i].set_ylim([0,100])
    
    # plot plot pad vs age
    plot_scatter(axs[1,i], data_average_mean, 'true', f'pad_{model}', color_scatter)

    # plot hline at 0
    axs[1,i].axline((0, 0), slope=0, color='black', linestyle='--', lw=.8)

    # plot regression line scipy stats
    plot_regression_line(axs[1,i], data_average_mean, 'true', f'pad_{model}', color_line)

    # set labels
    if i == 0:
        axs[1,i].set_ylabel('PAD [years]')
        axs[1,i].set_xlabel('')
    elif i == 1:
        axs[1,i].set_xlabel('Age [years]')
        axs[1,i].set_ylabel('')
    else:
        axs[1,i].set_ylabel('')
        axs[1,i].set_xlabel('')

    # set yticks
    axs[1,i].set_yticks([-30,0,30])
    axs[1,i].set_ylim([-40,40])

    # set xticks
    axs[1,i].set_xticks([20,50,80])
    axs[1,i].set_xlim([0,100])

# add legend to axs[1,1]
fig.legend(['Subject', 'Identity/Zero line', 'Regression line'], bbox_to_anchor=(0.5, -0.02), loc='center', ncol=5, frameon=False)

fig = plotting.set_style_ax(fig, axs)
fig.savefig(Path(result_dir, 'figures', f"fig3_{exp_name}_predictions.pdf"), dpi=300)
fig.savefig(Path(result_dir, 'figures', f"fig3_{exp_name}_predictions.png"), dpi=300)