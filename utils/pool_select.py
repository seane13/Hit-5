# utils/pool_select.py
from utils.lottery_stats import calculate_gaps, get_hot_warm_cold
import pandas as pd

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
