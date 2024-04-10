from typing import Any
from src import config_handler 
import pandas as pd
from pathlib import Path
from src.paths import Paths

LOCATION = Path(__file__).parent
VALIDATION_FILE = Path(LOCATION,'resources','FreeSurferColorLut.txt')

def read_rois(roi_file,validate=True):
    """ Read the roi file and return a dictionary with the roi names and the
    corresponding indices.
    args:
        roi_file (str): path to the roi file
        validate (bool): if True, validate the roi file (default: True)
    returns:
        rois (dict): dictionary with the roi names and the corresponding indices"""
    rois = config_handler.read_json(roi_file)
    if validate:
        validate_rois(rois)
    return rois

def read_roi_names(roi_file):
    """ Read the roi file and return a list with the roi names.
    args:
        roi_file (str): path to the roi file
    returns:
        roi_names (list): list with the roi names"""
    rois = read_rois(roi_file)
    roi_names = list(rois.keys())
    return roi_names

def save_to_roi_lut(rois,save_dir, name):
    """ Save as a look up table for the rois to be used in NRUs (Jonas') pipeline
    args:
        rois (dict): dictionary with the roi names and the corresponding indices
        save_dir (str): path to the directory where the roi look up table should be saved
        name (str): name of the roi selection
        save (bool): if True, save to excel sheet (default: True)"""
    fs_index = []
    pve_index = []
    pve_name = []

    roi_keys = list(rois.keys())

    for i,region in enumerate(roi_keys):
        hemis = list(rois[region].keys())
        for hemi in rois[region]['hemi']:
            n_labels = len(rois[region]['hemi'][hemi]['index'])
            fs_index = fs_index + rois[region]['hemi'][hemi]['index']
            pve_index = pve_index + n_labels*[i+1]
            pve_name = pve_name + n_labels*[region]

    df = pd.DataFrame({'FS_index':fs_index,'PVE_index':pve_index,'PVE_name':pve_name})
    file_name = f'ROI_LUT_FS_2_PVE_{name}.xlsx'
    file = Path(save_dir,file_name)
    df.to_excel(file,index=False)

def print_regions(rois):
    """ Print the regions in the roi file
    args:
        rois (dict): dictionary with the roi names and the corresponding indices"""
    roi_keys = list(rois.keys())
    print(f"Using {len(roi_keys)} regions:")
    for i,region in enumerate(roi_keys):
        print(f"{region} ({rois[region]['location']})")

def validate_rois(rois):
    """ Validate the roi file
    args:
        rois (dict): dictionary with the roi names and the corresponding indices"""
    
    dfFSRoiLut = pd.read_csv(VALIDATION_FILE,delim_whitespace=True, lineterminator='\n')
    dfFSRoiLut.set_index("#No.",inplace=True)

    for region in rois:
        for hemi in rois[region]['hemi']:
            indices = rois[region]['hemi'][hemi]['index']
            labels = rois[region]['hemi'][hemi]['label']
            assert len(indices) == len(labels), f"Number of indices and labels do not match. Indices: {len(indices)}, Labels: {len(labels)}."

            for i in range(len(indices)):
                label_expected = labels[i]
                index = indices[i]
                label_actual = dfFSRoiLut.loc[index]['Label']
                assert label_expected == label_actual, f"Labels do not match. Expected: {label_expected}, Actual: {label_actual}."

class Roi():
    """A representation of a Freesurfer ROI""" 
    def __init__(self, roi_name: str, roi_config: dict):
        self.name = roi_name
        self.type = roi_config['location']
        self.lh_labels = roi_config['hemi']['lh']['label']
        self.rh_labels = roi_config['hemi']['rh']['label']
        self.lh_index = roi_config['hemi']['lh']['index']
        self.rh_index = roi_config['hemi']['rh']['index']
        self.name_exceptios = {
            'Left-Thalamus-Proper': 'Left-Thalamus',
            'Right-Thalamus-Proper': 'Right-Thalamus'
        } 
        self.value = None

    def __repr__(self) -> str:
        return self.name

    def get_labels(self, hemi: str) -> list:
        if hemi == 'lh':
            labels = self.lh_labels
        elif hemi == 'rh':
            labels = self.rh_labels
        elif hemi == 'both':
            labels = self.lh_labels + self.rh_labels
        labels = self._check_labels(labels)
        return labels        
    
    def _check_labels(self, labels: list) -> list:
        new_labels = []
        for label in labels:
            if label in self.name_exceptios:
                label = self.name_exceptios[label]
            if self.type == "cortical":
                label = label.split('-')[-1]
            new_labels.append(label)
        return new_labels
    
    def get_index(self, hemi: str) -> list:
        if hemi == 'lh':
            return self.lh_index
        elif hemi == 'rh':
            return self.rh_index
        elif hemi == 'both':
            return self.lh_index + self.rh_index      
        
    def is_type(self, roi_type: str) -> bool:
        return self.type == roi_type
        
    def set_value(self, value: float):
        self.value = value

class BrainBuilder():
    def __init__(self):
        pass
    
    @staticmethod
    def build(fs_roi_file: Path, drop: list = ['cerebellum', 'brainstem']):
        rois = read_rois(fs_roi_file)
        for roi_name in drop:
            rois.pop(roi_name)

        selected_rois = []
        for roi_name, roi_config in rois.items():
            selected_rois.append(Roi(roi_name, roi_config))

        return Brain(selected_rois)

class Brain():
    def __init__(self, rois: list[Roi]):
        self.rois = {}
        for roi in rois:
            self.rois[roi.name] = roi

    def __call__(self, roi_name) -> Roi:
        return self.rois[roi_name]
        
    def get_structures(self, location='cortical'):
        rois = []
        for roi_name, roi in self.rois.items():
            if roi.is_type(location):
                rois.append(roi)
        return Brain(rois)
    
    def set_values(self, values: dict):
        for roi_name, value in values.items():
            self.rois[roi_name].set_value(value)
    
    
