import numpy as np

"""
All functions in this model need to be defined with params
The signature needs to be flexible to addapt to the pipeline
Names must match what can be packed in the original function
"""
# n_variables, tau_A=1.0, tau_S=1.0, rng_np=None


def normal_true_effects(n_variables, tau_A, tau_S, rng_np=None):
    # Essential params
    if rng_np is None:
        rng_np = np.random.default_rng()

    # Draws overall effects
    TE = rng_np.normal(
        loc=0,
        scale=np.sqrt(tau_A),
        size=n_variables
    )/np.sqrt(tau_S)  # Scaling to units of noise

    return TE
