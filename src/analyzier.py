from src.workflow import WorkflowResults
from src.statistics import CorrelatedTTest
from src.experiment import ExperimentResults

import pandas as pd
from sklearn.metrics import mean_absolute_error, r2_score

class Analyzer():
    """ """
    def __init__(self, results: ExperimentResults) -> None:
        self.experiment_name = results.name
        self.result_dir = results.result_dir
        self.data = results.data
        self.predictions = results.predictions
        self.workflow_names = results.workflow_names


class StatsAnalyzer(Analyzer):
    """ """
    def __init__(self, results: ExperimentResults) -> None:
        super().__init__(results)

    def analyze(self, reference: str):
        self._compute_pad()
        self._compute_scores()
        self._average_scores()
        self._stat_test(reference)
        print(self.result_table)

    def _compute_pad(self):
        # compute pad 
        for pipe in self.workflow_names:
            self.predictions[f'pad_{pipe}'] = self.predictions[pipe] - self.predictions.true

    def _compute_scores(self):
        # init dataframe for scores per fold
        folds = self.predictions.fold.unique()
        scores = pd.DataFrame(index=folds)

        # compute scores for each fold
        for fold in folds:
            # select data for fold
            df_fold = self.predictions[self.predictions.fold == fold]
            # compute scores (mean absolute error, r2, corr and corr_pad)
            for pipe in self.workflow_names:
                # compute MAE
                scores.loc[fold, f'{pipe}_mae'] = mean_absolute_error(df_fold.true, df_fold[pipe])
                # compute R2
                scores.loc[fold, f'{pipe}_r2'] = r2_score(df_fold.true, df_fold[pipe])
                # compute correlation with true
                scores.loc[fold, f'{pipe}_corr'] = df_fold[pipe].corr(df_fold.true)
                # compute correlation with pad and true
                scores.loc[fold, f'{pipe}_corr_pad'] = df_fold[f'pad_{pipe}'].corr(df_fold.true)
            # cound elements
            scores.loc[fold, f'count'] = len(df_fold)

        self.scores = scores

    def _average_scores(self):
        # average scores over folds
                # average scores over folds
        result_table = pd.DataFrame(index=self.workflow_names)

        score_names = ['mae', 'r2', 'corr', 'corr_pad']
        for score in score_names:
            temp_mean = self.scores[[f'{pipe}_{score}' for pipe in self.workflow_names]].mean()
            temp_std = self.scores[[f'{pipe}_{score}' for pipe in self.workflow_names]].std()
            temp_mean.rename(index=lambda s: s.removesuffix(f'_{score}'), inplace=True)
            temp_std.rename(index=lambda s: s.removesuffix(f'_{score}'), inplace=True)

            temp = temp_mean.copy()
            for pipe in self.workflow_names:
                temp.loc[pipe] = f"{temp_mean.loc[pipe].round(2)} ({temp_std.loc[pipe].round(2)})"

            result_table[score.upper()] = temp


        self.result_table = result_table

    def _stat_test(self, reference: str):
        nruns = int(len(self.predictions.subject_id) / self.predictions.subject_id.nunique()) 
        for pipe in self.workflow_names:
            if pipe == reference:
                continue
            a = self.scores[f'{reference}_mae'].to_numpy()
            b = self.scores[f'{pipe}_mae'].to_numpy()
            ttest = CorrelatedTTest(a, b, nruns)
            tstat, p, cil, ciu = ttest.ttest()
            pl, pr = ttest.probabilities()
            self.result_table.loc[pipe, 'tstat'] = round(tstat,2)
            self.result_table.loc[pipe, 'p'] = round(p,2)
            self.result_table.loc[pipe, 'ci'] = f"({cil:.2f}, {ciu:.2f})"
            self.result_table.loc[pipe, 'plr'] = f"({pl:.2f}, {pr:.2f})"

    def save(self):
        # split first column
        self.result_table['Pipeline'] = self.result_table.index
        self.result_table['Pipeline'] = self.result_table['Pipeline'].str.split('_').str[0]
        self.result_table['Pipeline'] = self.result_table['Pipeline'].replace({'pipeline-I':'I', 'pipeline-IIa':'IIa', 'pipeline-IIb':'IIb', 'pipeline-IIc':'IIc'})

        # add modality I = Reference, IIa = PET, IIb = MRI, IIc = PET+MRI based on pipeline
        self.result_table['Modality'] = self.result_table['Pipeline']
        self.result_table['Modality'] = self.result_table['Modality'].replace({'I':'Reference', 'IIa':'5-HT2AR', 'IIb':'GM', 'IIc':'5-HT2AR + GM'})
        
        # add model 
        self.result_table['Model'] = self.result_table.index
        self.result_table['Model'] = self.result_table['Model'].str.split('_').str[1:]
        self.result_table['Model'] = self.result_table['Model'].str.join('')
        # replace 'ens' with '' if it is available
        self.result_table['Model'] = self.result_table['Model'].str.replace('ens','')

        # change order of columns
        self.result_table = self.result_table[['Pipeline', 'Modality', 'Model', 'MAE', 'R2', 'CORR', 'CORR_PAD', 'tstat', 'p', 'ci', 'plr']]

        self.result_table.to_excel(self.result_dir / f'result_{self.experiment_name}.xlsx',index=False)