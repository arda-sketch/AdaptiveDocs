# From services.math_service
def square(x):
    """
Computes the square of a given number.

Parameters
----------
x : float or int
    The number to be squared.

Returns
-------
float or int
    The square of the input number.
"""
    return x * x

# From utils.helpers
def mean(values):
    """
Computes the arithmetic mean of a list of values.

Parameters
----------
values : list of numbers
    The list of numbers for which the mean is to be computed.

Returns
-------
float
    The arithmetic mean of the input values.
"""
    return sum(values) / len(values)

# From utils.helpers
def normalize(values):
    """
Normalize a list of numeric values to [0, 1].
"""
    min_v = min(values)
    max_v = max(values)
    return [(v - min_v) / (max_v - min_v) for v in values]

# From services.stats_service
def variance(values):
    """
Computes the variance of a list of values.

Parameters
----------
values : list of numbers
    The list of numbers for which the variance is to be computed.

Returns
-------
float
    The variance of the input values.
"""
    avg = mean(values)
    return sum((v - avg) ** 2 for v in values) / len(values)

# From services.stats_service
def rms(values):
    """
Computes the root mean square (RMS) of a list of values.

Parameters
----------
values : list of numbers
    The list of numbers for which the RMS is to be computed.

Returns
-------
float
    The root mean square of the input values.
"""
    return mean([square(v) for v in values]) ** 0.5

# From services.math_service
def preprocess(values):
    """
Normalize a list of numeric values to [0, 1].

Parameters
----------
values : list of float or int
    The list of numeric values to be normalized.

Returns
-------
list of float
    A new list containing the normalized values.
"""
    return normalize(values)

# From main
def analyze(values):
    """
Analyzes a list of values by computing both the variance and the root mean square (RMS).

Parameters
----------
values : list of numbers
    The list of numbers to be analyzed.

Returns
-------
dict
    A dictionary containing the variance and RMS of the input values.
"""
    v = variance(values)
    r = rms(values)
    return {
        "variance": v,
        "rms": r,
    }

