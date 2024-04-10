#%%
from pathlib import Path
import pandas as pd
from src.paths import Paths
from src.data_description import load_worklist

#%% set paths
data_dir = Path(__file__).parent.parent.parent / 'data'
paths = Paths(data_dir / "paths.json")
database_dir = Path(paths("CIMBI_DATABASE_DIR"))

#%% 1. combine worklist and database
# load files
alt_database_file = database_dir / "ALT_Impetus_JonasS.xlsx"
cimbi_database_file = database_dir / "C36_Impetus_JonasS.xlsx"

# reanme columns
alt_mapping = {"MR log number used for this ALT PET analysis - T1": "mr_id", 
               "CIMBI ID": "subject_id", 
               "ALT ID": "pet_id",
               "Gender": "gender", 
               "Age at ALT scan": "chron_age",
               "MR strength used for this ALT PET analysis - T1": "mr_strength",
               "ALT scan protocol": "camera"}   

cimbi_mapping = {"MR log number used for this Cimbi-36 PET analysis - T1": "mr_id",
                 "CIMBI ID": "subject_id",
                 "Cimbi-36 ID": "pet_id",
                 "Gender":"gender",
                 "Age at Cimbi36 scan":"chron_age",
                 "MR strength used for this Cimbi-36 PET analysis - T1": "mr_strength",
                 "Cimbi-36 scan protocol": "camera"}

# load data
alt_database = load_worklist(alt_database_file,alt_mapping.keys(),alt_mapping)
cimbi_database = load_worklist(cimbi_database_file,cimbi_mapping.keys(),cimbi_mapping)

# drop scans because new MR is quite far away from PET data
alt_scans_to_drop = ['f4165','f5037','f4550','f4295','f4324','f4412','f4352'] 

alt_database = alt_database[~alt_database['mr_id'].isin(alt_scans_to_drop)]

# combine cimbi and altanserin data
database = pd.concat([alt_database,cimbi_database],axis=0)
database.reset_index(inplace=True,drop=True)
database.set_index('subject_id',inplace=True)

# add camera column
database.loc[database['camera'].str.contains('HRRT'),'camera'] = 'HRRT'    
database.loc[database['camera'].str.contains('GEAdvance'),'camera'] = 'GE'

# add scanner column
database['scanner'] = database['mr_id'].str[0]

# add tracer column
database['tracer'] = database['pet_id'].str[0]

# add type column
database['type'] = "subject"
alt_ad_patients = ['alt283','alt285','alt290','alt301','alt307','alt311','alt345','alt346','alt371','alt373','alt375']
alt_ad_control =['alt286', 'alt297', 'alt336', 'alt338', 'alt339', 'alt377', 'alt379', 'alt381', 'alt382']
# set type to patient for altanserin patients
database.loc[database['pet_id'].isin(alt_ad_patients),'type'] = "patient"
# set type to control for altanserin controls
database.loc[database['pet_id'].isin(alt_ad_control),'type'] = "control"

# %% 2. load get_worklist_files to get the eventually used mr_id

alt_worklist_file = Path(paths('DATA_DIR')) / 'Altanserin' / 'worklist_get_files.xlsx'
cimbi_worklist_file = Path(paths('DATA_DIR')) / 'Cimbi36' / 'worklist_get_files.xlsx'

# rename columns
alt_mapping = {"MR log number used for this ALT PET analysis - T1": "mr_id", 
               "CIMBI ID": "subject_id", 
               "ALT ID": "pet_id"}   

cimbi_mapping = {"MR log number used for this Cimbi-36 PET analysis - T1": "mr_id",
                 "CIMBI ID": "subject_id",
                 "Cimbi-36 ID": "pet_id"}

# load files
alt_worklist = load_worklist(alt_worklist_file,alt_mapping.keys(),alt_mapping)
cimbi_worklist = load_worklist(cimbi_worklist_file,cimbi_mapping.keys(),cimbi_mapping)

# add tracer column
alt_worklist['tracer'] = 'a'
cimbi_worklist['tracer'] = 'C'

# combine cimbi and altanserin data
worklist = pd.concat([alt_worklist,cimbi_worklist],axis=0)
worklist.reset_index(inplace=True,drop=True)
worklist.set_index('subject_id',inplace=True)

# drop mr_id column
database.drop(columns=['mr_id'],inplace=True)

# merge worklist into database based on subject_id, tracer, and pet_id
db_wl = database.merge(worklist, on=['subject_id', 'tracer', 'pet_id'], how='left')

# %% 3. combine PET data
# load files
alt_pet_file = data_dir / 'pet' / 'alt_bpp_fslobes.xlsx'
cimbi_pet_file = data_dir / 'pet' / 'cimbi_bpnd_fslobes.xlsx'

# read data
df_pet_alt = pd.read_excel(alt_pet_file)
df_pet_cimbi = pd.read_excel(cimbi_pet_file)

# rename columns
df_pet_alt.rename(columns={'CIMBI ID':'subject_id'},inplace=True)
df_pet_cimbi.rename(columns={'CimbiID':'subject_id', 'PET_ID':'pet_id'},inplace=True)

# set indec to subject_id
df_pet_alt.set_index('subject_id',inplace=True)
df_pet_cimbi.set_index('subject_id',inplace=True)

# drop brain-stem, cerebellum, and All_voxels (alt)
df_pet_alt.drop(columns=['brain-stem','cerebellum','All_voxels'],inplace=True)
df_pet_cimbi.drop(columns=['brain-stem','cerebellum', 'pet_id'],inplace=True)

# add 'pet_' to columns name
df_pet_alt.columns = ['pet_' + col for col in df_pet_alt.columns]
df_pet_cimbi.columns = ['pet_' + col for col in df_pet_cimbi.columns]

# add tracer column to make merging easier
df_pet_alt['tracer'] = 'a'
df_pet_cimbi['tracer'] = 'C'

# concatenate both cimbi and alt
df_alt_cimbi = pd.concat([df_pet_alt,df_pet_cimbi],axis=0)

# merge alt and cimbi data into database
db_pet = db_wl.merge(df_alt_cimbi, on=['subject_id', 'tracer'], how='left')

# %% 4. combine brain-age data
# load files
alt_brainage_file = data_dir / 'brain-age' / 'alt_pyment_predicted_age.csv'
cimbi_brainage_file = data_dir / 'brain-age' / 'cimbi36_pyment_predicted_age.csv'

# read data
df_brainage_alt = pd.read_csv(alt_brainage_file)
df_brainage_cimbi = pd.read_csv(cimbi_brainage_file)

# concatenate both cimbi and alt
df_brainage_alt_cimbi = pd.concat([df_brainage_alt,df_brainage_cimbi],axis=0)

# drop duplicates
df_brainage_alt_cimbi.drop_duplicates(subset=['mrID'],inplace=True)

# rename index to mr_id and mr_predicted_age to pyment
df_brainage_alt_cimbi.rename(columns={'predicted_age':'pyment', 'mrID':'mr_id'},inplace=True)

# merge alt and cimbi data into database
db_pet.reset_index(inplace=True)
db_brainage = db_pet.merge(df_brainage_alt_cimbi, on=['mr_id'], how='left')

# %% 5. add mri data
# load files
alt_mri_file = data_dir / 'mri' / 'alt_mri_stats_fslobes.csv'
cimbi_mri_file = data_dir / 'mri' / 'cimbi_mri_stats_fslobes.csv'

# read data
df_mri_alt = pd.read_csv(alt_mri_file)
df_mri_cimbi = pd.read_csv(cimbi_mri_file)

# combine alt and cimbi
df_mri = pd.concat([df_mri_alt,df_mri_cimbi],axis=0)

# rename 'subject_id' to 'mr_id'
df_mri.rename(columns={'subject_id':'mr_id'},inplace=True)

# set index to mr_id
df_mri.set_index('mr_id',inplace=True)

# add 'mri_' to columns name 
df_mri.columns = ['mri_' + col for col in df_mri.columns]

# Drop mri_eITV, as we will use the SPM estimates
df_mri.rename(columns={'mri_eITV': 'eITV'},inplace=True)

# remove duplicates
df_mri = df_mri.loc[~df_mri.index.duplicated(keep='first')]

# merge mri data into database based on mr_id
db_mri = db_brainage.merge(df_mri, on=['mr_id'], how='left')

#%% 6. add ICV as estimated using SPM
# load files
alt_icv_file = data_dir / 'mri' / 'alt_icvs.csv'
cimbi_icv_file = data_dir / 'mri' / 'c36_icvs.csv'

# read data
df_icv_alt = pd.read_csv(alt_icv_file)
df_icv_cimbi = pd.read_csv(cimbi_icv_file)

# combine alt and cimbi
df_icv = pd.concat([df_icv_alt,df_icv_cimbi],axis=0)
df_icv.reset_index(inplace=True)
df_icv.drop(columns={'index', 'pet_id'},inplace=True)

# add icv to alt rows for subjects with both
duplicated_mr_id = df_icv[df_icv['mr_id'].duplicated()].mr_id

for duplicated_id in duplicated_mr_id:
    df_icv.loc[df_icv['mr_id'] == duplicated_id,'icv'] = max(df_icv[df_icv['mr_id'] == duplicated_id]['icv'])

df_icv.drop_duplicates(inplace=True)

# convert from L to mm3
df_icv['icv'] = df_icv['icv'] * 10**6
# merge mri data into database based on mr_id
df_icv = db_mri.merge(df_icv, on=['mr_id', 'subject_id'], how='left')

#%% 7. clean data and remove some subjects / scans
data = df_icv.copy()

# remove subjects that are identified to be problematic
remove = [55162]
data = data[~data['subject_id'].isin(remove)]

# mark duplicates
duplicates = data[data.duplicated(subset=['subject_id'],keep=False)].sort_values(by='subject_id')
data['both'] = data.duplicated(subset=['subject_id'],keep=False)

# %% 8. save the final file to excel
data.to_excel(data_dir / 'database.xlsx', index=False)

# %%
