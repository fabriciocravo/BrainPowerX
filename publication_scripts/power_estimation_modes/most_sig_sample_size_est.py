import numpy as np
from group_planning_strats import (
    group_p_est_strongest_effect
)
from effect_model import (
    draw_true_effects,
    draw_experiment_array
)
from joblib import(
    Parallel, delayed
)
import matplotlib.pyplot as plt


if __name__ == '__main__':

    N_NODES = 268
    N_VARIABLES = N_NODES * (N_NODES - 1) // 2
    TAU_A = 0.00088
    TAU_S = 1.0
    ESTIMATOR = group_p_est_strongest_effect

    N_REPS = 10000
    SAMPLE_SIZES = np.unique(
        np.logspace(np.log10(10), np.log10(10000), num=60, dtype=int)
    )

    def sample_size_curve_estimation(
        group_estimator,
        n_variables,
        tau_A,
        tau_S,
        tau_M,
        sample_sizes,
        seed=None,
    ):

        power_error = np.zeros((len(sample_sizes)))

        if seed is not None:
            rng_np = np.random.default_rng(seed)
        else:
            rng_np = np.random.default_rng()

        # Draw true effects
        true_effects = draw_true_effects(
            n_variables=n_variables,
            tau_A=tau_A,
            tau_S=tau_S,
            rng_np=rng_np
        )

        for i_s, n_sample in enumerate(sample_sizes):

            true_power = group_estimator(
                group_effect_array=true_effects,
                n_variables=n_variables,
                sample_size=n_sample
            )

            # The study planned strats work with multiple studies
            # So we use one list - for one study
            subject_array = draw_experiment_array(
                TE=true_effects,
                n_subs=n_sample,
                tau_mu=tau_M,
                rng_np=rng_np
            )

            power_estimation = group_estimator(
                group_effect_array=subject_array,
                n_variables=n_variables,
                sample_size=n_sample,
            )

            power_error[i_s] = np.abs(true_power - power_estimation)

        return power_error

    subsample_lists = Parallel(
        n_jobs=5, backend='loky')(
        delayed(sample_size_curve_estimation)(
            group_estimator=ESTIMATOR,
            n_variables=N_VARIABLES,
            tau_A=TAU_A,
            tau_S=TAU_S,
            tau_M=0,
            sample_sizes=SAMPLE_SIZES,
            seed=i
        ) for i in range(N_REPS)
    )

    # Aggregate across repetitions: shape (N_REPS, len(SAMPLE_SIZES))
    # -> mean/std per sample size
    power_error_array = np.stack(subsample_lists, axis=0)
    mean_error = power_error_array.mean(axis=0)
    std_error = power_error_array.std(axis=0)

    n_reps_actual = power_error_array.shape[0]
    sem = std_error / np.sqrt(n_reps_actual)
    ci95 = 1.96 * sem

    plt.errorbar(
        SAMPLE_SIZES,
        mean_error,
        yerr=ci95,
        marker='o',
        capsize=3
    )
    plt.xscale('log')
    plt.xlabel('Sample size')
    plt.ylabel('Power error (|true power - estimated power|)')
    plt.title('Power error vs. sample size')
    plt.tight_layout()
    plt.show()
