#%% Imports
from pathlib import Path
import argparse
from src.logsetup import Logger
from src.experiment import  ExperimentBuilder

import sys
import os
import warnings 

#%% set Paths and configs 
RESULTDIR = Path(__file__).parent.parent / "results"
DATADIR= Path(__file__).parent.parent / "data" 

def run(data_dir: Path, result_dir: Path, exp_name: str, n_jobs: int = 1):
    if not sys.warnoptions:
        warnings.simplefilter("ignore")
        os.environ["PYTHONWARNINGS"] = "ignore"
    logger = Logger(result_dir=result_dir, name=exp_name)
    with logger as redirector:
        # Build experiment
        experiment = ExperimentBuilder.build(data_dir, "experiment.yml", exp_name, result_dir)
            
        # run experiment 
        results = experiment.run(n_jobs)

if __name__ == '__main__':
    # Parse arguments
    # nice python run_experiment.py --exp_name experiment-I --n_jobs 40
    parser = argparse.ArgumentParser(description='Run experiment')
    parser.add_argument('--exp_name', type=str, default='experiment-I', help='Name of experiment')
    parser.add_argument('--data_dir', type=str, default=DATADIR, help='Path to data directory')
    parser.add_argument('--result_dir', type=str, default=RESULTDIR, help='Path to result directory')
    parser.add_argument('--n_jobs', type=int, default=1, help='Number of jobs to run in parallel')

    args = parser.parse_args()
    exp_name = args.exp_name
    data_dir = Path(args.data_dir)
    result_dir = Path(args.result_dir)
    n_jobs = args.n_jobs

    run(data_dir, result_dir, exp_name, n_jobs=n_jobs) 
# %%
