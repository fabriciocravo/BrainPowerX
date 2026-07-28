import numpy as np
from scipy import stats


def edges_to_pvalues(e_mat, N):

    t_stat = np.sqrt(N) * e_mat
    p_mat = 2 * stats.t.sf(np.abs(t_stat), df=N-1)
    return p_mat


def significance_map(p_mat, n_variables, alpha=0.05):

    if n_variables != p_mat.size:
        raise ValueError('Number of variables does not match p-vector')

    # fwer_alpha
    fwer_alpha = alpha/n_variables

    r_mat = p_mat < fwer_alpha
    return r_mat


def calculate_power_fwer(
        e_mat,
        n_variables,
        N,
        alpha=0.05
):

    # Two-sided critical value: alpha/n_variables split across both tails
    t_crit = stats.t.ppf(1 - alpha/(2*n_variables), N-1)
    nc = np.sqrt(N) * e_mat

    # Two-sided power: significant in either tail of the noncentral t
    pow_mat = stats.nct.sf(t_crit, N-1, nc) + stats.nct.cdf(-t_crit, N-1, nc)

    return pow_mat


# Random number global
_rng = np.random.default_rng()
