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
import nibabel as nib
import numpy as np
from src import fs_roi_lut
from src.experiment import ExperimentBuilder
from src import plotting

import matplotlib.pyplot as plt
import nilearn.plotting as niplot
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.axes_grid1 import make_axes_locatable

from nibabel.freesurfer.mghformat import MGHImage
import pandas as pd

#%% set plotting parameters
plotting.set_r_params(small=8, medium=10, big=12)
inch_to_cm = 1/2.54

#%%
#%% set Paths and configs 
RESULTDIR = Path(__file__).parent.parent / "results"
DATADIR= Path(__file__).parent.parent / "data" 
LOCATION = Path(__file__).parent

# %%
data_dir = DATADIR
result_dir = RESULTDIR
subject_dir = LOCATION.parent.parent

exp_name = "experiment-I"
reference="pipeline-IIa_bridge"
experiment = ExperimentBuilder.build(data_dir, "experiment.yml", exp_name, result_dir)
results = experiment.load()

#%% prepare data
from scipy import stats
data = results.predictions
# average over folds
data_average_mean = data.groupby(['subject_id']).mean().reset_index()
data_average_mean['tracer'] = data_average_mean['subject_id'].str[0]
data_average_std = data.groupby(['subject_id']).std().reset_index()

# %% Results Figure 4a
i_color = 7
color_line = sns.color_palette('Dark2', 8)[i_color]
color_scatter = sns.color_palette('Set2', 8)[i_color]

fig, ax = plotting.get_figures(1,1, figsize=(6*inch_to_cm,6*inch_to_cm))

# color scatter by std
sns.scatterplot(data=data_average_mean, x='pad_pipeline-IIa_bridge', y='pad_pipeline-IIb_bridge', ax=ax, color=color_scatter)

# plot identity line
x = np.linspace(-40, 40, 100)
ax.plot(x, x, color='black', linestyle='--', lw=.8)

# plot regression line and print correlation. use bayesian regression
from sklearn.linear_model import BayesianRidge
x_pad = data_average_mean['pad_pipeline-IIa_bridge'].values.reshape(-1,1)
y_pad = data_average_mean['pad_pipeline-IIb_bridge'].values.reshape(-1,1)
model = BayesianRidge()
model.fit(x_pad,y_pad)
y, y_std = model.predict(x.reshape(-1,1), return_std=True)
ci = 1.96 * y_std/np.sqrt(len(x_pad))

# total (orthogonal) least squares
from scipy import odr
def lin_func(B, x):
    '''Linear function y = m*x + b
    https://docs.scipy.org/doc/scipy/reference/odr.html'''
    # B is a vector of the parameters.
    # x is an array of the current x values.
    # x is in the same format as the x passed to Data or RealData.
    #
    # Return an array in the same format as y passed to Data or RealData.
    return B[0]*x + B[1]

linear = odr.Model(lin_func)
mydata = odr.RealData(x_pad.flatten(), y_pad.flatten())
myodr = odr.ODR(mydata, linear, beta0=[1., 2.])
myoutput = myodr.run()
myoutput.pprint()

model_params = myoutput.beta
y = lin_func(model_params, x)
#ax.fill_between(x, y - ci, y + ci, color=color_line, lw=1, alpha=0.3, interpolate=True, where=None)
ax.plot(x, y, color=color_line, lw=.8)

# compute correlation and r2
corr, p = stats.pearsonr(x_pad.flatten(), y_pad.flatten())
r2 = model.score(x_pad, y_pad)
slope = model.coef_[0]

# save corr and r2 to txt file
with open(RESULTDIR / 'corr_r2.txt', 'w') as f:
    f.write(f"Correlation: {corr:.5f}, p-value: {p:.5f}\n")
    f.write(f"R2: {r2:.5f}\n")
    f.write(f"Slope: {slope:.5f}\n")
    f.write(f"TLS fit: {model_params[0]}, {model_params[1]}")

print(f"Correlation: {corr:.5f}, p-value: {p:.5f}")
print(f"Slope: {slope:.5f}")
print(f"R2: {r2:.5f}")

# set labels
ax.set_xlabel('PAD (5-HT2AR) [years]')
ax.set_ylabel('PAD (GM) [years]')
ax.set_xticks([-30, 0, 30])
ax.set_yticks([-30, 0, 30])
ax.set_xlim([-40, 40])
ax.set_ylim([-40, 40])

#ax.set_title('PAD (PET) vs. PAD (MRI): r={corr:.2f}, p={p:.2f}, r2={r2:.2f}'.format(corr=corr, p=p, r2=r2))

fig.legend(['Subject', 'Identity line', 'TLS Fit'], 
           frameon=False, 
           bbox_to_anchor=(0.5, -0.05), 
           loc='center', 
           ncol=2)

fig = plotting.set_style_ax(fig,np.array([ax]))
fig.savefig(RESULTDIR / 'figures' / f'fig4a_{exp_name}.png', dpi=300, bbox_inches='tight')
fig.savefig(RESULTDIR / 'figures' / f'fig4a_{exp_name}.pdf', dpi=300, bbox_inches='tight')

# %% Prepare weights
# get weights for pipeline-IIc_ens_bridge
weights_IIc_ens_bridge = results.get_workflow_results('weights','pipeline-IIc_ens_bridge')

# get all weights starting with pet_ and mri_
weights_pet = weights_IIc_ens_bridge.filter(regex='pet')
weights_mri = weights_IIc_ens_bridge.filter(regex='mri')

# rename column pet or mri to weight
weights_pet.rename(columns={'pet':'weight'}, inplace=True)
weights_mri.rename(columns={'mri':'weight'}, inplace=True)

# add column with modality
weights_pet['modality'] = 'pet'
weights_mri['modality'] = 'mri'

# remove pet_ and mri_ from column names
weights_pet.columns = weights_pet.columns.str.replace('pet_','')
weights_mri.columns = weights_mri.columns.str.replace('mri_','')

# concat dataframes
weights = pd.concat([weights_pet, weights_mri])
# make it long format
weights = weights.melt(id_vars=['weight','modality'], var_name='ROI', value_name='value')

# Figure 4b
# plot weights (boxplot) with hue modality
# normalize weights to -1 and 1 for pet and mri separately
# weights['value'] = weights.groupby('modality')['value'].apply(lambda x: (x - x.min()) / (x.max() - x.min()) * 2 - 1)

fig, ax = plotting.get_figures(1,1, figsize=(6*inch_to_cm,6*inch_to_cm))
sns.boxplot(data=weights, x='modality', y='weight', ax=ax, palette='Set2')
ax.set_ylabel('Weight')
ax.set_xlabel('Modality')
ax.set_xticklabels(['5-HT2AR', 'GM'])
ax.set_yticks([0, 0.25 ,0.5, 0.75, 1])

fig = plotting.set_style_ax(fig, np.array([ax]))
fig.savefig(RESULTDIR / 'figures' / f'fig4b_{exp_name}.png', dpi=300, bbox_inches='tight')
fig.savefig(RESULTDIR / 'figures' / f'fig4b_{exp_name}.pdf', dpi=300, bbox_inches='tight')

#%% Figure 4c

fsaverage_dir = Path(subject_dir,'fsaverage')
fsaverage_mri = Path(fsaverage_dir,'mri','brain.mgz')
fsaverage_aparc = Path(fsaverage_dir,'mri','aparc+aseg.mgz')

mni_dir = Path(subject_dir,'cvs_avg35_inMNI152')
mni_mri = Path(mni_dir,'mri','brain.mgz')
mni_aparc = Path(mni_dir,'mri','aparc+aseg.mgz')

#%% load rois
rois = fs_roi_lut.read_rois(Path(data_dir,'rois_fs.json'))
rois.pop('cerebellum')
rois.pop('brain-stem')

#%% load weights
# get weights for pipeline-IIc_ens_bridge
exp_name = "experiment-I"
experiment = ExperimentBuilder.build(data_dir, "experiment.yml", exp_name, result_dir)
results = experiment.load()

weights_IIc_ens_bridge = results.get_workflow_results('weights','pipeline-IIc_ens_bridge')

# compute mean and std
weights_IIc_ens_bridge_mean = weights_IIc_ens_bridge.mean(axis=0)
weights_IIc_ens_bridge_std = weights_IIc_ens_bridge.std(axis=0)

# get all weights starting with pet_ and mri_
weights_pet = weights_IIc_ens_bridge_mean.filter(regex='pet_')
weights_mri = weights_IIc_ens_bridge_mean.filter(regex='mri_')

# normalize weights to [-1,1]
#weights_pet = weights_pet / weights_pet.abs().max()
#weights_mri = weights_mri / weights_mri.abs().max()

# remove pet_ and mri_ from column names
weights_pet.index = weights_pet.index.str.replace('pet_','')
weights_mri.index = weights_mri.index.str.replace('mri_','')

#%% load image data
def load_image(subject_dir, subject_id, image='brain.mgz'):
    mri = nib.load(subject_dir / subject_id / 'mri' / image)
    return mri

def load_geometry(subject_dir, subject_id, hemi='lh', surf_type='pial'):
    geometry = nib.freesurfer.read_geometry(subject_dir / subject_id / 'surf' / f'{hemi}.{surf_type}')
    return geometry

def load_annotation(subject_dir, subject_id, hemi='lh', annot='aparc'):
    annotation = nib.freesurfer.read_annot(subject_dir / subject_id / 'label' / f'{hemi}.{annot}.annot')

    return annotation

def add_values_to_rois(aparc_data, brain):
    rois = brain.rois
    mask = np.zeros_like(aparc_data)
    for i,roi in enumerate(rois):
        indices = brain.rois[roi].get_index('both')
        if brain.rois[roi].value:
            mask[np.isin(aparc_data, indices)] = brain.rois[roi].value
        else:
            mask[np.isin(aparc_data, indices)] = i+1
    data_masked = np.ma.masked_where(mask==0, mask)
    return data_masked

def get_masked_image(parcellation, brain):
    mask = add_values_to_rois(parcellation.get_fdata(), brain)
    masked_image = MGHImage(mask, header=aparc.header, affine=aparc.affine)
    return masked_image

def plot_brains(masked_image, background, fig, axs):
    niplot.plot_stat_map(masked_image, bg_img=background, figure=fig, axes=axs, cmap='PuOr', black_bg=True, annotate=False, draw_cross=False, display_mode='ortho', cut_coords=[10,1,10], vmax=10, colorbar=False)

#%% load data
mri = load_image(subject_dir, 'fsaverage', 'brain.mgz')
aparc = load_image(subject_dir, 'fsaverage', 'aparc+aseg.mgz')

# load mni image
mri = load_image(subject_dir, 'cvs_avg35_inMNI152', 'brain.mgz')
aparc = load_image(subject_dir, 'cvs_avg35_inMNI152', 'aparc+aseg.mgz')

#%% visualize using nilearn
fig, axs = plotting.get_figures(2,1,figsize=(15*inch_to_cm,10*inch_to_cm), sharex=False, sharey=False)

mri_brain = brain = fs_roi_lut.BrainBuilder.build(Path(data_dir,'rois_fs.json'), drop=['cerebellum', 'brain-stem'])
mri_brain.set_values(weights_mri)

mri_mask_img = get_masked_image(aparc, mri_brain)
plot_brains(mri_mask_img, mri, fig, axs[0])

pet_brain = fs_roi_lut.BrainBuilder.build(Path(data_dir,'rois_fs.json'), drop=['cerebellum', 'brain-stem'])
pet_brain.set_values(weights_pet)

pet_mask_img = get_masked_image(aparc, pet_brain)
plot_brains(pet_mask_img, mri, fig, axs[1])

plt.subplots_adjust(wspace=0, hspace=0)

plotting.save_figure(fig, Path(result_dir, 'figures', "fig4_brain_weights.pdf"))
plotting.save_figure(fig, Path(result_dir, 'figures', "fig4_brain_weights.png"))


# %% plot a colorbar for the weights vmax=10, vmin?=-10 cmap='PuOr'
fig, ax = plt.subplots(figsize=(.4*inch_to_cm,3*inch_to_cm))

cmap = plt.cm.PuOr
norm = plt.Normalize(vmin=-10, vmax=10)
cb = plt.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), cax=ax, orientation='vertical')
cb.set_label('Weight', fontsize=10)
cb.ax.tick_params(labelsize=8)
# ticks at -10, 0, 10
cb.set_ticks([-10,0,10])
cb.ax.set_yticklabels(['-10','0','10'])
plotting.save_figure(fig, Path(result_dir, 'figures', "fig4_colorbar.pdf"))
plotting.save_figure(fig, Path(result_dir, 'figures', "fig4_colorbar.png"))


#%% Figure Supplement 2.1
# plot weights (boxplot) with hue modality
fig, ax = plotting.get_figures(1,1, figsize=(18*inch_to_cm,7*inch_to_cm))
flierprops = dict(markersize=3, linestyle='none')
sns.boxplot(data=weights, x='ROI', y='value', hue='modality', ax=ax, palette='Set2', width=0.6, linewidth=.4, flierprops=flierprops)

# rotate xticks
# set ylabel
ax.set_ylabel('Standardized Weight')
#ax.set_yticks([-1, -0.5, 0, 0.5, 1])

fig = plotting.set_style_ax(fig, np.array([ax]))
ax.set_xticklabels(ax.get_xticklabels(), rotation=45, horizontalalignment='right')
fig.savefig(RESULTDIR / 'figures' / f'fig4_{exp_name}_weights_suppl.png', dpi=300, bbox_inches='tight')
fig.savefig(RESULTDIR / 'figures' / f'fig4_{exp_name}_weights_suppl.pdf', dpi=300, bbox_inches='tight')

# %%
