import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.inspection import permutation_importance

from src.workflow import WorkflowResults, WorkflowRepresentation
from src.weights import get_feature_weights

class Trainer:
    """Class for training a model with nested CV."""
    def train(
        self, data: pd.DataFrame, strat_col:str, label_col:str, cv_inner, cv_outer, workflow: WorkflowRepresentation, n_jobs: int = 1
    ) -> WorkflowResults:
        """Train model using nested cross-validation.
        Args:
            data (pd.DataFrame): dataframe to train on
            strat_col (str): name of column to stratify on
            label_col (str): name of label column
            cv_inner (sklearn.model_selection._split): inner cross-validation
            cv_outer (sklearn.model_selection._split): outer cross-validation
            workflow (WorkflowRepresentation): the workflow to run
            n_jobs (int): number of jobs to run in parallel (default: 1)
        Returns:
            results (WorkflowResults): results of training
        """
        # initialize arrays to store results
        y_pred = np.array([])
        y_true = np.array([])
        y_pred_std = np.array([])
        y_index = np.array([])
        y_fold = np.array([])

        # store coefficients in array if available
        coef = []

        # store best params in array
        best_params = np.array([])

        # index for outer CV !! make it pet_id
        index = np.arange(data.shape[0])

        # k-fold iterator for outer CV
        k = 1

        # store scores per fold
        scores = []

        # loop over outer folds
        for train_idx, test_idx in cv_outer.split(data, data[strat_col]):
            # get train and test data and index
            X_train, X_test = data.iloc[train_idx], data.iloc[test_idx]
            y_train, y_test = (
                data[label_col].iloc[train_idx],
                data[label_col].iloc[test_idx],
            )

            y_index_train, y_index_test = X_train.index.values, X_test.index.values

            # initiate grid search (inner CV)
            grid = GridSearchCV(
                workflow.pipeline,
                workflow.paramgrid,
                cv=cv_inner,
                scoring="neg_mean_absolute_error",
                n_jobs=n_jobs
            )

            # fit grid search
            grid.fit(X_train, y_train)
            
            # get best model
            best_pipe = grid.best_estimator_

            # fit best model on outer fold
            best_pipe.fit(X_train, y_train)

            # predict on test data
            y_pred_fold = best_pipe.predict(X_test)

            # try to get standard deviation of predictions
            try:
                y_pred_std_fold = best_pipe.predict(X_test, return_std=True)[1]
            except:
                y_pred_std_fold = np.zeros(y_pred_fold.shape)

            # TODO generalize this. Should be able to set other estimators then pyment and also to run without
            # compute scores per fold
            scores_fold = self._compute_scores(y_test, y_pred_fold)
            scores.append(scores_fold)

            # append results to arrays
            y_pred = np.append(y_pred, y_pred_fold)
            y_true = np.append(y_true, y_test)
            y_pred_std = np.append(y_pred_std, y_pred_std_fold)
            y_index = np.append(y_index, y_index_test)
            y_fold = np.append(y_fold, np.repeat(k, len(y_index_test)))
            k += 1

            # get coefficients 
            coef.append(get_feature_weights(best_pipe['model']))

            # append best params
            best_params = np.append(best_params, grid.best_params_)

        # print split counts
        self._print_split_strata(data, X_train, X_test, strat_col)

        # store results
        self._results = pd.DataFrame(
            {
                "index": y_index,
                "fold": y_fold,
                "pred": y_pred,
                "std": y_pred_std,
                "true": y_true,
            }
        )

        # store scores per fold
        self._scores = pd.DataFrame(scores)

        self._overalscores = self._compute_scores(y_true, y_pred)

        # print scores
        print("Scores:")
        for score, val in self._overalscores.items():
            print(f"{score}: {val:.3f}")

        # concatenate list of coefficients
        self._coef = pd.concat(coef).reset_index(drop=True)

        # store best params in dataframe
        self._best_params = pd.DataFrame(best_params)

        # store results
        return WorkflowResults(workflow.name,self._scores, self._results, self._best_params, self._coef)

    def _compute_scores(self, true, pred):
        """Get scores for model.
        Returns:
            scores (dict): dictionary with scores
        """
        # get scores
        scores = {
            "r2": r2_score(true, pred),
            "mae": mean_absolute_error(true, pred),
        }
        return scores

    def _print_split_strata(self, total, train, test, strat_col="chron_age_group"):
        """Get split strata for train and test data.
        Args:
            total (pd.Series): total counts
            train (pd.Series): train counts
            test (pd.Series): test counts
            strat_col (str): name of column to stratify on (default: "chron_age_group")
        Returns:
            split_strata (pd.Series): split strata
        """
        count_total = total[strat_col].value_counts()
        count_train = train[strat_col].value_counts()
        count_test = test[strat_col].value_counts()

        df_splits = pd.DataFrame(
            [count_total, count_train, count_test],
            index=["total", "train", "test"],
        ).T
        print(df_splits)

