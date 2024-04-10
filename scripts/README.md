# Scripts
Scripts to run and analyze the workflows.

## Directories
| Directories                | Description                                               |
|---------------------|------------------------------------------------------------------|
| preproc | The preprocessing and data wrangling steps to get the data into shape. This is very specific to the setup we had at the NRU. |
## Files
| File                | Description                                                      |
|---------------------|------------------------------------------------------------------|
|[print_demographics.py](print_demographics.py)| Print the demographics of the data |
|[run_analysis_eval.py](run_analysis_eval.py)| Evaluate the different models. Produce figures and tables for the article. |
|[run_analysis_modality.py](run_analysis_modality.py)| Compare the different modalities. Produce figures and tables for the article. |
|[run_experiment.py](run_experiment.py)| Run the actual predictions. |

## Usage

### 1. Preprocessing
#### Prepare FS annotations to be used in PET pipeline and FreeSurfer
- [fs_make_annotation.py](preproc/fs_make_annotation.py) creates annotation files for the Jonas pipeline. For this, create a rois_[name].json file explaining what rois to combine
- [fs_roi_lut.py](preproc/fs_roi_lut.py) creates the ROI_LUT_FS file for the Jonas pipeline. For this, create a rois_[name].json file explaining what rois to combine

#### Run Jonas Pipeline (Matlab)
We used an inhouse pipeline for the estimation of binding potential. 

#### Compute ICVs (Matlab)
We used SPM12 to compute the ICV for each subject.
- [compute_icv.m](preproc/compute_icv.m) computes the ICV for each subject
- [combine_icv.m](preproc/combine_icv.m) combines the ICV for each subject into one table

#### Get FS statistics
We used the FreeSurfer recon-all pipeline to compute statistics for aseg and aparc atlases.
- [fs_get_summary_stats.py](preproc/fs_get_summary_stats.py) gets the summary statistics for the FreeSurfer data from each subject
- [copy_mri_stats.py](preproc/copy_mri_stats.py) copies the mri stats from the FreeSurfer output to the data folder
- [combine_mri_rois.py](preproc/combine_mri_rois.py) combines regional data from the FS stats into regios defined in the [rois_fs.json](../data/rois_fs.json)

#### combine data into one super mega master sheet
- [combine_data.py](preproc/combine_data.py) combines the data from the different steps into one super mega master sheet

### 2. Run predictions
- [run_experiment.py](run_experiment.py) runs the predictions for the different models. It works as cli and can run different experiments. experiments are defined in the [experiment.yml](../data/experiment.yml) file. For the paper, experiment-I was used.

### 3. Analyze the results
- [run_analysis_eval.py](run_analysis_eval.py) evaluates the different models. It produces figures and tables for the article.
- [run_analysis_modality.py](run_analysis_modality.py) compares the different modalities. It produces figures and tables for the article.

