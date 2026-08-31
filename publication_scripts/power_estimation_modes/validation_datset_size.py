import numpy as np
import matplotlib.pyplot as plt
from joblib import Parallel, delayed

from effect_model import (
    draw_true_effects,
    draw_subject_array
)

from study_planning_strats import (
    p_est_subsampling_repetition,
    estimate_true_power
)

N_NODES = 30
N_VARIABLES = N_NODES * (N_NODES - 1) // 2
TAU_A = 0.00088
TAU_S = 1.0
TAU_MU = 0
REP_NUMBER = 100
REP_SUBSAMPLING = 100
SAMPLE_SIZES = [20, 40, 80]
DATASET_SIZES = [100, 200, 400, 1000]


def run_one_repetition(
    i_d_ds_pairs,
    N_VARIABLES,
    SAMPLE_SIZE,
    TAU_A,
    TAU_S,
    TAU_MU,
    n_rep_subsampling=100,
    seed=None
):
    rng_np = np.random.default_rng(seed)

    # Draw true effects
    TE = draw_true_effects(
        n_variables=N_VARIABLES,
        tau_A=TAU_A,
        tau_S=TAU_S,
        rng_np=rng_np
    )

    # Deterministic given TE and n_sample -> compute once
    tp = estimate_true_power(
        TE,
        N_VARIABLES,
        SAMPLE_SIZE,
        return_full_matrix=True
    )

    n_ds = len(i_d_ds_pairs)
    p_diff = np.zeros(n_ds)
    max_p_diff = np.zeros(n_ds)

    for i_d, ds in i_d_ds_pairs:
        n_subs = int(ds * SAMPLE_SIZE)

        dataset = np.asarray([draw_subject_array(
            TE=TE,
            n_subs=n_subs,
            tau_mu=TAU_MU,
            rng_np=rng_np
        )])

        power = p_est_subsampling_repetition(
            dataset,
            N_VARIABLES,
            SAMPLE_SIZE,
            exp_number=1,
            return_full_matrix=True,
            n_rep=n_rep_subsampling,
            rng_np=rng_np
        )

        p_diff[i_d] = np.abs(np.mean(power) - np.mean(tp))
        max_p_diff[i_d] = np.abs((power - tp).max())

    return tp, p_diff, max_p_diff


fig, (ax_mean, ax_max) = plt.subplots(1, 2, figsize=(10, 4), sharex=True)

for n_sample in SAMPLE_SIZES:
    
    i_d_ds_pairs = list(enumerate(DATASET_SIZES))

    results = Parallel(n_jobs=5)(
        delayed(run_one_repetition)(
            i_d_ds_pairs,
            N_VARIABLES,
            n_sample,
            TAU_A,
            TAU_S,
            TAU_MU,
            n_rep_subsampling=REP_SUBSAMPLING,
            seed=i_r
        )
        for i_r in range(REP_NUMBER)
    )

    # Unpack results back into the original arrays
    # (REP_NUMBER, N_VARIABLES)
    true_power = np.array([r[0] for r in results])
    # (REP_NUMBER, len(DATASET_SIZES))
    power_diff = np.array([r[1] for r in results])
    # (REP_NUMBER, len(DATASET_SIZES))
    max_power_diff = np.array([r[2] for r in results])

    mean_over_reps = power_diff.mean(axis=0)
    max_over_reps = max_power_diff.mean(axis=0)

    ax_mean.plot(DATASET_SIZES, mean_over_reps, marker='o',
                 label=f'N = {n_sample}')
    ax_max.plot(DATASET_SIZES, max_over_reps, marker='o',
                label=f'N = {n_sample}')

ax_mean.axhline(0, color='gray', linestyle='--', linewidth=1)
ax_mean.set_xlabel('Dataset size (number of subjects)')
ax_mean.set_ylabel('|Estimated power − true power|')
ax_mean.set_title('Mean per-edge error')
ax_mean.legend()

ax_max.axhline(0, color='gray', linestyle='--', linewidth=1)
ax_max.set_xlabel('Dataset size (number of subjects)')
ax_max.set_title('Max per-edge error')
ax_max.legend()

fig.suptitle('Error of subsampling-repetition power estimator')
fig.tight_layout()
plt.show()



