import pandas as pd
from utils.pool_select import select_pool

# --- Config ---
DATA_PATH = 'data/hit5_clean_deduped.csv'
NUMBER_COLUMNS = ['Num1', 'Num2', 'Num3', 'Num4', 'Num5']
GAP_N_COLD = 5   # Number of excessively cold numbers to include in each pool
TEST_WINDOW = 100   # How many of the last draws to test over

def backtest_pool_strategy(df, number_columns, test_window=TEST_WINDOW, gap_n_cold=GAP_N_COLD):
    backtest_df = df.tail(test_window).reset_index(drop=True)
    results = []
    for idx in range(test_window):
        train_df = backtest_df.iloc[:idx]
        current_draw = backtest_df.iloc[idx]
        if len(train_df) < 20:
            continue
        # Use the shared pool selection logic!
        pool = select_pool(train_df, number_columns, gap_n_cold)
        draw_nums = set(current_draw[number_columns])
        matches = draw_nums.intersection(pool)
        results.append({
            "draw": idx,
            "draw_nums": draw_nums,
            "pool": pool,
            "match_count": len(matches),
            "all_in_pool": draw_nums.issubset(pool)
        })
    results_df = pd.DataFrame(results)
    # Report
    coverage = results_df["all_in_pool"].mean()
    mean_matches = results_df["match_count"].mean()
    print(f"Coverage (all numbers in pool): {coverage:.2%}")
    print(f"Average pool matches per draw: {mean_matches:.2f}")
    print("Distribution of match counts:")
    print(results_df["match_count"].value_counts().sort_index())
    return results_df

if __name__ == "__main__":
    df = pd.read_csv(DATA_PATH)
    backtest_pool_strategy(df, NUMBER_COLUMNS)
