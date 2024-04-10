#%%
from pathlib import Path
from src.fs_roi_lut import read_rois, Roi
from src.fs_stats import StatsFile
from src.paths import Paths
import pandas as pd
import numpy as np
import os

#%% set paths
data_dir = Path(__file__).parent.parent.parent / 'data' 

# %% read rois
rois = read_rois(data_dir / "rois_fs.json")
rois.pop('brain-stem')
rois.pop('cerebellum')

# %% make a function
def combine_mri_stats(data_dir: Path, tracer: str, rois: dict) -> pd.DataFrame:
    roi_set = set()
    for roi in rois:
        roi_set.add(Roi(roi, rois[roi]))

    # create new df
    df = pd.DataFrame(columns=list(rois.keys()) + ['eITV'])

    # create stats objects
    aseg_stats = StatsFile(data_dir / f"aseg-stats_{tracer}.txt", 'subcortical')
    aparc_lh_stats = StatsFile(data_dir / f"aparc-stats_lh_{tracer}.txt", 'cortical')
    aparc_rh_stats = StatsFile(data_dir / f"aparc-stats_rh_{tracer}.txt", 'cortical')

    # combine rois
    for roi in roi_set:
        if roi.type == 'subcortical':
            vol = 1/2 * (aseg_stats.combine_rois(roi.get_labels('lh')) + aseg_stats.combine_rois(roi.get_labels('rh')))
        elif roi.type == 'cortical':
            vol = 1/2 * (aparc_lh_stats.combine_rois(roi.get_labels('lh')) + aparc_rh_stats.combine_rois(roi.get_labels('rh')))
        df[roi.name] = vol
    df['eITV'] = aseg_stats.stats['EstimatedTotalIntraCranialVol']
    df.to_csv(data_dir / f'{tracer}_mri_stats_fslobes.csv')
    return df

# %%
df_cimbi = combine_mri_stats(data_dir / 'mri', 'cimbi', rois)
df_alt = combine_mri_stats(data_dir / 'mri', 'alt', rois)

# %%
