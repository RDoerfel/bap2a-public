#%%
import numpy as np
import pandas as pd

from src.prep import bin_data, get_subsample

def _generate_data():
    """ Generate data for testing """
    # simulate data
    data1 = np.arange(0,11,1)
    data2 = np.arange(3,7,1)

    # append data with itself
    data1 = np.append(data1, data1)
    data2 = np.append(data2, data2)

    # create dataframes
    df1 = pd.DataFrame(data1, columns=['age'])
    df2 = pd.DataFrame(data2, columns=['age'])

    # add categorical variable
    df1['cat'] = 'a'
    df2['cat'] = 'b'
    df = pd.concat([df1, df2])

    # onehot
    df = pd.get_dummies(df, columns=['cat'])
    # combine dataframes and return
    return df

def test_bin_data():
    """ Test binning data """
    df = _generate_data()

    # bin data
    max_val = 10.0
    min_val = 0.0
    step = 2
    df = bin_data(df, 'age', min_val=min_val, max_val=max_val, step=step)

    # test if binning works
    bins = np.arange(min_val,max_val+2*step,step)
    expected = np.zeros(len(bins))
    actual = np.zeros(len(bins))
    for i in range(len(bins)-1):
        expected[i] = len(df[df['age'].between(bins[i], bins[i+1], inclusive='left')])
        actual[i] = len(df[df['age_group']==str(bins[i])])

    assert np.array_equal(expected, actual)

    # test that age 4 is in the right bin
    assert df[df['age']==4]['age_group'].values[0] == str(4.0)

def test_subsample():
    """ Test subsampling """
    df = _generate_data()

    # bin data
    max_val = 10.0
    min_val = 0.0
    step = 2
    col = 'age'
    df = bin_data(df, col, min_val=min_val, max_val=max_val, step=step)

    # get same age groups for a and b
    df_sampled = get_subsample(df, 'cat_b', 'age_group', match_nsamples=False)

    # convert age group to float
    df['age_group'] = df['age_group'].astype(float)
    df_sampled['age_group'] = df_sampled['age_group'].astype(float)

    # test if same age groups are in a and b
    expected = df[df['age_group'].between(2,6)].groupby(['age_group','cat_b'])['age'].count().to_numpy()
    actual = df_sampled.groupby(['age_group','cat_b'])['age'].count().to_numpy()

    assert np.array_equal(expected, actual)

def test_subsample_matched():
    """ Test subsampling with matched groups """
    df = _generate_data()

    # bin data
    max_val = 10.0
    min_val = 0.0
    step = 2
    col = 'age'

    # bin data
    df = bin_data(df, col, min_val=min_val, max_val=max_val, step=step)

    # get matched
    df_matched = get_subsample(df, 'cat_b', 'age_group', match_nsamples=True)

    count_total = df_matched["age_group"].value_counts()
    count_a = df_matched[df_matched["cat_b"] == True]["age_group"].value_counts()
    count_b = df_matched[df_matched["cat_a"] == True]["age_group"].value_counts()

    assert np.array_equal(count_a, count_b)

# %%
