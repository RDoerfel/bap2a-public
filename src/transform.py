import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer, make_column_selector
from src import prep
from src.nodim import transform_nodim, estimate_params

class DiMap(BaseEstimator, TransformerMixin):
    """Distribution Mapping Transformer."""

    def __init__(self, cat_col, sample_col, pattern, match_nsamples=True):
        """Initialize the transformer.
        Args:
            cat_col (str): name of categorical column (tracer)
            sample_col (str): name of column to sample (chron_age_group)
            pattern (str): pattern of columns to use
            match_nsamples (bool): if True, match number of samples in each bin, default True"""
        self.cat_col = cat_col
        self.sample_col = sample_col
        self.pattern = pattern
        self.match_nsamples = match_nsamples

    def fit(self, X, y=None):
        """Fit the transformer.
        Args:
            X (pd.DataFrame): dataframe to subsample
            y (pd.Series): target variable (not used)"""
        matched = prep.get_subsample(
            df=X,
            cat_col=self.cat_col,
            sample_col=self.sample_col,
            match_nsamples=self.match_nsamples,
        )
        X_subset_1 = matched[matched[self.cat_col]==True]
        X_subset_2 = matched[matched[self.cat_col]==False]

        # get params for all columns
        self.params1 = {}
        self.params2 = {}
        self.columns = [col for col in X.columns if col.startswith(self.pattern)]
        for col in self.columns:
            if col in [self.cat_col, self.sample_col]:
                continue
            self.params1[col] = estimate_params(X_subset_1[col])
            self.params2[col] = estimate_params(X_subset_2[col])


        return self

    def transform(self, X, y=None):
        """Transform the dataframe.
        Args:
            X (pd.DataFrame): dataframe to transform
            y (pd.Series): target variable (not used)"""
        X_transformed = X.copy()
        # transform all columns
        for col in self.columns:
            param1 = self.params1[col]
            param2 = self.params2[col]
            data = X_transformed[X_transformed[self.cat_col] == True][col]
            
            # self._error_checking(data,param1,col)
            X_transformed.loc[X_transformed[self.cat_col] == True, col] = transform_nodim(param1=param1, param2=param2, values=data)

        return X_transformed

    def _error_checking(self, data, param, col):
        """Check if column values are in the range of mu +- 5* std."""
        n_std = 5
        min_allowed = param["mu"] - n_std * param["std"]
        max_allowed = param["mu"] + n_std * param["std"]
        if (data.min() < min_allowed) or (data.max() > max_allowed):
            raise ValueError(
                f"Column {col} contains values outside of the range of mu +- {n_std} * std."
            )

class SelectCols(BaseEstimator, TransformerMixin):
    """ Select columns transformer."""
    
    def __init__(self, keep=None, drop=None):
        """Initialize the transformer.
        Args:
            columns (list): list of columns to select"""
        self.keep = keep
        self.drop = drop
        self.feature_names_in_ = None
        
    def fit(self, X, y=None):
        """Fit the transformer.
        Args:
            X (pd.DataFrame): dataframe to subsample
            y (pd.Series): target variable (not used)"""
        return self

    def transform(self, X, y=None):
        """Transform the dataframe.
        Args:
            X (pd.DataFrame): dataframe to transform
            y (pd.Series): target variable (not used)"""
        X_transformed = X.copy()
        # transform all columns
        if self.keep:
            X_transformed = X_transformed[self.keep]
        if self.drop:
            X_transformed = X_transformed.drop(columns=self.drop)
        
        # set feature names
        self.feature_names_in_ = X_transformed.columns

        return X_transformed

    def get_feature_names(self):
        """Get feature names."""
        return self.feature_names_in_
        
class OneHotPD(BaseEstimator, TransformerMixin):
    """One-hot encoding transformer."""

    def __init__(self, columns):
        """Initialize the transformer.
        Args:
            columns (list): list of columns to one-hot encode
            drop_first (bool): if True, drop first column, default True"""
        self.columns = columns

    def fit(self, X, y=None):
        """Fit the transformer.
        Args:
            X (pd.DataFrame): dataframe to subsample
            y (pd.Series): target variable (not used)"""
        return self

    def transform(self, X, y=None):
        """Transform the dataframe.
        Args:
            X (pd.DataFrame): dataframe to transform
            y (pd.Series): target variable (not used)"""
        X_transformed = X.copy()
        if self.columns:
            X_transformed = pd.get_dummies(X_transformed, columns=self.columns)
        return X_transformed


def get_column_transformer(pattern:str) -> ColumnTransformer:
    """Create a ColumnTransformer that selects columns based on regex pattern.
    Args:
        pattern (str): regex pattern
    Returns:
        ColumnTransformer
    """
    cs = make_column_selector(pattern=pattern)
    return ColumnTransformer([(pattern, 'passthrough', cs)], remainder='drop', verbose_feature_names_out=False).set_output(transform='pandas')


class NormEITV(BaseEstimator, TransformerMixin):
    """ Normalize the MRI data by ehte estimated Total Intracranial Volume (eITV)"""
    
    def __init__(self, pattern='mri', icv_col='eITV'):
        """Initialize the transformer.
        Args:
            patttern (str): pattern of columns to normalize, default 'mri'
            icv_col (str): name of column with ICV values, default 'icv'"""
        self.pattern = pattern
        self.icv_col = icv_col

    def fit(self, X, y=None):
        """Fit the transformer.
        Args:
            X (pd.DataFrame): dataframe to subsample
            y (pd.Series): target variable (not used)"""
        return self

    def transform(self, X, y=None):
        """Transform the dataframe.
        Args:
            X (pd.DataFrame): dataframe to transform
            y (pd.Series): target variable (not used)"""
        X_transformed = X.copy()

        # get columns starting with pattern
        columns = [col for col in X_transformed.columns if col.startswith(self.pattern)]

        for col in columns:
            X_transformed[col] = X_transformed[col] / X_transformed[self.icv_col]
        return X_transformed