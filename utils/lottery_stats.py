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
    std = mean_gap_series
