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

# Images for different values of tau A - replace when needed
# From Steph's effect size paper
TAU_A = 0.00088  # Brain wide associations
# TAU_A = 0.017  # Task based connectivity
# TAU_A = 0.025  # Task based activation

N_NODES = 268
N_VARIABLES = N_NODES * (N_NODES - 1) // 2
TAU_S = 1.0
TAU_MU = 0
QP = 0.1
REP_NUMBER = 100
REP_SUBSAMPLING = 100
SAMPLE_SIZES = [40, 80, 120]
DATASET_SIZES = [110, 200, 400, 1000, 2000]


def run_one_repetition(
    DATASET_SIZES,
    N_VARIABLES,
    SAMPLE_SIZES,
    TAU_A,
    TAU_S,
    TAU_MU,
    QP,
    n_rep_subsampling=100,
    seed=None
):
    print(seed/REP_NUMBER)

    rng_np = np.random.default_rng(seed)

    # Sort - don't care about array change
    DATASET_SIZES = sorted(DATASET_SIZES)
    SAMPLE_SIZES = sorted(SAMPLE_SIZES)

    # Draw true effects
    TE = draw_true_effects(
        n_variables=N_VARIABLES,
        tau_A=TAU_A,
        tau_S=TAU_S,
        rng_np=rng_np
    )

    # Compute true power for all sample sizes
    tp_list = np.asarray([
        estimate_true_power(TE, N_VARIABLES, n, return_full_matrix=True)
        for n in SAMPLE_SIZES
    ])

    n_ds = len(DATASET_SIZES)
    n_ss = len(SAMPLE_SIZES)

    p_diff = np.zeros((n_ss, n_ds))
    max_p_diff = np.zeros((n_ss, n_ds))

    # Create dataset
    total_dataset = np.asarray([draw_subject_array(
            TE=TE,
            n_subs=DATASET_SIZES[-1],
            tau_mu=TAU_MU,
            rng_np=rng_np
        )])
    
    for i_ss, n_sample in enumerate(SAMPLE_SIZES):
        tp = tp_list[i_ss]
        qt_index = int(QP*tp.size)
        tp_qt_power = sorted(tp)[-qt_index:]

        for i_ds, n_dataset in enumerate(DATASET_SIZES):
            
            # exp_number is 1 because the dataset is treat as one big exp
            power = p_est_subsampling_repetition(
                stacked_subject_array=total_dataset[:, :n_dataset],
                n_variables=N_VARIABLES,
                sample_size=n_sample,
                exp_number=1,
                return_full_matrix=True,
                n_rep=n_rep_subsampling,
                rng_np=rng_np
            )

            p_diff[i_ss, i_ds] = np.mean(power) - np.mean(tp)
            qt_power = sorted(power)[-qt_index:]
            max_p_diff[i_ss, i_ds] = np.mean(qt_power) - np.mean(tp_qt_power)

    return tp_list, p_diff, max_p_diff


# --- Run calculation ---
results = Parallel(n_jobs=5)(
    delayed(run_one_repetition)(
        DATASET_SIZES=DATASET_SIZES,
        N_VARIABLES=N_VARIABLES,
        SAMPLE_SIZES=SAMPLE_SIZES,
        TAU_A=TAU_A,
        TAU_S=TAU_S,
        TAU_MU=TAU_MU,
        QP=QP,
        n_rep_subsampling=REP_SUBSAMPLING,
        seed=i_r
    )
    for i_r in range(REP_NUMBER)
)

# (REP_NUMBER, n_ss, n_ds)
power_diff = np.array([r[1] for r in results])
qt_power_diff = np.array([r[2] for r in results])

# average over repetitions, abs after
mean_over_reps = np.abs(power_diff.mean(axis=0))   # (n_ss, n_ds)
qt_over_reps = np.abs(qt_power_diff.mean(axis=0))        # (n_ss, n_ds)

# --- plot ---
fig, (ax_mean, ax_max) = plt.subplots(1, 2, figsize=(10, 4), sharex=True)

for i_ss, n_sample in enumerate(sorted(SAMPLE_SIZES)):
    ax_mean.plot(sorted(DATASET_SIZES), mean_over_reps[i_ss],
                 marker='o', label=f'Sample Size = {n_sample}')
    ax_max.plot(sorted(DATASET_SIZES), qt_over_reps[i_ss],
                marker='o', label=f'Sample Size = {n_sample}')

ax_mean.axhline(0, color='gray', linestyle='--', linewidth=1)
ax_mean.set_ylim(bottom=0)
ax_mean.set_xlabel('Dataset size (number of subjects)')
ax_mean.set_ylabel('|Estimated power - true power|')
ax_mean.set_title('Mean per-edge error')
ax_mean.legend()

ax_max.axhline(0, color='gray', linestyle='--', linewidth=1)
ax_max.set_ylim(bottom=0)
ax_max.set_xlabel('Dataset size (number of subjects)')
ax_max.set_title(f'Top {int(QP*100)}% slice error')
ax_max.legend()

fig.suptitle(
    f'Error of subsampling-repetition power estimator '
    f'(τ_A = {TAU_A})'
)
fig.tight_layout()
plt.show()



