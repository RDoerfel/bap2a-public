#%%
from scipy import stats
import numpy as np
import matplotlib.pyplot as plt

class CorrelatedTTest:
    def __init__(self, a, b, nruns):
        self.mu, self.var, self.df = self._compute_statistics(a,b,nruns)

    def _compute_statistics(self,a,b,nruns):
        """Compute statistics for correlated t-test as described in [1]
        Args:
            a (np.array): array with scores from model a
            b (np.array): array with scores from model b
            nruns (int): number of repetions of the cross-validation
        Returns:
            mu (float): mean of the difference
            var (float): corrected standard deviation of the difference
            df (int): degrees of freedom

        References:
            [1] Nadeau, C., & Bengio, Y. (2003). Inference for the generalization error. Journal of Machine Learning Research, 3(Jan), 393-430.
        """

        # compute difference between a and b
        r = a - b
        r_hat = np.mean(r)

        # total number of folds
        J = len(r)
        df = J - 1
        # number of folds per run
        k = J // nruns

        # correlation heuristic after Nadeau and Bengio (2003)
        rho = 1/k

        # compute the variance of the difference
        var_hat = np.var(r, ddof=1)

        # apply correlation correction
        var_tilde = (1/J + rho / (1-rho)) * var_hat

        return r_hat, var_tilde, df

    def ttest(self,alpha=0.05):
        """Compute t-statistic and p-value for the correlated t-test
        Args:
            alpha (float): significance level default=0.05
        Returns:
            tstat (float): t-statistic
            pvalue (float): p-value
            zl (float): lower bound of the confidence interval
            zu (float): upper bound of the confidence interval
        """
        tstat = self.mu / np.sqrt(self.var)
        pvalue = 2 * stats.t.cdf(-np.abs(tstat), self.df)
        zl = stats.t.ppf(alpha/2, self.df,loc=self.mu, scale=np.sqrt(self.var))
        zu = stats.t.ppf(1-alpha/2, self.df,loc=self.mu, scale=np.sqrt(self.var))
        return tstat, pvalue, zl, zu

    def probabilities(self, rope=None):
        """Compute the probability that the difference between a and b is in the range of rope
        Args:
            rope (tuple): range of plausible effect
        Returns:
        if rope == 0:
            p_l (float): probability of mean absolute difference being negative
            p_u (float) = probability of mean absolute difference being positive
        else:
            p_l (float): probability of mean absolute difference being below rope
            p_u (float): probability of mean absolute difference being above rope
            p_rope (float): probability of mean absolute difference being in rope
        """
        if rope == None:
            prob = stats.t.cdf(0, self.df,loc=self.mu, scale=np.sqrt(self.var))
            return prob, 1-prob
        else:
            p_l = stats.t.cdf(-rope, self.df,loc=self.mu, scale=np.sqrt(self.var))
            p_u = 1 - stats.t.cdf(rope, self.df,loc=self.mu, scale=np.sqrt(self.var))
            p_rope = 1 - p_u - p_l
            return p_l, p_rope, p_u

    def plot(self, rope=None, ci=None):
        """Plot the probability density function of the difference between a and b
        Args:
            rope (float): range of plausible effect
            ci (tuple): confidence interval
        Returns:
            fig (matplotlib.figure.Figure): figure with the plot
        """
        fig, ax = plt.subplots()
        x = np.linspace(-2,2,100)
        ax.plot(x, stats.t.pdf(x, self.df,loc=self.mu, scale=np.sqrt(self.var)), label='PDF')
        if rope != None:
            ax.vlines(-rope,0,stats.t.pdf(-rope, self.df,loc=self.mu, scale=np.sqrt(self.var)), color='red', label='ROPE')
            ax.vlines(rope,0,stats.t.pdf(rope, self.df,loc=self.mu, scale=np.sqrt(self.var)), color='red', label='ROPE')
        if ci != None:
            tstat, p, zl, zu = self.ttest()
            ax.vlines(zl,0,stats.t.pdf(zl, self.df,loc=self.mu, scale=np.sqrt(self.var)), color='green', label='CI')
            ax.vlines(zu,0,stats.t.pdf(zu, self.df,loc=self.mu, scale=np.sqrt(self.var)), color='green', label='CI')
        ax.set_xlabel('Difference')
        ax.set_ylabel('Probability density')
        ax.legend()
        return fig





        






