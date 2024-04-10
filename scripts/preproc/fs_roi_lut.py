"""
python roi_lut.py --roi_file .\data\rois_fs.json --save_dir .\data --name fs
"""
#%%
from pathlib import Path
from src import fs_roi_lut
import argparse
# %%
name = 'fs'
LOCATION = Path(__file__).parent
data_dir = LOCATION.parent.parent / 'data' 
save_dir = data_dir / 'derivatives'
roi_file = data_dir / f'rois_{name}.json'

# %%

def roi_lut(roi_file, save_dir, name, save):
    """ Create a lookup table for the ROIs
    args:
        roi_file (Path): path to the json file containing the ROIs
        save_dir (Path): directory to save the lookup table
        name (str): name of the lookup table
        save (bool): save lookup table
    """
    # %%
    rois = fs_roi_lut.read_rois(roi_file)
    fs_roi_lut.print_regions(rois)
    if save:
        fs_roi_lut.save_to_roi_lut(rois, save_dir, name)


def get_parser():
    """ Get parser object for script get_data.py 
    returns: parser object
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--roi_file', type=str, default=roi_file, help='Json file containing the rois')
    parser.add_argument('--save_dir', type=str, default=save_dir, help='Path to the result directory')
    parser.add_argument('--create', action='store_true', help='Create roi_lut excel')
    parser.add_argument('--name', type=str, help='Name to add to file', default = name)
    return parser

def run():
    """ Run script create_roi_lut.py """
    parser = get_parser()
    args = parser.parse_args()

    roi_file = args.roi_file
    save_dir = args.save_dir
    name = args.name
    create = args.create

    print(f"roi_lut.py --roi_file {roi_file} --save_dir {save_dir} --name {name} --create")
    roi_lut(roi_file, save_dir, name, create)
    
if __name__ == "__main__":
    run()
