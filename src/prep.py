import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import logging

# %% binning
def bin_data(df, col_name, min_val=0.0, max_val=100.0, step=2.5):
    """Bin data into bins of size step from min_val to max_val.
    Args:
        df (pd.DataFrame): dataframe to bin
        col_name (str): name of column to bin
        min_val (float): minimum value of bins
        max_val (float): maximum value of bins
        step (float): size of bins
    Returns:
        df (pd.DataFrame): dataframe with binned column
    """
    # define bins from min_val to max_val in steps of step
    bins = np.arange(min_val, max_val + 2 * step, step)

    # divide into bins
    df[col_name + "_group"] = pd.cut(
        df[col_name], bins=list(bins), labels=bins[:-1], right=False
    ).astype(str)

    return df


def get_subsample(df, cat_col, sample_col, match_nsamples=True):
    """Get subsample of df with cat_col==cat_val and sample_col==sample_val.
    Args:
        df (pd.DataFrame): dataframe to subsample
        cat_col (str): name of categorical column
        sample_col (str): name of column to sample
        match_nsamples (bool): if True, match number of samples in each bin, default True
    Returns:
        df (pd.DataFrame): subsampled dataframe
    """
    # get age range values
    sample_vals = df[df[cat_col] == True][sample_col].unique()

    # match number of samples
    if match_nsamples:
        # get number of samples per age range
        samples_count = df[df[cat_col] == True][sample_col].value_counts()

        # subsample from each age range to match the number of samples in the coresponding group
        matched = pd.DataFrame()
        for group in sample_vals:
            n_samples = samples_count.loc[group]
            # get subsample from other group
            df_sub = df[(df[cat_col] == False) & (df[sample_col] == group)]

            if len(df_sub) < n_samples:
                subsample = df_sub
            else:
                subsample = df_sub.sample(n_samples)
            # append to matched
            matched = pd.concat([matched, subsample])

        # append original group
        df_sampled = pd.concat([matched, df[df[cat_col] == True]])

    else:
        df_sampled = df[df[sample_col].isin(sample_vals)]

    return df_sampled

