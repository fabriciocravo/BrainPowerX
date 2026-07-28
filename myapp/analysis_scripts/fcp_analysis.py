import json
import numpy as np
from .fcp_solution import fcp_beta
from .fcp_functions import (
    get_repetition_vector_estimation,
    extract_top_quantile,
    CI_calculation,
)

# β = 0.99987, so α ≈ 0.00013 (about 1.3×10⁻⁴).

# Parameters to calculate coverage for
p_group_list = [(0.95, 0.05)]
multi_corrected = True
r_list = [0.1, 0.2, 0.4, 0.8, 0.9]
quantile_percentages = [0.1, 0.2, 0.3, 0.4, 0.5]


# Tunable parameters
n_reps_per_subsample = 100   # reps behind each per-variable power estimate
n_reps_per_average = 500     # reps used to estimate the probability
n_variables = 1000

results = {}

for p_c, p_f in p_group_list:

    # One correction level per (p_c, p_f)
    # If not corrected, just take the p_c prob
    if multi_corrected:
        alpha = fcp_beta(p_c, p_f)
    else:
        alpha = p_c[0]

    for r in r_list:

        # Count reps where the lower-CI slice average lands below the true 0.5
        q_count = {q: 0 for q in quantile_percentages}
        q_estimated_avg = {q: 0 for q in quantile_percentages}

        for _ in range(n_reps_per_average):

            # Estimate per-variable power through subsampling repetition
            power_vec = get_repetition_vector_estimation(
                r, n_variables, n_reps_per_subsample
            )

            for q in quantile_percentages:

                # Take the top-X% variables by estimated power
                quantile_power, _ = extract_top_quantile(power_vec, q)

                # Lower confidence bound per variable at the corrected level
                lower_ci = CI_calculation(
                    quantile_power, alpha, n_reps_per_subsample
                )

                # Slice average vs. the known true average (0.5)
                q_average = np.mean(lower_ci)
                q_estimated_avg[q] += q_average
                q_count[q] += (q_average < 0.5)

        # Convert counts to probabilities and key by (p_c, p_f, r)
        key = f"pc={p_c}_pf={p_f}_r={r}"
        results[key] = {}
        for q in quantile_percentages:
            qk = f"q{int(round(q * 100))}"

            results[key][qk] = q_count[q] / n_reps_per_average
            results[key][f"{qk}_average"] = (
                q_estimated_avg[q] / n_reps_per_average
            )

# Save dictionary as json
with open("fcp_simulation_results.json", "w") as f:
    json.dump(results, f, indent=2)

print(json.dumps(results, indent=2))
