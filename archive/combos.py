import pandas as pd
import itertools
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.lottery_stats import number_frequency, recent_hits, draws_set
from utils.combo_filters import (
    valid_even_odd, has_3_consecutive, in_past_draws, in_sum_range, must_include
)
from utils.pool_select import select_pool

# --- Configuration ---
DATA_PATH = 'data/hit5_clean_deduped.csv'
NUMBER_COLUMNS = ['Num1', 'Num2', 'Num3', 'Num4', 'Num5']
SUM_RANGE = (80, 140)   # Acceptable sum range for draw
MUST_INCLUDE_NUMS = []  # e.g. set to [7, 19] if required
GAP_N_COLD = 5          # Number of excessively cold numbers to include in pool

# --- Load Data ---
df = pd.read_csv(DATA_PATH)

# --- Pool Selection (via shared logic!) ---
pool_numbers = select_pool(df, NUMBER_COLUMNS, gap_n_cold=GAP_N_COLD)
print(f"Combo pool numbers ({len(pool_numbers)}):", sorted(pool_numbers))

# --- Generate Candidate Combos ---
candidate_combos = list(itertools.combinations(pool_numbers, 5))
print(f"Total candidate combos from pool: {len(candidate_combos)}")

# --- Filtering ---
recent = recent_hits(df, NUMBER_COLUMNS, n=3)
past_draws = draws_set(df, NUMBER_COLUMNS)

filtered_combos = []
for combo in candidate_combos:
    if not valid_even_odd(combo):
        continue
    if has_3_consecutive(combo):
        continue
    if in_past_draws(combo, past_draws):
        continue
    if not in_sum_range(combo, SUM_RANGE):
        continue
    if MUST_INCLUDE_NUMS and not must_include(combo, MUST_INCLUDE_NUMS):
        continue
    filtered_combos.append(combo)
print(f"Combos after filtering: {len(filtered_combos)}")

# --- Scoring ---
freq = number_frequency(df, NUMBER_COLUMNS)
combo_scores = []
for combo in filtered_combos:
    score = sum(freq.get(n, 0) for n in combo)
    combo_scores.append((combo, score))
combo_scores.sort(key=lambda x: x[1], reverse=True)

print("Top 10 combos by historical-frequency sum score:")
for combo, score in combo_scores[:10]:
    print(f"{combo} - Score: {score}")

# --- Save Results ---
output_df = pd.DataFrame([
    {"Num1": c[0], "Num2": c[1], "Num3": c[2], "Num4": c[3], "Num5": c[4], "Score": s} for c, s in combo_scores
])
output_df.to_csv('data/top_combinations.csv', index=False)
