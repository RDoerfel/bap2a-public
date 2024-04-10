from pathlib import Path
import pandas as pd
import numpy as np

class StatsFile():
    def __init__(self, file: Path, type: str) -> None:
        self.file = file
        self.type = type
        self.stats = pd.read_csv(file, sep='\t')
        self.stats.rename(columns={'Measure:volume':'subject_id', 'lh.aparc.volume':'subject_id', 'rh.aparc.volume':'subject_id'}, inplace=True)
        self.stats.set_index('subject_id', inplace=True)
    
    def _check_id(self, id: str) -> bool:
        return id in self.stats.index

    def get_eitv(self, id: str) -> float:
        if not self._check_id(id):
            print(f"Subject {id} not found in {self.file}")
            return np.nan
        else:
            return self.stats.loc[id]['EstimatedTotalIntraCranialVol']
    
    def get_roi_volume(self, id: str, labels: list) -> float:
        if not self._check_id(id):
            print(f"Subject {id} not found in {self.file}")
            return np.nan
        else:
            volume = 0
            for label in labels:
                volume += self.stats.loc[id][label]
            return volume 
        
    def combine_rois(self, labels: list) -> pd.DataFrame:
        # return dataframe with summed columns for each label
        return self.stats[labels].sum(axis=1)
