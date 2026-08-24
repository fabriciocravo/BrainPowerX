import glob
import os

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde

from utils import get_param_from_mat, convert_t_stats


# Set parameter with gt directory
GTD = '/Users/f.cravogomes/Desktop/Pc_Res_Updated/Shinny_Calculator/gt_data/Task Voxel'


def load_sorted_effect_vectors(gt_dir):
    # Glob mat files in the directory
    mat_files = sorted(glob.glob(os.path.join(gt_dir, '*.mat')))

    study_names = []
    effect_vectors = []

    # For file in directory
    for mat_file in mat_files:

        # 'edge_level_stats' - get the t-stats
        t_stats = get_param_from_mat(mat_file, 'edge_level_stats')
        t_stats = np.asarray(t_stats)

        # 'meta_data' - get the meta_data
        meta_data = get_param_from_mat(mat_file, 'meta_data')

        # convert into effect sizes
        ef_sizes = convert_t_stats(t_stats, meta_data)

        # get absolute value
        ef_sizes = np.abs(ef_sizes)

        # sort vectors
        ef_sizes = np.sort(ef_sizes)

        # store effect vector into numpy array
        study_names.append(os.path.basename(mat_file))
        effect_vectors.append(ef_sizes)

    min_vars = min(v.size for v in effect_vectors)
    effect_matrix = np.vstack([v[-min_vars:] for v in effect_vectors])
    return study_names, effect_matrix


def pairwise_mean_absolute_difference(effect_matrix):
    n_studies = effect_matrix.shape[0]

    pair_means = []

    # for effect_vector_1 in numpy array
    for i in range(n_studies):

        # for effect_vector_2 in numpy array
        for j in range(i + 1, n_studies):

            # subtract effect_vector_2 from effect_vector_1
            diff = effect_matrix[i] - effect_matrix[j]

            # take absolute value of subtraction
            diff = np.abs(diff)

            # store subtraction into numpy array
            # Calculate mean of subtraction between effects
            pair_means.append(diff.mean())

    return np.array(pair_means)


def plot_comparison(effect_matrix, pair_means, study_names, out_path=None):

    # Figure with 2 plots
    fig, (ax_left, ax_mid, ax_right) = plt.subplots(1, 3, figsize=(11, 4.5))

    # Plot KDE of half normal of all effect size distributions
    grid = np.linspace(0, effect_matrix.max(), 400)
    for name, ef_sizes in zip(study_names, effect_matrix):
        kde = gaussian_kde(ef_sizes)
        ax_left.plot(grid, kde(grid), lw=1.5, label=name)

    ax_left.set_xlabel('|Cohen\'s d|')
    ax_left.set_ylabel('Density')
    ax_left.set_title('Effect size distributions within category')

    # Plot KDE of distribution of mean subtraction between effects
    grid_diff = np.linspace(0, pair_means.max() * 1.1, 400)
    kde_diff = gaussian_kde(pair_means)
    ax_mid.plot(grid_diff, kde_diff(grid_diff), color='k', lw=1.5)
    ax_mid.fill_between(grid_diff, kde_diff(grid_diff), alpha=0.25, color='k')

    ax_mid.set_xlabel('Mean |quantile difference| between study pairs')
    ax_mid.set_ylabel('Density')
    ax_mid.set_title('Pairwise divergence between studies')

    fig.tight_layout()

    if out_path:
        fig.savefig(out_path, dpi=300)

    return fig


if __name__ == '__main__':
    study_names, effect_matrix = load_sorted_effect_vectors(GTD)
    pair_means = pairwise_mean_absolute_difference(effect_matrix)
    plot_comparison(effect_matrix, pair_means, study_names)
    plt.show()

    # Create empty average power matrix 

    # Size number of mats and 
    # np.arange(20, n_sub_range + 1, skip_range=20)
    # calculated power values
    # and + 1 for power difference

    # Given the effect size matrix

    # For each effect vector

        # Get number of variables

        # Empty vector to accumulate results

        # For each effect

            # Compute the power curve for each effect

            # Add to empty vector

        # Calculate average power curve

    # Loop over all pairs 

        # Calculate average difference between power

    # return power matrix 