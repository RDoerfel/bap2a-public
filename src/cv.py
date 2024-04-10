from sklearn.model_selection import KFold, RepeatedStratifiedKFold, GridSearchCV


class CVSpec():
    """
    A class that stores the specifications for the CV process.

    Attributes:
    -----------
    n_splits : int, optional
        The number of folds to generate. Default is 5.
    n_repeats : int, optional
        The number of times the CV process should be repeated. Default is 1.
    random_state : int or None, optional
        The seed for the random number generator. Default is None.
    shuffle : bool, optional
        Whether to shuffle the data before splitting it. Default is True.

    Methods:
    --------
    None

    """
    def __init__(self, n_splits: int = 5, n_repeats: int =1, random_state: int = 42, shuffle: bool = True):
        self.n_splits = n_splits
        self.n_repeats = n_repeats
        self.random_state = random_state
        self.shuffle = shuffle

    def __str__(self) -> str:
        return f"\n\tNumber of splits: {self.n_splits}\n\tNumber of repeats: {self.n_repeats}\n\tRandom state: {self.random_state}\n\tShuffle: {self.shuffle}\n"
    
class CVGenerator:
    """
    A class that generates inner and outer CV objects.

    Attributes:
    -----------
    n_splits : int, optional
        The number of folds to generate. Default is 5.
    n_repeats : int, optional
        The number of times the CV process should be repeated. Default is 1.
    random_state : int or None, optional
        The seed for the random number generator. Default is None.
    shuffle : bool, optional
        Whether to shuffle the data before splitting it. Default is True.

    Methods:
    --------
    generate_inner(X, y):
        Generates an inner CV object.

    generate_outer(X, y):
        Generates an outer CV object.

    """
    def __init__(self, cv_spec: CVSpec):
        self.n_splits = cv_spec.n_splits
        self.n_repeats = cv_spec.n_repeats
        self.random_state = cv_spec.random_state
        self.shuffle = cv_spec.shuffle
        
    def generate_inner(self):
        """
        Generates an inner CV object.

        Returns:
        --------
        inner_cv : scikit-learn CV object
            The inner CV object.
        """
        return KFold(n_splits=self.n_splits, shuffle=self.shuffle, random_state=self.random_state)

    def generate_outer(self):
        """
        Generates an outer CV object.

        Returns:
        --------
        outer_cv : scikit-learn CV object
            The outer CV object.
        """
        return RepeatedStratifiedKFold(n_splits=self.n_splits, n_repeats=self.n_repeats, random_state=self.random_state)

    def generate_grid_search(self, pipeline, param_grid, n_jobs=10):
        """
        Generates a grid search object.

        Parameters:
        -----------
        pipeline : scikit-learn pipeline object
            The pipeline to be used in the grid search.
        param_grid : dict
            The parameter grid to be used in the grid search.
        n_jobs : int, optional

        Returns:
        --------
        grid_search : scikit-learn GridSearchCV object
            The grid search object.
        """
        return GridSearchCV(pipeline, param_grid, cv=self.generate_inner(), scoring="neg_mean_absolute_error", n_jobs=n_jobs)