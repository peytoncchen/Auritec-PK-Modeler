import numpy as np

def one_compartment_model(t, A, alpha):
    return A * np.exp(-alpha * t)


def two_compartment_model(t, A, alpha, B, beta):
    return A * np.exp(-alpha * t) + B * np.exp(-beta * t)
