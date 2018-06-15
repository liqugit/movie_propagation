"""
File: stats.py
Author: Joao Moreira
Creation Date: Oct 31, 2016

Description:
Several useful statistical functions.
"""
from itertools import islice

import numpy as np
import pandas as pd
import scipy.optimize as optimize


def sem(data):
    """
    Calculates the standard error of the mean for the given dataset.
    """
    return np.std(data)/np.sqrt(len(data))


def piecewise_linear(x, x0, y0, k1, k2):
    """
    Equation for a piecewise linear model with 1 breakpoint.
    Params:
    (x0, y0) - location of the breakpoint
    k1 - slope of the first line
    k2 - slope of the second line
    """
    return np.piecewise(
        x,
        [x < x0, x >= x0],
        [lambda x: k1*x + y0-k1*x0, lambda x: k2*x + y0-k2*x0]
    )


def sigmoid(x, L, x0, k):
    """
    Equation for a logistic function, which as an "S" shape (sigmoid curve).
    Params:
    x0 - the x-value of the sigmoid's midpoint
    k - the steepness of the curve
    L - the curve's maximum value

    More: https://en.wikipedia.org/wiki/Logistic_function
    """
    y = L / (1 + np.exp(-k*(x-x0)))
    return y


def exponential(x, A, B, tau):
    """
    Equation for an exponential function.
    Params:
    A - Distance between starting point (B) and maximum of function (A+B)
    B - y-value of the starting point at x=0
    tau - steepness of the ascent to the maximum value
    """
    y = B + A*(1 - np.exp(-x/tau))
    return y


def sum_squares(params, x_data, y_data, weights, func):
    """
    Calculates the weighted residual sum of squares for a given function.
    """
    y_pred = func(x_data, *params)
    return sum(((y_pred - y_data)*weights)**2)


def rmse(params, x_data, y_data, weights, model):
    """
    Root-mean-squared error calculated for the given model.
    """
    return np.sqrt(sum_squares(params, x_data, y_data, weights, model)/len(x_data))


def fit_least_squares_model(x_data, y_data, weights, model, p0, quiet=False):
    """
    Fits a given model to the data using weighted least squares and
    initial guess for the parameters `p0`.
    Returns the best-fit parameters and the root-mean-square error of the
    fit.

    quiet: Set to True to suppress fmin output. Default False.
    """
    params = optimize.fmin(
        sum_squares, p0, args=(x_data, y_data, weights, model),
        maxfun=1e5, maxiter=1e5, disp=1-int(quiet),
    )
    return (params, rmse(params, x_data, y_data, weights, model))


def least_squares_aic(x_data, y_data, weights, params, model):
    """
    Calculates the Akaike information criterion for the given data and least
    squares model.
    Params:
    x_data, y_data - empirical data
    params - fitted parameters
    model - model function
    """
    log_like = np.log(sum_squares(params, x_data, y_data, weights, model))
    return 2*len(params) + len(x_data)*log_like


def calc_prod_gender_fraction(producers):
    """
    Calculates the gender fraction of a movie's producer
    crew. The fraction only producers for which we know the
    gender.
    """
    females = sum(1 for p in producers if p["gender"] == "female")
    males = sum(1 for p in producers if p["gender"] == "male")
    try:
        return females/(males + females)
    except ZeroDivisionError:
        return np.nan


def find_largest_consec_region(s_bool, threshold=2):
    """
    Finds the start and end indices of largest consecutive region
    of values from the given boolean Series that are True. Ignores any short
    peaks of `threshold` (default 2) or less values.

    Inspired by: http://stackoverflow.com/a/24433632
    """
    indices = s_bool.index

    regions = pd.DataFrame()

    # First row of consecutive region is a True preceded by a False in tags
    regions["start"] = indices[s_bool & ~s_bool.shift(1).fillna(False)]

    # Last row of consecutive region is a False preceded by a True
    regions["end"] = indices[s_bool & ~s_bool.shift(-1).fillna(False)]

    # How long is each region
    regions["span"] = regions.end - regions.start + 1

    # index of the region with the longest span
    max_idx = regions.span.argmax()
    start_max = regions.start.iloc[max_idx]
    end_max = regions.end.iloc[max_idx]

    # How many years between gaps
    regions["gap"] = regions.start - regions.end.shift(1)

    # Are there any non-spurious gaps separated by `threshold` values or less
    # right after the largest gap?
    small_gaps = (regions.end > end_max)
    small_gaps &= (regions.gap <= threshold)
    small_gaps &= (regions.span > 1)

    # If so, the largest such gap is now the region's end
    if small_gaps.sum() > 0:
        end_max = regions.end[small_gaps].iloc[-1]

    return (start_max, end_max)


def window(seq, n=3):
    """
    Returns a sliding window (of width n) over data from the iterable:
       s -> (s0,s1,...s[n-1]), (s1,s2,...,sn), ...
    From: https://docs.python.org/3.6/library/itertools.html#itertools-recipes
    """
    it = iter(seq)
    result = tuple(islice(it, n))
    if len(result) == n:
        yield result
    for elem in it:
        result = result[1:] + (elem,)
        yield result


def custom_freq_rolling_mean(df, val_col, dt_col, num, freq):
    """
    Calculates a rolling mean using the specified time-window, even
    if corresponds to a variable frequency, i.e., not all time values
    from `dt_col` are present in the same frequency.

    val_col (string): column over which to perform rolling mean.
    dt_col (string):  column used for calculating frequency. Must have DateTime values.
    num (int):        length of rolling window
    freq (string):    frequency offset abbreviation

    Ex: for a frequency of 3 years use: num=3, freq="AS"

    Offset abbreviations: http://pandas.pydata.org/pandas-docs/stable/timeseries.html#offset-aliases

    This function was originally created to calculate a rolling mean
    with a window of 3 years, where not all windows have the same number
    of datapoints.
    As of versions 0.19.1, this behavior is not implemented in pandas:
    https://github.com/pandas-dev/pandas/issues/13969#issuecomment-239288339
    """
    val_grouped = df.resample(freq, on=dt_col)[val_col]

    freq_sum = val_grouped.sum().rolling(num, min_periods=1).sum()
    freq_count = val_grouped.count().rolling(num, min_periods=1).sum()

    return freq_sum/freq_count
