import math


def fcp_beta(p_c, p_f):
    k_p = math.sqrt((1 - p_f) / p_f)
    # maximal beta solving p_c = beta - k_p*sqrt(beta*(1-beta))
    beta = (
        (2*p_c + k_p**2 + k_p*math.sqrt(k_p**2 + 4*p_c*(1 - p_c)))
        / (2*(1 + k_p**2))
    )
    return beta


if __name__ == '__main__':

    print(fcp_beta(0.95, 0.5))
    print(fcp_beta(0.90, 0.5))
    print(fcp_beta(0.85, 0.5))
    print(fcp_beta(0.80, 0.5))
    print(fcp_beta(0.75, 0.5))
