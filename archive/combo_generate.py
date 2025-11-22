import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import itertools
from utils import combo_filters, lottery_stats, pool_select, viz

# === CONFIGURATION ===
DATA_PATH = 'data/hit5_clean_deduped.csv'
OUTPUT_PATH = 'data/hit5_combos_hot_cold_warm.csv'
NUMBER_COLUMNS = ['Num1', 'Num2', 'Num3', 'Num4', 'Num5']
HOT_N = 5    # Top N = "hot"
COLD_N = 5   # Bottom N = "cold"

# === LOAD DATA ===
df = pd.read_csv(DATA_PATH)
numbers = pd.concat([df[col] for col in NUMBER_COLUMNS])

# === BUILD FREQUENCY TABLE ===
freq = numbers.value_counts().sort_values(ascending=False)
hot_numbers = list(freq.head(HOT_N).index)
cold_numbers = list(freq.tail(COLD_N).index)
warm_numbers = [n for n in freq.index if n not in hot_numbers and n not in cold_numbers]

print(f"Hot numbers: {hot_numbers}")
print(f"Cold numbers: {cold_numbers}")
print(f"Warm numbers: {warm_numbers[:10]}... ({len(warm_numbers)} total)")

# === GENERATE ALL PICK 5 COMBOS: 1 cold, 1 hot, 3 warm ===
combos = set()
for cold in cold_numbers:
    for hot in hot_numbers:
        for warms in itertools.combinations(warm_numbers, 3):
            # Prevent overlap if warm equals hot or cold (shouldn't happen, but defensive)
            full_combo = set(warms) | {cold, hot}
            if len(full_combo) == 5:
                combos.add(tuple(sorted(full_combo)))

print(f"Total raw combos with 1 cold, 1 hot, 3 warm: {len(combos)}")

# === (OPTIONAL) FILTER LOGIC ===


from utils.combo_filters import (
    valid_even_odd, has_3_consecutive, in_past_draws, in_sum_range, must_include
)
from utils.lottery_stats import recent_hits, draws_set
SUM_RANGE = (80, 140)
past_draws = draws_set(df, NUMBER_COLUMNS)
filtered_combos = []
for combo in combos:
    if not valid_even_odd(combo): continue
    if has_3_consecutive(combo): continue
    if in_past_draws(combo, past_draws): continue
    if not in_sum_range(combo, SUM_RANGE): continue
    filtered_combos.append(combo)
print(f"Combos after filtering: {len(filtered_combos)}")
combos = filtered_combos

# === EXPORT RESULTS ===
combo_list = [dict(Num1=combo[0], Num2=combo[1], Num3=combo[2], Num4=combo[3], Num5=combo[4]) for combo in combos]
combo_df = pd.DataFrame(combo_list)
combo_df.to_csv(OUTPUT_PATH, index=False)
print(f"Combos saved to {OUTPUT_PATH}")

# === (OPTIONAL) PRINT SAMPLE COMBOS ===
print("Sample combos:")
for row in combo_df.head(10).itertuples(index=False):
    print(row)
