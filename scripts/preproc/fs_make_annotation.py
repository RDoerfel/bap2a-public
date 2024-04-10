#%%
from pathlib import Path
from src import fs_roi_lut
import nibabel as nib
import seaborn as sns

#%%
name = 'fs'
LOCATION = Path(__file__).parent
data_dir = LOCATION.parent.parent / 'data'
roi_file = Path(data_dir,f'rois_{name}.json')
location = Path(__file__).parent
subject_dir = location.parent.parent.parent / 'fsaverage'
annot_file = Path(subject_dir,'label','lh.aparc.annot')
hemi = 'lh'
# %%
rois = fs_roi_lut.read_rois(roi_file)
annot = nib.freesurfer.io.read_annot(annot_file,orig_ids=False)

# %%
n_regions = 7
vertices = annot[0]
vertices_new = vertices.copy()
annotations = annot[2]
annotations = [x.decode('UTF-8') for x in annotations]
annot_new = set()

palette = sns.color_palette("tab10")
ctab_new = annot[1][:n_regions]

# %%

index = 0
for region in rois:
    if rois[region]['location'] == 'cortical':
        color = palette[index]
        color_rgb = [int(x*255) for x in color]
        ctab_new[index][:3]= color_rgb
        print(f"region: {region}, index: {index}")
        
        for label in rois[region]['hemi'][hemi]['label']:
            label = label.split('-')[-1]
            label_index = annotations.index(label)
            print(f"{region}: {label}, {label_index}, vertices: {sum(vertices_new == label_index)}")
            vertices_new[vertices == label_index] = index
        annot_new.add(region)
        index = index + 1

#%%
nib.freesurfer.io.write_annot(subject_dir / 'label' / f'{hemi}.{name}.annot',vertices_new,ctab_new,list(annot_new))
nib.freesurfer.io.write_annot(data_dir / 'derivatives' / f'{hemi}.{name}.annot',vertices_new,ctab_new,list(annot_new))

test=nib.freesurfer.io.read_annot(subject_dir / 'label' / f'{hemi}.{name}.annot')

# %%

# %%
