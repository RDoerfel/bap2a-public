# Data

**This folder is only ment to contain derivative data. Subject data and delicate information stays on the servers.** 

## Directories
| Folder | Description                                         |
|--------|-----------------------------------------------------|
| derivatives | derivatives from scripts, to be used from other scripts. intermediate results so to say. | 
| brain-age | directory to store brain age estimates from other packages | 
| mri | directory to store the mri data. roi names should match the ones in [rois_fs.json](rois_fs.json) | 
| pet | directory to store pet data. roi names should match the ones in [rois_fs.json](rois_fs.json) | 

## Files
|file|description|
|--|--|
| [rois_fs.json](rois_fs.json) | FS based regions of interest to be used for the analysis. |
| [experiment.yml](experiment.yml) | Configureaton for the different experiments |
| [models.yml](models.yml) | Configuration for the different pipelines to run in each experiment |
| [pipelines.yml](pipelines.yml) | Configuration of the various models to run in each pipeline |






