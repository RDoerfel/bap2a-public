#%%
from src import simulation
from src.prep import bin_data
from src.transform import DiMap, SelectCols, OneHotPD, NormEITV, get_column_transformer

import pandas as pd
import numpy as np
import pytest
from sklearn.compose import ColumnTransformer
# %% generate dataset with two columns and two categories

def _generate_data():
    min = 20
    max = 60
    N = 100
    population = simulation.get_population(min,max,N).reshape(1,-1)
    slope1 = -0.01
    intercept1 = 2
    slope2 = -0.03
    intercept2 = 4
    measure1 = simulation.ageing(population,slope1,intercept1,noise_level=0).reshape(1,-1)
    measure2 = simulation.ageing(population,slope2,intercept2,noise_level=0).reshape(1,-1)

    df1 = pd.DataFrame(np.concatenate([population,measure1,measure1],axis=0).T,columns=['age','col1','col2'])
    df2 = pd.DataFrame(np.concatenate([population,measure2,measure2],axis=0).T,columns=['age','col1','col2'])

    df1['cat'] = 'a'
    df2['cat'] = 'b'

    df = pd.concat([df1,df2],axis=0)

    max_val = 60.0
    min_val = 20.0
    step = 2.5
    col = 'age'
    df = bin_data(df, col, min_val=min_val, max_val=max_val, step=step)

    return df

def test_dimap_multiple_columns():
    df = _generate_data()
    df = OneHotPD(columns=['cat']).fit_transform(df)

    dimap = DiMap(cat_col='cat_a', sample_col='age_group', pattern='col', match_nsamples=False)
    dimap.fit(df)
    X = dimap.transform(df)
    assert X['col1'].equals(X['col2'])

def test_dimap():
    df = _generate_data()
    df = OneHotPD(columns=['cat']).fit_transform(df)

    dimap = DiMap(cat_col='cat_a', sample_col='age_group', pattern='col', match_nsamples=False)
    dimap.fit(df)
    X = dimap.transform(df)

    error = np.mean(X[X['cat_a']==True]['col1'] - X[X['cat_b']==True]['col1'])

    assert error < 0.00001

def test_dimap_raise_value_error():
    df = _generate_data()
    df = OneHotPD(columns=['cat']).fit_transform(df)

    dimap = DiMap(cat_col='cat_a', sample_col='age_group', pattern='col', match_nsamples=False)
    dimap.fit(df)
    df.loc[0,'col2'] = -20
    with pytest.raises(ValueError):
        X = dimap.transform(df)

def test_selectcols_keep_shape():
    df = _generate_data()
    select = SelectCols(keep=['col1'])

    X = select.fit_transform(df)

    assert X.shape[1] == 1

def test_selectcols_keep_name():
    df = _generate_data()
    column = 'col1'
    select = SelectCols(keep=[column])

    X = select.fit_transform(df)

    assert X.columns[0] == column


def test_dropcols_drop():
    df = _generate_data()
    column = 'col1'
    drop = SelectCols(drop=[column])

    X = drop.fit_transform(df)

    assert column not in X.columns

def test_dropcols_keep_get_feature():
    df = _generate_data()
    column = 'col1'
    drop = SelectCols(keep=[column])
    drop.transform(df)
    cols = drop.get_feature_names()
    assert column in cols

def test_onehotencoder():
    df = _generate_data()
    df['cat'] = df['cat'].astype('category')
    onehot = OneHotPD(columns=['cat'])
    X = onehot.fit_transform(df)
    # check if cat_a from 0 to 99 and cat_b from 100 to 199 is 1
    assert np.all(X['cat_a'][0:99] == 1)
    assert np.all(X['cat_b'][100:199] == 1)    

def test_nortmeitv():
    df = _generate_data()
    norm = NormEITV(pattern='col', icv_col='age')
    X = norm.fit_transform(df)
    assert np.all(X['col1'] == X['col2'])
    assert np.all(X['col1'] == df['col1'] / df['age'])
    assert np.all(X['col2'] == df['col2'] / df['age'])

def test_get_column_transformer_instance():
    ct = get_column_transformer(pattern='col')
    assert isinstance(ct, ColumnTransformer)

def test_get_column_transformer_transform():
    df = _generate_data()
    pattern = 'col1'
    ct = get_column_transformer(pattern='col1')
    X = ct.fit_transform(df)
    df_col1 = df.loc[:,'col1'].to_frame()

    assert X.columns[0] == f'col1'
    assert np.all(X.to_numpy() == df_col1.to_numpy())



