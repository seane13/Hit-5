import numpy as np
import pandas as pd
from collections import defaultdict

def calculate_gaps(df, number_columns, window=None):
    """
    Returns a dict: number -> list of gaps (number of draws between appearances)
    If window is set, restricts analysis to window most recent draws.
    """
    if window is not None:
        df = df.tail(window)
    all_numbers = range(1, 43)
    gaps = {}
    for n in all_numbers:
        indices = np.where(df[number_columns].apply(lambda row: n in row.values, axis=1))[0]
        if len(indices) == 0:
            gaps[n] = []
            continue
        gap_list = [indices[0]]
        for i in range(1, len(indices)):
            gap_list.append(indices[i] - indices[i-1])
        gaps[n] = gap_list
    return gaps

def number_frequency(df, number_columns, window=None):
    """
    Returns dict: number -> number of times appeared in all/window draws.
    """
    if window is not None:
        df = df.tail(window)
    all_numbers = range(1, 43)
    freq = {n: df[number_columns].apply(lambda row: n in row.values, axis=1).sum() for n in all_numbers}
    return freq

def get_hot_warm_cold(df, number_columns, std_mult=1):
    """
    Classifies numbers as hot, warm, or cold by mean gap statistics.
    Returns (hot, warm, cold) lists.
    """
    gaps = calculate_gaps(df, number_columns)
    mean_gaps = {n: np.mean(g) if len(g) else np.nan for n, g in gaps.items()}
    mean_gap_series = pd.Series(mean_gaps)
    avg = mean_gap_series.mean()
    std = mean_gap_series.std()
    # Hot: much smaller than average gap, Cold: much larger
    hot = [n for n, m in mean_gaps.items() if not np.isnan(m) and m < avg - std_mult * std]
    cold = [n for n, m in mean_gaps.items() if not np.isnan(m) and m > avg + std_mult * std]
    warm = [n for n in range(1, 43) if n not in hot and n not in cold]
    return hot, warm, cold

def longest_gap_per_number(gaps):
    """
    Returns a dict: number -> longest gap for each number (0 if never drawn).
    """
    return {n: max(gap_list) if gap_list else 0 for n, gap_list in gaps.items()}

def recent_hits(df, number_columns, n=2):
    """Return a set of numbers that appeared in the last n draws."""
    return set(df[number_columns].tail(n).values.flatten())

def draws_set(df, number_columns):
    """
    Returns a set of all previous draws (as tuples of sorted numbers).
    Useful for checking if a combination was already drawn in the past.
    """
    return set(tuple(sorted(row)) for row in df[number_columns].values)
