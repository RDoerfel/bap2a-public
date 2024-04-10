#%%
from pathlib import Path
from src.fs_roi_lut import read_rois
from src.paths import Paths
import pandas as pd
import nibabel as nib
import numpy as np
import shutil

#%% set paths
data_dir = Path(__file__).parent.parent.parent / 'data' 
paths = Paths(data_dir / "paths.json")
worklist_file = data_dir / 'derivatives' / "combined_worklist.xlsx"
database_dir  = Path(paths("DATA_DIR")) / "Cimbi_database"
cimbi_dir = Path(paths("DATA_DIR")) / "Cimbi36"
alt_dir = Path(paths("DATA_DIR")) / "Altanserin"

#%% copy aparc and aseg stats to data_dir
def copy_asegstats2table(fs_subjects_dir, data_dir, name):
    file_name = f"aseg-stats_{name}.txt"
    file_path = fs_subjects_dir / file_name
    shutil.copy(file_path, data_dir / file_name)
    return
    
def copy_aparcstats2table(fs_subjects_dir, data_dir, name):
    for hemi in ['lh', 'rh']:
        file_name = f"aparc-stats_{hemi}_{name}.txt"
        file_path = fs_subjects_dir / file_name
        shutil.copy(file_path, data_dir / file_name)
    return

copy_asegstats2table(cimbi_dir / "FS_SUBJECTS", data_dir / 'mri', "cimbi")
copy_asegstats2table(alt_dir / "FS_SUBJECTS", data_dir / 'mri', "alt")
copy_aparcstats2table(cimbi_dir / "FS_SUBJECTS", data_dir / 'mri', "cimbi")
copy_aparcstats2table(alt_dir / "FS_SUBJECTS", data_dir / 'mri', "alt")
# %%
