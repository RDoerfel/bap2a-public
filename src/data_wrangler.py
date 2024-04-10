import pandas as pd
from pathlib import Path
from src.transform import OneHotPD
from src.prep import bin_data


class DataSpec():
    def __init__(self, data_file: Path, covarities: list, exclude: list, tracer: str, type: list):
        self.data_file = data_file
        self.covarities = covarities
        self.exclude = exclude
        self.tracer = tracer
        self.type = type

    def __str__(self):
        return f"\n\tFile: {self.data_file}\n\tCovarities: {self.covarities}\n\tExclude: {self.exclude}\n\tTracer: {self.tracer}"
    
class DataWrangler:
    def __init__(self, data_spec: DataSpec):

        self.covarities = data_spec.covarities
        self.exclude = data_spec.exclude
        self.tracer = data_spec.tracer
        self.data_file = data_spec.data_file
        self.type = data_spec.type
        self.data = None

    def _print_config(self):
        print(f"Covarities: {self.covarities}")
        print(f"Exclude: {self.exclude}")
        print(f"Tracer: {self.tracer}")

    def prepare_data(self):
        """Prepare data for experiment"""
        self._load_data(self.data_file)
        self._select_tracer(self.tracer)
        nscans = len(self.data["subject_id"])
        self._remove_hrrt_altanserin()
        nscans_after = len(self.data["subject_id"])
        print(f"Removed {nscans - nscans_after} HRRT altanserin scans")
        self._remove_second_scan()
        nscans_after2 = len(self.data["subject_id"])
        print(f"Removed {nscans_after - nscans_after2} follow-up scans")
        self._remove_nan()
        nscans_after3 = len(self.data["subject_id"])
        print(f"Removed {nscans_after2 - nscans_after3} scans with nan")
        self._keep_type(self.type)
        nscans_after4 = len(self.data["subject_id"])
        print(f"Removed {nscans_after3 - nscans_after4} scans that were not type {self.type}")
        self._remove_columns(self.exclude)
        self._dummify(self.covarities)
        self.data = bin_data(self.data, 'chron_age', min_val=0.0, max_val=100.0, step=2.5)
    
    def rename_columns(self, rename:list, prefix:str):
        """Rename columns in data by adding prefix"""
        for item in rename:
            # check if column exists
            if item in self.data.columns:
                self.data = self.data.rename(columns={item: prefix + '_' + item})

    def get_data(self):
        return self.data

    def _load_data(self,worklist_file):
        """Load data from worklist file"""
        self.data = pd.read_excel(worklist_file, index_col="pet_id")

    def _select_tracer(self,tracer):
        """Select data for tracer"""
        if tracer is not None:
            self.data = self.data[self.data["tracer"] == tracer]

    def _remove_columns(self,exclude):
        """Remove columns from data"""
        for item in exclude:
            # check if column exists
            if item in self.data.columns:
                self.data = self.data.drop(columns=[item])

    def _remove_hrrt_altanserin(self):
        """Remove HRRT altanserin self.data"""
        self.data = self.data[
            ((self.data["tracer"] == "a") & (self.data["camera"] == "GE")) | (self.data["tracer"] == "C")
        ]

    def _dummify(self, covarities):
        """dummify data"""
        # one-hot encode categoricals (_dummify)
        self.data = OneHotPD(covarities).fit_transform(self.data)

    def _remove_second_scan(self):
        """Remove second scan of same subject"""
        self.data = self.data[~self.data["subject_id"].duplicated(keep="first")]

    def _remove_nan(self):
        """Remove rows with nan"""
        self.data = self.data.dropna()

    def _keep_type(self, type_keep: list):
        """Keep only scans of type"""
        self.data = self.data[self.data["type"].isin(type_keep)]

    def save_data(self, resultdir: Path, name: str):
        """Save self.data to file"""
        self.data.to_excel(resultdir / f"prepared_data_{name}.xlsx")