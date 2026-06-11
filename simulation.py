import math
import random


def poisson(lam):

    L = math.exp(-lam)
    k = 0
    p = 1

    while p > L:
        k += 1
        p *= random.random()

    return k - 1


def simulate(home_xg, away_xg):

    h = poisson(home_xg)
    a = poisson(away_xg)

    return h, a