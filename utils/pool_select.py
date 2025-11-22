# utils/pool_select.py
from utils.lottery_stats import calculate_gaps, get_hot_warm_cold
import pandas as pd
import numpy as np

# Main pool-selection function

def select_pool(df, number_columns, gap_n_cold=5):
    hot, warm, cold = get_hot_warm_cold(df, number_columns)
    all_gaps = calculate_gaps(df, number_columns)
    current_gaps = {n: g[-1] if g else 0 for n, g in all_gaps.items()}
    # Excessively cold: top N by current gap
    excessively_cold = sorted(current_gaps, key=lambda n: current_gaps[n], reverse=True)[:gap_n_cold]
    # Warm with above-median current gap
    warm_gaps = {n: current_gaps[n] for n in warm}
    qualified_warm = []
    if warm_gaps:
        median_warm_gap = pd.Series(list(warm_gaps.values())).median()
        qualified_warm = [n for n in warm if current_gaps[n] >= median_warm_gap]
    pool = set(hot) | set(excessively_cold) | set(qualified_warm)
    return pool

def select_gap_pool(df, number_columns, N_hot=1, N_warm=3, N_cold=1):
    all_numbers = range(1, 43)
    gap_list = {}
    for num in all_numbers:
        gaps = []
        indices = df[number_columns].apply(lambda row: num in row.values, axis=1)
        hit_indices = list(np.where(indices)[0])
        if not hit_indices:
            continue
        for i in range(len(hit_indices)):
            if i == 0:
                gaps.append(hit_indices[i])
            else:
                gaps.append(hit_indices[i] - hit_indices[i-1])
        gap_list[num] = gaps

    mean_gaps = {num: np.mean(gaps) for num, gaps in gap_list.items()}
    mean_gap_series = pd.Series(mean_gaps)
    avg_gap = mean_gap_series.mean()
    std_gap = mean_gap_series.std()

    hot = mean_gap_series[mean_gap_series < (avg_gap - std_gap)].index.tolist()
    warm = mean_gap_series[(mean_gap_series >= (avg_gap - std_gap)) & (mean_gap_series <= (avg_gap + std_gap))].index.tolist()
    cold = mean_gap_series[mean_gap_series > (avg_gap + std_gap)].index.tolist()

    pool_numbers = []
    pool_numbers += hot[:N_hot]
    pool_numbers += warm[:N_warm]
    pool_numbers += cold[:N_cold]
    # Return a flat pool (for hit coverage test), or you can return all possible combos as in pool.py
    return set(pool_numbers)
