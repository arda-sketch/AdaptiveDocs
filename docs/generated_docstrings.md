# Generated Documentation

## services.math_service.square
```python
square(x)
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
```

## utils.helpers.mean
```python
mean(values)
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
```

## services.stats_service.variance
```python
variance(values)
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
```

## services.stats_service.rms
```python
rms(values)
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
```

## services.math_service.preprocess
```python
preprocess(values)
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
```

## main.analyze
```python
analyze(values)
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
```
