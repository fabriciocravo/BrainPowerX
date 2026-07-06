import math


def fcp_beta(p_c, p_f):
    k_p = math.sqrt((1 - p_f) / p_f)
    # maximal beta solving p_c = beta - k_p*sqrt(beta*(1-beta))
    beta = (
        (2*p_c + k_p**2 + k_p*math.sqrt(k_p**2 + 4*p_c*(1 - p_c)))
        / (2*(1 + k_p**2))
    )
    return beta
