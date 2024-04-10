#%%
from src import fs_roi_lut
import json
import os
import pytest
import pandas as pd

TEST_FILE_ROIS= 'rois.json'
TEST_FILE_LUT= 'ROI_LUT_FS_2_PVE_test.xlsx'

def _create_json(mode):
    """ create a json file for testing
    args: 
        mode (int): 0: working, 1: wrong label, 2 not matching index/label length"""
    layout = {'test_region':{'hemi':{'lh':{'label':['Unknown'], 'index':[0]},'rh':{'label':['Unknown'], 'index':[0]}},'location':'test','file':'test'}}
    if mode == 0:
        pass
    elif mode == 1:
        layout['test_region']['hemi']['lh']['index'] = [1]
    elif mode == 2:
        layout['test_region']['hemi']['lh']['index'] = [1,2]

    with open(TEST_FILE_ROIS, 'w') as outfile:
        json.dump(layout, outfile)

def teardown_module():
    os.remove(TEST_FILE_ROIS) 
    os.remove(TEST_FILE_LUT)

def test_read_rois_working():
    _create_json(mode=0)
    rois = fs_roi_lut.read_rois(TEST_FILE_ROIS,validate=True)
    assert rois['test_region']['hemi']['lh']['index'] == [0]

def read_roi_names():
    _create_json(mode=0)
    assert fs_roi_lut.read_roi_names(TEST_FILE_ROIS) == ['test_region']

def test_read_rois_wrong_label():
    _create_json(mode=1)
    with pytest.raises(AssertionError) as e:
        fs_roi_lut.read_rois(TEST_FILE_ROIS,validate=True)
    assert str(e.value) == "Labels do not match. Expected: Unknown, Actual: Left-Cerebral-Exterior."

def test_read_rois_not_matching_index_label_length():
    _create_json(mode=2)
    with pytest.raises(AssertionError) as e:
        fs_roi_lut.read_rois(TEST_FILE_ROIS,validate=True)
    assert str(e.value) == "Number of indices and labels do not match. Indices: 2, Labels: 1."

def test_save_to_roi_lut_exists():
    _create_json(mode=0)
    rois = fs_roi_lut.read_rois(TEST_FILE_ROIS,validate=True)
    fs_roi_lut.save_to_roi_lut(rois,'.','test')
    assert os.path.isfile(TEST_FILE_LUT)

def test_save_to_roi_lut_correct():
    _create_json(mode=0)
    rois = fs_roi_lut.read_rois(TEST_FILE_ROIS,validate=True)
    fs_roi_lut.save_to_roi_lut(rois,'.','test')

    df_test = pd.read_excel(TEST_FILE_LUT)

    assert df_test['FS_index'][0] == 0
    assert df_test['PVE_index'][0] == 1
    assert df_test['PVE_name'][0] == 'test_region'

# %%
