import numpy as np
from scipy import stats


def edges_to_pvalues(e_mat, N):

    t_stat = np.sqrt(N) * e_mat
    p_mat = stats.t.sf(t_stat, df=N-1)
    return p_mat


def significance_map(p_mat, alpha=0.05):

    # Always uper triangular in this experiment
    n_nodes = p_mat.shape[0]
    n_variables = n_nodes*(n_nodes - 1)//2

    # fwer_alpha
    fwer_alpha = alpha/n_variables

    r_mat = p_mat < fwer_alpha
    return r_mat


def calculate_power_fwer(
        e_mat,
        n_varibles,
        N,
        alpha=0.05
):

    t_crit = stats.t.ppf(1 - alpha/n_varibles, N-1)
    pow_mat = stats.nct.sf(t_crit, N-1, np.sqrt(N)*e_mat)

    return pow_mat


def upper(mat):
    iu, ju = np.triu_indices(mat.shape[0], k=1)
    return mat[iu, ju]


def stack_draws(draw_function, K, sample_size):
    """Stack K independent experiments at a given sample size."""

    def draw():
        return draw_function(sample_size)

    stack_heatmap = [draw() for i in range(K)]
    stack_heatmap = np.stack(stack_heatmap)

    n_variables = upper(stack_heatmap[0]).size

    return stack_heatmap, n_variables


# Random number global
_rng = np.random.default_rng()
