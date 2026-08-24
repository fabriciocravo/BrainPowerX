
import os
import pickle

import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
from joblib import Parallel, delayed

# Variable with key name to use for this analysis
var_key = 'abcd_fc_gt-test14-r-Ground_Truth.mat'
# var_key = 'abcd_fc_gt-test1-t2-Ground_Truth.mat'
# var_key = 'hcp_activation-WM-t-Ground_Truth.mat'
# var_key = 'hpc_fc_gt-REST_GAMBLING-t-Ground_Truth.mat'
sub_list = [20, 80, 200]
n_outer_reps = 5
n_inner_reps = 100
alpha = 0.05
STRIP_WIDTH = 10  # For the width of the cmap
fig_w = 1.0

# ---------------------------------------------------------------
# On folder './distribution_fit_data/'
# kde_fit.pkl - dictionary
# keys - file names with gt effect size measurements
# items - dictionaries with:
# - kde (key: 'kde')
# - sample sizes ('n')
# - number of variables ('n_var')
# ---------------------------------------------------------------
data_dir = './distribution_fit_data/'
with open(os.path.join(data_dir, 'kde_fit.pkl'), 'rb') as f:
    kde_fit = pickle.load(f)

# Sample sizes to estimate power
n_range = np.asarray(sub_list)

# Get KDE and sample size
kde = kde_fit[var_key]['kde']
n_var = kde_fit[var_key]['n_var']

# Draw one true effect from the KDE for each variable
true_effects = kde.resample(n_var).flatten()

# True power matrix - (n_variables x n_sample_sizes)
true_power_matrix = np.zeros((n_var, len(n_range)))

# Subsampled power matrix - (n_variables x n_sample_sizes)
subsampled_power_matrix = np.zeros((n_var, len(n_range)))

# Difference matrix - (n_variables x n_sample_sizes)
diff_matrix = np.zeros((n_var, len(n_range)))


def compute_power_for_n(
        n_sub,
        true_effects,
        n_var,
        n_outer_reps,
        n_inner_reps,
        alpha
):

    # empty culmultative tp vec
    cum_tp_vec = np.zeros(n_var)

    # empty culmultative ss vec
    cum_ss_vec = np.zeros(n_var)

    # empty culmultative dif vec
    cum_dif_vec = np.zeros(n_var)

    # For 100 repetitions
    for _ in range(n_outer_reps):

        # Calculate power from true effect for each true effect - 2 sided
        df = n_sub - 1
        ncp = true_effects * np.sqrt(n_sub)
        t_crit = stats.t.ppf(1 - alpha / (2*n_var), df)

        # Break the integral due to numerical instability
        cdf_pos = stats.nct.cdf(t_crit, df, ncp)
        cdf_neg = stats.nct.cdf(-t_crit, df, ncp)

        # Solve numerical instabilities
        cdf_pos = np.where(np.isnan(cdf_pos), 1.0, cdf_pos)
        cdf_neg = np.where(np.isnan(cdf_neg), 0.0, cdf_neg)

        # Assign to the correct broken values
        true_power = 1 - cdf_pos + cdf_neg

        # Sort and add to culmutative true power vec
        sorted_true_power = np.sort(true_power)
        cum_tp_vec += sorted_true_power

        # Susampled Significance vector - only zeroes
        sig_vector = np.zeros(n_var)

        # For 100 repetitions
        for _ in range(n_inner_reps):

            # For each n - generate a random seed (each seed is a subject)
            # Draw n_sub seeds
            subject_seeds = np.random.randint(0, 2**31 - 1, size=n_sub)

            # Each subject measurement is variable + N(0, 1) - seed = subject
            subject_data = np.empty((n_sub, n_var))
            for s_idx, seed in enumerate(subject_seeds):
                rng = np.random.default_rng(seed)
                subject_data[s_idx, :] = true_effects + rng.normal(0, 1, n_var)

            # Calculate average subsampled (accross subjects) effect
            sample_mean = subject_data.mean(axis=0)
            sample_std = subject_data.std(axis=0, ddof=1)
            t_stat = sample_mean / (sample_std / np.sqrt(n_sub))

            # Find significant effects
            significant = np.abs(t_stat) > t_crit

            # Add to significance vector
            sig_vector += significant.astype(float)

        # Sort subsampled significance vector
        subsampled_power = sig_vector / n_inner_reps
        sorted_subsampled_power = np.sort(subsampled_power)

        # Add to culmultative ss vec
        cum_ss_vec += sorted_subsampled_power

        # Calc dif sorted tp and sorted ss vec
        dif_vec = np.abs(sorted_true_power - sorted_subsampled_power)

        # Add to culmultative dif vec
        cum_dif_vec += dif_vec

    # Calculate averages and store in respective matrices
    return (
        cum_tp_vec / n_outer_reps,
        cum_ss_vec / n_outer_reps,
        cum_dif_vec / n_outer_reps
    )


# For each sample sizes - dispatched in parallel, one worker per n_sub
results = Parallel(n_jobs=-1, backend='loky')(
    delayed(compute_power_for_n)(
        n_sub,
        true_effects,
        n_var,
        n_outer_reps,
        n_inner_reps,
        alpha
    )
    for n_sub in n_range
)

for j, (tp_col, ss_col, dif_col) in enumerate(results):
    true_power_matrix[:, j] = tp_col
    subsampled_power_matrix[:, j] = ss_col
    diff_matrix[:, j] = dif_col


fig, axes = plt.subplots(
    3,
    len(n_range),
    figsize=(fig_w * len(n_range), 8),
    squeeze=False
)

power_im = None
diff_im = None

for j, n_sub in enumerate(n_range):
    tp_strip = np.tile(true_power_matrix[:, j:j+1], (1, STRIP_WIDTH))
    ss_strip = np.tile(subsampled_power_matrix[:, j:j+1], (1, STRIP_WIDTH))
    dif_strip = np.tile(diff_matrix[:, j:j+1], (1, STRIP_WIDTH))

    power_im = axes[0, j].imshow(
        tp_strip,
        aspect='auto',
        origin='lower',
        cmap='viridis',
        vmin=0,
        vmax=1
    )
    axes[0, j].set_title(f'n={n_sub}')
    axes[0, j].set_xticks([])
    axes[0, j].set_yticks([])

    axes[1, j].imshow(
        ss_strip,
        aspect='auto',
        origin='lower',
        cmap='viridis',
        vmin=0,
        vmax=1
    )
    axes[1, j].set_xticks([])
    axes[1, j].set_yticks([])

    diff_im = axes[2, j].imshow(
        dif_strip,
        aspect='auto',
        cmap='coolwarm',
        vmin=-0.2,
        vmax=0.2
    )
    axes[2, j].set_xticks([])
    axes[2, j].set_yticks([])

axes[0, 0].set_ylabel('True power')
axes[1, 0].set_ylabel('Subsampled power')
axes[2, 0].set_ylabel('Difference (true - subsampled)')

fig.colorbar(power_im, ax=axes[0, :].tolist(), label='power', fraction=0.03, pad=0.02)
fig.colorbar(power_im, ax=axes[1, :].tolist(), label='power', fraction=0.03, pad=0.02)
fig.colorbar(diff_im, ax=axes[2, :].tolist(), label='true - subsampled', fraction=0.03, pad=0.02)

plt.savefig('power_comparison.png', dpi=200)
plt.show()
