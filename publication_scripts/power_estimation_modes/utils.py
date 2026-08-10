import numpy as np
from scipy import stats


def edges_to_pvalues(exp, N):
    assert exp.shape[0] == N, (
        f"Expected {N} subjects, got {exp.shape[0]}"
    )

    mean = exp.mean(axis=0)
    sd = exp.std(axis=0, ddof=1)
    # Although normalized sd still needs to be estimated
    t_stat = np.sqrt(N) * mean / sd

    # Sf - survival function P(T > t_stat)
    # Probability that null generates higher stat
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

    # Primary tail (Survival function)
    pow_upper = np.nan_to_num(stats.nct.sf(t_crit, N - 1, nc), nan=0.0)

    # Opposite tail (CDF) - fill numerical precision NaNs with 0.0
    pow_lower = np.nan_to_num(stats.nct.cdf(-t_crit, N - 1, nc), nan=0.0)

    return pow_upper + pow_lower


# Random number global
_rng = np.random.default_rng()
