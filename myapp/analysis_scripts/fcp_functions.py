import numpy as np
from scipy.stats import norm


def get_repetition_vector_estimation(
        r,
        n_variables,
        n_reps_per_average
):

    power_vec = np.zeros(n_variables)
    for _ in range(n_reps_per_average):
        
        b = draw_correlated_binomial(r, n_variables)
        power_vec += b

    power_vec = power_vec / n_reps_per_average
    return power_vec


def draw_correlated_binomial(r, n_variables):

    # Create a MVN normal with a covariance term and an inpendent term
    # Zero centered and unit variance
    shared = np.sqrt(r) * np.random.randn()
    x = shared + np.sqrt(1 - r) * np.random.randn(n_variables)

    # Create a bernoulli variable from the MVN normal
    # If positive 1 if negative 0 (therefore mean 50%)
    b = (x > 0).astype(int)

    return b


def extract_top_quantile(power_vec, quantile_percentage):

    n = len(power_vec)
    # Top X% -> k variables
    k = max(1, round(n * quantile_percentage))
    # Indices of the k highest-power vars
    idx = np.argsort(power_vec)[-k:]
    return power_vec[idx], idx


def CI_calculation(power_vec, alpha, n_reps_per_average):
    # CLT approximation for CI computation
    n = n_reps_per_average
    z = norm.ppf(alpha)
    se = np.sqrt(power_vec * (1 - power_vec) / n)

    # Get the lower bound
    return power_vec - z * se
