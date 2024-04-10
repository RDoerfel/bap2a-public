#%%
from src.data_wrangler import DataWrangler, DataSpec
from pathlib import Path
import pandas as pd

#%% setup paths
DATADIR = Path(__file__).parent.parent / "data"
RESULTDIR = Path(__file__).parent.parent / "results"

#%% setup data
data_file = DATADIR / "database.xlsx"
data_spec = DataSpec(data_file,
                     covarities=['tracer'],
                     exclude=['both'],
                     tracer=None)

#%% setup data wrangler
data_wrangler = DataWrangler(data_spec)
data_wrangler.prepare_data()
data = data_wrangler.get_data()               

# %% setup summary csv
# row1: cimbi
# row2: altanserin
# row3: total
# column 1: count male/female
# column 2: mean age (std)
# column 3: count mr_strength == 1.5T / 3T
# column 4: count camera == GE / HRRT
summary_file = RESULTDIR / "data_descr.csv"

#%% setup summary dataframe
summary = pd.DataFrame(columns=['cimbi', 'altanserin', 'total'])
summary['cimbi'] = [0,0,0,0]
summary['altanserin'] = [0,0,0,0]
summary['total'] = [0,0,0,0]

#%% gender
print(data.groupby(['tracer_C','gender']).count()['subject_id'])
print(data.groupby(['gender']).count()['subject_id'])
#%% mr_strength
print(data.groupby(['tracer_C','mr_strength']).count()['subject_id'])
print(data.groupby(['mr_strength']).count()['subject_id'])
#%% camera
print(data.groupby(['tracer_C','camera']).count()['subject_id'])
print(data.groupby(['camera']).count()['subject_id'])

#%% age mean (std)
print(data.groupby(['tracer_C']).mean()['chron_age'])
print(data.groupby(['tracer_C']).std()['chron_age'])
print(data['chron_age'].mean())
print(data['chron_age'].std())

# %% age min / max
print(data.groupby(['tracer_C']).min()['chron_age'])
print(data.groupby(['tracer_C']).max()['chron_age'])
print(data['chron_age'].min())
print(data['chron_age'].max())
