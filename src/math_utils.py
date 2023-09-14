import numpy as np
from scipy.stats import norm  # , poisson
import re


def distribution(dist, condition=0):
    np.random.seed(3)
    if bool(re.fullmatch(r"constant\(-?\d+(\.\d+)?\)", dist)):
        c = float(re.search(r"-?\d+\.?\d*", dist).group())
        if condition:
            if c >= condition:
                return round(c, 2)
            raise "Error"
        return round(c, 2)
    elif bool(re.fullmatch(r"disc-uniform\(-?\d+(\.\d+)?, *-?\d+(\.\d+)?\)", dist)):
        a, b = map(float, re.findall(r"-?\d+\.?\d*", dist))
        assert a < b
        if condition:
            if condition <= a:
                return round(np.random.randint(a, b+1), 2)
            elif condition <= b:
                return round(np.random.randint(condition, b+1), 2)
            raise "Error"
        return round(np.random.randint(a, b+1), 2)
    elif bool(re.fullmatch(r"cont-uniform\(-?\d+(\.\d+)?, *-?\d+(\.\d+)?\)", dist)):
        a, b = map(float, re.findall(r"-?\d+\.?\d*", dist))
        assert a < b
        if condition:
            if condition <= a:
                return round(np.random.random()*(b-a)+a, 2)
            elif condition <= b:
                return round(np.random.random()*(b-condition)+condition, 2)
            raise "Error"
        return round(np.random.random()*(b-a)+a, 2)
    elif bool(re.fullmatch(r"normal\(-?\d+(\.\d+)?, *-?\d+(\.\d+)?\)", dist)):
        m, s = map(float, re.findall(r"-?\d+\.?\d*", dist))
        assert s > 0
        if condition:
            c = norm.sf(condition-0.005, loc=m, scale=s)
            p = 1
            n = condition
            probabilities = []
            while p/c > 0:
                p = norm.cdf(n+0.005, loc=m, scale=s) - norm.cdf(n-0.005, loc=m, scale=s)
                probabilities.append(p/c)
                n = round(n+0.01, 2)
            return np.random.choice(np.arange(condition, n, 0.01), p=probabilities)
        return round(np.random.normal(m, s), 2)
    elif bool(re.fullmatch(r"poisson\(-?\d+(\.\d+)?\)", dist)):
        p = float(re.search(r"-?\d+\.?\d*", dist).group())
        assert p > 0
        return round(np.random.poisson(p), 2)
    elif bool(re.fullmatch(r"exponential\(-?\d+(\.\d+)?\)", dist)):
        lambd = float(re.search(r"-?\d+\.?\d*", dist).group())
        assert lambd > 0
        return round(np.random.exponential(lambd), 2)


def logistic(x: float, start: float, stop: float, half: float) -> float:
    return 1 if x <= start else 2/(1+np.e**(np.log(3)*(min(stop, x)-start)/(half-start)))


def update_function(old_stat: float, old_c: float, new_stat: float, new_c: float, denominator: float) -> float:
    return (old_stat*old_c+new_stat*new_c)/denominator


def is_boolean_function(occurring_probability: float) -> float:
    return bool(np.random.choice(2, p=[1-occurring_probability, occurring_probability]))
