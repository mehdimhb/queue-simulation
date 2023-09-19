import numpy as np
import scipy.stats as sc
import re
from . import PRECISION


def distribution(dist: str, precision: int, is_integer: bool = False) -> float:
    if bool(re.fullmatch(r"Constant\(\d+(\.\d+)?\)", dist)):
        return round(float(re.search(r"\d+\.?\d*", dist).group()), precision)
    elif bool(re.fullmatch(r"Discrete Uniform\(\d+(\.\d+)?, \d+(\.\d+)?\)", dist)):
        a, b = map(int, re.findall(r"\d+\.?\d*", dist))
        return round(np.random.randint(a, b+1), precision)
    elif bool(re.fullmatch(r"Continuous Uniform\(\d+(\.\d+)?, \d+(\.\d+)?\)", dist)):
        a, b = map(float, re.findall(r"\d+\.?\d*", dist))
        return round(np.random.random()*(b-a)+a, precision)
    elif bool(re.fullmatch(r"Normal\(-?\d+(\.\d+)?, \d+(\.\d+)?\)", dist)):
        m, s = map(float, re.findall(r"-?\d+\.?\d*", dist))
        n, h = (1, 0.5) if is_integer else (10**(-precision), 5*10**(-precision-1))
        Px = 1
        denominator = sc.norm.sf(n-h, loc=m, scale=s)
        probabilities = []
        while Px/denominator > 0:
            Px = sc.norm.cdf(n+h, loc=m, scale=s) - sc.norm.cdf(n-h, loc=m, scale=s)
            probabilities.append(Px/denominator)
            n = round(n+2*h, precision)
        return round(
            np.random.choice(np.arange(1 if is_integer else 10**(-precision), n, round(2*h, precision)), p=probabilities),
            precision
        )
    elif bool(re.fullmatch(r"Poisson\(\d+(\.\d+)?\)", dist)):
        p = float(re.search(r"\d+\.?\d*", dist).group())
        n = 1
        Px = 1
        denominator = sc.poisson.sf(0, p)
        probabilities = []
        while Px/denominator > 0:
            Px = sc.poisson.pmf(n, p)
            probabilities.append(Px/denominator)
            n += 1
        return round(np.random.choice(np.arange(1, n, 1), p=probabilities), precision)
    elif bool(re.fullmatch(r"Exponential\(\d+(\.\d+)?\)", dist)):
        return round(np.random.exponential(float(re.search(r"\d+\.?\d*", dist).group())), precision)


def make_str(distribution: str, param1: float, param2: float) -> str:
    return f"{distribution}({param1})" if param2 is None else f"{distribution}({param1}, {param2})"


def logistic(x: float, start: float, half: float, stop: float) -> float:
    return 1 if x <= start else 2/(1+np.e**(np.log(3)*(min(stop, x)-start)/(half-start)))


def update_function(old_stat: float, old_c: float, new_stat: float, new_c: float, denominator: float) -> float:
    return round((old_stat*old_c+new_stat*new_c)/denominator, PRECISION)


def boolean_function(occurring_probability: float) -> bool:
    return bool(np.random.choice(2, p=[1-occurring_probability, occurring_probability]))
