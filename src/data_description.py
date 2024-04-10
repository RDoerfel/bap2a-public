import pandas as pd
from src.plotting import set_r_params, set_style
import seaborn as sns

def load_worklist(path,column_names, column_name_mapping):
    """Load worklist from excel file
    args:
        path (str): path to excel file
        column_names (list): list of column names to load
        column_name_mapping (dict): mapping of column names to new names
    returns:
        pandas.DataFrame: data"""
    data = pd.read_excel(path, usecols=column_names)
    data.rename(columns=column_name_mapping, inplace=True)
    return data

def print_demographics(data,baseline = False):
    """print demographics from data
    args:
        data (pandas.DataFrame): data
        baseline (bool): if True, print baseline demographics
    """
    n_scans = data.shape[0]
    if baseline:
        data = data.drop_duplicates(subset='subject_id', keep='first')
    n_subjects = data.shape[0]
    print(f"{n_subjects} and {n_scans} scans")
    n_female = sum(data['gender'] == 'Female')
    print("Subjects: {} (Female: {})".format(n_subjects,n_female))
    age_range = [data['chron_age'].min(), data['chron_age'].max()]
    print("Age range: {:.2f} to {:.2f}".format(age_range[0], age_range[1]))
    age_mean = data['chron_age'].mean()
    age_std = data['chron_age'].std()
    print("Age mean: {:.2f} +/- {:.2f}".format(age_mean, age_std))

def plot_age_distribution(data, xlim, ylim, xticks, yticks,title=None):
    """plot age distribution
    args:
        data (pandas.DataFrame): data
        xlim (list): x-axis limits
        ylim (list): y-axis limits
        xticks (list): x-axis ticks
        yticks (list): y-axis ticks
        title (str): plot title
    returns:
        seaborn.FacetGrid: plot"""
    cm = 1/2.54
    set_r_params(small=8, medium=10, big=12)
    grid = sns.displot(data,x='chron_age',hue='gender',kind='hist',palette='Dark2',multiple="stack",edgecolor='white',alpha=.9,height=7*cm,aspect=1)
    grid.set(xlim=xlim, ylim=ylim, xticks=xticks, yticks=yticks)
    grid.axes[0,0].set_xlabel('Chronological Age')
    grid.set(title=title)
    set_style(grid)
    return grid
