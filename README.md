# Multimodal brain age prediction using machine learning: combining structural MRI and 5-HT2AR PET derived features
Scripts and documentation for the paper "Multimodal brain age prediction using machine learning: combining structural MRI and 5-HT2AR PET derived features".

bioRxiv: [https://www.biorxiv.org/content/10.1101/2024.02.05.578968v2](https://www.biorxiv.org/content/10.1101/2024.02.05.578968v2)

## Abstract
To better assess the pathology of neurodegenerative disorders and the efficacy of neuroprotective interventions, it is necessary to develop biomarkers that can accurately capture age-related biological changes in the human brain. Brain serotonin 2A receptors (5-HT2AR) show a particularly profound age-related decline and are also reduced in neurodegenerative disorders, such as Alzheimer’s disease.

This study investigates whether the decline in 5-HT2AR binding, measured in vivo using positron emission tomography (PET), can be used as a biomarker for brain aging. Specifically, we aim to 1) predict brain age using 5-HT2AR binding outcomes, 2) compare 5-HT2AR-based predictions of brain age to predictions based on gray matter (GM) volume, as determined with structural magnetic resonance imaging (MRI), and 3) investigate whether combining 5-HT2AR and GM volume data improves prediction.

We used PET and MR images from 209 healthy individuals aged between 18 and 85 years (mean=38, std=18), and estimated 5-HT2AR binding and GM volume for 14 cortical and subcortical regions. Different machine learning algorithms were applied to predict chronological age based on 5-HT2AR binding, GM volume, and the combined measures. The mean absolute error (MAE) and a cross-validation approach were used for evaluation and model comparison.

We find that both the cerebral 5-HT2AR binding (mean MAE=6.63 years, std=0.74 years) and GM volume (mean MAE=6.95 years, std=0.83 years) predict chronological age accurately. Combining the two measures improves the prediction further (mean MAE=5.54 years, std=0.68). In conclusion, 5-HT2AR binding measured using PET might be useful for improving the quantification of a biomarker for brain aging.

## Citation
```
@article{D{\"o}rfel2024.02.05.578968,
  title = {Multimodal Brain Age Prediction Using Machine Learning: Combining Structural {{MRI}} and 5-{{HT2AR PET}} Derived Features},
  author = {D{\"o}rfel, Ruben P. and {Arenas-Gomez}, Joan M. and Svarer, Claus and Ganz, Melanie and Knudsen, Gitte M. and Svensson, Jonas E. and {Plav{\'e}n-Sigray}, Pontus},
  year = {2024},
  journal = {bioRxiv : the preprint server for biology},
  eprint = {https://www.biorxiv.org/content/early/2024/02/28/2024.02.05.578968.full.pdf},
  publisher = {Cold Spring Harbor Laboratory},
  doi = {10.1101/2024.02.05.578968},
``` 

## Usage
To use the code in this repository, you need to install the local package. This can be done by running the following command in the root of the repository:
```bash
# clone the repository
https://github.com/RDoerfel/bap2a-public.git

# install the environment
conda env create -f environment.yml

# activate the environment
conda activate bap2a-public

# install the package
pip install -e .

```